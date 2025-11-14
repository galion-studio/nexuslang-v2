"""
User model for Galion Platform Backend
Complete SQLAlchemy user model with authentication features.

"Your imagination is the end."
"""

from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from ..core.database import Base


class User(Base):
    """SQLAlchemy User model for authentication and user management"""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    bio = Column(Text)
    website = Column(String(255))
    avatar_url = Column(String(500))

    # Authentication
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_login = Column(DateTime)

    # Password reset
    reset_token = Column(String(255))
    reset_token_expires = Column(DateTime)

    # Email verification
    verification_token = Column(String(255))
    verification_token_expires = Column(DateTime)

    # Credits and billing
    credits = Column(Float, default=0.0)
    subscription_tier = Column(String(50), default='free')

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user_roles = relationship("UserRole", foreign_keys="UserRole.user_id", back_populates="user", cascade="all, delete-orphan")
    beta_profile = relationship("BetaTesterProfile", uselist=False, back_populates="user")
    feedback = relationship("UserFeedback", foreign_keys="UserFeedback.user_id", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    voice_sessions = relationship("VoiceSession", back_populates="user", cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        """Convert user to dictionary for API responses"""
        return {
            "id": str(self.id),
            "email": self.email,
            "username": self.username,
            "full_name": self.full_name,
            "bio": self.bio,
            "website": self.website,
            "avatar_url": self.avatar_url,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "credits": self.credits,
            "subscription_tier": self.subscription_tier,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


# Pydantic models for API
class UserBase(BaseModel):
    """Base user model"""
    email: str
    username: str
    full_name: Optional[str] = None
    bio: Optional[str] = None
    website: Optional[str] = None
    avatar_url: Optional[str] = None

class UserCreate(UserBase):
    """User creation model"""
    password: str

class UserUpdate(UserBase):
    """User update model"""
    pass

class UserResponse(UserBase):
    """User response model"""
    id: str
    is_active: bool
    is_verified: bool
    last_login: Optional[datetime]
    credits: float
    subscription_tier: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# Export classes
__all__ = ["User", "UserCreate", "UserUpdate", "UserResponse", "UserBase"]