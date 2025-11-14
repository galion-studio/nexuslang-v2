"""
Planner Agent for Deep Search System
Creates research strategies and plans execution
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

from .base_agent import BaseAgent, AgentResult, AgentState

logger = logging.getLogger(__name__)


class PlannerAgent(BaseAgent):
    """
    Agent responsible for creating research plans

    Analyzes the query and creates a comprehensive research strategy including:
    - Query decomposition
    - Search strategies
    - Resource allocation
    - Expected outcomes
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("planner", config)

    def _initialize(self):
        """Initialize planner-specific components"""
        self.personas = {
            "default": {
                "style": "balanced and comprehensive",
                "focus": "general knowledge synthesis"
            },
            "isaac": {
                "style": "Isaac Asimov-style clear explanations",
                "focus": "educational clarity and accessibility"
            },
            "technical": {
                "style": "detailed technical documentation",
                "focus": "precision and technical depth"
            },
            "creative": {
                "style": "engaging narrative-driven responses",
                "focus": "storytelling and engagement"
            }
        }

    async def execute(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> AgentResult:
        """
        Create a research plan for the given query

        Args:
            input_data: Contains query and initial context
            context: Additional research context

        Returns:
            AgentResult with research plan
        """
        query = input_data.get("query", "")
        context = context or {}

        # Analyze query complexity
        query_analysis = self._analyze_query(query)

        # Determine research approach
        research_approach = self._determine_research_approach(query_analysis, context)

        # Generate search queries
        search_queries = self._generate_search_queries(query, query_analysis)

        # Create execution plan
        execution_plan = self._create_execution_plan(query_analysis, research_approach, context)

        research_plan = {
            "original_query": query,
            "query_analysis": query_analysis,
            "research_approach": research_approach,
            "search_queries": search_queries,
            "execution_plan": execution_plan,
            "expected_complexity": query_analysis["complexity"],
            "estimated_sources": self._estimate_sources_needed(query_analysis),
            "persona_guidance": self._get_persona_guidance(context.get("persona", "default")),
            "created_at": datetime.utcnow().isoformat()
        }

        return AgentResult(
            agent_name=self.name,
            state=AgentState.COMPLETED,
            data={"research_plan": research_plan},
            metadata={
                "query_length": len(query),
                "search_queries_count": len(search_queries),
                "complexity_score": query_analysis["complexity"]
            },
            execution_time=0.0,  # Will be set by base class
            credits_used=0.5,  # Planning costs minimal credits
            success=True
        )

    def _analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze the complexity and nature of the query"""
        words = query.split()
        word_count = len(words)

        # Determine complexity based on various factors
        complexity_factors = {
            "length": min(word_count / 20, 1.0),  # Longer queries are more complex
            "question_words": 1.0 if any(word.lower() in ['what', 'how', 'why', 'when', 'where', 'who']) else 0.0,
            "technical_terms": self._count_technical_terms(query),
            "comparative": 1.0 if any(word.lower() in ['compare', 'versus', 'vs', 'difference']) else 0.0,
            "analytical": 1.0 if any(word.lower() in ['analyze', 'evaluate', 'assess']) else 0.0
        }

        # Calculate overall complexity score (0-1)
        complexity = sum(complexity_factors.values()) / len(complexity_factors)

        # Determine query type
        query_type = self._classify_query_type(query)

        return {
            "word_count": word_count,
            "complexity": complexity,
            "complexity_factors": complexity_factors,
            "query_type": query_type,
            "requires_deep_search": complexity > 0.4 or query_type in ["analytical", "comparative"],
            "estimated_depth": "quick" if complexity < 0.3 else "comprehensive" if complexity < 0.7 else "exhaustive"
        }

    def _count_technical_terms(self, query: str) -> float:
        """Count technical terms and return normalized score"""
        technical_indicators = [
            'algorithm', 'architecture', 'implementation', 'framework', 'library',
            'api', 'database', 'server', 'client', 'protocol', 'authentication',
            'security', 'performance', 'optimization', 'scalability', 'integration'
        ]

        query_lower = query.lower()
        technical_count = sum(1 for term in technical_indicators if term in query_lower)

        return min(technical_count / 3, 1.0)  # Normalize to 0-1

    def _classify_query_type(self, query: str) -> str:
        """Classify the type of query"""
        query_lower = query.lower()

        if any(word in query_lower for word in ['explain', 'how does', 'what is']):
            return "explanatory"
        elif any(word in query_lower for word in ['compare', 'versus', 'vs', 'difference']):
            return "comparative"
        elif any(word in query_lower for word in ['analyze', 'evaluate', 'assess']):
            return "analytical"
        elif any(word in query_lower for word in ['list', 'examples', 'types']):
            return "enumerative"
        elif '?' in query:
            return "question"
        else:
            return "informational"

    def _determine_research_approach(self, query_analysis: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Determine the best research approach"""
        depth = context.get("depth", query_analysis["estimated_depth"])

        approaches = {
            "quick": {
                "max_searches": 2,
                "max_sources": 5,
                "validation_level": "basic",
                "synthesis_depth": "summary"
            },
            "comprehensive": {
                "max_searches": 4,
                "max_sources": 15,
                "validation_level": "cross_reference",
                "synthesis_depth": "detailed"
            },
            "exhaustive": {
                "max_searches": 6,
                "max_sources": 25,
                "validation_level": "full_validation",
                "synthesis_depth": "comprehensive"
            }
        }

        approach = approaches.get(depth, approaches["comprehensive"])

        # Adjust based on query complexity
        if query_analysis["complexity"] > 0.8:
            approach["max_searches"] = min(approach["max_searches"] + 2, 8)
            approach["max_sources"] = min(approach["max_sources"] + 5, 30)

        return approach

    def _generate_search_queries(self, original_query: str, query_analysis: Dict[str, Any]) -> List[str]:
        """Generate multiple search queries for comprehensive research"""
        queries = [original_query]  # Always include original

        # Generate variations based on query type
        query_type = query_analysis["query_type"]

        if query_type == "explanatory":
            # Add "how to" and "tutorial" variations
            queries.extend([
                f"how to {original_query}",
                f"{original_query} tutorial",
                f"{original_query} guide"
            ])
        elif query_type == "comparative":
            # Add individual component searches
            parts = original_query.replace(' vs ', ' ').replace(' versus ', ' ').split()
            if len(parts) >= 2:
                queries.extend([
                    f"{parts[0]} {parts[1]}",
                    f"{parts[0]} advantages disadvantages",
                    f"{parts[1]} advantages disadvantages"
                ])
        elif query_type == "analytical":
            # Add research and analysis focused queries
            queries.extend([
                f"{original_query} analysis",
                f"{original_query} research",
                f"{original_query} case study"
            ])

        # Add technical depth if needed
        if query_analysis["complexity_factors"]["technical_terms"] > 0.5:
            queries.append(f"{original_query} implementation")
            queries.append(f"{original_query} best practices")

        return queries[:8]  # Limit to 8 queries max

    def _create_execution_plan(self, query_analysis: Dict[str, Any], research_approach: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Create detailed execution plan"""
        return {
            "phases": [
                {
                    "name": "search",
                    "description": "Gather relevant information from knowledge base",
                    "parallel_execution": True,
                    "max_concurrent": research_approach["max_searches"]
                },
                {
                    "name": "validate",
                    "description": "Cross-reference and validate information sources",
                    "parallel_execution": False,
                    "validation_level": research_approach["validation_level"]
                },
                {
                    "name": "synthesize",
                    "description": "Combine information into coherent response",
                    "parallel_execution": False,
                    "synthesis_depth": research_approach["synthesis_depth"]
                }
            ],
            "resource_allocation": {
                "max_search_time": 30,  # seconds
                "max_analysis_time": 60,  # seconds
                "memory_limit": "512MB"
            },
            "quality_checks": [
                "source_reliability",
                "information_recency",
                "factual_accuracy",
                "comprehensive_coverage"
            ]
        }

    def _estimate_sources_needed(self, query_analysis: Dict[str, Any]) -> int:
        """Estimate how many sources are needed"""
        base_sources = 3
        complexity_multiplier = query_analysis["complexity"] * 2
        return int(base_sources + complexity_multiplier * 7)  # 3-17 sources

    def _get_persona_guidance(self, persona: str) -> Dict[str, Any]:
        """Get writing guidance for the specified persona"""
        persona_info = self.personas.get(persona, self.personas["default"])

        guidance = {
            "writing_style": persona_info["style"],
            "focus_area": persona_info["focus"],
            "key_instructions": []
        }

        if persona == "isaac":
            guidance["key_instructions"] = [
                "Explain complex concepts with clarity and simplicity",
                "Use logical progression from basic to advanced concepts",
                "Include helpful analogies and examples",
                "Maintain scientific accuracy while being accessible"
            ]
        elif persona == "technical":
            guidance["key_instructions"] = [
                "Provide detailed technical specifications",
                "Include code examples and implementation details",
                "Focus on accuracy and precision",
                "Structure information for reference purposes"
            ]
        elif persona == "creative":
            guidance["key_instructions"] = [
                "Use engaging, conversational tone",
                "Incorporate storytelling elements and vivid language",
                "Create emotional connection with the audience",
                "Balance entertainment value with factual accuracy"
            ]

        return guidance