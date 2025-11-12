"""
Speech-to-Text API endpoints
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
import logging

from app.services.stt_service import stt_service

logger = logging.getLogger(__name__)

router = APIRouter()


class STTResponse(BaseModel):
    """STT response model"""
    text: str
    language: str
    confidence: float
    duration: float


@router.post("/stt", response_model=STTResponse)
async def speech_to_text(
    audio: UploadFile = File(...),
    language: str = None
):
    """
    Convert speech to text
    
    Args:
        audio: Audio file (WAV, MP3, WebM, etc.)
        language: Optional language code (e.g., 'en', 'es')
    
    Returns:
        STTResponse: Transcription result
    """
    try:
        # Read audio file
        audio_data = await audio.read()
        
        # Get file extension
        file_format = audio.filename.split('.')[-1] if '.' in audio.filename else 'wav'
        
        # Transcribe
        result = await stt_service.transcribe(
            audio_data,
            language=language,
            format=file_format
        )
        
        return STTResponse(**result)
        
    except Exception as e:
        logger.error(f"STT endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

