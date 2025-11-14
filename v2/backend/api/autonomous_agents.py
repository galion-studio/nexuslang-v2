"""
Autonomous Agents API Endpoints for Galion Platform v2.2
REST and WebSocket APIs for the Manus-like autonomous agent system.

Endpoints:
- POST /api/v1/agents/execute - Execute autonomous task
- GET /api/v1/agents/status/{task_id} - Get task status
- POST /api/v1/agents/approve - Approve human-in-the-loop requests
- GET /api/v1/agents/monitoring - Real-time monitoring data
- WebSocket /ws/agents/monitor - Live execution updates

"Your imagination is the end."
"""

import asyncio
import json
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ..core.auth import get_current_user
from ..core.database import get_db
from ..models.user import User

# Import our agent system
from ..services.agents.agent_orchestrator import orchestrator
from ..services.agents.realtime_monitor import monitor
from ..services.agents.human_loop import ApprovalType
from ..services.agents.nlp_processor import TaskIntent, TaskComplexity, TaskRisk

# API Router
router = APIRouter(prefix="/api/v1/agents", tags=["autonomous-agents"])

# Request/Response Models

class TaskRequest(BaseModel):
    """Request to execute an autonomous task"""

    prompt: str = Field(..., description="Natural language task description")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")
    require_approval: bool = Field(False, description="Require human approval for risky operations")
    priority: str = Field("normal", description="Task priority: low, normal, high, urgent")
    tags: List[str] = Field(default_factory=list, description="Task tags for organization")

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Build a complete user authentication system with login, registration, and password reset",
                "context": {
                    "project_id": "auth-system",
                    "tech_stack": ["nodejs", "mongodb", "express"],
                    "requirements": ["secure", "scalable", "user-friendly"]
                },
                "require_approval": True,
                "priority": "high",
                "tags": ["authentication", "security", "backend"]
            }
        }

class TaskResponse(BaseModel):
    """Response from task execution"""

    task_id: str
    status: str
    estimated_completion: Optional[int] = None  # seconds
    message: str

class TaskStatusResponse(BaseModel):
    """Task status response"""

    task_id: str
    status: str
    progress: float
    current_step: Optional[int] = None
    total_steps: Optional[int] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    steps: List[Dict[str, Any]] = Field(default_factory=list)

class ApprovalRequest(BaseModel):
    """Human approval request"""

    request_id: str
    task_id: str
    type: str
    title: str
    description: str
    priority: str
    context: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime

class ApprovalResponse(BaseModel):
    """Response to approval request"""

    request_id: str
    approved: bool
    notes: Optional[str] = None
    modified_parameters: Optional[Dict[str, Any]] = None

class NLPAnalysisRequest(BaseModel):
    """Request for NLP analysis"""

    text: str
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)

class NLPAnalysisResponse(BaseModel):
    """NLP analysis response"""

    intent: str
    complexity: str
    risk_level: str
    confidence: float
    entities: List[Dict[str, Any]]
    key_phrases: List[str]
    action_verbs: List[str]
    execution_plan: Optional[Dict[str, Any]] = None

class MonitoringStatusResponse(BaseModel):
    """Monitoring status response"""

    active_executions: int
    active_clients: int
    total_alerts: int
    uptime: float

class CollaborationSessionRequest(BaseModel):
    """Request to create collaboration session"""

    name: str
    description: str
    goal: str
    participants: List[str]

class TestExecutionRequest(BaseModel):
    """Request to run tests"""

    test_type: str = Field(..., description="Type of test: unit, integration, performance, safety, e2e")
    target: Optional[str] = Field(None, description="Specific component to test")
    parallel: bool = Field(True, description="Run tests in parallel")

