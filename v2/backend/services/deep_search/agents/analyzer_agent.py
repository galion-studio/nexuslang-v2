"""
Analyzer Agent for Deep Search System
Synthesizes and analyzes information from multiple sources
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

from .base_agent import BaseAgent, AgentResult, AgentState
from ..personas.persona_manager import PersonaManager

logger = logging.getLogger(__name__)


class AnalyzerAgent(BaseAgent):
    """
    Agent responsible for analyzing and synthesizing information

    Capabilities:
    - Information synthesis from multiple sources
    - Cross-validation of facts
    - Persona-based response generation
    - Confidence scoring and uncertainty handling
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("analyzer", config)

    def _initialize(self):
        """Initialize analyzer-specific components"""
        self.synthesis_strategies = [
            "consensus_based",
            "authority_weighted",
            "recency_weighted",
            "comprehensive_merge"
        ]
        self.persona_manager = PersonaManager()

    async def execute(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> AgentResult:
        """
        Analyze and synthesize information from sources

        Args:
            input_data: Contains query, sources, and research plan
            context: Additional context including persona and depth

        Returns:
            AgentResult with synthesized answer
        """
        query = input_data.get("query", "")
        sources = input_data.get("sources", [])
        research_plan = input_data.get("research_plan", {})
        context = context or {}

        if not sources:
            return AgentResult(
                agent_name=self.name,
                state=AgentState.FAILED,
                data={},
                metadata={"error": "No sources provided for analysis"},
                execution_time=0.0,
                credits_used=0.0,
                success=False,
                error_message="Analysis requires source information"
            )

        try:
            # Step 1: Validate and filter sources
            validated_sources = self._validate_sources(sources)

            # Step 2: Extract key information
            key_information = self._extract_key_information(validated_sources, query)

            # Step 3: Cross-validate facts
            validation_results = self._cross_validate_information(key_information)

            # Step 4: Synthesize response based on persona
            persona = context.get("persona", "default")
            synthesized_answer = await self._synthesize_response(
                query, key_information, validation_results, persona, context
            )

            # Step 5: Calculate confidence and quality metrics
            confidence_score = self._calculate_confidence_score(
                validated_sources, validation_results, synthesized_answer
            )

            quality_metrics = self._calculate_quality_metrics(
                validated_sources, synthesized_answer, validation_results
            )

            return AgentResult(
                agent_name=self.name,
                state=AgentState.COMPLETED,
                data={
                    "synthesized_answer": synthesized_answer,
                    "key_information": key_information,
                    "validation_results": validation_results,
                    "confidence_score": confidence_score,
                    "quality_metrics": quality_metrics,
                    "sources_analyzed": len(validated_sources),
                    "persona_used": persona
                },
                metadata={
                    "query": query,
                    "total_sources": len(sources),
                    "validated_sources": len(validated_sources),
                    "synthesis_strategy": "comprehensive_merge",
                    "persona": persona,
                    "confidence_score": confidence_score
                },
                execution_time=0.0,  # Will be set by base class
                credits_used=len(validated_sources) * 0.2,  # 0.2 credits per source analyzed
                success=True
            )

        except Exception as e:
            logger.error(f"Analysis execution failed: {e}", exc_info=True)
            return AgentResult(
                agent_name=self.name,
                state=AgentState.FAILED,
                data={},
                metadata={"error": str(e), "query": query},
                execution_time=0.0,
                credits_used=0.0,
                success=False,
                error_message=f"Analysis failed: {str(e)}"
            )

    def _validate_sources(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate and filter sources for quality"""
        validated = []

        for source in sources:
            # Basic validation checks
            if not source.get('content', '').strip():
                continue  # Skip empty content

            if len(source.get('content', '')) < 50:
                continue  # Skip too short content

            # Check for relevance (basic keyword matching)
            content_lower = source.get('content', '').lower()
            title_lower = source.get('title', '').lower()

            # This would be improved with actual query context
            # For now, assume all sources passed basic filtering

            validated.append(source)

        return validated

    def _extract_key_information(self, sources: List[Dict[str, Any]], query: str) -> Dict[str, Any]:
        """Extract key information from validated sources"""
        key_info = {
            "main_points": [],
            "supporting_facts": [],
            "contradictions": [],
            "gaps": [],
            "consensus_points": []
        }

        # Simple extraction logic (would be enhanced with NLP in production)
        all_content = []
        for source in sources:
            content = source.get('content', '')
            title = source.get('title', '')
            all_content.append(f"Title: {title}\nContent: {content}")

        combined_content = "\n\n".join(all_content)

        # Extract main points (simplified - look for sentences with keywords)
        sentences = combined_content.split('.')
        main_points = []

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20 and len(sentence) < 200:  # Reasonable sentence length
                main_points.append(sentence)

        key_info["main_points"] = main_points[:10]  # Limit to top 10
        key_info["supporting_facts"] = main_points[10:20] if len(main_points) > 10 else []

        return key_info

    def _cross_validate_information(self, key_information: Dict[str, Any]) -> Dict[str, Any]:
        """Cross-validate information across sources"""
        validation_results = {
            "consensus_level": 0.0,
            "contradictions_found": [],
            "information_gaps": [],
            "reliability_score": 0.0
        }

        main_points = key_information.get("main_points", [])

        if len(main_points) == 0:
            validation_results["consensus_level"] = 0.0
            validation_results["reliability_score"] = 0.0
            return validation_results

        # Simple consensus calculation (would be enhanced with similarity analysis)
        # For now, assume higher consensus with more sources
        consensus_base = min(len(main_points) / 5, 1.0)  # Up to 5 points for consensus
        validation_results["consensus_level"] = consensus_base

        # Reliability based on source verification and consensus
        reliability = consensus_base * 0.8  # Base reliability
        validation_results["reliability_score"] = reliability

        return validation_results

    def _synthesize_response(self, query: str, key_information: Dict[str, Any],
                           validation_results: Dict[str, Any], persona: str,
                           context: Dict[str, Any]) -> str:
        """Synthesize response based on persona and available information"""
        # For now, use synchronous fallback until async persona system is fully implemented
        main_points = key_information.get("main_points", [])
        return self._synthesize_fallback(query, main_points)

    def _synthesize_fallback(self, query: str, main_points: List[str]) -> str:
        """Fallback synthesis when persona system fails"""
        response_parts = [f"Based on research about '{query}':"]

        for i, point in enumerate(main_points[:5], 1):
            response_parts.append(f"{i}. {point}")

        return "\n".join(response_parts)

    def _synthesize_default_style(self, query: str, main_points: List[str],
                                supporting_facts: List[str], consensus_level: float) -> str:
        """Synthesize response in balanced, comprehensive style"""
        response_parts = []

        # Introduction
        response_parts.append(f"Let me help you understand: {query}")

        # Main points
        if main_points:
            response_parts.append("\nKey insights:")
            for i, point in enumerate(main_points[:5], 1):
                response_parts.append(f"{i}. {point}")

        # Supporting information
        if supporting_facts and len(response_parts) < 8:
            response_parts.append("\nAdditional details:")
            for fact in supporting_facts[:3]:
                response_parts.append(f"• {fact}")

        # Confidence note
        if consensus_level < 0.5:
            response_parts.append("\nNote: This information is based on available sources and should be verified for your specific needs.")
        elif consensus_level > 0.8:
            response_parts.append("\nThis represents a well-established consensus across multiple sources.")

        return "\n".join(response_parts)

    def _synthesize_isaac_style(self, query: str, main_points: List[str],
                               supporting_facts: List[str], consensus_level: float) -> str:
        """Synthesize response in Isaac Asimov style - clear, educational, engaging"""
        response_parts = []

        response_parts.append(f"To answer your question about '{query}', let me break this down step by step:")

        if main_points:
            response_parts.append("\nHere's what we know:")
            for i, point in enumerate(main_points[:6], 1):
                # Make it more educational and narrative
                response_parts.append(f"{i}. {point} This helps us understand the broader context.")

        if supporting_facts:
            response_parts.append("\nDigging deeper, we find:")
            for fact in supporting_facts[:2]:
                response_parts.append(f"• {fact}")

        response_parts.append("\nIn essence, this shows us how different pieces fit together to create a complete picture.")

        return "\n".join(response_parts)

    def _synthesize_technical_style(self, query: str, main_points: List[str],
                                  supporting_facts: List[str], consensus_level: float) -> str:
        """Synthesize response in technical documentation style"""
        response_parts = []

        response_parts.append(f"## Technical Analysis: {query}")
        response_parts.append("\n### Core Findings")

        if main_points:
            for i, point in enumerate(main_points[:8], 1):
                response_parts.append(f"**{i}.** {point}")

        if supporting_facts:
            response_parts.append("\n### Implementation Details")
            for fact in supporting_facts[:4]:
                response_parts.append(f"- {fact}")

        response_parts.append(f"\n### Validation Score: {consensus_level:.1%}")
        if consensus_level > 0.7:
            response_parts.append("✅ High confidence - Well validated across sources")
        elif consensus_level > 0.4:
            response_parts.append("⚠️ Medium confidence - Some variance in source information")
        else:
            response_parts.append("❌ Low confidence - Limited source validation")

        return "\n".join(response_parts)

    def _synthesize_creative_style(self, query: str, main_points: List[str],
                                 supporting_facts: List[str], consensus_level: float) -> str:
        """Synthesize response in creative, narrative-driven style"""
        response_parts = []

        response_parts.append(f"Imagine exploring the fascinating world of: {query}")
        response_parts.append("\nWhat makes this so intriguing is...")

        if main_points:
            for i, point in enumerate(main_points[:4], 1):
                if i == 1:
                    response_parts.append(f"\nFirst, picture this: {point}")
                elif i == 2:
                    response_parts.append(f"Then, consider that {point}")
                else:
                    response_parts.append(f"And don't forget: {point}")

        if supporting_facts:
            response_parts.append("\nThe story gets even more interesting when we look at:")
            for fact in supporting_facts[:2]:
                response_parts.append(f"• {fact}")

        response_parts.append(f"\nIt's a reminder that even complex topics like this can be broken down into fascinating, interconnected pieces.")

        return "\n".join(response_parts)

    def _calculate_confidence_score(self, sources: List[Dict[str, Any]],
                                  validation_results: Dict[str, Any],
                                  synthesized_answer: str) -> float:
        """Calculate overall confidence score"""
        base_score = 0.5

        # Source quality factor
        source_factor = min(len(sources) / 5, 1.0) * 0.3

        # Validation factor
        validation_factor = validation_results.get("consensus_level", 0.0) * 0.4

        # Answer quality factor (length and structure)
        answer_factor = min(len(synthesized_answer.split()) / 100, 1.0) * 0.3

        confidence = base_score + source_factor + validation_factor + answer_factor
        return min(confidence, 1.0)

    def _calculate_quality_metrics(self, sources: List[Dict[str, Any]],
                                 synthesized_answer: str,
                                 validation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate detailed quality metrics"""
        return {
            "source_count": len(sources),
            "average_source_length": sum(len(s.get('content', '')) for s in sources) / max(len(sources), 1),
            "verified_sources": sum(1 for s in sources if s.get('verified', False)),
            "answer_length": len(synthesized_answer),
            "consensus_level": validation_results.get("consensus_level", 0.0),
            "reliability_score": validation_results.get("reliability_score", 0.0),
            "information_density": len(synthesized_answer.split()) / max(len(sources), 1)
        }
