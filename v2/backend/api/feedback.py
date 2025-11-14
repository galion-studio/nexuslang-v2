"""
Feedback API Endpoints - User feedback collection and management
Handles feedback submission, voting, and admin management

Endpoints:
- POST /feedback - Submit feedback
- GET /feedback - Get user's feedback
- GET /feedback/admin - Admin feedback view
- PUT /feedback/{id} - Update feedback status
- POST /feedback/{id}/vote - Vote on feedback
- GET /feedback/stats - Feedback statistics
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from ..core.database import get_db
from ..models.feedback import Feedback, FeedbackVote, FeedbackCategory
from ..models.user import User
from ..core.auth import get_current_user
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_

router = APIRouter(prefix="/feedback", tags=["Feedback"])

# Pydantic models
class FeedbackSubmission(BaseModel):
    """Feedback submission request"""
    category: str = Field(..., description="Feedback category (bug, feature, improvement, general, other)")
    title: Optional[str] = Field(None, max_length=200, description="Brief title (optional)")
    comment: str = Field(..., min_length=1, max_length=5000, description="Detailed feedback comment")
    rating: Optional[int] = Field(None, ge=1, le=5, description="Rating 1-5 (optional)")
    platform: Optional[str] = Field(None, description="Platform where feedback originated")
    page_url: Optional[str] = Field(None, description="URL where feedback was submitted")
    is_anonymous: bool = Field(default=False, description="Submit anonymously")

class FeedbackUpdate(BaseModel):
    """Feedback update request (admin only)"""
    status: Optional[str] = Field(None, description="New status")
    priority: Optional[str] = Field(None, description="New priority")
    admin_response: Optional[str] = Field(None, description="Admin response")
    tags: Optional[List[str]] = Field(None, description="Tags for categorization")

class FeedbackResponse(BaseModel):
    """Feedback response model"""
    id: str
    user_id: Optional[str]
    category: str
    subcategory: Optional[str]
    title: Optional[str]
    comment: str
    rating: Optional[int]
    status: str
    priority: str
    platform: Optional[str]
    upvotes: int
    is_public: bool
    is_anonymous: bool
    created_at: datetime
    updated_at: datetime
    admin_response: Optional[str]
    responded_at: Optional[datetime]
    category_name: Optional[str]
    category_color: Optional[str]

class FeedbackVoteRequest(BaseModel):
    """Feedback vote request"""
    vote_type: str = Field(..., description="Vote type (upvote, downvote)")

class FeedbackStats(BaseModel):
    """Feedback statistics"""
    total_feedback: int
    new_feedback: int
    resolved_feedback: int
    average_rating: Optional[float]
    category_breakdown: List[Dict[str, Any]]
    platform_breakdown: List[Dict[str, Any]]
    recent_activity: List[Dict[str, Any]]

@router.post("", response_model=FeedbackResponse)
async def submit_feedback(
    feedback: FeedbackSubmission,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit user feedback

    - **category**: Feedback category
    - **title**: Brief title (optional)
    - **comment**: Detailed feedback
    - **rating**: Rating 1-5 (optional)
    - **platform**: Platform where feedback originated
    - **is_anonymous**: Submit anonymously
    """
    try:
        # Validate category
        valid_categories = ['bug', 'feature', 'improvement', 'general', 'other']
        if feedback.category not in valid_categories:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid category. Must be one of: {', '.join(valid_categories)}"
            )

        # Create feedback entry
        feedback_entry = Feedback(
            user_id=None if feedback.is_anonymous else current_user.id,
            category=feedback.category,
            title=feedback.title,
            comment=feedback.comment,
            rating=feedback.rating,
            platform=feedback.platform,
            page_url=feedback.page_url,
            is_anonymous=feedback.is_anonymous
        )

        db.add(feedback_entry)
        db.commit()
        db.refresh(feedback_entry)

        # Get category info
        category_info = db.query(FeedbackCategory).filter(
            FeedbackCategory.name == feedback.category
        ).first()

        return FeedbackResponse(
            id=str(feedback_entry.id),
            user_id=None if feedback.is_anonymous else str(current_user.id),
            category=feedback_entry.category,
            title=feedback_entry.title,
            comment=feedback_entry.comment,
            rating=feedback_entry.rating,
            status=feedback_entry.status,
            priority=feedback_entry.priority,
            platform=feedback_entry.platform,
            upvotes=feedback_entry.upvotes,
            is_public=feedback_entry.is_public,
            is_anonymous=feedback_entry.is_anonymous,
            created_at=feedback_entry.created_at,
            updated_at=feedback_entry.updated_at,
            admin_response=feedback_entry.admin_response,
            responded_at=feedback_entry.responded_at,
            category_name=category_info.display_name if category_info else None,
            category_color=category_info.color if category_info else None
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit feedback: {str(e)}"
        )

