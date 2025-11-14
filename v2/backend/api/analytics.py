"""
Analytics API Endpoints - Platform analytics and metrics
Provides dashboard data, user analytics, and usage statistics

Endpoints:
- GET /analytics/dashboard - Dashboard metrics
- GET /analytics/users - User analytics
- GET /analytics/voice - Voice usage statistics
- GET /analytics/events - Event tracking data
- POST /analytics/event - Track custom event
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from ..core.database import get_db
from ..models.analytics import AnalyticsEvent, AnalyticsMetric, UserSession, PerformanceMetric
from ..models.user import User
from ..models.voice_session import VoiceSession
from ..core.auth import get_current_user
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, extract

router = APIRouter(prefix="/analytics", tags=["Analytics"])

# Pydantic models
class DashboardMetrics(BaseModel):
    """Dashboard metrics response"""
    total_users: int
    active_users_today: int
    total_sessions: int
    total_commands: int
    average_session_duration: Optional[float]
    top_platform: str
    user_growth: List[Dict[str, Any]]
    session_trends: List[Dict[str, Any]]
    platform_distribution: List[Dict[str, Any]]

class UserAnalytics(BaseModel):
    """User analytics response"""
    total_registered: int
    beta_users: int
    active_users: int
    new_users_today: int
    user_engagement: List[Dict[str, Any]]
    geographic_distribution: List[Dict[str, Any]]

class VoiceAnalytics(BaseModel):
    """Voice usage analytics"""
    total_sessions: int
    total_commands: int
    average_accuracy: Optional[float]
    average_duration: Optional[float]
    commands_per_session: float
    platform_usage: List[Dict[str, Any]]
    hourly_usage: List[Dict[str, Any]]
    top_languages: List[Dict[str, Any]]

class EventData(BaseModel):
    """Event tracking data"""
    event_type: str = Field(..., description="Type of event")
    event_data: Optional[Dict[str, Any]] = Field(default=None, description="Additional event data")
    platform: Optional[str] = Field(default=None, description="Platform where event occurred")
    page_url: Optional[str] = Field(default=None, description="Current page URL")

class EventResponse(BaseModel):
    """Event tracking response"""
    event_id: str
    tracked_at: datetime

@router.get("/dashboard", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    days: int = Query(30, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get dashboard metrics and KPIs

    - **days**: Number of days to analyze (default: 30)
    """
    try:
        # Check admin privileges
        if not getattr(current_user, 'is_admin', False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required"
            )

        since_date = datetime.utcnow() - timedelta(days=days)

        # Basic metrics
        total_users = db.query(func.count(User.id)).scalar()

        active_users_today = db.query(func.count(func.distinct(UserSession.user_id))).filter(
            UserSession.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        ).scalar()

        session_stats = db.query(
            func.count(VoiceSession.id).label('total_sessions'),
            func.sum(VoiceSession.commands_count).label('total_commands'),
            func.avg(VoiceSession.duration_seconds).label('avg_duration')
        ).filter(VoiceSession.started_at >= since_date).first()

        # Top platform
        platform_stats = db.query(
            VoiceSession.platform,
            func.count(VoiceSession.id).label('count')
        ).filter(VoiceSession.started_at >= since_date).group_by(
            VoiceSession.platform
        ).order_by(desc('count')).first()

        # User growth (daily registrations)
        user_growth = db.query(
            func.date(User.created_at).label('date'),
            func.count(User.id).label('count')
        ).filter(User.created_at >= since_date).group_by(
            func.date(User.created_at)
        ).order_by('date').all()

        # Session trends
        session_trends = db.query(
            func.date(VoiceSession.started_at).label('date'),
            func.count(VoiceSession.id).label('sessions'),
            func.sum(VoiceSession.commands_count).label('commands')
        ).filter(VoiceSession.started_at >= since_date).group_by(
            func.date(VoiceSession.started_at)
        ).order_by('date').all()

        # Platform distribution
        platform_dist = db.query(
            VoiceSession.platform,
            func.count(VoiceSession.id).label('sessions'),
            func.sum(VoiceSession.commands_count).label('commands')
        ).filter(VoiceSession.started_at >= since_date).group_by(
            VoiceSession.platform
        ).order_by(desc('sessions')).all()

        return DashboardMetrics(
            total_users=total_users,
            active_users_today=active_users_today,
            total_sessions=session_stats.total_sessions or 0,
            total_commands=session_stats.total_commands or 0,
            average_session_duration=float(session_stats.avg_duration) if session_stats.avg_duration else None,
            top_platform=platform_stats.platform if platform_stats else "unknown",
            user_growth=[
                {"date": str(row.date), "new_users": row.count}
                for row in user_growth
            ],
            session_trends=[
                {"date": str(row.date), "sessions": row.sessions, "commands": row.commands or 0}
                for row in session_trends
            ],
            platform_distribution=[
                {"platform": row.platform, "sessions": row.sessions, "commands": row.commands or 0}
                for row in platform_dist
            ]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get dashboard metrics: {str(e)}"
        )

