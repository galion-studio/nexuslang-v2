"""
Content Management Service
Core service for managing content posts
"""

from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from models.content import ContentPost, PlatformPost, SocialAccount
from .platforms.reddit import RedditConnector
from .platforms.twitter import TwitterConnector
from .platforms.instagram import InstagramConnector
from .platforms.facebook import FacebookConnector
from .platforms.linkedin import LinkedInConnector
from .platforms.tiktok import TikTokConnector
from .platforms.youtube import YouTubeConnector
from .platforms.forums.hackernews import HackerNewsConnector
from .platforms.forums.producthunt import ProductHuntConnector
from .platforms.forums.devto import DevToConnector
from .platforms.forums.generic_forum import GenericForumConnector


# Map platform names to connector classes
PLATFORM_CONNECTORS = {
    "reddit": RedditConnector,
    "twitter": TwitterConnector,
    "instagram": InstagramConnector,
    "facebook": FacebookConnector,
    "linkedin": LinkedInConnector,
    "tiktok": TikTokConnector,
    "youtube": YouTubeConnector,
    "hackernews": HackerNewsConnector,
    "producthunt": ProductHuntConnector,
    "devto": DevToConnector,
    "generic_forum": GenericForumConnector
}


class ContentService:
    """
    Service for managing content across multiple platforms
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def publish_post(self, post_id: uuid.UUID) -> Dict:
        """
        Publish a content post to all selected platforms
        
        Args:
            post_id: Content post ID
        
        Returns:
            Dict with publishing results per platform
        """
        # Get content post
        result = await self.db.execute(
            select(ContentPost).where(ContentPost.id == post_id)
        )
        post = result.scalar_one_or_none()
        
        if not post:
            return {"error": "Post not found"}
        
        # Get social accounts for selected platforms
        results = {}
        
        for platform in post.platforms:
            try:
                # Get active social account for this brand and platform
                account_result = await self.db.execute(
                    select(SocialAccount).where(
                        SocialAccount.brand_id == post.brand_id,
                        SocialAccount.platform == platform,
                        SocialAccount.is_active == True
                    )
                )
                account = account_result.scalar_one_or_none()
                
                if not account:
                    results[platform] = {"success": False, "error": "No active account found"}
                    continue
                
                # Get platform connector
                connector_class = PLATFORM_CONNECTORS.get(platform)
                if not connector_class:
                    results[platform] = {"success": False, "error": "Platform not supported"}
                    continue
                
                # Initialize connector
                connector = connector_class(account.credentials or {})
                
                # Publish to platform
                platform_result = await connector.post_content(
                    content=post.content,
                    media_urls=[m.get("url") for m in post.media_urls] if post.media_urls else None,
                    metadata=post.metadata
                )
                
                # Create platform post record
                platform_post = PlatformPost(
                    content_post_id=post.id,
                    social_account_id=account.id,
                    platform=platform,
                    platform_post_id=platform_result.get("post_id"),
                    platform_url=platform_result.get("url"),
                    platform_content=post.content,
                    status="posted"
                )
                self.db.add(platform_post)
                
                results[platform] = platform_result
            
            except Exception as e:
                results[platform] = {"success": False, "error": str(e)}
                
                # Create failed platform post
                platform_post = PlatformPost(
                    content_post_id=post.id,
                    social_account_id=account.id if 'account' in locals() else None,
                    platform=platform,
                    status="failed",
                    error_message=str(e)
                )
                self.db.add(platform_post)
        
        # Update post status
        if all(r.get("success") for r in results.values()):
            post.status = "published"
        else:
            post.status = "partially_published"
        
        await self.db.commit()
        
        return results
    
    async def validate_account(self, account_id: uuid.UUID) -> bool:
        """
        Validate that a social account's credentials are still valid
        
        Args:
            account_id: Social account ID
        
        Returns:
            True if valid, False otherwise
        """
        result = await self.db.execute(
            select(SocialAccount).where(SocialAccount.id == account_id)
        )
        account = result.scalar_one_or_none()
        
        if not account:
            return False
        
        connector_class = PLATFORM_CONNECTORS.get(account.platform)
        if not connector_class:
            return False
        
        try:
            connector = connector_class(account.credentials or {})
            is_valid = await connector.validate_credentials()
            
            # Update account status
            account.sync_status = "active" if is_valid else "error"
            account.error_message = None if is_valid else "Invalid credentials"
            await self.db.commit()
            
            return is_valid
        
        except Exception as e:
            account.sync_status = "error"
            account.error_message = str(e)
            await self.db.commit()
            return False

