"""
Research models for Deep Search system.
Handles research sessions, bookmarks, and user research data.
"""

from sqlalchemy import Column, String, Text, Integer, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from .base import Base


class ResearchSession(Base):
    """
    Model for storing complete research sessions.

    Stores all data from a research query including:
    - Original query and parameters
    - Generated response and sources
    - Performance metrics
    - User metadata and tags
    """

    __tablename__ = "research_sessions"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)

    # Research parameters
    query = Column(Text, nullable=False)
    persona = Column(String(50), default="default")
    depth = Column(String(20), default="comprehensive")

    # Research results
    synthesized_answer = Column(Text, nullable=False)
    sources_used = Column(JSON, default=list)  # List of source objects
    confidence_score = Column(Float, default=0.0)
    processing_time = Column(Float, default=0.0)

    # Metadata
    metadata = Column(JSON, default=dict)  # Additional research metadata
    tags = Column(JSON, default=list)  # User-defined tags

    # Status
    is_bookmarked = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="research_sessions")
    bookmarks = relationship("ResearchBookmark", back_populates="research_session")

    def __repr__(self):
        return f"<ResearchSession(id='{self.id}', query='{self.query[:50]}...', user_id='{self.user_id}')>"


class ResearchBookmark(Base):
    """
    Model for storing bookmarked research sessions.

    Allows users to save important research findings with:
    - Custom titles and descriptions
    - Categorization and tagging
    - Importance levels
    - Personal notes
    """

    __tablename__ = "research_bookmarks"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    session_id = Column(String, ForeignKey("research_sessions.id"), nullable=False, index=True)

    # Bookmark metadata
    title = Column(String(200), nullable=False)
    description = Column(Text, default="")
    category = Column(String(50), default="general")  # research, learning, work, personal, etc.
    importance = Column(String(20), default="medium")  # low, medium, high, critical

    # Organization
    tags = Column(JSON, default=list)  # Additional tags for organization
    notes = Column(JSON, default=dict)  # Personal notes and annotations

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="research_bookmarks")
    research_session = relationship("ResearchSession", back_populates="bookmarks")

    def __repr__(self):
        return f"<ResearchBookmark(id='{self.id}', title='{self.title}', user_id='{self.user_id}')>"


class ResearchTag(Base):
    """
    Model for research tags and categorization.

    Provides structured tagging system for:
    - Research topics
    - User-defined categories
    - Collaborative tagging
    """

    __tablename__ = "research_tags"

    id = Column(String, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True, index=True)
    description = Column(Text, default="")
    color = Column(String(7), default="#007bff")  # Hex color code
    is_system_tag = Column(Boolean, default=False)  # System vs user-defined tags

    # Usage statistics
    usage_count = Column(Integer, default=0)
    created_by = Column(String, ForeignKey("users.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone(timezone=True), onupdate=func.now())

    # Relationships
    creator = relationship("User")

    def __repr__(self):
        return f"<ResearchTag(id='{self.id}', name='{self.name}', usage_count={self.usage_count})>"


class ResearchTemplate(Base):
    """
    Model for research templates.

    Pre-defined research workflows for common tasks:
    - Academic research
    - Technical documentation
    - Comparative analysis
    - Quick fact-checking
    """

    __tablename__ = "research_templates"

    id = Column(String, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, default="")
    category = Column(String(50), default="general")

    # Template configuration
    default_persona = Column(String(50), default="default")
    default_depth = Column(String(20), default="comprehensive")
    suggested_tags = Column(JSON, default=list)
    workflow_steps = Column(JSON, default=list)  # Pre-defined research steps

    # Template metadata
    is_public = Column(Boolean, default=False)
    usage_count = Column(Integer, default=0)
    created_by = Column(String, ForeignKey("users.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    creator = relationship("User")

    def __repr__(self):
        return f"<ResearchTemplate(id='{self.id}', name='{self.name}', category='{self.category}')>"


class ResearchAnalytics(Base):
    """
    Model for storing research usage analytics.

    Tracks:
    - Popular queries and topics
    - Performance metrics
    - User engagement patterns
    - System usage statistics
    """

    __tablename__ = "research_analytics"

    id = Column(String, primary_key=True, index=True)

    # Analytics data
    event_type = Column(String(50), nullable=False, index=True)  # query, bookmark, export, etc.
    user_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    session_id = Column(String, nullable=True)

    # Event data
    event_data = Column(JSON, default=dict)  # Flexible event data storage

    # Metrics
    processing_time = Column(Float, nullable=True)
    confidence_score = Column(Float, nullable=True)
    sources_count = Column(Integer, nullable=True)

    # Context
    user_agent = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)  # Support IPv4 and IPv6

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    def __repr__(self):
        return f"<ResearchAnalytics(id='{self.id}', event_type='{self.event_type}', user_id='{self.user_id}')>"


# Add relationships to User model (if not already present)
# This would typically be in the user.py model file, but shown here for completeness

# User.research_sessions = relationship("ResearchSession", back_populates="user")
# User.research_bookmarks = relationship("ResearchBookmark", back_populates="user")