@router.get("", response_model=List[FeedbackResponse])
async def get_user_feedback(
    limit: int = Query(20, description="Maximum feedback items to return"),
    offset: int = Query(0, description="Number of feedback items to skip"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's feedback history
    """
    try:
        feedback_items = db.query(Feedback).filter(
            Feedback.user_id == current_user.id
        ).order_by(desc(Feedback.created_at)).limit(limit).offset(offset).all()

        # Get category info
        categories = {cat.name: cat for cat in db.query(FeedbackCategory).all()}

        return [
            FeedbackResponse(
                id=str(fb.id),
                user_id=str(fb.user_id),
                category=fb.category,
                subcategory=fb.subcategory,
                title=fb.title,
                comment=fb.comment,
                rating=fb.rating,
                status=fb.status,
                priority=fb.priority,
                platform=fb.platform,
                upvotes=fb.upvotes,
                is_public=fb.is_public,
                is_anonymous=fb.is_anonymous,
                created_at=fb.created_at,
                updated_at=fb.updated_at,
                admin_response=fb.admin_response,
                responded_at=fb.responded_at,
                category_name=categories.get(fb.category).display_name if fb.category in categories else None,
                category_color=categories.get(fb.category).color if fb.category in categories else None
            )
            for fb in feedback_items
        ]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user feedback: {str(e)}"
        )

@router.get("/admin", response_model=List[FeedbackResponse])
async def get_all_feedback_admin(
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    category_filter: Optional[str] = Query(None, description="Filter by category"),
    priority_filter: Optional[str] = Query(None, description="Filter by priority"),
    limit: int = Query(50, description="Maximum feedback items to return"),
    offset: int = Query(0, description="Number of feedback items to skip"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all feedback for admin management (admin only)
    """
    try:
        # Check admin privileges
        if not getattr(current_user, 'is_admin', False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required"
            )

        # Build query
        query = db.query(Feedback)

        if status_filter:
            query = query.filter(Feedback.status == status_filter)
        if category_filter:
            query = query.filter(Feedback.category == category_filter)
        if priority_filter:
            query = query.filter(Feedback.priority == priority_filter)

        feedback_items = query.order_by(desc(Feedback.created_at)).limit(limit).offset(offset).all()

        # Get category and user info
        categories = {cat.name: cat for cat in db.query(FeedbackCategory).all()}
        users = {user.id: user for user in db.query(User).filter(
            User.id.in_([fb.user_id for fb in feedback_items if fb.user_id])
        ).all()}

        return [
            FeedbackResponse(
                id=str(fb.id),
                user_id=str(fb.user_id) if fb.user_id else None,
                category=fb.category,
                subcategory=fb.subcategory,
                title=fb.title,
                comment=fb.comment,
                rating=fb.rating,
                status=fb.status,
                priority=fb.priority,
                platform=fb.platform,
                upvotes=fb.upvotes,
                is_public=fb.is_public,
                is_anonymous=fb.is_anonymous,
                created_at=fb.created_at,
                updated_at=fb.updated_at,
                admin_response=fb.admin_response,
                responded_at=fb.responded_at,
                category_name=categories.get(fb.category).display_name if fb.category in categories else None,
                category_color=categories.get(fb.category).color if fb.category in categories else None
            )
            for fb in feedback_items
        ]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get feedback: {str(e)}"
        )

@router.put("/{feedback_id}", response_model=FeedbackResponse)
async def update_feedback(
    feedback_id: str,
    update: FeedbackUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update feedback status and response (admin only)
    """
    try:
        # Check admin privileges
        if not getattr(current_user, 'is_admin', False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required"
            )

        # Get feedback
        feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
        if not feedback:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Feedback not found"
            )

        # Update fields
        update_data = {}
        if update.status is not None:
            valid_statuses = ['new', 'reviewed', 'in_progress', 'resolved', 'closed', 'rejected']
            if update.status not in valid_statuses:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
                )
            update_data['status'] = update.status

        if update.priority is not None:
            valid_priorities = ['low', 'medium', 'high', 'urgent']
            if update.priority not in valid_priorities:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid priority. Must be one of: {', '.join(valid_priorities)}"
                )
            update_data['priority'] = update.priority

        if update.admin_response is not None:
            update_data['admin_response'] = update.admin_response
            update_data['responded_by'] = current_user.id
            update_data['responded_at'] = datetime.utcnow()

        if update.tags is not None:
            update_data['tags'] = update.tags

        if update_data:
            update_data['updated_at'] = datetime.utcnow()
            db.query(Feedback).filter(Feedback.id == feedback_id).update(update_data)
            db.commit()

            # Refresh feedback object
            db.refresh(feedback)

        # Get category info
        category_info = db.query(FeedbackCategory).filter(
            FeedbackCategory.name == feedback.category
        ).first()

        return FeedbackResponse(
            id=str(feedback.id),
            user_id=str(feedback.user_id) if feedback.user_id else None,
            category=feedback.category,
            subcategory=feedback.subcategory,
            title=feedback.title,
            comment=feedback.comment,
            rating=feedback.rating,
            status=feedback.status,
            priority=feedback.priority,
            platform=feedback.platform,
            upvotes=feedback.upvotes,
            is_public=feedback.is_public,
            is_anonymous=feedback.is_anonymous,
            created_at=feedback.created_at,
            updated_at=feedback.updated_at,
            admin_response=feedback.admin_response,
            responded_at=feedback.responded_at,
            category_name=category_info.display_name if category_info else None,
            category_color=category_info.color if category_info else None
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update feedback: {str(e)}"
        )

@router.post("/{feedback_id}/vote")
async def vote_on_feedback(
    feedback_id: str,
    vote: FeedbackVoteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Vote on feedback (upvote/downvote)
    """
    try:
        # Validate vote type
        if vote.vote_type not in ['upvote', 'downvote']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vote type must be 'upvote' or 'downvote'"
            )

        # Check if feedback exists
        feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
        if not feedback:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Feedback not found"
            )

        # Check if user already voted
        existing_vote = db.query(FeedbackVote).filter(
            and_(
                FeedbackVote.feedback_id == feedback_id,
                FeedbackVote.user_id == current_user.id
            )
        ).first()

        if existing_vote:
            # Update existing vote
            existing_vote.vote_type = vote.vote_type
            existing_vote.created_at = datetime.utcnow()
        else:
            # Create new vote
            new_vote = FeedbackVote(
                feedback_id=feedback_id,
                user_id=current_user.id,
                vote_type=vote.vote_type
            )
            db.add(new_vote)

        db.commit()

        return {
            "message": "Vote recorded successfully",
            "vote_type": vote.vote_type,
            "feedback_id": feedback_id
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to vote on feedback: {str(e)}"
        )

