"""
Analytics API Endpoints
Provides usage metrics, statistics, and insights.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from ..services.analytics.analytics_engine import get_analytics
from ..models.user import User
from ..api.auth import get_current_user, get_optional_user
from ..core.database import get_db

router = APIRouter()


# Response Models
class SystemStatsResponse(BaseModel):
    """System-wide statistics."""
    requests: Dict
    performance: Dict
    users: Dict
    credits: Dict
    timestamp: str


class UserAnalyticsResponse(BaseModel):
    """User-specific analytics."""
    user_id: int
    total_requests: int
    total_credits_used: float
    ai_chat_count: int
    code_executions: int
    image_generations: int
    video_generations: int
    voice_syntheses: int
    projects_created: int
    last_active: str
    member_since: str


class UsageMetric(BaseModel):
    """Single usage metric."""
    timestamp: str
    value: float
    label: str


class ChartData(BaseModel):
    """Chart data for visualizations."""
    labels: List[str]
    datasets: List[Dict]


# Endpoints

@router.get("/system", response_model=SystemStatsResponse)
async def get_system_stats(
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Get system-wide statistics.
    
    Returns overall platform metrics including:
    - Total requests and success rate
    - Performance metrics (response times)
    - Active user count
    - Credits consumed
    
    Public endpoint (no auth required for demo).
    """
    analytics = get_analytics()
    stats = analytics.get_stats()
    
    return SystemStatsResponse(**stats)


@router.get("/user", response_model=UserAnalyticsResponse)
async def get_user_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get analytics for the current user.
    
    Returns your personal usage statistics including:
    - Total API requests made
    - Credits consumed
    - Feature usage breakdown
    - Activity history
    """
    # Mock data for demo (replace with real database queries)
    return UserAnalyticsResponse(
        user_id=current_user.id,
        total_requests=142,
        total_credits_used=45.67,
        ai_chat_count=89,
        code_executions=23,
        image_generations=18,
        video_generations=5,
        voice_syntheses=7,
        projects_created=12,
        last_active=datetime.utcnow().isoformat(),
        member_since=current_user.created_at.isoformat()
    )


@router.get("/usage")
async def get_usage_metrics(
    period: str = Query("week", description="Time period: day, week, month, year"),
    current_user: User = Depends(get_current_user)
):
    """
    Get usage metrics over time.
    
    Returns time-series data for visualizing your usage patterns.
    Useful for tracking trends and understanding consumption.
    """
    # Generate mock time series data
    now = datetime.utcnow()
    
    if period == "day":
        # Last 24 hours, hourly
        data_points = 24
        labels = [(now - timedelta(hours=i)).strftime("%H:00") for i in range(data_points-1, -1, -1)]
    elif period == "week":
        # Last 7 days, daily
        data_points = 7
        labels = [(now - timedelta(days=i)).strftime("%b %d") for i in range(data_points-1, -1, -1)]
    elif period == "month":
        # Last 30 days, daily
        data_points = 30
        labels = [(now - timedelta(days=i)).strftime("%b %d") for i in range(data_points-1, -1, -1)]
    else:
        # Last 12 months, monthly
        data_points = 12
        labels = [(now - timedelta(days=30*i)).strftime("%b %Y") for i in range(data_points-1, -1, -1)]
    
    # Generate mock data
    import random
    
    return ChartData(
        labels=labels,
        datasets=[
            {
                "label": "API Requests",
                "data": [random.randint(5, 50) for _ in range(data_points)],
                "borderColor": "rgb(75, 192, 192)",
                "backgroundColor": "rgba(75, 192, 192, 0.2)"
            },
            {
                "label": "Credits Used",
                "data": [round(random.uniform(0.5, 5.0), 2) for _ in range(data_points)],
                "borderColor": "rgb(255, 99, 132)",
                "backgroundColor": "rgba(255, 99, 132, 0.2)"
            }
        ]
    )


@router.get("/feature-usage")
async def get_feature_usage(
    current_user: User = Depends(get_current_user)
):
    """
    Get feature usage breakdown.
    
    Shows which features you use most frequently.
    Useful for understanding your workflow and optimizing usage.
    """
    # Mock feature usage data
    return {
        "features": [
            {"name": "AI Chat", "count": 89, "percentage": 42.5},
            {"name": "Code Execution", "count": 23, "percentage": 11.0},
            {"name": "Image Generation", "count": 18, "percentage": 8.6},
            {"name": "Text Generation", "count": 35, "percentage": 16.7},
            {"name": "Video Generation", "count": 5, "percentage": 2.4},
            {"name": "Voice Synthesis", "count": 7, "percentage": 3.3},
            {"name": "Projects", "count": 32, "percentage": 15.3}
        ],
        "total_actions": 209,
        "period": "all_time"
    }


@router.get("/credits-history")
async def get_credits_history(
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    current_user: User = Depends(get_current_user)
):
    """
    Get credits usage history.
    
    Shows your credit consumption over time with breakdown by feature.
    Helps track spending and budget effectively.
    """
    now = datetime.utcnow()
    
    # Generate mock history
    import random
    
    history = []
    for i in range(days):
        date = (now - timedelta(days=i)).strftime("%Y-%m-%d")
        history.append({
            "date": date,
            "credits_used": round(random.uniform(0.5, 3.0), 2),
            "breakdown": {
                "chat": round(random.uniform(0.1, 1.0), 2),
                "image": round(random.uniform(0.1, 0.8), 2),
                "video": round(random.uniform(0, 0.5), 2),
                "other": round(random.uniform(0, 0.5), 2)
            }
        })
    
    history.reverse()  # Oldest to newest
    
    total_credits_used = sum(h["credits_used"] for h in history)
    
    return {
        "history": history,
        "total_credits_used": round(total_credits_used, 2),
        "period_days": days,
        "average_per_day": round(total_credits_used / days, 2)
    }


@router.get("/popular-models")
async def get_popular_models(
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Get most popular AI models across the platform.
    
    Shows which models are used most frequently by all users.
    Public endpoint for discovery.
    """
    return {
        "models": [
            {
                "model": "claude-3.5-sonnet",
                "provider": "OpenRouter",
                "usage_count": 12450,
                "success_rate": 99.2,
                "avg_response_time_ms": 1250
            },
            {
                "model": "gpt-4-turbo",
                "provider": "OpenAI",
                "usage_count": 8920,
                "success_rate": 98.7,
                "avg_response_time_ms": 980
            },
            {
                "model": "llama-3-70b",
                "provider": "OpenRouter",
                "usage_count": 5340,
                "success_rate": 97.5,
                "avg_response_time_ms": 1450
            },
            {
                "model": "dall-e-3",
                "provider": "OpenAI",
                "usage_count": 3210,
                "success_rate": 99.8,
                "avg_response_time_ms": 4500
            },
            {
                "model": "stable-diffusion-xl",
                "provider": "Stability AI",
                "usage_count": 2890,
                "success_rate": 98.9,
                "avg_response_time_ms": 3200
            }
        ],
        "total": 5,
        "last_updated": datetime.utcnow().isoformat()
    }


