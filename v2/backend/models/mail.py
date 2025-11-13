"""
Mail Integration Models for Galion Ecosystem
Supports multiple email providers with OAuth and IMAP/SMTP
"""

from sqlalchemy import Column, String, Boolean, DateTime, Text, JSON, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from ..core.database import Base


class MailProvider(Base):
    """Supported email providers configuration"""

    __tablename__ = "mail_providers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False)  # gmail, outlook, yahoo, etc.
    display_name = Column(String(100), nullable=False)
    client_id = Column(String(255))  # OAuth client ID
    client_secret = Column(String(255))  # OAuth client secret
    auth_url = Column(String(500))  # OAuth authorization URL
    token_url = Column(String(500))  # OAuth token exchange URL
    scope = Column(String(500))  # Required OAuth scopes
    imap_host = Column(String(100))  # IMAP server
    imap_port = Column(String(10))  # IMAP port
    smtp_host = Column(String(100))  # SMTP server
    smtp_port = Column(String(10))  # SMTP port
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    connections = relationship("MailConnection", back_populates="provider")


class MailConnection(Base):
    """User email account connections"""

    __tablename__ = "mail_connections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    provider_id = Column(UUID(as_uuid=True), ForeignKey('mail_providers.id', ondelete='CASCADE'), nullable=False)

    # Account details
    email = Column(String(254), nullable=False)
    display_name = Column(String(100))
    is_primary = Column(Boolean, default=False)

    # OAuth tokens
    access_token = Column(Text)
    refresh_token = Column(Text)
    token_expires_at = Column(DateTime)

    # IMAP/SMTP credentials (for non-OAuth providers)
    imap_username = Column(String(254))
    imap_password = Column(Text)  # Encrypted
    smtp_username = Column(String(254))
    smtp_password = Column(Text)  # Encrypted

    # Connection settings
    sync_enabled = Column(Boolean, default=True)
    sync_frequency = Column(String(20), default='15m')  # 15m, 30m, 1h, 6h, 24h
    last_sync_at = Column(DateTime)
    sync_status = Column(String(20), default='idle')  # idle, syncing, error, disabled

    # AI integration settings
    ai_assistant_enabled = Column(Boolean, default=True)
    voice_responses_enabled = Column(Boolean, default=False)
    auto_summarize = Column(Boolean, default=True)
    smart_replies = Column(Boolean, default=True)
    priority_detection = Column(Boolean, default=True)

    # Metadata
    connection_metadata = Column(JSONB, default=dict)  # Provider-specific data
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="mail_connections")
    provider = relationship("MailProvider", back_populates="connections")
    messages = relationship("MailMessage", back_populates="connection", cascade="all, delete-orphan")

    __table_args__ = (
        Index('ix_mail_connections_user_id', 'user_id'),
        Index('ix_mail_connections_email', 'email'),
        Index('ix_mail_connections_provider_id', 'provider_id'),
    )


class MailFolder(Base):
    """Email folders/labels for each connection"""

    __tablename__ = "mail_folders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    connection_id = Column(UUID(as_uuid=True), ForeignKey('mail_connections.id', ondelete='CASCADE'), nullable=False)

    # Folder details
    folder_id = Column(String(255), nullable=False)  # Provider-specific ID
    name = Column(String(255), nullable=False)
    display_name = Column(String(255))
    folder_type = Column(String(50))  # inbox, sent, drafts, trash, spam, etc.
    is_system = Column(Boolean, default=False)

    # Sync status
    last_sync_at = Column(DateTime)
    total_messages = Column(String(20))  # May be large number
    unread_count = Column(String(20))

    # AI categorization
    ai_category = Column(String(50))  # work, personal, marketing, etc.
    ai_priority = Column(String(20))  # high, medium, low

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    connection = relationship("MailConnection", back_populates="folders")
    messages = relationship("MailMessage", back_populates="folder", cascade="all, delete-orphan")

    __table_args__ = (
        Index('ix_mail_folders_connection_id', 'connection_id'),
        Index('ix_mail_folders_folder_type', 'folder_type'),
    )


