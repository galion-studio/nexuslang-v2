"""
Collaborative research API routes.
Handles multi-user research sessions and real-time collaboration.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import asyncio

from ..core.database import get_db
from ..api.auth import get_current_user
from ..models.user import User
from ..services.collaboration.collaborative_research import CollaborativeResearchManager

router = APIRouter()


# Request/Response Models

class CreateSessionRequest(BaseModel):
    """Request model for creating collaborative sessions."""
    title: str = Field(..., min_length=1, max_length=200, description="Session title")
    description: str = Field("", max_length=1000, description="Session description")
    settings: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Session settings")
    tags: Optional[List[str]] = Field(default_factory=list, description="Session tags")
    max_participants: Optional[int] = Field(10, ge=1, le=50, description="Maximum participants")
    is_public: Optional[bool] = Field(False, description="Whether session is public")


class CreateSessionResponse(BaseModel):
    """Response model for session creation."""
    success: bool
    session_id: Optional[str] = None
    title: Optional[str] = None
    created_at: Optional[str] = None
    error: Optional[str] = None


class JoinSessionRequest(BaseModel):
    """Request model for joining sessions."""
    invite_code: Optional[str] = Field(None, description="Invite code for private sessions")


class JoinSessionResponse(BaseModel):
    """Response model for joining sessions."""
    success: bool
    session_id: Optional[str] = None
    role: Optional[str] = None
    permissions: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class SendMessageRequest(BaseModel):
    """Request model for sending messages."""
    message: str = Field(..., min_length=1, max_length=2000, description="Message content")
    message_type: Optional[str] = Field("text", description="Message type: text, system, etc.")


class SendMessageResponse(BaseModel):
    """Response model for sending messages."""
    success: bool
    message_id: Optional[str] = None
    timestamp: Optional[str] = None
    error: Optional[str] = None


class AddArtifactRequest(BaseModel):
    """Request model for adding artifacts."""
    artifact_type: str = Field(..., description="Type of artifact")
    title: str = Field(..., min_length=1, max_length=200, description="Artifact title")
    content: Dict[str, Any] = Field(..., description="Artifact content")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class AddArtifactResponse(BaseModel):
    """Response model for adding artifacts."""
    success: bool
    artifact_id: Optional[str] = None
    created_at: Optional[str] = None
    error: Optional[str] = None


class UpdateSessionRequest(BaseModel):
    """Request model for updating sessions."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    max_participants: Optional[int] = Field(None, ge=1, le=50)
    is_public: Optional[bool] = Field(None)
    tags: Optional[List[str]] = Field(None)


class UpdateSessionResponse(BaseModel):
    """Response model for session updates."""
    success: bool
    updated_at: Optional[str] = None
    error: Optional[str] = None


class SessionInfo(BaseModel):
    """Information about a collaborative session."""
    id: str
    title: str
    description: str
    status: str
    is_owner: bool
    participant_count: int
    max_participants: int
    is_public: bool
    tags: List[str]
    created_at: str
    updated_at: Optional[str] = None
    last_activity: Optional[str] = None


class ListSessionsResponse(BaseModel):
    """Response model for listing sessions."""
    success: bool
    sessions: List[SessionInfo]
    total: int
    error: Optional[str] = None


class SessionStateResponse(BaseModel):
    """Response model for session state."""
    success: bool
    session: Optional[Dict[str, Any]] = None
    participants: Optional[List[Dict[str, Any]]] = None
    recent_messages: Optional[List[Dict[str, Any]]] = None
    artifacts: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None


# WebSocket connection manager for real-time collaboration
class CollaborationWebSocketManager:
    """Manages WebSocket connections for collaborative sessions."""

    def __init__(self):
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}  # session_id -> {user_id -> websocket}
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}  # connection_id -> metadata

    async def connect(self, websocket: WebSocket, session_id: str, user_id: str):
        """Connect a user to a collaborative session."""
        await websocket.accept()

        if session_id not in self.active_connections:
            self.active_connections[session_id] = {}

        self.active_connections[session_id][user_id] = websocket

        # Store connection metadata
        connection_id = f"{session_id}:{user_id}"
        self.connection_metadata[connection_id] = {
            "connected_at": datetime.utcnow().isoformat(),
            "session_id": session_id,
            "user_id": user_id
        }

    def disconnect(self, session_id: str, user_id: str):
        """Disconnect a user from a session."""
        if session_id in self.active_connections and user_id in self.active_connections[session_id]:
            del self.active_connections[session_id][user_id]

            # Clean up empty session connections
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]

        # Clean up metadata
        connection_id = f"{session_id}:{user_id}"
        if connection_id in self.connection_metadata:
            del self.connection_metadata[connection_id]

    async def broadcast_to_session(self, session_id: str, message: Dict[str, Any],
                                 exclude_user: Optional[str] = None):
        """Broadcast a message to all users in a session."""
        if session_id not in self.active_connections:
            return

        disconnected_users = []

        for user_id, websocket in self.active_connections[session_id].items():
            if user_id == exclude_user:
                continue

            try:
                await websocket.send_json(message)
            except Exception as e:
                # User disconnected
                disconnected_users.append(user_id)

        # Clean up disconnected users
        for user_id in disconnected_users:
            self.disconnect(session_id, user_id)

    async def send_to_user(self, session_id: str, user_id: str, message: Dict[str, Any]):
        """Send a message to a specific user in a session."""
        if (session_id in self.active_connections and
            user_id in self.active_connections[session_id]):
            try:
                await self.active_connections[session_id][user_id].send_json(message)
            except Exception as e:
                # User disconnected, clean up
                self.disconnect(session_id, user_id)


