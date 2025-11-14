"""
Zapier Integration Service
Handles Zapier webhooks and triggers for Galion platform automation.

"Your imagination is the end."
"""

import asyncio
import hmac
import hashlib
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from urllib.parse import urlencode

import httpx
from pydantic import BaseModel, Field

from ...core.config import settings

logger = logging.getLogger(__name__)


class ZapierTrigger(BaseModel):
    """Zapier trigger configuration"""
    id: str
    name: str
    description: str
    hook_url: str
    event_type: str
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0


class ZapierAction(BaseModel):
    """Zapier action configuration"""
    id: str
    name: str
    description: str
    action_type: str
    config: Dict[str, Any] = Field(default_factory=dict)
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_executed: Optional[datetime] = None
    execution_count: int = 0


class ZapierWebhookPayload(BaseModel):
    """Standard webhook payload structure"""
    event_type: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data: Dict[str, Any]
    source: str = "galion"
    version: str = "2.0"


class ZapierIntegrationService:
    """
    Zapier Integration Service

    Handles:
    - Webhook authentication and validation
    - Trigger management (sending data to Zapier)
    - Action handling (receiving commands from Zapier)
    - Integration lifecycle management
    """

    def __init__(self):
        self.triggers: Dict[str, ZapierTrigger] = {}
        self.actions: Dict[str, ZapierAction] = {}
        self.client = httpx.AsyncClient(timeout=30.0)
        self.logger = logging.getLogger(__name__)

        # Load existing configurations
        self._load_configurations()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    def _load_configurations(self):
        """Load trigger and action configurations"""
        # In production, this would load from database
        # For now, using in-memory storage
        pass

    def _verify_webhook_signature(self, payload: str, signature: str, secret: str) -> bool:
        """Verify Zapier webhook signature"""
        expected_signature = hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected_signature)

    async def handle_webhook(
        self,
        payload: Dict[str, Any],
        headers: Dict[str, str],
        webhook_secret: str
    ) -> Dict[str, Any]:
        """
        Handle incoming Zapier webhook

        Args:
            payload: Webhook payload
            headers: Request headers
            webhook_secret: Webhook secret for verification

        Returns:
            Response data
        """
        try:
            # Verify webhook signature if provided
            signature = headers.get('x-zapier-signature')
            if signature and webhook_secret:
                payload_str = json.dumps(payload, sort_keys=True)
                if not self._verify_webhook_signature(payload_str, signature, webhook_secret):
                    raise ValueError("Invalid webhook signature")

            event_type = payload.get('event_type', 'unknown')
            self.logger.info(f"Processing Zapier webhook: {event_type}")

            # Route to appropriate handler
            if event_type == 'user_created':
                return await self._handle_user_created(payload)
            elif event_type == 'voice_command':
                return await self._handle_voice_command(payload)
            elif event_type == 'agent_task_completed':
                return await self._handle_agent_task_completed(payload)
            elif event_type == 'system_alert':
                return await self._handle_system_alert(payload)
            else:
                return await self._handle_custom_event(event_type, payload)

        except Exception as e:
            self.logger.error(f"Webhook processing failed: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    async def trigger_event(
        self,
        trigger_id: str,
        event_data: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> bool:
        """
        Trigger a Zapier zap with event data

        Args:
            trigger_id: ID of the trigger to activate
            event_data: Data to send to Zapier
            user_id: Optional user context

        Returns:
            Success status
        """
        if trigger_id not in self.triggers:
            self.logger.warning(f"Trigger {trigger_id} not found")
            return False

        trigger = self.triggers[trigger_id]
        if not trigger.active:
            self.logger.info(f"Trigger {trigger_id} is inactive")
            return False

        try:
            # Prepare payload
            payload = ZapierWebhookPayload(
                event_type=trigger.event_type,
                data=event_data,
                source="galion",
                version="2.0"
            )

            # Send to Zapier
            response = await self.client.post(
                trigger.hook_url,
                json=payload.dict(),
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'Galion-Zapier-Integration/2.0'
                }
            )

            if response.status_code == 200:
                # Update trigger stats
                trigger.last_triggered = datetime.utcnow()
                trigger.trigger_count += 1
                self.logger.info(f"Successfully triggered Zapier zap: {trigger.name}")
                return True
            else:
                self.logger.error(f"Zapier trigger failed: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            self.logger.error(f"Trigger execution failed: {e}")
            return False

    async def create_trigger(
        self,
        name: str,
        description: str,
        hook_url: str,
        event_type: str
    ) -> str:
        """Create a new Zapier trigger"""
        trigger_id = f"trigger_{len(self.triggers) + 1}"

        trigger = ZapierTrigger(
            id=trigger_id,
            name=name,
            description=description,
            hook_url=hook_url,
            event_type=event_type,
            active=True
        )

        self.triggers[trigger_id] = trigger
        self.logger.info(f"Created Zapier trigger: {name}")

        return trigger_id

    async def create_action(
        self,
        name: str,
        description: str,
        action_type: str,
        config: Dict[str, Any]
    ) -> str:
        """Create a new Zapier action"""
        action_id = f"action_{len(self.actions) + 1}"

        action = ZapierAction(
            id=action_id,
            name=name,
            description=description,
            action_type=action_type,
            config=config,
            active=True
        )

        self.actions[action_id] = action
        self.logger.info(f"Created Zapier action: {name}")

        return action_id

    async def _handle_user_created(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle user creation event"""
        user_data = payload.get('data', {})
        user_id = user_data.get('user_id')

        self.logger.info(f"Processing user creation for: {user_id}")

        # Could trigger welcome email, user onboarding, etc.
        return {
            'status': 'processed',
            'event': 'user_created',
            'user_id': user_id,
            'actions_taken': ['user_welcome_sequence']
        }

    async def _handle_voice_command(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle voice command event"""
        command_data = payload.get('data', {})
        command = command_data.get('command')
        user_id = command_data.get('user_id')

        self.logger.info(f"Processing voice command: {command} for user {user_id}")

        # Could route to appropriate agent or automation
        return {
            'status': 'processed',
            'event': 'voice_command',
            'command': command,
            'user_id': user_id,
            'response': 'Command routed to agent system'
        }

    async def _handle_agent_task_completed(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle agent task completion event"""
        task_data = payload.get('data', {})
        task_id = task_data.get('task_id')
        result = task_data.get('result')

        self.logger.info(f"Processing task completion: {task_id}")

        # Could trigger notifications, follow-up actions, etc.
        return {
            'status': 'processed',
            'event': 'agent_task_completed',
            'task_id': task_id,
            'result_summary': str(result)[:100] + '...' if len(str(result)) > 100 else str(result)
        }

    async def _handle_system_alert(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle system alert event"""
        alert_data = payload.get('data', {})
        alert_type = alert_data.get('type')
        severity = alert_data.get('severity')

        self.logger.info(f"Processing system alert: {alert_type} ({severity})")

        # Could trigger escalation procedures, notifications, etc.
        return {
            'status': 'processed',
            'event': 'system_alert',
            'alert_type': alert_type,
            'severity': severity,
            'escalation_required': severity in ['critical', 'high']
        }

    async def _handle_custom_event(self, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle custom events"""
        self.logger.info(f"Processing custom event: {event_type}")

        return {
            'status': 'processed',
            'event': event_type,
            'data': payload.get('data', {}),
            'custom_handling': True
        }

    def get_triggers(self) -> List[Dict[str, Any]]:
        """Get all triggers"""
        return [
            {
                'id': trigger.id,
                'name': trigger.name,
                'description': trigger.description,
                'event_type': trigger.event_type,
                'active': trigger.active,
                'created_at': trigger.created_at.isoformat(),
                'last_triggered': trigger.last_triggered.isoformat() if trigger.last_triggered else None,
                'trigger_count': trigger.trigger_count,
            }
            for trigger in self.triggers.values()
        ]

    def get_actions(self) -> List[Dict[str, Any]]:
        """Get all actions"""
        return [
            {
                'id': action.id,
                'name': action.name,
                'description': action.description,
                'action_type': action.action_type,
                'active': action.active,
                'created_at': action.created_at.isoformat(),
                'last_executed': action.last_executed.isoformat() if action.last_executed else None,
                'execution_count': action.execution_count,
            }
            for action in self.actions.values()
        ]

    async def test_trigger(self, trigger_id: str) -> bool:
        """Test a trigger with sample data"""
        test_data = {
            'test': True,
            'timestamp': datetime.utcnow().isoformat(),
            'message': 'This is a test trigger from Galion'
        }

        return await self.trigger_event(trigger_id, test_data)


# Global service instance
_zapier_service: Optional[ZapierIntegrationService] = None

async def get_zapier_service() -> ZapierIntegrationService:
    """Get the global Zapier service instance"""
    global _zapier_service

    if _zapier_service is None:
        _zapier_service = ZapierIntegrationService()

    return _zapier_service
