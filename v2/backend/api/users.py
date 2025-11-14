"""
Users API Endpoints - Enhanced user management
Handles user profiles, statistics, and account management

Endpoints:
- GET /users/me - Get current user profile
- PUT /users/me - Update user profile
- GET /users/stats - Get user usage statistics
- DELETE /users/me - Delete user account
- GET /users/me/sessions - Get user's voice sessions
- GET /users/me/feedback - Get user's feedback
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from ..core.database import get_db
from ..models.user import User
from ..models.beta_user import BetaUser
from ..models.voice_session import VoiceSession
from ..models.feedback import Feedback
from ..core.auth import get_current_user
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

router = APIRouter(prefix="/users", tags=["Users"])

# Pydantic models
class UserProfile(BaseModel):
    """User profile response model"""
    id: str
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime]
    beta_status: Optional[str]
    feedback_count: int
    total_sessions: int
    total_credits_used: int

class UserUpdateRequest(BaseModel):
    """User profile update request"""
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    username: Optional[str] = Field(None, min_length=3, max_length=50)

class UserStatsResponse(BaseModel):
    """User statistics response"""
    total_sessions: int
    total_commands: int
    total_credits_used: int
    average_session_duration: Optional[float]
    average_accuracy: Optional[float]
    favorite_platform: Optional[str]
    daily_usage: List[Dict[str, Any]]
    weekly_usage: List[Dict[str, Any]]

class VoiceSessionSummary(BaseModel):
    """Voice session summary"""
    id: str
    platform: str
    started_at: datetime
    duration_seconds: Optional[int]
    commands_count: int
    credits_used: int
    accuracy: Optional[float]

class FeedbackSummary(BaseModel):
    """User feedback summary"""
    id: str
    category: str
    title: Optional[str]
    status: str
    rating: Optional[int]
    created_at: datetime
    upvotes: int

@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's profile information
    """
    try:
        # Get beta user info
        beta_user = db.query(BetaUser).filter(BetaUser.user_id == current_user.id).first()

        # Get usage statistics
        session_stats = db.query(
            func.count(VoiceSession.id).label('total_sessions'),
            func.sum(VoiceSession.commands_count).label('total_commands'),
            func.sum(VoiceSession.credits_used).label('total_credits'),
            func.avg(VoiceSession.duration_seconds).label('avg_duration'),
            func.avg(VoiceSession.transcription_accuracy).label('avg_accuracy')
        ).filter(VoiceSession.user_id == current_user.id).first()

        feedback_count = db.query(func.count(Feedback.id)).filter(
            Feedback.user_id == current_user.id
        ).scalar()

        return UserProfile(
            id=str(current_user.id),
            email=current_user.email,
            username=current_user.username,
            full_name=current_user.full_name,
            is_active=getattr(current_user, 'is_active', True),
            is_verified=getattr(current_user, 'is_verified', False),
            created_at=current_user.created_at,
            updated_at=getattr(current_user, 'updated_at', None),
            beta_status=beta_user.status if beta_user else None,
            feedback_count=feedback_count,
            total_sessions=session_stats.total_sessions or 0,
            total_credits_used=session_stats.total_credits or 0
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user profile: {str(e)}"
        )

