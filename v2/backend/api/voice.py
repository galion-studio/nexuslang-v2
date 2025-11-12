"""
Voice API routes.
Handles speech-to-text, text-to-speech, and voice cloning.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import io

from ..services.voice.stt_service import get_stt_service
from ..services.voice.tts_service import get_tts_service
from ..models.user import User
from ..api.auth import get_current_user, get_optional_user

router = APIRouter()


# Request/Response Models
class TTSRequest(BaseModel):
    text: str
    voice_id: Optional[str] = None
    emotion: Optional[str] = None
    speed: float = 1.0
    language: str = "en"


class STTResponse(BaseModel):
    text: str
    language: str
    confidence: float
    segments: list


class TTSResponse(BaseModel):
    audio_url: Optional[str] = None
    text: str
    voice_id: str
    audio_base64: Optional[str] = None


class VoiceInfo(BaseModel):
    id: str
    name: str
    language: str
    gender: Optional[str] = None


# Speech-to-Text Endpoints
@router.post("/stt", response_model=STTResponse)
async def speech_to_text(
    audio: UploadFile = File(...),
    language: Optional[str] = None,
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Convert speech to text using Whisper.
    
    Supports multiple audio formats: WAV, MP3, M4A, FLAC, etc.
    Auto-detects language if not specified.
    """
    if not audio.content_type or not audio.content_type.startswith('audio/'):
        raise HTTPException(400, "File must be audio format")
    
    # Read audio data
    audio_data = await audio.read()
    
    if len(audio_data) == 0:
        raise HTTPException(400, "Audio file is empty")
    
    # Transcribe
    stt_service = get_stt_service()
    result = await stt_service.transcribe(audio_data, language)
    
    return STTResponse(**result)


@router.post("/detect-language")
async def detect_language(
    audio: UploadFile = File(...),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Detect language from audio.
    """
    if not audio.content_type or not audio.content_type.startswith('audio/'):
        raise HTTPException(400, "File must be audio format")
    
    audio_data = await audio.read()
    
    if len(audio_data) == 0:
        raise HTTPException(400, "Audio file is empty")
    
    stt_service = get_stt_service()
    language = await stt_service.detect_language(audio_data)
    
    return {"language": language}


# Text-to-Speech Endpoints
@router.post("/tts")
async def text_to_speech(
    request: TTSRequest,
    return_audio: bool = False,
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Convert text to speech using TTS.
    
    Set return_audio=true to get audio as response.
    Otherwise returns audio URL.
    """
    if not request.text.strip():
        raise HTTPException(400, "Text cannot be empty")
    
    if len(request.text) > 5000:
        raise HTTPException(400, "Text too long (max 5000 characters)")
    
    # Synthesize speech
    tts_service = get_tts_service()
    audio_data = await tts_service.synthesize(
        request.text,
        request.voice_id,
        request.emotion,
        request.speed,
        request.language
    )
    
    if return_audio:
        # Return audio directly
        return StreamingResponse(
            io.BytesIO(audio_data),
            media_type="audio/wav",
            headers={
                "Content-Disposition": "attachment; filename=speech.wav"
            }
        )
    else:
        # Return base64 encoded audio
        import base64
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        return {
            "text": request.text,
            "voice_id": request.voice_id or "default",
            "audio_base64": audio_base64,
            "format": "wav"
        }


@router.post("/synthesize")
async def synthesize_speech(
    request: TTSRequest,
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Synthesize speech and return as audio stream.
    Direct audio response for playback.
    """
    if not request.text.strip():
        raise HTTPException(400, "Text cannot be empty")
    
    # Synthesize
    tts_service = get_tts_service()
    audio_data = await tts_service.synthesize(
        request.text,
        request.voice_id,
        request.emotion,
        request.speed,
        request.language
    )
    
    # Return as audio stream
    return StreamingResponse(
        io.BytesIO(audio_data),
        media_type="audio/wav"
    )


# Voice Management Endpoints
@router.get("/voices")
async def list_voices(
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Get list of available voices for text-to-speech.
    """
    tts_service = get_tts_service()
    voices = await tts_service.list_voices()
    
    return {
        "voices": [
            {"id": v, "name": v, "language": "en", "gender": "neutral"}
            for v in voices
        ],
        "total": len(voices)
    }


@router.post("/clone")
async def clone_voice(
    samples: list[UploadFile] = File(...),
    name: str = "custom_voice",
    current_user: User = Depends(get_current_user)
):
    """
    Clone a voice from audio samples (requires authentication).
    
    Provide 2-5 high-quality audio samples of the same voice.
    Each sample should be 3-10 seconds long.
    """
    if len(samples) < 2:
        raise HTTPException(400, "At least 2 audio samples required")
    
    if len(samples) > 10:
        raise HTTPException(400, "Maximum 10 audio samples allowed")
    
    # Read all samples
    audio_samples = []
    for sample in samples:
        if not sample.content_type or not sample.content_type.startswith('audio/'):
            raise HTTPException(400, "All files must be audio format")
        
        data = await sample.read()
        if len(data) == 0:
            raise HTTPException(400, f"Audio file {sample.filename} is empty")
        
        audio_samples.append(data)
    
    # Clone voice
    tts_service = get_tts_service()
    voice_id = await tts_service.clone_voice(audio_samples, name)
    
    return {
        "voice_id": voice_id,
        "status": "completed",
        "name": name,
        "message": "Voice cloned successfully! Use this voice_id in TTS requests."
    }

