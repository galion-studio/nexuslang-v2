"""
Content Manager Database Models
Multi-brand social media management system
"""

from sqlalchemy import Column, String, Text, Integer, Boolean, TIMESTAMP, ForeignKey, Numeric, BIGINT
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from core.database import Base


class Brand(Base):
    """
    Brand entity (Galion Studio, Galion App, Slavic Nomad, Marilyn Element)
    """
    __tablename__ = "brands"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    logo_url = Column(String(500))
    brand_color = Column(String(7), default='#000000')
    voice_guidelines = Column(Text)
    website_url = Column(String(500))
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    social_accounts = relationship("SocialAccount", back_populates="brand", cascade="all, delete-orphan")
    content_posts = relationship("ContentPost", back_populates="brand", cascade="all, delete-orphan")
    content_templates = relationship("ContentTemplate", back_populates="brand", cascade="all, delete-orphan")
    team_permissions = relationship("TeamPermission", back_populates="brand", cascade="all, delete-orphan")


class SocialAccount(Base):
    """
    Connected social media accounts per brand
    """
    __tablename__ = "social_accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    brand_id = Column(UUID(as_uuid=True), ForeignKey('brands.id', ondelete='CASCADE'), nullable=False)
    platform = Column(String(50), nullable=False)  # reddit, twitter, instagram, etc.
    account_name = Column(String(200), nullable=False)
    account_url = Column(String(500))
    account_id = Column(String(200))
    credentials = Column(JSONB)  # Encrypted OAuth tokens
    platform_metadata = Column(JSONB)  # Platform-specific settings
    is_active = Column(Boolean, default=True)
    last_synced = Column(TIMESTAMP)
    sync_status = Column(String(50), default='pending')
    error_message = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    brand = relationship("Brand", back_populates="social_accounts")
    platform_posts = relationship("PlatformPost", back_populates="social_account", cascade="all, delete-orphan")


class ContentPost(Base):
    """
    Content posts with multi-platform support
    """
    __tablename__ = "content_posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    brand_id = Column(UUID(as_uuid=True), ForeignKey('brands.id', ondelete='CASCADE'), nullable=False)
    title = Column(String(500))
    content = Column(Text, nullable=False)
    content_html = Column(Text)
    excerpt = Column(Text)
    media_urls = Column(JSONB, default=[])
    platforms = Column(JSONB, default=[])
    hashtags = Column(JSONB, default=[])
    mentions = Column(JSONB, default=[])
    metadata = Column(JSONB, default={})
    status = Column(String(50), default='draft')
    scheduled_at = Column(TIMESTAMP)
    published_at = Column(TIMESTAMP)
    failed_at = Column(TIMESTAMP)
    failure_reason = Column(Text)
    recurring_schedule = Column(JSONB)
    template_id = Column(UUID(as_uuid=True))
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'))
    updated_by = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'))
    approved_by = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'))
    approved_at = Column(TIMESTAMP)
    version = Column(Integer, default=1)
    parent_post_id = Column(UUID(as_uuid=True), ForeignKey('content_posts.id'))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    brand = relationship("Brand", back_populates="content_posts")
    platform_posts = relationship("PlatformPost", back_populates="content_post", cascade="all, delete-orphan")
    comments = relationship("PostComment", back_populates="content_post", cascade="all, delete-orphan")


class PlatformPost(Base):
    """
    Individual platform-specific posts
    """
    __tablename__ = "platform_posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_post_id = Column(UUID(as_uuid=True), ForeignKey('content_posts.id', ondelete='CASCADE'), nullable=False)
    social_account_id = Column(UUID(as_uuid=True), ForeignKey('social_accounts.id', ondelete='CASCADE'), nullable=False)
    platform = Column(String(50), nullable=False)
    platform_post_id = Column(String(200))
    platform_url = Column(String(500))
    platform_content = Column(Text)
    platform_metadata = Column(JSONB, default={})
    status = Column(String(50), default='pending')
    posted_at = Column(TIMESTAMP)
    failed_at = Column(TIMESTAMP)
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    last_retry_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    content_post = relationship("ContentPost", back_populates="platform_posts")
    social_account = relationship("SocialAccount", back_populates="platform_posts")
    analytics = relationship("PostAnalytics", back_populates="platform_post", cascade="all, delete-orphan")


