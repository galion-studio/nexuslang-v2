"""
Advanced Workflow Builder for Galion Agents

Enables creation of complex, dynamic workflows with conditional logic,
parallel execution, loops, and custom decision-making capabilities.
"""

import asyncio
import logging
import json
import uuid
from typing import Dict, Any, List, Optional, Union, Callable, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import networkx as nx

from .base_agent import AgentResult, AgentContext
from .agent_orchestrator import AgentOrchestrator


logger = logging.getLogger(__name__)


class WorkflowNodeType(Enum):
    """Types of nodes in a workflow."""
    START = "start"
    END = "end"
    TASK = "task"
    DECISION = "decision"
    PARALLEL = "parallel"
    JOIN = "join"
    LOOP = "loop"
    WAIT = "wait"
    WEBHOOK = "webhook"
    CONDITION = "condition"
    TRANSFORM = "transform"


class WorkflowStatus(Enum):
    """Workflow execution status."""
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


@dataclass
class WorkflowNode:
    """Represents a node in a workflow."""
    node_id: str
    node_type: WorkflowNodeType
    name: str
    description: str = ""
    config: Dict[str, Any] = field(default_factory=dict)
    position: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Execution state
    status: WorkflowStatus = WorkflowStatus.CREATED
    execution_order: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None

    def __post_init__(self):
        if not self.node_id:
            self.node_id = str(uuid.uuid4())


@dataclass
class WorkflowEdge:
    """Represents a connection between workflow nodes."""
    edge_id: str
    source_node: str
    target_node: str
    condition: Optional[str] = None  # Conditional logic for execution
    priority: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.edge_id:
            self.edge_id = str(uuid.uuid4())


@dataclass
class WorkflowExecution:
    """Represents a workflow execution instance."""
    execution_id: str
    workflow_id: str
    status: WorkflowStatus = WorkflowStatus.CREATED
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    current_nodes: Set[str] = field(default_factory=set)
    completed_nodes: Set[str] = field(default_factory=set)
    failed_nodes: Set[str] = field(default_factory=set)
    node_results: Dict[str, Any] = field(default_factory=dict)
    variables: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.execution_id:
            self.execution_id = str(uuid.uuid4())


