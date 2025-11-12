"""
RBAC (Role-Based Access Control) Models for Project Nexus
Includes: Roles, Permissions, UserRoles, BetaTesterProfiles, FeatureFlags
"""

from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, ForeignKey, ARRAY, JSON, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, INET, JSONB
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from ..core.database import Base


class Role(Base):
    """Role model for RBAC"""
    
    __tablename__ = "roles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False, index=True)
    display_name = Column(String(100), nullable=False)
    description = Column(Text)
    permissions = Column(JSONB, nullable=False, default=list)  # Array of permission strings
    is_system = Column(Boolean, default=False)  # System roles cannot be deleted
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user_roles = relationship("UserRole", back_populates="role", cascade="all, delete-orphan")


class Permission(Base):
    """Permission model"""
    
    __tablename__ = "permissions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource = Column(String(100), nullable=False)  # e.g., "users", "nexuslang"
    action = Column(String(50), nullable=False)     # e.g., "read", "write", "execute"
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('resource', 'action', name='uq_resource_action'),
    )


class UserRole(Base):
    """Many-to-many relationship between Users and Roles"""
    
    __tablename__ = "user_roles"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    assigned_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    expires_at = Column(DateTime, nullable=True)  # Optional expiration
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="user_roles")
    role = relationship("Role", back_populates="user_roles")
    assigned_by_user = relationship("User", foreign_keys=[assigned_by])


class BetaTesterProfile(Base):
    """Beta tester profile with tracking"""
    
    __tablename__ = "beta_tester_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    cohort = Column(String(50))  # "alpha", "beta-1", "beta-2", etc.
    invited_by = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    invited_at = Column(DateTime)
    accepted_at = Column(DateTime)
    onboarding_completed = Column(Boolean, default=False)
    feedback_count = Column(Integer, default=0)
    bugs_reported = Column(Integer, default=0)
    features_tested = Column(JSONB, default=list)  # Array of feature names
    test_assignments = Column(JSONB, default=list)  # Features assigned for testing
    notes = Column(Text)
    status = Column(String(20), default='invited')  # invited, active, inactive, graduated
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="beta_profile")
    invited_by_user = relationship("User", foreign_keys=[invited_by])


class FeatureFlag(Base):
    """Feature flag for gradual rollout"""
    
    __tablename__ = "feature_flags"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(200), nullable=False)
    description = Column(Text)
    enabled = Column(Boolean, default=False)
    rollout_percentage = Column(Integer, default=0)  # 0-100
    target_roles = Column(JSONB, default=list)  # Array of role names
    target_users = Column(JSONB, default=list)  # Array of user IDs
    target_cohorts = Column(JSONB, default=list)  # Array of cohort names
    metadata = Column(JSONB, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserFeedback(Base):
    """User feedback and bug reports"""
    
    __tablename__ = "user_feedback"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    feature_name = Column(String(200))
    feedback_type = Column(String(50), nullable=False)  # bug, feature_request, improvement, praise
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(20))  # critical, high, medium, low
    status = Column(String(50), default='new')  # new, in_review, planned, in_progress, resolved, wont_fix
    attachments = Column(JSONB, default=list)  # Array of file URLs
    metadata = Column(JSONB, default=dict)  # Browser, OS, etc.
    assigned_to = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    resolved_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="feedback")
    assigned_to_user = relationship("User", foreign_keys=[assigned_to])


class AuditLog(Base):
    """Enhanced audit logging"""
    
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'))
    event_type = Column(String(100), nullable=False)  # login, logout, role_assigned, etc.
    resource_type = Column(String(100))  # user, role, permission, etc.
    resource_id = Column(UUID(as_uuid=True))
    action = Column(String(50))  # create, read, update, delete
    details = Column(JSONB, default=dict)
    ip_address = Column(INET)
    user_agent = Column(Text)
    severity = Column(String(20), default='info')  # info, warning, error, critical
    request_id = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")


class APIKey(Base):
    """API key for programmatic access"""
    
    __tablename__ = "api_keys"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    key_hash = Column(String(255), unique=True, nullable=False)  # SHA-256 hash
    key_prefix = Column(String(20), nullable=False)  # For identification
    name = Column(String(200))  # User-friendly name
    permissions = Column(JSONB, default=list)  # Subset of user permissions
    rate_limit_override = Column(Integer)  # Custom rate limit
    last_used_at = Column(DateTime)
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")


# Update User model to include new relationships
# This would be added to v2/backend/models/user.py:
"""
# Add these to User model:
user_roles = relationship("UserRole", foreign_keys="UserRole.user_id", back_populates="user")
beta_profile = relationship("BetaTesterProfile", uselist=False, back_populates="user")
feedback = relationship("UserFeedback", foreign_keys="UserFeedback.user_id", back_populates="user")
audit_logs = relationship("AuditLog", back_populates="user")
api_keys = relationship("APIKey", back_populates="user")
"""

