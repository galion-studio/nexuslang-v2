"""
Mail Integration API
Connect and manage email accounts with AI assistance
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID
import secrets
import urllib.parse
import logging

from ..api.auth import get_current_user
from ..models.user import User
from ..models.mail import (
    MailProvider, MailConnection, MailFolder,
    MailMessage, MailAIInteraction
)
from ..core.database import get_db
from ..core.errors import ResourceNotFoundError, ValidationError
from ..services.mail import MailService

router = APIRouter(prefix="/mail", tags=["Mail Integration"])
logger = logging.getLogger(__name__)


# Request/Response Models
class MailProviderResponse(BaseModel):
    id: str
    name: str
    display_name: str
    is_active: bool


class MailConnectionRequest(BaseModel):
    provider_name: str = Field(..., description="Email provider (gmail, outlook, yahoo, etc.)")
    email: EmailStr
    use_oauth: bool = True
    imap_username: Optional[str] = None
    imap_password: Optional[str] = None
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None


class MailConnectionResponse(BaseModel):
    id: str
    provider_name: str
    email: str
    display_name: Optional[str]
    is_primary: bool
    sync_enabled: bool
    sync_frequency: str
    last_sync_at: Optional[datetime]
    sync_status: str
    ai_assistant_enabled: bool
    voice_responses_enabled: bool
    auto_summarize: bool
    smart_replies: bool
    priority_detection: bool
    created_at: datetime


class OAuthURLResponse(BaseModel):
    auth_url: str
    state: str


class MailFolderResponse(BaseModel):
    id: str
    name: str
    display_name: Optional[str]
    folder_type: Optional[str]
    total_messages: Optional[str]
    unread_count: Optional[str]
    ai_category: Optional[str]
    ai_priority: Optional[str]


class MailMessageResponse(BaseModel):
    id: str
    message_id: Optional[str]
    thread_id: Optional[str]
    subject: Optional[str]
    sender_name: Optional[str]
    sender_email: Optional[str]
    sent_at: Optional[datetime]
    received_at: Optional[datetime]
    is_read: bool
    is_starred: bool
    ai_summary: Optional[str]
    ai_category: Optional[str]
    ai_sentiment: Optional[str]
    ai_priority: Optional[str]
    ai_action_items: Optional[List[Dict[str, Any]]]
    ai_keywords: Optional[List[str]]
    has_attachments: bool


class MailMessageDetailResponse(BaseModel):
    id: str
    subject: Optional[str]
    sender_name: Optional[str]
    sender_email: Optional[str]
    recipients: List[Dict[str, str]]
    cc_recipients: Optional[List[Dict[str, str]]]
    sent_at: Optional[datetime]
    received_at: Optional[datetime]
    is_read: bool
    is_starred: bool
    body_text: Optional[str]
    body_html: Optional[str]
    attachments: Optional[List[Dict[str, Any]]]
    ai_summary: Optional[str]
    ai_category: Optional[str]
    ai_sentiment: Optional[str]
    ai_priority: Optional[str]
    ai_action_items: Optional[List[Dict[str, Any]]]
    ai_keywords: Optional[List[str]]
    voice_response_url: Optional[str]
    user_labels: List[str]
    user_notes: Optional[str]


class AISummaryRequest(BaseModel):
    message_id: str
    include_action_items: bool = True
    include_keywords: bool = True
    custom_instructions: Optional[str] = None


class AIResponseRequest(BaseModel):
    message_id: str
    response_type: str = Field(..., description="reply, forward, draft")
    tone: str = "professional"
    length: str = "medium"
    custom_instructions: Optional[str] = None
    generate_voice: bool = False


class MailSettingsUpdate(BaseModel):
    sync_enabled: Optional[bool] = None
    sync_frequency: Optional[str] = None
    ai_assistant_enabled: Optional[bool] = None
    voice_responses_enabled: Optional[bool] = None
    auto_summarize: Optional[bool] = None
    smart_replies: Optional[bool] = None
    priority_detection: Optional[bool] = None


# Dependencies
async def get_mail_service(db: AsyncSession = Depends(get_db)) -> MailService:
    """Get mail service instance"""
    return MailService(db)


# Provider Management
@router.get("/providers", response_model=List[MailProviderResponse])
async def list_providers(db: AsyncSession = Depends(get_db)):
    """List all supported email providers"""
    try:
        stmt = select(MailProvider).where(MailProvider.is_active == True)
        result = await db.execute(stmt)
        providers = result.scalars().all()

        return [
            MailProviderResponse(
                id=str(p.id),
                name=p.name,
                display_name=p.display_name,
                is_active=p.is_active
            )
            for p in providers
        ]
    except Exception as e:
        logger.error(f"Failed to list mail providers: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve providers")


# OAuth Flow
@router.get("/oauth/{provider_name}/url")
async def get_oauth_url(
    provider_name: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get OAuth authorization URL for a provider"""
    try:
        # Get provider configuration
        stmt = select(MailProvider).where(
            and_(MailProvider.name == provider_name, MailProvider.is_active == True)
        )
        result = await db.execute(stmt)
        provider = result.scalar_one_or_none()

        if not provider:
            raise HTTPException(status_code=404, detail="Provider not found")

        # Generate state parameter for security
        state = secrets.token_urlsafe(32)

        # Store state in session/cache (simplified - in production use Redis)
        # For now, we'll validate it contains user_id
        state_data = f"{current_user.id}:{state}"

        # Build authorization URL
        params = {
            'client_id': provider.client_id,
            'redirect_uri': f"{settings.FRONTEND_URL}/settings/mail/oauth/callback",
            'scope': provider.scope,
            'response_type': 'code',
            'state': state_data,
            'access_type': 'offline',
            'prompt': 'consent'
        }

        auth_url = f"{provider.auth_url}?{urllib.parse.urlencode(params)}"

        return OAuthURLResponse(auth_url=auth_url, state=state_data)

    except Exception as e:
        logger.error(f"Failed to generate OAuth URL for {provider_name}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate authorization URL")