# Global WebSocket manager instance
websocket_manager = CollaborationWebSocketManager()


# API Endpoints

@router.post("/sessions", response_model=CreateSessionResponse)
async def create_collaborative_session(
    request: CreateSessionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new collaborative research session.

    Allows users to start multi-user research sessions with real-time
    collaboration features.
    """
    try:
        collab_manager = CollaborativeResearchManager()

        session_data = request.dict()
        # Remove None values
        session_data = {k: v for k, v in session_data.items() if v is not None}

        result = await collab_manager.create_collaborative_session(db, current_user.id, session_data)

        return CreateSessionResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create collaborative session: {str(e)}"
        )


@router.post("/sessions/{session_id}/join", response_model=JoinSessionResponse)
async def join_session(
    session_id: str,
    request: JoinSessionRequest = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Join an existing collaborative session.

    Allows users to participate in ongoing research sessions.
    """
    try:
        collab_manager = CollaborativeResearchManager()

        invite_code = request.invite_code if request else None

        result = await collab_manager.join_session(db, current_user.id, session_id, invite_code)

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=result.get("error", "Failed to join session")
            )

        return JoinSessionResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to join session: {str(e)}"
        )


@router.post("/sessions/{session_id}/leave")
async def leave_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Leave a collaborative session.

    Removes the user from active participation in the session.
    """
    try:
        collab_manager = CollaborativeResearchManager()

        result = await collab_manager.leave_session(db, current_user.id, session_id)

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get("error", "Not a participant in this session")
            )

        return {"success": True, "message": "Left session successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to leave session: {str(e)}"
        )


@router.get("/sessions", response_model=ListSessionsResponse)
async def list_user_sessions(
    include_archived: bool = Query(False, description="Include archived sessions"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List collaborative sessions for the current user.

    Returns sessions owned by the user and sessions they participate in.
    """
    try:
        collab_manager = CollaborativeResearchManager()

        result = await collab_manager.list_user_sessions(db, current_user.id, include_archived)

        return ListSessionsResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list sessions: {str(e)}"
        )


@router.get("/sessions/{session_id}", response_model=SessionStateResponse)
async def get_session_state(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the current state of a collaborative session.

    Returns session information, participants, recent messages, and artifacts.
    """
    try:
        collab_manager = CollaborativeResearchManager()

        result = await collab_manager.get_session_state(db, current_user.id, session_id)

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=result.get("error", "Access denied")
            )

        return SessionStateResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session state: {str(e)}"
        )


@router.put("/sessions/{session_id}", response_model=UpdateSessionResponse)
async def update_session(
    session_id: str,
    request: UpdateSessionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update collaborative session settings.

    Allows session owners to modify session configuration.
    """
    try:
        collab_manager = CollaborativeResearchManager()

        update_data = request.dict(exclude_unset=True)

        result = await collab_manager.update_session_settings(
            db, current_user.id, session_id, update_data
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=result.get("error", "Permission denied")
            )

        return UpdateSessionResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update session: {str(e)}"
        )


@router.post("/sessions/{session_id}/messages", response_model=SendMessageResponse)
async def send_message(
    session_id: str,
    request: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Send a message in a collaborative session.

    Enables real-time communication between session participants.
    """
    try:
        collab_manager = CollaborativeResearchManager()

        result = await collab_manager.send_message(
            db, current_user.id, session_id, request.message, request.message_type
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=result.get("error", "Failed to send message")
            )

        return SendMessageResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send message: {str(e)}"
        )


@router.post("/sessions/{session_id}/artifacts", response_model=AddArtifactResponse)
async def add_artifact(
    session_id: str,
    request: AddArtifactRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Add an artifact to a collaborative session.

    Allows participants to contribute research notes, findings, and documents.
    """
    try:
        collab_manager = CollaborativeResearchManager()

        artifact_data = {
            "type": request.artifact_type,
            "title": request.title,
            "content": request.content,
            "metadata": request.metadata
        }

        result = await collab_manager.add_artifact(
            db, current_user.id, session_id, artifact_data
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=result.get("error", "Failed to add artifact")
            )

        return AddArtifactResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add artifact: {str(e)}"
        )


