"""
Workplace Service Models
Cross-platform workspace, team, and project management models.

Models:
- Workspace: Central hub for teams and projects
- WorkspaceMember: Team members with roles and permissions
- SyncEvent: Cross-platform synchronization events
- TimeLog: Time tracking with AI categorization
- Task: Project tasks with AI assignment
- LiveSession: Real-time collaboration sessions
- CodeReview: AI-assisted code review records
- Payment: Advanced billing and compensation
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float, ForeignKey, JSON, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import and_
import uuid
from datetime import datetime

from ..core.database import Base


class Workspace(Base):
    """Workspace model - central hub for cross-platform teams"""

    __tablename__ = "workspaces"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Workspace settings
    billing_cycle = Column(String(50), default="monthly")  # monthly, quarterly, annual
    tax_rate = Column(Float, default=0.0)
    currency = Column(String(10), default="USD")
    workflow_type = Column(String(50), default="kanban")  # kanban, scrum, waterfall

    # Platform permissions
    platform_permissions = Column(JSONB, default=dict)  # Platform-specific access controls

    # Status
    is_active = Column(Boolean, default=True)
    member_count = Column(Integer, default=1)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    owner = relationship("User", foreign_keys=[owner_id])
    members = relationship("WorkspaceMember", back_populates="workspace", cascade="all, delete-orphan")
    sync_events = relationship("SyncEvent", back_populates="workspace", cascade="all, delete-orphan")


class WorkspaceMember(Base):
    """Workspace member with roles and platform-specific permissions"""

    __tablename__ = "workspace_members"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Role and permissions
    role = Column(String(50), default="member")  # owner, admin, member, viewer
    can_create_projects = Column(Boolean, default=False)
    can_review_applications = Column(Boolean, default=False)
    can_post_jobs = Column(Boolean, default=False)
    platform_permissions = Column(JSONB, default=dict)  # Platform-specific permissions

    # Member details
    skills = Column(ARRAY(String), nullable=True)
    availability_status = Column(String(50), default="available")  # available, busy, away
    performance_score = Column(Float, default=5.0)  # 1-10 scale
    workload_capacity = Column(Integer, default=40)  # Hours per week

    # Timestamps
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_active = Column(DateTime, default=datetime.utcnow)

    # Relationships
    workspace = relationship("Workspace", back_populates="members")
    user = relationship("User")

    __table_args__ = (
        {'schema': None},
    )


class SyncEvent(Base):
    """Cross-platform synchronization events"""

    __tablename__ = "sync_events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Event details
    event_type = Column(String(100), nullable=False)  # task_created, time_logged, project_updated, etc.
    payload = Column(JSONB, nullable=False)
    source_platform = Column(String(50), nullable=False)  # galion.app, galion.studio, developer.galion.app
    target_platforms = Column(ARRAY(String), nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    workspace = relationship("Workspace", back_populates="sync_events")


class Task(Base):
    """Project tasks with AI-powered assignment and tracking"""

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)

    # Status and priority
    status = Column(String(50), default="backlog")  # backlog, in_progress, review, done, cancelled
    priority = Column(String(20), default="medium")  # low, medium, high, urgent
    complexity = Column(String(20), default="medium")  # simple, medium, complex

    # Assignment
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_at = Column(DateTime, nullable=True)
    assignment_method = Column(String(50), default="manual")  # manual, ai_recommended

    # Time tracking
    hours_estimate = Column(Float, nullable=True)
    hours_logged = Column(Float, default=0.0)

    # Requirements
    required_skills = Column(ARRAY(String), nullable=True)
    blockers = Column(ARRAY(String), nullable=True)

    # AI analysis
    ai_analysis = Column(JSONB, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    project = relationship("Project")
    assignee = relationship("User")
    time_logs = relationship("TimeLog", back_populates="task", cascade="all, delete-orphan")


class TimeLog(Base):
    """Time tracking entries with AI categorization"""

    __tablename__ = "time_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Time details
    hours = Column(Float, nullable=False)
    work_date = Column(DateTime, nullable=False)
    description = Column(Text, nullable=False)

    # Categorization
    category = Column(String(100), default="development")  # development, design, research, etc.
    billable = Column(Boolean, default=True)
    auto_categorized = Column(Boolean, default=False)
    ai_analysis = Column(JSONB, nullable=True)

    # Financial
    hourly_rate = Column(Float, nullable=True)
    total_amount = Column(Float, default=0.0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    task = relationship("Task", back_populates="time_logs")


class LiveSession(Base):
    """Live collaboration sessions for real-time editing"""

    __tablename__ = "live_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Session details
    session_type = Column(String(50), nullable=False)  # kanban, timeline, whiteboard
    max_participants = Column(Integer, default=10)
    participants = Column(ARRAY(Integer), default=list)  # Array of user IDs
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ended_at = Column(DateTime, nullable=True)


class CodeReview(Base):
    """AI-assisted code review records"""

    __tablename__ = "code_reviews"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    requested_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Code details
    code_content = Column(Text, nullable=False)
    language = Column(String(50), nullable=False)
    review_type = Column(String(50), default="general")  # security, performance, best_practices, general
    severity_level = Column(String(20), default="medium")  # low, medium, high, critical

    # AI analysis
    ai_analysis = Column(JSONB, nullable=True)
    ai_feedback = Column(JSONB, nullable=True)

    # Status
    status = Column(String(50), default="pending")  # pending, in_progress, completed

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Payment(Base):
    """Advanced billing and compensation records"""

    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    workspace_id = Column(Integer, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)

    # Payment details
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="USD")
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    description = Column(Text, nullable=False)

    # Status
    status = Column(String(50), default="pending")  # pending, paid, failed, cancelled
    auto_generated = Column(Boolean, default=False)
    billing_data = Column(JSONB, nullable=True)

    # Payment processing
    stripe_payment_intent_id = Column(String(255), nullable=True)
    processed_at = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User")
    workspace = relationship("Workspace")


# Helper functions for the workplace service
def _user_has_workspace_access(db, user_id: int, workspace_id: int) -> bool:
    """Check if user has access to workspace"""
    from sqlalchemy.orm import Session
    session = db if isinstance(db, Session) else db()

    # Check if user is owner
    workspace = session.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        return False

    if workspace.owner_id == user_id:
        return True

    # Check if user is a member
    member = session.query(WorkspaceMember).filter(
        and_(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user_id
        )
    ).first()

    return member is not None
