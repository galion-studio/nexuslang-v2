"""IDE services."""
# Project and file management services
# AI-powered code assistance

from .ide_service import IDEService
from .ai_assistant import IDEAIAssistant, get_ide_ai_assistant

__all__ = ['IDEService', 'IDEAIAssistant', 'get_ide_ai_assistant']