class MailMessage(Base):
    """Email messages with AI analysis"""

    __tablename__ = "mail_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    connection_id = Column(UUID(as_uuid=True), ForeignKey('mail_connections.id', ondelete='CASCADE'), nullable=False)
    folder_id = Column(UUID(as_uuid=True), ForeignKey('mail_folders.id', ondelete='CASCADE'), nullable=False)

    # Message identifiers
    message_id = Column(String(500))  # RFC 822 Message-ID
    thread_id = Column(String(500))  # Conversation thread ID
    provider_message_id = Column(String(500))  # Provider-specific ID

    # Message content
    subject = Column(Text)
    sender_name = Column(String(255))
    sender_email = Column(String(254))
    recipients = Column(JSONB)  # List of {name, email} objects
    cc_recipients = Column(JSONB)  # CC recipients
    bcc_recipients = Column(JSONB)  # BCC recipients

    # Content
    body_text = Column(Text)  # Plain text version
    body_html = Column(Text)  # HTML version
    attachments = Column(JSONB)  # List of attachment metadata

    # Message metadata
    sent_at = Column(DateTime)
    received_at = Column(DateTime)
    is_read = Column(Boolean, default=False)
    is_starred = Column(Boolean, default=False)
    is_draft = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    size_bytes = Column(String(20))  # Message size

    # AI analysis
    ai_summary = Column(Text)  # AI-generated summary
    ai_category = Column(String(50))  # work, personal, marketing, spam, etc.
    ai_sentiment = Column(String(20))  # positive, negative, neutral
    ai_priority = Column(String(20))  # urgent, high, medium, low
    ai_action_items = Column(JSONB)  # Extracted action items
    ai_keywords = Column(JSONB)  # Important keywords/phrases

    # Voice integration
    voice_transcript = Column(Text)  # If voice message
    voice_response_url = Column(String(500))  # Generated voice response

    # User interactions
    user_labels = Column(JSONB, default=list)  # Custom user labels
    user_notes = Column(Text)  # User notes on the message

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    connection = relationship("MailConnection", back_populates="messages")
    folder = relationship("MailFolder", back_populates="messages")

    __table_args__ = (
        Index('ix_mail_messages_connection_id', 'connection_id'),
        Index('ix_mail_messages_folder_id', 'folder_id'),
        Index('ix_mail_messages_thread_id', 'thread_id'),
        Index('ix_mail_messages_sent_at', 'sent_at'),
        Index('ix_mail_messages_ai_category', 'ai_category'),
        Index('ix_mail_messages_ai_priority', 'ai_priority'),
    )


class MailAIInteraction(Base):
    """AI interactions with email (summaries, responses, etc.)"""

    __tablename__ = "mail_ai_interactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    message_id = Column(UUID(as_uuid=True), ForeignKey('mail_messages.id', ondelete='CASCADE'), nullable=False)

    # Interaction details
    interaction_type = Column(String(50))  # summary, reply, forward, categorize
    ai_model_used = Column(String(100))  # Which AI model was used
    prompt_used = Column(Text)  # The prompt sent to AI
    ai_response = Column(Text)  # AI-generated content

    # Voice integration
    voice_request = Column(Boolean, default=False)
    voice_response_generated = Column(Boolean, default=False)
    voice_response_url = Column(String(500))

    # User feedback
    user_rating = Column(String(10))  # excellent, good, poor, etc.
    user_feedback = Column(Text)

    # Performance metrics
    processing_time_ms = Column(String(10))
    tokens_used = Column(String(10))

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User")
    message = relationship("MailMessage")

    __table_args__ = (
        Index('ix_mail_ai_interactions_user_id', 'user_id'),
        Index('ix_mail_ai_interactions_message_id', 'message_id'),
        Index('ix_mail_ai_interactions_type', 'interaction_type'),
    )
