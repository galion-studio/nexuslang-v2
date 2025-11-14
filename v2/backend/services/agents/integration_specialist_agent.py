"""
Integration Specialist Agent
Handles all integration-related tasks including Zapier, n8n, webhooks, and API connections.

"Your imagination is the end."
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from .base_agent import BaseAgent, AgentResult, AgentContext, PersonalityTraits, AgentCapabilities
from ..integrations.zapier_integration import get_zapier_service
from ..integrations.n8n_integration import get_n8n_service

logger = logging.getLogger(__name__)


class IntegrationSpecialistAgent(BaseAgent):
    """
    Integration Specialist Agent

    Capabilities:
    - Zapier integration management
    - n8n workflow orchestration
    - Webhook configuration and testing
    - API integration setup
    - Integration monitoring and troubleshooting
    - Cross-platform automation
    """

    def __init__(self):
        super().__init__(
            name="IntegrationSpecialist",
            personality=PersonalityTraits(
                creativity=0.7,
                analytical=0.9,
                communication=0.8,
                organization=0.9,
                adaptability=0.8
            ),
            capabilities=AgentCapabilities(
                expertise=[
                    "zapier_integration",
                    "n8n_workflows",
                    "webhook_management",
                    "api_integration",
                    "automation_setup",
                    "integration_monitoring",
                    "cross_platform_automation"
                ],
                tools=[
                    "zapier_trigger_creator",
                    "n8n_workflow_builder",
                    "webhook_tester",
                    "api_client",
                    "integration_monitor",
                    "automation_orchestrator"
                ]
            )
        )

    async def execute(self, task: str, context: AgentContext) -> AgentResult:
        """
        Execute integration-related tasks

        Args:
            task: Task description
            context: Execution context

        Returns:
            AgentResult with execution outcome
        """
        try:
            task_lower = task.lower()

            # Route to appropriate handler
            if any(keyword in task_lower for keyword in ['zapier', 'trigger', 'webhook']):
                return await self._handle_zapier_task(task, context)
            elif any(keyword in task_lower for keyword in ['n8n', 'workflow', 'automation']):
                return await self._handle_n8n_task(task, context)
            elif any(keyword in task_lower for keyword in ['test', 'verify', 'check']):
                return await self._handle_testing_task(task, context)
            elif any(keyword in task_lower for keyword in ['monitor', 'status', 'health']):
                return await self._handle_monitoring_task(task, context)
            elif any(keyword in task_lower for keyword in ['setup', 'configure', 'integrate']):
                return await self._handle_setup_task(task, context)
            else:
                return await self._handle_general_integration_task(task, context)

        except Exception as e:
            logger.error(f"Integration task failed: {e}")
            return AgentResult(
                success=False,
                data={"error": str(e)},
                cost=0.01,
                metadata={"error_type": "execution_error"}
            )

    async def _handle_zapier_task(self, task: str, context: AgentContext) -> AgentResult:
        """Handle Zapier-related tasks"""
        zapier_service = await get_zapier_service()

        task_lower = task.lower()

        if 'create trigger' in task_lower or 'setup trigger' in task_lower:
            # Extract trigger details from task
            trigger_config = self._extract_trigger_config(task)

            trigger_id = await zapier_service.create_trigger(
                name=trigger_config.get('name', f'Trigger_{datetime.now().strftime("%Y%m%d_%H%M%S")}'),
                description=trigger_config.get('description', 'Auto-created trigger'),
                hook_url=trigger_config.get('hook_url', ''),
                event_type=trigger_config.get('event_type', 'custom_event')
            )

            return AgentResult(
                success=True,
                data={
                    "trigger_id": trigger_id,
                    "action": "created_trigger",
                    "details": trigger_config
                },
                cost=0.02,
                metadata={"integration_type": "zapier", "action": "create_trigger"}
            )

        elif 'test trigger' in task_lower:
            # Test existing triggers
            triggers = zapier_service.get_triggers()
            test_results = []

            for trigger in triggers[:3]:  # Test first 3 triggers
                try:
                    success = await zapier_service.test_trigger(trigger['id'])
                    test_results.append({
                        "trigger_id": trigger['id'],
                        "name": trigger['name'],
                        "success": success
                    })
                except Exception as e:
                    test_results.append({
                        "trigger_id": trigger['id'],
                        "name": trigger['name'],
                        "success": False,
                        "error": str(e)
                    })

            return AgentResult(
                success=True,
                data={"test_results": test_results},
                cost=0.03,
                metadata={"integration_type": "zapier", "action": "test_triggers"}
            )

        return AgentResult(
            success=False,
            data={"error": "Unsupported Zapier task"},
            cost=0.01,
            metadata={"integration_type": "zapier", "action": "unsupported"}
        )

    async def _handle_n8n_task(self, task: str, context: AgentContext) -> AgentResult:
        """Handle n8n-related tasks"""
        n8n_service = await get_n8n_service()

        task_lower = task.lower()

        if 'create workflow' in task_lower or 'setup workflow' in task_lower:
            # Extract workflow details from task
            workflow_config = self._extract_workflow_config(task)

            workflow_id = await n8n_service.create_workflow(
                name=workflow_config.get('name', f'Workflow_{datetime.now().strftime("%Y%m%d_%H%M%S")}'),
                description=workflow_config.get('description', 'Auto-created workflow'),
                webhook_url=workflow_config.get('webhook_url', ''),
                webhook_method=workflow_config.get('method', 'POST'),
                headers=workflow_config.get('headers', {})
            )

            return AgentResult(
                success=True,
                data={
                    "workflow_id": workflow_id,
                    "action": "created_workflow",
                    "details": workflow_config
                },
                cost=0.02,
                metadata={"integration_type": "n8n", "action": "create_workflow"}
            )

        elif 'create trigger' in task_lower:
            # Extract trigger details
            trigger_config = self._extract_n8n_trigger_config(task)

            trigger_id = await n8n_service.create_trigger(
                name=trigger_config.get('name', f'Trigger_{datetime.now().strftime("%Y%m%d_%H%M%S")}'),
                event_type=trigger_config.get('event_type', 'custom_event'),
                workflow_ids=trigger_config.get('workflow_ids', []),
                conditions=trigger_config.get('conditions', {})
            )

            return AgentResult(
                success=True,
                data={
                    "trigger_id": trigger_id,
                    "action": "created_trigger",
                    "details": trigger_config
                },
                cost=0.02,
                metadata={"integration_type": "n8n", "action": "create_trigger"}
            )

        elif 'test workflow' in task_lower:
            # Test existing workflows
            workflows = n8n_service.get_workflows()
            test_results = []

            for workflow in workflows[:3]:  # Test first 3 workflows
                try:
                    result = await n8n_service.test_workflow(workflow['id'])
                    test_results.append({
                        "workflow_id": workflow['id'],
                        "name": workflow['name'],
                        "success": result.get('status') == 'success',
                        "response_time": result.get('response_time')
                    })
                except Exception as e:
                    test_results.append({
                        "workflow_id": workflow['id'],
                        "name": workflow['name'],
                        "success": False,
                        "error": str(e)
                    })

            return AgentResult(
                success=True,
                data={"test_results": test_results},
                cost=0.03,
                metadata={"integration_type": "n8n", "action": "test_workflows"}
            )

        return AgentResult(
            success=False,
            data={"error": "Unsupported n8n task"},
            cost=0.01,
            metadata={"integration_type": "n8n", "action": "unsupported"}
        )

    async def _handle_testing_task(self, task: str, context: AgentContext) -> AgentResult:
        """Handle testing and verification tasks"""
        zapier_service = await get_zapier_service()
        n8n_service = await get_n8n_service()

        # Test all integrations
        results = {
            "zapier_triggers": len(zapier_service.get_triggers()),
            "n8n_workflows": len(n8n_service.get_workflows()),
            "n8n_triggers": len(n8n_service.get_triggers()),
        }

        # Test health
        try:
            zapier_health = {
                'service': 'zapier',
                'status': 'healthy',
                'triggers_count': results['zapier_triggers'],
            }
            n8n_health = await n8n_service.health_check()
            results['health_check'] = {
                'zapier': zapier_health,
                'n8n': n8n_health,
                'overall_status': 'healthy' if n8n_health['status'] == 'healthy' else 'issues'
            }
        except Exception as e:
            results['health_check'] = {'error': str(e)}

        return AgentResult(
            success=True,
            data=results,
            cost=0.02,
            metadata={"action": "integration_testing"}
        )

    async def _handle_monitoring_task(self, task: str, context: AgentContext) -> AgentResult:
        """Handle monitoring tasks"""
        zapier_service = await get_zapier_service()
        n8n_service = await get_n8n_service()

        # Get comprehensive status
        zapier_triggers = zapier_service.get_triggers()
        n8n_workflows = n8n_service.get_workflows()
        n8n_triggers = n8n_service.get_triggers()

        monitoring_data = {
            "zapier": {
                "total_triggers": len(zapier_triggers),
                "active_triggers": len([t for t in zapier_triggers if t['active']]),
                "total_trigger_calls": sum(t['trigger_count'] for t in zapier_triggers),
            },
            "n8n": {
                "total_workflows": len(n8n_workflows),
                "active_workflows": len([w for w in n8n_workflows if w['active']]),
                "total_triggers": len(n8n_triggers),
                "active_triggers": len([t for t in n8n_triggers if t['active']]),
                "total_executions": sum(w['trigger_count'] for w in n8n_workflows),
                "success_rate": sum(w['success_count'] for w in n8n_workflows) /
                              max(sum(w['trigger_count'] for w in n8n_workflows), 1) * 100
            },
            "timestamp": datetime.utcnow().isoformat()
        }

        return AgentResult(
            success=True,
            data=monitoring_data,
            cost=0.02,
            metadata={"action": "integration_monitoring"}
        )

    async def _handle_setup_task(self, task: str, context: AgentContext) -> AgentResult:
        """Handle setup and configuration tasks"""
        # Auto-setup common integrations
        setup_results = []

        try:
            zapier_service = await get_zapier_service()
            n8n_service = await get_n8n_service()

            # Create default triggers for common events
            default_triggers = [
                {
                    'name': 'User Registration',
                    'event_type': 'user_created',
                    'hook_url': 'https://hooks.zapier.com/hooks/catch/YOUR_HOOK_ID/',
                },
                {
                    'name': 'Voice Command',
                    'event_type': 'voice_command',
                    'hook_url': 'https://hooks.zapier.com/hooks/catch/YOUR_HOOK_ID/',
                },
                {
                    'name': 'System Alert',
                    'event_type': 'system_alert',
                    'hook_url': 'https://hooks.zapier.com/hooks/catch/YOUR_HOOK_ID/',
                }
            ]

            for trigger_config in default_triggers:
                try:
                    trigger_id = await zapier_service.create_trigger(
                        name=trigger_config['name'],
                        description=f"Auto-created trigger for {trigger_config['event_type']}",
                        hook_url=trigger_config['hook_url'],
                        event_type=trigger_config['event_type']
                    )
                    setup_results.append({
                        "type": "zapier_trigger",
                        "name": trigger_config['name'],
                        "id": trigger_id,
                        "status": "created"
                    })
                except Exception as e:
                    setup_results.append({
                        "type": "zapier_trigger",
                        "name": trigger_config['name'],
                        "status": "failed",
                        "error": str(e)
                    })

        except Exception as e:
            setup_results.append({
                "type": "setup_error",
                "error": str(e)
            })

        return AgentResult(
            success=len(setup_results) > 0,
            data={"setup_results": setup_results},
            cost=0.03,
            metadata={"action": "integration_setup"}
        )

    async def _handle_general_integration_task(self, task: str, context: AgentContext) -> AgentResult:
        """Handle general integration tasks"""
        # Provide integration recommendations and best practices
        recommendations = {
            "zapier_best_practices": [
                "Use specific event types for better trigger filtering",
                "Test triggers with sample data before production use",
                "Monitor trigger success rates regularly",
                "Use webhook signatures for security"
            ],
            "n8n_best_practices": [
                "Design workflows with error handling",
                "Use correlation IDs for tracking",
                "Implement retry logic for failed executions",
                "Monitor workflow performance metrics"
            ],
            "general_advice": [
                "Start with simple integrations and scale up",
                "Document all integration endpoints and data formats",
                "Implement proper error handling and logging",
                "Regularly review and optimize integration performance"
            ]
        }

        return AgentResult(
            success=True,
            data={
                "recommendations": recommendations,
                "analysis": "Integration architecture analysis complete",
                "next_steps": [
                    "Review existing integrations",
                    "Identify automation opportunities",
                    "Implement monitoring and alerting",
                    "Create documentation"
                ]
            },
            cost=0.02,
            metadata={"action": "general_integration_analysis"}
        )

    def _extract_trigger_config(self, task: str) -> Dict[str, Any]:
        """Extract trigger configuration from task description"""
        # Simple NLP-like extraction - in production use proper NLP
        config = {}

        # Extract name
        if 'named' in task.lower() or 'called' in task.lower():
            # Very basic extraction
            pass

        # Default configuration
        config.update({
            'name': f'Trigger_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'description': 'Auto-created by Integration Specialist',
            'hook_url': 'https://hooks.zapier.com/hooks/catch/YOUR_HOOK_ID/',
            'event_type': 'custom_event'
        })

        return config

    def _extract_workflow_config(self, task: str) -> Dict[str, Any]:
        """Extract workflow configuration from task description"""
        config = {
            'name': f'Workflow_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'description': 'Auto-created by Integration Specialist',
            'webhook_url': 'https://your-n8n-instance.com/webhook/YOUR_WEBHOOK_PATH',
            'method': 'POST',
            'headers': {}
        }

        return config

    def _extract_n8n_trigger_config(self, task: str) -> Dict[str, Any]:
        """Extract n8n trigger configuration from task description"""
        config = {
            'name': f'Trigger_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'event_type': 'custom_event',
            'workflow_ids': [],
            'conditions': {}
        }

        return config