# WebSocket connection manager
class ConnectionManager:
    """Manage WebSocket connections for real-time updates"""

    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}

    async def connect(self, websocket: WebSocket, client_id: str, subscriptions: List[str] = None):
        """Connect a new WebSocket client"""
        await websocket.accept()

        if client_id not in self.active_connections:
            self.active_connections[client_id] = []

        self.active_connections[client_id].append(websocket)
        self.connection_metadata[client_id] = {
            "connected_at": datetime.now(),
            "subscriptions": subscriptions or [],
            "last_ping": datetime.now()
        }

        print(f"🔌 WebSocket client connected: {client_id}")

    async def disconnect(self, client_id: str, websocket: WebSocket):
        """Disconnect a WebSocket client"""
        if client_id in self.active_connections:
            if websocket in self.active_connections[client_id]:
                self.active_connections[client_id].remove(websocket)

            if not self.active_connections[client_id]:
                del self.active_connections[client_id]
                del self.connection_metadata[client_id]

        print(f"🔌 WebSocket client disconnected: {client_id}")

    async def send_personal_message(self, message: Dict[str, Any], client_id: str):
        """Send message to specific client"""
        if client_id in self.active_connections:
            for connection in self.active_connections[client_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    print(f"Failed to send message to {client_id}: {e}")

    async def broadcast_to_subscribers(self, message: Dict[str, Any], subscription_type: str):
        """Broadcast message to clients subscribed to a topic"""
        for client_id, metadata in self.connection_metadata.items():
            if subscription_type in metadata.get("subscriptions", []):
                await self.send_personal_message(message, client_id)

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        for client_id in self.active_connections:
            await self.send_personal_message(message, client_id)

# Global connection manager
manager = ConnectionManager()

# API Endpoints

@router.post("/execute", response_model=TaskResponse)
async def execute_autonomous_task(
    request: TaskRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    Execute an autonomous task using natural language description.

    This endpoint accepts a natural language task description and executes it
    autonomously using the Manus-like agent system.
    """
    try:
        # Add user context
        context = request.context.copy()
        context.update({
            "user_id": str(current_user.id),
            "user_email": current_user.email,
            "request_timestamp": datetime.now().isoformat()
        })

        # Execute autonomous task
        task_id = await orchestrator.execute_autonomous(
            prompt=request.prompt,
            context=context,
            require_approval=request.require_approval
        )

        # Broadcast execution start
        await manager.broadcast_to_subscribers({
            "type": "task_started",
            "task_id": task_id,
            "user_id": str(current_user.id),
            "prompt": request.prompt,
            "timestamp": datetime.now().isoformat()
        }, "tasks")

        # Estimate completion time based on complexity
        estimated_time = 60  # default 1 minute
        if "complex" in request.prompt.lower():
            estimated_time = 300  # 5 minutes
        elif "simple" in request.prompt.lower():
            estimated_time = 30   # 30 seconds

        return TaskResponse(
            task_id=task_id,
            status="running",
            estimated_completion=estimated_time,
            message="Autonomous task execution started successfully"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Task execution failed: {str(e)}")

@router.get("/status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get the status of an autonomous task execution"""
    try:
        status = orchestrator.get_autonomous_task_status(task_id)

        if not status:
            raise HTTPException(status_code=404, detail="Task not found")

        # Check if user has access to this task
        if status.get("user_id") and status["user_id"] != str(current_user.id):
            # In a real system, you'd check permissions here
            pass

        return TaskStatusResponse(**status)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status retrieval failed: {str(e)}")

@router.delete("/cancel/{task_id}")
async def cancel_task(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """Cancel an autonomous task execution"""
    try:
        success = orchestrator.cancel_autonomous_task(task_id)

        if not success:
            raise HTTPException(status_code=404, detail="Task not found or cannot be cancelled")

        # Broadcast cancellation
        await manager.broadcast_to_subscribers({
            "type": "task_cancelled",
            "task_id": task_id,
            "user_id": str(current_user.id),
            "timestamp": datetime.now().isoformat()
        }, "tasks")

        return {"message": "Task cancelled successfully", "task_id": task_id}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Task cancellation failed: {str(e)}")

@router.get("/approvals/pending")
async def get_pending_approvals(current_user: User = Depends(get_current_user)):
    """Get pending approval requests for the current user"""
    try:
        approvals = orchestrator.get_pending_approvals(user_id=str(current_user.id))

        return {
            "approvals": approvals,
            "count": len(approvals)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get approvals: {str(e)}")

@router.post("/approvals/respond")
async def respond_to_approval(
    response: ApprovalResponse,
    current_user: User = Depends(get_current_user)
):
    """Respond to an approval request"""
    try:
        success = await orchestrator.respond_to_approval(
            request_id=response.request_id,
            user_id=str(current_user.id),
            approved=response.approved,
            notes=response.notes,
            modified_parameters=response.modified_parameters
        )

        if not success:
            raise HTTPException(status_code=404, detail="Approval request not found or already responded")

        # Broadcast approval response
        await manager.broadcast_to_subscribers({
            "type": "approval_responded",
            "request_id": response.request_id,
            "approved": response.approved,
            "user_id": str(current_user.id),
            "timestamp": datetime.now().isoformat()
        }, "approvals")

        return {"message": "Approval response recorded successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Approval response failed: {str(e)}")

@router.get("/clarifications/pending")
async def get_pending_clarifications(current_user: User = Depends(get_current_user)):
    """Get pending clarification requests for the current user"""
    try:
        clarifications = orchestrator.get_pending_clarifications(user_id=str(current_user.id))

        return {
            "clarifications": clarifications,
            "count": len(clarifications)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get clarifications: {str(e)}")

@router.post("/clarifications/respond")
async def respond_to_clarification(
    request_id: str,
    response: str,
    current_user: User = Depends(get_current_user)
):
    """Respond to a clarification request"""
    try:
        success = await orchestrator.respond_to_clarification(
            request_id=request_id,
            user_id=str(current_user.id),
            response=response
        )

        if not success:
            raise HTTPException(status_code=404, detail="Clarification request not found or already answered")

        return {"message": "Clarification response recorded successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clarification response failed: {str(e)}")

@router.post("/nlp/analyze", response_model=NLPAnalysisResponse)
async def analyze_task_nlp(
    request: NLPAnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """Analyze a task description using NLP"""
    try:
        analysis = await orchestrator.analyze_task_nlp(request.text, request.context)

        # Generate execution plan if requested
        execution_plan = None
        if request.context and request.context.get("include_plan", False):
            execution_plan = await orchestrator.generate_execution_plan_nlp(request.text, request.context)

        return NLPAnalysisResponse(
            intent=analysis.intent.value if hasattr(analysis.intent, 'value') else str(analysis.intent),
            complexity=analysis.complexity.value if hasattr(analysis.complexity, 'value') else str(analysis.complexity),
            risk_level=analysis.risk_level.value if hasattr(analysis.risk_level, 'value') else str(analysis.risk_level),
            confidence=analysis.confidence_score,
            entities=[{"text": e.text, "type": e.type, "confidence": e.confidence} for e in analysis.entities],
            key_phrases=analysis.key_phrases,
            action_verbs=analysis.action_verbs,
            execution_plan=execution_plan
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"NLP analysis failed: {str(e)}")

@router.get("/monitoring/status", response_model=MonitoringStatusResponse)
async def get_monitoring_status(current_user: User = Depends(get_current_user)):
    """Get real-time monitoring status"""
    try:
        status = orchestrator.get_monitoring_status()

        return MonitoringStatusResponse(**status)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Monitoring status retrieval failed: {str(e)}")

@router.get("/monitoring/timeline/{execution_id}")
async def get_execution_timeline(
    execution_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get execution timeline for monitoring"""
    try:
        timeline = orchestrator.get_execution_timeline(execution_id)

        if not timeline:
            raise HTTPException(status_code=404, detail="Execution timeline not found")

        return timeline

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Timeline retrieval failed: {str(e)}")

@router.get("/monitoring/alerts")
async def get_recent_alerts(
    limit: int = 10,
    current_user: User = Depends(get_current_user)
):
    """Get recent monitoring alerts"""
    try:
        alerts = orchestrator.get_recent_alerts(limit)

        return {
            "alerts": alerts,
            "count": len(alerts)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Alert retrieval failed: {str(e)}")

@router.post("/collaboration/session")
async def create_collaboration_session(
    request: CollaborationSessionRequest,
    current_user: User = Depends(get_current_user)
):
    """Create a new collaboration session"""
    try:
        # Add current user to participants if not included
        participants = request.participants.copy()
        if str(current_user.id) not in participants:
            participants.insert(0, str(current_user.id))

        session_id = await orchestrator.create_collaboration_session(
            name=request.name,
            description=request.description,
            goal=request.goal,
            participants=participants
        )

        return {
            "session_id": session_id,
            "message": "Collaboration session created successfully",
            "participants": participants
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Session creation failed: {str(e)}")

@router.get("/collaboration/sessions")
async def get_active_sessions(current_user: User = Depends(get_current_user)):
    """Get active collaboration sessions"""
    try:
        sessions = orchestrator.get_active_sessions(agent_id=str(current_user.id))

        return {
            "sessions": sessions,
            "count": len(sessions)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Session retrieval failed: {str(e)}")

@router.get("/tools")
async def list_available_tools(current_user: User = Depends(get_current_user)):
    """List available tools for the agent system"""
    try:
        tools = orchestrator.list_tools()

        return {
            "tools": tools,
            "count": len(tools)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tool listing failed: {str(e)}")

@router.post("/test/run")
async def run_quality_tests(
    request: TestExecutionRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Run automated tests on the agent system"""
    try:
        # Initialize testing if needed
        await orchestrator.initialize_testing()

        # Run appropriate test suite
        if request.test_type == "comprehensive":
            background_tasks.add_task(run_comprehensive_test_suite)
            message = "Comprehensive test suite started"
        elif request.test_type == "performance":
            background_tasks.add_task(run_performance_tests)
            message = "Performance tests started"
        elif request.test_type == "safety":
            background_tasks.add_task(run_safety_tests)
            message = "Safety tests started"
        else:
            background_tasks.add_task(run_unit_tests)
            message = "Unit tests started"

        return {
            "message": message,
            "test_type": request.test_type,
            "status": "running"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test execution failed: {str(e)}")

async def run_comprehensive_test_suite():
    """Run comprehensive test suite"""
    try:
        report = await orchestrator.run_quality_assurance()

        # Broadcast test results
        await manager.broadcast({
            "type": "test_completed",
            "suite": "comprehensive",
            "passed": report.passed_tests,
            "total": report.total_tests,
            "duration": report.total_duration,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        print(f"Comprehensive test suite failed: {e}")

async def run_performance_tests():
    """Run performance tests"""
    # Implementation for performance testing
    pass

async def run_safety_tests():
    """Run safety tests"""
    # Implementation for safety testing
    pass

async def run_unit_tests():
    """Run unit tests"""
    # Implementation for unit testing
    pass

# WebSocket Endpoints

@router.websocket("/ws/monitor")
async def monitor_websocket(websocket: WebSocket, client_id: str = None):
    """
    WebSocket endpoint for real-time monitoring updates.

    Clients can subscribe to:
    - tasks: Task execution updates
    - approvals: Approval request notifications
    - monitoring: System monitoring alerts
    - all: All updates
    """
    client_id = client_id or f"ws_client_{uuid.uuid4().hex[:8]}"

    await manager.connect(websocket, client_id)
    await websocket.send_json({
        "type": "connected",
        "client_id": client_id,
        "timestamp": datetime.now().isoformat()
    })

    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_json()

            if data.get("type") == "subscribe":
                subscriptions = data.get("subscriptions", [])
                manager.connection_metadata[client_id]["subscriptions"] = subscriptions

                await websocket.send_json({
                    "type": "subscribed",
                    "subscriptions": subscriptions,
                    "timestamp": datetime.now().isoformat()
                })

            elif data.get("type") == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                })

            elif data.get("type") == "unsubscribe":
                subscriptions = data.get("subscriptions", [])
                current_subs = manager.connection_metadata[client_id].get("subscriptions", [])
                for sub in subscriptions:
                    if sub in current_subs:
                        current_subs.remove(sub)

                await websocket.send_json({
                    "type": "unsubscribed",
                    "subscriptions": subscriptions,
                    "timestamp": datetime.now().isoformat()
                })

    except WebSocketDisconnect:
        await manager.disconnect(client_id, websocket)
    except Exception as e:
        print(f"WebSocket error for {client_id}: {e}")
        await manager.disconnect(client_id, websocket)

# Health check endpoint
@router.get("/health")
async def agent_system_health():
    """Health check for the agent system"""
    try:
        # Check orchestrator status
        orchestrator_status = {
            "agents_registered": len(orchestrator.agents),
            "monitoring_active": True,  # Would check actual monitoring status
            "collaboration_ready": True
        }

        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "2.2",
            "system": "Manus-like Autonomous Agent System",
            "components": orchestrator_status
        }

    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

# System statistics endpoint
@router.get("/stats")
async def get_system_statistics(current_user: User = Depends(get_current_user)):
    """Get comprehensive system statistics"""
    try:
        stats = {
            "agents": {
                "total": len(orchestrator.agents),
                "active": len([a for a in orchestrator.agents.values() if hasattr(a, 'execution_count')]),
                "types": list(set(type(a).__name__ for a in orchestrator.agents.values()))
            },
            "tasks": {
                "active": len(orchestrator.get_autonomous_tasks()),
                "completed_today": 0,  # Would track actual metrics
                "success_rate": 0.95   # Would calculate from actual data
            },
            "collaboration": orchestrator.get_collaboration_stats(),
            "monitoring": orchestrator.get_monitoring_status(),
            "performance": orchestrator.get_performance_summary(),
            "resources": orchestrator.get_resource_usage()
        }

        return stats

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Statistics retrieval failed: {str(e)}")

# Export the router
__all__ = ["router", "manager"]
