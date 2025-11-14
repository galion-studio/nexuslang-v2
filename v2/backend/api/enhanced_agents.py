"""
Enhanced Agent Orchestration API
REST API for NexusLang v2 agent orchestration system.

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
from ..services.agents.enhanced_orchestrator import (
    get_enhanced_orchestrator,
    NexusTask,
    TaskPriority,
    TaskStatus,
    AgentRole
)
from ..core.auth import get_current_user
from ..models.user import User

router = APIRouter(prefix="/enhanced-agents", tags=["Enhanced Agent Orchestration"])
security = HTTPBearer()


# Pydantic Models
class TaskPriorityEnum(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class TaskStatusEnum(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NexusTaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=2000)
    priority: TaskPriorityEnum = TaskPriorityEnum.NORMAL
    dependencies: List[str] = Field(default_factory=list)
    deadline: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list)
    nexus_code: Optional[str] = Field(None, max_length=50000)
    cost_estimate: float = Field(default=0.0, ge=0)


class NexusTaskResponse(BaseModel):
    id: str
    title: str
    description: str
    priority: str
    status: str
    assigned_agent: Optional[str]
    dependencies: List[str]
    created_at: datetime
    updated_at: datetime
    deadline: Optional[datetime]
    tags: List[str]
    nexus_code: Optional[str]
    compiled_binary_size: Optional[int]
    execution_result: Optional[Dict[str, Any]]
    cost_estimate: float
    actual_cost: float
    metadata: Dict[str, Any]


class NexusCodeExecution(BaseModel):
    code: str = Field(..., min_length=1, max_length=50000)
    compile_binary: bool = Field(default=False)
    optimize: bool = Field(default=True)


class NexusCodeResponse(BaseModel):
    success: bool
    result: Optional[Dict[str, Any]]
    error: Optional[str]
    binary_compiled: bool
    execution_time: Optional[float]
    binary_size: Optional[int]


class SystemStatusResponse(BaseModel):
    metrics: Dict[str, Any]
    agents: Dict[str, Dict[str, Any]]
    active_tasks: int
    pending_tasks: int
    completed_tasks: int


# Dependencies
async def get_orchestrator():
    """Get the enhanced orchestrator instance"""
    return await get_enhanced_orchestrator()


# Routes
@router.post("/tasks", response_model=NexusTaskResponse, status_code=status.HTTP_201_CREATED)
async def create_nexus_task(
    task_data: NexusTaskCreate,
    background_tasks: BackgroundTasks,
    orchestrator = Depends(get_orchestrator),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new NexusLang task for agent execution.

    - Validates task data
    - Adds to processing queue
    - Returns task details
    """
    try:
        # Convert priority enum
        priority_map = {
            TaskPriorityEnum.LOW: TaskPriority.LOW,
            TaskPriorityEnum.NORMAL: TaskPriority.NORMAL,
            TaskPriorityEnum.HIGH: TaskPriority.HIGH,
            TaskPriorityEnum.CRITICAL: TaskPriority.CRITICAL,
        }
        priority = priority_map[task_data.priority]

        # Create the task
        task_id = await orchestrator.create_nexus_task(
            title=task_data.title,
            description=task_data.description,
            nexus_code=task_data.nexus_code,
            priority=priority,
            dependencies=task_data.dependencies,
            deadline=task_data.deadline,
            tags=set(task_data.tags),
        )

        # Get the created task
        task = orchestrator.tasks[task_id]

        # Auto-assign if possible
        background_tasks.add_task(orchestrator.assign_task_to_agent, task_id)

        return NexusTaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            priority=task.priority.name.lower(),
            status=task.status.value,
            assigned_agent=task.assigned_agent,
            dependencies=list(task.dependencies),
            created_at=task.created_at,
            updated_at=task.updated_at,
            deadline=task.deadline,
            tags=list(task.tags),
            nexus_code=task.nexus_code,
            compiled_binary_size=len(task.compiled_binary) if task.compiled_binary else None,
            execution_result=task.execution_result,
            cost_estimate=task.cost_estimate,
            actual_cost=task.actual_cost,
            metadata=task.metadata,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create task: {str(e)}"
        )


@router.get("/tasks", response_model=List[NexusTaskResponse])
async def list_nexus_tasks(
    status_filter: Optional[str] = None,
    priority_filter: Optional[str] = None,
    assigned_agent: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    orchestrator = Depends(get_orchestrator),
    current_user: User = Depends(get_current_user),
):
    """
    List NexusLang tasks with optional filtering.

    - Supports filtering by status, priority, and assigned agent
    - Pagination support
    """
    tasks = list(orchestrator.tasks.values())

    # Apply filters
    if status_filter:
        tasks = [t for t in tasks if t.status.value == status_filter]

    if priority_filter:
        tasks = [t for t in tasks if t.priority.name.lower() == priority_filter]

    if assigned_agent:
        tasks = [t for t in tasks if t.assigned_agent == assigned_agent]

    # Sort by creation date (newest first)
    tasks.sort(key=lambda t: t.created_at, reverse=True)

    # Apply pagination
    tasks = tasks[offset:offset + limit]

    return [
        NexusTaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            priority=task.priority.name.lower(),
            status=task.status.value,
            assigned_agent=task.assigned_agent,
            dependencies=list(task.dependencies),
            created_at=task.created_at,
            updated_at=task.updated_at,
            deadline=task.deadline,
            tags=list(task.tags),
            nexus_code=task.nexus_code,
            compiled_binary_size=len(task.compiled_binary) if task.compiled_binary else None,
            execution_result=task.execution_result,
            cost_estimate=task.cost_estimate,
            actual_cost=task.actual_cost,
            metadata=task.metadata,
        )
        for task in tasks
    ]


