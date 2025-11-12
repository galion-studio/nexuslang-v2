"""
Text-to-Speech service using ElevenLabs
"""

from elevenlabs import generate, Voice, VoiceSettings
from typing import Optional, AsyncGenerator
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class TTSService:
    """Text-to-Speech service using ElevenLabs"""
    
    def __init__(self):
        self.api_key = settings.ELEVENLABS_API_KEY
        self.voice_id = settings.ELEVENLABS_VOICE_ID
        self.model = settings.ELEVENLABS_MODEL
    
    async def synthesize(
        self,
        text: str,
        voice_id: Optional[str] = None,
        speed: float = 1.0,
        stability: float = 0.5,
        similarity_boost: float = 0.75,
        stream: bool = False
    ) -> bytes:
        """
        Convert text to speech using ElevenLabs
        
        Args:
            text: Text to convert to speech
            voice_id: ElevenLabs voice ID (uses default if None)
            speed: Speaking rate (0.5 - 2.0)
            stability: Voice stability (0.0 - 1.0)
            similarity_boost: Voice similarity (0.0 - 1.0)
            stream: Stream audio chunks if True
        
        Returns:
            bytes: Audio data (MP3 format)
        """
        try:
            voice_id = voice_id or self.voice_id
            
            logger.info(f"🔊 Generating TTS for text: '{text[:100]}{'...' if len(text) > 100 else ''}'")
            
            # Generate audio
            audio = generate(
                text=text,
                voice=Voice(
                    voice_id=voice_id,
                    settings=VoiceSettings(
                        stability=stability,
                        similarity_boost=similarity_boost
                    )
                ),
                model=self.model,
                api_key=self.api_key,
                stream=False  # We'll handle streaming separately
            )
            
            logger.info(f"✅ TTS generation successful, audio size: {len(audio)} bytes")
            return audio
                
        except Exception as e:
            logger.error(f"❌ TTS error: {e}")
            # Fallback: return error message
            raise
    
    def get_available_voices(self) -> list:
        """Get list of available voices"""
        # Predefined voices (could be fetched from ElevenLabs API)
        return [
            {
                "id": "21m00Tcm4TlvDq8ikWAM",
                "name": "Rachel",
                "category": "professional",
                "description": "Clear, professional female voice"
            },
            {
                "id": "MF3mGyEYCl7XYWbV9V6O",
                "name": "Adam",
                "category": "casual",
                "description": "Warm, conversational male voice"
            },
            {
                "id": "ErXwobaYiN019PkySvjV",
                "name": "Antoni",
                "category": "technical",
                "description": "Clear, precise male voice"
            }
        ]


# Singleton instance
tts_service = TTSService()

