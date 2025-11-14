"""
Feedback Model - Database model for user feedback collection
Manages user ratings, comments, and feature requests
"""

from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from ..core.database import Base


class Feedback(Base):
    """
    Feedback model for collecting user feedback and ratings

    Supports different feedback categories and tracks resolution status
    """
    __tablename__ = "feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category = Column(String(50), nullable=False, index=True)  # bug, feature, improvement, general, other
    subcategory = Column(String(100))  # More specific categorization
    rating = Column(Integer)  # 1-5 star rating (optional)
    title = Column(String(200))  # Brief title/summary
    comment = Column(Text, nullable=False)  # Detailed feedback
    status = Column(String(20), default="new", index=True)  # new, reviewed, in_progress, resolved, closed, rejected
    priority = Column(String(10), default="medium")  # low, medium, high, urgent
    platform = Column(String(50))  # galion-app, developer-platform, galion-studio
    page_url = Column(String(500))  # URL where feedback was submitted
    user_agent = Column(Text)  # Browser/client information
    attachments = Column(JSONB)  # URLs to attached files/images
    tags = Column(JSONB)  # Custom tags for categorization
    metadata = Column(JSONB)  # Additional metadata
    admin_response = Column(Text)  # Admin's response to feedback
    responded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    responded_at = Column(DateTime)
    upvotes = Column(Integer, default=0)  # Community upvotes
    is_public = Column(Boolean, default=False)  # Whether feedback is visible to other users
    is_anonymous = Column(Boolean, default=False)  # Whether user wants to remain anonymous
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    responder = relationship("User", foreign_keys=[responded_by])

    def __repr__(self):
        return f"<Feedback(id={self.id}, user_id={self.user_id}, category={self.category}, status={self.status})>"

    @property
    def is_resolved(self) -> bool:
        """Check if feedback has been resolved"""
        return self.status in ["resolved", "closed"]

    @property
    def is_pending(self) -> bool:
        """Check if feedback is still pending"""
        return self.status in ["new", "reviewed", "in_progress"]

    @property
    def days_old(self) -> int:
        """Get age of feedback in days"""
        return (datetime.utcnow() - self.created_at).days

    def respond(self, response: str, responder_id: uuid.UUID):
        """Add admin response to feedback"""
        self.admin_response = response
        self.responded_by = responder_id
        self.responded_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def change_status(self, new_status: str):
        """Change feedback status"""
        valid_statuses = ["new", "reviewed", "in_progress", "resolved", "closed", "rejected"]
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid status: {new_status}")
        self.status = new_status
        self.updated_at = datetime.utcnow()

    def upvote(self):
        """Increment upvote count"""
        self.upvotes += 1
        self.updated_at = datetime.utcnow()

    def make_public(self):
        """Make feedback visible to other users"""
        self.is_public = True
        self.updated_at = datetime.utcnow()


class FeedbackAttachment(Base):
    """
    Feedback Attachment model for file attachments
    """
    __tablename__ = "feedback_attachments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    feedback_id = Column(UUID(as_uuid=True), ForeignKey("feedback.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_url = Column(String(500), nullable=False)
    file_type = Column(String(50))  # image, video, document, etc.
    file_size = Column(Integer)  # Size in bytes
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    feedback = relationship("Feedback")

    def __repr__(self):
        return f"<FeedbackAttachment(id={self.id}, feedback_id={self.feedback_id}, filename={self.filename})>"


class FeedbackVote(Base):
    """
    Feedback Vote model for tracking upvotes
    """
    __tablename__ = "feedback_votes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    feedback_id = Column(UUID(as_uuid=True), ForeignKey("feedback.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    vote_type = Column(String(10), default="upvote")  # upvote, downvote
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    feedback = relationship("Feedback")
    user = relationship("User")

    def __repr__(self):
        return f"<FeedbackVote(feedback_id={self.feedback_id}, user_id={self.user_id}, type={self.vote_type})>"


class FeedbackCategory(Base):
    """
    Feedback Category model for organizing feedback types
    """
    __tablename__ = "feedback_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False)
    display_name = Column(String(100), nullable=False)
    description = Column(Text)
    icon = Column(String(50))  # Icon identifier
    color = Column(String(7))  # Hex color code
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<FeedbackCategory(name={self.name}, display_name={self.display_name})>"
