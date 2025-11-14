"""
Real-time Monitoring System for Galion Platform v2.2
Provides live execution monitoring and status updates for autonomous systems.

Features:
- Real-time execution tracking
- Live status updates via WebSocket
- Performance metrics streaming
- Alert generation and notifications
- Execution timeline visualization
- Resource usage monitoring

"Your imagination is the end."
"""

import asyncio
from typing import Dict, List, Optional, Any, Callable, Set
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from enum import Enum
import logging
import json
import websockets
import uuid

logger = logging.getLogger(__name__)

class MonitoringEventType(Enum):
    """Types of monitoring events"""
    EXECUTION_STARTED = "execution_started"
    EXECUTION_PROGRESS = "execution_progress"
    EXECUTION_COMPLETED = "execution_completed"
    EXECUTION_FAILED = "execution_failed"
    STEP_STARTED = "step_started"
    STEP_COMPLETED = "step_completed"
    STEP_FAILED = "step_failed"
    APPROVAL_NEEDED = "approval_needed"
    APPROVAL_GRANTED = "approval_granted"
    RESOURCE_USAGE = "resource_usage"
    PERFORMANCE_METRIC = "performance_metric"
    ALERT_GENERATED = "alert_generated"

class MonitoringEvent(BaseModel):
    """A monitoring event"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: MonitoringEventType
    timestamp: datetime = Field(default_factory=datetime.now)

    # Event context
    execution_id: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None

    # Event data
    data: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "timestamp": self.timestamp.isoformat(),
            "execution_id": self.execution_id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "data": self.data,
            "metadata": self.metadata
        }

class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class Alert(BaseModel):
    """A monitoring alert"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    severity: AlertSeverity
    title: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.now)

    # Context
    execution_id: Optional[str] = None
    user_id: Optional[str] = None
    component: str  # "autonomous_executor", "workflow_engine", "agent_orchestrator"

    # Resolution
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None

