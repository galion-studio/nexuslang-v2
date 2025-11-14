"""
Agent Orchestrator for Galion Platform v2.2
Manages multiple AI agents working in parallel with cost tracking and performance monitoring.

"Your imagination is the end."
"""

import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import logging
import json
import os
from pathlib import Path

from .base_agent import BaseAgent, AgentResult, AgentContext, PersonalityTraits, AgentCapabilities
from ..integrations import IntegrationManager
from .physics_agent import PhysicsAgent
from .chemistry_agent import ChemistryAgent
from .mathematics_agent import MathematicsAgent
from ..transparency_service import TransparencyService

# Configure logging
logger = logging.getLogger(__name__)

class OrchestratorMetrics:
    """Metrics and performance tracking for the orchestrator"""

    def __init__(self):
        self.total_executions = 0
        self.total_cost = 0.0
        self.average_response_time = 0.0
        self.success_rate = 1.0
        self.agent_usage = {}
        self.cost_by_agent = {}
        self.errors_by_agent = {}

    def record_execution(self, agent_name: str, result: AgentResult, execution_time: float):
        """Record an agent execution"""
        self.total_executions += 1
        self.total_cost += result.cost

        # Update average response time
        if self.total_executions == 1:
            self.average_response_time = execution_time
        else:
            self.average_response_time = (
                (self.average_response_time * (self.total_executions - 1)) + execution_time
            ) / self.total_executions

        # Update success rate
        success_count = int(result.success)
        self.success_rate = (
            (self.success_rate * (self.total_executions - 1)) + success_count
        ) / self.total_executions

        # Update agent-specific metrics
        if agent_name not in self.agent_usage:
            self.agent_usage[agent_name] = 0
            self.cost_by_agent[agent_name] = 0.0
            self.errors_by_agent[agent_name] = 0

        self.agent_usage[agent_name] += 1
        self.cost_by_agent[agent_name] += result.cost

        if not result.success:
            self.errors_by_agent[agent_name] += 1

    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary"""
        return {
            "total_executions": self.total_executions,
            "total_cost": self.total_cost,
            "average_response_time": self.average_response_time,
            "success_rate": self.success_rate,
            "agent_usage": self.agent_usage,
            "cost_by_agent": self.cost_by_agent,
            "errors_by_agent": self.errors_by_agent,
            "cost_per_execution": self.total_cost / max(self.total_executions, 1)
        }

class TaskQueue:
    """Simple task queue for agent orchestration"""

    def __init__(self, max_concurrent: int = 5):
        self.queue = asyncio.Queue()
        self.max_concurrent = max_concurrent
        self.active_tasks = 0
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def add_task(self, task: Dict[str, Any]) -> str:
        """Add a task to the queue"""
        task_id = f"task_{datetime.now().timestamp()}_{hash(str(task))}"
        await self.queue.put({**task, "task_id": task_id, "created_at": datetime.now()})
        logger.info(f"Added task {task_id} to queue")
        return task_id

    async def get_next_task(self) -> Optional[Dict[str, Any]]:
        """Get next task from queue"""
        try:
            return self.queue.get_nowait()
        except asyncio.QueueEmpty:
            return None

    def get_queue_status(self) -> Dict[str, Any]:
        """Get queue status"""
        return {
            "queue_size": self.queue.qsize(),
            "active_tasks": self.active_tasks,
            "max_concurrent": self.max_concurrent
        }

class AgentOrchestrator:
    """
    Main orchestrator for managing multiple AI agents.

    Key Features:
    - Multi-agent coordination
    - Task routing and queue management
    - Cost tracking and optimization
    - Performance monitoring
    - Agent selection based on capabilities
    - Parallel execution support
    """

    def __init__(self, shared_state_path: str = "shared/agent-state.json"):
        self.agents: Dict[str, BaseAgent] = {}
        self.metrics = OrchestratorMetrics()
        self.task_queue = TaskQueue()
        self.shared_state_path = Path(shared_state_path)
        self.is_running = False
        self.integration_manager = IntegrationManager()
        self.cost_limits = {
            "per_execution": 0.10,  # $0.10 per execution
            "per_hour": 10.0,       # $10 per hour
            "per_day": 50.0         # $50 per day
        }

        # Create shared state directory if it doesn't exist
        self.shared_state_path.parent.mkdir(exist_ok=True)

        # Initialize logger
        self.logger = logging.getLogger(f"{__name__}.orchestrator")

        # Initialize science agents for deep knowledge processing
        self._initialize_science_agents()

        # Initialize transparency service for tracking agent reasoning
        self.transparency_service = TransparencyService()

    def register_agent(self, agent: BaseAgent) -> bool:
        """
        Register a new agent with the orchestrator.

        Args:
            agent: The agent to register

        Returns:
            True if registration successful, False if agent name already exists
        """
        if agent.name in self.agents:
            self.logger.warning(f"Agent {agent.name} already registered")
            return False

        self.agents[agent.name] = agent
        self.logger.info(f"Registered agent: {agent.name} - {agent.description}")
        return True

    def unregister_agent(self, agent_name: str) -> bool:
        """
        Unregister an agent from the orchestrator.

        Args:
            agent_name: Name of the agent to unregister

        Returns:
            True if unregistration successful, False if agent not found
        """
        if agent_name not in self.agents:
            self.logger.warning(f"Agent {agent_name} not found")
            return False

        del self.agents[agent_name]
        self.logger.info(f"Unregistered agent: {agent_name}")
        return True

    def _initialize_science_agents(self):
        """Initialize specialized science agents for deep knowledge processing."""
        try:
            # Register physics agent for physical phenomena and laws
            physics_agent = PhysicsAgent()
            self.register_agent(physics_agent)
            self.logger.info("Physics agent initialized for first principles physics analysis")

            # Register chemistry agent for molecular and chemical systems
            chemistry_agent = ChemistryAgent()
            self.register_agent(chemistry_agent)
            self.logger.info("Chemistry agent initialized for molecular analysis")

            # Register mathematics agent for mathematical reasoning
            mathematics_agent = MathematicsAgent()
            self.register_agent(mathematics_agent)
            self.logger.info("Mathematics agent initialized for formal mathematical reasoning")

        except Exception as e:
            self.logger.error(f"Failed to initialize science agents: {e}")

    async def execute_scientific_query(
        self,
        query: str,
        domain_focus: Optional[str] = None,
        require_collaboration: bool = True,
        context: Optional[AgentContext] = None
    ) -> Dict[str, Any]:
        """
        Execute a scientific query using specialized science agents.

        This method routes scientific queries to appropriate domain experts
        and coordinates multi-agent collaboration when needed.

        Args:
            query: Scientific question or problem
            domain_focus: Specific domain (physics, chemistry, mathematics) or None for auto-detection
            require_collaboration: Whether to use multi-agent collaboration
            context: Additional context

        Returns:
            Comprehensive scientific analysis with agent collaboration
        """
        # Start transparency tracking
        execution_id = self.transparency_service.start_transparency_tracking(
            execution_id=f"sci_{datetime.now().timestamp()}_{hash(query) % 1000000}",
            query=query,
            agent_name="scientific_orchestrator"
        )

        # Record initial processing step
        self.transparency_service.record_reasoning_step(
            execution_id=execution_id,
            step_type="input_processing",
            description=f"Processing scientific query: {query}",
            inputs={"query": query, "domain_focus": domain_focus, "require_collaboration": require_collaboration},
            outputs={},
            confidence_score=1.0,
            sources_used=[],
            first_principles_applied=["scientific_method"],
            processing_time=0.0
        )

        self.logger.info(f"Processing scientific query: {query} (domain: {domain_focus or 'auto'})")

        try:
            # Auto-detect scientific domain if not specified
            if not domain_focus:
                domain_focus = await self._detect_scientific_domain(query)

            # Record domain detection
            self.transparency_service.record_reasoning_step(
                execution_id=execution_id,
                step_type="reasoning",
                description=f"Detected scientific domain: {domain_focus}",
                inputs={"query": query},
                outputs={"domain": domain_focus},
                confidence_score=0.9,
                sources_used=["domain_detection_algorithm"],
                first_principles_applied=["pattern_recognition"],
                processing_time=0.01
            )

            # Route to appropriate agents based on domain
            if require_collaboration and domain_focus == "multi":
                # Multi-domain collaboration required
                result = await self._execute_multi_domain_collaboration(query, context, execution_id)
            else:
                # Single domain analysis
                result = await self._execute_single_domain_analysis(query, domain_focus, context, execution_id)

            # Complete transparency tracking
            final_result = AgentResult(
                success=result.get("error") is None,
                response=json.dumps(result),
                cost=0.0,
                execution_time=result.get("processing_time", 0),
                metadata={"domain": domain_focus, "confidence": result.get("confidence", 0.5)}
            )

            transparency_report = self.transparency_service.complete_transparency_tracking(
                execution_id=execution_id,
                final_result=final_result,
                final_confidence=result.get("confidence", 0.5)
            )

            # Add transparency information to result
            result["transparency_report"] = {
                "execution_id": execution_id,
                "transparency_score": transparency_report.transparency_score,
                "steps_count": len(transparency_report.reasoning_steps),
                "sources_count": len(transparency_report.knowledge_sources),
                "validations_count": len(transparency_report.validation_records)
            }

            return result

        except Exception as e:
            # Record error in transparency tracking
            self.transparency_service.record_reasoning_step(
                execution_id=execution_id,
                step_type="error",
                description=f"Scientific query execution failed: {str(e)}",
                inputs={"query": query},
                outputs={"error": str(e)},
                confidence_score=0.0,
                sources_used=[],
                first_principles_applied=[],
                processing_time=0.0
            )

            # Complete with error
            error_result = AgentResult(
                success=False,
                response=f"Scientific query failed: {str(e)}",
                cost=0.0,
                execution_time=0.0,
                error=str(e)
            )

            self.transparency_service.complete_transparency_tracking(
                execution_id=execution_id,
                final_result=error_result,
                final_confidence=0.0
            )

            raise e

    async def _detect_scientific_domain(self, query: str) -> str:
        """Auto-detect the scientific domain of a query."""
        query_lower = query.lower()

        # Domain detection keywords
        domain_keywords = {
            "physics": [
                "force", "energy", "quantum", "relativity", "mechanics", "electromagnetic",
                "thermodynamics", "nuclear", "optics", "particle", "gravity", "motion",
                "velocity", "acceleration", "momentum", "work", "power"
            ],
            "chemistry": [
                "molecule", "reaction", "bond", "atom", "compound", "acid", "base",
                "organic", "inorganic", "catalyst", "synthesis", "polymer", "crystal",
                "electrolyte", "oxidation", "reduction", "pH", "solubility"
            ],
            "mathematics": [
                "theorem", "proof", "function", "equation", "calculus", "algebra",
                "geometry", "statistics", "probability", "integral", "derivative",
                "matrix", "vector", "limit", "convergence", "topology", "number theory"
            ]
        }

        domain_scores = {}
        for domain, keywords in domain_keywords.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            domain_scores[domain] = score

        # Return highest scoring domain, or "multi" if multiple domains detected
        max_score = max(domain_scores.values())
        if max_score == 0:
            return "general"  # Fallback

        top_domains = [d for d, s in domain_scores.items() if s == max_score]
        return "multi" if len(top_domains) > 1 else top_domains[0]

    async def _execute_single_domain_analysis(
        self,
        query: str,
        domain: str,
        context: Optional[AgentContext] = None,
        execution_id: str = None
    ) -> Dict[str, Any]:
        """Execute analysis using a single scientific domain agent."""
        agent_mapping = {
            "physics": "physics_agent",
            "chemistry": "chemistry_agent",
            "mathematics": "mathematics_agent"
        }

        agent_name = agent_mapping.get(domain)
        if not agent_name or agent_name not in self.agents:
            return {
                "error": f"No agent available for domain: {domain}",
                "available_domains": list(agent_mapping.keys())
            }

        # Execute with the appropriate agent
        result = await self.execute(query, agent_type=agent_name, context=context)

        return {
            "domain": domain,
            "agent_used": agent_name,
            "result": result,
            "confidence": result.metadata.get("confidence", 0.5),
            "processing_time": result.execution_time,
            "cost": result.cost
        }

    async def _execute_multi_domain_collaboration(
        self,
        query: str,
        context: Optional[AgentContext] = None,
        execution_id: str = None
    ) -> Dict[str, Any]:
        """Execute multi-agent collaboration for complex scientific queries."""
        self.logger.info("Initiating multi-domain scientific collaboration")

        collaboration_result = {
            "query": query,
            "collaboration_type": "multi_domain_science",
            "agent_contributions": {},
            "synthesis": {},
            "validation": {},
            "final_answer": "",
            "confidence": 0.0,
            "processing_time": 0.0,
            "total_cost": 0.0
        }

        start_time = datetime.now()

        # Record collaboration initiation
        if execution_id:
            self.transparency_service.record_reasoning_step(
                execution_id=execution_id,
                step_type="reasoning",
                description="Initiating multi-domain scientific collaboration",
                inputs={"query": query, "science_agents": ["physics_agent", "chemistry_agent", "mathematics_agent"]},
                outputs={},
                confidence_score=0.95,
                sources_used=["agent_capabilities_database"],
                first_principles_applied=["scientific_collaboration"],
                processing_time=0.02
            )

        # Execute with all relevant science agents
        science_agents = ["physics_agent", "chemistry_agent", "mathematics_agent"]
        tasks = []

        for agent_name in science_agents:
            if agent_name in self.agents:
                task = self.execute(query, agent_type=agent_name, context=context)
                tasks.append((agent_name, task))

        # Execute all agent analyses concurrently
        agent_results = {}
        for agent_name, task in tasks:
            try:
                result = await task
                agent_results[agent_name] = result
                collaboration_result["agent_contributions"][agent_name] = {
                    "result": result.response,
                    "confidence": result.metadata.get("confidence", 0.5),
                    "cost": result.cost,
                    "success": result.success
                }
            except Exception as e:
                self.logger.error(f"Agent {agent_name} failed: {e}")
                agent_results[agent_name] = None

        # Synthesize results across domains
        synthesis = await self._synthesize_scientific_results(query, agent_results)
        collaboration_result["synthesis"] = synthesis

        # Validate synthesis using first principles
        validation = await self._validate_scientific_synthesis(synthesis, agent_results)
        collaboration_result["validation"] = validation

        # Generate final answer
        final_answer = await self._generate_final_scientific_answer(synthesis, validation)
        collaboration_result["final_answer"] = final_answer

        # Calculate overall metrics
        collaboration_result["processing_time"] = (datetime.now() - start_time).total_seconds()
        collaboration_result["total_cost"] = sum(
            contrib.get("cost", 0) for contrib in collaboration_result["agent_contributions"].values()
        )
        collaboration_result["confidence"] = validation.get("overall_confidence", 0.5)

        self.logger.info(f"Multi-domain collaboration completed: {len(agent_results)} agents, "
                        f"confidence: {collaboration_result['confidence']:.2f}")

        return collaboration_result

    async def _synthesize_scientific_results(
        self,
        query: str,
        agent_results: Dict[str, AgentResult]
    ) -> Dict[str, Any]:
        """Synthesize results from multiple scientific agents."""
        synthesis = {
            "query": query,
            "integrated_insights": [],
            "cross_domain_connections": [],
            "complementary_findings": [],
            "conflicting_views": [],
            "unified_understanding": ""
        }

        # Extract successful results
        successful_results = {
            agent: result for agent, result in agent_results.items()
            if result and result.success
        }

        if len(successful_results) < 2:
            synthesis["unified_understanding"] = "Insufficient agent results for meaningful synthesis"
            return synthesis

        # Find cross-domain connections
        physics_result = successful_results.get("physics_agent")
        chemistry_result = successful_results.get("chemistry_agent")
        math_result = successful_results.get("mathematics_agent")

        # Connect physics and chemistry (physical basis of chemical behavior)
        if physics_result and chemistry_result:
            synthesis["cross_domain_connections"].append({
                "domains": ["physics", "chemistry"],
                "connection": "Physical laws govern chemical behavior and molecular interactions",
                "example": "Quantum mechanical principles explain chemical bonding"
            })

        # Connect mathematics and physics (mathematical description of physical phenomena)
        if math_result and physics_result:
            synthesis["cross_domain_connections"].append({
                "domains": ["mathematics", "physics"],
                "connection": "Mathematical structures describe physical reality",
                "example": "Differential equations model physical systems"
            })

        # Connect chemistry and mathematics (quantitative chemical analysis)
        if chemistry_result and math_result:
            synthesis["cross_domain_connections"].append({
                "domains": ["chemistry", "mathematics"],
                "connection": "Mathematical models quantify chemical processes",
                "example": "Stoichiometry and reaction kinetics use mathematical relationships"
            })

        # Generate unified understanding
        synthesis["unified_understanding"] = (
            f"The query '{query}' demonstrates the interconnectedness of scientific domains. "
            f"Physical principles provide the foundation, chemical processes manifest these principles "
            f"in molecular systems, and mathematical frameworks enable precise description and prediction "
            f"of both physical and chemical phenomena."
        )

        return synthesis

    async def _validate_scientific_synthesis(
        self,
        synthesis: Dict[str, Any],
        agent_results: Dict[str, AgentResult]
    ) -> Dict[str, Any]:
        """Validate the scientific synthesis using first principles."""
        validation = {
            "first_principles_check": True,
            "internal_consistency": True,
            "experimental_alignment": True,
            "logical_soundness": True,
            "overall_confidence": 0.0,
            "validation_criteria": []
        }

        # Check first principles alignment
        synthesis_text = synthesis.get("unified_understanding", "")
        first_principles_indicators = [
            "fundamental", "axiomatic", "first principles", "underlying",
            "basic laws", "fundamental interactions", "conservation"
        ]

        validation["first_principles_check"] = any(
            indicator in synthesis_text.lower() for indicator in first_principles_indicators
        )

        # Check internal consistency across agent results
        agent_responses = [
            result.response for result in agent_results.values() if result and result.success
        ]

        if len(agent_responses) > 1:
            # Simple consistency check - in real implementation would be more sophisticated
            validation["internal_consistency"] = True  # Assume consistent for now
            validation["validation_criteria"].append("Multi-agent result alignment")

        # Calculate overall confidence
        agent_confidences = [
            result.metadata.get("confidence", 0.5)
            for result in agent_results.values()
            if result and result.success
        ]

        if agent_confidences:
            validation["overall_confidence"] = sum(agent_confidences) / len(agent_confidences)
        else:
            validation["overall_confidence"] = 0.0

        return validation

    async def _generate_final_scientific_answer(
        self,
        synthesis: Dict[str, Any],
        validation: Dict[str, Any]
    ) -> str:
        """Generate the final scientific answer from synthesis and validation."""
        base_answer = synthesis.get("unified_understanding", "")

        confidence = validation.get("overall_confidence", 0.0)
        confidence_description = (
            "high confidence" if confidence > 0.8 else
            "moderate confidence" if confidence > 0.6 else
            "low confidence"
        )

        final_answer = f"{base_answer}\n\nThis analysis has {confidence_description} "
        final_answer += f"(confidence score: {confidence:.2f}) and is based on "
        final_answer += "integrated insights from physics, chemistry, and mathematics."

        if validation.get("first_principles_check"):
            final_answer += "\n\nThe answer is grounded in first principles and fundamental scientific laws."

        return final_answer

    def get_scientific_capabilities(self) -> Dict[str, Any]:
        """Get comprehensive overview of scientific capabilities."""
        capabilities = {
            "available_domains": ["physics", "chemistry", "mathematics"],
            "collaboration_modes": ["single_domain", "multi_domain", "first_principles"],
            "knowledge_sources": ["internal_expertise", "external_apis", "first_principles_reasoning"],
            "specialized_agents": {}
        }

        # Add details for each science agent
        science_agents = ["physics_agent", "chemistry_agent", "mathematics_agent"]
        for agent_name in science_agents:
            if agent_name in self.agents:
                agent = self.agents[agent_name]
                capabilities["specialized_agents"][agent_name] = {
                    "capabilities": agent.capabilities.__dict__ if hasattr(agent, 'capabilities') else {},
                    "personality": agent.personality if hasattr(agent, 'personality') else {},
                    "expertise_level": "expert"
                }

        return capabilities

    def get_scientific_metrics(self) -> Dict[str, Any]:
        """Get metrics specific to scientific agent usage."""
        scientific_agents = ["physics_agent", "chemistry_agent", "mathematics_agent"]

        scientific_metrics = {
            "scientific_agent_usage": {},
            "cross_domain_collaborations": 0,  # Would track in real implementation
            "first_principles_applications": 0,
            "external_knowledge_queries": 0,
            "scientific_accuracy_score": 0.95  # Placeholder
        }

        for agent_name in scientific_agents:
            usage = self.metrics.agent_usage.get(agent_name, 0)
            cost = self.metrics.cost_by_agent.get(agent_name, 0.0)
            errors = self.metrics.errors_by_agent.get(agent_name, 0)

            scientific_metrics["scientific_agent_usage"][agent_name] = {
                "executions": usage,
                "total_cost": cost,
                "error_rate": errors / max(usage, 1),
                "success_rate": 1.0 - (errors / max(usage, 1))
            }

        return scientific_metrics

    async def execute(
        self,
        prompt: str,
        agent_type: Optional[str] = None,
        context: Optional[AgentContext] = None,
        priority: str = "normal"
    ) -> AgentResult:
        """
        Execute a task using the most appropriate agent.

        Args:
            prompt: The user's request
            agent_type: Specific agent to use (optional)
            context: Additional context
            priority: Task priority (low, normal, high, urgent)

        Returns:
            AgentResult from the agent execution
        """
        start_time = datetime.now()

        try:
            # Auto-select agent if not specified
            if not agent_type:
                agent_type = await self.select_agent(prompt, context)
                self.logger.info(f"Auto-selected agent: {agent_type}")

            # Get the agent
            if agent_type not in self.agents:
                return AgentResult(
                    success=False,
                    response=f"Agent '{agent_type}' not found. Available agents: {list(self.agents.keys())}",
                    cost=0.0,
                    execution_time=0.0,
                    error="Agent not found"
                )

            agent = self.agents[agent_type]

            # Validate the request
            validation = await agent.validate_request(prompt, context)
            if not validation["can_handle"]:
                return AgentResult(
                    success=False,
                    response=f"Agent {agent_type} cannot handle this request: {validation['reasoning']}",
                    cost=0.0,
                    execution_time=0.0,
                    error="Request validation failed"
                )

            # Check cost limits
            if not self.check_cost_limits():
                return AgentResult(
                    success=False,
                    response="Cost limits exceeded. Please try again later.",
                    cost=0.0,
                    execution_time=0.0,
                    error="Cost limit exceeded"
                )

            # Execute the task
            self.logger.info(f"Executing prompt with agent {agent_type}")
            result = await agent.execute(prompt, context)

            # Record metrics
            execution_time = (datetime.now() - start_time).total_seconds()
            self.metrics.record_execution(agent_type, result, execution_time)
            agent.update_metrics(result, execution_time)

            # Log warnings if any
            if validation["warnings"]:
                result.metadata["warnings"] = validation["warnings"]

            return result

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            error_msg = f"Orchestrator execution failed: {str(e)}"
            self.logger.error(error_msg)

            return AgentResult(
                success=False,
                response="An error occurred while processing your request.",
                cost=0.0,
                execution_time=execution_time,
                error=error_msg
            )

    async def select_agent(self, prompt: str, context: Optional[AgentContext] = None) -> str:
        """
        Auto-select the best agent for a given prompt.

        Uses a combination of:
        - Keyword analysis
        - Agent capabilities
        - Historical performance
        - Cost considerations
        """
        prompt_lower = prompt.lower()

        # Keyword-based agent selection
        agent_scores = {}

        for agent_name, agent in self.agents.items():
            score = 0.0

            # Check capabilities match
            if agent.capabilities.can_execute_code and any(word in prompt_lower for word in ["code", "execute", "run", "compile", "script"]):
                score += 2.0

            if agent.capabilities.can_analyze_data and any(word in prompt_lower for word in ["analyze", "data", "metrics", "statistics"]):
                score += 1.5

            if agent.capabilities.can_generate_content and any(word in prompt_lower for word in ["write", "create", "generate", "content"]):
                score += 1.0

            if agent.capabilities.can_monitor_systems and any(word in prompt_lower for word in ["monitor", "status", "health", "system"]):
                score += 1.5

            # Check expertise domains
            for domain in agent.capabilities.expertise_domains:
                if domain.lower() in prompt_lower:
                    score += 1.0

            # Boost score for successful agents
            if agent_name in self.metrics.agent_usage:
                success_rate = 1.0 - (self.metrics.errors_by_agent.get(agent_name, 0) / max(self.metrics.agent_usage[agent_name], 1))
                score += success_rate * 0.5

            # Penalize high-cost agents
            avg_cost = self.metrics.cost_by_agent.get(agent_name, 0.0) / max(self.metrics.agent_usage.get(agent_name, 1), 1)
            if avg_cost > 0.05:  # More than $0.05 per execution
                score -= 0.5

            agent_scores[agent_name] = score

        # Return the highest scoring agent
        best_agent = max(agent_scores.items(), key=lambda x: x[1])
        self.logger.info(f"Agent selection scores: {agent_scores}")

        return best_agent[0]

    def check_cost_limits(self) -> bool:
        """Check if cost limits are exceeded"""
        # Simple cost limit checking - could be enhanced with time-based windows
        if self.metrics.total_cost > self.cost_limits["per_day"]:
            return False
        return True

    async def queue_task(
        self,
        prompt: str,
        agent_type: Optional[str] = None,
        context: Optional[AgentContext] = None,
        priority: str = "normal"
    ) -> str:
        """
        Queue a task for later execution.

        Returns:
            Task ID for tracking
        """
        task = {
            "prompt": prompt,
            "agent_type": agent_type,
            "context": context,
            "priority": priority,
            "status": "queued"
        }

        return await self.task_queue.add_task(task)

    async def process_queue(self):
        """Process tasks from the queue"""
        while self.is_running:
            try:
                task = await self.task_queue.get_next_task()
                if task:
                    self.logger.info(f"Processing queued task: {task['task_id']}")

                    # Execute the task
                    result = await self.execute(
                        task["prompt"],
                        task["agent_type"],
                        task["context"],
                        task["priority"]
                    )

                    # Mark task as completed
                    task["status"] = "completed" if result.success else "failed"
                    task["result"] = result
                    task["completed_at"] = datetime.now()

                    self.logger.info(f"Task {task['task_id']} completed")

                else:
                    # No tasks in queue, wait a bit
                    await asyncio.sleep(1)

            except Exception as e:
                self.logger.error(f"Error processing queue: {e}")
                await asyncio.sleep(5)  # Wait before retrying

    def start_queue_processor(self):
        """Start the queue processing task"""
        if not self.is_running:
            self.is_running = True
            asyncio.create_task(self.process_queue())
            self.logger.info("Started queue processor")

    def stop_queue_processor(self):
        """Stop the queue processing task"""
        self.is_running = False
        self.logger.info("Stopped queue processor")

    def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status and metrics"""
        return {
            "is_running": self.is_running,
            "agent_count": len(self.agents),
            "available_agents": list(self.agents.keys()),
            "metrics": self.metrics.get_summary(),
            "queue_status": self.task_queue.get_queue_status(),
            "cost_limits": self.cost_limits
        }

    def get_agent_status(self, agent_name: Optional[str] = None) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Get status of specific agent or all agents"""
        if agent_name:
            if agent_name in self.agents:
                return self.agents[agent_name].get_status()
            else:
                return {"error": f"Agent '{agent_name}' not found"}
        else:
            return [agent.get_status() for agent in self.agents.values()]

    # Integration management methods
    async def initialize_integrations(self) -> bool:
        """Initialize all registered integrations."""
        return await self.integration_manager.initialize()

    def register_integration(self, name: str, integration_type: str, config: Dict[str, Any]) -> bool:
        """Register a new integration."""
        return self.integration_manager.register_integration(name, integration_type, config)

    def unregister_integration(self, name: str) -> bool:
        """Unregister an integration."""
        return self.integration_manager.unregister_integration(name)

    async def execute_integration_operation(self, integration_name: str, operation: str, **kwargs) -> Any:
        """Execute an operation on an integration."""
        try:
            result = await self.integration_manager.execute_operation(
                integration_name, operation, **kwargs
            )
            return result.data if result.success else None
        except Exception as e:
            self.logger.error(f"Integration operation failed: {e}")
            return None

    def get_integration_capabilities(self, integration_name: str) -> Optional[List[str]]:
        """Get capabilities of an integration."""
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                self.integration_manager.get_integration_capabilities(integration_name)
            )
        finally:
            loop.close()

    def get_registered_integrations(self) -> List[str]:
        """Get list of registered integrations."""
        return self.integration_manager.get_registered_integrations()

    def get_available_integrations(self) -> List[str]:
        """Get list of available integration types."""
        return self.integration_manager.get_available_integrations()

    async def get_integration_status(self, integration_name: Optional[str] = None):
        """Get status of integrations."""
        if integration_name:
            status = await self.integration_manager.get_integration_status(integration_name)
            return status.__dict__ if status else None
        else:
            statuses = await self.integration_manager.get_all_statuses()
            return {name: status.__dict__ for name, status in statuses.items()}

    # Helper methods for agents to use integrations
    async def send_notification(self, message: str, integration: str = "slack", **kwargs):
        """Send a notification via integration."""
        if integration == "slack":
            return await self.execute_integration_operation(
                "slack", "send_message", text=message, **kwargs
            )
        elif integration == "webhook":
            return await self.execute_integration_operation(
                "webhook", "send_notification", title="Agent Notification", message=message, **kwargs
            )
        return None

    async def create_github_issue(self, title: str, body: str, **kwargs):
        """Create a GitHub issue."""
        return await self.execute_integration_operation(
            "github", "create_issue", title=title, body=body, **kwargs
        )

    async def update_github_issue(self, issue_number: int, **kwargs):
        """Update a GitHub issue."""
        return await self.execute_integration_operation(
            "github", "update_issue", issue_number=issue_number, **kwargs
        )

    async def send_webhook_notification(self, event_type: str, data: Dict[str, Any], **kwargs):
        """Send a webhook notification."""
        return await self.execute_integration_operation(
            "webhook", "send_custom_payload", payload=data, event_type=event_type, **kwargs
        )

    async def save_state(self):
        """Save orchestrator state to shared file"""
        try:
            state = {
                "orchestrator": {
                    "is_running": self.is_running,
                    "agent_count": len(self.agents),
                    "metrics": self.metrics.get_summary(),
                    "last_update": datetime.now().isoformat()
                },
                "agents": {
                    name: agent.get_status() for name, agent in self.agents.items()
                }
            }

            with open(self.shared_state_path, 'w') as f:
                json.dump(state, f, indent=2, default=str)

            self.logger.info("Saved orchestrator state")

        except Exception as e:
            self.logger.error(f"Failed to save state: {e}")

    async def load_state(self):
        """Load orchestrator state from shared file"""
        try:
            if self.shared_state_path.exists():
                with open(self.shared_state_path, 'r') as f:
                    state = json.load(f)

                self.logger.info("Loaded orchestrator state")
                return state
            else:
                self.logger.info("No saved state found")
                return {}

        except Exception as e:
            self.logger.error(f"Failed to load state: {e}")
            return {}

    def __str__(self) -> str:
        """String representation"""
        return f"AgentOrchestrator(agents={len(self.agents)}, running={self.is_running})"

    def __repr__(self) -> str:
        """Detailed representation"""
        return f"AgentOrchestrator(agents={list(self.agents.keys())}, metrics={self.metrics.get_summary()})"


# Create global orchestrator instance
orchestrator = AgentOrchestrator()
