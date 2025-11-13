"""
Text-to-Speech Service
Uses Coqui TTS for speech synthesis.
"""

from typing import Optional, Dict, Any
import tempfile
from pathlib import Path
import os

from ...core.config import settings


class TTSService:
    """
    Text-to-Speech service using Coqui TTS.
    """
    
    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize TTS service.
        
        Args:
            model_name: TTS model name
        """
        self.model_name = model_name or settings.TTS_MODEL
        self.device = settings.TTS_DEVICE
        self.tts = None
        
    def load_model(self):
        """
        Load TTS model.
        Lazy loading to save memory.
        """
        if self.tts is None:
            print(f"Loading TTS model: {self.model_name} on {self.device}")
            
            try:
                from TTS.api import TTS
                self.tts = TTS(model_name=self.model_name, progress_bar=False)
                
                if self.device == "cuda":
                    self.tts.to("cuda")
                
                print("✅ TTS model loaded")
            except ImportError:
                print("❌ TTS not installed. Install with: pip install TTS")
                raise
    
    async def synthesize(
        self,
        text: str,
        voice_id: Optional[str] = None,
        emotion: Optional[str] = None,
        speed: float = 1.0,
        language: str = "en"
    ) -> bytes:
        """
        Synthesize speech from text.
        
        Args:
            text: Text to synthesize
            voice_id: Voice model ID (uses default if None)
            emotion: Emotion/tone (happy, sad, neutral, etc.)
            speed: Speech speed multiplier
            language: Language code
        
        Returns:
            Audio bytes (WAV format)
        """
        # Load model if not loaded
        self.load_model()
        
        # Create temp file for output
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            temp_path = f.name
        
        try:
            # Apply emotion/tone adjustments to text
            if emotion:
                text = self._apply_emotion(text, emotion)
            
            # Synthesize
            self.tts.tts_to_file(
                text=text,
                file_path=temp_path,
                speaker=voice_id,
                language=language,
                speed=speed
            )
            
            # Read audio file
            with open(temp_path, 'rb') as f:
                audio_data = f.read()
            
            return audio_data
        
        finally:
            # Clean up temp file
            Path(temp_path).unlink(missing_ok=True)
    
    def _apply_emotion(self, text: str, emotion: str) -> str:
        """
        Apply emotion to text using prosody markers.
        Different TTS models handle this differently.
        """
        # Emotion mappings (simplified)
        emotion_markers = {
            "happy": "😊 ",
            "excited": "🎉 ",
            "sad": "😢 ",
            "angry": "😠 ",
            "calm": "😌 ",
            "thoughtful": "🤔 ",
            "friendly": "👋 ",
            "professional": ""
        }
        
        marker = emotion_markers.get(emotion.lower(), "")
        return marker + text
    
    async def list_voices(self) -> list[str]:
        """
        Get list of available voices.
        """
        self.load_model()
        
        try:
            # Get speakers from model
            if hasattr(self.tts, 'speakers'):
                return list(self.tts.speakers)
            return ["default"]
        except:
            return ["default"]
    
    async def clone_voice(
        self,
        audio_samples: list[bytes],
        voice_name: str
    ) -> str:
        """
        Clone a voice from audio samples.
        Uses voice conversion or speaker encoder.
        
        Args:
            audio_samples: List of audio bytes
            voice_name: Name for cloned voice
        
        Returns:
            voice_id of cloned voice
        """
        # TODO: Implement voice cloning
        # This requires:
        # 1. Speaker encoder model
        # 2. Fine-tuning on samples
        # 3. Saving voice embeddings
        
        print(f"Voice cloning requested: {voice_name}")
        print(f"Samples: {len(audio_samples)}")
        
        # For now, return a placeholder
        voice_id = f"cloned_{voice_name}_{hash(audio_samples[0]) % 10000}"
        
        return voice_id


# Global TTS service instance
_tts_service = None


def get_tts_service() -> TTSService:
    """Get or create global TTS service."""
    global _tts_service
    if _tts_service is None:
        _tts_service = TTSService()
    return _tts_service

