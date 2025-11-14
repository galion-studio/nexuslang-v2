"""
Persona Manager for Deep Search
Manages different writing personas and their application
"""

import logging
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BasePersona(ABC):
    """Base class for all writing personas"""

    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        self.personality_traits = self._define_personality()

    @abstractmethod
    def _define_personality(self) -> Dict[str, Any]:
        """Define the personality traits for this persona"""
        pass

    @abstractmethod
    async def synthesize(self, query: str, information: Dict[str, Any],
                        context: Dict[str, Any] = None) -> str:
        """Synthesize information using this persona's style"""
        pass

    def get_personality_prompt(self) -> str:
        """Get the personality prompt for this persona"""
        traits = self.personality_traits
        prompt = f"""You are writing in the style of {traits['inspiration']}.

Writing Style Guidelines:
- Tone: {traits['tone']}
- Structure: {traits['structure']}
- Language: {traits['language']}
- Purpose: {traits['purpose']}

Key Characteristics:
"""

        for characteristic in traits['characteristics']:
            prompt += f"- {characteristic}\n"

        return prompt


class PersonaManager:
    """
    Manages different writing personas for deep search responses

    Provides access to specialized writing styles optimized for different:
    - Audiences (technical vs general)
    - Purposes (education vs entertainment)
    - Complexity levels (simple explanations vs detailed analysis)
    """

    def __init__(self):
        self.personas = {}
        self._initialize_personas()

    def _initialize_personas(self):
        """Initialize all available personas"""
        from .isaac_persona import IsaacPersona
        from .technical_persona import TechnicalPersona
        from .creative_persona import CreativePersona

        self.personas = {
            'default': IsaacPersona(),  # Default to Isaac Asimov style
            'isaac': IsaacPersona(),
            'technical': TechnicalPersona(),
            'creative': CreativePersona()
        }

        logger.info(f"Initialized {len(self.personas)} writing personas")

    async def synthesize_with_persona(
        self,
        persona_name: str,
        query: str,
        information: Dict[str, Any],
        context: Dict[str, Any] = None
    ) -> str:
        """
        Synthesize information using a specific persona

        Args:
            persona_name: Name of the persona to use
            query: Original research query
            information: Research information to synthesize
            context: Additional context

        Returns:
            Synthesized response in the persona's style
        """
        persona = self.personas.get(persona_name.lower())

        if not persona:
            logger.warning(f"Persona '{persona_name}' not found, using default")
            persona = self.personas['default']

        try:
            synthesized = await persona.synthesize(query, information, context)
            logger.info(f"Synthesized response using {persona.name} persona")
            return synthesized

        except Exception as e:
            logger.error(f"Persona synthesis failed: {e}")
            # Fallback to default persona
            default_persona = self.personas['default']
            return await default_persona.synthesize(query, information, context)

    def get_available_personas(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all available personas"""
        return {
            name: {
                'name': persona.name,
                'description': persona.personality_traits.get('description', ''),
                'best_for': persona.personality_traits.get('best_for', []),
                'inspiration': persona.personality_traits.get('inspiration', '')
            }
            for name, persona in self.personas.items()
        }

    def get_persona_info(self, persona_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific persona"""
        persona = self.personas.get(persona_name.lower())
        if not persona:
            return None

        return {
            'name': persona.name,
            'personality_traits': persona.personality_traits,
            'personality_prompt': persona.get_personality_prompt()
        }
