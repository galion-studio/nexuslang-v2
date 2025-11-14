"""
Collaborative research system for Deep Search.
Enables real-time multi-user research sessions with shared workspaces.
"""

import logging
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
import asyncio
import json
from dataclasses import dataclass, asdict
from enum import Enum

from ...models.research import ResearchSession, ResearchBookmark
from ...models.collaboration import (
    CollaborativeSession, SessionParticipant, SessionMessage,
    SessionArtifact, CollaborationPermission
)

logger = logging.getLogger(__name__)


class CollaborationRole(Enum):
    """Roles for collaborative session participants."""
    OWNER = "owner"
    EDITOR = "editor"
    VIEWER = "viewer"
    GUEST = "guest"


class SessionStatus(Enum):
    """Status of collaborative sessions."""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class CollaborationEvent(Enum):
    """Types of collaboration events."""
    USER_JOINED = "user_joined"
    USER_LEFT = "user_left"
    MESSAGE_SENT = "message_sent"
    ARTIFACT_ADDED = "artifact_added"
    ARTIFACT_UPDATED = "artifact_updated"
    RESEARCH_UPDATED = "research_updated"
    STATUS_CHANGED = "status_changed"
    PERMISSION_CHANGED = "permission_changed"


@dataclass
class CollaborationMessage:
    """Message structure for real-time collaboration."""
    event_type: CollaborationEvent
    session_id: str
    user_id: str
    username: str
    data: Dict[str, Any]
    timestamp: datetime

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = asdict(self)
        result["event_type"] = self.event_type.value
        result["timestamp"] = self.timestamp.isoformat()
        return result