@router.get("/stats", response_model=FeedbackStats)
async def get_feedback_stats(
    days: int = Query(30, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get feedback statistics (admin only)
    """
    try:
        # Check admin privileges
        if not getattr(current_user, 'is_admin', False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required"
            )

        since_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days)

        # Basic stats
        total_feedback = db.query(func.count(Feedback.id)).filter(
            Feedback.created_at >= since_date
        ).scalar()

        new_feedback = db.query(func.count(Feedback.id)).filter(
            and_(
                Feedback.status == 'new',
                Feedback.created_at >= since_date
            )
        ).scalar()

        resolved_feedback = db.query(func.count(Feedback.id)).filter(
            and_(
                Feedback.status.in_(['resolved', 'closed']),
                Feedback.created_at >= since_date
            )
        ).scalar()

        avg_rating = db.query(func.avg(Feedback.rating)).filter(
            and_(
                Feedback.rating.isnot(None),
                Feedback.created_at >= since_date
            )
        ).scalar()

        # Category breakdown
        category_stats = db.query(
            Feedback.category,
            func.count(Feedback.id).label('count')
        ).filter(Feedback.created_at >= since_date).group_by(
            Feedback.category
        ).order_by(desc('count')).all()

        # Platform breakdown
        platform_stats = db.query(
            Feedback.platform,
            func.count(Feedback.id).label('count')
        ).filter(
            and_(
                Feedback.platform.isnot(None),
                Feedback.created_at >= since_date
            )
        ).group_by(Feedback.platform).order_by(desc('count')).all()

        # Recent activity (last 7 days)
        recent_activity = db.query(
            func.date(Feedback.created_at).label('date'),
            func.count(Feedback.id).label('count')
        ).filter(Feedback.created_at >= since_date).group_by(
            func.date(Feedback.created_at)
        ).order_by('date').all()

        return FeedbackStats(
            total_feedback=total_feedback,
            new_feedback=new_feedback,
            resolved_feedback=resolved_feedback,
            average_rating=float(avg_rating) if avg_rating else None,
            category_breakdown=[
                {"category": row.category, "count": row.count}
                for row in category_stats
            ],
            platform_breakdown=[
                {"platform": row.platform, "count": row.count}
                for row in platform_stats
            ],
            recent_activity=[
                {"date": str(row.date), "count": row.count}
                for row in recent_activity
            ]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get feedback stats: {str(e)}"
        )

# Fallback auth import
try:
    from ..core.auth import get_current_user
except ImportError:
    async def get_current_user():
        raise HTTPException(status_code=501, detail="Authentication not implemented")
