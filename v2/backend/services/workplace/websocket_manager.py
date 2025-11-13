"""
WebSocket Manager Service
Real-time collaboration and live session management for workplace.

Features:
- Workspace-based connections
- Live session management
- Real-time task updates
- Cursor position sharing
- Voice command broadcasting
"""

import json
import logging
from typing import Dict, List, Set, Optional
from fastapi import WebSocket
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manager for WebSocket connections and real-time collaboration"""

    def __init__(self):
        # active_connections[workspace_id][user_id] = websocket
        self.active_connections: Dict[int, Dict[int, WebSocket]] = {}
        # workspace_sessions[workspace_id] = set of active user_ids
        self.workspace_sessions: Dict[int, Set[int]] = {}
        # live_sessions[session_id] = {"participants": set, "project_id": int, "type": str}
        self.live_sessions: Dict[str, Dict] = {}

    async def connect(self, websocket: WebSocket, workspace_id: int, user_id: int):
        """Connect a user to a workspace"""
        await websocket.accept()

        if workspace_id not in self.active_connections:
            self.active_connections[workspace_id] = {}
            self.workspace_sessions[workspace_id] = set()

        self.active_connections[workspace_id][user_id] = websocket
        self.workspace_sessions[workspace_id].add(user_id)

        logger.info(f"User {user_id} connected to workspace {workspace_id}")

    def disconnect(self, workspace_id: int, user_id: int):
        """Disconnect a user from a workspace"""
        if workspace_id in self.active_connections:
            if user_id in self.active_connections[workspace_id]:
                del self.active_connections[workspace_id][user_id]
                self.workspace_sessions[workspace_id].discard(user_id)

                # Clean up empty workspaces
                if not self.active_connections[workspace_id]:
                    del self.active_connections[workspace_id]
                    del self.workspace_sessions[workspace_id]

        logger.info(f"User {user_id} disconnected from workspace {workspace_id}")

    async def broadcast_to_workspace(
        self,
        workspace_id: int,
        message: Dict,
        exclude_user: Optional[int] = None
    ):
        """Broadcast message to all users in a workspace"""
        if workspace_id not in self.active_connections:
            return

        disconnected_users = []
        for user_id, websocket in self.active_connections[workspace_id].items():
            if exclude_user and user_id == exclude_user:
                continue

            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send message to user {user_id}: {e}")
                disconnected_users.append(user_id)

        # Clean up disconnected users
        for user_id in disconnected_users:
            self.disconnect(workspace_id, user_id)

    async def send_to_user(self, workspace_id: int, user_id: int, message: Dict):
        """Send message to specific user in workspace"""
        if (workspace_id in self.active_connections and
            user_id in self.active_connections[workspace_id]):
            try:
                websocket = self.active_connections[workspace_id][user_id]
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send message to user {user_id}: {e}")
                self.disconnect(workspace_id, user_id)

    async def broadcast_to_live_session(self, session_id: str, message: Dict):
        """Broadcast to all participants in a live session"""
        if session_id not in self.live_sessions:
            return

        session = self.live_sessions[session_id]
        workspace_id = session.get("workspace_id")

        if not workspace_id:
            return

        # Send to all session participants
        for user_id in session["participants"]:
            await self.send_to_user(workspace_id, user_id, message)

    def add_to_live_session(self, session_id: str, user_id: int):
        """Add user to live session"""
        if session_id in self.live_sessions:
            self.live_sessions[session_id]["participants"].add(user_id)

    def remove_from_live_session(self, session_id: str, user_id: int):
        """Remove user from live session"""
        if session_id in self.live_sessions:
            self.live_sessions[session_id]["participants"].discard(user_id)

    def create_live_session(self, session_id: str, project_id: int, workspace_id: int, session_type: str):
        """Create a new live session"""
        self.live_sessions[session_id] = {
            "project_id": project_id,
            "workspace_id": workspace_id,
            "type": session_type,
            "participants": set(),
            "created_at": datetime.utcnow()
        }

    def end_live_session(self, session_id: str):
        """End a live session"""
        if session_id in self.live_sessions:
            del self.live_sessions[session_id]

    def get_workspace_users(self, workspace_id: int) -> List[int]:
        """Get list of active users in workspace"""
        if workspace_id in self.workspace_sessions:
            return list(self.workspace_sessions[workspace_id])
        return []

    def get_live_session_participants(self, session_id: str) -> List[int]:
        """Get participants in a live session"""
        if session_id in self.live_sessions:
            return list(self.live_sessions[session_id]["participants"])
        return []


# Global instance
websocket_manager = WebSocketManager()
