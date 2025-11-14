"""
Usage analytics API routes.
Provides comprehensive analytics data for research patterns and system usage.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from ..api.auth import get_current_user, get_admin_user
from ..models.user import User
from ..core.database import get_db
from ..services.analytics.usage_analytics import UsageAnalyticsService
import sqlalchemy as sa

router = APIRouter()


# Request/Response Models

class AnalyticsRequest(BaseModel):
    """Base analytics request model."""
    date_from: Optional[datetime] = Field(None, description="Start date for analytics")
    date_to: Optional[datetime] = Field(None, description="End date for analytics")
    user_id: Optional[str] = Field(None, description="Specific user ID (admin only)")


class ResearchAnalyticsResponse(BaseModel):
    """Response model for research analytics."""
    success: bool
    analytics: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class CollaborationAnalyticsResponse(BaseModel):
    """Response model for collaboration analytics."""
    success: bool
    analytics: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class FeatureAdoptionResponse(BaseModel):
    """Response model for feature adoption analytics."""
    success: bool
    analytics: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class UserBehaviorResponse(BaseModel):
    """Response model for user behavior analytics."""
    success: bool
    analytics: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class PerformanceAnalyticsResponse(BaseModel):
    """Response model for performance analytics."""
    success: bool
    analytics: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ResearchInsightsResponse(BaseModel):
    """Response model for research insights."""
    success: bool
    insights: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class AnalyticsSummaryResponse(BaseModel):
    """Response model for analytics summary."""
    success: bool
    summary: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class TopItemsResponse(BaseModel):
    """Response model for top items analytics."""
    success: bool
    top_items: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class TrendAnalysisResponse(BaseModel):
    """Response model for trend analysis."""
    success: bool
    trends: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# API Endpoints

@router.get("/research", response_model=ResearchAnalyticsResponse)
async def get_research_analytics(
    date_from: Optional[datetime] = Query(None, description="Start date (ISO format)"),
    date_to: Optional[datetime] = Query(None, description="End date (ISO format)"),
    current_user: User = Depends(get_current_user),
    db: sa.AsyncSession = Depends(get_db)
):
    """
    Get comprehensive research analytics.

    Returns detailed analysis of research queries, patterns, topics, and usage.
    Regular users see their own data, admins can see all users' data.
    """
    try:
        analytics_service = UsageAnalyticsService()

        # Only admins can specify other users
        user_id = None
        if current_user.role == "admin":
            user_id = Query(None)  # This should be passed as a parameter, but simplified for now

        analytics = await analytics_service.get_research_analytics(
            db, date_from, date_to, user_id
        )

        if "error" in analytics:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=analytics["error"]
            )

        return ResearchAnalyticsResponse(success=True, analytics=analytics)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Research analytics failed: {str(e)}"
        )


@router.get("/collaboration", response_model=CollaborationAnalyticsResponse)
async def get_collaboration_analytics(
    date_from: Optional[datetime] = Query(None, description="Start date (ISO format)"),
    date_to: Optional[datetime] = Query(None, description="End date (ISO format)"),
    current_user: User = Depends(get_admin_user),  # Admin only for collaboration analytics
    db: sa.AsyncSession = Depends(get_db)
):
    """
    Get collaboration analytics (admin only).

    Returns analysis of collaborative sessions, user interactions, and engagement patterns.
    """
    try:
        analytics_service = UsageAnalyticsService()

        analytics = await analytics_service.get_collaboration_analytics(
            db, date_from, date_to
        )

        if "error" in analytics:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=analytics["error"]
            )

        return CollaborationAnalyticsResponse(success=True, analytics=analytics)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Collaboration analytics failed: {str(e)}"
        )


@router.get("/features", response_model=FeatureAdoptionResponse)
async def get_feature_adoption_analytics(
    date_from: Optional[datetime] = Query(None, description="Start date (ISO format)"),
    date_to: Optional[datetime] = Query(None, description="End date (ISO format)"),
    current_user: User = Depends(get_admin_user),  # Admin only
    db: sa.AsyncSession = Depends(get_db)
):
    """
    Get feature adoption analytics (admin only).

    Returns analysis of how different features are being adopted and used.
    """
    try:
        analytics_service = UsageAnalyticsService()

        analytics = await analytics_service.get_feature_adoption_analytics(
            db, date_from, date_to
        )

        if "error" in analytics:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=analytics["error"]
            )

        return FeatureAdoptionResponse(success=True, analytics=analytics)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Feature adoption analytics failed: {str(e)}"
        )


@router.get("/users", response_model=UserBehaviorResponse)
async def get_user_behavior_analytics(
    date_from: Optional[datetime] = Query(None, description="Start date (ISO format)"),
    date_to: Optional[datetime] = Query(None, description="End date (ISO format)"),
    current_user: User = Depends(get_admin_user),  # Admin only
    db: sa.AsyncSession = Depends(get_db)
):
    """
    Get user behavior analytics (admin only).

    Returns analysis of user engagement, retention, and behavior patterns.
    """
    try:
        analytics_service = UsageAnalyticsService()

        analytics = await analytics_service.get_user_behavior_analytics(
            db, date_from, date_to
        )

        if "error" in analytics:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=analytics["error"]
            )

        return UserBehaviorResponse(success=True, analytics=analytics)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"User behavior analytics failed: {str(e)}"
        )


@router.get("/performance", response_model=PerformanceAnalyticsResponse)
async def get_performance_analytics(
    date_from: Optional[datetime] = Query(None, description="Start date (ISO format)"),
    date_to: Optional[datetime] = Query(None, description="End date (ISO format)"),
    current_user: User = Depends(get_admin_user),  # Admin only
    db: sa.AsyncSession = Depends(get_db)
):
    """
    Get system performance analytics (admin only).

    Returns analysis of response times, success rates, and system performance metrics.
    """
    try:
        analytics_service = UsageAnalyticsService()

        analytics = await analytics_service.get_performance_analytics(
            db, date_from, date_to
        )

        if "error" in analytics:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=analytics["error"]
            )

        return PerformanceAnalyticsResponse(success=True, analytics=analytics)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Performance analytics failed: {str(e)}"
        )


@router.get("/insights", response_model=ResearchInsightsResponse)
async def get_research_insights(
    date_from: Optional[datetime] = Query(None, description="Start date (ISO format)"),
    date_to: Optional[datetime] = Query(None, description="End date (ISO format)"),
    current_user: User = Depends(get_admin_user),  # Admin only
    db: sa.AsyncSession = Depends(get_db)
):
    """
    Get actionable research insights (admin only).

    Returns AI-generated insights and recommendations based on analytics data.
    """
    try:
        analytics_service = UsageAnalyticsService()

        # Get combined analytics data
        research_analytics = await analytics_service.get_research_analytics(db, date_from, date_to)
        collaboration_analytics = await analytics_service.get_collaboration_analytics(db, date_from, date_to)
        feature_analytics = await analytics_service.get_feature_adoption_analytics(db, date_from, date_to)

        combined_data = {
            "research": research_analytics,
            "collaboration": collaboration_analytics,
            "features": feature_analytics
        }

        insights = analytics_service.generate_research_insights(combined_data)

        return ResearchInsightsResponse(success=True, insights=insights)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Research insights failed: {str(e)}"
        )


@router.get("/summary", response_model=AnalyticsSummaryResponse)
async def get_analytics_summary(
    current_user: User = Depends(get_current_user),
    db: sa.AsyncSession = Depends(get_db)
):
    """
    Get analytics summary dashboard.

    Returns key metrics and summary statistics for quick overview.
    """
    try:
        analytics_service = UsageAnalyticsService()

        # Get last 30 days of data
        date_from = datetime.utcnow() - timedelta(days=30)
        date_to = datetime.utcnow()

        # Get research analytics
        research_analytics = await analytics_service.get_research_analytics(
            db, date_from, date_to, current_user.id if current_user.role != "admin" else None
        )

        summary = {
            "total_researches": research_analytics.get("total_researches", 0),
            "active_users": research_analytics.get("user_engagement", {}).get("total_users", 0),
            "popular_topics": research_analytics.get("topic_analysis", {}).get("top_topics", [])[:3],
            "peak_usage_times": research_analytics.get("temporal_patterns", {}).get("peak_usage_hours", []),
            "most_used_persona": research_analytics.get("persona_usage", {}).get("most_used_persona"),
            "success_rate": research_analytics.get("performance_metrics", {}).get("success_rate", 0),
            "date_range": {
                "from": date_from.isoformat(),
                "to": date_to.isoformat()
            }
        }

        return AnalyticsSummaryResponse(success=True, summary=summary)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analytics summary failed: {str(e)}"
        )


@router.get("/top", response_model=TopItemsResponse)
async def get_top_items_analytics(
    category: str = Query(..., description="Category: queries, topics, users, features"),
    limit: int = Query(10, ge=1, le=50, description="Number of items to return"),
    date_from: Optional[datetime] = Query(None, description="Start date (ISO format)"),
    date_to: Optional[datetime] = Query(None, description="End date (ISO format)"),
    current_user: User = Depends(get_current_user),
    db: sa.AsyncSession = Depends(get_db)
):
    """
    Get top items analytics.

    Returns ranked lists of most popular queries, topics, users, or features.
    """
    try:
        analytics_service = UsageAnalyticsService()

        # Get analytics data
        research_analytics = await analytics_service.get_research_analytics(
            db, date_from, date_to, current_user.id if current_user.role != "admin" else None
        )

        top_items = {}

        if category == "queries":
            # Most common query patterns (simplified)
            query_patterns = research_analytics.get("query_patterns", {})
            top_items = {
                "category": "queries",
                "items": query_patterns.get("common_keywords", [])[:limit],
                "total_unique": query_patterns.get("unique_queries", 0)
            }

        elif category == "topics":
            topic_analysis = research_analytics.get("topic_analysis", {})
            top_items = {
                "category": "topics",
                "items": topic_analysis.get("top_topics", [])[:limit],
                "total_topics": len(topic_analysis.get("topic_distribution", {}))
            }

        elif category == "users":
            if current_user.role != "admin":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied"
                )
            user_engagement = research_analytics.get("user_engagement", {})
            top_items = {
                "category": "users",
                "items": user_engagement.get("power_users", [])[:limit],
                "total_users": user_engagement.get("total_users", 0)
            }

        elif category == "features":
            # Mock feature usage data
            feature_usage = [
                {"feature": "deep_search", "usage_count": 1250, "adoption_rate": 85.2},
                {"feature": "citation_management", "usage_count": 890, "adoption_rate": 67.8},
                {"feature": "research_templates", "usage_count": 567, "adoption_rate": 45.6},
                {"feature": "voice_research", "usage_count": 234, "adoption_rate": 18.9},
                {"feature": "multi_language", "usage_count": 345, "adoption_rate": 27.8}
            ]
            top_items = {
                "category": "features",
                "items": sorted(feature_usage, key=lambda x: x["usage_count"], reverse=True)[:limit],
                "total_features": len(feature_usage)
            }

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid category: {category}"
            )

        return TopItemsResponse(success=True, top_items=top_items)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Top items analytics failed: {str(e)}"
        )


@router.get("/trends", response_model=TrendAnalysisResponse)
async def get_trend_analysis(
    metric: str = Query(..., description="Metric: usage, topics, performance, adoption"),
    period: str = Query("30d", description="Time period: 7d, 30d, 90d"),
    current_user: User = Depends(get_admin_user),  # Admin only
    db: sa.AsyncSession = Depends(get_db)
):
    """
    Get trend analysis for specified metrics (admin only).

    Returns time-series data showing trends over the specified period.
    """
    try:
        # Parse period
        if period == "7d":
            days = 7
        elif period == "30d":
            days = 30
        elif period == "90d":
            days = 90
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid period: {period}"
            )

        date_from = datetime.utcnow() - timedelta(days=days)
        date_to = datetime.utcnow()

        analytics_service = UsageAnalyticsService()

        # Generate mock trend data (would be real time-series data in production)
        trends = {
            "metric": metric,
            "period": period,
            "data_points": days,
            "trend": "increasing" if metric in ["usage", "adoption"] else "stable",
            "change_percentage": 15.7 if metric == "usage" else -2.3,
            "time_series": []
        }

        # Generate time series data points
        for i in range(days):
            date = (date_from + timedelta(days=i)).date().isoformat()
            if metric == "usage":
                value = 100 + (i * 2.5) + (i % 7 * 10)  # Weekly pattern with growth
            elif metric == "topics":
                value = 50 + (i % 10 * 3)  # Topic diversity variation
            elif metric == "performance":
                value = 95 + ((i % 5) - 2)  # Performance variation
            elif metric == "adoption":
                value = 20 + (i * 1.8)  # Adoption growth
            else:
                value = 50 + (i % 20 - 10)  # Default variation

            trends["time_series"].append({
                "date": date,
                "value": round(value, 1),
                "change": round((value - (100 if metric == "usage" else 50)) / (100 if metric == "usage" else 50) * 100, 1)
            })

        return TrendAnalysisResponse(success=True, trends=trends)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Trend analysis failed: {str(e)}"
        )


@router.get("/export")
async def export_analytics_data(
    format: str = Query("json", description="Export format: json, csv"),
    include_sensitive: bool = Query(False, description="Include sensitive user data"),
    date_from: Optional[datetime] = Query(None, description="Start date (ISO format)"),
    date_to: Optional[datetime] = Query(None, description="End date (ISO format)"),
    current_user: User = Depends(get_admin_user),  # Admin only
    db: sa.AsyncSession = Depends(get_db)
):
    """
    Export analytics data for external analysis (admin only).

    Returns comprehensive analytics data in the requested format.
    """
    try:
        analytics_service = UsageAnalyticsService()

        # Get all analytics data
        research_analytics = await analytics_service.get_research_analytics(db, date_from, date_to)
        collaboration_analytics = await analytics_service.get_collaboration_analytics(db, date_from, date_to)
        feature_analytics = await analytics_service.get_feature_adoption_analytics(db, date_from, date_to)
        user_analytics = await analytics_service.get_user_behavior_analytics(db, date_from, date_to)

        export_data = {
            "export_timestamp": datetime.utcnow().isoformat(),
            "date_range": {
                "from": date_from.isoformat() if date_from else None,
                "to": date_to.isoformat() if date_to else None
            },
            "research_analytics": research_analytics,
            "collaboration_analytics": collaboration_analytics,
            "feature_analytics": feature_analytics,
            "user_analytics": user_analytics if include_sensitive else {"message": "Sensitive data excluded"}
        }

        if format == "json":
            return {
                "success": True,
                "data": export_data,
                "format": "json"
            }
        elif format == "csv":
            # Convert to CSV format (simplified)
            csv_data = "timestamp,metric,value\n"
            for key, value in export_data.items():
                if isinstance(value, (int, float)):
                    csv_data += f"{export_data['export_timestamp']},{key},{value}\n"

            return {
                "success": True,
                "data": csv_data,
                "format": "csv",
                "filename": f"analytics_export_{datetime.utcnow().date()}.csv"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported format: {format}"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analytics export failed: {str(e)}"
        )


@router.post("/refresh-cache")
async def refresh_analytics_cache(
    current_user: User = Depends(get_admin_user),  # Admin only
    db: sa.AsyncSession = Depends(get_db)
):
    """
    Refresh analytics cache (admin only).

    Forces recalculation of analytics data and updates cached results.
    """
    try:
        analytics_service = UsageAnalyticsService()

        # Clear cache
        analytics_service.analytics_cache.clear()

        # Pre-calculate some common analytics to warm the cache
        date_from = datetime.utcnow() - timedelta(days=30)

        await analytics_service.get_research_analytics(db, date_from)
        await analytics_service.get_collaboration_analytics(db, date_from)
        await analytics_service.get_feature_adoption_analytics(db, date_from)

        return {
            "success": True,
            "message": "Analytics cache refreshed successfully",
            "cache_size": len(analytics_service.analytics_cache),
            "refreshed_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cache refresh failed: {str(e)}"
        )
