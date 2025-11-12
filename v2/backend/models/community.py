"""
Community and social feature models.
"""

from sqlalchemy import Column, String, Text, Integer, DateTime, Boolean, ARRAY
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

from ..core.database import Base
class Post(Base):
    """Community post model."""
    
    __tablename__ = "posts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    author_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    category = Column(String(100), default="general")
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    tags = Column(ARRAY(String), default=[])
    upvotes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    views_count = Column(Integer, default=0)
    is_pinned = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Comment(Base):
    """Comment model."""
    
    __tablename__ = "comments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    author_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    parent_id = Column(UUID(as_uuid=True), index=True)
    content = Column(Text, nullable=False)
    upvotes_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Team(Base):
    """Team model."""
    
    __tablename__ = "teams"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    avatar_url = Column(Text)
    owner_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    is_public = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TeamMember(Base):
    """Team member model."""
    
    __tablename__ = "team_members"
    
    team_id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    role = Column(String(20), nullable=False, default="viewer")
    joined_at = Column(DateTime, default=datetime.utcnow)


class Star(Base):
    """Project star model."""
    
    __tablename__ = "stars"
    
    user_id = Column(UUID(as_uuid=True), primary_key=True)
    project_id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

