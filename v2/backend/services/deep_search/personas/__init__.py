"""
Deep Search Writing Personas
Specialized writing styles for different audiences and purposes
"""

from .persona_manager import PersonaManager
from .isaac_persona import IsaacPersona
from .technical_persona import TechnicalPersona
from .creative_persona import CreativePersona

__all__ = ['PersonaManager', 'IsaacPersona', 'TechnicalPersona', 'CreativePersona']
