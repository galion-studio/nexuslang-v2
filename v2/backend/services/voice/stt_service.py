"""
Backend Speech-to-Text Service
Handles server-side speech recognition using Whisper API
"""

import os
import logging
from typing import Optional, Dict, Any
import openai
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class STTRequest(BaseModel):
    """STT request model"""
    audio_data: bytes
    language: str = "en"
    model: str = "whisper-1"
    response_format: str = "json"
    temperature: float = 0.0


class STTResponse(BaseModel):
    """STT response model"""
    text: str
    language: str
    confidence: float = 0.9
    processing_time: float
    model: str


class BackendSTTService:
    """
    Backend STT service using OpenAI Whisper API
    """

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not found, STT service will not work")

        # Initialize OpenAI client
        self.client = openai.OpenAI(api_key=self.api_key) if self.api_key else None

    async def transcribe_audio(self, request: STTRequest) -> STTResponse:
        """
        Transcribe audio data using Whisper API

        Args:
            request: STT request with audio data

        Returns:
            STT response with transcription

        Raises:
            Exception: If transcription fails
        """
        if not self.client:
            raise Exception("OpenAI API key not configured")

        try:
            import time
            start_time = time.time()

            # Save audio data to temporary file
            import tempfile
            import base64

            # If audio_data is base64 encoded, decode it
            if isinstance(request.audio_data, str):
                audio_data = base64.b64decode(request.audio_data)
            else:
                audio_data = request.audio_data

            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name

            try:
                # Call Whisper API
                with open(temp_file_path, "rb") as audio_file:
                    transcription = self.client.audio.transcriptions.create(
                        file=audio_file,
                        model=request.model,
                        language=request.language,
                        response_format=request.response_format,
                        temperature=request.temperature
                    )

                processing_time = time.time() - start_time

                # Extract text from response
                if isinstance(transcription, dict):
                    text = transcription.get("text", "")
                else:
                    text = str(transcription)

                # Clean up text
                text = text.strip()

                response = STTResponse(
                    text=text,
                    language=request.language,
                    confidence=0.9,  # Whisper doesn't provide confidence
                    processing_time=processing_time,
                    model=request.model
                )

                logger.info(f"STT transcription completed in {processing_time:.2f}s")
                return response

            finally:
                # Clean up temporary file
                import os
                try:
                    os.unlink(temp_file_path)
                except:
                    pass

        except Exception as e:
            logger.error(f"STT transcription failed: {str(e)}")
            raise Exception(f"Speech recognition failed: {str(e)}")

    async def get_supported_languages(self) -> list[str]:
        """
        Get list of supported languages

        Returns:
            List of language codes
        """
        # Whisper supports these languages
        return [
            "en", "zh", "de", "es", "ru", "ko", "fr", "ja", "pt", "tr",
            "pl", "ca", "nl", "ar", "sv", "it", "id", "hi", "fi", "vi",
            "he", "uk", "el", "ms", "cs", "ro", "da", "hu", "ta", "no",
            "th", "ur", "hr", "bg", "lt", "la", "mi", "ml", "cy", "sk",
            "te", "fa", "lv", "bn", "sr", "az", "sl", "kn", "et", "mk",
            "br", "eu", "is", "hy", "ne", "mn", "bs", "kk", "sq", "sw",
            "gl", "mr", "pa", "si", "km", "sn", "yo", "so", "af", "oc",
            "ka", "be", "tg", "sd", "gu", "am", "yi", "lo", "uz", "fo",
            "ht", "ps", "tk", "nn", "mt", "sa", "lb", "my", "bo", "tl",
            "mg", "as", "tt", "haw", "ln", "ha", "ba", "jw", "su"
        ]

    def is_available(self) -> bool:
        """
        Check if STT service is available

        Returns:
            True if service is configured and ready
        """
        return self.client is not None


# Global instance
stt_service = BackendSTTService()