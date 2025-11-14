"""
Error tracking and alerting system for Deep Search.
Captures, analyzes, and alerts on system errors and issues.
"""

import logging
import traceback
import asyncio
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import json
import hashlib
import threading
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)


class ErrorEvent:
    """Represents a single error event."""

    def __init__(self, error_type: str, message: str, traceback_str: Optional[str] = None,
                 context: Optional[Dict[str, Any]] = None, severity: str = "error"):
        self.error_type = error_type
        self.message = message
        self.traceback = traceback_str
        self.context = context or {}
        self.severity = severity
        self.timestamp = datetime.utcnow()
        self.id = self._generate_id()

    def _generate_id(self) -> str:
        """Generate unique error ID."""
        content = f"{self.error_type}:{self.message}:{self.timestamp.isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:8]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'id': self.id,
            'error_type': self.error_type,
            'message': self.message,
            'traceback': self.traceback,
            'context': self.context,
            'severity': self.severity,
            'timestamp': self.timestamp.isoformat(),
            'fingerprint': self._generate_fingerprint()
        }

    def _generate_fingerprint(self) -> str:
        """Generate error fingerprint for grouping similar errors."""
        key_content = f"{self.error_type}:{self.message}"
        if self.traceback:
            # Use first few lines of traceback for fingerprinting
            traceback_lines = self.traceback.split('\n')[:3]
            key_content += ''.join(traceback_lines)
        return hashlib.md5(key_content.encode()).hexdigest()[:12]


class AlertRule:
    """Represents an alerting rule."""

    def __init__(self, name: str, condition: Callable, threshold: Any,
                 severity: str = "warning", cooldown_minutes: int = 60):
        self.name = name
        self.condition = condition
        self.threshold = threshold
        self.severity = severity
        self.cooldown_minutes = cooldown_minutes
        self.last_triggered = None

    def should_trigger(self, data: Dict[str, Any]) -> bool:
        """Check if alert should be triggered."""
        # Check cooldown
        if self.last_triggered:
            time_since_last = (datetime.utcnow() - self.last_triggered).total_seconds() / 60
            if time_since_last < self.cooldown_minutes:
                return False

        # Check condition
        return self.condition(data, self.threshold)

    def trigger(self):
        """Mark alert as triggered."""
        self.last_triggered = datetime.utcnow()


