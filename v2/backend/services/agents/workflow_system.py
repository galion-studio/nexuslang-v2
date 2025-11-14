"""
Intelligent Workflow System for Galion Platform v2.2
Provides advanced workflow capabilities with decision points and conditional logic.

Features:
- Dynamic workflow execution with branching
- Decision points with conditional logic
- Loop constructs and error handling
- State persistence and recovery
- Parallel execution support
- Human-in-the-loop integration

"Your imagination is the end."
"""

import asyncio
from typing import Dict, List, Optional, Any, Union, Callable, Set
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
import logging
import json
from pathlib import Path

from .base_agent import AgentResult, AgentContext

logger = logging.getLogger(__name__)

class WorkflowNodeType(Enum):
    """Types of nodes in a workflow"""
    TASK = "task"           # Execute a task/agent
    DECISION = "decision"   # Make a decision based on conditions
    LOOP = "loop"          # Loop construct
    PARALLEL = "parallel"  # Parallel execution
    HUMAN_APPROVAL = "human_approval"  # Require human approval
    END = "end"           # End of workflow

class WorkflowStatus(Enum):
    """Status of a workflow execution"""
    PENDING = "pending"
    RUNNING = "running"
    WAITING_DECISION = "waiting_decision"
    WAITING_APPROVAL = "waiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class WorkflowCondition(BaseModel):
    """A condition for decision making"""

    field: str  # Field to check (e.g., "result.success", "context.user_role")
    operator: str  # "equals", "contains", "greater_than", "less_than", "regex_match"
    value: Any  # Value to compare against
    case_sensitive: bool = True

    def evaluate(self, data: Dict[str, Any]) -> bool:
        """Evaluate the condition against provided data"""
        try:
            # Extract field value using dot notation
            field_value = self._get_nested_value(data, self.field)

            if self.operator == "equals":
                if not self.case_sensitive and isinstance(field_value, str) and isinstance(self.value, str):
                    return field_value.lower() == self.value.lower()
                return field_value == self.value

            elif self.operator == "contains":
                if isinstance(field_value, (list, str)) and self.value in field_value:
                    return True
                return False

            elif self.operator == "greater_than":
                return float(field_value) > float(self.value)

            elif self.operator == "less_than":
                return float(field_value) < float(self.value)

            elif self.operator == "regex_match":
                import re
                pattern = re.compile(self.value, re.IGNORECASE if not self.case_sensitive else 0)
                return bool(pattern.match(str(field_value)))

            else:
                logger.warning(f"Unknown operator: {self.operator}")
                return False

        except Exception as e:
            logger.error(f"Error evaluating condition: {e}")
            return False

    def _get_nested_value(self, data: Dict[str, Any], field_path: str) -> Any:
        """Get nested value using dot notation"""
        keys = field_path.split('.')
        current = data

        for key in keys:
            if isinstance(current, dict):
                current = current.get(key)
            elif isinstance(current, list) and key.isdigit():
                current = current[int(key)] if int(key) < len(current) else None
            else:
                return None

            if current is None:
                return None

        return current

class WorkflowNode(BaseModel):
    """A node in the workflow graph"""

    id: str
    type: WorkflowNodeType
    name: str
    description: str = ""

    # Task-specific fields
    agent_type: Optional[str] = None
    prompt_template: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)

    # Decision-specific fields
    conditions: List[WorkflowCondition] = Field(default_factory=list)
    branches: Dict[str, str] = Field(default_factory=dict)  # branch_name -> node_id

    # Loop-specific fields
    loop_condition: Optional[WorkflowCondition] = None
    max_iterations: int = 10

    # Parallel-specific fields
    parallel_nodes: List[str] = Field(default_factory=list)

    # Approval-specific fields
    approval_message: Optional[str] = None
    auto_approve_conditions: List[WorkflowCondition] = Field(default_factory=list)

    # Execution metadata
    requires_approval: bool = False
    timeout_seconds: Optional[int] = None
    retry_count: int = 0

class WorkflowEdge(BaseModel):
    """An edge connecting workflow nodes"""

    from_node: str
    to_node: str
    condition: Optional[WorkflowCondition] = None  # Optional condition for traversal

