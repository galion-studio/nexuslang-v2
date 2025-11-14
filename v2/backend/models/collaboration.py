"""
Collaboration models for Deep Search.
Handles collaborative research sessions and multi-user interactions.
"""

from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from .base import Base


class CollaborativeSession(Base):
    """
    Model for collaborative research sessions.

    Enables multiple users to work together on research projects
    with real-time collaboration features.
    """

    __tablename__ = "collaborative_sessions"

    id = Column(String, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, default="")
    owner_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)

    # Session status and configuration
    status = Column(String(20), default="active", index=True)  # active, paused, completed, archived
    settings = Column(JSON, default=dict)  # Session-specific settings
    tags = Column(JSON, default=list)  # Session tags for organization

    # Participant management
    max_participants = Column(Integer, default=10)
    is_public = Column(Boolean, default=False)

    # Activity tracking
    participant_count = Column(Integer, default=1)
    message_count = Column(Integer, default=0)
    artifact_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_activity = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    owner = relationship("User", back_populates="owned_collaborative_sessions")
    participants = relationship("SessionParticipant", back_populates="session")
    messages = relationship("SessionMessage", back_populates="session")
    artifacts = relationship("SessionArtifact", back_populates="session")

    def __repr__(self):
        return f"<CollaborativeSession(id='{self.id}', title='{self.title}', owner_id='{self.owner_id}', status='{self.status}')>"


