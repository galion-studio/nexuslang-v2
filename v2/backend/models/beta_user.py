"""
Beta User Model - Database model for beta testing management
Manages beta user invitations, waitlist, and referral tracking
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from ..core.database import Base


class BetaUser(Base):
    """
    Beta User model for managing beta testing program

    Tracks invitation codes, referral system, and user status
    in the beta testing phase.
    """
    __tablename__ = "beta_users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    invitation_code = Column(String(50), unique=True, nullable=False, index=True)
    invited_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    status = Column(String(20), default="pending", index=True)  # pending, active, completed, banned
    joined_at = Column(DateTime, default=datetime.utcnow)
    feedback_count = Column(Integer, default=0)
    referral_count = Column(Integer, default=0)
    waitlist_position = Column(Integer)
    priority_score = Column(Integer, default=0)  # For waitlist prioritization
    notes = Column(Text)  # Admin notes
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    inviter = relationship("User", foreign_keys=[invited_by])

    def __repr__(self):
        return f"<BetaUser(id={self.id}, user_id={self.user_id}, status={self.status}, invitation_code={self.invitation_code[:8]}...)>"

    @property
    def is_active(self) -> bool:
        """Check if beta user is active"""
        return self.status == "active"

    @property
    def is_pending(self) -> bool:
        """Check if beta user is still pending"""
        return self.status == "pending"

    @property
    def is_completed(self) -> bool:
        """Check if beta user has completed beta testing"""
        return self.status == "completed"

    def activate(self):
        """Activate the beta user"""
        self.status = "active"
        self.joined_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def complete(self):
        """Mark beta testing as completed"""
        self.status = "completed"
        self.updated_at = datetime.utcnow()

    def ban(self):
        """Ban the beta user"""
        self.status = "banned"
        self.updated_at = datetime.utcnow()

    def increment_referral_count(self):
        """Increment referral count when someone joins via this user's invitation"""
        self.referral_count += 1
        self.updated_at = datetime.utcnow()

    def increment_feedback_count(self):
        """Increment feedback count when user submits feedback"""
        self.feedback_count += 1
        self.updated_at = datetime.utcnow()


class BetaInvitation(Base):
    """
    Beta Invitation model for tracking invitation usage
    Separate table for invitation codes that can be used before user registration
    """
    __tablename__ = "beta_invitations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), nullable=False, index=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    used_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    expires_at = Column(DateTime)
    used_at = Column(DateTime)
    is_used = Column(String(1), default="N")  # Y/N for performance
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    user = relationship("User", foreign_keys=[used_by])

    def __repr__(self):
        return f"<BetaInvitation(code={self.code[:8]}..., email={self.email}, used={self.is_used})>"

    @property
    def is_expired(self) -> bool:
        """Check if invitation has expired"""
        return self.expires_at and datetime.utcnow() > self.expires_at

    @property
    def is_available(self) -> bool:
        """Check if invitation is available for use"""
        return not self.is_used == "Y" and not self.is_expired

    def use(self, user_id: uuid.UUID):
        """Mark invitation as used by a user"""
        self.used_by = user_id
        self.used_at = datetime.utcnow()
        self.is_used = "Y"


class BetaWaitlist(Base):
    """
    Beta Waitlist model for managing waitlist positions
    Tracks users who signed up but don't have invitations yet
    """
    __tablename__ = "beta_waitlist"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255))
    signup_source = Column(String(50), default="website")  # website, referral, social, etc.
    priority_score = Column(Integer, default=0)
    position = Column(Integer)
    invited_at = Column(DateTime)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<BetaWaitlist(email={self.email}, position={self.position}, priority={self.priority_score})>"

    @property
    def is_invited(self) -> bool:
        """Check if user has been invited"""
        return self.invited_at is not None

    def invite(self):
        """Mark as invited"""
        self.invited_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()