class WorkflowDefinition(BaseModel):
    """Complete workflow definition"""

    id: str
    name: str
    description: str
    version: str = "1.0.0"

    nodes: Dict[str, WorkflowNode] = Field(default_factory=dict)
    edges: List[WorkflowEdge] = Field(default_factory=list)

    start_node: str
    end_nodes: List[str] = Field(default_factory=list)

    # Global settings
    max_execution_time: int = 3600  # 1 hour
    allow_parallel: bool = True
    require_approval_for_changes: bool = False

class WorkflowExecution(BaseModel):
    """Execution state of a workflow"""

    id: str
    workflow_id: str
    status: WorkflowStatus = WorkflowStatus.PENDING

    # Execution state
    current_nodes: Set[str] = Field(default_factory=set)
    completed_nodes: Set[str] = Field(default_factory=set)
    failed_nodes: Set[str] = Field(default_factory=set)

    # Node results
    node_results: Dict[str, AgentResult] = Field(default_factory=dict)
    node_start_times: Dict[str, datetime] = Field(default_factory=dict)
    node_end_times: Dict[str, datetime] = Field(default_factory=dict)

    # Context and data
    context: Dict[str, Any] = Field(default_factory=dict)
    variables: Dict[str, Any] = Field(default_factory=dict)

    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_execution_time: float = 0.0

    # User context
    user_id: Optional[str] = None
    session_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "workflow_id": self.workflow_id,
            "status": self.status.value,
            "progress": self.get_progress(),
            "current_nodes": list(self.current_nodes),
            "completed_nodes": list(self.completed_nodes),
            "failed_nodes": list(self.failed_nodes),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "total_execution_time": self.total_execution_time
        }

    def get_progress(self) -> float:
        """Calculate overall progress (0-100)"""
        total_nodes = len(self.node_results)
        if total_nodes == 0:
            return 0.0

        completed_count = len(self.completed_nodes)
        return (completed_count / total_nodes) * 100.0

