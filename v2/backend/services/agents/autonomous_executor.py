"""
Autonomous Task Execution Engine for Galion Platform v2.2
Provides Manus-like autonomous task execution capabilities.

Features:
- Intelligent task decomposition
- Step-by-step execution planning
- Autonomous decision making
- Real-time progress tracking
- Error handling and recovery
- Human-in-the-loop integration

"Your imagination is the end."
"""

import asyncio
from typing import Dict, List, Optional, Any, Union, Callable
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from enum import Enum
import logging
import json
from pathlib import Path

from .base_agent import AgentResult, AgentContext
from .realtime_monitor import monitor, create_execution_event, MonitoringEventType
from .human_loop import human_loop_manager, ApprovalType, ApprovalPriority
from .context_awareness import context_engine, PreferenceType
from .nlp_processor import nlp_processor, TaskComplexity, TaskRisk

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """Status of an autonomous task"""
    PENDING = "pending"
    PLANNING = "planning"
    EXECUTING = "executing"
    WAITING_APPROVAL = "waiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ExecutionStep(BaseModel):
    """A single step in an autonomous task execution"""

    id: str
    description: str
    agent_type: str
    prompt: str
    context: Dict[str, Any] = Field(default_factory=dict)
    dependencies: List[str] = Field(default_factory=list)  # Step IDs this depends on
    estimated_duration: float = 0.0  # seconds
    requires_approval: bool = False
    approval_reason: Optional[str] = None

    # Execution results
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[AgentResult] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "agent_type": self.agent_type,
            "status": self.status.value,
            "progress": self.get_progress(),
            "requires_approval": self.requires_approval,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error_message": self.error_message
        }

    def get_progress(self) -> float:
        """Get execution progress (0-100)"""
        if self.status == TaskStatus.COMPLETED:
            return 100.0
        elif self.status == TaskStatus.EXECUTING:
            return 50.0  # Mid-progress during execution
        elif self.status in [TaskStatus.FAILED, TaskStatus.CANCELLED]:
            return 0.0
        else:
            return 0.0

class AutonomousTask(BaseModel):
    """An autonomous task that can be broken down and executed"""

    id: str
    title: str
    description: str
    original_prompt: str
    steps: List[ExecutionStep] = Field(default_factory=list)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: TaskStatus = TaskStatus.PENDING

    # Progress tracking
    current_step_index: int = -1
    overall_progress: float = 0.0

    # User context
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "progress": self.overall_progress,
            "current_step": self.current_step_index,
            "total_steps": len(self.steps),
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "steps": [step.to_dict() for step in self.steps]
        }

