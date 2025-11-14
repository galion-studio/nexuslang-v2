"""
Agent API Endpoints for Galion Platform v2.2
Provides RESTful API for interacting with AI agents.

"Your imagination is the end."
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import sys
import os

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="", tags=["agents"])

# Global variables - will be initialized when needed
orchestrator = None
imports_available = None

def _ensure_imports():
    """Lazy import of dependencies to avoid module-level import issues"""
    global orchestrator, imports_available

    if imports_available is not None:
        return imports_available

    try:
        # Add current directory to path for imports
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)

        from core.auth import create_access_token, decode_token
        from services.agents.agent_orchestrator import AgentOrchestrator
        from services.agents.base_agent import AgentContext, AgentResult

        # Initialize orchestrator
        orchestrator = AgentOrchestrator()

        imports_available = True
        logger.info("✅ Agent dependencies loaded successfully")
        return True

    except ImportError as e:
        logger.warning(f"❌ Agent dependencies not available: {e}")
        imports_available = False
        return False

# Pydantic models for API
class AgentRequest(BaseModel):
    """Request model for agent interactions"""

    prompt: str = Field(..., description="The user's request or question")
    agent_type: Optional[str] = Field(None, description="Specific agent to use (optional)")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    priority: str = Field("normal", description="Request priority (low, normal, high, urgent)")

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "How can I improve my investment portfolio?",
                "agent_type": "financial_advisor",
                "context": {"user_id": "123", "risk_tolerance": "moderate"},
                "priority": "normal"
            }
        }

class AgentResponse(BaseModel):
    """Response model for agent interactions"""

    success: bool
    response: str
    cost: float
    execution_time: float
    metadata: Dict[str, Any]
    error: Optional[str] = None
    next_actions: List[str] = []

class AgentStatus(BaseModel):
    """Agent status information"""

    name: str
    version: str
    status: str
    execution_count: int
    total_cost: float
    average_execution_time: float
    success_rate: float
    capabilities: Dict[str, Any]
    personality: Dict[str, Any]

class AgentHealthResponse(BaseModel):
    """Health check response for agent system"""

    status: str
    agent_count: Optional[int] = None
    queue_size: Optional[int] = None
    timestamp: datetime
    error: Optional[str] = None

class OrchestratorStatus(BaseModel):
    """Orchestrator status information"""

    is_running: bool
    agent_count: int
    available_agents: List[str]
    metrics: Dict[str, Any]
    queue_status: Dict[str, Any]
    cost_limits: Dict[str, Any]

class TaskStatus(BaseModel):
    """Task status information"""

    task_id: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[AgentResponse] = None

# Initialize agents on startup
@router.on_event("startup")
async def startup_event():
    """Initialize agents when the API starts"""
    if not _ensure_imports():
        logger.warning("❌ Cannot initialize agent system - dependencies not available")
        return

    try:
        logger.info("Initializing agent system...")

        # Import agent classes
        try:
            from services.agents.financial_advisor import FinancialAdvisorAgent
            from services.agents.customer_support import CustomerSupportAgent
            from services.agents.monitoring_agent import MonitoringAgent
            logger.info("Agent classes imported successfully")
        except ImportError as e:
            logger.error(f"Failed to import agent classes: {e}")
            return

        # Register agents
        try:
            fa_agent = FinancialAdvisorAgent()
            cs_agent = CustomerSupportAgent()
            mon_agent = MonitoringAgent()

            orchestrator.register_agent(fa_agent)
            orchestrator.register_agent(cs_agent)
            orchestrator.register_agent(mon_agent)

            logger.info(f"Registered agents: {[agent.name for agent in orchestrator.agents.values()]}")
        except Exception as e:
            logger.error(f"Failed to register agents: {e}")
            return

        # Start queue processor
        try:
            orchestrator.start_queue_processor()
            logger.info("Queue processor started")
        except Exception as e:
            logger.error(f"Failed to start queue processor: {e}")
            return

        logger.info("✅ Agent system initialized successfully")

    except Exception as e:
        logger.error(f"❌ Failed to initialize agent system: {e}")
        # Don't re-raise - let the API start without agents rather than crash

@router.post("/execute", response_model=AgentResponse)
async def execute_agent(
    request: AgentRequest,
    background_tasks: BackgroundTasks
):
    """
    Execute an agent request.

    This endpoint allows users to interact with AI agents through the orchestrator.
    The orchestrator will automatically select the best agent or use the specified one.
    """
    if not imports_available:
        raise HTTPException(status_code=503, detail="Agent system dependencies not available")

    try:
        # Create agent context with user information (mock for now)
        context = AgentContext(
            user_id="demo-user",
            user_preferences={},
            system_state={"platform_version": "v2.2"}
        )

        # Merge with request context
        if request.context:
            context.metadata.update(request.context)

        # Execute the agent request
        result = await orchestrator.execute(
            prompt=request.prompt,
            agent_type=request.agent_type,
            context=context,
            priority=request.priority
        )

        # Convert AgentResult to API response format
        response = AgentResponse(
            success=result.success,
            response=result.response,
            cost=result.cost,
            execution_time=result.execution_time,
            metadata=result.metadata,
            error=result.error,
            next_actions=result.next_actions
        )

        # Log the interaction for analytics
        background_tasks.add_task(
            log_agent_interaction,
            user_id="demo-user",
            request=request,
            response=response
        )

        return response

    except Exception as e:
        logger.error(f"Agent execution failed: {e}")
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")

@router.post("/queue", response_model=Dict[str, str])
async def queue_agent_task(
    request: AgentRequest,
):
    """
    Queue an agent task for later execution.

    Useful for long-running tasks or batch processing.
    """
    try:
        # Create agent context
        context = AgentContext(
            user_id="demo-user",
            user_preferences={},
            system_state={"platform_version": "v2.2"}
        )

        if request.context:
            context.metadata.update(request.context)

        # Queue the task
        task_id = await orchestrator.queue_task(
            prompt=request.prompt,
            agent_type=request.agent_type,
            context=context,
            priority=request.priority
        )

        return {"task_id": task_id, "status": "queued"}

    except Exception as e:
        logger.error(f"Task queuing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Task queuing failed: {str(e)}")

@router.get("/status", response_model=OrchestratorStatus)
async def get_orchestrator_status(
):
    """
    Get the current status of the agent orchestrator.

    Includes metrics, queue status, and available agents.
    """
    try:
        # Check if user has admin permissions (would implement proper RBAC)
        # Admin check removed for demo

        status = orchestrator.get_status()
        return OrchestratorStatus(**status)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Status retrieval failed: {str(e)}")

@router.get("/agents", response_model=List[AgentStatus])
async def list_agents():
    """
    List all available agents and their status.

    Provides detailed information about each agent's capabilities and performance.
    """
    try:
        agents = orchestrator.get_agent_status()
        return [AgentStatus(**agent) for agent in agents]

    except Exception as e:
        logger.error(f"Agent listing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Agent listing failed: {str(e)}")

@router.get("/agents/{agent_name}", response_model=AgentStatus)
async def get_agent_status(
    agent_name: str,
):
    """
    Get detailed status for a specific agent.
    """
    try:
        agent_status = orchestrator.get_agent_status(agent_name)

        if isinstance(agent_status, dict) and "error" in agent_status:
            raise HTTPException(status_code=404, detail=agent_status["error"])

        return AgentStatus(**agent_status)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Agent status retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Agent status retrieval failed: {str(e)}")

@router.post("/save-state")
async def save_orchestrator_state(
):
    """
    Manually save the orchestrator state.

    Admin endpoint for state persistence.
    """
    try:
        # Admin check removed for demo

        await orchestrator.save_state()
        return {"message": "State saved successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"State save failed: {e}")
        raise HTTPException(status_code=500, detail=f"State save failed: {str(e)}")

@router.post("/load-state")
async def load_orchestrator_state(
):
    """
    Manually load the orchestrator state.

    Admin endpoint for state restoration.
    """
    try:
        # Admin check removed for demo

        state = await orchestrator.load_state()
        return {"message": "State loaded successfully", "state": state}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"State load failed: {e}")
        raise HTTPException(status_code=500, detail=f"State load failed: {str(e)}")

# Background task functions
async def log_agent_interaction(
    user_id: str,
    request: AgentRequest,
    response: AgentResponse
):
    """
    Log agent interactions for analytics and monitoring.

    This would typically write to a database or analytics service.
    """
    try:
        interaction_log = {
            "user_id": user_id,
            "timestamp": datetime.now(),
            "request": request.model_dump(),
            "response": response.model_dump(),
            "agent_type": request.agent_type,
            "cost": response.cost,
            "success": response.success
        }

        # In a real implementation, this would save to database
        logger.info(f"Agent interaction logged: {interaction_log}")

    except Exception as e:
        logger.error(f"Failed to log agent interaction: {e}")

# Health check endpoint
@router.get("/health", response_model=AgentHealthResponse)
async def agent_health_check():
    """Health check for the agent system"""
    if not _ensure_imports():
        return {
            "status": "unhealthy",
            "error": "Agent dependencies not available",
            "timestamp": datetime.now()
        }

    try:
        status = orchestrator.get_status()
        return {
            "status": "healthy" if status["is_running"] else "unhealthy",
            "agent_count": status["agent_count"],
            "queue_size": status["queue_status"]["queue_size"],
            "timestamp": datetime.now()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now()
        }