class CollaborativeResearchManager:
    """
    Manages collaborative research sessions and real-time collaboration.

    Features:
    - Multi-user research sessions
    - Real-time synchronization
    - Role-based permissions
    - Session artifacts and notes
    - Chat and communication
    - Session recording and replay
    """

    def __init__(self):
        # In-memory session tracking (in production, use Redis)
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.session_participants: Dict[str, Set[str]] = {}

        # WebSocket connection management (placeholder for now)
        self.websocket_connections: Dict[str, Dict[str, Any]] = {}

        # Session limits
        self.max_participants_per_session = 10
        self.max_sessions_per_user = 5
        self.session_timeout_hours = 24

    async def create_collaborative_session(self, session, owner_id: str,
                                         session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new collaborative research session.

        Args:
            session: Database session
            owner_id: ID of the session owner
            session_data: Session configuration

        Returns:
            Session creation result
        """
        try:
            # Check user session limit
            existing_sessions = await self._count_user_sessions(session, owner_id)
            if existing_sessions >= self.max_sessions_per_user:
                return {
                    "success": False,
                    "error": f"Maximum {self.max_sessions_per_user} sessions per user reached"
                }

            # Create collaborative session
            collab_session = CollaborativeSession(
                title=session_data.get("title", "Collaborative Research Session"),
                description=session_data.get("description", ""),
                owner_id=owner_id,
                status=SessionStatus.ACTIVE.value,
                settings=json.dumps(session_data.get("settings", {})),
                tags=json.dumps(session_data.get("tags", [])),
                max_participants=session_data.get("max_participants", self.max_participants_per_session),
                is_public=session_data.get("is_public", False)
            )

            session.add(collab_session)
            await session.commit()
            await session.refresh(collab_session)

            # Add owner as participant with owner role
            owner_participant = SessionParticipant(
                session_id=str(collab_session.id),
                user_id=owner_id,
                role=CollaborationRole.OWNER.value,
                permissions=json.dumps(self._get_role_permissions(CollaborationRole.OWNER)),
                joined_at=datetime.utcnow()
            )

            session.add(owner_participant)
            await session.commit()

            # Initialize in-memory tracking
            session_id_str = str(collab_session.id)
            self.active_sessions[session_id_str] = {
                "id": session_id_str,
                "title": collab_session.title,
                "owner_id": owner_id,
                "status": SessionStatus.ACTIVE.value,
                "participants": {owner_id: CollaborationRole.OWNER.value},
                "created_at": collab_session.created_at.isoformat(),
                "last_activity": datetime.utcnow().isoformat()
            }
            self.session_participants[session_id_str] = {owner_id}

            logger.info(f"Created collaborative session '{collab_session.title}' for user {owner_id}")

            return {
                "success": True,
                "session_id": session_id_str,
                "title": collab_session.title,
                "created_at": collab_session.created_at.isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to create collaborative session: {e}")
            await session.rollback()
            return {
                "success": False,
                "error": str(e)
            }

    async def join_session(self, session, user_id: str, session_id: str,
                          invite_code: Optional[str] = None) -> Dict[str, Any]:
        """
        Join an existing collaborative session.

        Args:
            session: Database session
            user_id: User joining the session
            session_id: Session to join
            invite_code: Optional invite code for private sessions

        Returns:
            Join result
        """
        try:
            # Get session
            collab_session = await session.get(CollaborativeSession, session_id)
            if not collab_session:
                return {"success": False, "error": "Session not found"}

            if collab_session.status != SessionStatus.ACTIVE.value:
                return {"success": False, "error": "Session is not active"}

            # Check if user is already a participant
            existing_participant = await session.execute(
                session.query(SessionParticipant).filter(
                    SessionParticipant.session_id == session_id,
                    SessionParticipant.user_id == user_id
                )
            )
            participant = existing_participant.scalar_one_or_none()

            if participant:
                # User is already in session, just update last activity
                participant.last_activity = datetime.utcnow()
                await session.commit()

                return {
                    "success": True,
                    "session_id": session_id,
                    "role": participant.role,
                    "message": "Already a participant"
                }

            # Check participant limit
            current_participants = await self._count_session_participants(session, session_id)
            if current_participants >= collab_session.max_participants:
                return {"success": False, "error": "Session is full"}

            # Check access permissions
            if not collab_session.is_public:
                # For private sessions, require invite code or owner permission
                if not invite_code and collab_session.owner_id != user_id:
                    return {"success": False, "error": "Private session requires invitation"}

                # TODO: Validate invite code if provided

            # Add user as participant
            new_participant = SessionParticipant(
                session_id=session_id,
                user_id=user_id,
                role=CollaborationRole.EDITOR.value,  # Default role for new participants
                permissions=json.dumps(self._get_role_permissions(CollaborationRole.EDITOR)),
                joined_at=datetime.utcnow(),
                last_activity=datetime.utcnow()
            )

            session.add(new_participant)
            await session.commit()

            # Update in-memory tracking
            if session_id in self.active_sessions:
                self.active_sessions[session_id]["participants"][user_id] = CollaborationRole.EDITOR.value
                self.active_sessions[session_id]["last_activity"] = datetime.utcnow().isoformat()
            self.session_participants[session_id].add(user_id)

            # Broadcast join event
            await self._broadcast_event(session_id, CollaborationEvent.USER_JOINED, user_id, {
                "username": f"User {user_id[:8]}",  # TODO: Get actual username
                "role": CollaborationRole.EDITOR.value
            })

            logger.info(f"User {user_id} joined collaborative session {session_id}")

            return {
                "success": True,
                "session_id": session_id,
                "role": CollaborationRole.EDITOR.value,
                "permissions": self._get_role_permissions(CollaborationRole.EDITOR)
            }

        except Exception as e:
            logger.error(f"Failed to join session {session_id}: {e}")
            await session.rollback()
            return {
                "success": False,
                "error": str(e)
            }

    async def leave_session(self, session, user_id: str, session_id: str) -> Dict[str, Any]:
        """
        Leave a collaborative session.

        Args:
            session: Database session
            user_id: User leaving
            session_id: Session to leave

        Returns:
            Leave result
        """
        try:
            # Update participant status
            participant_query = session.query(SessionParticipant).filter(
                SessionParticipant.session_id == session_id,
                SessionParticipant.user_id == user_id
            )
            participant = await session.execute(participant_query)
            participant_record = participant.scalar_one_or_none()

            if participant_record:
                participant_record.left_at = datetime.utcnow()
                await session.commit()

                # Update in-memory tracking
                if session_id in self.session_participants:
                    self.session_participants[session_id].discard(user_id)
                    if user_id in self.active_sessions.get(session_id, {}).get("participants", {}):
                        del self.active_sessions[session_id]["participants"][user_id]

                # Broadcast leave event
                await self._broadcast_event(session_id, CollaborationEvent.USER_LEFT, user_id, {
                    "username": f"User {user_id[:8]}"
                })

                # Check if session should be archived (no active participants)
                if len(self.session_participants.get(session_id, set())) == 0:
                    await self._archive_session(session, session_id)

                logger.info(f"User {user_id} left collaborative session {session_id}")

                return {"success": True}

            return {"success": False, "error": "Not a participant in this session"}

        except Exception as e:
            logger.error(f"Failed to leave session {session_id}: {e}")
            return {"success": False, "error": str(e)}

    async def send_message(self, session, user_id: str, session_id: str,
                          message: str, message_type: str = "text") -> Dict[str, Any]:
        """
        Send a message in a collaborative session.

        Args:
            session: Database session
            user_id: Message sender
            session_id: Target session
            message: Message content
            message_type: Type of message (text, system, etc.)

        Returns:
            Send result
        """
        try:
            # Verify user is participant
            if not await self._is_participant(session, user_id, session_id):
                return {"success": False, "error": "Not a participant in this session"}

            # Create message record
            session_message = SessionMessage(
                session_id=session_id,
                user_id=user_id,
                message_type=message_type,
                content=message,
                metadata=json.dumps({"timestamp": datetime.utcnow().isoformat()})
            )

            session.add(session_message)
            await session.commit()

            # Broadcast message event
            await self._broadcast_event(session_id, CollaborationEvent.MESSAGE_SENT, user_id, {
                "message_id": str(session_message.id),
                "message": message,
                "message_type": message_type,
                "username": f"User {user_id[:8]}"
            })

            # Update session activity
            await self._update_session_activity(session_id)

            return {
                "success": True,
                "message_id": str(session_message.id),
                "timestamp": session_message.created_at.isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to send message in session {session_id}: {e}")
            await session.rollback()
            return {"success": False, "error": str(e)}

    async def add_artifact(self, session, user_id: str, session_id: str,
                          artifact_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add an artifact to a collaborative session.

        Args:
            session: Database session
            user_id: Artifact creator
            session_id: Target session
            artifact_data: Artifact information

        Returns:
            Add result
        """
        try:
            # Verify user is participant and has edit permissions
            permissions = await self._get_user_permissions(session, user_id, session_id)
            if "edit" not in permissions.get("artifacts", []):
                return {"success": False, "error": "Insufficient permissions"}

            # Create artifact
            artifact = SessionArtifact(
                session_id=session_id,
                user_id=user_id,
                artifact_type=artifact_data.get("type", "note"),
                title=artifact_data.get("title", ""),
                content=json.dumps(artifact_data.get("content", {})),
                metadata=json.dumps(artifact_data.get("metadata", {}))
            )

            session.add(artifact)
            await session.commit()
            await session.refresh(artifact)

            # Broadcast artifact event
            await self._broadcast_event(session_id, CollaborationEvent.ARTIFACT_ADDED, user_id, {
                "artifact_id": str(artifact.id),
                "artifact_type": artifact.artifact_type,
                "title": artifact.title,
                "username": f"User {user_id[:8]}"
            })

            return {
                "success": True,
                "artifact_id": str(artifact.id),
                "created_at": artifact.created_at.isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to add artifact to session {session_id}: {e}")
            await session.rollback()
            return {"success": False, "error": str(e)}

    async def get_session_state(self, session, user_id: str, session_id: str) -> Dict[str, Any]:
        """
        Get the current state of a collaborative session.

        Args:
            session: Database session
            user_id: Requesting user
            session_id: Target session

        Returns:
            Session state
        """
        try:
            # Verify user has access
            if not await self._is_participant(session, user_id, session_id):
                return {"success": False, "error": "Access denied"}

            # Get session info
            collab_session = await session.get(CollaborativeSession, session_id)
            if not collab_session:
                return {"success": False, "error": "Session not found"}

            # Get participants
            participants_query = session.query(SessionParticipant).filter(
                SessionParticipant.session_id == session_id,
                SessionParticipant.left_at.is_(None)  # Active participants
            )
            participants_result = await session.execute(participants_query)
            participants = participants_result.scalars().all()

            # Get recent messages
            messages_query = session.query(SessionMessage).filter(
                SessionMessage.session_id == session_id
            ).order_by(SessionMessage.created_at.desc()).limit(50)

            messages_result = await session.execute(messages_query)
            messages = messages_result.scalars().all()

            # Get artifacts
            artifacts_query = session.query(SessionArtifact).filter(
                SessionArtifact.session_id == session_id
            ).order_by(SessionArtifact.created_at.desc())

            artifacts_result = await session.execute(artifacts_query)
            artifacts = artifacts_result.scalars().all()

            return {
                "success": True,
                "session": {
                    "id": str(collab_session.id),
                    "title": collab_session.title,
                    "description": collab_session.description,
                    "owner_id": collab_session.owner_id,
                    "status": collab_session.status,
                    "settings": json.loads(collab_session.settings) if collab_session.settings else {},
                    "tags": json.loads(collab_session.tags) if collab_session.tags else [],
                    "created_at": collab_session.created_at.isoformat(),
                    "updated_at": collab_session.updated_at.isoformat() if collab_session.updated_at else None
                },
                "participants": [
                    {
                        "user_id": p.user_id,
                        "role": p.role,
                        "joined_at": p.joined_at.isoformat(),
                        "permissions": json.loads(p.permissions) if p.permissions else {}
                    }
                    for p in participants
                ],
                "recent_messages": [
                    {
                        "id": str(m.id),
                        "user_id": m.user_id,
                        "message_type": m.message_type,
                        "content": m.content,
                        "created_at": m.created_at.isoformat()
                    }
                    for m in messages
                ],
                "artifacts": [
                    {
                        "id": str(a.id),
                        "user_id": a.user_id,
                        "artifact_type": a.artifact_type,
                        "title": a.title,
                        "content": json.loads(a.content) if a.content else {},
                        "metadata": json.loads(a.metadata) if a.metadata else {},
                        "created_at": a.created_at.isoformat(),
                        "updated_at": a.updated_at.isoformat() if a.updated_at else None
                    }
                    for a in artifacts
                ]
            }

        except Exception as e:
            logger.error(f"Failed to get session state for {session_id}: {e}")
            return {"success": False, "error": str(e)}

    async def update_session_settings(self, session, user_id: str, session_id: str,
                                    settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update collaborative session settings.

        Args:
            session: Database session
            user_id: User making the update
            session_id: Target session
            settings: New settings

        Returns:
            Update result
        """
        try:
            # Verify user has admin permissions
            permissions = await self._get_user_permissions(session, user_id, session_id)
            if "admin" not in permissions.get("session", []):
                return {"success": False, "error": "Insufficient permissions"}

            # Update session
            collab_session = await session.get(CollaborativeSession, session_id)
            if not collab_session:
                return {"success": False, "error": "Session not found"}

            # Update allowed settings
            if "title" in settings:
                collab_session.title = settings["title"]
            if "description" in settings:
                collab_session.description = settings["description"]
            if "max_participants" in settings:
                collab_session.max_participants = min(settings["max_participants"], self.max_participants_per_session)
            if "is_public" in settings:
                collab_session.is_public = settings["is_public"]
            if "tags" in settings:
                collab_session.tags = json.dumps(settings["tags"])

            collab_session.updated_at = datetime.utcnow()
            await session.commit()

            # Broadcast settings change
            await self._broadcast_event(session_id, CollaborationEvent.STATUS_CHANGED, user_id, {
                "settings_updated": True,
                "updated_fields": list(settings.keys())
            })

            return {"success": True, "updated_at": collab_session.updated_at.isoformat()}

        except Exception as e:
            logger.error(f"Failed to update session settings: {e}")
            await session.rollback()
            return {"success": False, "error": str(e)}

    async def list_user_sessions(self, session, user_id: str,
                               include_archived: bool = False) -> Dict[str, Any]:
        """
        List collaborative sessions for a user.

        Args:
            session: Database session
            user_id: Target user
            include_archived: Whether to include archived sessions

        Returns:
            User's sessions
        """
        try:
            # Get sessions where user is owner or participant
            owner_sessions = session.query(CollaborativeSession).filter(
                CollaborativeSession.owner_id == user_id
            )

            if not include_archived:
                owner_sessions = owner_sessions.filter(
                    CollaborativeSession.status != SessionStatus.ARCHIVED.value
                )

            owner_result = await session.execute(owner_sessions)
            owned_sessions = owner_result.scalars().all()

            # Get sessions where user is participant
            participant_sessions_query = session.query(CollaborativeSession).join(
                SessionParticipant,
                CollaborativeSession.id == SessionParticipant.session_id
            ).filter(
                SessionParticipant.user_id == user_id,
                SessionParticipant.left_at.is_(None)  # Still active
            )

            if not include_archived:
                participant_sessions_query = participant_sessions_query.filter(
                    CollaborativeSession.status != SessionStatus.ARCHIVED.value
                )

            participant_result = await session.execute(participant_sessions_query)
            participated_sessions = participant_result.scalars().all()

            # Combine and deduplicate
            all_sessions = list(set(owned_sessions + participated_sessions))

            sessions_data = []
            for sess in all_sessions:
                # Get participant count
                participant_count = await self._count_session_participants(session, str(sess.id))

                # Check if user is owner
                is_owner = sess.owner_id == user_id

                sessions_data.append({
                    "id": str(sess.id),
                    "title": sess.title,
                    "description": sess.description,
                    "status": sess.status,
                    "is_owner": is_owner,
                    "participant_count": participant_count,
                    "max_participants": sess.max_participants,
                    "is_public": sess.is_public,
                    "tags": json.loads(sess.tags) if sess.tags else [],
                    "created_at": sess.created_at.isoformat(),
                    "updated_at": sess.updated_at.isoformat() if sess.updated_at else None,
                    "last_activity": self.active_sessions.get(str(sess.id), {}).get("last_activity")
                })

            return {
                "success": True,
                "sessions": sessions_data,
                "total": len(sessions_data)
            }

        except Exception as e:
            logger.error(f"Failed to list user sessions: {e}")
            return {"success": False, "error": str(e), "sessions": [], "total": 0}

    # Helper methods

    def _get_role_permissions(self, role: CollaborationRole) -> Dict[str, List[str]]:
        """Get permissions for a collaboration role."""
        base_permissions = {
            "session": ["view"],
            "chat": ["read"],
            "artifacts": ["view"]
        }

        if role == CollaborationRole.EDITOR:
            base_permissions.update({
                "chat": ["read", "write"],
                "artifacts": ["view", "create", "edit"],
                "research": ["view", "contribute"]
            })
        elif role == CollaborationRole.OWNER:
            base_permissions.update({
                "session": ["view", "edit", "delete", "manage_participants"],
                "chat": ["read", "write", "moderate"],
                "artifacts": ["view", "create", "edit", "delete"],
                "research": ["view", "contribute", "manage"],
                "admin": ["full_access"]
            })

        return base_permissions

    async def _is_participant(self, session, user_id: str, session_id: str) -> bool:
        """Check if user is an active participant in session."""
        try:
            participant_query = session.query(SessionParticipant).filter(
                SessionParticipant.session_id == session_id,
                SessionParticipant.user_id == user_id,
                SessionParticipant.left_at.is_(None)
            )
            result = await session.execute(participant_query)
            return result.scalar_one_or_none() is not None
        except Exception:
            return False

    async def _get_user_permissions(self, session, user_id: str, session_id: str) -> Dict[str, Any]:
        """Get user's permissions in a session."""
        try:
            participant_query = session.query(SessionParticipant).filter(
                SessionParticipant.session_id == session_id,
                SessionParticipant.user_id == user_id,
                SessionParticipant.left_at.is_(None)
            )
            result = await session.execute(participant_query)
            participant = result.scalar_one_or_none()

            if participant:
                return json.loads(participant.permissions) if participant.permissions else {}
            else:
                # Check if user is owner
                session_query = session.query(CollaborativeSession).filter(
                    CollaborativeSession.id == session_id,
                    CollaborativeSession.owner_id == user_id
                )
                session_result = await session.execute(session_query)
                if session_result.scalar_one_or_none():
                    return self._get_role_permissions(CollaborationRole.OWNER)

            return {}
        except Exception as e:
            logger.error(f"Error getting user permissions: {e}")
            return {}

    async def _count_user_sessions(self, session, user_id: str) -> int:
        """Count active sessions for a user."""
        try:
            count_query = session.query(CollaborativeSession).filter(
                CollaborativeSession.owner_id == user_id,
                CollaborativeSession.status.in_([SessionStatus.ACTIVE.value, SessionStatus.PAUSED.value])
            )
            result = await session.execute(count_query)
            sessions = result.scalars().all()
            return len(sessions)
        except Exception:
            return 0

    async def _count_session_participants(self, session, session_id: str) -> int:
        """Count active participants in a session."""
        try:
            count_query = session.query(SessionParticipant).filter(
                SessionParticipant.session_id == session_id,
                SessionParticipant.left_at.is_(None)
            )
            result = await session.execute(count_query)
            participants = result.scalars().all()
            return len(participants)
        except Exception:
            return 0

    async def _broadcast_event(self, session_id: str, event_type: CollaborationEvent,
                              user_id: str, data: Dict[str, Any]):
        """Broadcast event to all session participants."""
        # This would integrate with WebSocket broadcasting
        # For now, just log the event
        event = CollaborationMessage(
            event_type=event_type,
            session_id=session_id,
            user_id=user_id,
            username=f"User {user_id[:8]}",  # TODO: Get actual username
            data=data,
            timestamp=datetime.utcnow()
        )

        logger.info(f"Collaboration event: {event.event_type.value} in session {session_id}")

        # TODO: Implement actual WebSocket broadcasting
        # await websocket_manager.broadcast_to_session(session_id, event.to_dict())

    async def _update_session_activity(self, session_id: str):
        """Update session last activity timestamp."""
        if session_id in self.active_sessions:
            self.active_sessions[session_id]["last_activity"] = datetime.utcnow().isoformat()

    async def _archive_session(self, session, session_id: str):
        """Archive a session with no active participants."""
        try:
            collab_session = await session.get(CollaborativeSession, session_id)
            if collab_session:
                collab_session.status = SessionStatus.ARCHIVED.value
                collab_session.updated_at = datetime.utcnow()
                await session.commit()

                # Clean up in-memory tracking
                if session_id in self.active_sessions:
                    del self.active_sessions[session_id]
                if session_id in self.session_participants:
                    del self.session_participants[session_id]

                logger.info(f"Archived session {session_id} due to no active participants")

        except Exception as e:
            logger.error(f"Failed to archive session {session_id}: {e}")

    async def cleanup_inactive_sessions(self, session):
        """Clean up sessions that have been inactive for too long."""
        try:
            # Find sessions inactive for more than timeout period
            timeout_threshold = datetime.utcnow() - timedelta(hours=self.session_timeout_hours)

            inactive_sessions_query = session.query(CollaborativeSession).filter(
                CollaborativeSession.status == SessionStatus.ACTIVE.value,
                CollaborativeSession.updated_at < timeout_threshold
            )

            inactive_result = await session.execute(inactive_sessions_query)
            inactive_sessions = inactive_result.scalars().all()

            archived_count = 0
            for sess in inactive_sessions:
                sess.status = SessionStatus.ARCHIVED.value
                sess.updated_at = datetime.utcnow()
                archived_count += 1

                # Clean up in-memory tracking
                session_id_str = str(sess.id)
                if session_id_str in self.active_sessions:
                    del self.active_sessions[session_id_str]
                if session_id_str in self.session_participants:
                    del self.session_participants[session_id_str]

            if archived_count > 0:
                await session.commit()
                logger.info(f"Archived {archived_count} inactive sessions")

            return archived_count

        except Exception as e:
            logger.error(f"Failed to cleanup inactive sessions: {e}")
            await session.rollback()
            return 0
