"""
Advanced monitoring and observability for Galion AI
Comprehensive logging, metrics, alerting, and dashboards
"""

import time
import logging
import json
import asyncio
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from collections import defaultdict, deque
import threading
import psutil
import os
from pathlib import Path

# Optional monitoring dependencies
try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastAPIIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False
    sentry_sdk = None

try:
    from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, generate_latest
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    Counter = Histogram = Gauge = CollectorRegistry = generate_latest = None

try:
    import datadog
    DATADOG_AVAILABLE = True
except ImportError:
    DATADOG_AVAILABLE = False
    datadog = None


class MonitoringConfig:
    """Monitoring configuration"""

    def __init__(self):
        self.enabled = True
        self.log_level = logging.INFO
        self.log_to_file = True
        self.log_to_console = True
        self.log_directory = "logs"
        self.max_log_files = 30
        self.max_log_size_mb = 100

        # External services
        self.sentry_dsn = os.getenv("SENTRY_DSN")
        self.datadog_api_key = os.getenv("DATADOG_API_KEY")
        self.datadog_app_key = os.getenv("DATADOG_APP_KEY")

        # Metrics
        self.metrics_enabled = True
        self.metrics_port = 9090

        # Alerting
        self.alerting_enabled = True
        self.alert_webhook_url = os.getenv("ALERT_WEBHOOK_URL")


class LogContext:
    """Context manager for structured logging"""

    def __init__(self, logger, **context):
        self.logger = logger
        self.context = context
        self.start_time = time.time()

    def __enter__(self):
        self.logger.info(f"Starting operation: {self.context.get('operation', 'unknown')}",
                        extra=self.context)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        self.context['duration_seconds'] = round(duration, 3)

        if exc_type:
            self.context['error_type'] = exc_type.__name__
            self.context['error_message'] = str(exc_val)
            self.logger.error(f"Operation failed: {self.context.get('operation', 'unknown')}",
                            extra=self.context, exc_info=exc_tb)
        else:
            self.logger.info(f"Operation completed: {self.context.get('operation', 'unknown')}",
                           extra=self.context)


