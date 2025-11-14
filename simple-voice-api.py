"""
Simple Voice API for Galion Platform
Standalone voice endpoints for testing the voice infrastructure we built
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import logging
import uvicorn
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Galion Voice API",
    description="Voice infrastructure for Galion Platform",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TranscribeRequest(BaseModel):
    audio_data: str
    language: Optional[str] = "en"

class SynthesizeRequest(BaseModel):
    text: str
    voice: Optional[str] = "alloy"

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "voice-api"}

@app.post("/api/v2/voice/transcribe")
async def transcribe_audio(request: TranscribeRequest):
    logger.info(f"Voice transcription: {len(request.audio_data)} chars, lang: {request.language}")

    return {
        "text": f"Voice transcription successful: {len(request.audio_data)} bytes processed in {request.language}",
        "confidence": 0.85,
        "language": request.language,
        "duration": 2.5,
        "status": "success"
    }

@app.post("/api/v2/voice/synthesize")
async def synthesize_speech(request: SynthesizeRequest):
    logger.info(f"Voice synthesis: '{request.text}' with voice '{request.voice}'")

    # Mock WAV file
    mock_wav = b"RIFF\x24\x08\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80>\x00\x00\x00}\x00\x00\x02\x00\x10\x00data\x00\x08\x00\x00"
    mock_wav += b"\x00\x01\x02\x03\x04\x05\x06\x07" * 50

    return StreamingResponse(
        iter([mock_wav]),
        media_type="audio/wav",
        headers={
            "X-Voice": request.voice,
            "X-Text": request.text[:50]
        }
    )

@app.get("/api/v2/voice/voices")
async def get_voices():
    return {
        "voices": [
            {"id": "alloy", "name": "Alloy", "language": "en"},
            {"id": "echo", "name": "Echo", "language": "en"},
            {"id": "nova", "name": "Nova", "language": "en"}
        ]
    }

@app.get("/api/v2/voice/health")
async def voice_health():
    return {
        "status": "healthy",
        "stt": {"healthy": True, "mode": "mock"},
        "tts": {"healthy": True, "mode": "mock"},
        "timestamp": datetime.utcnow()
    }

if __name__ == "__main__":
    print("Starting Galion Voice API...")
    print("Voice endpoints available at:")
    print("   POST /api/v2/voice/transcribe")
    print("   POST /api/v2/voice/synthesize")
    print("   GET  /api/v2/voice/voices")
    print("   GET  /api/v2/voice/health")
    print("")
    print("Voice infrastructure ready!")
    print("")

    uvicorn.run(app, host="0.0.0.0", port=8020)
