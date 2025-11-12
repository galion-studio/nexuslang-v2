"""
Project and file models for IDE.
"""

from sqlalchemy import Column, String, Text, Integer, DateTime, Enum as SQLEnum, LargeBinary
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import enum

from ..core.database import Base


class VisibilityType(str, enum.Enum):
    """Project visibility options."""
    PRIVATE = "private"
    PUBLIC = "public"
    UNLISTED = "unlisted"


class RoleType(str, enum.Enum):
    """Collaboration role types."""
    OWNER = "owner"
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"


class Project(Base):
    """Project model."""
    
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    visibility = Column(SQLEnum(VisibilityType), nullable=False, default=VisibilityType.PRIVATE)
    stars_count = Column(Integer, default=0)
    forks_count = Column(Integer, default=0)
    forked_from = Column(UUID(as_uuid=True), index=True)  # For tracking forks
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class File(Base):
    """File model."""
    
    __tablename__ = "files"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    path = Column(Text, nullable=False)
    content = Column(Text)
    binary_content = Column(LargeBinary)  # For .nxb files
    version = Column(Integer, default=1)
    size_bytes = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Collaborator(Base):
    """Project collaborator model."""
    
    __tablename__ = "collaborators"
    
    project_id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), primary_key=True)
    role = Column(SQLEnum(RoleType), nullable=False, default=RoleType.VIEWER)
    invited_at = Column(DateTime, default=datetime.utcnow)
    accepted_at = Column(DateTime)

