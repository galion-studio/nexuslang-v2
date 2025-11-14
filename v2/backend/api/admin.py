"""
Admin API Endpoints
Comprehensive admin automation and management tools.

"Your imagination is the end."
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

from ..core.database import get_db
from ..services.admin.admin_service import get_admin_service, AdminService
from ..core.auth import get_current_user, get_current_admin_user
from ..models.user import User

router = APIRouter(prefix="/admin", tags=["Admin Management"])
security = HTTPBearer()


# Pydantic Models
class AutomationTaskStatus(str, Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"


class AutomationTaskResponse(BaseModel):
    id: str
    name: str
    description: str
    schedule: str
    enabled: bool
    last_run: Optional[str]
    next_run: Optional[str]
    success_count: int
    failure_count: int
    metadata: Dict[str, Any]


class AdminMetricsResponse(BaseModel):
    total_users: int
    active_users_24h: int
    active_users_7d: int
    total_credits_used: float
    average_session_time: float
    system_health_score: float
    active_agents: int
    pending_tasks: int
    completed_tasks_24h: int
    failed_tasks_24h: int
    api_response_time_avg: float
    error_rate_24h: float
    voice_sessions_24h: int
    storage_usage_gb: float
    bandwidth_usage_gb: float


class AdminDashboardResponse(BaseModel):
    metrics: AdminMetricsResponse
    user_stats: Dict[str, Any]
    system_health: Dict[str, Any]
    agent_stats: Dict[str, Any]
    voice_stats: Dict[str, Any]
    recent_activity: List[Dict[str, Any]]
    alerts: List[Dict[str, Any]]


class UserManagementAction(str, Enum):
    ACTIVATE = "activate"
    DEACTIVATE = "deactivate"
    RESET_PASSWORD = "reset_password"
    CHANGE_ROLE = "change_role"


class UserManagementRequest(BaseModel):
    user_id: str = Field(..., description="User ID to manage")
    action: UserManagementAction = Field(..., description="Action to perform")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional data for the action")


# Dependencies
async def get_admin_service_dep() -> AdminService:
    """Get the admin service instance"""
    return await get_admin_service()


# Routes
@router.get("/dashboard", response_model=AdminDashboardResponse)
async def get_admin_dashboard(
    admin_service: AdminService = Depends(get_admin_service_dep),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),  # Requires admin permissions
):
    """
    Get comprehensive admin dashboard data.

    Requires admin permissions.
    Returns system metrics, user statistics, health checks, and recent activity.
    """
    try:
        return await admin_service.get_admin_dashboard_data(db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve admin dashboard data: {str(e)}"
        )


@router.get("/metrics", response_model=AdminMetricsResponse)
async def get_admin_metrics(
    admin_service: AdminService = Depends(get_admin_service_dep),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Get key admin metrics for monitoring."""
    try:
        metrics = await admin_service._get_admin_metrics(db)
        return AdminMetricsResponse(**metrics.__dict__)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve admin metrics: {str(e)}"
        )


