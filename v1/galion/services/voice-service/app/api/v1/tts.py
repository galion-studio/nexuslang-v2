"""
Text-to-Speech API endpoints
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
import logging

from app.services.tts_service import tts_service

logger = logging.getLogger(__name__)

router = APIRouter()


class TTSRequest(BaseModel):
    """TTS request model"""
    text: str
    voice_id: str = None
    speed: float = 1.0
    stability: float = 0.5
    similarity_boost: float = 0.75


@router.post("/tts")
async def text_to_speech(request: TTSRequest):
    """
    Convert text to speech
    
    Args:
        request: TTS request with text and voice settings
    
    Returns:
        Audio data (MP3 format)
    """
    try:
        # Generate audio
        audio_data = await tts_service.synthesize(
            text=request.text,
            voice_id=request.voice_id,
            speed=request.speed,
            stability=request.stability,
            similarity_boost=request.similarity_boost
        )
        
        # Return audio as response
        return Response(
            content=audio_data,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline; filename=speech.mp3"
            }
        )
        
    except Exception as e:
        logger.error(f"TTS endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/voices")
async def get_voices():
    """Get available voices"""
    return {
        "voices": tts_service.get_available_voices()
    }

