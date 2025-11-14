"""
Voice Session Manager
Manages voice interaction sessions, transcripts, and analytics
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import uuid
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete

from ...models.voice_session import VoiceSession
from ...models.user import User

logger = logging.getLogger(__name__)

class VoiceSessionManager:
    """
    Manages voice interaction sessions with database persistence.

    Tracks:
    - Session metadata (user, duration, quality)
    - Transcripts and conversation history
    - Performance metrics
    - Voice quality analytics
    """

    def __init__(self):
        self.active_sessions: Dict[str, Dict[str, Any]] = {}

    async def create_session(
        self,
        user_id: str,
        session_type: str = "voice_call",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create new voice session.

        Args:
            user_id: User identifier
            session_type: Type of voice session
            metadata: Additional session metadata

        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())

        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "session_type": session_type,
            "started_at": datetime.now(),
            "is_active": True,
            "commands_count": 0,
            "total_duration": 0.0,
            "transcription_accuracy": 0.0,
            "audio_quality_score": 0.0,
            "conversation_turns": [],
            "metadata": metadata or {},
            "performance_metrics": {
                "stt_latency_avg": 0.0,
                "tts_latency_avg": 0.0,
                "total_requests": 0,
                "successful_requests": 0
            }
        }

        self.active_sessions[session_id] = session_data

        # Persist to database
        await self._persist_session(session_data)

        logger.info(f"Created voice session: {session_id} for user: {user_id}")
        return session_id

    async def update_session(
        self,
        session_id: str,
        updates: Dict[str, Any]
    ):
        """
        Update session data.

        Args:
            updates: Fields to update
        """
        if session_id not in self.active_sessions:
            logger.warning(f"Session not found: {session_id}")
            return

        session = self.active_sessions[session_id]

        # Update in-memory data
        for key, value in updates.items():
            if key in session:
                session[key] = value
            elif key in session.get("performance_metrics", {}):
                session["performance_metrics"][key] = value

        # Handle special updates
        if "conversation_turn" in updates:
            session["conversation_turns"].append(updates["conversation_turn"])
            session["commands_count"] += 1

        if "duration" in updates:
            session["total_duration"] += updates["duration"]

        # Persist updates
        await self._update_session(session_id, updates)

    async def end_session(self, session_id: str) -> Dict[str, Any]:
        """
        End voice session and calculate final metrics.

        Returns:
            Session summary
        """
        if session_id not in self.active_sessions:
            logger.warning(f"Session not found for ending: {session_id}")
            return {}

        session = self.active_sessions[session_id]
        session["is_active"] = False
        session["ended_at"] = datetime.now()

        # Calculate final metrics
        if session["started_at"] and session["ended_at"]:
            total_duration = (session["ended_at"] - session["started_at"]).total_seconds()
            session["total_duration"] = total_duration

        # Calculate averages
        metrics = session["performance_metrics"]
        if metrics["total_requests"] > 0:
            metrics["success_rate"] = metrics["successful_requests"] / metrics["total_requests"]

        # Persist final state
        await self._finalize_session(session)

        # Remove from active sessions
        summary = session.copy()
        del self.active_sessions[session_id]

        logger.info(f"Ended voice session: {session_id}")
        return summary

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data"""
        return self.active_sessions.get(session_id)

    async def get_user_sessions(
        self,
        user_id: str,
        limit: int = 10,
        include_inactive: bool = False
    ) -> List[Dict[str, Any]]:
        """Get user's voice sessions"""
        sessions = []

        # Active sessions
        for session in self.active_sessions.values():
            if session["user_id"] == user_id:
                sessions.append(session.copy())

        # Include inactive sessions from database
        if include_inactive:
            # TODO: Query database for historical sessions
            pass

        return sessions[-limit:]  # Return most recent

    async def get_session_analytics(
        self,
        user_id: Optional[str] = None,
        time_range: str = "24h"
    ) -> Dict[str, Any]:
        """
        Get voice session analytics.

        Args:
            user_id: Specific user (None for all users)
            time_range: Time range for analytics
        """
        # Parse time range
        if time_range == "24h":
            hours = 24
        elif time_range == "7d":
            hours = 168
        elif time_range == "30d":
            hours = 720
        else:
            hours = 24

        cutoff_time = datetime.now() - timedelta(hours=hours)

        # Aggregate metrics
        total_sessions = 0
        total_duration = 0.0
        total_commands = 0
        avg_accuracy = 0.0
        session_count = 0

        sessions_to_analyze = []
        if user_id:
            # User's sessions
            for session in self.active_sessions.values():
                if session["user_id"] == user_id:
                    sessions_to_analyze.append(session)
        else:
            # All active sessions
            sessions_to_analyze = list(self.active_sessions.values())

        for session in sessions_to_analyze:
            if session["started_at"] > cutoff_time:
                total_sessions += 1
                total_duration += session["total_duration"]
                total_commands += session["commands_count"]
                if session["transcription_accuracy"] > 0:
                    avg_accuracy += session["transcription_accuracy"]
                    session_count += 1

        return {
            "time_range": time_range,
            "total_sessions": total_sessions,
            "total_duration_hours": total_duration / 3600,
            "total_commands": total_commands,
            "average_accuracy": avg_accuracy / max(session_count, 1),
            "commands_per_session": total_commands / max(total_sessions, 1),
            "average_session_duration": total_duration / max(total_sessions, 1)
        }

    async def _persist_session(self, session_data: Dict[str, Any]):
        """Persist session to database"""
        try:
            # TODO: Implement database persistence
            # This would create a VoiceSession record
            logger.debug(f"Persisting session: {session_data['session_id']}")
        except Exception as e:
            logger.error(f"Session persistence failed: {e}")

    async def _update_session(self, session_id: str, updates: Dict[str, Any]):
        """Update session in database"""
        try:
            # TODO: Implement database updates
            logger.debug(f"Updating session: {session_id}")
        except Exception as e:
            logger.error(f"Session update failed: {e}")

    async def _finalize_session(self, session_data: Dict[str, Any]):
        """Finalize session in database"""
        try:
            # TODO: Implement final session storage
            logger.debug(f"Finalizing session: {session_data['session_id']}")
        except Exception as e:
            logger.error(f"Session finalization failed: {e}")

    def get_active_sessions_count(self) -> int:
        """Get count of active sessions"""
        return len(self.active_sessions)

    def get_sessions_summary(self) -> Dict[str, Any]:
        """Get summary of all sessions"""
        total_duration = sum(s["total_duration"] for s in self.active_sessions.values())
        total_commands = sum(s["commands_count"] for s in self.active_sessions.values())

        return {
            "active_sessions": len(self.active_sessions),
            "total_duration_hours": total_duration / 3600,
            "total_commands": total_commands,
            "average_commands_per_session": total_commands / max(len(self.active_sessions), 1)
        }

# Global voice session manager
_voice_session_manager = None

def get_voice_session_manager() -> VoiceSessionManager:
    """Get global voice session manager"""
    global _voice_session_manager
    if _voice_session_manager is None:
        _voice_session_manager = VoiceSessionManager()
    return _voice_session_manager

