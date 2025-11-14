"""
Technical Persona
Detailed technical documentation style
"""

import logging
from typing import Dict, Any, Optional
from .persona_manager import BasePersona

logger = logging.getLogger(__name__)


class TechnicalPersona(BasePersona):
    """
    Technical documentation persona

    Characteristics:
    - Precise technical language
    - Structured documentation format
    - Code examples and implementation details
    - Focus on accuracy and completeness
    - Reference-style formatting
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("Technical Documentation", config)

    def _define_personality(self) -> Dict[str, Any]:
        """Define technical documentation personality"""
        return {
            'inspiration': 'Technical documentation and API references',
            'tone': 'Precise, objective, and comprehensive',
            'structure': 'Structured documentation with clear sections',
            'language': 'Technical terminology with precise definitions',
            'purpose': 'Provide complete technical information for implementation',
            'description': 'Detailed technical documentation with precise specifications',
            'best_for': ['API documentation', 'Technical specifications', 'Developer guides', 'Implementation details'],
            'characteristics': [
                'Use precise technical terminology and definitions',
                'Structure information in clear, logical sections',
                'Include code examples and implementation details',
                'Focus on accuracy and completeness over simplicity',
                'Use consistent formatting and documentation standards',
                'Provide specifications, requirements, and constraints',
                'Include troubleshooting and edge cases',
                'Reference external standards and best practices'
            ]
        }

    async def synthesize(self, query: str, information: Dict[str, Any],
                        context: Dict[str, Any] = None) -> str:
        """
        Synthesize information in technical documentation style

        Creates structured, comprehensive technical documentation
        with specifications, examples, and implementation details.
        """
        context = context or {}
        main_points = information.get('main_points', [])
        sources = information.get('sources_used', [])
        confidence = information.get('confidence_score', 0.0)

        # Build response structure
        response_parts = []

        # Header
        response_parts.append(f"# Technical Analysis: {query}")
        response_parts.append("")

        # Overview section
        response_parts.append("## Overview")
        if main_points:
            response_parts.append("This analysis covers the following key technical aspects:")
            for point in main_points[:3]:
                response_parts.append(f"- {point}")
        response_parts.append("")

        # Detailed specifications
        if main_points:
            response_parts.append("## Technical Specifications")
            for i, point in enumerate(main_points, 1):
                response_parts.append(f"**{i}.** {point}")
            response_parts.append("")

        # Implementation details
        supporting_facts = information.get('supporting_facts', [])
        if supporting_facts:
            response_parts.append("## Implementation Details")
            for fact in supporting_facts:
                response_parts.append(f"- {fact}")
            response_parts.append("")

        # Requirements and constraints
        response_parts.append("## Requirements & Constraints")
        response_parts.append(f"- **Validation Score**: {confidence:.1%}")
        if confidence >= 0.8:
            response_parts.append("- **Confidence Level**: High - Well validated across sources")
        elif confidence >= 0.6:
            response_parts.append("- **Confidence Level**: Medium - Some variance in source information")
        else:
            response_parts.append("- **Confidence Level**: Low - Limited source validation available")
        response_parts.append("")

        # Source references
        if sources and context.get('include_sources', True):
            response_parts.append("## References")
            for i, source in enumerate(sources, 1):
                title = source.get('title', f'Technical Source {i}')
                response_parts.append(f"{i}. {title}")
            response_parts.append("")

        # Technical notes
        response_parts.append("## Technical Notes")
        response_parts.append("- This analysis is based on available technical documentation and specifications")
        response_parts.append("- Implementation details may vary based on specific requirements and constraints")
        response_parts.append("- Always validate against current standards and best practices")

        return "\n".join(response_parts)
