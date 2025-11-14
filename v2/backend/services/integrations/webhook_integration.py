"""
Webhook Integration

Provides generic webhook functionality for custom integrations,
notifications, and external service callbacks.
"""

import hmac
import hashlib
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from .base_integration import BaseIntegration, IntegrationResult


class WebhookIntegration(BaseIntegration):
    """Generic webhook integration for custom notifications and callbacks."""

    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.webhook_url = config.get('webhook_url', '')
        self.secret = config.get('secret', '')  # for webhook signature verification
        self.headers = config.get('headers', {})

    def get_required_config_fields(self) -> List[str]:
        return ['webhook_url']

    async def test_connection(self) -> IntegrationResult:
        """Test webhook endpoint by sending a test payload."""
        test_payload = {
            'test': True,
            'timestamp': datetime.now().isoformat(),
            'integration': self.name
        }

        return await self._send_webhook(test_payload, 'test')

    async def get_capabilities(self) -> List[str]:
        return [
            'send_notification',
            'send_alert',
            'send_status_update',
            'send_task_update',
            'send_agent_status',
            'send_system_metrics',
            'send_custom_payload',
            'verify_signature',
            'retry_failed_webhooks',
            'batch_notifications'
        ]

    async def execute_operation(self, operation: str, **kwargs) -> IntegrationResult:
        """Execute a webhook operation."""

        operations = {
            'send_notification': self._send_notification,
            'send_alert': self._send_alert,
            'send_status_update': self._send_status_update,
            'send_task_update': self._send_task_update,
            'send_agent_status': self._send_agent_status,
            'send_system_metrics': self._send_system_metrics,
            'send_custom_payload': self._send_custom_payload,
            'verify_signature': self._verify_signature,
            'retry_failed_webhooks': self._retry_failed_webhooks,
            'batch_notifications': self._batch_notifications
        }

        if operation not in operations:
            return IntegrationResult(
                success=False,
                error=f"Unknown operation: {operation}"
            )

        try:
            return await operations[operation](**kwargs)
        except Exception as e:
            return IntegrationResult(
                success=False,
                error=f"Operation failed: {str(e)}"
            )

    async def _send_webhook(self, payload: Dict[str, Any], event_type: str = 'notification') -> IntegrationResult:
        """Send a webhook with proper headers and signature."""
        if not self.webhook_url:
            return IntegrationResult(
                success=False,
                error="Webhook URL not configured"
            )

        # Prepare headers
        headers = dict(self.headers)
        headers.update({
            'Content-Type': 'application/json',
            'User-Agent': f'Galion-Agent-Webhook/{self.name}',
            'X-Webhook-Event': event_type,
            'X-Webhook-Source': 'galion-agent-system'
        })

        # Add signature if secret is configured
        if self.secret:
            payload_str = json.dumps(payload, separators=(',', ':'), sort_keys=True)
            signature = hmac.new(
                self.secret.encode('utf-8'),
                payload_str.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()

            headers['X-Webhook-Signature'] = f'sha256={signature}'

        # Add timestamp
        payload['timestamp'] = datetime.now().isoformat()
        payload['event_type'] = event_type
        payload['integration'] = self.name

        return await self._make_request('POST', self.webhook_url, json=payload, headers=headers)

    async def _send_notification(self, **kwargs) -> IntegrationResult:
        """Send a general notification."""
        title = kwargs.get('title', 'Notification')
        message = kwargs.get('message', '')
        priority = kwargs.get('priority', 'normal')
        category = kwargs.get('category', 'general')

        payload = {
            'notification': {
                'title': title,
                'message': message,
                'priority': priority,
                'category': category,
                'metadata': kwargs.get('metadata', {})
            }
        }

        return await self._send_webhook(payload, 'notification')

    async def _send_alert(self, **kwargs) -> IntegrationResult:
        """Send an alert notification."""
        severity = kwargs.get('severity', 'info')  # info, warning, error, critical
        title = kwargs.get('title', 'Alert')
        description = kwargs.get('description', '')
        source = kwargs.get('source', 'galion-system')

        payload = {
            'alert': {
                'severity': severity,
                'title': title,
                'description': description,
                'source': source,
                'triggered_at': datetime.now().isoformat(),
                'metadata': kwargs.get('metadata', {})
            }
        }

        return await self._send_webhook(payload, 'alert')

    async def _send_status_update(self, **kwargs) -> IntegrationResult:
        """Send a status update."""
        component = kwargs.get('component', 'system')
        status = kwargs.get('status', 'unknown')  # healthy, degraded, down
        message = kwargs.get('message', '')
        metrics = kwargs.get('metrics', {})

        payload = {
            'status_update': {
                'component': component,
                'status': status,
                'message': message,
                'metrics': metrics,
                'updated_at': datetime.now().isoformat()
            }
        }

        return await self._send_webhook(payload, 'status_update')

    async def _send_task_update(self, **kwargs) -> IntegrationResult:
        """Send a task update."""
        task_id = kwargs.get('task_id')
        task_title = kwargs.get('task_title', '')
        status = kwargs.get('status', 'unknown')
        progress = kwargs.get('progress', 0)
        assigned_agent = kwargs.get('assigned_agent', '')

        if not task_id:
            return IntegrationResult(
                success=False,
                error="task_id is required"
            )

        payload = {
            'task_update': {
                'task_id': task_id,
                'task_title': task_title,
                'status': status,
                'progress': progress,
                'assigned_agent': assigned_agent,
                'updated_at': datetime.now().isoformat(),
                'metadata': kwargs.get('metadata', {})
            }
        }

        return await self._send_webhook(payload, 'task_update')

    async def _send_agent_status(self, **kwargs) -> IntegrationResult:
        """Send agent status update."""
        agent_name = kwargs.get('agent_name')
        agent_type = kwargs.get('agent_type', '')
        status = kwargs.get('status', 'unknown')
        current_task = kwargs.get('current_task')
        success_rate = kwargs.get('success_rate', 0.0)

        if not agent_name:
            return IntegrationResult(
                success=False,
                error="agent_name is required"
            )

        payload = {
            'agent_status': {
                'agent_name': agent_name,
                'agent_type': agent_type,
                'status': status,
                'current_task': current_task,
                'success_rate': success_rate,
                'last_updated': datetime.now().isoformat(),
                'metrics': kwargs.get('metrics', {})
            }
        }

        return await self._send_webhook(payload, 'agent_status')

    async def _send_system_metrics(self, **kwargs) -> IntegrationResult:
        """Send system metrics."""
        metrics = kwargs.get('metrics', {})
        time_range = kwargs.get('time_range', '1h')
        system_health = kwargs.get('system_health', 'unknown')

        payload = {
            'system_metrics': {
                'metrics': metrics,
                'time_range': time_range,
                'system_health': system_health,
                'collected_at': datetime.now().isoformat(),
                'metadata': kwargs.get('metadata', {})
            }
        }

        return await self._send_webhook(payload, 'system_metrics')

    async def _send_custom_payload(self, **kwargs) -> IntegrationResult:
        """Send a custom payload."""
        custom_payload = kwargs.get('payload', {})
        event_type = kwargs.get('event_type', 'custom')

        if not custom_payload:
            return IntegrationResult(
                success=False,
                error="payload is required"
            )

        payload = {
            'custom': custom_payload
        }

        return await self._send_webhook(payload, event_type)

    async def _verify_signature(self, **kwargs) -> IntegrationResult:
        """Verify webhook signature (for incoming webhooks)."""
        payload = kwargs.get('payload', '')
        signature = kwargs.get('signature', '')
        expected_signature = kwargs.get('expected_signature')

        if not self.secret:
            return IntegrationResult(
                success=False,
                error="Webhook secret not configured"
            )

        if expected_signature:
            # Verify against provided signature
            is_valid = hmac.compare_digest(signature, expected_signature)
        else:
            # Generate and verify signature
            if isinstance(payload, dict):
                payload_str = json.dumps(payload, separators=(',', ':'), sort_keys=True)
            else:
                payload_str = str(payload)

            expected_sig = hmac.new(
                self.secret.encode('utf-8'),
                payload_str.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()

            expected_signature = f'sha256={expected_sig}'
            is_valid = hmac.compare_digest(signature, expected_signature)

        return IntegrationResult(
            success=is_valid,
            data={'signature_valid': is_valid, 'expected_signature': expected_signature}
        )

    async def _retry_failed_webhooks(self, **kwargs) -> IntegrationResult:
        """Retry failed webhook deliveries."""
        failed_webhooks = kwargs.get('failed_webhooks', [])
        max_retries = kwargs.get('max_retries', 3)

        results = []
        for webhook in failed_webhooks:
            payload = webhook.get('payload', {})
            attempt = webhook.get('attempt', 0)

            if attempt >= max_retries:
                results.append({
                    'webhook_id': webhook.get('id'),
                    'status': 'max_retries_exceeded',
                    'attempts': attempt
                })
                continue

            # Retry the webhook
            result = await self._send_webhook(payload, webhook.get('event_type', 'retry'))

            results.append({
                'webhook_id': webhook.get('id'),
                'status': 'success' if result.success else 'failed',
                'attempts': attempt + 1,
                'error': result.error if not result.success else None
            })

        return IntegrationResult(
            success=True,
            data={'retry_results': results}
        )

    async def _batch_notifications(self, **kwargs) -> IntegrationResult:
        """Send multiple notifications in batch."""
        notifications = kwargs.get('notifications', [])

        if not notifications:
            return IntegrationResult(
                success=False,
                error="notifications list is required"
            )

        payload = {
            'batch_notifications': {
                'count': len(notifications),
                'notifications': notifications,
                'batch_id': f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'sent_at': datetime.now().isoformat()
            }
        }

        return await self._send_webhook(payload, 'batch_notifications')

    def create_webhook_payload(self, event_type: str, data: Dict[str, Any],
                             metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Helper method to create standardized webhook payloads."""
        return {
            'event_type': event_type,
            'data': data,
            'metadata': metadata or {},
            'webhook_integration': self.name,
            'timestamp': datetime.now().isoformat()
        }

    def get_webhook_signature(self, payload: Dict[str, Any]) -> str:
        """Generate webhook signature for outgoing webhooks."""
        if not self.secret:
            return ''

        payload_str = json.dumps(payload, separators=(',', ':'), sort_keys=True)
        signature = hmac.new(
            self.secret.encode('utf-8'),
            payload_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        return f'sha256={signature}'

    def validate_incoming_webhook(self, payload: str, signature: str) -> bool:
        """Validate incoming webhook signature."""
        if not self.secret:
            return False

        expected_signature = hmac.new(
            self.secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        expected_signature = f'sha256={expected_signature}'

        return hmac.compare_digest(signature, expected_signature)