@router.post("/oauth/callback")
async def handle_oauth_callback(
    code: str,
    state: str,
    error: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    mail_service: MailService = Depends(get_mail_service),
    db: AsyncSession = Depends(get_db)
):
    """Handle OAuth callback and create mail connection"""
    try:
        if error:
            raise HTTPException(status_code=400, detail=f"OAuth error: {error}")

        # Validate state parameter
        if not state or ':' not in state:
            raise HTTPException(status_code=400, detail="Invalid state parameter")

        user_id, state_token = state.split(':', 1)

        if str(current_user.id) != user_id:
            raise HTTPException(status_code=400, detail="State validation failed")

        # Exchange code for tokens and create connection
        connection = await mail_service.create_oauth_connection(
            user_id=str(current_user.id),
            auth_code=code,
            state=state
        )

        return {
            "connection_id": str(connection.id),
            "email": connection.email,
            "provider": connection.provider.name,
            "status": "connected"
        }

    except Exception as e:
        logger.error(f"OAuth callback failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to complete OAuth connection")


# Connection Management
@router.post("/connections", response_model=MailConnectionResponse)
async def create_connection(
    connection_data: MailConnectionRequest,
    current_user: User = Depends(get_current_user),
    mail_service: MailService = Depends(get_mail_service),
    db: AsyncSession = Depends(get_db)
):
    """Create a new mail connection"""
    try:
        if connection_data.use_oauth:
            # Redirect to OAuth flow
            provider_stmt = select(MailProvider).where(MailProvider.name == connection_data.provider_name)
            provider_result = await db.execute(provider_stmt)
            provider = provider_result.scalar_one_or_none()

            if not provider:
                raise HTTPException(status_code=404, detail="Provider not found")

            # Generate OAuth URL
            state = secrets.token_urlsafe(32)
            state_data = f"{current_user.id}:{state}"

            params = {
                'client_id': provider.client_id,
                'redirect_uri': f"{settings.FRONTEND_URL}/settings/mail/oauth/callback",
                'scope': provider.scope,
                'response_type': 'code',
                'state': state_data,
                'access_type': 'offline',
                'prompt': 'consent'
            }

            auth_url = f"{provider.auth_url}?{urllib.parse.urlencode(params)}"
            raise HTTPException(
                status_code=302,
                detail="Redirect to OAuth",
                headers={"Location": auth_url}
            )
        else:
            # Create IMAP/SMTP connection
            connection = await mail_service.create_manual_connection(
                user_id=str(current_user.id),
                provider_name=connection_data.provider_name,
                email=connection_data.email,
                imap_username=connection_data.imap_username,
                imap_password=connection_data.imap_password,
                smtp_username=connection_data.smtp_username,
                smtp_password=connection_data.smtp_password
            )

            return await _format_connection_response(connection)

    except Exception as e:
        logger.error(f"Failed to create mail connection: {e}")
        raise HTTPException(status_code=500, detail="Failed to create connection")