class ErrorTracker:
    """
    Comprehensive error tracking and alerting system.

    Features:
    - Error capture and classification
    - Error fingerprinting and grouping
    - Real-time alerting with configurable rules
    - Error trend analysis
    - Integration with monitoring systems
    - Multiple notification channels
    """

    def __init__(self):
        self.errors = []
        self.error_groups = defaultdict(list)
        self.alert_rules = []
        self.notifications_sent = []
        self.max_errors_stored = 10000
        self.max_group_size = 100

        # Default alert rules
        self._setup_default_alert_rules()

        # Notification channels
        self.notification_channels = {
            'email': self._send_email_notification,
            'log': self._send_log_notification,
            'webhook': self._send_webhook_notification
        }

        # Notification settings
        self.notification_config = {
            'email': {
                'enabled': False,
                'smtp_server': 'localhost',
                'smtp_port': 587,
                'sender_email': 'alerts@deepsearch.com',
                'recipient_emails': []
            },
            'webhook': {
                'enabled': False,
                'url': '',
                'headers': {}
            }
        }

    def _setup_default_alert_rules(self):
        """Setup default alerting rules."""
        # High error rate alert
        self.add_alert_rule(
            "high_error_rate",
            lambda data, threshold: data.get('error_rate', 0) > threshold,
            5.0,  # 5% error rate
            "error",
            30  # 30 minute cooldown
        )

        # Critical errors alert
        self.add_alert_rule(
            "critical_errors",
            lambda data, threshold: data.get('critical_errors_last_hour', 0) >= threshold,
            3,  # 3+ critical errors per hour
            "critical",
            15  # 15 minute cooldown
        )

        # Repeated errors alert
        self.add_alert_rule(
            "repeated_errors",
            lambda data, threshold: data.get('repeated_error_groups', 0) >= threshold,
            5,  # 5+ error groups with multiple occurrences
            "warning",
            60  # 1 hour cooldown
        )

        # Performance degradation alert
        self.add_alert_rule(
            "performance_degradation",
            lambda data, threshold: data.get('avg_response_time', 0) > threshold,
            10.0,  # 10+ seconds average response time
            "warning",
            45  # 45 minute cooldown
        )

    def capture_error(self, error_type: str, message: str,
                     traceback_str: Optional[str] = None,
                     context: Optional[Dict[str, Any]] = None,
                     severity: str = "error") -> str:
        """
        Capture and store an error event.

        Args:
            error_type: Type of error (e.g., 'database', 'api', 'external_service')
            message: Error message
            traceback_str: Full traceback string
            context: Additional context information
            severity: Error severity (debug, info, warning, error, critical)

        Returns:
            Error event ID
        """
        error_event = ErrorEvent(error_type, message, traceback_str, context, severity)

        # Add to main error list
        self.errors.append(error_event)

        # Group similar errors
        fingerprint = error_event._generate_fingerprint()
        if len(self.error_groups[fingerprint]) < self.max_group_size:
            self.error_groups[fingerprint].append(error_event)

        # Maintain size limits
        if len(self.errors) > self.max_errors_stored:
            self.errors = self.errors[-self.max_errors_stored:]

        # Check alert rules
        self._check_alerts()

        logger.error(f"Captured error: {error_type} - {message}")

        return error_event.id

    def capture_exception(self, exc: Exception, context: Optional[Dict[str, Any]] = None,
                         severity: str = "error") -> str:
        """
        Capture an exception with full traceback.

        Args:
            exc: The exception object
            context: Additional context information
            severity: Error severity

        Returns:
            Error event ID
        """
        error_type = type(exc).__name__
        message = str(exc)
        traceback_str = ''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))

        return self.capture_error(error_type, message, traceback_str, context, severity)

    def add_alert_rule(self, name: str, condition: Callable, threshold: Any,
                      severity: str = "warning", cooldown_minutes: int = 60):
        """
        Add a custom alert rule.

        Args:
            name: Rule name
            condition: Function that takes (data, threshold) and returns bool
            threshold: Threshold value for the condition
            severity: Alert severity
            cooldown_minutes: Minutes to wait before re-triggering
        """
        rule = AlertRule(name, condition, threshold, severity, cooldown_minutes)
        self.alert_rules.append(rule)
        logger.info(f"Added alert rule: {name}")

    def _check_alerts(self):
        """Check all alert rules against current error data."""
        current_data = self.get_error_summary()

        for rule in self.alert_rules:
            if rule.should_trigger(current_data):
                self._trigger_alert(rule, current_data)
                rule.trigger()

    def _trigger_alert(self, rule: AlertRule, data: Dict[str, Any]):
        """Trigger an alert for a rule."""
        alert_data = {
            'rule_name': rule.name,
            'severity': rule.severity,
            'threshold': rule.threshold,
            'current_value': self._get_current_value_for_rule(rule, data),
            'timestamp': datetime.utcnow().isoformat(),
            'error_summary': data
        }

        # Send notifications
        self._send_notifications(alert_data)

        # Log alert
        logger.warning(f"Alert triggered: {rule.name} (severity: {rule.severity})")

        # Store alert
        self.notifications_sent.append(alert_data)

        # Keep only recent alerts
        if len(self.notifications_sent) > 1000:
            self.notifications_sent = self.notifications_sent[-1000:]

    def _get_current_value_for_rule(self, rule: AlertRule, data: Dict[str, Any]) -> Any:
        """Get the current value that triggered the rule."""
        if rule.name == "high_error_rate":
            return data.get('error_rate', 0)
        elif rule.name == "critical_errors":
            return data.get('critical_errors_last_hour', 0)
        elif rule.name == "repeated_errors":
            return data.get('repeated_error_groups', 0)
        elif rule.name == "performance_degradation":
            return data.get('avg_response_time', 0)
        else:
            return None

    def get_error_summary(self, hours: int = 1) -> Dict[str, Any]:
        """
        Get error summary for the specified time period.

        Args:
            hours: Number of hours to look back

        Returns:
            Error summary statistics
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_errors = [e for e in self.errors if e.timestamp > cutoff_time]

        # Basic statistics
        total_errors = len(recent_errors)
        error_types = Counter(e.error_type for e in recent_errors)
        severities = Counter(e.severity for e in recent_errors)

        # Error rate (assuming we know total requests - this would come from monitoring)
        # For now, use a mock total requests value
        mock_total_requests = max(total_errors * 20, 1000)  # Assume at least 1000 requests
        error_rate = (total_errors / mock_total_requests) * 100

        # Critical errors
        critical_errors = sum(1 for e in recent_errors if e.severity == "critical")

        # Repeated error groups
        repeated_groups = sum(1 for group in self.error_groups.values() if len(group) > 1)

        # Most common errors
        common_errors = error_types.most_common(5)

        return {
            'total_errors': total_errors,
            'error_rate': error_rate,
            'critical_errors_last_hour': critical_errors,
            'repeated_error_groups': repeated_groups,
            'error_types': dict(error_types),
            'severities': dict(severities),
            'most_common_errors': common_errors,
            'time_period_hours': hours
        }

    def get_error_groups(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get error groups with occurrence counts.

        Returns:
            List of error groups sorted by frequency
        """
        groups_data = []

        for fingerprint, errors in self.error_groups.items():
            if errors:
                latest_error = max(errors, key=lambda e: e.timestamp)
                groups_data.append({
                    'fingerprint': fingerprint,
                    'count': len(errors),
                    'latest_occurrence': latest_error.timestamp.isoformat(),
                    'error_type': latest_error.error_type,
                    'message': latest_error.message,
                    'severity': latest_error.severity,
                    'first_occurrence': min(e.timestamp for e in errors).isoformat()
                })

        # Sort by count (most frequent first)
        groups_data.sort(key=lambda x: x['count'], reverse=True)

        return groups_data[:limit]

    def get_error_details(self, error_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific error.

        Args:
            error_id: Error event ID

        Returns:
            Error details or None if not found
        """
        for error in self.errors:
            if error.id == error_id:
                return error.to_dict()
        return None

    def get_error_trends(self, days: int = 7) -> Dict[str, Any]:
        """
        Get error trends over time.

        Args:
            days: Number of days to analyze

        Returns:
            Error trend data
        """
        cutoff_time = datetime.utcnow() - timedelta(days=days)

        # Group errors by day
        daily_errors = defaultdict(lambda: defaultdict(int))

        for error in self.errors:
            if error.timestamp > cutoff_time:
                day = error.timestamp.date().isoformat()
                daily_errors[day][error.error_type] += 1
                daily_errors[day]['total'] += 1

        # Convert to time series
        trend_data = []
        current_date = cutoff_time.date()

        while current_date <= datetime.utcnow().date():
            date_str = current_date.isoformat()
            day_data = daily_errors.get(date_str, {})

            trend_data.append({
                'date': date_str,
                'total_errors': day_data.get('total', 0),
                'by_type': {k: v for k, v in day_data.items() if k != 'total'}
            })

            current_date += timedelta(days=1)

        return {
            'period_days': days,
            'trend_data': trend_data,
            'summary': {
                'total_errors': sum(d['total_errors'] for d in trend_data),
                'average_daily_errors': sum(d['total_errors'] for d in trend_data) / len(trend_data),
                'peak_day': max(trend_data, key=lambda x: x['total_errors'])['date'] if trend_data else None
            }
        }

    def configure_notifications(self, channel: str, config: Dict[str, Any]):
        """
        Configure notification settings.

        Args:
            channel: Notification channel (email, webhook, etc.)
            config: Configuration settings
        """
        if channel in self.notification_config:
            self.notification_config[channel].update(config)
            logger.info(f"Updated notification config for {channel}")
        else:
            logger.warning(f"Unknown notification channel: {channel}")

    def _send_notifications(self, alert_data: Dict[str, Any]):
        """Send notifications through configured channels."""
        for channel_name, config in self.notification_config.items():
            if config.get('enabled', False):
                try:
                    send_func = self.notification_channels.get(channel_name)
                    if send_func:
                        asyncio.create_task(send_func(alert_data, config))
                except Exception as e:
                    logger.error(f"Failed to send {channel_name} notification: {e}")

    async def _send_email_notification(self, alert_data: Dict[str, Any], config: Dict[str, Any]):
        """Send email notification."""
        try:
            if not config.get('recipient_emails'):
                return

            msg = MIMEMultipart()
            msg['From'] = config['sender_email']
            msg['To'] = ', '.join(config['recipient_emails'])
            msg['Subject'] = f"Deep Search Alert: {alert_data['rule_name']}"

            body = f"""
Deep Search System Alert

Rule: {alert_data['rule_name']}
Severity: {alert_data['severity']}
Threshold: {alert_data['threshold']}
Current Value: {alert_data['current_value']}

Error Summary:
- Total Errors: {alert_data['error_summary'].get('total_errors', 0)}
- Error Rate: {alert_data['error_summary'].get('error_rate', 0):.2f}%

Time: {alert_data['timestamp']}

Please check the system monitoring dashboard for more details.
            """

            msg.attach(MIMEText(body, 'plain'))

            # Note: In production, you would actually send the email
            # For demo purposes, we just log it
            logger.info(f"Email alert would be sent: {msg['Subject']}")

        except Exception as e:
            logger.error(f"Email notification failed: {e}")

    async def _send_log_notification(self, alert_data: Dict[str, Any], config: Dict[str, Any]):
        """Send log notification."""
        logger.warning(f"ALERT: {alert_data['rule_name']} - {alert_data['severity']} - Current: {alert_data['current_value']} (Threshold: {alert_data['threshold']})")

    async def _send_webhook_notification(self, alert_data: Dict[str, Any], config: Dict[str, Any]):
        """Send webhook notification."""
        try:
            import aiohttp

            async with aiohttp.ClientSession() as session:
                headers = config.get('headers', {})
                headers['Content-Type'] = 'application/json'

                async with session.post(config['url'], json=alert_data, headers=headers) as response:
                    if response.status == 200:
                        logger.info("Webhook notification sent successfully")
                    else:
                        logger.error(f"Webhook notification failed: {response.status}")

        except ImportError:
            logger.warning("aiohttp not available for webhook notifications")
        except Exception as e:
            logger.error(f"Webhook notification failed: {e}")

    def export_errors(self, format: str = "json", days: int = 7) -> str:
        """
        Export error data for analysis.

        Args:
            format: Export format (json, csv)
            days: Number of days of data to export

        Returns:
            Exported data as string
        """
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        recent_errors = [e for e in self.errors if e.timestamp > cutoff_time]

        if format == "json":
            error_data = [e.to_dict() for e in recent_errors]
            return json.dumps(error_data, indent=2, default=str)
        elif format == "csv":
            if not recent_errors:
                return "id,timestamp,error_type,message,severity,traceback"

            lines = ["id,timestamp,error_type,message,severity,traceback"]
            for error in recent_errors:
                # Escape commas and quotes in CSV
                message = error.message.replace('"', '""')
                traceback_short = (error.traceback or "")[:100].replace('"', '""')
                lines.append(f'"{error.id}","{error.timestamp.isoformat()}","{error.error_type}","{message}","{error.severity}","{traceback_short}"')

            return "\n".join(lines)
        else:
            return json.dumps({"error": "Unsupported format"}, default=str)

    def clear_errors(self, days_to_keep: int = 30):
        """
        Clear old error data.

        Args:
            days_to_keep: Number of days of error data to keep
        """
        cutoff_time = datetime.utcnow() - timedelta(days=days_to_keep)

        # Filter errors
        self.errors = [e for e in self.errors if e.timestamp > cutoff_time]

        # Clean up error groups
        fingerprints_to_remove = []
        for fingerprint, errors in self.error_groups.items():
            filtered_errors = [e for e in errors if e.timestamp > cutoff_time]
            if filtered_errors:
                self.error_groups[fingerprint] = filtered_errors
            else:
                fingerprints_to_remove.append(fingerprint)

        for fingerprint in fingerprints_to_remove:
            del self.error_groups[fingerprint]

        logger.info(f"Cleaned up errors older than {days_to_keep} days")

    def get_health_status(self) -> Dict[str, Any]:
        """
        Get error tracking system health status.

        Returns:
            Health status information
        """
        recent_errors = self.get_error_summary(hours=1)

        health_status = {
            'system': 'error_tracker',
            'status': 'healthy',
            'metrics': {
                'total_errors': len(self.errors),
                'error_groups': len(self.error_groups),
                'alert_rules': len(self.alert_rules),
                'recent_errors': recent_errors['total_errors'],
                'error_rate': recent_errors['error_rate']
            },
            'last_updated': datetime.utcnow().isoformat()
        }

        # Determine health status
        if recent_errors['error_rate'] > 10:
            health_status['status'] = 'critical'
        elif recent_errors['error_rate'] > 5:
            health_status['status'] = 'warning'
        elif recent_errors['critical_errors_last_hour'] > 0:
            health_status['status'] = 'warning'

        return health_status


# Global error tracker instance
_error_tracker = None


def get_error_tracker() -> ErrorTracker:
    """Get the global error tracker instance."""
    global _error_tracker
    if _error_tracker is None:
        _error_tracker = ErrorTracker()
    return _error_tracker


# Convenience functions for error capture
def capture_error(error_type: str, message: str, **kwargs):
    """Convenience function to capture an error."""
    tracker = get_error_tracker()
    return tracker.capture_error(error_type, message, **kwargs)


def capture_exception(exc: Exception, **kwargs):
    """Convenience function to capture an exception."""
    tracker = get_error_tracker()
    return tracker.capture_exception(exc, **kwargs)
