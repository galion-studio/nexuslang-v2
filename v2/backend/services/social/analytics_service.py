"""
Analytics Aggregation Service
Syncs and aggregates analytics from all platforms
"""

from typing import Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import uuid
import asyncio

from models.content import PlatformPost, PostAnalytics, SocialAccount
from .content_service import PLATFORM_CONNECTORS


class AnalyticsService:
    """
    Service for syncing and aggregating analytics from platforms
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def sync_post_analytics(self, platform_post_id: uuid.UUID) -> Dict:
        """
        Sync analytics for a specific platform post
        
        Args:
            platform_post_id: Platform post ID
        
        Returns:
            Dict with analytics data
        """
        # Get platform post
        result = await self.db.execute(
            select(PlatformPost, SocialAccount)
            .join(SocialAccount, PlatformPost.social_account_id == SocialAccount.id)
            .where(PlatformPost.id == platform_post_id)
        )
        row = result.first()
        
        if not row:
            return {"error": "Platform post not found"}
        
        platform_post, account = row
        
        if not platform_post.platform_post_id:
            return {"error": "No platform post ID"}
        
        try:
            # Get platform connector
            connector_class = PLATFORM_CONNECTORS.get(platform_post.platform)
            if not connector_class:
                return {"error": "Platform not supported"}
            
            # Initialize connector and fetch analytics
            connector = connector_class(account.credentials or {})
            analytics_data = await connector.get_post_analytics(platform_post.platform_post_id)
            
            # Check if analytics record exists
            existing_result = await self.db.execute(
                select(PostAnalytics).where(PostAnalytics.platform_post_id == platform_post_id)
            )
            existing_analytics = existing_result.scalar_one_or_none()
            
            if existing_analytics:
                # Update existing analytics
                existing_analytics.likes = analytics_data.get("likes", 0)
                existing_analytics.comments = analytics_data.get("comments", 0)
                existing_analytics.shares = analytics_data.get("shares", 0)
                existing_analytics.views = analytics_data.get("views", 0)
                existing_analytics.clicks = analytics_data.get("clicks", 0)
                existing_analytics.saves = analytics_data.get("saves", 0)
                existing_analytics.reach = analytics_data.get("reach", 0)
                existing_analytics.impressions = analytics_data.get("impressions", 0)
                existing_analytics.engagement_rate = analytics_data.get("engagement_rate", 0.0)
                existing_analytics.platform_specific_metrics = analytics_data.get("platform_specific_metrics", {})
                existing_analytics.synced_at = datetime.utcnow()
            else:
                # Create new analytics record
                new_analytics = PostAnalytics(
                    platform_post_id=platform_post_id,
                    likes=analytics_data.get("likes", 0),
                    comments=analytics_data.get("comments", 0),
                    shares=analytics_data.get("shares", 0),
                    views=analytics_data.get("views", 0),
                    clicks=analytics_data.get("clicks", 0),
                    saves=analytics_data.get("saves", 0),
                    reach=analytics_data.get("reach", 0),
                    impressions=analytics_data.get("impressions", 0),
                    engagement_rate=analytics_data.get("engagement_rate", 0.0),
                    platform_specific_metrics=analytics_data.get("platform_specific_metrics", {})
                )
                self.db.add(new_analytics)
            
            await self.db.commit()
            
            return analytics_data
        
        except Exception as e:
            return {"error": str(e)}
    
    async def sync_all_recent_posts(self, days: int = 7) -> Dict:
        """
        Sync analytics for all posts from the last N days
        
        Args:
            days: Number of days to look back
        
        Returns:
            Dict with sync results
        """
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get all platform posts from recent days
        result = await self.db.execute(
            select(PlatformPost).where(
                PlatformPost.posted_at >= cutoff_date,
                PlatformPost.status == "posted"
            )
        )
        recent_posts = result.scalars().all()
        
        results = {
            "total": len(recent_posts),
            "successful": 0,
            "failed": 0,
            "errors": []
        }
        
        # Sync analytics for each post
        for post in recent_posts:
            try:
                analytics = await self.sync_post_analytics(post.id)
                if "error" not in analytics:
                    results["successful"] += 1
                else:
                    results["failed"] += 1
                    results["errors"].append({
                        "post_id": str(post.id),
                        "error": analytics["error"]
                    })
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({
                    "post_id": str(post.id),
                    "error": str(e)
                })
        
        return results
    
    async def get_aggregated_analytics(
        self,
        brand_id: Optional[uuid.UUID] = None,
        platform: Optional[str] = None,
        days: int = 30
    ) -> Dict:
        """
        Get aggregated analytics across posts
        
        Args:
            brand_id: Optional brand filter
            platform: Optional platform filter
            days: Number of days to aggregate
        
        Returns:
            Dict with aggregated metrics
        """
        from datetime import timedelta
        from sqlalchemy import func
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Build query
        query = select(
            func.count(PlatformPost.id).label('total_posts'),
            func.sum(PostAnalytics.likes).label('total_likes'),
            func.sum(PostAnalytics.comments).label('total_comments'),
            func.sum(PostAnalytics.shares).label('total_shares'),
            func.sum(PostAnalytics.views).label('total_views'),
            func.avg(PostAnalytics.engagement_rate).label('avg_engagement_rate')
        ).select_from(PlatformPost).join(
            PostAnalytics,
            PlatformPost.id == PostAnalytics.platform_post_id,
            isouter=True
        ).where(
            PlatformPost.posted_at >= cutoff_date
        )
        
        # Apply filters
        if platform:
            query = query.where(PlatformPost.platform == platform)
        
        result = await self.db.execute(query)
        row = result.first()
        
        return {
            "period_days": days,
            "total_posts": row.total_posts or 0,
            "total_likes": row.total_likes or 0,
            "total_comments": row.total_comments or 0,
            "total_shares": row.total_shares or 0,
            "total_views": row.total_views or 0,
            "avg_engagement_rate": float(row.avg_engagement_rate or 0.0)
        }


async def start_analytics_sync_worker():
    """
    Background worker that continuously syncs analytics
    Runs every hour
    """
    from core.database import get_db
    
    while True:
        try:
            async for db in get_db():
                analytics_service = AnalyticsService(db)
                results = await analytics_service.sync_all_recent_posts(days=7)
                
                print(f"Analytics sync completed: {results['successful']} successful, "
                      f"{results['failed']} failed out of {results['total']} posts")
        
        except Exception as e:
            print(f"Analytics sync worker error: {e}")
        
        # Run every hour
        await asyncio.sleep(3600)

