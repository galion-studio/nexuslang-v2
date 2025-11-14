"""
Backend Text-to-Speech Service
Handles server-side text-to-speech conversion using OpenAI TTS API
"""

import os
import logging
from typing import Optional, Dict, Any
import openai
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class TTSRequest(BaseModel):
    """TTS request model"""
    text: str
    voice: str = "alloy"
    model: str = "tts-1"
    response_format: str = "mp3"
    speed: float = 1.0


class TTSResponse(BaseModel):
    """TTS response model"""
    audio_data: bytes
    content_type: str
    duration_estimate: float
    processing_time: float
    voice: str
    text: str


class BackendTTSService:
    """
    Backend TTS service using OpenAI TTS API
    """

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not found, TTS service will not work")

        # Initialize OpenAI client
        self.client = openai.OpenAI(api_key=self.api_key) if self.api_key else None

        # Voice configurations
        self.voices = {
            "alloy": {"gender": "neutral", "style": "balanced"},
            "echo": {"gender": "male", "style": "warm"},
            "fable": {"gender": "female", "style": "storytelling"},
            "onyx": {"gender": "male", "style": "deep"},
            "nova": {"gender": "female", "style": "young"},
            "shimmer": {"gender": "female", "style": "bright"}
        }

    async def generate_speech(self, request: TTSRequest) -> TTSResponse:
        """
        Generate speech from text using OpenAI TTS API

        Args:
            request: TTS request with text and settings

        Returns:
            TTS response with audio data

        Raises:
            Exception: If speech generation fails
        """
        if not self.client:
            raise Exception("OpenAI API key not configured")

        try:
            import time
            start_time = time.time()

            # Validate voice
            if request.voice not in self.voices:
                raise Exception(f"Unsupported voice: {request.voice}")

            # Validate speed
            if not (0.25 <= request.speed <= 4.0):
                raise Exception("Speed must be between 0.25 and 4.0")

            # Call OpenAI TTS API
            response = self.client.audio.speech.create(
                model=request.model,
                voice=request.voice,
                input=request.text,
                response_format=request.response_format,
                speed=request.speed
            )

            # Get audio data
            audio_data = b""
            for chunk in response.iter_bytes():
                audio_data += chunk

            processing_time = time.time() - start_time

            # Estimate duration (rough calculation)
            words_per_minute = 150  # Average speaking rate
            word_count = len(request.text.split())
            duration_estimate = (word_count / words_per_minute) * 60 / request.speed

            # Determine content type
            content_type_map = {
                "mp3": "audio/mpeg",
                "opus": "audio/opus",
                "aac": "audio/aac",
                "flac": "audio/flac"
            }
            content_type = content_type_map.get(request.response_format, "audio/mpeg")

            tts_response = TTSResponse(
                audio_data=audio_data,
                content_type=content_type,
                duration_estimate=duration_estimate,
                processing_time=processing_time,
                voice=request.voice,
                text=request.text
            )

            logger.info(f"TTS generation completed in {processing_time:.2f}s for text: '{request.text[:50]}...'")
            return tts_response

        except Exception as e:
            logger.error(f"TTS generation failed: {str(e)}")
            raise Exception(f"Text-to-speech generation failed: {str(e)}")

    async def get_available_voices(self) -> Dict[str, Dict[str, Any]]:
        """
        Get list of available voices with metadata

        Returns:
            Dictionary of voice configurations
        """
        return self.voices

    async def estimate_cost(self, text: str, model: str = "tts-1") -> float:
        """
        Estimate cost for TTS generation

        Args:
            text: Text to synthesize
            model: TTS model to use

        Returns:
            Estimated cost in USD
        """
        # OpenAI TTS pricing (per 1K characters)
        pricing = {
            "tts-1": 0.015,
            "tts-1-hd": 0.030
        }

        rate = pricing.get(model, 0.015)
        char_count = len(text)

        # Calculate cost for 1K characters
        cost_per_1k = rate
        total_cost = (char_count / 1000) * cost_per_1k

        return round(total_cost, 6)

    def is_available(self) -> bool:
        """
        Check if TTS service is available

        Returns:
            True if service is configured and ready
        """
        return self.client is not None


# Global instance
tts_service = BackendTTSService()