@router.get("/users", response_model=UserAnalytics)
async def get_user_analytics(
    days: int = Query(30, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user analytics and engagement metrics
    """
    try:
        # Check admin privileges
        if not getattr(current_user, 'is_admin', False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required"
            )

        since_date = datetime.utcnow() - timedelta(days=days)

        # User counts
        total_registered = db.query(func.count(User.id)).scalar()
        beta_users = db.query(func.count(BetaUser.id)).scalar()  # Would need import
        active_users = db.query(func.count(func.distinct(UserSession.user_id))).filter(
            UserSession.created_at >= since_date
        ).scalar()

        new_users_today = db.query(func.count(User.id)).filter(
            User.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        ).scalar()

        # User engagement (daily active users)
        engagement = db.query(
            func.date(UserSession.created_at).label('date'),
            func.count(func.distinct(UserSession.user_id)).label('active_users')
        ).filter(UserSession.created_at >= since_date).group_by(
            func.date(UserSession.created_at)
        ).order_by('date').all()

        # Geographic distribution (placeholder - would need IP geolocation)
        geographic_dist = [
            {"country": "United States", "users": 1250},
            {"country": "United Kingdom", "users": 340},
            {"country": "Germany", "users": 280},
            {"country": "Canada", "users": 195},
            {"country": "Australia", "users": 120}
        ]

        return UserAnalytics(
            total_registered=total_registered,
            beta_users=beta_users,
            active_users=active_users,
            new_users_today=new_users_today,
            user_engagement=[
                {"date": str(row.date), "active_users": row.active_users}
                for row in engagement
            ],
            geographic_distribution=geographic_dist
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user analytics: {str(e)}"
        )

@router.get("/voice", response_model=VoiceAnalytics)
async def get_voice_analytics(
    days: int = Query(30, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get voice usage analytics and statistics
    """
    try:
        # Check admin privileges
        if not getattr(current_user, 'is_admin', False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required"
            )

        since_date = datetime.utcnow() - timedelta(days=days)

        # Voice session statistics
        session_stats = db.query(
            func.count(VoiceSession.id).label('total_sessions'),
            func.sum(VoiceSession.commands_count).label('total_commands'),
            func.avg(VoiceSession.transcription_accuracy).label('avg_accuracy'),
            func.avg(VoiceSession.duration_seconds).label('avg_duration')
        ).filter(VoiceSession.started_at >= since_date).first()

        commands_per_session = (
            session_stats.total_commands / session_stats.total_sessions
            if session_stats.total_sessions and session_stats.total_sessions > 0
            else 0
        )

        # Platform usage
        platform_usage = db.query(
            VoiceSession.platform,
            func.count(VoiceSession.id).label('sessions'),
            func.sum(VoiceSession.commands_count).label('commands'),
            func.avg(VoiceSession.transcription_accuracy).label('avg_accuracy')
        ).filter(VoiceSession.started_at >= since_date).group_by(
            VoiceSession.platform
        ).order_by(desc('sessions')).all()

        # Hourly usage patterns
        hourly_usage = db.query(
            extract('hour', VoiceSession.started_at).label('hour'),
            func.count(VoiceSession.id).label('sessions')
        ).filter(VoiceSession.started_at >= since_date).group_by(
            extract('hour', VoiceSession.started_at)
        ).order_by('hour').all()

        # Top languages
        language_usage = db.query(
            VoiceSession.language,
            func.count(VoiceSession.id).label('sessions')
        ).filter(
            and_(VoiceSession.started_at >= since_date, VoiceSession.language.isnot(None))
        ).group_by(VoiceSession.language).order_by(desc('sessions')).limit(10).all()

        return VoiceAnalytics(
            total_sessions=session_stats.total_sessions or 0,
            total_commands=session_stats.total_commands or 0,
            average_accuracy=float(session_stats.avg_accuracy) if session_stats.avg_accuracy else None,
            average_duration=float(session_stats.avg_duration) if session_stats.avg_duration else None,
            commands_per_session=commands_per_session,
            platform_usage=[
                {
                    "platform": row.platform,
                    "sessions": row.sessions,
                    "commands": row.commands or 0,
                    "avg_accuracy": float(row.avg_accuracy) if row.avg_accuracy else None
                }
                for row in platform_usage
            ],
            hourly_usage=[
                {"hour": int(row.hour), "sessions": row.sessions}
                for row in hourly_usage
            ],
            top_languages=[
                {"language": row.language, "sessions": row.sessions}
                for row in language_usage
            ]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get voice analytics: {str(e)}"
        )

@router.post("/event", response_model=EventResponse)
async def track_event(
    event: EventData,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Track a custom analytics event

    - **event_type**: Type of event (click, view, submit, etc.)
    - **event_data**: Additional structured data
    - **platform**: Platform where event occurred
    - **page_url**: Current page URL
    """
    try:
        # Create analytics event
        analytics_event = AnalyticsEvent(
            user_id=current_user.id,
            event_type=event.event_type,
            event_category="user_interaction",  # Default category
            event_action=event.event_type,
            event_data=event.event_data,
            platform=event.platform,
            page_url=event.page_url
        )

        db.add(analytics_event)
        db.commit()
        db.refresh(analytics_event)

        return EventResponse(
            event_id=str(analytics_event.id),
            tracked_at=analytics_event.created_at
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to track event: {str(e)}"
        )

@router.get("/events")
async def get_events(
    event_type: Optional[str] = None,
    platform: Optional[str] = None,
    limit: int = Query(100, description="Maximum events to return"),
    offset: int = Query(0, description="Number of events to skip"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get analytics events with optional filtering

    - **event_type**: Filter by event type
    - **platform**: Filter by platform
    - **limit**: Maximum events to return
    - **offset**: Number of events to skip
    """
    try:
        # Check admin privileges
        if not getattr(current_user, 'is_admin', False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required"
            )

        # Build query
        query = db.query(AnalyticsEvent)

        if event_type:
            query = query.filter(AnalyticsEvent.event_type == event_type)
        if platform:
            query = query.filter(AnalyticsEvent.platform == platform)

        events = query.order_by(desc(AnalyticsEvent.created_at)).limit(limit).offset(offset).all()

        return {
            "events": [
                {
                    "id": str(event.id),
                    "user_id": str(event.user_id),
                    "event_type": event.event_type,
                    "event_data": event.event_data,
                    "platform": event.platform,
                    "created_at": event.created_at
                }
                for event in events
            ],
            "total": len(events)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get events: {str(e)}"
        )

# Import required models
try:
    from ..models.beta_user import BetaUser
except ImportError:
    # Fallback for when beta user model is not available
    class BetaUser:
        id = None

# Fallback auth import
try:
    from ..core.auth import get_current_user
except ImportError:
    async def get_current_user():
        raise HTTPException(status_code=501, detail="Authentication not implemented")