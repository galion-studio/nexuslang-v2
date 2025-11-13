"""
Workplace Service Schemas
Pydantic models for workplace API requests and responses.

Organized by API sections:
- Synchronization APIs
- User Management APIs
- Project Management APIs
- Time Tracking APIs
- Task Management APIs
- Billing APIs
- Analytics APIs
- AI Integration APIs
- Real-time Collaboration APIs
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date
from enum import Enum


# Enums
class Platform(str, Enum):
    GALION_APP = "galion.app"
    GALION_STUDIO = "galion.studio"
    DEVELOPER_GALION_APP = "developer.galion.app"


class EventType(str, Enum):
    TASK_CREATED = "task_created"
    TASK_UPDATED = "task_updated"
    TIME_LOGGED = "time_logged"
    PROJECT_UPDATED = "project_updated"
    USER_JOINED = "user_joined"
    USER_LEFT = "user_left"


class TaskStatus(str, Enum):
    BACKLOG = "backlog"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskComplexity(str, Enum):
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"


class MemberRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class PredictionType(str, Enum):
    PROJECT_COMPLETION = "project_completion"
    TEAM_PERFORMANCE = "team_performance"
    RESOURCE_NEEDS = "resource_needs"


class InsightType(str, Enum):
    GENERAL = "general"
    RISK = "risk"
    RESOURCE = "resource"
    TIMELINE = "timeline"


class ReviewType(str, Enum):
    SECURITY = "security"
    PERFORMANCE = "performance"
    BEST_PRACTICES = "best_practices"
    GENERAL = "general"


class SeverityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SessionType(str, Enum):
    KANBAN = "kanban"
    TIMELINE = "timeline"
    WHITEBOARD = "whiteboard"


# Base Models
class WorkspaceBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    billing_cycle: str = "monthly"
    tax_rate: float = 0.0
    currency: str = "USD"
    workflow_type: str = "kanban"
    platform_permissions: Dict[str, Any] = Field(default_factory=dict)


class WorkspaceMemberBase(BaseModel):
    user_id: int
    role: MemberRole = MemberRole.MEMBER
    can_create_projects: bool = False
    can_review_applications: bool = False
    can_post_jobs: bool = False
    platform_permissions: Dict[str, Any] = Field(default_factory=dict)
    skills: Optional[List[str]] = None
    availability_status: str = "available"
    performance_score: float = 5.0
    workload_capacity: int = 40


# Synchronization APIs
class PlatformUpdate(BaseModel):
    workspace_id: int
    event_type: str
    payload: Dict[str, Any]
    source_platform: Platform
    target_platforms: List[Platform]
    notify_users: bool = False


class SyncEventResponse(BaseModel):
    id: int
    event_type: str
    source_platform: Platform
    target_platforms: List[Platform]
    payload: Dict[str, Any]
    user_id: int
    timestamp: datetime


class SyncHistoryResponse(BaseModel):
    workspace_id: int
    events: List[SyncEventResponse]
    total: int


# User Management APIs
class WorkspaceInvitation(BaseModel):
    role: MemberRole = MemberRole.MEMBER
    can_create_projects: bool = False
    can_review_applications: bool = False
    can_post_jobs: bool = False
    platform_permissions: Dict[str, Any] = Field(default_factory=dict)
    invitation_message: str = ""


class InviteUserResponse(BaseModel):
    message: str
    workspace: str
    role: MemberRole
    platform_permissions: Dict[str, Any]


# Project Management APIs
class ProjectInsightResponse(BaseModel):
    project_id: int
    insight_type: InsightType
    insights: Dict[str, Any]
    generated_at: datetime
    confidence_score: float


# Time Tracking APIs
class SmartTimeLogRequest(BaseModel):
    task_id: Optional[int] = None
    project_id: Optional[int] = None
    hours: float = Field(..., gt=0)
    work_date: Optional[date] = None
    description: str = Field(..., min_length=1)


class SmartTimeLogResponse(BaseModel):
    time_log_id: int
    task_id: Optional[int]
    project_id: Optional[int]
    hours: float
    category: str
    billable: bool
    amount: float
    auto_categorized: bool
    ai_insights: Dict[str, Any]


# Task Management APIs
class SmartAssignmentRequest(BaseModel):
    task_id: int
    criteria: Optional[Dict[str, Any]] = None


class SmartAssignmentResponse(BaseModel):
    task_id: int
    analysis: Dict[str, Any]
    assignment_made: bool
    assignee: Optional[Dict[str, Any]]
    alternatives: List[Dict[str, Any]]
    reasoning: str


# Billing APIs
class AutoBillingRequest(BaseModel):
    workspace_id: int
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class BillingInvoice(BaseModel):
    id: int
    user_id: int
    amount: float
    description: str


class AutoBillingResponse(BaseModel):
    workspace_id: int
    billing_period: Dict[str, datetime]
    invoices_generated: int
    total_amount: float
    optimization_insights: Dict[str, Any]
    invoices: List[BillingInvoice]


# Analytics APIs
class PredictiveAnalyticsResponse(BaseModel):
    workspace_id: int
    prediction_type: PredictionType
    timeframe_days: int
    generated_at: datetime
    predictions: Dict[str, Any]
    confidence_levels: Dict[str, Any]
    recommendations: List[str]
    risk_factors: List[str]


# AI Integration APIs
class WorkflowOptimizationRequest(BaseModel):
    workspace_id: int
    focus_areas: Optional[List[str]] = ["bottlenecks", "resource_allocation", "timeline"]
    constraints: Optional[Dict[str, Any]] = None
    apply_changes: bool = False


class WorkflowOptimizationResponse(BaseModel):
    workspace_id: int
    optimization_focus: List[str]
    recommendations: List[Dict[str, Any]]
    expected_improvements: Dict[str, Any]
    implementation_plan: Dict[str, Any]
    applied_changes: List[Dict[str, Any]]
    generated_at: datetime


# Real-time Collaboration APIs
class VoiceContextRequest(BaseModel):
    context_type: str = "general"
    include_history: bool = True


class VoiceContextResponse(BaseModel):
    user_context: Dict[str, Any]
    ai_preferences: Dict[str, Any]
    workspace_settings: Dict[str, Any]
    generated_at: datetime


class LiveSessionRequest(BaseModel):
    project_id: int
    session_type: SessionType
    max_participants: int = 10


class LiveSessionResponse(BaseModel):
    session_id: str
    project_id: int
    session_type: SessionType
    max_participants: int
    participants: List[int]
    websocket_url: str
    started_at: datetime


class CodeReviewRequest(BaseModel):
    project_id: int
    code_content: str
    language: str
    context: str = ""
    review_type: ReviewType = ReviewType.GENERAL
    severity_level: SeverityLevel = SeverityLevel.MEDIUM


class CodeReviewResponse(BaseModel):
    review_id: int
    analysis: Dict[str, Any]
    feedback: Dict[str, Any]
    recommendations: List[str]
    severity_breakdown: Dict[str, Any]
    estimated_effort: str
    generated_at: datetime


# Workspace Response Models
class WorkspaceResponse(WorkspaceBase):
    id: int
    owner_id: int
    is_active: bool
    member_count: int
    created_at: datetime
    updated_at: datetime


class WorkspaceMemberResponse(WorkspaceMemberBase):
    id: int
    workspace_id: int
    joined_at: datetime
    last_active: datetime


class TaskResponse(BaseModel):
    id: int
    project_id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    complexity: TaskComplexity
    assignee_id: Optional[int]
    assigned_at: Optional[datetime]
    assignment_method: str
    hours_estimate: Optional[float]
    hours_logged: float
    required_skills: Optional[List[str]]
    blockers: Optional[List[str]]
    ai_analysis: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime


# Validators
class SmartTimeLogRequestValidator(SmartTimeLogRequest):
    @validator('hours')
    def validate_hours(cls, v):
        if v <= 0 or v > 24:
            raise ValueError('Hours must be between 0 and 24')
        return v

    @validator('description')
    def validate_description(cls, v):
        if len(v.strip()) < 5:
            raise ValueError('Description must be at least 5 characters long')
        return v.strip()


# Update the main models to use validators
SmartTimeLogRequest = SmartTimeLogRequestValidator
