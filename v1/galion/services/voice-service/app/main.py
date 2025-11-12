"""
Main application entry point for Voice Service
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.api.v1 import voice, stt, tts
from prometheus_client import make_asgi_app

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info(f"🎙️ Starting {settings.SERVICE_NAME} v{settings.SERVICE_VERSION}")
    logger.info(f"📡 Whisper API: {'configured' if settings.OPENAI_API_KEY else 'missing'}")
    logger.info(f"🔊 ElevenLabs API: {'configured' if settings.ELEVENLABS_API_KEY else 'missing'}")
    logger.info(f"🧠 OpenRouter API: {'configured' if settings.OPENROUTER_API_KEY else 'missing'}")
    yield
    logger.info(f"👋 Shutting down {settings.SERVICE_NAME}")


# Create FastAPI app
app = FastAPI(
    title="Nexus Core Voice Service",
    description="Voice interface with STT, TTS, and intelligent intent routing",
    version=settings.SERVICE_VERSION,
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(voice.router, prefix="/api/v1/voice", tags=["voice"])
app.include_router(stt.router, prefix="/api/v1/voice", tags=["stt"])
app.include_router(tts.router, prefix="/api/v1/voice", tags=["tts"])

# Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION,
        "features": {
            "stt": bool(settings.OPENAI_API_KEY),
            "tts": bool(settings.ELEVENLABS_API_KEY),
            "intent": bool(settings.OPENROUTER_API_KEY)
        }
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "🎙️ Nexus Core Voice Service",
        "version": settings.SERVICE_VERSION,
        "tagline": "Talk to Nexus like you talk to JARVIS",
        "endpoints": {
            "voice_stream": "ws://localhost:8003/api/v1/voice/stream",
            "stt": "POST /api/v1/voice/stt",
            "tts": "POST /api/v1/voice/tts",
            "health": "GET /health",
            "metrics": "GET /metrics",
            "docs": "GET /docs"
        },
        "quick_start": "Hold space bar and say 'show my profile'"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )

