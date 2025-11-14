"""
n8n Integration Service
Handles n8n workflow triggers and automation for Galion platform.

"Your imagination is the end."
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import uuid

import httpx
from pydantic import BaseModel, Field

from ...core.config import settings

logger = logging.getLogger(__name__)


class N8nWorkflow(BaseModel):
    """n8n workflow configuration"""
    id: str
    name: str
    description: str
    webhook_url: str
    webhook_method: str = "POST"
    headers: Dict[str, str] = Field(default_factory=dict)
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0
    success_count: int = 0
    failure_count: int = 0


class N8nTrigger(BaseModel):
    """n8n trigger event configuration"""
    id: str
    name: str
    event_type: str
    workflow_ids: List[str] = Field(default_factory=list)
    conditions: Dict[str, Any] = Field(default_factory=dict)
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)


class N8nWebhookPayload(BaseModel):
    """Standard webhook payload for n8n"""
    event_type: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data: Dict[str, Any]
    source: str = "galion"
    version: str = "2.0"
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))


class N8nIntegrationService:
    """
    n8n Integration Service

    Handles:
    - Workflow webhook management
    - Event-based triggers
    - Workflow execution monitoring
    - Error handling and retries
    - Integration lifecycle management
    """

    def __init__(self):
        self.workflows: Dict[str, N8nWorkflow] = {}
        self.triggers: Dict[str, N8nTrigger] = {}
        self.client = httpx.AsyncClient(timeout=60.0)  # n8n workflows can be complex
        self.logger = logging.getLogger(__name__)

        # Load existing configurations
        self._load_configurations()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    def _load_configurations(self):
        """Load workflow and trigger configurations"""
        # In production, this would load from database
        # For now, using in-memory storage
        pass

    async def trigger_workflow(
        self,
        workflow_id: str,
        event_data: Dict[str, Any],
        user_id: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Trigger an n8n workflow execution

        Args:
            workflow_id: ID of the workflow to trigger
            event_data: Data to send to the workflow
            user_id: Optional user context
            correlation_id: Optional correlation ID for tracking

        Returns:
            Execution result
        """
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")

        workflow = self.workflows[workflow_id]
        if not workflow.active:
            return {
                'status': 'skipped',
                'reason': 'workflow_inactive',
                'workflow_id': workflow_id
            }

        try:
            # Prepare payload
            payload = N8nWebhookPayload(
                event_type=f"galion_{workflow.name.lower().replace(' ', '_')}",
                data=event_data,
                source="galion",
                correlation_id=correlation_id or str(uuid.uuid4())
            )

            # Add user context if provided
            if user_id:
                payload.data['user_id'] = user_id

            # Prepare headers
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'Galion-n8n-Integration/2.0',
                'X-Correlation-ID': payload.correlation_id,
                **workflow.headers
            }

            # Execute webhook
            response = await self.client.request(
                method=workflow.webhook_method,
                url=workflow.webhook_url,
                json=payload.dict(),
                headers=headers
            )

            # Update workflow stats
            workflow.last_triggered = datetime.utcnow()
            workflow.trigger_count += 1

            if response.status_code >= 200 and response.status_code < 300:
                workflow.success_count += 1
                status = 'success'
            else:
                workflow.failure_count += 1
                status = 'failed'

            result = {
                'status': status,
                'workflow_id': workflow_id,
                'correlation_id': payload.correlation_id,
                'response_status': response.status_code,
                'response_time': response.elapsed.total_seconds(),
                'timestamp': datetime.utcnow().isoformat()
            }

            self.logger.info(f"n8n workflow triggered: {workflow.name} - {status}")
            return result

        except Exception as e:
            self.logger.error(f"Workflow execution failed: {e}")
            workflow.failure_count += 1

            return {
                'status': 'error',
                'workflow_id': workflow_id,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }

    async def handle_event(
        self,
        event_type: str,
        event_data: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Handle an event and trigger relevant workflows

        Args:
            event_type: Type of event
            event_data: Event data
            user_id: Optional user context

        Returns:
            List of workflow execution results
        """
        results = []

        # Find triggers for this event type
        matching_triggers = [
            trigger for trigger in self.triggers.values()
            if trigger.event_type == event_type and trigger.active
        ]

        for trigger in matching_triggers:
            # Check conditions if any
            if self._check_trigger_conditions(trigger, event_data):
                # Trigger all associated workflows
                for workflow_id in trigger.workflow_ids:
                    try:
                        result = await self.trigger_workflow(
                            workflow_id,
                            event_data,
                            user_id
                        )
                        results.append({
                            'trigger_id': trigger.id,
                            'workflow_id': workflow_id,
                            **result
                        })
                    except Exception as e:
                        self.logger.error(f"Failed to trigger workflow {workflow_id}: {e}")
                        results.append({
                            'trigger_id': trigger.id,
                            'workflow_id': workflow_id,
                            'status': 'error',
                            'error': str(e)
                        })

        return results

    def _check_trigger_conditions(self, trigger: N8nTrigger, event_data: Dict[str, Any]) -> bool:
        """Check if trigger conditions are met"""
        if not trigger.conditions:
            return True

        # Simple condition checking - could be enhanced with more complex logic
        for key, expected_value in trigger.conditions.items():
            actual_value = event_data.get(key)
            if actual_value != expected_value:
                return False

        return True

    async def create_workflow(
        self,
        name: str,
        description: str,
        webhook_url: str,
        webhook_method: str = "POST",
        headers: Optional[Dict[str, str]] = None
    ) -> str:
        """Create a new n8n workflow configuration"""
        workflow_id = f"workflow_{len(self.workflows) + 1}"

        workflow = N8nWorkflow(
            id=workflow_id,
            name=name,
            description=description,
            webhook_url=webhook_url,
            webhook_method=webhook_method,
            headers=headers or {},
            active=True
        )

        self.workflows[workflow_id] = workflow
        self.logger.info(f"Created n8n workflow: {name}")

        return workflow_id

    async def create_trigger(
        self,
        name: str,
        event_type: str,
        workflow_ids: List[str],
        conditions: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new event trigger"""
        trigger_id = f"trigger_{len(self.triggers) + 1}"

        trigger = N8nTrigger(
            id=trigger_id,
            name=name,
            event_type=event_type,
            workflow_ids=workflow_ids,
            conditions=conditions or {},
            active=True
        )

        self.triggers[trigger_id] = trigger
        self.logger.info(f"Created n8n trigger: {name} for event {event_type}")

        return trigger_id

    async def test_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Test a workflow with sample data"""
        test_data = {
            'test': True,
            'timestamp': datetime.utcnow().isoformat(),
            'message': 'This is a test workflow execution from Galion',
            'sample_data': {
                'user_id': 'test_user_123',
                'action': 'test_action',
                'metadata': {'source': 'integration_test'}
            }
        }

        return await self.trigger_workflow(workflow_id, test_data)

    def get_workflows(self) -> List[Dict[str, Any]]:
        """Get all workflows"""
        return [
            {
                'id': workflow.id,
                'name': workflow.name,
                'description': workflow.description,
                'webhook_url': workflow.webhook_url,
                'webhook_method': workflow.webhook_method,
                'active': workflow.active,
                'created_at': workflow.created_at.isoformat(),
                'last_triggered': workflow.last_triggered.isoformat() if workflow.last_triggered else None,
                'trigger_count': workflow.trigger_count,
                'success_count': workflow.success_count,
                'failure_count': workflow.failure_count,
                'success_rate': (workflow.success_count / workflow.trigger_count * 100) if workflow.trigger_count > 0 else 0,
            }
            for workflow in self.workflows.values()
        ]

    def get_triggers(self) -> List[Dict[str, Any]]:
        """Get all triggers"""
        return [
            {
                'id': trigger.id,
                'name': trigger.name,
                'event_type': trigger.event_type,
                'workflow_ids': trigger.workflow_ids,
                'conditions': trigger.conditions,
                'active': trigger.active,
                'created_at': trigger.created_at.isoformat(),
            }
            for trigger in self.triggers.values()
        ]

    async def get_workflow_stats(self, workflow_id: str) -> Dict[str, Any]:
        """Get detailed statistics for a workflow"""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")

        workflow = self.workflows[workflow_id]

        return {
            'workflow_id': workflow_id,
            'name': workflow.name,
            'total_executions': workflow.trigger_count,
            'successful_executions': workflow.success_count,
            'failed_executions': workflow.failure_count,
            'success_rate': (workflow.success_count / workflow.trigger_count * 100) if workflow.trigger_count > 0 else 0,
            'last_execution': workflow.last_triggered.isoformat() if workflow.last_triggered else None,
            'average_response_time': 0.0,  # Would need to track this
        }

    async def bulk_trigger_event(
        self,
        event_type: str,
        events_data: List[Dict[str, Any]],
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Trigger multiple events of the same type

        Args:
            event_type: Type of events
            events_data: List of event data
            user_id: Optional user context

        Returns:
            List of execution results
        """
        all_results = []

        for event_data in events_data:
            results = await self.handle_event(event_type, event_data, user_id)
            all_results.extend(results)

        return all_results

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on n8n integration"""
        health_status = {
            'service': 'n8n_integration',
            'status': 'healthy',
            'workflows_count': len(self.workflows),
            'triggers_count': len(self.triggers),
            'active_workflows': len([w for w in self.workflows.values() if w.active]),
            'active_triggers': len([t for t in self.triggers.values() if t.active]),
            'timestamp': datetime.utcnow().isoformat()
        }

        # Test a sample workflow if available
        sample_workflow = next(iter(self.workflows.values()), None)
        if sample_workflow:
            try:
                test_result = await self.test_workflow(sample_workflow.id)
                health_status['test_workflow_status'] = test_result['status']
            except Exception as e:
                health_status['test_workflow_status'] = 'error'
                health_status['test_error'] = str(e)

        return health_status


# Global service instance
_n8n_service: Optional[N8nIntegrationService] = None

async def get_n8n_service() -> N8nIntegrationService:
    """Get the global n8n service instance"""
    global _n8n_service

    if _n8n_service is None:
        _n8n_service = N8nIntegrationService()

    return _n8n_service