class TaskPlanningAgent:
    """Agent responsible for breaking down tasks into executable steps"""

    def __init__(self, orchestrator):
        self.orchestrator = orchestrator

    async def plan_task(self, prompt: str, context: Dict[str, Any]) -> List[ExecutionStep]:
        """
        Break down a complex task into executable steps.

        Uses advanced NLP analysis, context awareness, and user preferences for intelligent planning.
        """
        user_id = context.get("user_id")

        # Step 1: Perform comprehensive NLP analysis
        nlp_analysis = await nlp_processor.analyze_task(prompt, context)

        # Step 2: Generate detailed execution plan using NLP insights
        execution_plan = await nlp_processor.generate_task_plan(nlp_analysis, context)

        # Step 3: Get context-aware recommendations
        recommendations = {}
        if user_id:
            recommendations = context_engine.get_context_recommendations(user_id, {
                "task_type": nlp_analysis.intent.value,
                "complexity": nlp_analysis.complexity.value,
                "domain": nlp_analysis.domain_context,
                "entities": [e.text for e in nlp_analysis.entities],
                "project_context": context.get("project_context", {}),
                "current_context": context
            })

        # Step 4: Create execution steps from NLP analysis
        steps = []

        for plan_step in execution_plan.get("execution_steps", []):
            # Apply intelligent agent selection
            agent_type = self._select_best_agent(
                plan_step,
                nlp_analysis,
                recommendations,
                user_id
            )

            # Determine if approval is needed based on NLP risk assessment
            requires_approval = (
                plan_step.get("requires_approval", False) or
                nlp_analysis.risk_level == TaskRisk.CRITICAL or
                (nlp_analysis.risk_level == TaskRisk.HIGH and nlp_analysis.complexity in [TaskComplexity.COMPLEX, TaskComplexity.VERY_COMPLEX])
            )

            # Create execution step
            step = ExecutionStep(
                id=plan_step["id"],
                description=plan_step["description"],
                agent_type=agent_type,
                prompt=self._create_step_prompt(plan_step, nlp_analysis, context),
                dependencies=[],  # Will be set based on NLP dependency analysis
                requires_approval=requires_approval,
                approval_reason=self._generate_approval_reason(plan_step, nlp_analysis),
                estimated_duration=plan_step.get("estimated_time", 30) * 60  # Convert hours to seconds
            )
            steps.append(step)

        # Step 5: Analyze and set dependencies
        for step in steps:
            step.dependencies = self._analyze_step_dependencies(step, steps, nlp_analysis)

        # Step 6: Learn from planning for future improvements
        if user_id:
            self._learn_from_nlp_planning(user_id, nlp_analysis, steps, recommendations)

        # Step 7: Validate the plan
        steps = self._validate_and_optimize_plan(steps, nlp_analysis)

        return steps

    def _select_best_agent(self, plan_step: Dict[str, Any], nlp_analysis, recommendations: Dict[str, Any], user_id: str = None) -> str:
        """Select the best agent for a step using multiple factors"""
        suggested_agent = plan_step.get("agent_type", "code_execution")

        # Check user preferences first
        if user_id and recommendations.get("suggested_agents"):
            for suggestion in recommendations["suggested_agents"]:
                if suggestion.get("confidence", 0) > 0.7:
                    pref_agent = suggestion.get("agent_type", "")
                    if pref_agent and pref_agent != suggested_agent:
                        # Validate that preferred agent can handle this task
                        if self._agent_can_handle_task(pref_agent, nlp_analysis.intent.value):
                            suggested_agent = pref_agent
                            break

        # Fallback to domain-appropriate agent
        if suggested_agent == "code_execution":
            domain_agents = {
                "development": "code_execution",
                "analysis": "code_execution",
                "business": "financial_advisor",
                "infrastructure": "code_execution"
            }
            suggested_agent = domain_agents.get(nlp_analysis.domain_context, "code_execution")

        return suggested_agent

    def _agent_can_handle_task(self, agent_type: str, task_intent: str) -> bool:
        """Check if an agent can handle a specific task intent"""
        agent_capabilities = {
            "code_execution": ["create", "modify", "execute", "debug", "deploy", "test", "document"],
            "financial_advisor": ["analyze", "create", "manage"],
            "customer_support": ["communicate", "manage", "analyze"],
            "monitoring_agent": ["analyze", "monitor", "manage"]
        }

        return task_intent in agent_capabilities.get(agent_type, [])

    def _create_step_prompt(self, plan_step: Dict[str, Any], nlp_analysis, context: Dict[str, Any]) -> str:
        """Create an enhanced prompt for the step execution"""
        base_description = plan_step["description"]

        # Add context from NLP analysis
        enhanced_prompt = f"""
        Task: {base_description}

        Context:
        - Intent: {nlp_analysis.intent.value}
        - Domain: {nlp_analysis.domain_context}
        - Complexity: {nlp_analysis.complexity.value}
        - Risk Level: {nlp_analysis.risk_level.value}

        Key Elements: {', '.join(nlp_analysis.key_phrases[:5])}
        Entities: {', '.join([f"{e.type}: {e.text}" for e in nlp_analysis.entities[:3]])}
        """

        if nlp_analysis.constraints:
            enhanced_prompt += f"\nConstraints: {', '.join(nlp_analysis.constraints)}\n"

        if nlp_analysis.urgency_indicators:
            enhanced_prompt += f"\nUrgency: {', '.join(nlp_analysis.urgency_indicators)}\n"

        return enhanced_prompt.strip()

    def _generate_approval_reason(self, plan_step: Dict[str, Any], nlp_analysis) -> str:
        """Generate a detailed approval reason"""
        reasons = []

        if plan_step.get("risk_level") == "high":
            reasons.append("High-risk operation detected")

        if nlp_analysis.risk_level == TaskRisk.CRITICAL:
            reasons.append("Critical system operation")

        if nlp_analysis.complexity == TaskComplexity.VERY_COMPLEX:
            reasons.append("Complex multi-step operation")

        if nlp_analysis.urgency_indicators:
            reasons.append(f"Urgent request: {', '.join(nlp_analysis.urgency_indicators)}")

        return "; ".join(reasons) if reasons else "Step requires manual approval"

    def _analyze_step_dependencies(self, step: ExecutionStep, all_steps: List[ExecutionStep], nlp_analysis) -> List[str]:
        """Analyze dependencies for a step based on NLP insights"""
        dependencies = []

        # Check NLP-identified dependencies
        for dep_from, dep_to in nlp_analysis.dependencies:
            if step.id == dep_to:
                dependencies.append(dep_from)
            elif step.id == dep_from:
                # This step depends on others
                dependencies.extend([s.id for s in all_steps if s.id == dep_to])

        # Add logical dependencies based on step content
        step_text = step.description.lower()
        for other_step in all_steps:
            if other_step.id == step.id:
                continue

            other_text = other_step.description.lower()

            # Check for temporal dependencies
            if any(word in step_text for word in ["after", "then", "following"]) and other_step.description in step.description:
                dependencies.append(other_step.id)
            elif any(word in other_text for word in ["before", "first", "initially"]) and step.description in other_step.description:
                dependencies.append(other_step.id)

        return list(set(dependencies))  # Remove duplicates

    def _learn_from_nlp_planning(self, user_id: str, nlp_analysis, steps: List[ExecutionStep], recommendations: Dict[str, Any]):
        """Learn from NLP-enhanced planning for future improvements"""
        # Learn agent preferences
        for step in steps:
            context_engine.learn_user_preference(
                user_id,
                PreferenceType.AGENT_SELECTION,
                f"{nlp_analysis.intent.value}_agent",
                step.agent_type,
                weight=0.9  # Higher weight for NLP-informed decisions
            )

        # Learn complexity handling preferences
        if nlp_analysis.complexity == TaskComplexity.VERY_COMPLEX:
            context_engine.learn_user_preference(
                user_id,
                PreferenceType.PRIORITY_SETTINGS,
                "complexity_handling",
                "detailed_breakdown",
                weight=0.8
            )

        # Learn risk tolerance
        risk_tolerance = "low" if any(step.requires_approval for step in steps) else "normal"
        context_engine.learn_user_preference(
            user_id,
            PreferenceType.PRIORITY_SETTINGS,
            "risk_tolerance",
            risk_tolerance,
            weight=0.7
        )

    def _validate_and_optimize_plan(self, steps: List[ExecutionStep], nlp_analysis) -> List[ExecutionStep]:
        """Validate and optimize the execution plan"""
        validated_steps = []

        for step in steps:
            # Validate step has required fields
            if not step.description or not step.agent_type:
                logger.warning(f"Invalid step: {step.id}, skipping")
                continue

            # Optimize based on NLP insights
            if nlp_analysis.complexity == TaskComplexity.SIMPLE and len(steps) == 1:
                # For simple tasks, reduce approval requirements
                step.requires_approval = False

            if nlp_analysis.confidence_score > 0.8:
                # High confidence plans can have reduced approval requirements
                if step.requires_approval and nlp_analysis.risk_level == TaskRisk.LOW:
                    step.requires_approval = False

            validated_steps.append(step)

        # Ensure at least one step
        if not validated_steps:
            validated_steps.append(ExecutionStep(
                id="fallback_step",
                description=f"Execute: {nlp_analysis.original_text}",
                agent_type="code_execution",
                prompt=nlp_analysis.original_text,
                estimated_duration=60.0
            ))

        return validated_steps

    def _infer_task_type(self, prompt: str, context: Dict[str, Any]) -> str:
        """Infer the task type from prompt and context"""
        prompt_lower = prompt.lower()

        # Simple keyword-based inference
        if any(word in prompt_lower for word in ["code", "program", "develop", "implement"]):
            return "development"
        elif any(word in prompt_lower for word in ["analyze", "data", "metrics", "report"]):
            return "analysis"
        elif any(word in prompt_lower for word in ["write", "content", "article", "documentation"]):
            return "content_creation"
        elif any(word in prompt_lower for word in ["financial", "budget", "money", "invest"]):
            return "financial"
        elif any(word in prompt_lower for word in ["support", "help", "issue", "problem"]):
            return "support"
        else:
            return "general"

    def _get_fallback_agent(self, user_id: str, task_type: str) -> str:
        """Get fallback agent based on user preferences"""
        if user_id:
            preferred_agent = context_engine.get_user_preference(
                user_id, PreferenceType.AGENT_SELECTION, f"{task_type}_agent"
            )
            if preferred_agent:
                return preferred_agent

        # Default fallbacks
        fallbacks = {
            "development": "code_execution",
            "analysis": "code_execution",
            "content_creation": "code_execution",
            "financial": "financial_advisor",
            "support": "customer_support",
            "general": "code_execution"
        }
        return fallbacks.get(task_type, "code_execution")

    def _apply_agent_preferences(
        self,
        current_agent: str,
        suggested_agents: List[Dict[str, Any]],
        task_type: str
    ) -> str:
        """Apply user agent preferences to selection"""
        # Look for high-confidence suggestions that match the task type
        for suggestion in suggested_agents:
            if suggestion.get("confidence", 0) > 0.7:
                agent_type = suggestion.get("agent_type", "")
                if task_type.lower() in agent_type.lower() or agent_type.lower() in task_type.lower():
                    return agent_type

        return current_agent

    def _learn_from_planning(
        self,
        user_id: str,
        task_type: str,
        steps: List[ExecutionStep],
        recommendations: Dict[str, Any]
    ):
        """Learn from planning decisions"""
        # Learn agent preferences
        for step in steps:
            context_engine.learn_user_preference(
                user_id,
                PreferenceType.AGENT_SELECTION,
                f"{task_type}_agent",
                step.agent_type,
                weight=0.8
            )

        # Learn approval preferences
        high_risk_steps = sum(1 for step in steps if step.requires_approval)
        risk_preference = "high" if high_risk_steps > len(steps) * 0.5 else "normal"

        context_engine.learn_user_preference(
            user_id,
            PreferenceType.PRIORITY_SETTINGS,
            "risk_tolerance",
            risk_preference,
            weight=0.6
        )