class MetricsCollector:
    """Advanced metrics collection"""

    def __init__(self):
        self.registry = CollectorRegistry() if PROMETHEUS_AVAILABLE else None

        # Core metrics
        self.http_requests_total = self._create_counter(
            'http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status_code']
        )

        self.http_request_duration = self._create_histogram(
            'http_request_duration_seconds',
            'HTTP request duration',
            ['method', 'endpoint']
        )

        self.ai_operations_total = self._create_counter(
            'ai_operations_total',
            'Total AI operations',
            ['operation_type', 'model', 'provider']
        )

        self.ai_operation_duration = self._create_histogram(
            'ai_operation_duration_seconds',
            'AI operation duration',
            ['operation_type', 'model']
        )

        self.database_queries_total = self._create_counter(
            'database_queries_total',
            'Total database queries',
            ['operation']
        )

        self.database_query_duration = self._create_histogram(
            'database_query_duration_seconds',
            'Database query duration',
            ['operation']
        )

        # System metrics
        self.cpu_usage = self._create_gauge('cpu_usage_percent', 'CPU usage percentage')
        self.memory_usage = self._create_gauge('memory_usage_bytes', 'Memory usage in bytes')
        self.disk_usage = self._create_gauge('disk_usage_bytes', 'Disk usage in bytes')

        # Business metrics
        self.active_users = self._create_gauge('active_users', 'Number of active users')
        self.api_calls_per_minute = self._create_gauge('api_calls_per_minute', 'API calls per minute')

        # Error metrics
        self.errors_total = self._create_counter(
            'errors_total',
            'Total errors',
            ['error_type', 'endpoint']
        )

    def _create_counter(self, name, description, labels=None):
        if not self.registry:
            return None
        return Counter(name, description, labels or [], registry=self.registry)

    def _create_histogram(self, name, description, labels=None):
        if not self.registry:
            return None
        return Histogram(name, description, labels or [], registry=self.registry)

    def _create_gauge(self, name, description, labels=None):
        if not self.registry:
            return None
        return Gauge(name, description, labels or [], registry=self.registry)

    def record_http_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record HTTP request metrics"""
        if self.http_requests_total:
            self.http_requests_total.labels(method, endpoint, str(status_code)).inc()
        if self.http_request_duration:
            self.http_request_duration.labels(method, endpoint).observe(duration)

    def record_ai_operation(self, operation_type: str, model: str, provider: str, duration: float):
        """Record AI operation metrics"""
        if self.ai_operations_total:
            self.ai_operations_total.labels(operation_type, model, provider).inc()
        if self.ai_operation_duration:
            self.ai_operation_duration.labels(operation_type, model).observe(duration)

    def record_database_query(self, operation: str, duration: float):
        """Record database query metrics"""
        if self.database_queries_total:
            self.database_queries_total.labels(operation).inc()
        if self.database_query_duration:
            self.database_query_duration.labels(operation).observe(duration)

    def record_error(self, error_type: str, endpoint: str = ""):
        """Record error metrics"""
        if self.errors_total:
            self.errors_total.labels(error_type, endpoint).inc()

    def update_system_metrics(self):
        """Update system resource metrics"""
        if not self.cpu_usage:
            return

        # CPU usage
        self.cpu_usage.set(psutil.cpu_percent(interval=1))

        # Memory usage
        memory = psutil.virtual_memory()
        self.memory_usage.set(memory.used)

        # Disk usage
        disk = psutil.disk_usage('/')
        self.disk_usage.set(disk.used)

    def get_metrics(self) -> str:
        """Get metrics in Prometheus format"""
        if self.registry:
            return generate_latest(self.registry).decode('utf-8')
        return ""


class AlertManager:
    """Alert management and notification system"""

    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.alerts = {}
        self.alert_history = deque(maxlen=1000)

    async def send_alert(self, alert_type: str, message: str, severity: str = "warning",
                        metadata: Dict[str, Any] = None):
        """Send an alert"""
        if not self.config.alerting_enabled:
            return

        alert = {
            'id': f"{alert_type}_{int(time.time())}",
            'type': alert_type,
            'message': message,
            'severity': severity,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }

        self.alerts[alert['id']] = alert
        self.alert_history.append(alert)

        # Send to configured webhook
        if self.config.alert_webhook_url:
            await self._send_webhook_alert(alert)

        # Send to external monitoring
        if DATADOG_AVAILABLE and self.config.datadog_api_key:
            self._send_datadog_alert(alert)

        # Log alert
        logger = logging.getLogger(__name__)
        log_method = logger.warning if severity == "warning" else logger.error
        log_method(f"ALERT [{severity.upper()}]: {message}", extra=alert)

    async def _send_webhook_alert(self, alert: Dict[str, Any]):
        """Send alert to webhook"""
        try:
            import aiohttp

            async with aiohttp.ClientSession() as session:
                await session.post(
                    self.config.alert_webhook_url,
                    json=alert,
                    headers={'Content-Type': 'application/json'}
                )
        except Exception as e:
            logging.error(f"Failed to send webhook alert: {e}")

    def _send_datadog_alert(self, alert: Dict[str, Any]):
        """Send alert to DataDog"""
        try:
            # DataDog alerting would go here
            pass
        except Exception as e:
            logging.error(f"Failed to send DataDog alert: {e}")

    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get active alerts"""
        return list(self.alerts.values())

    def resolve_alert(self, alert_id: str):
        """Resolve an alert"""
        if alert_id in self.alerts:
            alert = self.alerts[alert_id]
            alert['resolved_at'] = datetime.now().isoformat()
            alert['status'] = 'resolved'
            del self.alerts[alert_id]


