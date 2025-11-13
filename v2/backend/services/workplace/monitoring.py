"""
Workplace Service Monitoring
Comprehensive monitoring, health checks, and metrics for workplace service.
"""

import logging
import time
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


@dataclass
class WorkplaceMetrics:
    """Workplace service metrics collection."""
    total_workspaces: int = 0
    total_members: int = 0
    active_sessions: int = 0
    total_tasks: int = 0
    completed_tasks: int = 0
    total_time_logged: float = 0.0
    total_billing_amount: float = 0.0
    ai_requests_count: int = 0
    ai_errors_count: int = 0
    websocket_connections: int = 0
    sync_events_processed: int = 0
    response_times: List[float] = None

    def __post_init__(self):
        if self.response_times is None:
            self.response_times = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "workspaces": {
                "total": self.total_workspaces,
                "active_members": self.total_members
            },
            "tasks": {
                "total": self.total_tasks,
                "completed": self.completed_tasks,
                "completion_rate": self.total_tasks and (self.completed_tasks / self.total_tasks) or 0
            },
            "time_tracking": {
                "total_hours": self.total_time_logged,
                "avg_daily_hours": self._calculate_avg_daily_hours()
            },
            "billing": {
                "total_amount": self.total_billing_amount,
                "currency": "USD"
            },
            "ai_service": {
                "requests_total": self.ai_requests_count,
                "errors_total": self.ai_errors_count,
                "success_rate": self.ai_requests_count and (1 - self.ai_errors_count / self.ai_requests_count) or 1
            },
            "real_time": {
                "websocket_connections": self.websocket_connections,
                "active_sessions": self.active_sessions
            },
            "sync": {
                "events_processed": self.sync_events_processed
            },
            "performance": {
                "avg_response_time": self._calculate_avg_response_time(),
                "response_time_p95": self._calculate_percentile_response_time(95),
                "response_time_p99": self._calculate_percentile_response_time(99)
            }
        }

    def _calculate_avg_daily_hours(self) -> float:
        """Calculate average daily hours logged."""
        # This is a simplified calculation - in production you'd use actual date ranges
        days = 30  # Assume 30-day period
        return self.total_time_logged / max(days, 1)

    def _calculate_avg_response_time(self) -> float:
        """Calculate average response time."""
        if not self.response_times:
            return 0.0
        return sum(self.response_times) / len(self.response_times)

    def _calculate_percentile_response_time(self, percentile: float) -> float:
        """Calculate percentile response time."""
        if not self.response_times:
            return 0.0
        sorted_times = sorted(self.response_times)
        index = int(len(sorted_times) * percentile / 100)
        return sorted_times[min(index, len(sorted_times) - 1)]

    def record_response_time(self, response_time: float):
        """Record a response time measurement."""
        self.response_times.append(response_time)
        # Keep only last 1000 measurements to prevent memory issues
        if len(self.response_times) > 1000:
            self.response_times = self.response_times[-1000:]


class WorkplaceHealthChecker:
    """Health checker for workplace service components."""

    def __init__(self):
        self.last_check = datetime.utcnow()
        self.check_interval = 60  # seconds
        self._health_cache = {}

    async def check_overall_health(self, db_session) -> Dict[str, Any]:
        """Perform comprehensive health check."""
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {},
            "response_time": 0
        }

        start_time = time.time()

        try:
            # Database connectivity
            health_status["checks"]["database"] = await self._check_database(db_session)

            # AI service availability
            health_status["checks"]["ai_service"] = await self._check_ai_service()

            # WebSocket service
            health_status["checks"]["websocket"] = await self._check_websocket_service()

            # External services
            health_status["checks"]["external_services"] = await self._check_external_services()

            # Resource usage
            health_status["checks"]["system_resources"] = self._check_system_resources()

            # Determine overall status
            all_checks = health_status["checks"]
            if any(check.get("status") == "unhealthy" for check in all_checks.values()):
                health_status["status"] = "unhealthy"
            elif any(check.get("status") == "degraded" for check in all_checks.values()):
                health_status["status"] = "degraded"

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            health_status["status"] = "error"
            health_status["error"] = str(e)

        health_status["response_time"] = time.time() - start_time
        return health_status

    async def _check_database(self, db_session) -> Dict[str, Any]:
        """Check database connectivity and basic queries."""
        try:
            start_time = time.time()

            # Test basic query
            from ..models.workplace import Workspace
            workspace_count = db_session.query(Workspace).count()

            response_time = time.time() - start_time

            return {
                "status": "healthy",
                "response_time": response_time,
                "workspace_count": workspace_count,
                "details": "Database connection successful"
            }

        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "details": "Database connection failed"
            }

    async def _check_ai_service(self) -> Dict[str, Any]:
        """Check AI service availability."""
        try:
            from .ai_service import AIService
            ai_service = AIService()

            # Test basic AI functionality (lightweight)
            if hasattr(ai_service, 'ai_router') and ai_service.ai_router:
                return {
                    "status": "healthy",
                    "provider": "openrouter",
                    "details": "AI service initialized successfully"
                }
            else:
                return {
                    "status": "degraded",
                    "details": "AI service using fallback mode"
                }

        except Exception as e:
            logger.error(f"AI service health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "details": "AI service unavailable"
            }

    async def _check_websocket_service(self) -> Dict[str, Any]:
        """Check WebSocket service status."""
        try:
            from .websocket_manager import websocket_manager

            connection_count = len(websocket_manager.active_connections)
            session_count = sum(len(sessions) for sessions in websocket_manager.active_connections.values())

            return {
                "status": "healthy",
                "active_connections": connection_count,
                "active_sessions": session_count,
                "details": "WebSocket service operational"
            }

        except Exception as e:
            logger.error(f"WebSocket health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "details": "WebSocket service error"
            }

    async def _check_external_services(self) -> Dict[str, Any]:
        """Check external service dependencies."""
        external_checks = {}

        # OpenRouter API
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get("https://openrouter.ai/api/v1/models", timeout=5) as response:
                    if response.status == 200:
                        external_checks["openrouter"] = "healthy"
                    else:
                        external_checks["openrouter"] = "degraded"
        except Exception:
            external_checks["openrouter"] = "unhealthy"

        # Determine overall status
        if all(status == "healthy" for status in external_checks.values()):
            overall_status = "healthy"
        elif any(status == "unhealthy" for status in external_checks.values()):
            overall_status = "unhealthy"
        else:
            overall_status = "degraded"

        return {
            "status": overall_status,
            "services": external_checks,
            "details": f"External services checked: {len(external_checks)}"
        }

    def _check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            # Determine status based on thresholds
            if cpu_percent > 90 or memory.percent > 90 or disk.percent > 95:
                status = "unhealthy"
            elif cpu_percent > 70 or memory.percent > 80 or disk.percent > 85:
                status = "degraded"
            else:
                status = "healthy"

            return {
                "status": status,
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent,
                "details": f"CPU: {cpu_percent}%, Memory: {memory.percent}%, Disk: {disk.percent}%"
            }

        except Exception as e:
            logger.error(f"System resources check failed: {e}")
            return {
                "status": "unknown",
                "error": str(e),
                "details": "Unable to check system resources"
            }


