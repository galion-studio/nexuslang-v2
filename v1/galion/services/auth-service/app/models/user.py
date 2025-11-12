"""
User database model.
Defines the structure of the users table in PostgreSQL.
"""

from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, Date, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

from app.database import Base


class User(Base):
    """
    User model for authentication and profile management.
    Maps to the public.users table in PostgreSQL.
    
    This table stores:
    - Authentication credentials (email, password hash)
    - User profile information (name, phone, bio)
    - Security settings (MFA, account lockout)
    - Preferences and metadata
    """
    
    __tablename__ = "users"
    __table_args__ = {"schema": "public"}
    
    # Primary key - UUID is better than integer for distributed systems
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Authentication fields
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)  # Never store plain passwords!
    
    # Profile information
    name = Column(String(255), nullable=False)
    phone = Column(String(50))
    bio = Column(Text)
    
    # Role-based access control
    role = Column(String(50), nullable=False, default="user")
    # Possible roles: 'user', 'sponsor', 'affiliate', 'admin', 'superadmin'
    
    # Account status
    status = Column(String(50), nullable=False, default="active")
    # Possible statuses: 'active', 'suspended', 'deleted'
    
    # Email verification
    email_verified = Column(Boolean, default=False)
    
    # Security features
    failed_login_count = Column(Integer, default=0)
    account_locked_until = Column(DateTime(timezone=True))
    
    # Two-Factor Authentication (TOTP) - GitHub-style 2FA
    totp_enabled = Column(Boolean, default=False)
    totp_secret = Column(String(32))  # Base32 encoded TOTP secret
    totp_verified_at = Column(DateTime(timezone=True))  # When 2FA was verified
    backup_codes = Column(JSONB, default=[])
    
    # Age Verification (18+ requirement)
    date_of_birth = Column(Date)  # User's date of birth
    age_verified = Column(Boolean, default=False)  # Has age been verified
    age_verified_at = Column(DateTime(timezone=True))  # When verified
    # is_adult computed in database as: date_of_birth <= CURRENT_DATE - INTERVAL '18 years'
    
    # Subscription and Badge System
    current_plan_id = Column(UUID(as_uuid=True))  # FK to subscription_plans
    badge_name = Column(String(50))  # Explorer, Pioneer, Master, Legend, Titan
    subscription_status = Column(String(20), default="free")  # free, active, cancelled, expired  # Hashed backup/recovery codes
    backup_codes_generated_at = Column(DateTime(timezone=True))
    
    # Preferences - JSONB allows flexible storage without schema changes
    preferences = Column(JSONB, default={})
    
    # Timestamps - always include these for audit trails
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True))
    deleted_at = Column(DateTime(timezone=True))  # Soft delete
    
    def __repr__(self):
        return f"<User {self.email}>"

