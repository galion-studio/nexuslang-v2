"""
n8n Specialist Agent
Specializes in creating, building, and managing n8n workflows automatically.

"Your imagination is the end."
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import json
import uuid

from .base_agent import BaseAgent, AgentResult, AgentContext, PersonalityTraits, AgentCapabilities
from ..integrations.n8n_integration import get_n8n_service

logger = logging.getLogger(__name__)


class N8nSpecialistAgent(BaseAgent):
    """
    n8n Specialist Agent

    Capabilities:
    - Automated n8n workflow creation
    - Workflow template generation
    - Workflow optimization and testing
    - Integration pipeline building
    - Workflow monitoring and maintenance
    - n8n best practices implementation
    """

    def __init__(self):
        super().__init__(
            name="N8nSpecialist",
            personality=PersonalityTraits(
                creativity=0.8,
                analytical=0.8,
                communication=0.7,
                organization=0.9,
                adaptability=0.8
            ),
            capabilities=AgentCapabilities(
                expertise=[
                    "n8n_workflow_creation",
                    "workflow_automation",
                    "integration_pipelines",
                    "workflow_optimization",
                    "n8n_best_practices",
                    "workflow_testing",
                    "workflow_maintenance"
                ],
                tools=[
                    "workflow_builder",
                    "template_generator",
                    "integration_tester",
                    "performance_optimizer",
                    "workflow_validator",
                    "automation_script_writer"
                ]
            )
        )

        self.workflow_templates = self._load_workflow_templates()

    def _load_workflow_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load predefined workflow templates"""
        return {
            "user_onboarding": {
                "description": "Complete user onboarding workflow with email notifications and account setup",
                "nodes": ["webhook", "set", "email", "http_request", "set"],
                "connections": [
                    {"from": "webhook", "to": "set", "output": 0, "input": 0},
                    {"from": "set", "to": "email", "output": 0, "input": 0},
                    {"from": "email", "to": "http_request", "output": 0, "input": 0},
                    {"from": "http_request", "to": "set1", "output": 0, "input": 0}
                ]
            },
            "data_sync": {
                "description": "Automated data synchronization between multiple systems",
                "nodes": ["schedule", "http_request", "set", "function", "if", "email"],
                "connections": [
                    {"from": "schedule", "to": "http_request", "output": 0, "input": 0},
                    {"from": "http_request", "to": "set", "output": 0, "input": 0},
                    {"from": "set", "to": "function", "output": 0, "input": 0},
                    {"from": "function", "to": "if", "output": 0, "input": 0},
                    {"from": "if", "to": "email", "output": 0, "input": 1}  # Error path
                ]
            },
            "error_monitoring": {
                "description": "Comprehensive error monitoring and alerting system",
                "nodes": ["webhook", "function", "if", "slack", "email", "set"],
                "connections": [
                    {"from": "webhook", "to": "function", "output": 0, "input": 0},
                    {"from": "function", "to": "if", "output": 0, "input": 0},
                    {"from": "if", "to": "slack", "output": 0, "input": 0},
                    {"from": "if", "to": "email", "output": 1, "input": 0},
                    {"from": "slack", "to": "set", "output": 0, "input": 0},
                    {"from": "email", "to": "set", "output": 0, "input": 0}
                ]
            },
            "api_integration": {
                "description": "Generic API integration workflow with error handling",
                "nodes": ["webhook", "http_request", "function", "if", "set", "return"],
                "connections": [
                    {"from": "webhook", "to": "http_request", "output": 0, "input": 0},
                    {"from": "http_request", "to": "function", "output": 0, "input": 0},
                    {"from": "http_request", "to": "function", "output": 1, "input": 0},  # Error path
                    {"from": "function", "to": "if", "output": 0, "input": 0},
                    {"from": "function", "to": "set", "output": 1, "input": 0},  # Error handling
                    {"from": "if", "to": "set1", "output": 0, "input": 0},
                    {"from": "if", "to": "return", "output": 1, "input": 0},
                    {"from": "set1", "to": "return", "output": 0, "input": 0}
                ]
            },
            "notification_system": {
                "description": "Multi-channel notification system (email, Slack, SMS)",
                "nodes": ["webhook", "function", "if", "email", "slack", "twilio", "set"],
                "connections": [
                    {"from": "webhook", "to": "function", "output": 0, "input": 0},
                    {"from": "function", "to": "if", "output": 0, "input": 0},
                    {"from": "if", "to": "email", "output": 0, "input": 0},
                    {"from": "if", "to": "slack", "output": 1, "input": 0},
                    {"from": "if", "to": "twilio", "output": 2, "input": 0},
                    {"from": "email", "to": "set", "output": 0, "input": 0},
                    {"from": "slack", "to": "set", "output": 0, "input": 0},
                    {"from": "twilio", "to": "set", "output": 0, "input": 0}
                ]
            }
        }

    async def execute(self, task: str, context: AgentContext) -> AgentResult:
        """
        Execute n8n specialist tasks

        Args:
            task: Task description
            context: Execution context

        Returns:
            AgentResult with execution outcome
        """
        try:
            task_lower = task.lower()

            # Route to appropriate handler
            if any(keyword in task_lower for keyword in ['create', 'build', 'generate']):
                return await self._handle_creation_task(task, context)
            elif any(keyword in task_lower for keyword in ['template', 'use template']):
                return await self._handle_template_task(task, context)
            elif any(keyword in task_lower for keyword in ['test', 'verify', 'validate']):
                return await self._handle_testing_task(task, context)
            elif any(keyword in task_lower for keyword in ['optimize', 'improve', 'performance']):
                return await self._handle_optimization_task(task, context)
            elif any(keyword in task_lower for keyword in ['monitor', 'status', 'health']):
                return await self._handle_monitoring_task(task, context)
            elif any(keyword in task_lower for keyword in ['maintain', 'update', 'fix']):
                return await self._handle_maintenance_task(task, context)
            else:
                return await self._handle_general_n8n_task(task, context)

        except Exception as e:
            logger.error(f"n8n Specialist task failed: {e}")
            return AgentResult(
                success=False,
                data={"error": str(e)},
                cost=0.02,
                metadata={"error_type": "execution_error"}
            )

    async def _handle_creation_task(self, task: str, context: AgentContext) -> AgentResult:
        """Handle workflow creation tasks"""
        n8n_service = await get_n8n_service()

        # Analyze task to determine workflow requirements
        workflow_config = self._analyze_workflow_requirements(task)

        # Create the workflow
        workflow_id = await n8n_service.create_workflow(
            name=workflow_config['name'],
            description=workflow_config['description'],
            webhook_url=workflow_config.get('webhook_url', 'https://your-n8n-instance.com/webhook/auto_generated'),
            webhook_method=workflow_config.get('method', 'POST'),
            headers=workflow_config.get('headers', {})
        )

        # Create associated trigger if needed
        trigger_config = workflow_config.get('trigger')
        if trigger_config:
            trigger_id = await n8n_service.create_trigger(
                name=f"{workflow_config['name']} Trigger",
                event_type=trigger_config.get('event_type', 'custom_event'),
                workflow_ids=[workflow_id],
                conditions=trigger_config.get('conditions', {})
            )

            return AgentResult(
                success=True,
                data={
                    "workflow_id": workflow_id,
                    "trigger_id": trigger_id,
                    "action": "created_workflow_with_trigger",
                    "details": workflow_config
                },
                cost=0.03,
                metadata={"action": "create_workflow_with_trigger"}
            )

        return AgentResult(
            success=True,
            data={
                "workflow_id": workflow_id,
                "action": "created_workflow",
                "details": workflow_config
            },
            cost=0.02,
            metadata={"action": "create_workflow"}
        )

    async def _handle_template_task(self, task: str, context: AgentContext) -> AgentResult:
        """Handle workflow template tasks"""
        task_lower = task.lower()

        # Determine which template to use
        template_name = None
        if 'user' in task_lower and 'onboard' in task_lower:
            template_name = 'user_onboarding'
        elif 'data' in task_lower and 'sync' in task_lower:
            template_name = 'data_sync'
        elif 'error' in task_lower or 'monitor' in task_lower:
            template_name = 'error_monitoring'
        elif 'api' in task_lower:
            template_name = 'api_integration'
        elif 'notification' in task_lower or 'alert' in task_lower:
            template_name = 'notification_system'

        if not template_name or template_name not in self.workflow_templates:
            return AgentResult(
                success=False,
                data={"error": "Could not determine appropriate template", "available_templates": list(self.workflow_templates.keys())},
                cost=0.01,
                metadata={"action": "template_selection_failed"}
            )

        template = self.workflow_templates[template_name]

        # Customize template based on task requirements
        customized_config = self._customize_template(template, task)

        n8n_service = await get_n8n_service()

        workflow_id = await n8n_service.create_workflow(
            name=customized_config['name'],
            description=customized_config['description'],
            webhook_url=customized_config.get('webhook_url', 'https://your-n8n-instance.com/webhook/template_based'),
            webhook_method=customized_config.get('method', 'POST'),
            headers=customized_config.get('headers', {})
        )

        return AgentResult(
            success=True,
            data={
                "workflow_id": workflow_id,
                "template_used": template_name,
                "action": "created_workflow_from_template",
                "details": customized_config
            },
            cost=0.025,
            metadata={"action": "create_workflow_from_template", "template": template_name}
        )

    async def _handle_testing_task(self, task: str, context: AgentContext) -> AgentResult:
        """Handle workflow testing tasks"""
        n8n_service = await get_n8n_service()

        workflows = n8n_service.get_workflows()
        test_results = []

        for workflow in workflows[:5]:  # Test up to 5 workflows
            try:
                result = await n8n_service.test_workflow(workflow['id'])
                test_results.append({
                    "workflow_id": workflow['id'],
                    "name": workflow['name'],
                    "test_result": result.get('status'),
                    "execution_time": result.get('response_time'),
                    "correlation_id": result.get('correlation_id')
                })
            except Exception as e:
                test_results.append({
                    "workflow_id": workflow['id'],
                    "name": workflow['name'],
                    "test_result": "error",
                    "error": str(e)
                })

        # Analyze test results
        successful_tests = len([r for r in test_results if r['test_result'] == 'success'])
        total_tests = len(test_results)
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0

        return AgentResult(
            success=True,
            data={
                "test_results": test_results,
                "summary": {
                    "total_tests": total_tests,
                    "successful_tests": successful_tests,
                    "failed_tests": total_tests - successful_tests,
                    "success_rate": success_rate
                },
                "recommendations": self._generate_test_recommendations(test_results)
            },
            cost=0.03,
            metadata={"action": "workflow_testing"}
        )

    async def _handle_optimization_task(self, task: str, context: AgentContext) -> AgentResult:
        """Handle workflow optimization tasks"""
        n8n_service = await get_n8n_service()

        workflows = n8n_service.get_workflows()
        optimization_recommendations = []

        for workflow in workflows:
            issues = []

            # Check success rate
            if workflow['trigger_count'] > 0:
                success_rate = workflow['success_count'] / workflow['trigger_count']
                if success_rate < 0.9:
                    issues.append({
                        "type": "low_success_rate",
                        "severity": "high",
                        "description": f"Success rate is {success_rate*100:.1f}%",
                        "recommendation": "Add comprehensive error handling and retry logic"
                    })

            # Check for workflows with no executions
            if workflow['trigger_count'] == 0:
                issues.append({
                    "type": "no_executions",
                    "severity": "medium",
                    "description": "Workflow has never been executed",
                    "recommendation": "Test the workflow and verify trigger configuration"
                })

            # Check for high failure rates in recent executions
            recent_failures = workflow.get('recent_failures', 0)  # Mock data
            if recent_failures > 5:
                issues.append({
                    "type": "high_failure_rate",
                    "severity": "high",
                    "description": f"{recent_failures} recent failures detected",
                    "recommendation": "Review error logs and implement circuit breaker pattern"
                })

            if issues:
                optimization_recommendations.append({
                    "workflow_id": workflow['id'],
                    "workflow_name": workflow['name'],
                    "issues": issues,
                    "priority_score": sum(3 if issue['severity'] == 'high' else 1 if issue['severity'] == 'medium' else 0 for issue in issues)
                })

        # Sort by priority
        optimization_recommendations.sort(key=lambda x: x['priority_score'], reverse=True)

        return AgentResult(
            success=True,
            data={
                "optimization_recommendations": optimization_recommendations,
                "summary": {
                    "workflows_analyzed": len(workflows),
                    "workflows_needing_attention": len(optimization_recommendations),
                    "high_priority_issues": len([r for r in optimization_recommendations if r['priority_score'] >= 3])
                }
            },
            cost=0.03,
            metadata={"action": "workflow_optimization"}
        )

    async def _handle_monitoring_task(self, task: str, context: AgentContext) -> AgentResult:
        """Handle workflow monitoring tasks"""
        n8n_service = await get_n8n_service()

        workflows = n8n_service.get_workflows()
        triggers = n8n_service.get_triggers()

        monitoring_data = {
            "workflow_health": {
                "total_workflows": len(workflows),
                "active_workflows": len([w for w in workflows if w['active']]),
                "inactive_workflows": len([w for w in workflows if not w['active']]),
                "workflows_with_errors": len([w for w in workflows if w['failure_count'] > 0]),
                "average_success_rate": sum(
                    (w['success_count'] / max(w['trigger_count'], 1) * 100) for w in workflows
                ) / max(len(workflows), 1)
            },
            "trigger_status": {
                "total_triggers": len(triggers),
                "active_triggers": len([t for t in triggers if t['active']]),
                "inactive_triggers": len([t for t in triggers if not t['active']])
            },
            "performance_metrics": {
                "total_executions": sum(w['trigger_count'] for w in workflows),
                "successful_executions": sum(w['success_count'] for w in workflows),
                "failed_executions": sum(w['failure_count'] for w in workflows),
                "overall_success_rate": sum(w['success_count'] for w in workflows) /
                                     max(sum(w['trigger_count'] for w in workflows), 1) * 100
            },
            "alerts": self._generate_monitoring_alerts(workflows, triggers)
        }

        return AgentResult(
            success=True,
            data=monitoring_data,
            cost=0.02,
            metadata={"action": "workflow_monitoring"}
        )

    async def _handle_maintenance_task(self, task: str, context: AgentContext) -> AgentResult:
        """Handle workflow maintenance tasks"""
        n8n_service = await get_n8n_service()

        maintenance_actions = []

        # Check for workflows that need updates
        workflows = n8n_service.get_workflows()

        for workflow in workflows:
            actions = []

            # Check if workflow is outdated (mock logic)
            days_since_creation = (datetime.utcnow() - workflow['created_at']).days
            if days_since_creation > 30 and workflow['trigger_count'] == 0:
                actions.append({
                    "action": "review_unused_workflow",
                    "description": "Workflow created over 30 days ago but never executed",
                    "recommendation": "Review and either activate or remove the workflow"
                })

            # Check for workflows with high error rates
            if workflow['trigger_count'] > 10:
                error_rate = workflow['failure_count'] / workflow['trigger_count']
                if error_rate > 0.2:
                    actions.append({
                        "action": "fix_high_error_rate",
                        "description": f"Error rate of {error_rate*100:.1f}% is above acceptable threshold",
                        "recommendation": "Review error logs and implement better error handling"
                    })

            # Check for missing documentation
            if not workflow.get('description') or len(workflow['description']) < 10:
                actions.append({
                    "action": "add_documentation",
                    "description": "Workflow lacks proper documentation",
                    "recommendation": "Add comprehensive description and usage instructions"
                })

            if actions:
                maintenance_actions.append({
                    "workflow_id": workflow['id'],
                    "workflow_name": workflow['name'],
                    "maintenance_actions": actions
                })

        return AgentResult(
            success=True,
            data={
                "maintenance_actions": maintenance_actions,
                "summary": {
                    "workflows_reviewed": len(workflows),
                    "workflows_needing_maintenance": len(maintenance_actions),
                    "total_actions_required": sum(len(w['maintenance_actions']) for w in maintenance_actions)
                }
            },
            cost=0.025,
            metadata={"action": "workflow_maintenance"}
        )

    async def _handle_general_n8n_task(self, task: str, context: AgentContext) -> AgentResult:
        """Handle general n8n tasks"""
        n8n_service = await get_n8n_service()

        # Provide comprehensive n8n ecosystem overview
        workflows = n8n_service.get_workflows()
        triggers = n8n_service.get_triggers()

        ecosystem_overview = {
            "n8n_ecosystem_status": {
                "workflows": {
                    "total": len(workflows),
                    "active": len([w for w in workflows if w['active']]),
                    "inactive": len([w for w in workflows if not w['active']]),
                    "with_errors": len([w for w in workflows if w['failure_count'] > 0])
                },
                "triggers": {
                    "total": len(triggers),
                    "active": len([t for t in triggers if t['active']]),
                    "inactive": len([t for t in triggers if not t['active']])
                },
                "performance": {
                    "total_executions": sum(w['trigger_count'] for w in workflows),
                    "success_rate": sum(w['success_count'] for w in workflows) /
                                  max(sum(w['trigger_count'] for w in workflows), 1) * 100,
                    "average_executions_per_workflow": sum(w['trigger_count'] for w in workflows) / max(len(workflows), 1)
                }
            },
            "available_templates": list(self.workflow_templates.keys()),
            "capabilities": [
                "Automated workflow creation",
                "Template-based workflow generation",
                "Workflow testing and validation",
                "Performance monitoring and optimization",
                "Error handling and recovery",
                "Integration with external services",
                "Real-time workflow execution monitoring"
            ],
            "best_practices": [
                "Always include error handling in workflows",
                "Use descriptive names for nodes and connections",
                "Implement proper logging and monitoring",
                "Test workflows thoroughly before production use",
                "Document workflow purpose and usage",
                "Use environment variables for sensitive data",
                "Implement rate limiting for external API calls"
            ],
            "next_steps": [
                "Review existing workflows for optimization opportunities",
                "Implement comprehensive monitoring and alerting",
                "Create workflow templates for common use cases",
                "Establish regular maintenance and review processes",
                "Consider implementing workflow versioning"
            ]
        }

        return AgentResult(
            success=True,
            data=ecosystem_overview,
            cost=0.02,
            metadata={"action": "n8n_ecosystem_overview"}
        )

    def _analyze_workflow_requirements(self, task: str) -> Dict[str, Any]:
        """Analyze task description to determine workflow requirements"""
        task_lower = task.lower()

        config = {
            'name': f'Workflow_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'description': 'Auto-generated workflow',
            'method': 'POST',
            'headers': {},
            'trigger': None
        }

        # Determine workflow type and configuration
        if 'user' in task_lower and 'welcome' in task_lower:
            config.update({
                'name': 'User Welcome Workflow',
                'description': 'Sends welcome email and sets up user account',
                'trigger': {
                    'event_type': 'user_created',
                    'conditions': {}
                }
            })
        elif 'notification' in task_lower or 'alert' in task_lower:
            config.update({
                'name': 'Notification Workflow',
                'description': 'Handles multi-channel notifications',
                'trigger': {
                    'event_type': 'notification_required',
                    'conditions': {}
                }
            })
        elif 'data' in task_lower and 'sync' in task_lower:
            config.update({
                'name': 'Data Sync Workflow',
                'description': 'Synchronizes data between systems',
                'trigger': {
                    'event_type': 'data_updated',
                    'conditions': {}
                }
            })

        return config

    def _customize_template(self, template: Dict[str, Any], task: str) -> Dict[str, Any]:
        """Customize a workflow template based on task requirements"""
        customized = template.copy()

        # Add task-specific customizations
        task_lower = task.lower()

        if 'email' in task_lower:
            customized['name'] = 'Email Notification Workflow'
            customized['description'] = 'Automated email notifications with templates'
        elif 'slack' in task_lower:
            customized['name'] = 'Slack Integration Workflow'
            customized['description'] = 'Slack notifications and channel management'
        elif 'database' in task_lower or 'db' in task_lower:
            customized['name'] = 'Database Operation Workflow'
            customized['description'] = 'Database operations with error handling'

        return customized

    def _generate_test_recommendations(self, test_results: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []

        failed_tests = [r for r in test_results if r.get('test_result') != 'success']
        if failed_tests:
            recommendations.append(f"Fix {len(failed_tests)} failing workflows")

        slow_tests = [r for r in test_results if r.get('execution_time', 0) > 10]
        if slow_tests:
            recommendations.append("Optimize slow-running workflows")

        untested_workflows = [r for r in test_results if r.get('test_result') == 'error']
        if untested_workflows:
            recommendations.append("Review workflows that couldn't be tested")

        if not recommendations:
            recommendations.append("All workflows are functioning well")

        return recommendations

    def _generate_monitoring_alerts(self, workflows: List[Dict[str, Any]], triggers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate monitoring alerts based on workflow and trigger status"""
        alerts = []

        # Check for workflows with high error rates
        for workflow in workflows:
            if workflow['trigger_count'] > 5:
                error_rate = workflow['failure_count'] / workflow['trigger_count']
                if error_rate > 0.3:
                    alerts.append({
                        'type': 'high_error_rate',
                        'severity': 'high',
                        'workflow_id': workflow['id'],
                        'message': f"Workflow '{workflow['name']}' has {error_rate*100:.1f}% error rate"
                    })

        # Check for inactive triggers that should be active
        inactive_triggers = [t for t in triggers if not t['active']]
        if inactive_triggers:
            alerts.append({
                'type': 'inactive_triggers',
                'severity': 'medium',
                'count': len(inactive_triggers),
                'message': f"{len(inactive_triggers)} triggers are inactive"
            })

        # Check for workflows with no recent executions
        stale_workflows = []
        for workflow in workflows:
            if workflow['last_triggered']:
                days_since_execution = (datetime.utcnow() - datetime.fromisoformat(workflow['last_triggered'])).days
                if days_since_execution > 7:
                    stale_workflows.append(workflow['name'])

        if stale_workflows:
            alerts.append({
                'type': 'stale_workflows',
                'severity': 'low',
                'workflows': stale_workflows,
                'message': f"{len(stale_workflows)} workflows haven't executed in over a week"
            })

        return alerts
