"""
Integrations API Endpoints
Handles Zapier and n8n workflow integrations for Galion platform.

"Your imagination is the end."
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from ..core.database import get_db
from ..services.integrations.zapier_integration import get_zapier_service
from ..services.integrations.n8n_integration import get_n8n_service
from ..core.auth import get_current_user
from ..models.user import User

router = APIRouter(prefix="/integrations", tags=["Integrations"])
security = HTTPBearer()


# Pydantic Models
class ZapierTriggerCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    hook_url: str = Field(..., description="Zapier webhook URL")
    event_type: str = Field(..., description="Event type to trigger on")


class ZapierActionCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    action_type: str = Field(..., description="Type of action")
    config: Dict[str, Any] = Field(default_factory=dict, description="Action configuration")


class N8nWorkflowCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    webhook_url: str = Field(..., description="n8n webhook URL")
    webhook_method: str = Field(default="POST", description="HTTP method")
    headers: Dict[str, str] = Field(default_factory=dict, description="Custom headers")


class N8nTriggerCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    event_type: str = Field(..., description="Event type to trigger on")
    workflow_ids: List[str] = Field(..., description="Workflow IDs to trigger")
    conditions: Dict[str, Any] = Field(default_factory=dict, description="Trigger conditions")


class EventTrigger(BaseModel):
    event_type: str = Field(..., description="Type of event")
    data: Dict[str, Any] = Field(..., description="Event data")
    user_id: Optional[str] = Field(None, description="User context")


class BulkEventTrigger(BaseModel):
    event_type: str = Field(..., description="Type of event")
    events_data: List[Dict[str, Any]] = Field(..., description="List of event data")
    user_id: Optional[str] = Field(None, description="User context")


# Dependencies
async def get_zapier_service_dep():
    """Get the Zapier service instance"""
    return await get_zapier_service()


async def get_n8n_service_dep():
    """Get the n8n service instance"""
    return await get_n8n_service()


# Zapier Integration Routes
@router.post("/zapier/webhook/{webhook_secret}")
async def zapier_webhook(
    webhook_secret: str,
    payload: Dict[str, Any],
    request: Request,
    zapier_service = Depends(get_zapier_service_dep),
):
    """
    Handle Zapier webhook

    This endpoint receives webhooks from Zapier and processes them accordingly.
    The webhook_secret should be configured in your Zapier zap for security.
    """
    try:
        headers = dict(request.headers)
        result = await zapier_service.handle_webhook(payload, headers, webhook_secret)

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Webhook processing failed: {str(e)}"
        )


@router.post("/zapier/triggers", response_model=Dict[str, str])
async def create_zapier_trigger(
    trigger_data: ZapierTriggerCreate,
    zapier_service = Depends(get_zapier_service_dep),
    current_user: User = Depends(get_current_user),
):
    """Create a new Zapier trigger"""
    try:
        trigger_id = await zapier_service.create_trigger(
            name=trigger_data.name,
            description=trigger_data.description,
            hook_url=trigger_data.hook_url,
            event_type=trigger_data.event_type,
        )

        return {"trigger_id": trigger_id, "message": "Trigger created successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create trigger: {str(e)}"
        )


@router.get("/zapier/triggers")
async def list_zapier_triggers(
    zapier_service = Depends(get_zapier_service_dep),
    current_user: User = Depends(get_current_user),
):
    """List all Zapier triggers"""
    try:
        return zapier_service.get_triggers()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list triggers: {str(e)}"
        )


@router.post("/zapier/triggers/{trigger_id}/test")
async def test_zapier_trigger(
    trigger_id: str,
    zapier_service = Depends(get_zapier_service_dep),
    current_user: User = Depends(get_current_user),
):
    """Test a Zapier trigger with sample data"""
    try:
        success = await zapier_service.test_trigger(trigger_id)

        if success:
            return {"message": "Trigger test successful"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Trigger test failed"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Trigger test failed: {str(e)}"
        )


@router.post("/zapier/actions", response_model=Dict[str, str])
async def create_zapier_action(
    action_data: ZapierActionCreate,
    zapier_service = Depends(get_zapier_service_dep),
    current_user: User = Depends(get_current_user),
):
    """Create a new Zapier action"""
    try:
        action_id = await zapier_service.create_action(
            name=action_data.name,
            description=action_data.description,
            action_type=action_data.action_type,
            config=action_data.config,
        )

        return {"action_id": action_id, "message": "Action created successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create action: {str(e)}"
        )


@router.get("/zapier/actions")
async def list_zapier_actions(
    zapier_service = Depends(get_zapier_service_dep),
    current_user: User = Depends(get_current_user),
):
    """List all Zapier actions"""
    try:
        return zapier_service.get_actions()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list actions: {str(e)}"
        )


# n8n Integration Routes
@router.post("/n8n/workflows", response_model=Dict[str, str])
async def create_n8n_workflow(
    workflow_data: N8nWorkflowCreate,
    n8n_service = Depends(get_n8n_service_dep),
    current_user: User = Depends(get_current_user),
):
    """Create a new n8n workflow configuration"""
    try:
        workflow_id = await n8n_service.create_workflow(
            name=workflow_data.name,
            description=workflow_data.description,
            webhook_url=workflow_data.webhook_url,
            webhook_method=workflow_data.webhook_method,
            headers=workflow_data.headers,
        )

        return {"workflow_id": workflow_id, "message": "Workflow created successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create workflow: {str(e)}"
        )


@router.get("/n8n/workflows")
async def list_n8n_workflows(
    n8n_service = Depends(get_n8n_service_dep),
    current_user: User = Depends(get_current_user),
):
    """List all n8n workflows"""
    try:
        return n8n_service.get_workflows()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list workflows: {str(e)}"
        )


@router.post("/n8n/workflows/{workflow_id}/test")
async def test_n8n_workflow(
    workflow_id: str,
    n8n_service = Depends(get_n8n_service_dep),
    current_user: User = Depends(get_current_user),
):
    """Test an n8n workflow with sample data"""
    try:
        result = await n8n_service.test_workflow(workflow_id)
        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Workflow test failed: {str(e)}"
        )


@router.get("/n8n/workflows/{workflow_id}/stats")
async def get_n8n_workflow_stats(
    workflow_id: str,
    n8n_service = Depends(get_n8n_service_dep),
    current_user: User = Depends(get_current_user),
):
    """Get statistics for a specific n8n workflow"""
    try:
        return await n8n_service.get_workflow_stats(workflow_id)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workflow stats: {str(e)}"
        )


@router.post("/n8n/triggers", response_model=Dict[str, str])
async def create_n8n_trigger(
    trigger_data: N8nTriggerCreate,
    n8n_service = Depends(get_n8n_service_dep),
    current_user: User = Depends(get_current_user),
):
    """Create a new n8n event trigger"""
    try:
        trigger_id = await n8n_service.create_trigger(
            name=trigger_data.name,
            event_type=trigger_data.event_type,
            workflow_ids=trigger_data.workflow_ids,
            conditions=trigger_data.conditions,
        )

        return {"trigger_id": trigger_id, "message": "Trigger created successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create trigger: {str(e)}"
        )


@router.get("/n8n/triggers")
async def list_n8n_triggers(
    n8n_service = Depends(get_n8n_service_dep),
    current_user: User = Depends(get_current_user),
):
    """List all n8n triggers"""
    try:
        return n8n_service.get_triggers()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list triggers: {str(e)}"
        )


# Event Triggering Routes (for both Zapier and n8n)
@router.post("/events/trigger")
async def trigger_event(
    event_data: EventTrigger,
    background_tasks: BackgroundTasks,
    zapier_service = Depends(get_zapier_service_dep),
    n8n_service = Depends(get_n8n_service_dep),
    current_user: User = Depends(get_current_user),
):
    """
    Trigger an event that will be sent to configured Zapier zaps and n8n workflows

    This endpoint allows manual triggering of events for testing integrations.
    """
    try:
        results = []

        # Trigger Zapier zaps
        zapier_triggers = [
            trigger for trigger in zapier_service.triggers.values()
            if trigger.event_type == event_data.event_type and trigger.active
        ]

        for trigger in zapier_triggers:
            background_tasks.add_task(
                zapier_service.trigger_event,
                trigger.id,
                event_data.data,
                event_data.user_id
            )
            results.append({
                'integration': 'zapier',
                'trigger_id': trigger.id,
                'status': 'triggered'
            })

        # Trigger n8n workflows
        n8n_results = await n8n_service.handle_event(
            event_data.event_type,
            event_data.data,
            event_data.user_id
        )

        for result in n8n_results:
            results.append({
                'integration': 'n8n',
                **result
            })

        return {
            'message': f'Event "{event_data.event_type}" triggered successfully',
            'results': results,
            'total_triggers': len(results)
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Event triggering failed: {str(e)}"
        )


@router.post("/events/bulk-trigger")
async def bulk_trigger_events(
    bulk_data: BulkEventTrigger,
    background_tasks: BackgroundTasks,
    n8n_service = Depends(get_n8n_service_dep),
    current_user: User = Depends(get_current_user),
):
    """
    Bulk trigger multiple events of the same type

    Useful for processing batches of events through n8n workflows.
    """
    try:
        results = await n8n_service.bulk_trigger_event(
            bulk_data.event_type,
            bulk_data.events_data,
            bulk_data.user_id
        )

        return {
            'message': f'Bulk triggered {len(bulk_data.events_data)} events of type "{bulk_data.event_type}"',
            'results': results,
            'successful_triggers': len([r for r in results if r.get('status') == 'success']),
            'failed_triggers': len([r for r in results if r.get('status') == 'failed' or r.get('status') == 'error'])
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk event triggering failed: {str(e)}"
        )


# Health Check Routes
@router.get("/health")
async def get_integrations_health(
    zapier_service = Depends(get_zapier_service_dep),
    n8n_service = Depends(get_n8n_service_dep),
    current_user: User = Depends(get_current_user),
):
    """Get health status of all integrations"""
    try:
        zapier_health = {
            'service': 'zapier',
            'status': 'healthy',
            'triggers_count': len(zapier_service.triggers),
            'actions_count': len(zapier_service.actions),
            'active_triggers': len([t for t in zapier_service.triggers.values() if t.active]),
        }

        n8n_health = await n8n_service.health_check()

        return {
            'integrations': [zapier_health, n8n_health],
            'overall_status': 'healthy' if all(h['status'] == 'healthy' for h in [zapier_health, n8n_health]) else 'degraded',
            'timestamp': datetime.utcnow().isoformat()
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}"
        )


# Integration Setup Helper Routes
@router.get("/setup/zapier")
async def get_zapier_setup_info():
    """
    Get setup information for Zapier integration

    Returns webhook URLs and configuration examples.
    """
    return {
        'webhook_base_url': 'https://api.galion.app/v2/integrations/zapier/webhook',
        'supported_events': [
            'user_created',
            'voice_command',
            'agent_task_completed',
            'system_alert',
            'custom_event'
        ],
        'authentication': 'webhook_secret parameter in URL',
        'payload_format': {
            'event_type': 'string',
            'timestamp': 'ISO datetime',
            'data': 'object',
            'source': 'galion',
            'version': '2.0'
        },
        'example_payload': {
            'event_type': 'user_created',
            'timestamp': '2024-01-01T12:00:00Z',
            'data': {'user_id': '123', 'email': 'user@example.com'},
            'source': 'galion',
            'version': '2.0'
        }
    }


@router.get("/setup/n8n")
async def get_n8n_setup_info():
    """
    Get setup information for n8n integration

    Returns webhook configuration and event types.
    """
    return {
        'webhook_methods': ['POST', 'GET', 'PUT', 'PATCH'],
        'supported_events': [
            'user_registration',
            'voice_session_started',
            'voice_session_ended',
            'agent_task_created',
            'agent_task_completed',
            'system_backup_completed',
            'error_alert',
            'performance_alert',
            'custom_business_event'
        ],
        'authentication': 'custom headers support',
        'payload_format': {
            'event_type': 'string',
            'timestamp': 'ISO datetime',
            'data': 'object',
            'source': 'galion',
            'version': '2.0',
            'correlation_id': 'UUID string'
        },
        'example_workflow_triggers': [
            'Send welcome email on user registration',
            'Create support ticket on error alert',
            'Send Slack notification on system backup completion',
            'Trigger CRM update on voice session completion'
        ]
    }