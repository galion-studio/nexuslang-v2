"""
Agent Orchestrator for Deep Search System
Based on MushroomFleet/deep-search-persona architecture
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from .base_agent import BaseAgent, AgentResult, AgentState
from .planner_agent import PlannerAgent
from .searcher_agent import SearcherAgent
from .analyzer_agent import AnalyzerAgent
from ..workflow.state_machine import StateMachine, ResearchState

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Orchestrates multiple agents for deep research tasks

    Manages the execution flow:
    1. Planner Agent: Creates research plan
    2. Searcher Agent: Gathers information
    3. Analyzer Agent: Synthesizes findings

    Provides parallel execution and result aggregation
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.agents = {}
        self.state_machine = StateMachine(self.config.get('workflow', {}))

        # Initialize specialized agents
        self._initialize_agents()

        logger.info("Agent Orchestrator initialized with adaptive workflow")

    def _initialize_agents(self):
        """Initialize all specialized agents"""
        agent_configs = self.config.get('agents', {})

        # Planner Agent - Creates research strategy
        self.agents['planner'] = PlannerAgent(
            config=agent_configs.get('planner', {})
        )

        # Searcher Agent - Finds and retrieves information
        self.agents['searcher'] = SearcherAgent(
            config=agent_configs.get('searcher', {})
        )

        # Analyzer Agent - Analyzes and synthesizes information
        self.agents['analyzer'] = AnalyzerAgent(
            config=agent_configs.get('analyzer', {})
        )

    async def execute_research(
        self,
        query: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Execute complete research workflow using adaptive state machine

        Args:
            query: Research query
            context: Additional context (persona, depth, etc.)

        Returns:
            Dict containing synthesized answer and metadata
        """
        context = context or {}

        try:
            logger.info(f"Starting adaptive deep research for query: {query}")

            # Prepare initial workflow data
            workflow_data = {
                "query": query,
                "context": context,
                "workflow_type": "deep_research"
            }

            # Execute adaptive workflow
            workflow_result = await self.state_machine.execute_workflow(
                workflow_data, self
            )

            if not workflow_result.success:
                return self._create_error_response(
                    f"Workflow failed: {workflow_result.final_state.value}"
                )

            # Extract final results
            final_data = workflow_result.data
            synthesized_answer = (
                final_data.get('synthesized_answer') or
                final_data.get('final_answer') or
                "I apologize, but I was unable to generate a comprehensive answer from the available information."
            )

            # Prepare response
            response = {
                "query": query,
                "synthesized_answer": synthesized_answer,
                "sources_used": final_data.get('sources_used', []),
                "metadata": {
                    "workflow_path": workflow_result.execution_path,
                    "adaptation_decisions": workflow_result.adaptation_decisions,
                    "iterations": workflow_result.metadata.get('iterations', 0),
                    "processing_phases": workflow_result.execution_path
                },
                "confidence_score": final_data.get('confidence_score', 0.0),
                "processing_time": workflow_result.total_time,
                "agent_stats": final_data.get('agent_stats', {}),
                "persona_used": context.get('persona', 'default'),
                "depth_used": context.get('depth', 'comprehensive'),
                "quality_metrics": workflow_result.quality_metrics
            }

            logger.info(f"Adaptive research completed: {len(response['sources_used'])} sources, "
                       f"confidence {response['confidence_score']:.2f} in {response['processing_time']:.2f}s")

            return response

        except Exception as e:
            logger.error(f"Adaptive research orchestration failed: {e}", exc_info=True)
            return self._create_error_response(f"Research failed: {str(e)}")

    def _deduplicate_sources(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate sources based on content similarity"""
        if len(sources) <= 1:
            return sources

        deduplicated = []
        seen_titles = set()

        for source in sources:
            title = source.get('title', '').lower().strip()
            if title and title not in seen_titles:
                seen_titles.add(title)
                deduplicated.append(source)

        return deduplicated[:20]  # Limit to top 20 sources

    def _calculate_confidence_score(
        self,
        search_results: List[AgentResult],
        analysis_result: AgentResult,
        sources_count: int
    ) -> float:
        """Calculate overall confidence score"""
        base_score = 0.5

        # Factor 1: Number of successful searches
        search_factor = min(len(search_results) / 3, 1.0) * 0.3

        # Factor 2: Number of sources found
        source_factor = min(sources_count / 10, 1.0) * 0.4

        # Factor 3: Analysis success
        analysis_factor = 0.3 if analysis_result.success else 0.0

        confidence = base_score + search_factor + source_factor + analysis_factor
        return min(confidence, 1.0)

    def _collect_agent_stats(self, results: List[AgentResult]) -> Dict[str, Any]:
        """Collect statistics from all agent executions"""
        total_credits = sum(result.credits_used for result in results)
        total_time = sum(result.execution_time for result in results)
        successful_agents = sum(1 for result in results if result.success)

        return {
            "total_agents": len(results),
            "successful_agents": successful_agents,
            "failed_agents": len(results) - successful_agents,
            "total_credits_used": total_credits,
            "total_execution_time": total_time,
            "agents_executed": [result.agent_name for result in results]
        }

    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create standardized error response"""
        return {
            "query": "",
            "synthesized_answer": f"I apologize, but I encountered an error during research: {error_message}",
            "sources_used": [],
            "metadata": {"error": error_message},
            "confidence_score": 0.0,
            "processing_time": 0.0,
            "agent_stats": {},
            "persona_used": "error",
            "depth_used": "error"
        }

    def calculate_research_credits(
        self,
        depth: str,
        processing_time: float,
        sources_count: int
    ) -> float:
        """Calculate credits used for research based on complexity"""
        base_credits = {
            "quick": 5.0,
            "comprehensive": 15.0,
            "exhaustive": 25.0
        }.get(depth, 15.0)

        # Add credits based on processing time (longer = more complex)
        time_bonus = min(processing_time / 60 * 2, 10.0)  # Max 10 credits for time

        # Add credits based on sources analyzed
        source_bonus = min(sources_count / 5 * 1, 5.0)  # Max 5 credits for sources

        return base_credits + time_bonus + source_bonus

    async def _handle_planning(self, workflow_data: Dict[str, Any],
                             agent_orchestrator: Any) -> Dict[str, Any]:
        """Handle planning state"""
        query = workflow_data.get("query", "")
        context = workflow_data.get("context", {})

        # Use planner agent to create research plan
        try:
            plan_result = await self.agents['planner']._execute_with_monitoring(
                input_data={"query": query, "context": context},
                context=context
            )

            return {"data": plan_result.data}

        except Exception as e:
            return {"error": f"Planning failed: {e}"}

    async def _handle_searching(self, workflow_data: Dict[str, Any],
                               agent_orchestrator: Any) -> Dict[str, Any]:
        """Handle searching state"""
        query = workflow_data.get("query", "")
        context = workflow_data.get("context", {})

        try:
            # Use searcher agent to find information
            search_result = await self.agents['searcher']._execute_with_monitoring(
                input_data={"query": query, "context": context},
                context=context
            )

            return {"data": search_result.data}

        except Exception as e:
            return {"error": f"Searching failed: {e}"}

    async def _handle_analyzing(self, workflow_data: Dict[str, Any],
                               agent_orchestrator: Any) -> Dict[str, Any]:
        """Handle analyzing state"""
        sources = workflow_data.get("sources", [])
        query = workflow_data.get("query", "")
        context = workflow_data.get("context", {})

        if not sources:
            return {"error": "No sources to analyze"}

        try:
            # Use analyzer agent to synthesize information
            analysis_result = await self.agents['analyzer']._execute_with_monitoring(
                input_data={
                    "query": query,
                    "sources": sources,
                    "context": context
                },
                context=context
            )

            return {"data": analysis_result.data}

        except Exception as e:
            return {"error": f"Analysis failed: {e}"}

    async def _handle_validating(self, workflow_data: Dict[str, Any],
                                agent_orchestrator: Any) -> Dict[str, Any]:
        """Handle validating state"""
        facts = workflow_data.get("key_information", {}).get("main_points", [])
        sources = workflow_data.get("sources", [])

        try:
            # Use fact checker for validation
            from ..validation.fact_checker import FactChecker
            fact_checker = FactChecker()

            validation_report = await fact_checker.validate_facts(facts, sources)

            return {
                "data": {
                    "validation_report": validation_report,
                    "confidence_score": validation_report.overall_confidence
                }
            }

        except Exception as e:
            return {"error": f"Validation failed: {e}"}

    async def _handle_synthesizing(self, workflow_data: Dict[str, Any],
                                  agent_orchestrator: Any) -> Dict[str, Any]:
        """Handle synthesizing state"""
        # Synthesis is typically handled by the analyzer, but we can do final formatting here
        synthesized_answer = workflow_data.get("synthesized_answer", "")

        if not synthesized_answer:
            return {"error": "No synthesized answer to finalize"}

        # Final formatting and quality checks
        final_answer = self._finalize_synthesis(synthesized_answer, workflow_data)

        return {
            "data": {
                "final_answer": final_answer,
                "synthesis_complete": True
            }
        }

    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        return {
            agent_name: agent.get_status()
            for agent_name, agent in self.agents.items()
        }

    def reset_agents(self):
        """Reset all agents to initial state"""
        for agent in self.agents.values():
            agent.reset()
        logger.info("All agents reset")

    def _finalize_synthesis(self, answer: str, workflow_data: Dict[str, Any]) -> str:
        """Finalize the synthesis with formatting and quality improvements"""
        # Add source citations if available
        sources = workflow_data.get("sources_used", [])
        if sources:
            answer += "\n\n**Sources:**"
            for i, source in enumerate(sources[:5], 1):
                title = source.get('title', f'Source {i}')
                answer += f"\n{i}. {title}"

        # Add confidence note
        confidence = workflow_data.get("confidence_score", 0.0)
        if confidence < 0.7:
            answer += f"\n\n*Note: This response has a confidence score of {confidence:.1%} based on available sources.*"

        return answer