class HealthChecker:
    """Comprehensive health checking system"""

    def __init__(self):
        self.checks = {}
        self.last_check_results = {}

    def register_check(self, name: str, check_func: Callable):
        """Register a health check"""
        self.checks[name] = check_func

    async def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks"""
        results = {}
        overall_healthy = True

        for name, check_func in self.checks.items():
            try:
                start_time = time.time()
                result = await check_func()
                duration = time.time() - start_time

                check_result = {
                    'healthy': result.get('healthy', True),
                    'message': result.get('message', 'OK'),
                    'duration_seconds': round(duration, 3),
                    'timestamp': datetime.now().isoformat(),
                    'details': result.get('details', {})
                }

                results[name] = check_result
                self.last_check_results[name] = check_result

                if not check_result['healthy']:
                    overall_healthy = False

            except Exception as e:
                results[name] = {
                    'healthy': False,
                    'message': f"Check failed: {str(e)}",
                    'duration_seconds': 0,
                    'timestamp': datetime.now().isoformat(),
                    'details': {}
                }
                overall_healthy = False

        return {
            'overall_healthy': overall_healthy,
            'checks': results,
            'timestamp': datetime.now().isoformat()
        }

    async def database_check(self) -> Dict[str, Any]:
        """Check database connectivity"""
        try:
            from ..core.database import get_db

            async for db in get_db():
                # Simple query to test connection
                result = await db.execute("SELECT 1")
                data = result.fetchone()
                await db.close()

                return {
                    'healthy': data is not None,
                    'message': 'Database connection OK',
                    'details': {'response': data[0] if data else None}
                }
        except Exception as e:
            return {
                'healthy': False,
                'message': f'Database connection failed: {str(e)}',
                'details': {}
            }

    async def redis_check(self) -> Dict[str, Any]:
        """Check Redis connectivity"""
        try:
            import redis.asyncio as redis

            redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
            await redis_client.ping()
            await redis_client.close()

            return {
                'healthy': True,
                'message': 'Redis connection OK',
                'details': {}
            }
        except Exception as e:
            return {
                'healthy': False,
                'message': f'Redis connection failed: {str(e)}',
                'details': {}
            }

    async def ai_services_check(self) -> Dict[str, Any]:
        """Check AI services availability"""
        try:
            from ..services.ai import get_ai_router

            ai_router = get_ai_router()
            # Basic health check
            healthy = ai_router is not None

            return {
                'healthy': healthy,
                'message': 'AI services OK' if healthy else 'AI services unavailable',
                'details': {'router_available': healthy}
            }
        except Exception as e:
            return {
                'healthy': False,
                'message': f'AI services check failed: {str(e)}',
                'details': {}
            }


class MonitoringSystem:
    """Main monitoring system orchestrator"""

    def __init__(self, config: MonitoringConfig = None):
        self.config = config or MonitoringConfig()
        self.metrics = MetricsCollector()
        self.alerts = AlertManager(self.config)
        self.health = HealthChecker()
        self.logger = self._setup_logging()

        # Register default health checks
        self.health.register_check('database', self.health.database_check)
        self.health.register_check('redis', self.health.redis_check)
        self.health.register_check('ai_services', self.health.ai_services_check)

        # Setup external monitoring
        self._setup_external_monitoring()

        # Start background monitoring
        self._start_background_tasks()

    def _setup_logging(self) -> logging.Logger:
        """Setup comprehensive logging"""
        logger = logging.getLogger('galion_monitoring')
        logger.setLevel(self.config.log_level)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Console handler
        if self.config.log_to_console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        # File handler with rotation
        if self.config.log_to_file:
            from logging.handlers import RotatingFileHandler

            log_dir = Path(self.config.log_directory)
            log_dir.mkdir(exist_ok=True)

            file_handler = RotatingFileHandler(
                log_dir / 'galion.log',
                maxBytes=self.config.max_log_size_mb * 1024 * 1024,
                backupCount=self.config.max_log_files
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        return logger

    def _setup_external_monitoring(self):
        """Setup external monitoring services"""
        # Sentry
        if SENTRY_AVAILABLE and self.config.sentry_dsn:
            sentry_sdk.init(
                dsn=self.config.sentry_dsn,
                integrations=[
                    FastAPIIntegration(),
                    SqlalchemyIntegration(),
                ],
                traces_sample_rate=1.0,
                environment=os.getenv("ENVIRONMENT", "development")
            )

        # DataDog
        if DATADOG_AVAILABLE and self.config.datadog_api_key:
            datadog.initialize(
                api_key=self.config.datadog_api_key,
                app_key=self.config.datadog_app_key,
                env=os.getenv("ENVIRONMENT", "development")
            )

    def _start_background_tasks(self):
        """Start background monitoring tasks"""
        def system_metrics_updater():
            """Update system metrics periodically"""
            while True:
                try:
                    self.metrics.update_system_metrics()
                    time.sleep(60)  # Update every minute
                except Exception as e:
                    self.logger.error(f"Failed to update system metrics: {e}")
                    time.sleep(60)

        def health_checker():
            """Run health checks periodically"""
            while True:
                try:
                    asyncio.run(self.run_health_checks())
                    time.sleep(300)  # Check every 5 minutes
                except Exception as e:
                    self.logger.error(f"Failed to run health checks: {e}")
                    time.sleep(300)

        # Start threads
        threading.Thread(target=system_metrics_updater, daemon=True).start()
        threading.Thread(target=health_checker, daemon=True).start()

    async def run_health_checks(self):
        """Run all health checks and handle alerts"""
        results = await self.health.run_all_checks()

        if not results['overall_healthy']:
            unhealthy_checks = [
                name for name, check in results['checks'].items()
                if not check['healthy']
            ]

            await self.alerts.send_alert(
                'health_check_failed',
                f"Unhealthy services: {', '.join(unhealthy_checks)}",
                severity='error',
                metadata=results
            )

        return results

    def create_log_context(self, **context) -> LogContext:
        """Create a structured logging context"""
        return LogContext(self.logger, **context)

    def record_http_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record HTTP request metrics"""
        self.metrics.record_http_request(method, endpoint, status_code, duration)

        # Alert on high error rates
        if status_code >= 500:
            asyncio.create_task(self.alerts.send_alert(
                'http_5xx_error',
                f"HTTP 5xx error: {method} {endpoint}",
                severity='error',
                metadata={'method': method, 'endpoint': endpoint, 'status_code': status_code}
            ))

    def record_ai_operation(self, operation_type: str, model: str, provider: str, duration: float):
        """Record AI operation metrics"""
        self.metrics.record_ai_operation(operation_type, model, provider, duration)

        # Alert on slow AI operations
        if duration > 30:  # 30 seconds
            asyncio.create_task(self.alerts.send_alert(
                'slow_ai_operation',
                f"Slow AI operation: {operation_type} on {model} ({duration:.1f}s)",
                severity='warning',
                metadata={'operation_type': operation_type, 'model': model, 'duration': duration}
            ))

    def record_error(self, error_type: str, endpoint: str = "", metadata: Dict[str, Any] = None):
        """Record error metrics"""
        self.metrics.record_error(error_type, endpoint)

        # Alert on critical errors
        if error_type in ['database_error', 'ai_service_error', 'authentication_error']:
            asyncio.create_task(self.alerts.send_alert(
                f'{error_type}',
                f"Critical error: {error_type}",
                severity='error',
                metadata=metadata or {}
            ))

    def get_monitoring_report(self) -> Dict[str, Any]:
        """Get comprehensive monitoring report"""
        return {
            'health': self.health.last_check_results,
            'active_alerts': self.alerts.get_active_alerts(),
            'metrics': {
                'prometheus': self.metrics.get_metrics(),
                'summary': {
                    'total_alerts': len(self.alerts.alert_history),
                    'active_alerts': len(self.alerts.alerts),
                    'health_checks': len(self.health.checks)
                }
            },
            'system_info': {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'uptime': time.time() - psutil.boot_time()
            },
            'timestamp': datetime.now().isoformat()
        }


