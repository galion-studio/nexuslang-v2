"""
AI Services Module
Provides unified access to multiple AI models through OpenRouter.
"""

from .ai_router import AIRouter, AIModel, AIProvider, get_ai_router

__all__ = [
    "AIRouter",
    "AIModel",
    "AIProvider",
    "get_ai_router"
]
