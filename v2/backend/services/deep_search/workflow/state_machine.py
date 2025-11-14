"""
Adaptive State Machine for Deep Search Workflows
Based on MushroomFleet/deep-search-persona architecture

Implements dynamic research workflows that adapt based on:
- Quality of results
- Confidence scores
- Time constraints
- Resource availability
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ResearchState(Enum):
    """Research workflow states"""
    INITIALIZING = "initializing"
    PLANNING = "planning"
    SEARCHING = "searching"
    ANALYZING = "analyzing"
    VALIDATING = "validating"
    SYNTHESIZING = "synthesizing"
    COMPLETED = "completed"
    FAILED = "failed"
    STUCK = "stuck"


@dataclass
class WorkflowResult:
    """Result of a workflow execution"""
    final_state: ResearchState
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    execution_path: List[ResearchState]
    quality_metrics: Dict[str, Any]
    adaptation_decisions: List[Dict[str, Any]]
    total_time: float
    success: bool


class StateMachine:
    """
    Adaptive state machine for research workflows

    Features:
    - Dynamic state transitions based on quality metrics
    - Backtracking when quality is insufficient
    - Parallel execution capabilities
    - Quality-based decision making
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.current_state = ResearchState.INITIALIZING
        self.execution_history: List[ResearchState] = []
        self.quality_thresholds = self.config.get('quality_thresholds', {
            'min_confidence': 0.6,
            'min_sources': 3,
            'max_iterations': 5,
            'quality_improvement_required': 0.1
        })

        # State handlers
        self.state_handlers: Dict[ResearchState, Callable] = {
            ResearchState.PLANNING: self._handle_planning,
            ResearchState.SEARCHING: self._handle_searching,
            ResearchState.ANALYZING: self._handle_analyzing,
            ResearchState.VALIDATING: self._handle_validating,
            ResearchState.SYNTHESIZING: self._handle_synthesizing
        }

        # Transition rules
        self.transition_rules = self._define_transition_rules()

        logger.info("Initialized adaptive state machine")

    def _define_transition_rules(self) -> Dict[ResearchState, Dict[str, ResearchState]]:
        """Define state transition rules"""
        return {
            ResearchState.INITIALIZING: {
                "success": ResearchState.PLANNING,
                "error": ResearchState.FAILED
            },
            ResearchState.PLANNING: {
                "success": ResearchState.SEARCHING,
                "error": ResearchState.FAILED,
                "insufficient_info": ResearchState.SEARCHING  # Skip to search if planning gives minimal info
            },
            ResearchState.SEARCHING: {
                "success": ResearchState.ANALYZING,
                "insufficient_results": ResearchState.SEARCHING,  # Retry search with different queries
                "error": ResearchState.FAILED
            },
            ResearchState.ANALYZING: {
                "success": ResearchState.VALIDATING,
                "low_quality": ResearchState.SEARCHING,  # Go back to search for better sources
                "error": ResearchState.FAILED
            },
            ResearchState.VALIDATING: {
                "success": ResearchState.SYNTHESIZING,
                "contradictions_found": ResearchState.ANALYZING,  # Re-analyze with validation in mind
                "insufficient_validation": ResearchState.SEARCHING,  # Get more sources
                "error": ResearchState.FAILED
            },
            ResearchState.SYNTHESIZING: {
                "success": ResearchState.COMPLETED,
                "incomplete_synthesis": ResearchState.ANALYZING,  # Need better analysis
                "error": ResearchState.FAILED
            }
        }

    async def execute_workflow(self, input_data: Dict[str, Any],
                             agent_orchestrator: Any) -> WorkflowResult:
        """
        Execute the complete research workflow

        Args:
            input_data: Initial workflow data
            agent_orchestrator: Agent orchestrator for executing tasks

        Returns:
            WorkflowResult with complete execution details
        """
        start_time = asyncio.get_event_loop().time()
        self.current_state = ResearchState.INITIALIZING
        self.execution_history = [self.current_state]

        workflow_data = input_data.copy()
        adaptation_decisions = []
        iteration_count = 0
        max_iterations = self.quality_thresholds['max_iterations']

        try:
            while self.current_state not in [ResearchState.COMPLETED, ResearchState.FAILED, ResearchState.STUCK]:
                iteration_count += 1

                # Check for infinite loops
                if iteration_count > max_iterations:
                    self.current_state = ResearchState.STUCK
                    break

                # Execute current state
                state_result = await self._execute_state(workflow_data, agent_orchestrator)

                # Evaluate quality and decide next state
                quality_assessment = self._assess_quality(state_result, workflow_data)

                # Determine transition
                transition_decision = self._decide_transition(
                    self.current_state, quality_assessment, workflow_data
                )

                adaptation_decisions.append({
                    "iteration": iteration_count,
                    "from_state": self.current_state.value,
                    "to_state": transition_decision["next_state"].value,
                    "reason": transition_decision["reason"],
                    "quality_metrics": quality_assessment
                })

                # Update state and data
                self.current_state = transition_decision["next_state"]
                self.execution_history.append(self.current_state)

                # Update workflow data with state results
                workflow_data.update(state_result.get("data", {}))

                # Check for completion conditions
                if self._is_workflow_complete(workflow_data, quality_assessment):
                    self.current_state = ResearchState.COMPLETED
                    self.execution_history.append(self.current_state)
                    break

            # Calculate final metrics
            total_time = asyncio.get_event_loop().time() - start_time
            quality_metrics = self._calculate_final_quality_metrics(workflow_data)

            success = self.current_state == ResearchState.COMPLETED

            result = WorkflowResult(
                final_state=self.current_state,
                data=workflow_data,
                metadata={
                    "iterations": iteration_count,
                    "total_states_visited": len(self.execution_history),
                    "unique_states": len(set(self.execution_history))
                },
                execution_path=[state.value for state in self.execution_history],
                quality_metrics=quality_metrics,
                adaptation_decisions=adaptation_decisions,
                total_time=total_time,
                success=success
            )

            logger.info(f"Workflow completed: {self.current_state.value} in {total_time:.2f}s")
            return result

        except Exception as e:
            total_time = asyncio.get_event_loop().time() - start_time
            logger.error(f"Workflow execution failed: {e}")

            return WorkflowResult(
                final_state=ResearchState.FAILED,
                data=workflow_data,
                metadata={"error": str(e)},
                execution_path=[state.value for state in self.execution_history],
                quality_metrics={},
                adaptation_decisions=adaptation_decisions,
                total_time=total_time,
                success=False
            )

    async def _execute_state(self, workflow_data: Dict[str, Any],
                           agent_orchestrator: Any) -> Dict[str, Any]:
        """Execute the current state using appropriate handlers"""
        handler = self.state_handlers.get(self.current_state)

        if not handler:
            return {"error": f"No handler for state {self.current_state}"}

        try:
            return await handler(workflow_data, agent_orchestrator)
        except Exception as e:
            logger.error(f"State execution failed for {self.current_state}: {e}")
            return {"error": str(e), "state": self.current_state.value}

    async def _handle_planning(self, workflow_data: Dict[str, Any],
                             agent_orchestrator: Any) -> Dict[str, Any]:
        """Handle planning state"""
        query = workflow_data.get("query", "")
        context = workflow_data.get("context", {})

        # Use planner agent to create research plan
        plan_data = {"query": query, "context": context}

        try:
            # This would integrate with the planner agent
            # For now, return basic planning result
            planning_result = {
                "research_plan": {
                    "search_queries": [query],  # Would be expanded by planner agent
                    "expected_complexity": "medium",
                    "estimated_sources": 5
                },
                "confidence": 0.8
            }

            return {"data": planning_result}

        except Exception as e:
            return {"error": f"Planning failed: {e}"}

    async def _handle_searching(self, workflow_data: Dict[str, Any],
                               agent_orchestrator: Any) -> Dict[str, Any]:
        """Handle searching state"""
        query = workflow_data.get("query", "")
        context = workflow_data.get("context", {})

        try:
            # Use searcher agent to find information
            search_result = await agent_orchestrator._agents['searcher']._execute_with_monitoring(
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
            analysis_result = await agent_orchestrator._agents['analyzer']._execute_with_monitoring(
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

    def _assess_quality(self, state_result: Dict[str, Any],
                       workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the quality of the current state result"""
        quality_metrics = {
            "confidence_score": 0.0,
            "source_count": 0,
            "information_density": 0.0,
            "contradiction_level": 0.0,
            "completeness_score": 0.0
        }

        data = state_result.get("data", {})

        # Assess based on current state
        if self.current_state == ResearchState.SEARCHING:
            sources = data.get("sources", [])
            quality_metrics["source_count"] = len(sources)
            quality_metrics["confidence_score"] = min(len(sources) / 5, 1.0)  # 5+ sources = high confidence

        elif self.current_state == ResearchState.ANALYZING:
            synthesized_answer = data.get("synthesized_answer", "")
            quality_metrics["information_density"] = len(synthesized_answer.split()) / 100  # Words per 100 expected
            quality_metrics["confidence_score"] = data.get("confidence_score", 0.0)

        elif self.current_state == ResearchState.VALIDATING:
            validation_report = data.get("validation_report")
            if validation_report:
                quality_metrics["confidence_score"] = validation_report.overall_confidence
                quality_metrics["contradiction_level"] = validation_report.uncertain_facts / max(validation_report.facts_validated, 1)

        return quality_metrics

    def _decide_transition(self, current_state: ResearchState,
                          quality_assessment: Dict[str, Any],
                          workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Decide the next state based on quality assessment"""

        confidence = quality_assessment.get("confidence_score", 0.0)
        min_confidence = self.quality_thresholds['min_confidence']

        # Default transition
        rules = self.transition_rules.get(current_state, {})
        next_state = rules.get("success", ResearchState.FAILED)
        reason = "default_success"

        # Adaptive decisions based on quality
        if current_state == ResearchState.SEARCHING:
            source_count = quality_assessment.get("source_count", 0)
            if source_count < self.quality_thresholds['min_sources']:
                next_state = rules.get("insufficient_results", ResearchState.SEARCHING)
                reason = f"insufficient_sources_{source_count}"
            elif confidence < min_confidence:
                next_state = ResearchState.SEARCHING
                reason = f"low_confidence_{confidence:.2f}"

        elif current_state == ResearchState.ANALYZING:
            if confidence < min_confidence:
                next_state = rules.get("low_quality", ResearchState.SEARCHING)
                reason = f"analysis_quality_insufficient_{confidence:.2f}"

        elif current_state == ResearchState.VALIDATING:
            contradiction_level = quality_assessment.get("contradiction_level", 0.0)
            if contradiction_level > 0.3:  # High contradiction level
                next_state = rules.get("contradictions_found", ResearchState.ANALYZING)
                reason = f"high_contradictions_{contradiction_level:.2f}"
            elif confidence < min_confidence:
                next_state = rules.get("insufficient_validation", ResearchState.SEARCHING)
                reason = f"validation_confidence_low_{confidence:.2f}"

        return {
            "next_state": next_state,
            "reason": reason,
            "confidence": confidence
        }

    def _is_workflow_complete(self, workflow_data: Dict[str, Any],
                            quality_assessment: Dict[str, Any]) -> bool:
        """Check if the workflow should be considered complete"""
        # Check if we have a synthesized answer with sufficient quality
        synthesized_answer = workflow_data.get("synthesized_answer", "")
        confidence = quality_assessment.get("confidence_score", 0.0)

        has_answer = len(synthesized_answer.strip()) > 100  # At least 100 chars
        sufficient_quality = confidence >= self.quality_thresholds['min_confidence']

        return has_answer and sufficient_quality

    def _finalize_synthesis(self, answer: str, workflow_data: Dict[str, Any]) -> str:
        """Finalize the synthesis with formatting and quality improvements"""
        # Add source citations if available
        sources = workflow_data.get("sources_used", [])
        if sources:
            answer += "\n\n**Sources:**"
            for i, source in enumerate(sources[:5], 1):  # Limit to 5 sources
                title = source.get("title", f"Source {i}")
                answer += f"\n{i}. {title}"

        # Add confidence note
        confidence = workflow_data.get("confidence_score", 0.0)
        if confidence < 0.7:
            answer += f"\n\n*Note: This response has a confidence score of {confidence:.1%} based on available sources.*"

        return answer

    def _calculate_final_quality_metrics(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate final quality metrics for the workflow"""
        return {
            "final_answer_length": len(workflow_data.get("synthesized_answer", "")),
            "sources_used": len(workflow_data.get("sources_used", [])),
            "validation_score": workflow_data.get("confidence_score", 0.0),
            "workflow_efficiency": len(workflow_data.get("execution_path", [])),
            "adaptation_events": len(workflow_data.get("adaptation_decisions", []))
        }

    def get_workflow_stats(self) -> Dict[str, Any]:
        """Get workflow execution statistics"""
        return {
            "current_state": self.current_state.value,
            "execution_history": [state.value for state in self.execution_history],
            "total_states": len(self.execution_history),
            "unique_states": len(set(self.execution_history)),
            "quality_thresholds": self.quality_thresholds
        }