class WorkflowDefinition:
    """Defines a complete workflow with nodes and edges."""

    def __init__(self, workflow_id: str, name: str, description: str = ""):
        self.workflow_id = workflow_id or str(uuid.uuid4())
        self.name = name
        self.description = description
        self.version = "1.0.0"
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

        # Workflow structure
        self.nodes: Dict[str, WorkflowNode] = {}
        self.edges: Dict[str, WorkflowEdge] = {}

        # Graph representation for analysis
        self.graph = nx.DiGraph()

        # Validation and execution metadata
        self.is_valid = False
        self.validation_errors: List[str] = []

    def add_node(self, node: WorkflowNode) -> None:
        """Add a node to the workflow."""
        self.nodes[node.node_id] = node
        self.graph.add_node(node.node_id, **node.__dict__)
        self.updated_at = datetime.now()
        self.is_valid = False  # Mark as needing revalidation

    def add_edge(self, edge: WorkflowEdge) -> None:
        """Add an edge between nodes."""
        # Validate that nodes exist
        if edge.source_node not in self.nodes:
            raise ValueError(f"Source node {edge.source_node} does not exist")
        if edge.target_node not in self.nodes:
            raise ValueError(f"Target node {edge.target_node} does not exist")

        self.edges[edge.edge_id] = edge
        self.graph.add_edge(edge.source_node, edge.target_node, **edge.__dict__)
        self.updated_at = datetime.now()
        self.is_valid = False

    def remove_node(self, node_id: str) -> None:
        """Remove a node and its connected edges."""
        if node_id in self.nodes:
            # Remove connected edges
            edges_to_remove = [
                edge_id for edge_id, edge in self.edges.items()
                if edge.source_node == node_id or edge.target_node == node_id
            ]
            for edge_id in edges_to_remove:
                del self.edges[edge_id]

            # Remove node
            del self.nodes[node_id]
            self.graph.remove_node(node_id)
            self.updated_at = datetime.now()
            self.is_valid = False

    def validate(self) -> bool:
        """Validate the workflow structure."""
        self.validation_errors = []

        # Check for start node
        start_nodes = [node for node in self.nodes.values() if node.node_type == WorkflowNodeType.START]
        if len(start_nodes) != 1:
            self.validation_errors.append("Workflow must have exactly one START node")

        # Check for end node
        end_nodes = [node for node in self.nodes.values() if node.node_type == WorkflowNodeType.END]
        if len(end_nodes) < 1:
            self.validation_errors.append("Workflow must have at least one END node")

        # Check for cycles (except for loop nodes)
        try:
            cycles = list(nx.simple_cycles(self.graph))
            # Filter out cycles that are legitimate loops
            loop_cycles = []
            for cycle in cycles:
                if not any(self.nodes[node].node_type == WorkflowNodeType.LOOP for node in cycle):
                    loop_cycles.append(cycle)

            if loop_cycles:
                self.validation_errors.append(f"Workflow contains cycles: {loop_cycles}")
        except Exception as e:
            self.validation_errors.append(f"Graph analysis failed: {e}")

        # Check for isolated nodes
        isolated_nodes = [node_id for node_id in nx.isolates(self.graph)]
        if isolated_nodes:
            self.validation_errors.append(f"Isolated nodes found: {isolated_nodes}")

        # Validate node configurations
        for node in self.nodes.values():
            errors = self._validate_node_config(node)
            self.validation_errors.extend(errors)

        self.is_valid = len(self.validation_errors) == 0
        return self.is_valid

    def _validate_node_config(self, node: WorkflowNode) -> List[str]:
        """Validate a node's configuration."""
        errors = []

        if node.node_type == WorkflowNodeType.TASK:
            if not node.config.get('agent_type'):
                errors.append(f"Task node {node.node_id} missing agent_type")
            if not node.config.get('task_description'):
                errors.append(f"Task node {node.node_id} missing task_description")

        elif node.node_type == WorkflowNodeType.DECISION:
            if not node.config.get('condition'):
                errors.append(f"Decision node {node.node_id} missing condition")

        elif node.node_type == WorkflowNodeType.LOOP:
            if not node.config.get('loop_condition'):
                errors.append(f"Loop node {node.node_id} missing loop_condition")
            if not isinstance(node.config.get('max_iterations', 0), int):
                errors.append(f"Loop node {node.node_id} max_iterations must be integer")

        elif node.node_type == WorkflowNodeType.WAIT:
            if not node.config.get('wait_duration'):
                errors.append(f"Wait node {node.node_id} missing wait_duration")

        elif node.node_type == WorkflowNodeType.WEBHOOK:
            if not node.config.get('webhook_url'):
                errors.append(f"Webhook node {node.node_id} missing webhook_url")

        return errors

    def get_execution_path(self, start_node: str = None) -> List[str]:
        """Get the execution path from a starting node."""
        if not start_node:
            start_nodes = [node_id for node_id, node in self.nodes.items()
                          if node.node_type == WorkflowNodeType.START]
            if not start_nodes:
                return []
            start_node = start_nodes[0]

        try:
            # Get topological sort for execution order
            execution_order = list(nx.topological_sort(self.graph))
            # Filter to nodes reachable from start
            reachable = set(nx.descendants(self.graph, start_node))
            reachable.add(start_node)

            return [node for node in execution_order if node in reachable]
        except Exception:
            # Fallback to BFS if topological sort fails
            return list(nx.bfs_tree(self.graph, start_node).nodes())

    def to_dict(self) -> Dict[str, Any]:
        """Convert workflow to dictionary representation."""
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_valid": self.is_valid,
            "validation_errors": self.validation_errors,
            "nodes": {node_id: node.__dict__ for node_id, node in self.nodes.items()},
            "edges": {edge_id: edge.__dict__ for edge_id, edge in self.edges.items()}
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkflowDefinition':
        """Create workflow from dictionary representation."""
        workflow = cls(
            workflow_id=data["workflow_id"],
            name=data["name"],
            description=data.get("description", "")
        )

        workflow.version = data.get("version", "1.0.0")
        workflow.created_at = datetime.fromisoformat(data["created_at"])
        workflow.updated_at = datetime.fromisoformat(data["updated_at"])
        workflow.is_valid = data.get("is_valid", False)
        workflow.validation_errors = data.get("validation_errors", [])

        # Restore nodes
        for node_id, node_data in data.get("nodes", {}).items():
            # Remove computed fields
            node_dict = {k: v for k, v in node_data.items()
                        if k not in ['node_id', 'node_type']}
            node_dict['node_type'] = WorkflowNodeType(node_data['node_type'])

            node = WorkflowNode(node_id=node_id, **node_dict)
            workflow.add_node(node)

        # Restore edges
        for edge_id, edge_data in data.get("edges", {}).items():
            edge_dict = {k: v for k, v in edge_data.items() if k != 'edge_id'}
            edge = WorkflowEdge(edge_id=edge_id, **edge_dict)
            workflow.add_edge(edge)

        return workflow