class WorkflowEngine:
    """
    Intelligent workflow execution engine.

    Features:
    - Dynamic workflow execution with branching logic
    - Decision points with conditional evaluation
    - Parallel execution support
    - Loop constructs
    - Error handling and recovery
    - Human-in-the-loop integration
    """

    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.active_executions: Dict[str, WorkflowExecution] = {}
        self.workflow_definitions: Dict[str, WorkflowDefinition] = {}
        self.execution_callbacks: Dict[str, List[Callable]] = {}

        self.logger = logging.getLogger(f"{__name__}.engine")

    def register_workflow(self, workflow: WorkflowDefinition) -> bool:
        """Register a workflow definition"""
        if workflow.id in self.workflow_definitions:
            self.logger.warning(f"Workflow {workflow.id} already registered")
            return False

        # Validate workflow
        if not self._validate_workflow(workflow):
            self.logger.error(f"Workflow {workflow.id} validation failed")
            return False

        self.workflow_definitions[workflow.id] = workflow
        self.logger.info(f"Registered workflow: {workflow.name} ({workflow.id})")
        return True

    def _validate_workflow(self, workflow: WorkflowDefinition) -> bool:
        """Validate workflow definition"""
        # Check start node exists
        if workflow.start_node not in workflow.nodes:
            return False

        # Check end nodes exist
        for end_node in workflow.end_nodes:
            if end_node not in workflow.nodes:
                return False

        # Check all edges reference valid nodes
        for edge in workflow.edges:
            if edge.from_node not in workflow.nodes or edge.to_node not in workflow.nodes:
                return False

        return True

    async def execute_workflow(
        self,
        workflow_id: str,
        context: Dict[str, Any] = None,
        user_id: str = None,
        session_id: str = None
    ) -> str:
        """
        Start execution of a workflow.

        Returns execution ID for tracking.
        """
        if workflow_id not in self.workflow_definitions:
            raise ValueError(f"Workflow {workflow_id} not found")

        workflow = self.workflow_definitions[workflow_id]

        # Create execution instance
        execution_id = f"wf_exec_{datetime.now().timestamp()}_{hash(workflow_id) % 10000}"
        execution = WorkflowExecution(
            id=execution_id,
            workflow_id=workflow_id,
            context=context or {},
            user_id=user_id,
            session_id=session_id
        )

        self.active_executions[execution_id] = execution

        # Start execution in background
        asyncio.create_task(self._execute_workflow_async(execution_id))

        return execution_id

    async def _execute_workflow_async(self, execution_id: str):
        """Execute workflow asynchronously"""
        execution = self.active_executions.get(execution_id)
        if not execution:
            return

        workflow = self.workflow_definitions.get(execution.workflow_id)
        if not workflow:
            execution.status = WorkflowStatus.FAILED
            return

        try:
            execution.status = WorkflowStatus.RUNNING
            execution.started_at = datetime.now()

            await self._notify_callbacks(execution_id, "started")

            # Start with the start node
            execution.current_nodes.add(workflow.start_node)

            # Execute until completion
            while execution.status == WorkflowStatus.RUNNING:
                if not execution.current_nodes:
                    # No more nodes to execute - check if we reached an end
                    if self._check_completion(execution, workflow):
                        execution.status = WorkflowStatus.COMPLETED
                        execution.completed_at = datetime.now()
                        execution.total_execution_time = (
                            execution.completed_at - execution.started_at
                        ).total_seconds()
                        await self._notify_callbacks(execution_id, "completed")
                    else:
                        execution.status = WorkflowStatus.FAILED
                        await self._notify_callbacks(execution_id, "failed", {"reason": "No executable nodes"})
                    break

                # Execute current nodes
                await self._execute_current_nodes(execution, workflow)

                # Small delay to prevent tight loops
                await asyncio.sleep(0.1)

        except Exception as e:
            self.logger.error(f"Workflow execution {execution_id} failed: {e}")
            execution.status = WorkflowStatus.FAILED
            await self._notify_callbacks(execution_id, "failed", {"error": str(e)})

    async def _execute_current_nodes(self, execution: WorkflowExecution, workflow: WorkflowDefinition):
        """Execute all current nodes"""
        # Get executable nodes (not waiting for decisions/approvals)
        executable_nodes = []
        for node_id in execution.current_nodes:
            node = workflow.nodes[node_id]
            if node.type not in [WorkflowNodeType.DECISION, WorkflowNodeType.HUMAN_APPROVAL]:
                executable_nodes.append(node_id)
            elif node.type == WorkflowNodeType.HUMAN_APPROVAL and self._check_auto_approve(node, execution):
                executable_nodes.append(node_id)

        if not executable_nodes:
            # Check if we're waiting for decisions or approvals
            waiting_decisions = any(
                workflow.nodes[node_id].type == WorkflowNodeType.DECISION
                for node_id in execution.current_nodes
            )
            waiting_approvals = any(
                workflow.nodes[node_id].type == WorkflowNodeType.HUMAN_APPROVAL
                for node_id in execution.current_nodes
            )

            if waiting_decisions:
                execution.status = WorkflowStatus.WAITING_DECISION
            elif waiting_approvals:
                execution.status = WorkflowStatus.WAITING_APPROVAL
            # If neither, we'll fail in the main loop
            return

        # Execute nodes (for now, sequentially - could be parallel)
        for node_id in executable_nodes:
            await self._execute_node(node_id, execution, workflow)
            execution.current_nodes.remove(node_id)

            # Add next nodes based on edges
            next_nodes = self._get_next_nodes(node_id, execution, workflow)
            execution.current_nodes.update(next_nodes)

    async def _execute_node(self, node_id: str, execution: WorkflowExecution, workflow: WorkflowDefinition):
        """Execute a single node"""
        node = workflow.nodes[node_id]
        execution.node_start_times[node_id] = datetime.now()

        await self._notify_callbacks(execution.id, "node_started", {"node_id": node_id, "node_name": node.name})

        try:
            if node.type == WorkflowNodeType.TASK:
                result = await self._execute_task_node(node, execution)

            elif node.type == WorkflowNodeType.DECISION:
                result = await self._execute_decision_node(node, execution)

            elif node.type == WorkflowNodeType.LOOP:
                result = await self._execute_loop_node(node, execution)

            elif node.type == WorkflowNodeType.PARALLEL:
                result = await self._execute_parallel_node(node, execution)

            elif node.type == WorkflowNodeType.HUMAN_APPROVAL:
                result = await self._execute_approval_node(node, execution)

            elif node.type == WorkflowNodeType.END:
                result = AgentResult(success=True, response="Workflow completed", cost=0.0, execution_time=0.0)

            else:
                result = AgentResult(
                    success=False,
                    response=f"Unknown node type: {node.type}",
                    cost=0.0,
                    execution_time=0.0,
                    error=f"Unsupported node type: {node.type}"
                )

            execution.node_results[node_id] = result
            execution.node_end_times[node_id] = datetime.now()

            if result.success:
                execution.completed_nodes.add(node_id)
                await self._notify_callbacks(execution.id, "node_completed", {
                    "node_id": node_id,
                    "result": result.to_dict()
                })
            else:
                execution.failed_nodes.add(node_id)
                await self._notify_callbacks(execution.id, "node_failed", {
                    "node_id": node_id,
                    "error": result.error
                })

        except Exception as e:
            self.logger.error(f"Node execution failed: {node_id} - {e}")
            execution.node_results[node_id] = AgentResult(
                success=False,
                response="Node execution failed",
                cost=0.0,
                execution_time=0.0,
                error=str(e)
            )
            execution.failed_nodes.add(node_id)
            execution.node_end_times[node_id] = datetime.now()

    async def _execute_task_node(self, node: WorkflowNode, execution: WorkflowExecution) -> AgentResult:
        """Execute a task node"""
        # Prepare prompt from template
        prompt = node.prompt_template or node.description
        if node.parameters:
            # Substitute variables
            prompt = self._substitute_variables(prompt, execution)

        # Execute using orchestrator
        context = AgentContext(
            user_id=execution.user_id,
            session_id=execution.session_id,
            system_state=execution.context
        )

        return await self.orchestrator.execute(
            prompt,
            agent_type=node.agent_type,
            context=context
        )

    async def _execute_decision_node(self, node: WorkflowNode, execution: WorkflowExecution) -> AgentResult:
        """Execute a decision node"""
        # Evaluate conditions and return appropriate branch
        for condition in node.conditions:
            if condition.evaluate(execution.variables):
                # Store decision result
                execution.variables[f"{node.id}_decision"] = condition.field
                return AgentResult(
                    success=True,
                    response=f"Decision made: {condition.field}",
                    cost=0.0,
                    execution_time=0.0,
                    metadata={"decision": condition.field, "branch": node.branches.get("true", "default")}
                )

        # Default branch
        execution.variables[f"{node.id}_decision"] = "default"
        return AgentResult(
            success=True,
            response="Decision made: default",
            cost=0.0,
            execution_time=0.0,
            metadata={"decision": "default", "branch": node.branches.get("false", "default")}
        )

    async def _execute_loop_node(self, node: WorkflowNode, execution: WorkflowExecution) -> AgentResult:
        """Execute a loop node"""
        iteration_count = execution.variables.get(f"{node.id}_iterations", 0)

        if node.loop_condition and node.loop_condition.evaluate(execution.variables):
            if iteration_count < node.max_iterations:
                execution.variables[f"{node.id}_iterations"] = iteration_count + 1
                return AgentResult(
                    success=True,
                    response=f"Loop iteration {iteration_count + 1}",
                    cost=0.0,
                    execution_time=0.0,
                    metadata={"continue_loop": True, "iteration": iteration_count + 1}
                )

        # Exit loop
        return AgentResult(
            success=True,
            response="Loop completed",
            cost=0.0,
            execution_time=0.0,
            metadata={"continue_loop": False}
        )

    async def _execute_parallel_node(self, node: WorkflowNode, execution: WorkflowExecution) -> AgentResult:
        """Execute a parallel node"""
        # For now, just mark as completed - parallel execution handled at workflow level
        return AgentResult(
            success=True,
            response=f"Parallel execution started for {len(node.parallel_nodes)} nodes",
            cost=0.0,
            execution_time=0.0,
            metadata={"parallel_nodes": node.parallel_nodes}
        )

    async def _execute_approval_node(self, node: WorkflowNode, execution: WorkflowExecution) -> AgentResult:
        """Execute an approval node"""
        return AgentResult(
            success=True,
            response="Waiting for approval",
            cost=0.0,
            execution_time=0.0,
            metadata={"approval_required": True, "message": node.approval_message}
        )

    def _check_auto_approve(self, node: WorkflowNode, execution: WorkflowExecution) -> bool:
        """Check if node can be auto-approved"""
        for condition in node.auto_approve_conditions:
            if not condition.evaluate(execution.variables):
                return False
        return True

    def _get_next_nodes(self, node_id: str, execution: WorkflowExecution, workflow: WorkflowDefinition) -> List[str]:
        """Get next nodes based on edges and conditions"""
        next_nodes = []

        for edge in workflow.edges:
            if edge.from_node == node_id:
                # Check edge condition if present
                if edge.condition and not edge.condition.evaluate(execution.variables):
                    continue

                next_nodes.append(edge.to_node)

        return next_nodes

    def _check_completion(self, execution: WorkflowExecution, workflow: WorkflowDefinition) -> bool:
        """Check if workflow is completed"""
        # Check if any end node is completed
        return any(end_node in execution.completed_nodes for end_node in workflow.end_nodes)

    def _substitute_variables(self, template: str, execution: WorkflowExecution) -> str:
        """Substitute variables in template string"""
        result = template

        # Substitute execution variables
        for key, value in execution.variables.items():
            result = result.replace(f"{{{{variables.{key}}}}}", str(value))

        # Substitute context variables
        for key, value in execution.context.items():
            result = result.replace(f"{{{{context.{key}}}}}", str(value))

        return result

    async def _notify_callbacks(self, execution_id: str, event: str, data: Dict[str, Any] = None):
        """Notify registered callbacks"""
        if execution_id in self.execution_callbacks:
            for callback in self.execution_callbacks[execution_id]:
                try:
                    await callback(execution_id, event, data or {})
                except Exception as e:
                    self.logger.error(f"Callback error: {e}")

    def register_callback(self, execution_id: str, callback: Callable):
        """Register callback for execution events"""
        if execution_id not in self.execution_callbacks:
            self.execution_callbacks[execution_id] = []
        self.execution_callbacks[execution_id].append(callback)

    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get execution status"""
        execution = self.active_executions.get(execution_id)
        return execution.to_dict() if execution else None

    def cancel_execution(self, execution_id: str) -> bool:
        """Cancel a workflow execution"""
        execution = self.active_executions.get(execution_id)
        if execution and execution.status in [WorkflowStatus.PENDING, WorkflowStatus.RUNNING]:
            execution.status = WorkflowStatus.CANCELLED
            execution.completed_at = datetime.now()
            return True
        return False

    async def approve_node(self, execution_id: str, node_id: str) -> bool:
        """Approve a waiting approval node"""
        execution = self.active_executions.get(execution_id)
        if not execution:
            return False

        if node_id in execution.current_nodes:
            workflow = self.workflow_definitions.get(execution.workflow_id)
            if workflow and workflow.nodes[node_id].type == WorkflowNodeType.HUMAN_APPROVAL:
                # Mark as approved and continue execution
                execution.current_nodes.remove(node_id)
                execution.completed_nodes.add(node_id)

                # Add next nodes
                next_nodes = self._get_next_nodes(node_id, execution, workflow)
                execution.current_nodes.update(next_nodes)

                # Resume execution if waiting
                if execution.status == WorkflowStatus.WAITING_APPROVAL:
                    execution.status = WorkflowStatus.RUNNING
                    # Restart execution loop
                    asyncio.create_task(self._continue_execution(execution_id))

                return True

        return False

    async def _continue_execution(self, execution_id: str):
        """Continue execution after approval"""
        execution = self.active_executions.get(execution_id)
        if execution and execution.status == WorkflowStatus.RUNNING:
            await self._execute_workflow_async(execution_id)

    def cleanup_executions(self, max_age_hours: int = 24):
        """Clean up old executions"""
        cutoff = datetime.now().replace(hour=datetime.now().hour - max_age_hours)

        to_remove = []
        for exec_id, execution in self.active_executions.items():
            if (execution.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED] and
                execution.completed_at and execution.completed_at < cutoff):
                to_remove.append(exec_id)

        for exec_id in to_remove:
            del self.active_executions[exec_id]
            if exec_id in self.execution_callbacks:
                del self.execution_callbacks[exec_id]

        self.logger.info(f"Cleaned up {len(to_remove)} old executions")
