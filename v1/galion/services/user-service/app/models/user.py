"""
User database model.
Shared with auth service - same table, same schema.
"""

from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

from app.database import Base


class User(Base):
    """
    User model - represents a user in the system.
    
    This is the same table used by auth-service.
    User service can read and update user profiles.
    Only auth-service creates users (registration).
    """
    __tablename__ = "users"
    __table_args__ = {"schema": "public"}
    
    # Primary key - UUID for distributed systems
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # User credentials
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # User profile information
    name = Column(String(255), nullable=False)
    bio = Column(Text, nullable=True)  # User biography/description
    avatar_url = Column(String(500), nullable=True)  # Profile picture URL
    
    # User role and permissions
    role = Column(String(50), default="user", nullable=False)  # user, admin, superadmin
    
    # Account status
    email_verified = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<User {self.email}>"