class WorkflowEngine:
    """
    Advanced workflow execution engine with dynamic decision-making,
    parallel execution, loops, and error handling.
    """

    def __init__(self, orchestrator: AgentOrchestrator):
        self.orchestrator = orchestrator
        self.active_executions: Dict[str, WorkflowExecution] = {}
        self.execution_history: Dict[str, WorkflowExecution] = {}

        # Execution management
        self.max_concurrent_executions = 10
        self.execution_timeout = timedelta(hours=2)
        self.node_timeout = timedelta(minutes=30)

        # Performance monitoring
        self.execution_stats = defaultdict(int)

    async def execute_workflow(self, workflow: WorkflowDefinition,
                             input_data: Dict[str, Any] = None,
                             execution_id: str = None) -> WorkflowExecution:
        """Execute a workflow definition."""
        # Validate workflow
        if not workflow.validate():
            execution = WorkflowExecution(
                execution_id=execution_id or str(uuid.uuid4()),
                workflow_id=workflow.workflow_id,
                status=WorkflowStatus.FAILED
            )
            execution.metadata["validation_errors"] = workflow.validation_errors
            return execution

        # Create execution instance
        execution = WorkflowExecution(
            execution_id=execution_id or str(uuid.uuid4()),
            workflow_id=workflow.workflow_id,
            variables=input_data or {},
            status=WorkflowStatus.RUNNING,
            started_at=datetime.now()
        )

        self.active_executions[execution.execution_id] = execution

        try:
            # Execute workflow
            await self._execute_workflow_nodes(workflow, execution)

            # Mark as completed
            execution.status = WorkflowStatus.COMPLETED
            execution.completed_at = datetime.now()

        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            execution.status = WorkflowStatus.FAILED
            execution.metadata["error"] = str(e)
            execution.completed_at = datetime.now()

        finally:
            # Move to history
            self.execution_history[execution.execution_id] = execution
            if execution.execution_id in self.active_executions:
                del self.active_executions[execution.execution_id]

            # Update stats
            self.execution_stats[execution.status.value] += 1

        return execution

    async def _execute_workflow_nodes(self, workflow: WorkflowDefinition,
                                    execution: WorkflowExecution) -> None:
        """Execute workflow nodes in the correct order."""
        # Get execution path
        execution_path = workflow.get_execution_path()

        # Track parallel executions
        parallel_groups: Dict[str, List[str]] = defaultdict(list)
        join_nodes: Dict[str, str] = {}  # join_node -> parallel_node

        # Execute nodes
        for node_id in execution_path:
            node = workflow.nodes[node_id]

            # Check for parallel execution
            if node.node_type == WorkflowNodeType.PARALLEL:
                # Collect all parallel branches
                parallel_branches = []
                for edge in workflow.edges.values():
                    if edge.source_node == node_id:
                        parallel_branches.append(edge.target_node)

                # Execute branches in parallel
                await self._execute_parallel_branches(workflow, execution, parallel_branches)

            elif node.node_type == WorkflowNodeType.JOIN:
                # Wait for parallel branches to complete
                await self._wait_for_join(workflow, execution, node_id)

            else:
                # Execute single node
                await self._execute_node(workflow, execution, node_id)

            # Check execution status
            if execution.status != WorkflowStatus.RUNNING:
                break

    async def _execute_parallel_branches(self, workflow: WorkflowDefinition,
                                       execution: WorkflowExecution,
                                       branch_nodes: List[str]) -> None:
        """Execute multiple branches in parallel."""
        # Create tasks for each branch
        branch_tasks = []
        for node_id in branch_nodes:
            task = asyncio.create_task(
                self._execute_node(workflow, execution, node_id)
            )
            branch_tasks.append(task)

        # Wait for all branches to complete
        await asyncio.gather(*branch_tasks, return_exceptions=True)

    async def _wait_for_join(self, workflow: WorkflowDefinition,
                           execution: WorkflowExecution, join_node_id: str) -> None:
        """Wait for parallel branches to complete at a join node."""
        # This is a simplified implementation - in a full system,
        # you'd track which branches feed into each join node
        await asyncio.sleep(0.1)  # Brief pause for synchronization

    async def _execute_node(self, workflow: WorkflowDefinition,
                          execution: WorkflowExecution, node_id: str) -> None:
        """Execute a single workflow node."""
        node = workflow.nodes[node_id]

        # Update execution state
        execution.current_nodes.add(node_id)
        node.status = WorkflowStatus.RUNNING
        node.started_at = datetime.now()
        node.execution_order = len(execution.completed_nodes) + len(execution.failed_nodes) + 1

        try:
            # Execute based on node type
            if node.node_type == WorkflowNodeType.START:
                # Nothing to do for start node
                pass

            elif node.node_type == WorkflowNodeType.END:
                # Mark workflow as completed
                execution.status = WorkflowStatus.COMPLETED

            elif node.node_type == WorkflowNodeType.TASK:
                result = await self._execute_task_node(node, execution)
                execution.node_results[node_id] = result

            elif node.node_type == WorkflowNodeType.DECISION:
                await self._execute_decision_node(workflow, node, execution)

            elif node.node_type == WorkflowNodeType.LOOP:
                await self._execute_loop_node(workflow, node, execution)

            elif node.node_type == WorkflowNodeType.WAIT:
                await self._execute_wait_node(node, execution)

            elif node.node_type == WorkflowNodeType.WEBHOOK:
                await self._execute_webhook_node(node, execution)

            elif node.node_type == WorkflowNodeType.CONDITION:
                await self._execute_condition_node(workflow, node, execution)

            elif node.node_type == WorkflowNodeType.TRANSFORM:
                await self._execute_transform_node(node, execution)

            # Mark node as completed
            node.status = WorkflowStatus.COMPLETED
            node.completed_at = datetime.now()
            execution.completed_nodes.add(node_id)

        except Exception as e:
            logger.error(f"Node execution failed: {node_id} - {e}")
            node.status = WorkflowStatus.FAILED
            node.error = str(e)
            node.completed_at = datetime.now()
            execution.failed_nodes.add(node_id)
            execution.status = WorkflowStatus.FAILED

        finally:
            execution.current_nodes.discard(node_id)

    async def _execute_task_node(self, node: WorkflowNode, execution: WorkflowExecution) -> Any:
        """Execute a task node by calling the appropriate agent."""
        agent_type = node.config.get('agent_type')
        task_description = node.config.get('task_description')
        task_params = node.config.get('parameters', {})

        if not agent_type or not task_description:
            raise ValueError(f"Task node {node.node_id} missing required configuration")

        # Create task context
        context = AgentContext(
            workflow_execution_id=execution.execution_id,
            workflow_variables=execution.variables.copy(),
            collaboration_history=[],
            user_preferences={}
        )

        # Execute task via orchestrator
        result = await self.orchestrator.execute_task(
            description=task_description,
            agent_type=agent_type,
            context=context,
            **task_params
        )

        # Store result in workflow variables
        if node.config.get('store_result'):
            result_key = node.config.get('result_variable', f"task_{node.node_id}_result")
            execution.variables[result_key] = result.data if result.success else None

        return result

    async def _execute_decision_node(self, workflow: WorkflowDefinition,
                                   node: WorkflowNode, execution: WorkflowExecution) -> None:
        """Execute a decision node with conditional logic."""
        condition = node.config.get('condition')
        if not condition:
            raise ValueError(f"Decision node {node.node_id} missing condition")

        # Evaluate condition
        condition_result = self._evaluate_condition(condition, execution.variables)

        # Find appropriate outgoing edge
        target_node = None
        for edge in workflow.edges.values():
            if edge.source_node == node.node_id:
                if edge.condition == "true" and condition_result:
                    target_node = edge.target_node
                    break
                elif edge.condition == "false" and not condition_result:
                    target_node = edge.target_node
                    break
                elif edge.condition is None:  # Default path
                    target_node = edge.target_node

        if target_node:
            # Execute target node immediately (bypass normal flow)
            await self._execute_node(workflow, execution, target_node)

    async def _execute_loop_node(self, workflow: WorkflowDefinition,
                               node: WorkflowNode, execution: WorkflowExecution) -> None:
        """Execute a loop node with iteration logic."""
        loop_condition = node.config.get('loop_condition')
        max_iterations = node.config.get('max_iterations', 10)
        iteration_variable = node.config.get('iteration_variable', 'loop_index')

        if not loop_condition:
            raise ValueError(f"Loop node {node.node_id} missing loop_condition")

        iteration_count = 0

        while iteration_count < max_iterations:
            # Set iteration variable
            execution.variables[iteration_variable] = iteration_count

            # Evaluate loop condition
            if not self._evaluate_condition(loop_condition, execution.variables):
                break

            # Execute loop body (nodes connected to this loop)
            loop_body_nodes = [
                edge.target_node for edge in workflow.edges.values()
                if edge.source_node == node.node_id
            ]

            for body_node_id in loop_body_nodes:
                await self._execute_node(workflow, execution, body_node_id)

                # Check if we should break out of loop
                if execution.status != WorkflowStatus.RUNNING:
                    return

            iteration_count += 1

            # Prevent infinite loops
            if iteration_count >= max_iterations:
                logger.warning(f"Loop node {node.node_id} reached max iterations ({max_iterations})")

    async def _execute_wait_node(self, node: WorkflowNode, execution: WorkflowExecution) -> None:
        """Execute a wait node with timing logic."""
        wait_duration = node.config.get('wait_duration')

        if isinstance(wait_duration, str):
            # Parse duration string (e.g., "30s", "5m", "1h")
            wait_duration = self._parse_duration(wait_duration)
        elif isinstance(wait_duration, (int, float)):
            wait_duration = timedelta(seconds=wait_duration)
        else:
            raise ValueError(f"Invalid wait duration: {wait_duration}")

        # Wait for the specified duration
        await asyncio.sleep(wait_duration.total_seconds())

    async def _execute_webhook_node(self, node: WorkflowNode, execution: WorkflowExecution) -> None:
        """Execute a webhook node to call external services."""
        webhook_url = node.config.get('webhook_url')
        method = node.config.get('method', 'POST')
        payload = node.config.get('payload', {})

        if not webhook_url:
            raise ValueError(f"Webhook node {node.node_id} missing webhook_url")

        # Merge execution variables into payload
        webhook_payload = {**payload}
        for key, value in execution.variables.items():
            if isinstance(value, (str, int, float, bool, list, dict)):
                webhook_payload[key] = value

        # Execute webhook via integration
        result = await self.orchestrator.execute_integration_operation(
            "webhook", "send_custom_payload",
            payload=webhook_payload,
            event_type=f"workflow_{node.node_id}"
        )

        if not result:
            logger.warning(f"Webhook execution failed for node {node.node_id}")

    async def _execute_condition_node(self, workflow: WorkflowDefinition,
                                    node: WorkflowNode, execution: WorkflowExecution) -> None:
        """Execute a condition node for complex logic."""
        condition_script = node.config.get('condition_script')
        condition_variables = node.config.get('condition_variables', [])

        if not condition_script:
            raise ValueError(f"Condition node {node.node_id} missing condition_script")

        # Create execution context for condition
        condition_context = execution.variables.copy()

        # Evaluate condition (simplified - in production, use a safe script evaluator)
        try:
            # This is a simplified implementation - use ast.literal_eval or a safe evaluator
            condition_result = eval(condition_script, {"__builtins__": {}}, condition_context)
        except Exception as e:
            logger.error(f"Condition evaluation failed: {e}")
            condition_result = False

        # Store result
        result_variable = node.config.get('result_variable', f"condition_{node.node_id}_result")
        execution.variables[result_variable] = condition_result

    async def _execute_transform_node(self, node: WorkflowNode, execution: WorkflowExecution) -> None:
        """Execute a transform node to manipulate data."""
        transform_script = node.config.get('transform_script')
        input_variables = node.config.get('input_variables', [])
        output_variable = node.config.get('output_variable')

        if not transform_script:
            raise ValueError(f"Transform node {node.node_id} missing transform_script")

        # Prepare transform context
        transform_context = {}
        for var_name in input_variables:
            if var_name in execution.variables:
                transform_context[var_name] = execution.variables[var_name]

        # Execute transform (simplified - use safe evaluation in production)
        try:
            result = eval(transform_script, {"__builtins__": {}}, transform_context)

            if output_variable:
                execution.variables[output_variable] = result

        except Exception as e:
            logger.error(f"Transform execution failed: {e}")
            if output_variable:
                execution.variables[output_variable] = None

    def _evaluate_condition(self, condition: str, variables: Dict[str, Any]) -> bool:
        """Evaluate a condition expression."""
        try:
            # Simple variable substitution and evaluation
            # In production, use a proper expression evaluator
            for var_name, var_value in variables.items():
                if isinstance(var_value, str):
                    condition = condition.replace(f"${{{var_name}}}", f"'{var_value}'")
                else:
                    condition = condition.replace(f"${{{var_name}}}", str(var_value))

            # Evaluate condition
            return bool(eval(condition, {"__builtins__": {}}, variables))

        except Exception as e:
            logger.error(f"Condition evaluation failed: {condition} - {e}")
            return False

    def _parse_duration(self, duration_str: str) -> timedelta:
        """Parse duration string into timedelta."""
        import re

        # Match patterns like "30s", "5m", "1h", "2d"
        match = re.match(r'^(\d+)([smhd])$', duration_str.lower())
        if not match:
            raise ValueError(f"Invalid duration format: {duration_str}")

        value, unit = match.groups()
        value = int(value)

        if unit == 's':
            return timedelta(seconds=value)
        elif unit == 'm':
            return timedelta(minutes=value)
        elif unit == 'h':
            return timedelta(hours=value)
        elif unit == 'd':
            return timedelta(days=value)
        else:
            raise ValueError(f"Unknown time unit: {unit}")

    def get_execution_status(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get the status of a workflow execution."""
        if execution_id in self.active_executions:
            return self.active_executions[execution_id]
        elif execution_id in self.execution_history:
            return self.execution_history[execution_id]
        return None

    def cancel_execution(self, execution_id: str) -> bool:
        """Cancel a running workflow execution."""
        if execution_id in self.active_executions:
            execution = self.active_executions[execution_id]
            execution.status = WorkflowStatus.CANCELLED
            execution.completed_at = datetime.now()
            return True
        return False

    def get_execution_stats(self) -> Dict[str, Any]:
        """Get workflow execution statistics."""
        return dict(self.execution_stats)

    def list_active_executions(self) -> List[WorkflowExecution]:
        """List all active workflow executions."""
        return list(self.active_executions.values())

    def list_execution_history(self, limit: int = 50) -> List[WorkflowExecution]:
        """List recent workflow execution history."""
        executions = list(self.execution_history.values())
        return sorted(executions, key=lambda x: x.started_at or datetime.min, reverse=True)[:limit]