class SessionParticipant(Base):
    """
    Model for tracking session participants and their roles.

    Manages user permissions and activity within collaborative sessions.
    """

    __tablename__ = "session_participants"

    id = Column(String, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("collaborative_sessions.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)

    # Role and permissions
    role = Column(String(20), default="editor")  # owner, editor, viewer, guest
    permissions = Column(JSON, default=dict)  # Detailed permission settings

    # Activity tracking
    joined_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    last_activity = Column(DateTime(timezone=True), server_default=func.now())
    left_at = Column(DateTime(timezone=True), nullable=True)

    # Engagement metrics
    messages_sent = Column(Integer, default=0)
    artifacts_created = Column(Integer, default=0)
    contributions_made = Column(Integer, default=0)

    # Relationships
    session = relationship("CollaborativeSession", back_populates="participants")
    user = relationship("User", back_populates="session_participations")

    def __repr__(self):
        return f"<SessionParticipant(session_id='{self.session_id}', user_id='{self.user_id}', role='{self.role}')>"


class SessionMessage(Base):
    """
    Model for messages within collaborative sessions.

    Supports text chat, system notifications, and structured messages
    for session communication.
    """

    __tablename__ = "session_messages"

    id = Column(String, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("collaborative_sessions.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)  # Null for system messages

    # Message content
    message_type = Column(String(20), default="text")  # text, system, notification, action
    content = Column(Text, nullable=False)
    metadata = Column(JSON, default=dict)  # Additional message metadata

    # Message threading (for replies)
    parent_message_id = Column(String, ForeignKey("session_messages.id"), nullable=True)
    thread_id = Column(String, nullable=True, index=True)

    # Reactions and engagement
    reactions = Column(JSON, default=dict)  # User reactions (thumbs_up, etc.)
    edited_at = Column(DateTime(timezone=True), nullable=True)
    edited_by = Column(String, ForeignKey("users.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    session = relationship("CollaborativeSession", back_populates="messages")
    author = relationship("User", foreign_keys=[user_id])
    editor = relationship("User", foreign_keys=[edited_by])
    parent_message = relationship("SessionMessage", remote_side=[id])
    thread_messages = relationship("SessionMessage", backref="thread_parent")

    def __repr__(self):
        return f"<SessionMessage(id='{self.id}', session_id='{self.session_id}', type='{self.message_type}')>"


class SessionArtifact(Base):
    """
    Model for artifacts created within collaborative sessions.

    Stores research notes, findings, documents, and other collaborative
    work products.
    """

    __tablename__ = "session_artifacts"

    id = Column(String, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("collaborative_sessions.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)

    # Artifact metadata
    artifact_type = Column(String(50), nullable=False)  # note, research, document, image, etc.
    title = Column(String(200), nullable=False)
    description = Column(Text, default="")

    # Content storage
    content = Column(JSON, default=dict)  # Flexible content storage
    metadata = Column(JSON, default=dict)  # Additional metadata

    # Version control
    version = Column(Integer, default=1)
    parent_artifact_id = Column(String, ForeignKey("session_artifacts.id"), nullable=True)

    # Collaboration features
    is_shared = Column(Boolean, default=True)
    tags = Column(JSON, default=list)
    permissions = Column(JSON, default=dict)  # Override session permissions

    # Engagement tracking
    view_count = Column(Integer, default=0)
    edit_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    session = relationship("CollaborativeSession", back_populates="artifacts")
    author = relationship("User", back_populates="session_artifacts")
    parent_artifact = relationship("SessionArtifact", remote_side=[id])

    def __repr__(self):
        return f"<SessionArtifact(id='{self.id}', type='{self.artifact_type}', title='{self.title}')>"


class CollaborationInvite(Base):
    """
    Model for managing collaboration invitations.

    Handles invites to private collaborative sessions with
    expiration and usage tracking.
    """

    __tablename__ = "collaboration_invites"

    id = Column(String, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("collaborative_sessions.id"), nullable=False, index=True)
    inviter_id = Column(String, ForeignKey("users.id"), nullable=False)
    invitee_email = Column(String(255), nullable=True, index=True)  # For email invites
    invitee_user_id = Column(String, ForeignKey("users.id"), nullable=True)  # For direct user invites

    # Invite details
    invite_code = Column(String(100), nullable=False, unique=True, index=True)
    role_offered = Column(String(20), default="editor")
    custom_message = Column(Text, default="")

    # Status tracking
    status = Column(String(20), default="pending")  # pending, accepted, declined, expired
    expires_at = Column(DateTime(timezone=True), nullable=False)
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    responded_at = Column(DateTime(timezone=True), nullable=True)

    # Usage limits
    max_uses = Column(Integer, default=1)
    uses_remaining = Column(Integer, default=1)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    session = relationship("CollaborativeSession")
    inviter = relationship("User", foreign_keys=[inviter_id])
    invitee = relationship("User", foreign_keys=[invitee_user_id])

    def __repr__(self):
        return f"<CollaborationInvite(id='{self.id}', session_id='{self.session_id}', status='{self.status}')>"


class CollaborationActivity(Base):
    """
    Model for tracking collaboration activities and analytics.

    Records user interactions, session metrics, and collaboration patterns
    for analytics and insights.
    """

    __tablename__ = "collaboration_activities"

    id = Column(String, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("collaborative_sessions.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)

    # Activity details
    activity_type = Column(String(50), nullable=False, index=True)  # join, leave, message, artifact, etc.
    activity_data = Column(JSON, default=dict)  # Activity-specific data

    # Context
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)

    # Metrics
    processing_time = Column(Integer, nullable=True)  # Milliseconds
    data_size = Column(Integer, nullable=True)  # Bytes transferred

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    session = relationship("CollaborativeSession")
    user = relationship("User")

    def __repr__(self):
        return f"<CollaborationActivity(session_id='{self.session_id}', type='{self.activity_type}')>"


class CollaborationPermission(Base):
    """
    Model for defining granular collaboration permissions.

    Provides fine-grained access control for collaborative features.
    """

    __tablename__ = "collaboration_permissions"

    id = Column(String, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, default="")
    category = Column(String(50), nullable=False)  # session, chat, artifacts, research, admin

    # Permission settings
    default_for_role = Column(JSON, default=dict)  # Default permissions by role
    is_system_permission = Column(Boolean, default=True)

    # Usage tracking
    usage_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<CollaborationPermission(name='{self.name}', category='{self.category}')>"


# Add relationships to User model (if not already present)
# This would typically be in the user.py model file, but shown here for completeness

# User.owned_collaborative_sessions = relationship("CollaborativeSession", back_populates="owner")
# User.session_participations = relationship("SessionParticipant", back_populates="user")
# User.session_messages = relationship("SessionMessage", foreign_keys="SessionMessage.user_id")
# User.session_artifacts = relationship("SessionArtifact", back_populates="author")
# User.collaboration_invites_sent = relationship("CollaborationInvite", foreign_keys="CollaborationInvite.inviter_id")
# User.collaboration_invites_received = relationship("CollaborationInvite", foreign_keys="CollaborationInvite.invitee_user_id")
# User.collaboration_activities = relationship("CollaborationActivity", back_populates="user")