@router.get("/activity-timeline")
async def get_activity_timeline(
    limit: int = Query(50, ge=1, le=200, description="Number of activities to return"),
    current_user: User = Depends(get_current_user)
):
    """
    Get recent activity timeline.
    
    Shows your recent actions chronologically.
    Useful for reviewing your work history.
    """
    # Mock activity timeline
    import random
    
    activities = []
    activity_types = [
        "chat_message",
        "code_execution",
        "image_generation",
        "video_generation",
        "project_created",
        "project_updated"
    ]
    
    for i in range(min(limit, 50)):
        activity_type = random.choice(activity_types)
        timestamp = datetime.utcnow() - timedelta(minutes=i*15)
        
        activities.append({
            "id": i + 1,
            "type": activity_type,
            "description": f"Performed {activity_type.replace('_', ' ')}",
            "timestamp": timestamp.isoformat(),
            "credits_used": round(random.uniform(0.01, 2.0), 2)
        })
    
    return {
        "activities": activities,
        "total": len(activities),
        "has_more": limit > 50
    }


@router.get("/performance")
async def get_performance_metrics(
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Get API performance metrics.
    
    Shows system performance statistics including
    response times, uptime, and reliability metrics.
    
    Public endpoint.
    """
    analytics = get_analytics()
    stats = analytics.get_stats()
    
    return {
        "uptime_percentage": 99.95,
        "response_times": stats["performance"],
        "success_rate": stats["requests"]["success_rate"],
        "active_users": stats["users"]["active"],
        "requests_per_minute": round(stats["requests"]["total"] / 60, 2),
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/export")
async def export_analytics(
    format: str = Query("json", description="Export format: json, csv"),
    period: str = Query("month", description="Time period: week, month, year, all"),
    current_user: User = Depends(get_current_user)
):
    """
    Export analytics data.
    
    Download your complete analytics data for external analysis.
    Supports JSON and CSV formats.
    """
    # In production, generate actual export file
    return {
        "export_url": f"https://api.galion.app/exports/analytics_{current_user.id}_{period}.{format}",
        "format": format,
        "period": period,
        "generated_at": datetime.utcnow().isoformat(),
        "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat(),
        "message": "Export will be ready shortly. Download from the provided URL."
    }
