"""
Speech-to-Text service using OpenAI Whisper
"""

import openai
from typing import Optional
import io
import logging
from pydub import AudioSegment

from app.config import settings

logger = logging.getLogger(__name__)


class STTService:
    """Speech-to-Text service using OpenAI Whisper"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_WHISPER_MODEL
    
    async def transcribe(
        self,
        audio_data: bytes,
        language: Optional[str] = None,
        format: str = "webm"
    ) -> dict:
        """
        Transcribe audio to text using Whisper
        
        Args:
            audio_data: Raw audio bytes
            language: ISO-639-1 language code (e.g., 'en', 'es')
            format: Audio format (webm, wav, mp3, etc.)
        
        Returns:
            dict: {
                "text": "transcribed text",
                "language": "en",
                "confidence": 0.95,
                "duration": 2.3
            }
        """
        try:
            # Convert audio to appropriate format if needed
            if format != "wav":
                audio_data = self._convert_to_wav(audio_data, format)
            
            # Get audio duration
            audio = AudioSegment.from_file(io.BytesIO(audio_data), format="wav")
            duration = len(audio) / 1000.0  # Convert to seconds
            
            # Create file-like object
            audio_file = io.BytesIO(audio_data)
            audio_file.name = "audio.wav"
            
            # Transcribe using Whisper
            logger.info(f"🎤 Transcribing {duration:.1f}s audio with Whisper (language: {language or 'auto'})")
            
            transcription = self.client.audio.transcriptions.create(
                model=self.model,
                file=audio_file,
                language=language,
                response_format="verbose_json"
            )
            
            result = {
                "text": transcription.text,
                "language": transcription.language,
                "confidence": self._calculate_confidence(transcription),
                "duration": duration
            }
            
            logger.info(f"✅ Transcription successful: '{result['text'][:100]}{'...' if len(result['text']) > 100 else ''}'")
            return result
            
        except Exception as e:
            logger.error(f"❌ STT error: {e}")
            raise
    
    def _convert_to_wav(self, audio_data: bytes, from_format: str) -> bytes:
        """Convert audio to WAV format"""
        try:
            logger.debug(f"🔄 Converting audio from {from_format} to WAV")
            audio = AudioSegment.from_file(io.BytesIO(audio_data), format=from_format)
            
            # Convert to mono, 16kHz (optimal for Whisper)
            audio = audio.set_channels(settings.AUDIO_CHANNELS)
            audio = audio.set_frame_rate(settings.AUDIO_SAMPLE_RATE)
            
            # Export as WAV
            buffer = io.BytesIO()
            audio.export(buffer, format="wav")
            return buffer.getvalue()
        except Exception as e:
            logger.error(f"❌ Audio conversion error: {e}")
            raise
    
    def _calculate_confidence(self, transcription) -> float:
        """Calculate confidence score from Whisper response"""
        # Whisper doesn't provide confidence directly
        # Use heuristics: word count, no hallucination markers
        text = transcription.text
        
        if not text or text.strip() == "":
            return 0.0
        
        # Start with high confidence (Whisper is very accurate)
        confidence = 0.95
        
        # Reduce confidence for very short responses
        word_count = len(text.split())
        if word_count < 3:
            confidence -= 0.1
        
        # Reduce for common hallucination patterns
        hallucination_markers = [
            "thank you for watching",
            "subscribe",
            "[music]",
            "[applause]",
            "don't forget to like"
        ]
        for marker in hallucination_markers:
            if marker.lower() in text.lower():
                confidence -= 0.3
                break
        
        return max(0.0, min(1.0, confidence))


# Singleton instance
stt_service = STTService()