@router.get("/connections", response_model=List[MailConnectionResponse])
async def list_connections(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List user's mail connections"""
    try:
        stmt = (
            select(MailConnection)
            .where(MailConnection.user_id == current_user.id)
            .options(select("*").select_from(MailProvider))
        )
        result = await db.execute(stmt)
        connections = result.scalars().all()

        return [await _format_connection_response(conn) for conn in connections]

    except Exception as e:
        logger.error(f"Failed to list mail connections: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve connections")


@router.get("/connections/{connection_id}", response_model=MailConnectionResponse)
async def get_connection(
    connection_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific mail connection"""
    try:
        stmt = select(MailConnection).where(
            and_(
                MailConnection.id == UUID(connection_id),
                MailConnection.user_id == current_user.id
            )
        )
        result = await db.execute(stmt)
        connection = result.scalar_one_or_none()

        if not connection:
            raise HTTPException(status_code=404, detail="Connection not found")

        return await _format_connection_response(connection)

    except Exception as e:
        logger.error(f"Failed to get mail connection: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve connection")


@router.put("/connections/{connection_id}", response_model=MailConnectionResponse)
async def update_connection_settings(
    connection_id: str,
    settings: MailSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update mail connection settings"""
    try:
        stmt = select(MailConnection).where(
            and_(
                MailConnection.id == UUID(connection_id),
                MailConnection.user_id == current_user.id
            )
        )
        result = await db.execute(stmt)
        connection = result.scalar_one_or_none()

        if not connection:
            raise HTTPException(status_code=404, detail="Connection not found")

        # Update settings
        update_data = settings.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(connection, key, value)

        connection.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(connection)

        return await _format_connection_response(connection)

    except Exception as e:
        logger.error(f"Failed to update mail connection: {e}")
        raise HTTPException(status_code=500, detail="Failed to update connection")


@router.delete("/connections/{connection_id}")
async def delete_connection(
    connection_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a mail connection"""
    try:
        stmt = select(MailConnection).where(
            and_(
                MailConnection.id == UUID(connection_id),
                MailConnection.user_id == current_user.id
            )
        )
        result = await db.execute(stmt)
        connection = result.scalar_one_or_none()

        if not connection:
            raise HTTPException(status_code=404, detail="Connection not found")

        await db.delete(connection)
        await db.commit()

        return {"message": "Connection deleted successfully"}

    except Exception as e:
        logger.error(f"Failed to delete mail connection: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete connection")


@router.post("/connections/{connection_id}/sync")
async def sync_connection(
    connection_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    mail_service: MailService = Depends(get_mail_service),
    db: AsyncSession = Depends(get_db)
):
    """Trigger manual sync for a mail connection"""
    try:
        stmt = select(MailConnection).where(
            and_(
                MailConnection.id == UUID(connection_id),
                MailConnection.user_id == current_user.id
            )
        )
        result = await db.execute(stmt)
        connection = result.scalar_one_or_none()

        if not connection:
            raise HTTPException(status_code=404, detail="Connection not found")

        # Start background sync
        background_tasks.add_task(
            mail_service.sync_connection,
            str(connection.id)
        )

        return {"message": "Sync started", "connection_id": connection_id}

    except Exception as e:
        logger.error(f"Failed to start mail sync: {e}")
        raise HTTPException(status_code=500, detail="Failed to start sync")


# Folder Management
@router.get("/connections/{connection_id}/folders", response_model=List[MailFolderResponse])
async def list_folders(
    connection_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List folders for a mail connection"""
    try:
        # Verify connection ownership
        conn_stmt = select(MailConnection).where(
            and_(
                MailConnection.id == UUID(connection_id),
                MailConnection.user_id == current_user.id
            )
        )
        conn_result = await db.execute(conn_stmt)
        connection = conn_result.scalar_one_or_none()

        if not connection:
            raise HTTPException(status_code=404, detail="Connection not found")

        # Get folders
        stmt = select(MailFolder).where(MailFolder.connection_id == UUID(connection_id))
        result = await db.execute(stmt)
        folders = result.scalars().all()

        return [
            MailFolderResponse(
                id=str(f.id),
                name=f.name,
                display_name=f.display_name,
                folder_type=f.folder_type,
                total_messages=f.total_messages,
                unread_count=f.unread_count,
                ai_category=f.ai_category,
                ai_priority=f.ai_priority
            )
            for f in folders
        ]

    except Exception as e:
        logger.error(f"Failed to list mail folders: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve folders")


# Message Management
@router.get("/connections/{connection_id}/messages", response_model=List[MailMessageResponse])
async def list_messages(
    connection_id: str,
    folder_id: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    search: Optional[str] = None,
    category: Optional[str] = None,
    priority: Optional[str] = None,
    unread_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List messages for a mail connection"""
    try:
        # Verify connection ownership
        conn_stmt = select(MailConnection).where(
            and_(
                MailConnection.id == UUID(connection_id),
                MailConnection.user_id == current_user.id
            )
        )
        conn_result = await db.execute(conn_stmt)
        connection = conn_result.scalar_one_or_none()

        if not connection:
            raise HTTPException(status_code=404, detail="Connection not found")

        # Build query
        stmt = select(MailMessage).where(MailMessage.connection_id == UUID(connection_id))

        if folder_id:
            stmt = stmt.where(MailMessage.folder_id == UUID(folder_id))

        if search:
            # Simple search - in production, use full-text search
            search_filter = f"%{search}%"
            stmt = stmt.where(
                or_(
                    MailMessage.subject.ilike(search_filter),
                    MailMessage.body_text.ilike(search_filter),
                    MailMessage.sender_name.ilike(search_filter),
                    MailMessage.sender_email.ilike(search_filter)
                )
            )

        if category:
            stmt = stmt.where(MailMessage.ai_category == category)

        if priority:
            stmt = stmt.where(MailMessage.ai_priority == priority)

        if unread_only:
            stmt = stmt.where(MailMessage.is_read == False)

        stmt = stmt.order_by(desc(MailMessage.sent_at)).limit(limit).offset(offset)

        result = await db.execute(stmt)
        messages = result.scalars().all()

        return [
            MailMessageResponse(
                id=str(m.id),
                message_id=m.message_id,
                thread_id=m.thread_id,
                subject=m.subject,
                sender_name=m.sender_name,
                sender_email=m.sender_email,
                sent_at=m.sent_at,
                received_at=m.received_at,
                is_read=m.is_read,
                is_starred=m.is_starred,
                ai_summary=m.ai_summary,
                ai_category=m.ai_category,
                ai_sentiment=m.ai_sentiment,
                ai_priority=m.ai_priority,
                ai_action_items=m.ai_action_items,
                ai_keywords=m.ai_keywords,
                has_attachments=bool(m.attachments and len(m.attachments) > 0)
            )
            for m in messages
        ]

    except Exception as e:
        logger.error(f"Failed to list mail messages: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve messages")


@router.get("/messages/{message_id}", response_model=MailMessageDetailResponse)
async def get_message(
    message_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed message information"""
    try:
        stmt = (
            select(MailMessage)
            .join(MailConnection)
            .where(
                and_(
                    MailMessage.id == UUID(message_id),
                    MailConnection.user_id == current_user.id
                )
            )
        )
        result = await db.execute(stmt)
        message = result.scalar_one_or_none()

        if not message:
            raise HTTPException(status_code=404, detail="Message not found")

        return MailMessageDetailResponse(
            id=str(message.id),
            subject=message.subject,
            sender_name=message.sender_name,
            sender_email=message.sender_email,
            recipients=message.recipients or [],
            cc_recipients=message.cc_recipients,
            sent_at=message.sent_at,
            received_at=message.received_at,
            is_read=message.is_read,
            is_starred=message.is_starred,
            body_text=message.body_text,
            body_html=message.body_html,
            attachments=message.attachments,
            ai_summary=message.ai_summary,
            ai_category=message.ai_category,
            ai_sentiment=message.ai_sentiment,
            ai_priority=message.ai_priority,
            ai_action_items=message.ai_action_items,
            ai_keywords=message.ai_keywords,
            voice_response_url=message.voice_response_url,
            user_labels=message.user_labels or [],
            user_notes=message.user_notes
        )

    except Exception as e:
        logger.error(f"Failed to get mail message: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve message")


# AI Integration
@router.post("/ai/summarize")
async def generate_ai_summary(
    request: AISummaryRequest,
    current_user: User = Depends(get_current_user),
    mail_service: MailService = Depends(get_mail_service),
    db: AsyncSession = Depends(get_db)
):
    """Generate AI summary for a message"""
    try:
        summary = await mail_service.generate_ai_summary(
            user_id=str(current_user.id),
            message_id=request.message_id,
            include_action_items=request.include_action_items,
            include_keywords=request.include_keywords,
            custom_instructions=request.custom_instructions
        )

        return {"summary": summary}

    except Exception as e:
        logger.error(f"Failed to generate AI summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate summary")


@router.post("/ai/generate-response")
async def generate_ai_response(
    request: AIResponseRequest,
    current_user: User = Depends(get_current_user),
    mail_service: MailService = Depends(get_mail_service),
    db: AsyncSession = Depends(get_db)
):
    """Generate AI response for a message"""
    try:
        response = await mail_service.generate_ai_response(
            user_id=str(current_user.id),
            message_id=request.message_id,
            response_type=request.response_type,
            tone=request.tone,
            length=request.length,
            custom_instructions=request.custom_instructions,
            generate_voice=request.generate_voice
        )

        return {
            "response": response.get("text"),
            "voice_url": response.get("voice_url"),
            "suggestions": response.get("suggestions", [])
        }

    except Exception as e:
        logger.error(f"Failed to generate AI response: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate response")


@router.put("/messages/{message_id}/read")
async def mark_message_read(
    message_id: str,
    read: bool = True,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark message as read/unread"""
    try:
        stmt = (
            select(MailMessage)
            .join(MailConnection)
            .where(
                and_(
                    MailMessage.id == UUID(message_id),
                    MailConnection.user_id == current_user.id
                )
            )
        )
        result = await db.execute(stmt)
        message = result.scalar_one_or_none()

        if not message:
            raise HTTPException(status_code=404, detail="Message not found")

        message.is_read = read
        message.updated_at = datetime.utcnow()
        await db.commit()

        return {"message": "Message updated", "is_read": read}

    except Exception as e:
        logger.error(f"Failed to update message read status: {e}")
        raise HTTPException(status_code=500, detail="Failed to update message")


@router.put("/messages/{message_id}/star")
async def star_message(
    message_id: str,
    starred: bool = True,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Star/unstar a message"""
    try:
        stmt = (
            select(MailMessage)
            .join(MailConnection)
            .where(
                and_(
                    MailMessage.id == UUID(message_id),
                    MailConnection.user_id == current_user.id
                )
            )
        )
        result = await db.execute(stmt)
        message = result.scalar_one_or_none()

        if not message:
            raise HTTPException(status_code=404, detail="Message not found")

        message.is_starred = starred
        message.updated_at = datetime.utcnow()
        await db.commit()

        return {"message": "Message updated", "is_starred": starred}

    except Exception as e:
        logger.error(f"Failed to update message star status: {e}")
        raise HTTPException(status_code=500, detail="Failed to update message")


# Helper functions
async def _format_connection_response(connection: MailConnection) -> MailConnectionResponse:
    """Format mail connection for API response"""
    return MailConnectionResponse(
        id=str(connection.id),
        provider_name=connection.provider.name,
        email=connection.email,
        display_name=connection.display_name,
        is_primary=connection.is_primary,
        sync_enabled=connection.sync_enabled,
        sync_frequency=connection.sync_frequency,
        last_sync_at=connection.last_sync_at,
        sync_status=connection.sync_status,
        ai_assistant_enabled=connection.ai_assistant_enabled,
        voice_responses_enabled=connection.voice_responses_enabled,
        auto_summarize=connection.auto_summarize,
        smart_replies=connection.smart_replies,
        priority_detection=connection.priority_detection,
        created_at=connection.created_at
    )


# Import settings at the end to avoid circular imports
from ..core.config import settings
