"""
Isaac Asimov Persona
Clear, educational writing style inspired by Isaac Asimov
"""

import logging
from typing import Dict, Any, Optional
from .persona_manager import BasePersona

logger = logging.getLogger(__name__)


class IsaacPersona(BasePersona):
    """
    Isaac Asimov-inspired persona

    Characteristics:
    - Clear, straightforward explanations
    - Logical progression of ideas
    - Educational tone without being condescending
    - Balances accessibility with accuracy
    - Uses analogies and examples effectively
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("Isaac Asimov", config)

    def _define_personality(self) -> Dict[str, Any]:
        """Define Isaac Asimov's writing personality"""
        return {
            'inspiration': 'Isaac Asimov - Foundation series author and science communicator',
            'tone': 'Educational, clear, and engaging',
            'structure': 'Logical progression with clear explanations',
            'language': 'Accessible vocabulary, precise terminology when needed',
            'purpose': 'Make complex topics understandable while maintaining scientific accuracy',
            'description': 'Clear, educational explanations that make complex topics accessible',
            'best_for': ['Educational content', 'Science communication', 'General audiences', 'Complex topics'],
            'characteristics': [
                'Explain complex concepts with clarity and simplicity',
                'Use logical progression from basic to advanced concepts',
                'Include helpful analogies and examples',
                'Maintain scientific accuracy while being accessible',
                'Structure information progressively and intuitively',
                'Use engaging but educational tone',
                'Connect ideas to show how they fit together',
                'Admit uncertainties when appropriate'
            ]
        }

    async def synthesize(self, query: str, information: Dict[str, Any],
                        context: Dict[str, Any] = None) -> str:
        """
        Synthesize information in Isaac Asimov style

        Creates clear, educational responses that break down complex topics
        into understandable components with logical flow.
        """
        context = context or {}
        main_points = information.get('main_points', [])
        sources = information.get('sources_used', [])
        confidence = information.get('confidence_score', 0.0)

        # Build response structure
        response_parts = []

        # Opening - Set the context
        response_parts.append(f"To answer your question about '{query}', let me break this down step by step:")

        # Main explanation
        if main_points:
            response_parts.append("\nHere's what we understand about this topic:")
            for i, point in enumerate(main_points[:6], 1):
                response_parts.append(f"{i}. {point}")

        # Connect the ideas
        if len(main_points) > 1:
            response_parts.append("\nThese points connect together to give us a complete picture of the subject.")

        # Add supporting information if available
        supporting_facts = information.get('supporting_facts', [])
        if supporting_facts:
            response_parts.append("\nTo further illustrate this:")
            for fact in supporting_facts[:2]:
                response_parts.append(f"• {fact}")

        # Educational conclusion
        response_parts.append("\nIn essence, this shows us how different aspects of the topic interrelate and function together.")

        # Source attribution
        if sources and context.get('include_sources', True):
            response_parts.append("\n**Sources consulted:**")
            for i, source in enumerate(sources[:3], 1):
                title = source.get('title', f'Source {i}')
                response_parts.append(f"{i}. {title}")

        # Confidence note
        if confidence < 0.7:
            response_parts.append(f"\n*Note: This explanation is based on available information with {confidence:.1%} confidence.*")

        return "\n".join(response_parts)
