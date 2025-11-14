"""
Voice Activity Detection (VAD) Service
Detects presence of speech in audio streams using Silero VAD
"""

import torch
import numpy as np
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class VADDetector:
    """
    Voice Activity Detection using Silero VAD model.

    Detects speech segments in audio streams with high accuracy.
    """

    def __init__(self, threshold: float = 0.5, sampling_rate: int = 16000):
        """
        Initialize VAD detector.

        Args:
            threshold: Speech probability threshold (0.0-1.0)
            sampling_rate: Audio sampling rate (Hz)
        """
        self.threshold = threshold
        self.sampling_rate = sampling_rate
        self.model = None
        self.device = "cpu"  # Use CPU for RunPod

        # Load model on first use (lazy loading)
        self._load_model()

    def _load_model(self):
        """Load Silero VAD model"""
        if self.model is not None:
            return

        try:
            logger.info("Loading Silero VAD model...")

            # Import torch and torchaudio
            import torch
            import torchaudio

            # Load Silero VAD model
            self.model, utils = torch.hub.load(
                repo_or_dir='snakers4/silero-vad',
                model='silero_vad',
                force_reload=False,
                trust_repo=True
            )

            # Move to device
            self.model.to(self.device)
            self.model.eval()

            # Get utility functions
            self.get_speech_timestamps = utils[0]

            logger.info("✅ Silero VAD model loaded")

        except ImportError as e:
            logger.warning(f"Silero VAD not available: {e}")
            logger.warning("Falling back to simple energy-based VAD")
            self.model = None
        except Exception as e:
            logger.error(f"Failed to load VAD model: {e}")
            self.model = None

    async def detect(self, audio_data: bytes) -> bool:
        """
        Detect if audio contains speech.

        Args:
            audio_data: Raw audio bytes (16-bit PCM, mono)

        Returns:
            True if speech detected, False otherwise
        """
        try:
            if self.model is None:
                # Fallback: simple energy-based detection
                return self._simple_vad_detection(audio_data)

            # Convert bytes to numpy array
            audio_array = self._bytes_to_array(audio_data)

            if len(audio_array) == 0:
                return False

            # Run VAD inference
            with torch.no_grad():
                # Convert to tensor
                audio_tensor = torch.from_numpy(audio_array).float().to(self.device)

                # Get speech probability
                speech_prob = self.model(audio_tensor, self.sampling_rate).item()

                # Check against threshold
                is_speech = speech_prob >= self.threshold

                logger.debug(".3f")
                return is_speech

        except Exception as e:
            logger.error(f"VAD detection failed: {e}")
            # Fallback to simple detection
            return self._simple_vad_detection(audio_data)

    def _bytes_to_array(self, audio_data: bytes) -> np.ndarray:
        """Convert audio bytes to numpy array"""
        try:
            # Assume 16-bit PCM, mono
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            # Normalize to [-1, 1]
            audio_array = audio_array.astype(np.float32) / 32768.0
            return audio_array
        except Exception as e:
            logger.error(f"Audio conversion failed: {e}")
            return np.array([])

    def _simple_vad_detection(self, audio_data: bytes) -> bool:
        """
        Simple energy-based voice activity detection.
        Fallback when Silero VAD is not available.
        """
        try:
            if len(audio_data) < 100:  # Too short
                return False

            # Convert to numpy array
            audio_array = self._bytes_to_array(audio_data)

            if len(audio_array) == 0:
                return False

            # Calculate RMS energy
            rms = np.sqrt(np.mean(audio_array ** 2))

            # Simple threshold (tune based on audio levels)
            energy_threshold = 0.01  # Adjust as needed

            is_speech = rms > energy_threshold

            logger.debug(".4f")
            return is_speech

        except Exception as e:
            logger.error(f"Simple VAD failed: {e}")
            return False

    async def get_speech_segments(self, audio_data: bytes) -> list:
        """
        Get detailed speech segments from audio.

        Returns:
            List of speech segments with start/end times
        """
        try:
            if self.model is None:
                return []

            audio_array = self._bytes_to_array(audio_data)
            if len(audio_array) == 0:
                return []

            audio_tensor = torch.from_numpy(audio_array).float().to(self.device)

            # Get speech timestamps
            speech_timestamps = self.get_speech_timestamps(
                audio_tensor,
                self.model,
                sampling_rate=self.sampling_rate,
                threshold=self.threshold
            )

            # Convert to list of dicts
            segments = []
            for ts in speech_timestamps:
                segments.append({
                    "start": ts["start"] / self.sampling_rate,  # Convert to seconds
                    "end": ts["end"] / self.sampling_rate
                })

            return segments

        except Exception as e:
            logger.error(f"Speech segment detection failed: {e}")
            return []

    def update_threshold(self, new_threshold: float):
        """Update VAD detection threshold"""
        self.threshold = max(0.0, min(1.0, new_threshold))
        logger.info(f"VAD threshold updated to: {self.threshold}")

    def get_stats(self) -> dict:
        """Get VAD detector statistics"""
        return {
            "model_loaded": self.model is not None,
            "threshold": self.threshold,
            "sampling_rate": self.sampling_rate,
            "device": self.device
        }

# Global VAD detector instance
_vad_detector = None

def get_vad_detector(threshold: float = 0.5) -> VADDetector:
    """Get or create global VAD detector instance"""
    global _vad_detector
    if _vad_detector is None:
        _vad_detector = VADDetector(threshold=threshold)
    return _vad_detector