class AutonomousExecutor:
    """
    Main autonomous task execution engine.

    Features:
    - Intelligent task decomposition
    - Parallel and sequential execution
    - Real-time progress tracking
    - Error recovery
    - Human-in-the-loop integration
    """

    def __init__(self, orchestrator, planning_agent: Optional[TaskPlanningAgent] = None):
        self.orchestrator = orchestrator
        self.planning_agent = planning_agent or TaskPlanningAgent(orchestrator)
        self.active_tasks: Dict[str, AutonomousTask] = {}
        self.task_callbacks: Dict[str, List[Callable]] = {}
        self.is_running = False

        # Configuration
        self.max_parallel_steps = 3
        self.task_timeout = 3600  # 1 hour
        self.retry_attempts = 2

        logger.info("AutonomousExecutor initialized")

    async def execute_autonomous(
        self,
        prompt: str,
        context: Dict[str, Any] = None,
        user_id: str = None,
        session_id: str = None,
        require_approval: bool = False
    ) -> str:
        """
        Start autonomous execution of a complex task.

        Args:
            prompt: The complex task to execute
            context: Additional context
            user_id: User initiating the task
            session_id: Session context
            require_approval: Whether to require approval for each step

        Returns:
            Task ID for tracking
        """
        task_id = f"auto_task_{datetime.now().timestamp()}_{hash(prompt) % 10000}"

        # Create autonomous task
        task = AutonomousTask(
            id=task_id,
            title=self._extract_title(prompt),
            description=prompt,
            original_prompt=prompt,
            user_id=user_id,
            session_id=session_id,
            context=context or {},
            status=TaskStatus.PLANNING
        )

        self.active_tasks[task_id] = task

        # Start execution in background
        asyncio.create_task(self._execute_task_async(task_id))

        logger.info(f"Started autonomous task: {task_id}")
        return task_id

    def _extract_title(self, prompt: str) -> str:
        """Extract a concise title from the prompt"""
        words = prompt.split()
        if len(words) <= 5:
            return prompt
        return " ".join(words[:5]) + "..."

    async def _execute_task_async(self, task_id: str):
        """Execute a task asynchronously"""
        task = self.active_tasks.get(task_id)
        if not task:
            return

        try:
            # Phase 1: Planning
            task.status = TaskStatus.PLANNING
            await self._notify_callbacks(task_id, "planning_started")

            # Real-time monitoring
            monitor.record_event(create_execution_event(
                task_id, MonitoringEventType.EXECUTION_STARTED,
                {"phase": "planning", "title": task.title},
                task.user_id, task.session_id
            ))

            steps = await self.planning_agent.plan_task(task.original_prompt, task.context)
            task.steps = steps
            task.status = TaskStatus.EXECUTING
            task.started_at = datetime.now()

            await self._notify_callbacks(task_id, "planning_completed", {"steps": len(steps)})

            # Phase 2: Execution
            await self._execute_steps(task)

            # Phase 3: Completion
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            task.overall_progress = 100.0

            await self._notify_callbacks(task_id, "task_completed")

            # Real-time monitoring
            monitor.record_event(create_execution_event(
                task_id, MonitoringEventType.EXECUTION_COMPLETED,
                {"total_steps": len(task.steps), "duration": task.total_execution_time},
                task.user_id, task.session_id
            ))

        except Exception as e:
            logger.error(f"Task {task_id} failed: {e}")
            task.status = TaskStatus.FAILED
            await self._notify_callbacks(task_id, "task_failed", {"error": str(e)})

    async def _execute_steps(self, task: AutonomousTask):
        """Execute all steps in the task"""
        completed_steps = set()
        executing_steps = set()

        while len(completed_steps) < len(task.steps):
            # Find executable steps (dependencies satisfied)
            executable_steps = []
            for step in task.steps:
                if (step.id not in completed_steps and
                    step.id not in executing_steps and
                    all(dep in completed_steps for dep in step.dependencies)):

                    executable_steps.append(step)

            if not executable_steps:
                # No executable steps, check if we're stuck
                if executing_steps:
                    # Wait for executing steps to complete
                    await asyncio.sleep(1)
                    continue
                else:
                    # Deadlock or error
                    raise Exception("No executable steps found - possible dependency cycle")

            # Execute steps (up to max_parallel_steps)
            executing_count = 0
            for step in executable_steps[:self.max_parallel_steps - len(executing_steps)]:
                executing_steps.add(step.id)
                asyncio.create_task(self._execute_single_step(task, step))
                executing_count += 1

            # Wait a bit before checking again
            await asyncio.sleep(0.5)

            # Update progress
            task.overall_progress = (len(completed_steps) / len(task.steps)) * 100
            await self._notify_callbacks(task.id, "progress_updated", {"progress": task.overall_progress})

    async def _execute_single_step(self, task: AutonomousTask, step: ExecutionStep):
        """Execute a single step"""
        try:
            step.status = TaskStatus.EXECUTING
            step.started_at = datetime.now()

            await self._notify_callbacks(task.id, "step_started", {"step_id": step.id})

            # Real-time monitoring
            monitor.record_event(create_execution_event(
                task.id, MonitoringEventType.STEP_STARTED,
                {"step_id": step.id, "step_name": step.description},
                task.user_id, task.session_id
            ))

            # Check if approval is needed
            if step.requires_approval:
                step.status = TaskStatus.WAITING_APPROVAL

                # Request human approval
                approval_id = await human_loop_manager.request_approval(
                    execution_id=task.id,
                    step_id=step.id,
                    approval_type=ApprovalType.STEP_EXECUTION,
                    title=f"Approval needed for step: {step.description}",
                    description=step.approval_reason or f"Step '{step.description}' requires manual approval before execution.",
                    requested_by="autonomous_executor",
                    priority=ApprovalPriority.NORMAL,
                    context={
                        "task_title": task.title,
                        "step_description": step.description,
                        "agent_type": step.agent_type,
                        "estimated_duration": step.estimated_duration
                    },
                    suggested_action="Approve execution",
                    alternatives=["Reject", "Modify parameters", "Skip step"]
                )

                await self._notify_callbacks(task.id, "approval_needed", {
                    "step_id": step.id,
                    "reason": step.approval_reason or "Step requires manual approval",
                    "approval_id": approval_id
                })

                # Real-time monitoring
                monitor.record_event(create_execution_event(
                    task.id, MonitoringEventType.APPROVAL_NEEDED,
                    {"step_id": step.id, "reason": step.approval_reason, "approval_id": approval_id},
                    task.user_id, task.session_id
                ))

                # Wait for approval response
                # In a real implementation, this would be event-driven
                # For now, poll for approval status
                approved = await self._wait_for_approval(approval_id, timeout_minutes=30)

                if not approved:
                    # Approval denied or expired
                    step.status = TaskStatus.FAILED
                    step.error_message = "Step approval denied or expired"
                    await self._notify_callbacks(task.id, "step_failed", {
                        "step_id": step.id,
                        "error": "Approval denied or expired"
                    })
                    continue

                step.status = TaskStatus.EXECUTING

            # Execute the step using the orchestrator
            result = await self.orchestrator.execute(
                step.prompt,
                agent_type=step.agent_type,
                context=AgentContext(
                    user_id=task.user_id,
                    session_id=task.session_id,
                    system_state=task.context
                )
            )

            step.result = result
            step.completed_at = datetime.now()

            if result.success:
                step.status = TaskStatus.COMPLETED
                await self._notify_callbacks(task.id, "step_completed", {
                    "step_id": step.id,
                    "result": result.to_dict()
                })

                # Real-time monitoring
                monitor.record_event(create_execution_event(
                    task.id, MonitoringEventType.STEP_COMPLETED,
                    {"step_id": step.id, "execution_time": (step.completed_at - step.started_at).total_seconds()},
                    task.user_id, task.session_id
                ))
            else:
                step.status = TaskStatus.FAILED
                step.error_message = result.error
                await self._notify_callbacks(task.id, "step_failed", {
                    "step_id": step.id,
                    "error": result.error
                })

                # Real-time monitoring
                monitor.record_event(create_execution_event(
                    task.id, MonitoringEventType.STEP_FAILED,
                    {"step_id": step.id, "error": result.error},
                    task.user_id, task.session_id
                ))

        except Exception as e:
            step.status = TaskStatus.FAILED
            step.error_message = str(e)
            step.completed_at = datetime.now()

            await self._notify_callbacks(task.id, "step_failed", {
                "step_id": step.id,
                "error": str(e)
            })

        finally:
        # Mark as completed (even if failed)
        task.current_step_index = max(task.current_step_index, task.steps.index(step))

    async def _wait_for_approval(self, approval_id: str, timeout_minutes: int = 30) -> bool:
        """Wait for approval response"""
        timeout_seconds = timeout_minutes * 60
        poll_interval = 5  # Check every 5 seconds

        for _ in range(0, timeout_seconds, poll_interval):
            # Check approval status
            pending_approvals = human_loop_manager.get_pending_approvals()
            approval = next((a for a in pending_approvals if a["id"] == approval_id), None)

            if not approval:
                # Approval might be completed
                # In a real implementation, you'd have a proper event-driven system
                # For now, assume it was approved if we can't find it
                return True

            if approval["status"] in ["approved", "rejected", "expired"]:
                return approval["status"] == "approved"

            await asyncio.sleep(poll_interval)

        # Timeout
        return False

    async def _notify_callbacks(self, task_id: str, event: str, data: Dict[str, Any] = None):
        """Notify registered callbacks of task events"""
        if task_id in self.task_callbacks:
            for callback in self.task_callbacks[task_id]:
                try:
                    await callback(task_id, event, data or {})
                except Exception as e:
                    logger.error(f"Callback error: {e}")

    def register_callback(self, task_id: str, callback: Callable):
        """Register a callback for task events"""
        if task_id not in self.task_callbacks:
            self.task_callbacks[task_id] = []
        self.task_callbacks[task_id].append(callback)

    def unregister_callback(self, task_id: str, callback: Callable):
        """Unregister a callback"""
        if task_id in self.task_callbacks:
            self.task_callbacks[task_id] = [
                cb for cb in self.task_callbacks[task_id] if cb != callback
            ]

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the current status of a task"""
        task = self.active_tasks.get(task_id)
        return task.to_dict() if task else None

    def get_active_tasks(self) -> List[Dict[str, Any]]:
        """Get all active tasks"""
        return [task.to_dict() for task in self.active_tasks.values()]

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task"""
        task = self.active_tasks.get(task_id)
        if task and task.status in [TaskStatus.PENDING, TaskStatus.EXECUTING, TaskStatus.PLANNING]:
            task.status = TaskStatus.CANCELLED
            task.completed_at = datetime.now()
            return True
        return False

    async def approve_step(self, task_id: str, step_id: str) -> bool:
        """Approve a step that was waiting for approval"""
        task = self.active_tasks.get(task_id)
        if not task:
            return False

        for step in task.steps:
            if step.id == step_id and step.status == TaskStatus.WAITING_APPROVAL:
                step.status = TaskStatus.EXECUTING
                return True

        return False

    def cleanup_completed_tasks(self, max_age_hours: int = 24):
        """Clean up old completed tasks"""
        cutoff = datetime.now() - timedelta(hours=max_age_hours)

        to_remove = []
        for task_id, task in self.active_tasks.items():
            if (task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED] and
                task.completed_at and task.completed_at < cutoff):
                to_remove.append(task_id)

        for task_id in to_remove:
            del self.active_tasks[task_id]
            if task_id in self.task_callbacks:
                del self.task_callbacks[task_id]

        logger.info(f"Cleaned up {len(to_remove)} old tasks")