@router.get("/tasks/{task_id}", response_model=NexusTaskResponse)
async def get_nexus_task(
    task_id: str,
    orchestrator = Depends(get_orchestrator),
    current_user: User = Depends(get_current_user),
):
    """Get details of a specific NexusLang task."""
    if task_id not in orchestrator.tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    task = orchestrator.tasks[task_id]

    return NexusTaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        priority=task.priority.name.lower(),
        status=task.status.value,
        assigned_agent=task.assigned_agent,
        dependencies=list(task.dependencies),
        created_at=task.created_at,
        updated_at=task.updated_at,
        deadline=task.deadline,
        tags=list(task.tags),
        nexus_code=task.nexus_code,
        compiled_binary_size=len(task.compiled_binary) if task.compiled_binary else None,
        execution_result=task.execution_result,
        cost_estimate=task.cost_estimate,
        actual_cost=task.actual_cost,
        metadata=task.metadata,
    )


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_nexus_task(
    task_id: str,
    orchestrator = Depends(get_orchestrator),
    current_user: User = Depends(get_current_user),
):
    """Delete a NexusLang task."""
    if task_id not in orchestrator.tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Only allow deletion of pending tasks
    task = orchestrator.tasks[task_id]
    if task.status != TaskStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only delete pending tasks"
        )

    del orchestrator.tasks[task_id]

    # Remove from cache (would need to implement cache deletion)
    # await orchestrator.cache.delete(f"nexus_task:{task_id}")


@router.post("/execute", response_model=NexusCodeResponse)
async def execute_nexus_code(
    execution_data: NexusCodeExecution,
    orchestrator = Depends(get_orchestrator),
    current_user: User = Depends(get_current_user),
):
    """
    Execute NexusLang code directly.

    - Supports both interpreted and compiled execution
    - Returns execution results and performance metrics
    """
    try:
        result = await orchestrator.execute_nexus_code(
            execution_data.code,
            execution_data.compile_binary
        )

        return NexusCodeResponse(
            success=result['success'],
            result=result.get('result'),
            error=result.get('error'),
            binary_compiled=execution_data.compile_binary,
            execution_time=result.get('result', {}).get('execution_time'),
            binary_size=len(result.get('binary', b'')) if 'binary' in result else None,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Code execution failed: {str(e)}"
        )


@router.post("/tasks/{task_id}/assign")
async def assign_task_to_agent(
    task_id: str,
    agent_name: Optional[str] = None,
    orchestrator = Depends(get_orchestrator),
    current_user: User = Depends(get_current_user),
):
    """Manually assign a task to an agent."""
    if task_id not in orchestrator.tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    task = orchestrator.tasks[task_id]
    if task.status != TaskStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task is not in pending status"
        )

    success = await orchestrator.assign_task_to_agent(task_id, agent_name)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to assign task to agent"
        )

    return {"message": "Task assigned successfully"}


@router.get("/agents")
async def list_agents(
    orchestrator = Depends(get_orchestrator),
    current_user: User = Depends(get_current_user),
):
    """List all available agents and their status."""
    agents = {}
    for name, node in orchestrator.agent_nodes.items():
        agents[name] = {
            "role": node.role.value,
            "capabilities": list(node.capabilities),
            "workload": node.workload,
            "is_active": node.is_active,
            "performance_score": node.performance_score,
            "last_heartbeat": node.last_heartbeat.isoformat(),
        }

    return agents


@router.get("/status", response_model=SystemStatusResponse)
async def get_system_status(
    orchestrator = Depends(get_orchestrator),
    current_user: User = Depends(get_current_user),
):
    """Get comprehensive system status and metrics."""
    return await orchestrator.get_system_status()


@router.post("/agents/{agent_name}/heartbeat")
async def agent_heartbeat(
    agent_name: str,
    orchestrator = Depends(get_orchestrator),
):
    """Receive heartbeat from an agent."""
    if agent_name not in orchestrator.agent_nodes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )

    orchestrator.agent_nodes[agent_name].last_heartbeat = datetime.utcnow()
    orchestrator.agent_nodes[agent_name].is_active = True

    return {"message": "Heartbeat received"}


@router.post("/shutdown")
async def shutdown_orchestrator(
    background_tasks: BackgroundTasks,
    orchestrator = Depends(get_orchestrator),
    current_user: User = Depends(get_current_user),
):
    """Gracefully shutdown the orchestrator (admin only)."""
    # In a real implementation, you'd check for admin permissions
    background_tasks.add_task(orchestrator.shutdown)

    return {"message": "Orchestrator shutdown initiated"}