class WorkplaceMonitor:
    """Main monitoring service for workplace operations."""

    def __init__(self):
        self.metrics = WorkplaceMetrics()
        self.health_checker = WorkplaceHealthChecker()
        self._is_monitoring = False

    async def start_monitoring(self):
        """Start the monitoring service."""
        if self._is_monitoring:
            return

        self._is_monitoring = True
        logger.info("🏥 Workplace monitoring service started")

        # Start background monitoring tasks
        # In production, you might want to run these as separate tasks

    async def stop_monitoring(self):
        """Stop the monitoring service."""
        self._is_monitoring = False
        logger.info("🏥 Workplace monitoring service stopped")

    async def get_health_status(self, db_session) -> Dict[str, Any]:
        """Get current health status."""
        return await self.health_checker.check_overall_health(db_session)

    async def get_metrics(self, db_session) -> Dict[str, Any]:
        """Get current metrics."""
        # Update metrics from database
        await self._update_metrics_from_db(db_session)
        return self.metrics.to_dict()

    async def _update_metrics_from_db(self, db_session):
        """Update metrics from database queries."""
        try:
            from ..models.workplace import Workspace, WorkspaceMember, Task, TimeLog, Payment, SyncEvent, LiveSession

            # Workspace metrics
            self.metrics.total_workspaces = db_session.query(Workspace).count()
            self.metrics.total_members = db_session.query(WorkspaceMember).count()

            # Task metrics
            self.metrics.total_tasks = db_session.query(Task).count()
            self.metrics.completed_tasks = db_session.query(Task).filter(Task.status == "done").count()

            # Time tracking metrics
            time_logs = db_session.query(TimeLog).all()
            self.metrics.total_time_logged = sum(log.hours for log in time_logs)

            # Billing metrics
            payments = db_session.query(Payment).filter(Payment.status == "paid").all()
            self.metrics.total_billing_amount = sum(payment.amount for payment in payments)

            # Sync events
            self.metrics.sync_events_processed = db_session.query(SyncEvent).count()

            # Active sessions (simplified)
            self.metrics.active_sessions = db_session.query(LiveSession).filter(LiveSession.is_active == True).count()

        except Exception as e:
            logger.error(f"Failed to update metrics from database: {e}")

    def record_ai_request(self, success: bool = True):
        """Record an AI service request."""
        self.metrics.ai_requests_count += 1
        if not success:
            self.metrics.ai_errors_count += 1

    def record_websocket_connection(self, connected: bool = True):
        """Record WebSocket connection change."""
        if connected:
            self.metrics.websocket_connections += 1
        else:
            self.metrics.websocket_connections = max(0, self.metrics.websocket_connections - 1)

    def record_response_time(self, response_time: float):
        """Record API response time."""
        self.metrics.record_response_time(response_time)


# Global monitoring instance
workplace_monitor = WorkplaceMonitor()


@asynccontextmanager
async def monitoring_context(operation: str):
    """Context manager for monitoring operations."""
    start_time = time.time()
    try:
        yield
        response_time = time.time() - start_time
        workplace_monitor.record_response_time(response_time)
        logger.info(f"✅ {operation} completed in {response_time:.3f}s")
    except Exception as e:
        response_time = time.time() - start_time
        workplace_monitor.record_response_time(response_time)
        logger.error(f"❌ {operation} failed in {response_time:.3f}s: {e}")
        raise


def create_monitoring_middleware():
    """Create monitoring middleware for FastAPI."""
    from fastapi import Request, Response
    import time

    async def monitoring_middleware(request: Request, call_next):
        start_time = time.time()

        # Record the request
        logger.info(f"📨 {request.method} {request.url.path} - Started")

        try:
            response = await call_next(request)
            process_time = time.time() - start_time

            # Record successful response
            workplace_monitor.record_response_time(process_time)
            logger.info(f"✅ {request.method} {request.url.path} - {response.status_code} in {process_time:.3f}s")

            return response

        except Exception as e:
            process_time = time.time() - start_time
            workplace_monitor.record_response_time(process_time)
            logger.error(f"❌ {request.method} {request.url.path} - Error in {process_time:.3f}s: {e}")
            raise

    return monitoring_middleware