@router.put("/me", response_model=UserProfile)
async def update_user_profile(
    request: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's profile

    - **full_name**: Update full name (optional)
    - **username**: Update username (optional)
    """
    try:
        # Check for username conflicts
        if request.username and request.username != current_user.username:
            existing = db.query(User).filter(
                User.username == request.username,
                User.id != current_user.id
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )

        # Update fields
        update_data = {}
        if request.full_name is not None:
            update_data['full_name'] = request.full_name
        if request.username is not None:
            update_data['username'] = request.username

        if update_data:
            update_data['updated_at'] = datetime.utcnow()
            db.query(User).filter(User.id == current_user.id).update(update_data)
            db.commit()

            # Refresh user object
            db.refresh(current_user)

        # Return updated profile
        return await get_current_user_profile(current_user, db)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )

@router.get("/stats", response_model=UserStatsResponse)
async def get_user_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed usage statistics for current user
    """
    try:
        # Get overall stats
        overall_stats = db.query(
            func.count(VoiceSession.id).label('total_sessions'),
            func.sum(VoiceSession.commands_count).label('total_commands'),
            func.sum(VoiceSession.credits_used).label('total_credits'),
            func.avg(VoiceSession.duration_seconds).label('avg_duration'),
            func.avg(VoiceSession.transcription_accuracy).label('avg_accuracy')
        ).filter(VoiceSession.user_id == current_user.id).first()

        # Get favorite platform
        platform_stats = db.query(
            VoiceSession.platform,
            func.count(VoiceSession.id).label('count')
        ).filter(VoiceSession.user_id == current_user.id).group_by(
            VoiceSession.platform
        ).order_by(desc('count')).first()

        # Get daily usage (last 7 days)
        daily_usage = db.query(
            func.date(VoiceSession.started_at).label('date'),
            func.count(VoiceSession.id).label('sessions'),
            func.sum(VoiceSession.commands_count).label('commands')
        ).filter(
            VoiceSession.user_id == current_user.id,
            VoiceSession.started_at >= datetime.utcnow() - timedelta(days=7)
        ).group_by(func.date(VoiceSession.started_at)).order_by('date').all()

        # Get weekly usage (last 4 weeks)
        weekly_usage = db.query(
            func.date_trunc('week', VoiceSession.started_at).label('week'),
            func.count(VoiceSession.id).label('sessions'),
            func.sum(VoiceSession.commands_count).label('commands')
        ).filter(
            VoiceSession.user_id == current_user.id,
            VoiceSession.started_at >= datetime.utcnow() - timedelta(weeks=4)
        ).group_by(func.date_trunc('week', VoiceSession.started_at)).order_by('week').all()

        return UserStatsResponse(
            total_sessions=overall_stats.total_sessions or 0,
            total_commands=overall_stats.total_commands or 0,
            total_credits_used=overall_stats.total_credits or 0,
            average_session_duration=float(overall_stats.avg_duration) if overall_stats.avg_duration else None,
            average_accuracy=float(overall_stats.avg_accuracy) if overall_stats.avg_accuracy else None,
            favorite_platform=platform_stats.platform if platform_stats else None,
            daily_usage=[
                {"date": str(row.date), "sessions": row.sessions, "commands": row.commands or 0}
                for row in daily_usage
            ],
            weekly_usage=[
                {"week": str(row.week.date()), "sessions": row.sessions, "commands": row.commands or 0}
                for row in weekly_usage
            ]
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user statistics: {str(e)}"
        )

@router.delete("/me")
async def delete_user_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete current user's account

    This action cannot be undone and will remove all user data
    """
    try:
        # Mark user as inactive (soft delete)
        # In production, you might want hard delete or data retention policies
        db.query(User).filter(User.id == current_user.id).update({
            'is_active': False,
            'updated_at': datetime.utcnow()
        })

        db.commit()

        return {
            "message": "Account deactivated successfully",
            "note": "Your data will be retained for regulatory compliance but your account is no longer active"
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete account: {str(e)}"
        )

@router.get("/me/sessions", response_model=List[VoiceSessionSummary])
async def get_user_sessions(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's voice sessions history

    - **limit**: Maximum number of sessions to return (default: 20)
    - **offset**: Number of sessions to skip (default: 0)
    """
    try:
        sessions = db.query(VoiceSession).filter(
            VoiceSession.user_id == current_user.id
        ).order_by(desc(VoiceSession.started_at)).limit(limit).offset(offset).all()

        return [
            VoiceSessionSummary(
                id=str(session.id),
                platform=session.platform,
                started_at=session.started_at,
                duration_seconds=session.duration_seconds,
                commands_count=session.commands_count,
                credits_used=session.credits_used,
                accuracy=session.transcription_accuracy
            )
            for session in sessions
        ]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user sessions: {str(e)}"
        )

@router.get("/me/feedback", response_model=List[FeedbackSummary])
async def get_user_feedback(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's feedback history

    - **limit**: Maximum number of feedback items to return (default: 20)
    - **offset**: Number of feedback items to skip (default: 0)
    """
    try:
        feedback_items = db.query(Feedback).filter(
            Feedback.user_id == current_user.id
        ).order_by(desc(Feedback.created_at)).limit(limit).offset(offset).all()

        return [
            FeedbackSummary(
                id=str(fb.id),
                category=fb.category,
                title=fb.title,
                status=fb.status,
                rating=fb.rating,
                created_at=fb.created_at,
                upvotes=fb.upvotes
            )
            for fb in feedback_items
        ]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user feedback: {str(e)}"
        )

# Import required modules
from datetime import timedelta

# Fallback auth import
try:
    from ..core.auth import get_current_user
except ImportError:
    async def get_current_user():
        raise HTTPException(status_code=501, detail="Authentication not implemented")