class PostAnalytics(Base):
    """
    Engagement metrics for platform posts
    """
    __tablename__ = "post_analytics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform_post_id = Column(UUID(as_uuid=True), ForeignKey('platform_posts.id', ondelete='CASCADE'), nullable=False)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    views = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    saves = Column(Integer, default=0)
    reach = Column(Integer, default=0)
    impressions = Column(Integer, default=0)
    engagement_rate = Column(Numeric(5, 2), default=0.00)
    platform_specific_metrics = Column(JSONB, default={})
    synced_at = Column(TIMESTAMP, server_default=func.now())
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    platform_post = relationship("PlatformPost", back_populates="analytics")


class ContentTemplate(Base):
    """
    Reusable content templates per brand
    """
    __tablename__ = "content_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    brand_id = Column(UUID(as_uuid=True), ForeignKey('brands.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    template_content = Column(Text, nullable=False)
    template_variables = Column(JSONB, default=[])
    platforms = Column(JSONB, default=[])
    tags = Column(JSONB, default=[])
    category = Column(String(100))
    use_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    brand = relationship("Brand", back_populates="content_templates")


class TeamPermission(Base):
    """
    Role-based access control for content management
    """
    __tablename__ = "team_permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    brand_id = Column(UUID(as_uuid=True), ForeignKey('brands.id', ondelete='CASCADE'))
    role = Column(String(50), nullable=False)
    permissions = Column(JSONB, default={})
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    brand = relationship("Brand", back_populates="team_permissions")


class PostComment(Base):
    """
    Team comments and feedback on draft posts
    """
    __tablename__ = "post_comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_post_id = Column(UUID(as_uuid=True), ForeignKey('content_posts.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    comment = Column(Text, nullable=False)
    parent_comment_id = Column(UUID(as_uuid=True), ForeignKey('post_comments.id', ondelete='CASCADE'))
    is_resolved = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    content_post = relationship("ContentPost", back_populates="comments")


class ContentActivityLog(Base):
    """
    Audit trail for all content management actions
    """
    __tablename__ = "content_activity_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'))
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    changes = Column(JSONB, default={})
    metadata = Column(JSONB, default={})
    ip_address = Column(String(45))
    user_agent = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())


class MediaAsset(Base):
    """
    Centralized media library
    """
    __tablename__ = "media_assets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    brand_id = Column(UUID(as_uuid=True), ForeignKey('brands.id', ondelete='CASCADE'))
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255))
    file_url = Column(String(500), nullable=False)
    thumbnail_url = Column(String(500))
    file_type = Column(String(50))
    mime_type = Column(String(100))
    file_size_bytes = Column(BIGINT)
    width = Column(Integer)
    height = Column(Integer)
    duration_seconds = Column(Integer)
    alt_text = Column(Text)
    description = Column(Text)
    tags = Column(JSONB, default=[])
    metadata = Column(JSONB, default={})
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'))
    use_count = Column(Integer, default=0)
    is_public = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


class N8nWebhook(Base):
    """
    N8n workflow integration tracking
    """
    __tablename__ = "n8n_webhooks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    webhook_url = Column(String(500), nullable=False)
    webhook_method = Column(String(10), default='POST')
    trigger_event = Column(String(100))
    is_active = Column(Boolean, default=True)
    last_triggered_at = Column(TIMESTAMP)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


class ScheduledJob(Base):
    """
    Track scheduled posting jobs
    """
    __tablename__ = "scheduled_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_type = Column(String(50), nullable=False)
    entity_type = Column(String(50))
    entity_id = Column(UUID(as_uuid=True))
    scheduled_for = Column(TIMESTAMP, nullable=False)
    status = Column(String(50), default='pending')
    priority = Column(Integer, default=5)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    payload = Column(JSONB, default={})
    result = Column(JSONB)
    error_message = Column(Text)
    started_at = Column(TIMESTAMP)
    completed_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

