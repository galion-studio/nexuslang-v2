"""
Voice API Endpoints - FastAPI routes for voice services
Provides REST and WebSocket endpoints for STT, TTS, and voice session management

Endpoints:
- POST /api/v2/voice/transcribe - Transcribe audio to text
- POST /api/v2/voice/synthesize - Generate speech from text
- GET /api/v2/voice/voices - List available voices
- POST /api/v2/voice/session/start - Start voice session
- POST /api/v2/voice/session/end - End voice session
- GET /api/v2/voice/session/{id}/stats - Get session stats
- GET /api/v2/voice/health - Health check
- WebSocket /ws/voice - Real-time voice streaming
"""

import logging
import base64
from typing import Optional, Dict, Any, List
from datetime import datetime

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

# Import voice services
from ..services.voice.stt_service import stt_service, STTRequest, STTResponse
from ..services.voice.tts_service import tts_service, TTSRequest, TTSResponse
from ..services.voice.voice_session import VoiceSessionService, VoiceSessionData, VoiceCommandData

# Database dependency
from ..core.database import get_db
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/voice", tags=["voice"])

# Pydantic models for API requests/responses
class TranscribeRequest(BaseModel):
    """Request model for transcription"""
    audio_data: str = Field(..., description="Base64 encoded audio data")
    language: str = Field(default="en", description="Language code")
    model: str = Field(default="whisper-1", description="STT model to use")

class SynthesizeRequest(BaseModel):
    """Request model for speech synthesis"""
    text: str = Field(..., description="Text to convert to speech")
    voice: str = Field(default="alloy", description="Voice to use")
    model: str = Field(default="tts-1", description="TTS model to use")
    speed: float = Field(default=1.0, description="Speech speed (0.25-4.0)")

class SessionStartRequest(BaseModel):
    """Request to start a voice session"""
    platform: str = Field(default="galion-app", description="Platform name")

class SessionEndRequest(BaseModel):
    """Request to end a voice session"""
    session_id: str = Field(..., description="Session ID to end")

# Enhanced endpoints using real services
@router.post("/transcribe")
async def transcribe_audio(request: TranscribeRequest):
    """
    Transcribe audio data to text using OpenAI Whisper
    """
    try:
        logger.info(f"Voice transcription requested: {len(request.audio_data)} chars of base64 data")

        if not stt_service.is_available():
            raise HTTPException(status_code=503, detail="STT service not available")

        # Convert base64 to bytes
        try:
            audio_bytes = base64.b64decode(request.audio_data)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid base64 audio data: {str(e)}")

        # Create STT request
        stt_request = STTRequest(
            audio_data=audio_bytes,
            language=request.language,
            model=request.model
        )

        # Process transcription
        response = await stt_service.transcribe_audio(stt_request)

        return {
            "text": response.text,
            "confidence": response.confidence,
            "language": response.language,
            "processing_time": response.processing_time,
            "model": response.model,
            "status": "success"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transcription failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@router.post("/synthesize")
async def synthesize_speech(request: SynthesizeRequest):
    """
    Generate speech from text using OpenAI TTS
    """
    try:
        logger.info(f"Voice synthesis requested: '{request.text[:50]}...' with voice '{request.voice}'")

        if not tts_service.is_available():
            raise HTTPException(status_code=503, detail="TTS service not available")

        # Create TTS request
        tts_request = TTSRequest(
            text=request.text,
            voice=request.voice,
            model=request.model,
            speed=request.speed
        )

        # Generate speech
        response = await tts_service.generate_speech(tts_request)

        # Return audio stream
        return StreamingResponse(
            iter([response.audio_data]),
            media_type=response.content_type,
            headers={
                "Content-Length": str(len(response.audio_data)),
                "X-Voice": response.voice,
                "X-Text-Length": str(len(response.text)),
                "X-Processing-Time": str(response.processing_time),
                "X-Estimated-Duration": str(response.duration_estimate)
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"TTS generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Speech synthesis failed: {str(e)}")

@router.get("/voices")
async def get_available_voices():
    """
    Get list of available voices for TTS
    """
    try:
        voices = await tts_service.get_available_voices()

        voice_list = []
        for voice_id, config in voices.items():
            voice_list.append({
                "id": voice_id,
                "name": voice_id.title(),
                "language": "en",
                "gender": config.get("gender", "neutral"),
                "style": config.get("style", "neutral")
            })

        return {
            "voices": voice_list,
            "count": len(voice_list)
        }

    except Exception as e:
        logger.error(f"Failed to get voices: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve voices")

@router.post("/session/start")
async def start_voice_session(
    request: SessionStartRequest,
    db: Session = Depends(get_db)
):
    """
    Start a new voice session
    """
    try:
        # For now, we'll use a mock user_id - in production this would come from auth
        user_id = "mock_user_id"

        session_service = VoiceSessionService(db)
        session_id = await session_service.create_session(user_id, request.platform)

        return {
            "session_id": session_id,
            "status": "started",
            "platform": request.platform,
            "timestamp": datetime.utcnow()
        }

    except Exception as e:
        logger.error(f"Failed to start session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start session: {str(e)}")

@router.post("/session/end")
async def end_voice_session(
    request: SessionEndRequest,
    db: Session = Depends(get_db)
):
    """
    End a voice session
    """
    try:
        session_service = VoiceSessionService(db)
        success = await session_service.end_session(request.session_id)

        if not success:
            raise HTTPException(status_code=404, detail="Session not found or already ended")

        return {
            "session_id": request.session_id,
            "status": "ended",
            "timestamp": datetime.utcnow()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to end session {request.session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to end session: {str(e)}")

@router.get("/session/{session_id}/stats")
async def get_session_stats(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Get statistics for a voice session
    """
    try:
        # For now, we'll use a mock user_id - in production this would come from auth
        user_id = "mock_user_id"

        session_service = VoiceSessionService(db)
        stats = await session_service.get_session_stats(user_id)

        return {
            "session_id": session_id,
            "stats": stats,
            "timestamp": datetime.utcnow()
        }

    except Exception as e:
        logger.error(f"Failed to get session stats for {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get session stats: {str(e)}")

@router.get("/health")
async def voice_health_check():
    """
    Health check for voice services
    """
    stt_available = stt_service.is_available()
    tts_available = tts_service.is_available()

    overall_status = "healthy" if (stt_available and tts_available) else "degraded"

    return {
        "status": overall_status,
        "stt": {
            "healthy": stt_available,
            "mode": "whisper" if stt_available else "unavailable"
        },
        "tts": {
            "healthy": tts_available,
            "mode": "openai" if tts_available else "unavailable"
        },
        "services": {
            "total": 2,
            "healthy": (1 if stt_available else 0) + (1 if tts_available else 0),
            "unhealthy": (1 if not stt_available else 0) + (1 if not tts_available else 0)
        },
        "timestamp": datetime.utcnow()
    }

# Export router
__all__ = ["router"]