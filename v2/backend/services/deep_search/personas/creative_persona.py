"""
Creative Persona
Engaging, narrative-driven writing style
"""

import logging
from typing import Dict, Any, Optional
from .persona_manager import BasePersona

logger = logging.getLogger(__name__)


class CreativePersona(BasePersona):
    """
    Creative storytelling persona

    Characteristics:
    - Engaging narrative style
    - Storytelling elements
    - Emotional connection
    - Accessible language
    - Entertainment value balanced with information
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("Creative Storytelling", config)

    def _define_personality(self) -> Dict[str, Any]:
        """Define creative storytelling personality"""
        return {
            'inspiration': 'Engaging storytellers and science communicators',
            'tone': 'Conversational, enthusiastic, and engaging',
            'structure': 'Narrative flow with engaging transitions',
            'language': 'Vivid, accessible language with storytelling elements',
            'purpose': 'Make information memorable and enjoyable while educating',
            'description': 'Engaging narrative style that makes complex topics entertaining',
            'best_for': ['General audiences', 'Educational entertainment', 'Marketing content', 'Broad appeal topics'],
            'characteristics': [
                'Use engaging, conversational tone',
                'Incorporate storytelling elements and vivid language',
                'Create emotional connection with the audience',
                'Balance entertainment value with factual accuracy',
                'Use analogies, metaphors, and relatable examples',
                'Build curiosity and maintain interest throughout',
                'Make complex topics feel accessible and exciting',
                'End with thought-provoking insights or calls to imagination'
            ]
        }

    async def synthesize(self, query: str, information: Dict[str, Any],
                        context: Dict[str, Any] = None) -> str:
        """
        Synthesize information in creative storytelling style

        Creates engaging, narrative-driven responses that make
        information memorable and enjoyable to read.
        """
        context = context or {}
        main_points = information.get('main_points', [])
        sources = information.get('sources_used', [])
        confidence = information.get('confidence_score', 0.0)

        # Build response structure
        response_parts = []

        # Engaging opening
        response_parts.append(f"Imagine diving into the fascinating world of: **{query}**")
        response_parts.append("")

        # Narrative hook
        if main_points:
            response_parts.append("What makes this topic so intriguing is how it connects different ideas in unexpected ways:")
            response_parts.append("")

        # Story-like progression
        if main_points:
            for i, point in enumerate(main_points[:4], 1):
                if i == 1:
                    response_parts.append(f"First, picture this: {point}")
                elif i == 2:
                    response_parts.append(f"Then, consider that {point}")
                elif i == 3:
                    response_parts.append(f"But here's where it gets really interesting: {point}")
                else:
                    response_parts.append(f"And finally: {point}")

        # Supporting details as "hidden gems"
        supporting_facts = information.get('supporting_facts', [])
        if supporting_facts:
            response_parts.append("")
            response_parts.append("The story gets even more compelling when we discover:")
            for fact in supporting_facts[:2]:
                response_parts.append(f"• {fact}")

        # Engaging conclusion
        response_parts.append("")
        response_parts.append("It's a reminder that even complex topics like this can be broken down into fascinating, interconnected pieces that spark our curiosity and imagination.")

        # Inspirational close
        response_parts.append("")
        response_parts.append("*What aspect of this topic intrigues you most?*")

        # Source attribution (subtle)
        if sources and context.get('include_sources', True):
            response_parts.append("")
            response_parts.append("---")
            response_parts.append("*Drawing from sources including:* " +
                               ", ".join([s.get('title', 'research') for s in sources[:3]]))

        return "\n".join(response_parts)