@router.websocket("/ws/sessions/{session_id}")
async def collaborative_websocket(
    websocket: WebSocket,
    session_id: str,
    token: str = Query(...),  # JWT token for authentication
    db: AsyncSession = Depends(get_db)
):
    """
    WebSocket endpoint for real-time collaborative session communication.

    Provides live updates for messages, artifacts, participant changes, and research updates.
    """
    # TODO: Implement JWT token validation
    # For now, accept any connection (in production, validate token)

    user_id = "test_user"  # TODO: Extract from validated JWT token
    username = f"User {user_id[:8]}"  # TODO: Get from user database

    try:
        # Connect to session
        await websocket_manager.connect(websocket, session_id, user_id)

        # Send welcome message
        await websocket.send_json({
            "type": "welcome",
            "session_id": session_id,
            "user_id": user_id,
            "username": username,
            "timestamp": datetime.utcnow().isoformat()
        })

        # Broadcast user joined event
        await websocket_manager.broadcast_to_session(
            session_id,
            {
                "type": "user_joined",
                "user_id": user_id,
                "username": username,
                "timestamp": datetime.utcnow().isoformat()
            },
            exclude_user=user_id
        )

        # Message handling loop
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_json()

                message_type = data.get("type", "unknown")

                if message_type == "ping":
                    # Respond to ping
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    })

                elif message_type == "message":
                    # Handle chat message
                    collab_manager = CollaborativeResearchManager()
                    result = await collab_manager.send_message(
                        db, user_id, session_id, data.get("content", ""), data.get("message_type", "text")
                    )

                    if result["success"]:
                        # Broadcast message to all participants
                        await websocket_manager.broadcast_to_session(
                            session_id,
                            {
                                "type": "message",
                                "message_id": result["message_id"],
                                "user_id": user_id,
                                "username": username,
                                "content": data.get("content", ""),
                                "message_type": data.get("message_type", "text"),
                                "timestamp": result["timestamp"]
                            }
                        )

                elif message_type == "artifact":
                    # Handle artifact addition
                    collab_manager = CollaborativeResearchManager()
                    artifact_data = {
                        "type": data.get("artifact_type", "note"),
                        "title": data.get("title", ""),
                        "content": data.get("content", {}),
                        "metadata": data.get("metadata", {})
                    }

                    result = await collab_manager.add_artifact(
                        db, user_id, session_id, artifact_data
                    )

                    if result["success"]:
                        # Broadcast artifact addition
                        await websocket_manager.broadcast_to_session(
                            session_id,
                            {
                                "type": "artifact_added",
                                "artifact_id": result["artifact_id"],
                                "user_id": user_id,
                                "username": username,
                                "artifact_type": artifact_data["type"],
                                "title": artifact_data["title"],
                                "timestamp": result["created_at"]
                            }
                        )

                # Handle other message types as needed

            except json.JSONDecodeError:
                # Invalid JSON, ignore
                continue

    except WebSocketDisconnect:
        # User disconnected
        websocket_manager.disconnect(session_id, user_id)

        # Broadcast user left event
        await websocket_manager.broadcast_to_session(
            session_id,
            {
                "type": "user_left",
                "user_id": user_id,
                "username": username,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    except Exception as e:
        # Handle unexpected errors
        try:
            websocket_manager.disconnect(session_id, user_id)
        except:
            pass

        logger.error(f"WebSocket error for session {session_id}, user {user_id}: {e}")


@router.get("/sessions/{session_id}/export")
async def export_session_data(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Export collaborative session data.

    Provides a complete export of session messages, artifacts, and metadata.
    """
    try:
        collab_manager = CollaborativeResearchManager()

        # Get session state (this will validate permissions)
        session_state = await collab_manager.get_session_state(db, current_user.id, session_id)

        if not session_state["success"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        # Format export data
        export_data = {
            "export_timestamp": datetime.utcnow().isoformat(),
            "session_id": session_id,
            "exported_by": current_user.id,
            "data": session_state
        }

        return {
            "success": True,
            "export_data": export_data,
            "message_count": len(session_state.get("recent_messages", [])),
            "artifact_count": len(session_state.get("artifacts", [])),
            "participant_count": len(session_state.get("participants", []))
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export session data: {str(e)}"
        )