# Global monitoring instance
_monitoring_system: Optional[MonitoringSystem] = None

def get_monitoring_system() -> MonitoringSystem:
    """Get global monitoring system instance"""
    global _monitoring_system
    if _monitoring_system is None:
        _monitoring_system = MonitoringSystem()
    return _monitoring_system


# FastAPI middleware for monitoring
async def monitoring_middleware(request, call_next):
    """FastAPI middleware for request monitoring"""
    monitoring = get_monitoring_system()

    start_time = time.time()
    method = request.method
    endpoint = str(request.url.path)

    # Create log context
    with monitoring.create_log_context(
        operation=f"http_{method.lower()}",
        endpoint=endpoint,
        user_id=getattr(request.state, 'user_id', None),
        ip_address=getattr(request.client, 'host', None) if request.client else None
    ):
        try:
            response = await call_next(request)
            duration = time.time() - start_time

            # Record metrics
            monitoring.record_http_request(method, endpoint, response.status_code, duration)

            # Add monitoring headers
            response.headers['X-Response-Time'] = f"{duration:.3f}s"
            response.headers['X-Request-ID'] = getattr(request.state, 'request_id', 'unknown')

            return response

        except Exception as e:
            duration = time.time() - start_time
            monitoring.record_error('http_error', endpoint, {
                'method': method,
                'duration': duration,
                'error': str(e)
            })
            raise


# Convenience functions
def log_operation(operation: str, **context):
    """Decorator for logging operations"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            monitoring = get_monitoring_system()
            with monitoring.create_log_context(operation=operation, **context):
                return await func(*args, **kwargs)
        return wrapper
    return decorator


def alert_on_error(alert_type: str, severity: str = "error"):
    """Decorator to send alerts on errors"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                monitoring = get_monitoring_system()
                await monitoring.alerts.send_alert(
                    alert_type,
                    f"Error in {func.__name__}: {str(e)}",
                    severity=severity,
                    metadata={'function': func.__name__, 'error': str(e)}
                )
                raise
        return wrapper
    return decorator
