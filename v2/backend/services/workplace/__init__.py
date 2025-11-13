"""
Workplace Services
Cross-platform workplace management services.

Services:
- websocket_manager: Real-time collaboration
- ai_service: AI-powered features
- notification_service: Cross-platform notifications
- sync_service: Platform synchronization
"""

from .websocket_manager import WebSocketManager
from .ai_service import AIService
from .notification_service import NotificationService
from .sync_service import SyncService

__all__ = [
    "WebSocketManager",
    "AIService",
    "NotificationService",
    "SyncService"
]
