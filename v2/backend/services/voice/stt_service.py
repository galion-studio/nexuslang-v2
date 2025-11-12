"""
Speech-to-Text Service
Uses OpenAI Whisper for speech recognition.
"""

import whisper
import tempfile
from typing import Dict, Any, Optional
from pathlib import Path

from ...core.config import settings


class STTService:
    """
    Speech-to-Text service using Whisper.
    """
    
    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize STT service.
        
        Args:
            model_name: Whisper model name (tiny, base, small, medium, large)
        """
        self.model_name = model_name or settings.WHISPER_MODEL
        self.device = settings.WHISPER_DEVICE
        self.model = None
        
    def load_model(self):
        """
        Load Whisper model.
        Lazy loading to save memory.
        """
        if self.model is None:
            print(f"Loading Whisper model: {self.model_name} on {self.device}")
            self.model = whisper.load_model(self.model_name, device=self.device)
            print("✅ Whisper model loaded")
    
    async def transcribe(
        self,
        audio_data: bytes,
        language: Optional[str] = None,
        task: str = "transcribe"
    ) -> Dict[str, Any]:
        """
        Transcribe audio to text.
        
        Args:
            audio_data: Audio bytes (WAV, MP3, etc.)
            language: Language code (auto-detect if None)
            task: 'transcribe' or 'translate' (translate to English)
        
        Returns:
            Dict with 'text', 'language', 'confidence', 'segments'
        """
        # Load model if not loaded
        self.load_model()
        
        # Save audio to temp file (Whisper requires file path)
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            f.write(audio_data)
            temp_path = f.name
        
        try:
            # Transcribe
            result = self.model.transcribe(
                temp_path,
                language=language,
                task=task,
                fp16=False  # Disable for CPU
            )
            
            # Calculate average confidence
            segments = result.get("segments", [])
            avg_confidence = sum(s.get("no_speech_prob", 0) for s in segments) / len(segments) if segments else 0.0
            
            return {
                "text": result["text"],
                "language": result.get("language", "unknown"),
                "confidence": 1.0 - avg_confidence,  # Convert no_speech_prob to confidence
                "segments": [
                    {
                        "start": s["start"],
                        "end": s["end"],
                        "text": s["text"]
                    }
                    for s in segments
                ]
            }
        
        finally:
            # Clean up temp file
            Path(temp_path).unlink(missing_ok=True)
    
    async def detect_language(self, audio_data: bytes) -> str:
        """
        Detect language from audio.
        """
        self.load_model()
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            f.write(audio_data)
            temp_path = f.name
        
        try:
            # Load audio and detect language
            audio = whisper.load_audio(temp_path)
            audio = whisper.pad_or_trim(audio)
            
            # Make log-Mel spectrogram
            mel = whisper.log_mel_spectrogram(audio).to(self.model.device)
            
            # Detect language
            _, probs = self.model.detect_language(mel)
            detected_lang = max(probs, key=probs.get)
            
            return detected_lang
        
        finally:
            Path(temp_path).unlink(missing_ok=True)


# Global STT service instance
_stt_service = None


def get_stt_service() -> STTService:
    """Get or create global STT service."""
    global _stt_service
    if _stt_service is None:
        _stt_service = STTService()
    return _stt_service