class ExecutionTimeline(BaseModel):
    """Timeline of execution events"""

    execution_id: str
    events: List[MonitoringEvent] = Field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    def add_event(self, event: MonitoringEvent):
        """Add an event to the timeline"""
        self.events.append(event)

        # Update timing
        if not self.start_time or event.timestamp < self.start_time:
            self.start_time = event.timestamp
        if not self.end_time or event.timestamp > self.end_time:
            self.end_time = event.timestamp

    def get_duration(self) -> Optional[float]:
        """Get total execution duration in seconds"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

    def get_events_by_type(self, event_type: MonitoringEventType) -> List[MonitoringEvent]:
        """Get events of a specific type"""
        return [event for event in self.events if event.type == event_type]

class PerformanceMetrics(BaseModel):
    """Performance metrics for monitoring"""

    timestamp: datetime = Field(default_factory=datetime.now)
    execution_id: str

    # Timing metrics
    response_time: float = 0.0
    execution_time: float = 0.0

    # Resource metrics
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    network_io: float = 0.0

    # Agent metrics
    agent_cost: float = 0.0
    agent_calls: int = 0
    tool_calls: int = 0

    # System metrics
    active_executions: int = 0
    queue_size: int = 0
    error_rate: float = 0.0

class WebSocketClient:
    """WebSocket client for real-time updates"""

    def __init__(self, websocket, client_id: str):
        self.websocket = websocket
        self.client_id = client_id
        self.subscriptions: Set[str] = set()
        self.connected_at = datetime.now()
        self.last_ping = datetime.now()

    async def send_event(self, event: MonitoringEvent):
        """Send an event to this client"""
        try:
            await self.websocket.send(json.dumps({
                "type": "event",
                "data": event.to_dict()
            }))
            self.last_ping = datetime.now()
        except Exception as e:
            logger.error(f"Failed to send event to client {self.client_id}: {e}")

    async def send_alert(self, alert: Alert):
        """Send an alert to this client"""
        try:
            await self.websocket.send(json.dumps({
                "type": "alert",
                "data": alert.model_dump()
            }))
            self.last_ping = datetime.now()
        except Exception as e:
            logger.error(f"Failed to send alert to client {self.client_id}: {e}")

    def subscribe(self, execution_id: str):
        """Subscribe to execution updates"""
        self.subscriptions.add(execution_id)

    def unsubscribe(self, execution_id: str):
        """Unsubscribe from execution updates"""
        self.subscriptions.discard(execution_id)

    def is_subscribed(self, execution_id: str) -> bool:
        """Check if subscribed to execution"""
        return execution_id in self.subscriptions

class RealtimeMonitor:
    """
    Real-time monitoring system for autonomous executions.

    Provides live tracking, WebSocket updates, and alerting.
    """

    def __init__(self):
        self.timelines: Dict[str, ExecutionTimeline] = {}
        self.active_clients: Dict[str, WebSocketClient] = {}
        self.alerts: List[Alert] = []
        self.performance_history: List[PerformanceMetrics] = []

        # Configuration
        self.max_timeline_age = timedelta(hours=24)
        self.max_alerts = 1000
        self.performance_retention = timedelta(hours=1)

        # WebSocket server
        self.websocket_server = None
        self.is_running = False

        self.logger = logging.getLogger(f"{__name__}.monitor")

    async def start_monitoring(self, host: str = "localhost", port: int = 8765):
        """Start the monitoring system"""
        self.is_running = True

        # Start WebSocket server
        self.websocket_server = await websockets.serve(
            self._handle_websocket,
            host,
            port
        )

        self.logger.info(f"Real-time monitoring started on ws://{host}:{port}")

        # Start cleanup task
        asyncio.create_task(self._cleanup_task())

    async def stop_monitoring(self):
        """Stop the monitoring system"""
        self.is_running = False

        if self.websocket_server:
            self.websocket_server.close()
            await self.websocket_server.wait_closed()

        self.logger.info("Real-time monitoring stopped")

    def record_event(self, event: MonitoringEvent):
        """Record a monitoring event"""
        # Add to timeline
        if event.execution_id not in self.timelines:
            self.timelines[event.execution_id] = ExecutionTimeline(execution_id=event.execution_id)

        self.timelines[event.execution_id].add_event(event)

        # Broadcast to subscribed clients
        asyncio.create_task(self._broadcast_event(event))

        # Check for alerts
        asyncio.create_task(self._check_alerts(event))

        self.logger.debug(f"Recorded event: {event.type.value} for execution {event.execution_id}")

    async def _broadcast_event(self, event: MonitoringEvent):
        """Broadcast event to subscribed clients"""
        for client in self.active_clients.values():
            if client.is_subscribed(event.execution_id):
                await client.send_event(event)

    async def _check_alerts(self, event: MonitoringEvent):
        """Check if event triggers any alerts"""
        # Check for execution failures
        if event.type == MonitoringEventType.EXECUTION_FAILED:
            alert = Alert(
                severity=AlertSeverity.ERROR,
                title="Execution Failed",
                message=f"Execution {event.execution_id} failed",
                execution_id=event.execution_id,
                component="autonomous_executor"
            )
            await self._generate_alert(alert)

        # Check for long-running executions
        elif event.type == MonitoringEventType.EXECUTION_STARTED:
            # Schedule a check for long execution
            asyncio.create_task(self._check_long_execution(event.execution_id))

        # Check for step failures
        elif event.type == MonitoringEventType.STEP_FAILED:
            step_data = event.data.get("step_id", "unknown")
            alert = Alert(
                severity=AlertSeverity.WARNING,
                title="Step Failed",
                message=f"Step {step_data} failed in execution {event.execution_id}",
                execution_id=event.execution_id,
                component="autonomous_executor"
            )
            await self._generate_alert(alert)

    async def _check_long_execution(self, execution_id: str, threshold_minutes: int = 30):
        """Check if execution is running too long"""
        await asyncio.sleep(threshold_minutes * 60)  # Wait threshold time

        timeline = self.timelines.get(execution_id)
        if timeline and not timeline.end_time:
            alert = Alert(
                severity=AlertSeverity.WARNING,
                title="Long-Running Execution",
                message=f"Execution {execution_id} has been running for over {threshold_minutes} minutes",
                execution_id=execution_id,
                component="autonomous_executor"
            )
            await self._generate_alert(alert)

    async def _generate_alert(self, alert: Alert):
        """Generate and broadcast an alert"""
        self.alerts.append(alert)

        # Keep only recent alerts
        if len(self.alerts) > self.max_alerts:
            self.alerts = self.alerts[-self.max_alerts:]

        # Broadcast to all clients
        for client in self.active_clients.values():
            await client.send_alert(alert)

        self.logger.warning(f"Alert generated: {alert.title} - {alert.message}")

    def record_performance_metrics(self, metrics: PerformanceMetrics):
        """Record performance metrics"""
        self.performance_history.append(metrics)

        # Clean old metrics
        cutoff = datetime.now() - self.performance_retention
        self.performance_history = [
            m for m in self.performance_history
            if m.timestamp > cutoff
        ]

    async def _handle_websocket(self, websocket, path):
        """Handle WebSocket connections"""
        client_id = str(uuid.uuid4())
        client = WebSocketClient(websocket, client_id)
        self.active_clients[client_id] = client

        self.logger.info(f"WebSocket client connected: {client_id}")

        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self._handle_client_message(client, data)
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": "Invalid JSON message"
                    }))
                except Exception as e:
                    self.logger.error(f"Error handling message from {client_id}: {e}")
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": "Internal server error"
                    }))

        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            # Clean up client
            if client_id in self.active_clients:
                del self.active_clients[client_id]
            self.logger.info(f"WebSocket client disconnected: {client_id}")

    async def _handle_client_message(self, client: WebSocketClient, data: Dict[str, Any]):
        """Handle messages from WebSocket clients"""
        msg_type = data.get("type")

        if msg_type == "subscribe":
            execution_id = data.get("execution_id")
            if execution_id:
                client.subscribe(execution_id)
                await client.websocket.send(json.dumps({
                    "type": "subscribed",
                    "execution_id": execution_id
                }))

                # Send current timeline if available
                timeline = self.timelines.get(execution_id)
                if timeline:
                    for event in timeline.events[-10:]:  # Send last 10 events
                        await client.send_event(event)

        elif msg_type == "unsubscribe":
            execution_id = data.get("execution_id")
            if execution_id:
                client.unsubscribe(execution_id)
                await client.websocket.send(json.dumps({
                    "type": "unsubscribed",
                    "execution_id": execution_id
                }))

        elif msg_type == "ping":
            await client.websocket.send(json.dumps({
                "type": "pong",
                "timestamp": datetime.now().isoformat()
            }))

        elif msg_type == "get_status":
            # Send current status
            status = self.get_monitoring_status()
            await client.websocket.send(json.dumps({
                "type": "status",
                "data": status
            }))

    async def _cleanup_task(self):
        """Periodic cleanup task"""
        while self.is_running:
            try:
                await asyncio.sleep(300)  # Clean up every 5 minutes

                # Clean old timelines
                cutoff = datetime.now() - self.max_timeline_age
                to_remove = []

                for exec_id, timeline in self.timelines.items():
                    if timeline.end_time and timeline.end_time < cutoff:
                        to_remove.append(exec_id)

                for exec_id in to_remove:
                    del self.timelines[exec_id]

                # Clean old alerts (keep only last 100)
                if len(self.alerts) > 100:
                    self.alerts = self.alerts[-100:]

                # Clean disconnected clients (based on ping timeout)
                timeout_cutoff = datetime.now() - timedelta(minutes=5)
                disconnected = []

                for client_id, client in self.active_clients.items():
                    if client.last_ping < timeout_cutoff:
                        disconnected.append(client_id)

                for client_id in disconnected:
                    del self.active_clients[client_id]
                    self.logger.info(f"Cleaned up disconnected client: {client_id}")

                self.logger.debug(f"Cleanup completed: removed {len(to_remove)} timelines, {len(disconnected)} clients")

            except Exception as e:
                self.logger.error(f"Error in cleanup task: {e}")

    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        return {
            "active_executions": len(self.timelines),
            "active_clients": len(self.active_clients),
            "total_alerts": len(self.alerts),
            "active_alerts": len([a for a in self.alerts if not a.resolved]),
            "uptime": (datetime.now() - datetime.fromtimestamp(asyncio.get_event_loop().time())).total_seconds()
        }

    def get_execution_timeline(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get timeline for an execution"""
        timeline = self.timelines.get(execution_id)
        if not timeline:
            return None

        return {
            "execution_id": execution_id,
            "duration": timeline.get_duration(),
            "event_count": len(timeline.events),
            "events": [event.to_dict() for event in timeline.events[-50:]],  # Last 50 events
            "start_time": timeline.start_time.isoformat() if timeline.start_time else None,
            "end_time": timeline.end_time.isoformat() if timeline.end_time else None
        }

    def get_recent_alerts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        return [alert.model_dump() for alert in self.alerts[-limit:]]

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance metrics summary"""
        if not self.performance_history:
            return {}

        recent_metrics = [
            m for m in self.performance_history
            if m.timestamp > datetime.now() - timedelta(minutes=5)
        ]

        if not recent_metrics:
            return {}

        return {
            "avg_response_time": sum(m.response_time for m in recent_metrics) / len(recent_metrics),
            "avg_execution_time": sum(m.execution_time for m in recent_metrics) / len(recent_metrics),
            "avg_cpu_usage": sum(m.cpu_usage for m in recent_metrics) / len(recent_metrics),
            "avg_memory_usage": sum(m.memory_usage for m in recent_metrics) / len(recent_metrics),
            "total_agent_cost": sum(m.agent_cost for m in recent_metrics),
            "total_agent_calls": sum(m.agent_calls for m in recent_metrics),
            "avg_active_executions": sum(m.active_executions for m in recent_metrics) / len(recent_metrics)
        }

# Integration helper functions

def create_execution_event(
    execution_id: str,
    event_type: MonitoringEventType,
    data: Dict[str, Any] = None,
    user_id: str = None,
    session_id: str = None,
    metadata: Dict[str, Any] = None
) -> MonitoringEvent:
    """Helper to create monitoring events"""
    return MonitoringEvent(
        type=event_type,
        execution_id=execution_id,
        user_id=user_id,
        session_id=session_id,
        data=data or {},
        metadata=metadata or {}
    )

# Global monitor instance
monitor = RealtimeMonitor()
