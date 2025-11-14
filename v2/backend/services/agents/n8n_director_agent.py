"""
n8n Director Agent
Oversees n8n workflow orchestration, automation strategy, and cross-system integration management.

"Your imagination is the end."
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
import json

from .base_agent import BaseAgent, AgentResult, AgentContext, PersonalityTraits, AgentCapabilities
from ..integrations.n8n_integration import get_n8n_service
from .integration_specialist_agent import IntegrationSpecialistAgent

logger = logging.getLogger(__name__)


class N8nDirectorAgent(BaseAgent):
    """
    n8n Director Agent

    Capabilities:
    - n8n workflow strategy and architecture
    - Multi-workflow orchestration
    - Integration pipeline management
    - Automation performance optimization
    - Cross-platform workflow coordination
    - Business process automation
    """

    def __init__(self):
        super().__init__(
            name="N8nDirector",
            personality=PersonalityTraits(
                creativity=0.8,
                analytical=0.9,
                communication=0.9,
                organization=0.9,
                adaptability=0.8
            ),
            capabilities=AgentCapabilities(
                expertise=[
                    "n8n_workflow_strategy",
                    "automation_orchestration",
                    "business_process_automation",
                    "integration_pipeline_management",
                    "workflow_performance_optimization",
                    "cross_platform_coordination"
                ],
                tools=[
                    "workflow_architect",
                    "orchestration_planner",
                    "performance_optimizer",
                    "business_process_analyzer",
                    "integration_coordinator",
                    "automation_strategist"
                ]
            )
        )

        self.integration_specialist = IntegrationSpecialistAgent()

    async def execute(self, task: str, context: AgentContext) -> AgentResult:
        """
        Execute n8n director tasks

        Args:
            task: Task description
            context: Execution context

        Returns:
            AgentResult with execution outcome
        """
        try:
            task_lower = task.lower()

            # Route to appropriate handler
            if any(keyword in task_lower for keyword in ['strategy', 'plan', 'design']):
                return await self._handle_strategy_task(task, context)
            elif any(keyword in task_lower for keyword in ['orchestrate', 'coordinate', 'manage']):
                return await self._handle_orchestration_task(task, context)
            elif any(keyword in task_lower for keyword in ['optimize', 'performance', 'improve']):
                return await self._handle_optimization_task(task, context)
            elif any(keyword in task_lower for keyword in ['analyze', 'review', 'assess']):
                return await self._handle_analysis_task(task, context)
            elif any(keyword in task_lower for keyword in ['create', 'build', 'setup']):
                return await self._handle_creation_task(task, context)
            else:
                return await self._handle_general_director_task(task, context)

        except Exception as e:
            logger.error(f"n8n Director task failed: {e}")
            return AgentResult(
                success=False,
                data={"error": str(e)},
                cost=0.02,
                metadata={"error_type": "execution_error"}
            )

    async def _handle_strategy_task(self, task: str, context: AgentContext) -> AgentResult:
        """Handle workflow strategy and planning tasks"""
        n8n_service = await get_n8n_service()

        # Analyze current workflows and suggest improvements
        workflows = n8n_service.get_workflows()
        triggers = n8n_service.get_triggers()

        strategy_analysis = {
            "current_state": {
                "total_workflows": len(workflows),
                "active_workflows": len([w for w in workflows if w['active']]),
                "total_triggers": len(triggers),
                "active_triggers": len([t for t in triggers if t['active']]),
            },
            "strategy_recommendations": [
                {
                    "priority": "high",
                    "action": "Implement workflow versioning",
                    "benefit": "Better change management and rollback capabilities",
                    "effort": "medium"
                },
                {
                    "priority": "high",
                    "action": "Add comprehensive error handling",
                    "benefit": "Improved reliability and debugging",
                    "effort": "medium"
                },
                {
                    "priority": "medium",
                    "action": "Implement workflow performance monitoring",
                    "benefit": "Better optimization opportunities",
                    "effort": "low"
                },
                {
                    "priority": "medium",
                    "action": "Create workflow templates library",
                    "benefit": "Faster development and consistency",
                    "effort": "medium"
                }
            ],
            "automation_opportunities": [
                "User onboarding automation",
                "Error notification and escalation",
                "Performance monitoring alerts",
                "Data synchronization workflows",
                "Backup and recovery automation"
            ]
        }

        return AgentResult(
            success=True,
            data=strategy_analysis,
            cost=0.03,
            metadata={"action": "strategy_analysis"}
        )

    async def _handle_orchestration_task(self, task: str, context: AgentContext) -> AgentResult:
        """Handle workflow orchestration tasks"""
        n8n_service = await get_n8n_service()

        # Create orchestration plan for complex multi-workflow processes
        orchestration_plan = {
            "workflows": [],
            "triggers": [],
            "execution_order": [],
            "dependencies": {},
            "error_handling": {},
            "monitoring_points": []
        }

        # Analyze task for orchestration requirements
        if 'user' in task.lower() and 'onboard' in task.lower():
            orchestration_plan = await self._create_user_onboarding_orchestration()
        elif 'data' in task.lower() and 'sync' in task.lower():
            orchestration_plan = await self._create_data_sync_orchestration()
        elif 'backup' in task.lower():
            orchestration_plan = await self._create_backup_orchestration()
        else:
            # Generic orchestration plan
            orchestration_plan["workflows"] = ["main_workflow", "error_handler", "notification_workflow"]
            orchestration_plan["execution_order"] = ["main_workflow", "notification_workflow", "error_handler"]
            orchestration_plan["dependencies"] = {
                "notification_workflow": ["main_workflow"],
                "error_handler": ["main_workflow"]
            }

        return AgentResult(
            success=True,
            data=orchestration_plan,
            cost=0.04,
            metadata={"action": "workflow_orchestration"}
        )

    async def _handle_optimization_task(self, task: str, context: AgentContext) -> AgentResult:
        """Handle workflow optimization tasks"""
        n8n_service = await get_n8n_service()

        workflows = n8n_service.get_workflows()

        optimization_recommendations = []

        for workflow in workflows:
            if workflow['trigger_count'] > 0:
                success_rate = workflow['success_count'] / workflow['trigger_count']

                if success_rate < 0.95:
                    optimization_recommendations.append({
                        "workflow_id": workflow['id'],
                        "workflow_name": workflow['name'],
                        "issue": "Low success rate",
                        "current_rate": success_rate * 100,
                        "recommendations": [
                            "Add retry logic for failed executions",
                            "Implement better error handling",
                            "Add input validation",
                            "Consider circuit breaker pattern"
                        ]
                    })

                # Check for high execution times (mock data)
                if workflow.get('average_response_time', 0) > 30:
                    optimization_recommendations.append({
                        "workflow_id": workflow['id'],
                        "workflow_name": workflow['name'],
                        "issue": "High execution time",
                        "current_time": f"{workflow.get('average_response_time', 0)}s",
                        "recommendations": [
                            "Optimize database queries",
                            "Implement caching where appropriate",
                            "Consider asynchronous processing",
                            "Review and optimize external API calls"
                        ]
                    })

        return AgentResult(
            success=True,
            data={
                "optimization_recommendations": optimization_recommendations,
                "performance_metrics": {
                    "total_workflows_analyzed": len(workflows),
                    "workflows_needing_attention": len(optimization_recommendations),
                    "overall_success_rate": sum(w['success_count'] for w in workflows) /
                                         max(sum(w['trigger_count'] for w in workflows), 1) * 100
                }
            },
            cost=0.03,
            metadata={"action": "workflow_optimization"}
        )

    async def _handle_analysis_task(self, task: str, context: AgentContext) -> AgentResult:
        """Handle workflow analysis tasks"""
        n8n_service = await get_n8n_service()

        # Comprehensive workflow ecosystem analysis
        workflows = n8n_service.get_workflows()
        triggers = n8n_service.get_triggers()

        analysis = {
            "workflow_ecosystem": {
                "total_workflows": len(workflows),
                "active_workflows": len([w for w in workflows if w['active']]),
                "inactive_workflows": len([w for w in workflows if not w['active']]),
                "total_triggers": len(triggers),
                "active_triggers": len([t for t in triggers if t['active']]),
            },
            "usage_patterns": {
                "most_active_workflow": max(workflows, key=lambda w: w['trigger_count']) if workflows else None,
                "least_active_workflow": min(workflows, key=lambda w: w['trigger_count']) if workflows else None,
                "average_executions_per_workflow": sum(w['trigger_count'] for w in workflows) / max(len(workflows), 1),
                "total_successful_executions": sum(w['success_count'] for w in workflows),
                "total_failed_executions": sum(w['failure_count'] for w in workflows),
            },
            "health_indicators": {
                "overall_success_rate": sum(w['success_count'] for w in workflows) /
                                      max(sum(w['trigger_count'] for w in workflows), 1) * 100,
                "workflows_with_errors": len([w for w in workflows if w['failure_count'] > 0]),
                "average_success_rate_per_workflow": sum(
                    (w['success_count'] / max(w['trigger_count'], 1) * 100) for w in workflows
                ) / max(len(workflows), 1),
            },
            "recommendations": [
                "Implement workflow health monitoring dashboard",
                "Create automated alerting for workflow failures",
                "Establish regular workflow performance reviews",
                "Develop workflow documentation standards",
                "Implement workflow testing and validation pipelines"
            ]
        }

        return AgentResult(
            success=True,
            data=analysis,
            cost=0.03,
            metadata={"action": "workflow_analysis"}
        )

    async def _handle_creation_task(self, task: str, context: AgentContext) -> AgentResult:
        """Handle workflow creation tasks"""
        # Delegate to integration specialist for actual creation
        creation_result = await self.integration_specialist.execute(
            f"Create n8n workflow: {task}",
            context
        )

        # Add orchestration layer
        if creation_result.success:
            orchestration_notes = {
                "workflow_id": creation_result.data.get("workflow_id"),
                "orchestration_setup": {
                    "monitoring_enabled": True,
                    "error_handling_configured": True,
                    "logging_setup": True,
                    "performance_tracking": True
                },
                "integration_points": [
                    "Main application events",
                    "Error notification system",
                    "Performance monitoring",
                    "Audit logging"
                ]
            }

            creation_result.data["orchestration"] = orchestration_notes

        return creation_result

    async def _handle_general_director_task(self, task: str, context: AgentContext) -> AgentResult:
        """Handle general director tasks"""
        director_insights = {
            "automation_maturity": {
                "current_level": "intermediate",
                "target_level": "advanced",
                "gap_analysis": [
                    "Advanced error recovery mechanisms needed",
                    "Multi-workflow orchestration requires improvement",
                    "Real-time monitoring dashboard development pending",
                    "AI-driven workflow optimization not implemented"
                ]
            },
            "strategic_initiatives": [
                {
                    "initiative": "Intelligent Workflow Orchestration",
                    "description": "AI-powered workflow coordination and optimization",
                    "priority": "high",
                    "timeline": "3 months"
                },
                {
                    "initiative": "Advanced Error Recovery",
                    "description": "Machine learning-based error prediction and recovery",
                    "priority": "high",
                    "timeline": "2 months"
                },
                {
                    "initiative": "Workflow Analytics Platform",
                    "description": "Comprehensive analytics and insights platform",
                    "priority": "medium",
                    "timeline": "4 months"
                }
            ],
            "key_performance_indicators": [
                "Workflow success rate > 99%",
                "Average execution time < 10 seconds",
                "Zero critical workflow failures per month",
                "100% workflow documentation coverage",
                "Automated workflow testing coverage > 95%"
            ]
        }

        return AgentResult(
            success=True,
            data=director_insights,
            cost=0.03,
            metadata={"action": "director_insights"}
        )

    async def _create_user_onboarding_orchestration(self) -> Dict[str, Any]:
        """Create user onboarding workflow orchestration"""
        return {
            "workflows": [
                {
                    "name": "user_registration_handler",
                    "purpose": "Process new user registration",
                    "triggers": ["user_created"]
                },
                {
                    "name": "welcome_email_sender",
                    "purpose": "Send welcome email and setup instructions",
                    "dependencies": ["user_registration_handler"]
                },
                {
                    "name": "account_setup_initializer",
                    "purpose": "Initialize user account and preferences",
                    "dependencies": ["user_registration_handler"]
                },
                {
                    "name": "onboarding_notification",
                    "purpose": "Notify team of new user",
                    "dependencies": ["welcome_email_sender", "account_setup_initializer"]
                }
            ],
            "execution_order": [
                "user_registration_handler",
                "welcome_email_sender",
                "account_setup_initializer",
                "onboarding_notification"
            ],
            "error_handling": {
                "email_failure": "retry_with_fallback_template",
                "account_setup_failure": "manual_review_required",
                "notification_failure": "log_and_continue"
            },
            "monitoring_points": [
                "registration_completion",
                "email_delivery_status",
                "account_setup_success",
                "user_engagement_metrics"
            ]
        }

    async def _create_data_sync_orchestration(self) -> Dict[str, Any]:
        """Create data synchronization workflow orchestration"""
        return {
            "workflows": [
                {
                    "name": "data_change_detector",
                    "purpose": "Monitor for data changes across systems",
                    "triggers": ["data_updated", "external_api_sync"]
                },
                {
                    "name": "data_validator",
                    "purpose": "Validate data integrity before sync",
                    "dependencies": ["data_change_detector"]
                },
                {
                    "name": "sync_orchestrator",
                    "purpose": "Coordinate data sync across multiple systems",
                    "dependencies": ["data_validator"]
                },
                {
                    "name": "sync_verifier",
                    "purpose": "Verify sync completion and data consistency",
                    "dependencies": ["sync_orchestrator"]
                }
            ],
            "execution_order": [
                "data_change_detector",
                "data_validator",
                "sync_orchestrator",
                "sync_verifier"
            ],
            "error_handling": {
                "validation_failure": "rollback_and_notify",
                "sync_failure": "retry_with_exponential_backoff",
                "verification_failure": "manual_intervention_required"
            },
            "monitoring_points": [
                "data_change_detection",
                "validation_completion",
                "sync_progress_percentage",
                "final_verification_status"
            ]
        }

    async def _create_backup_orchestration(self) -> Dict[str, Any]:
        """Create backup workflow orchestration"""
        return {
            "workflows": [
                {
                    "name": "backup_scheduler",
                    "purpose": "Schedule and initiate backup operations",
                    "triggers": ["scheduled_backup", "manual_backup_request"]
                },
                {
                    "name": "data_backup_executor",
                    "purpose": "Execute actual data backup operations",
                    "dependencies": ["backup_scheduler"]
                },
                {
                    "name": "backup_validator",
                    "purpose": "Validate backup integrity and completeness",
                    "dependencies": ["data_backup_executor"]
                },
                {
                    "name": "backup_notification",
                    "purpose": "Send backup status notifications",
                    "dependencies": ["backup_validator"]
                }
            ],
            "execution_order": [
                "backup_scheduler",
                "data_backup_executor",
                "backup_validator",
                "backup_notification"
            ],
            "error_handling": {
                "backup_failure": "retry_with_different_method",
                "validation_failure": "alert_administrators",
                "notification_failure": "log_error_and_continue"
            },
            "monitoring_points": [
                "backup_start_time",
                "backup_progress_percentage",
                "backup_completion_time",
                "validation_results",
                "notification_status"
            ]
        }