@router.post("/users/manage")
async def manage_user(
    request: UserManagementRequest,
    background_tasks: BackgroundTasks,
    admin_service: AdminService = Depends(get_admin_service_dep),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Perform user management actions.

    Requires admin permissions.
    Actions: activate, deactivate, reset_password, change_role
    """
    try:
        # This would implement the actual user management logic
        # For now, return success
        background_tasks.add_task(
            admin_service._perform_user_action,
            request.user_id,
            request.action,
            request.data or {},
            db
        )

        return {
            "message": f"User management action '{request.action}' initiated for user {request.user_id}",
            "action": request.action,
            "user_id": request.user_id,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"User management action failed: {str(e)}"
        )


@router.get("/automation/tasks", response_model=List[AutomationTaskResponse])
async def get_automation_tasks(
    admin_service: AdminService = Depends(get_admin_service_dep),
    current_user: User = Depends(get_current_admin_user),
):
    """Get all automation tasks and their status."""
    try:
        return await admin_service.get_automation_tasks()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve automation tasks: {str(e)}"
        )


@router.post("/automation/tasks/{task_id}/run")
async def run_automation_task(
    task_id: str,
    background_tasks: BackgroundTasks,
    admin_service: AdminService = Depends(get_admin_service_dep),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Manually execute an automation task.

    Requires admin permissions.
    """
    try:
        # Run the task in background
        background_tasks.add_task(admin_service.run_automation_task, task_id, db)

        return {
            "message": f"Automation task '{task_id}' execution initiated",
            "task_id": task_id,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute automation task: {str(e)}"
        )


@router.post("/automation/tasks/{task_id}/toggle")
async def toggle_automation_task(
    task_id: str,
    enabled: bool,
    admin_service: AdminService = Depends(get_admin_service_dep),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Enable or disable an automation task.

    Requires admin permissions.
    """
    try:
        if task_id not in admin_service.automation.tasks:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Automation task not found"
            )

        admin_service.automation.tasks[task_id].enabled = enabled

        return {
            "message": f"Automation task '{task_id}' {'enabled' if enabled else 'disabled'}",
            "task_id": task_id,
            "enabled": enabled,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to toggle automation task: {str(e)}"
        )


@router.get("/system/health")
async def get_system_health(
    admin_service: AdminService = Depends(get_admin_service_dep),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Get detailed system health information."""
    try:
        return await admin_service._get_system_health(db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve system health: {str(e)}"
        )


@router.get("/users/stats")
async def get_user_statistics(
    admin_service: AdminService = Depends(get_admin_service_dep),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Get detailed user statistics."""
    try:
        return await admin_service._get_user_statistics(db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user statistics: {str(e)}"
        )


@router.get("/agents/stats")
async def get_agent_statistics(
    admin_service: AdminService = Depends(get_admin_service_dep),
    current_user: User = Depends(get_current_admin_user),
):
    """Get detailed agent system statistics."""
    try:
        return await admin_service._get_agent_statistics()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve agent statistics: {str(e)}"
        )


@router.get("/voice/stats")
async def get_voice_statistics(
    admin_service: AdminService = Depends(get_admin_service_dep),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Get detailed voice interaction statistics."""
    try:
        return await admin_service._get_voice_statistics(db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve voice statistics: {str(e)}"
        )


@router.get("/activity/recent")
async def get_recent_activity(
    limit: int = 50,
    admin_service: AdminService = Depends(get_admin_service_dep),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Get recent system activity."""
    try:
        activity = await admin_service._get_recent_activity(db)
        return activity[:limit]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve recent activity: {str(e)}"
        )


@router.get("/alerts")
async def get_system_alerts(
    admin_service: AdminService = Depends(get_admin_service_dep),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Get active system alerts."""
    try:
        return await admin_service._get_system_alerts(db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve system alerts: {str(e)}"
        )


@router.post("/system/backup")
async def trigger_system_backup(
    background_tasks: BackgroundTasks,
    admin_service: AdminService = Depends(get_admin_service_dep),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Trigger a manual system backup.

    Requires admin permissions.
    """
    try:
        background_tasks.add_task(admin_service.automation._perform_data_backup, db)

        return {
            "message": "System backup initiated",
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate system backup: {str(e)}"
        )


@router.post("/system/maintenance/{action}")
async def perform_system_maintenance(
    action: str,
    background_tasks: BackgroundTasks,
    admin_service: AdminService = Depends(get_admin_service_dep),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Perform system maintenance actions.

    Available actions: cleanup, optimize, health_check
    Requires admin permissions.
    """
    valid_actions = ['cleanup', 'optimize', 'health_check']

    if action not in valid_actions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid maintenance action. Valid actions: {', '.join(valid_actions)}"
        )

    try:
        if action == 'cleanup':
            background_tasks.add_task(admin_service.automation._cleanup_inactive_users, db)
        elif action == 'optimize':
            background_tasks.add_task(admin_service.automation._generate_performance_report, db)
        elif action == 'health_check':
            background_tasks.add_task(admin_service.automation._system_health_check, db)

        return {
            "message": f"System maintenance action '{action}' initiated",
            "action": action,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform system maintenance: {str(e)}"
        )