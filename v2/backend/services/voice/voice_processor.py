"""
Voice Processor Service
Handles real-time voice processing pipeline: VAD -> STT -> AI -> TTS -> Audio Stream
"""

import asyncio
from typing import Dict, Any, Optional, List, Callable
import numpy as np
import io
import base64
from datetime import datetime
import logging

from .stt_service import get_stt_service
from .tts_service import get_tts_service
from .vad_detector import get_vad_detector

logger = logging.getLogger(__name__)

class VoiceProcessor:
    """
    Real-time voice processing pipeline for Galion Platform.

    Pipeline:
    1. Audio Input (WebSocket/WebRTC)
    2. Voice Activity Detection (VAD)
    3. Speech-to-Text (STT)
    4. AI Processing
    5. Text-to-Speech (TTS)
    6. Audio Output Streaming
    """

    def __init__(self):
        self.stt_service = get_stt_service()
        self.tts_service = get_tts_service()
        self.vad_detector = get_vad_detector()

        # Processing state
        self.is_processing = False
        self.audio_buffer = []
        self.silence_threshold = 0.5  # seconds
        self.max_buffer_size = 30  # seconds

        # Callbacks
        self.on_transcription: Optional[Callable] = None
        self.on_response: Optional[Callable] = None
        self.on_error: Optional[Callable] = None

    async def start_processing(self):
        """Start the voice processing pipeline"""
        self.is_processing = True
        logger.info("Voice processor started")

    async def stop_processing(self):
        """Stop the voice processing pipeline"""
        self.is_processing = False
        self.audio_buffer.clear()
        logger.info("Voice processor stopped")

    async def process_audio_chunk(self, audio_data: bytes) -> Optional[Dict[str, Any]]:
        """
        Process a chunk of audio data through the pipeline.

        Args:
            audio_data: Raw audio bytes (typically 100-200ms chunks)

        Returns:
            Dict with processing results if speech detected, None otherwise
        """
        if not self.is_processing:
            return None

        try:
            # Add to buffer
            self.audio_buffer.append(audio_data)

            # Limit buffer size (circular buffer)
            buffer_duration = self._calculate_buffer_duration()
            if buffer_duration > self.max_buffer_size:
                # Remove oldest chunks
                while self._calculate_buffer_duration() > self.max_buffer_size:
                    self.audio_buffer.pop(0)

            # Check for voice activity
            is_speech = await self._detect_voice_activity(audio_data)
            if not is_speech:
                return None

            # Process buffered audio
            combined_audio = self._combine_audio_chunks()
            if not combined_audio:
                return None

            # Speech-to-Text
            transcription = await self.stt_service.transcribe(combined_audio)
            user_text = transcription.get("text", "").strip()

            if not user_text:
                return None

            # Callback for transcription
            if self.on_transcription:
                await self.on_transcription(user_text)

            # AI Processing (placeholder - integrate with agent system)
            ai_response = await self._process_with_ai(user_text)

            # Text-to-Speech
            audio_response = await self.tts_service.synthesize(
                text=ai_response,
                voice_id="default",
                emotion="friendly"
            )

            # Clear buffer after processing
            self.audio_buffer.clear()

            # Callback for response
            if self.on_response:
                await self.on_response(ai_response, audio_response)

            return {
                "user_text": user_text,
                "ai_response": ai_response,
                "audio_response": audio_response,
                "audio_base64": base64.b64encode(audio_response).decode('utf-8'),
                "confidence": transcription.get("confidence", 0.0),
                "language": transcription.get("language", "en"),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Voice processing error: {e}")
            if self.on_error:
                await self.on_error(str(e))
            return None

    async def _detect_voice_activity(self, audio_data: bytes) -> bool:
        """Detect if audio chunk contains speech"""
        try:
            return await self.vad_detector.detect(audio_data)
        except Exception as e:
            logger.warning(f"VAD detection failed: {e}")
            # Fallback: assume speech if audio data present
            return len(audio_data) > 1000

    def _combine_audio_chunks(self) -> bytes:
        """Combine buffered audio chunks into single audio stream"""
        if not self.audio_buffer:
            return b""

        # Simple concatenation (assuming same format)
        # In production, would need proper audio format handling
        return b"".join(self.audio_buffer)

    def _calculate_buffer_duration(self) -> float:
        """Calculate approximate duration of buffered audio"""
        # Rough estimation: assume 16kHz 16-bit mono
        # 16kHz * 16-bit * 1-channel = 32KB/second
        total_bytes = sum(len(chunk) for chunk in self.audio_buffer)
        return total_bytes / (16000 * 2)  # 16kHz * 16-bit

    async def _process_with_ai(self, user_text: str) -> str:
        """
        Process user text with AI (placeholder for agent integration)

        In production, this would route to the appropriate agent.
        """
        try:
            # Placeholder AI processing
            # TODO: Integrate with agent orchestrator

            # Simple echo response for now
            if "hello" in user_text.lower():
                return "Hello! How can I help you today?"
            elif "help" in user_text.lower():
                return "I'm here to assist you. What would you like to know?"
            else:
                return f"I heard you say: {user_text}. How can I help you with that?"

        except Exception as e:
            logger.error(f"AI processing failed: {e}")
            return "I'm sorry, I encountered an error processing your request. Please try again."

    async def get_processing_stats(self) -> Dict[str, Any]:
        """Get voice processing statistics"""
        return {
            "is_processing": self.is_processing,
            "buffer_size": len(self.audio_buffer),
            "buffer_duration": self._calculate_buffer_duration(),
            "max_buffer_size": self.max_buffer_size,
            "silence_threshold": self.silence_threshold
        }

class VoiceSessionManager:
    """
    Manages multiple voice processing sessions for concurrent users
    """

    def __init__(self):
        self.sessions: Dict[str, VoiceProcessor] = {}
        self.session_timeout = 3600  # 1 hour

    def create_session(self, session_id: str) -> VoiceProcessor:
        """Create new voice processing session"""
        processor = VoiceProcessor()
        self.sessions[session_id] = processor
        logger.info(f"Created voice session: {session_id}")
        return processor

    def get_session(self, session_id: str) -> Optional[VoiceProcessor]:
        """Get existing voice processing session"""
        return self.sessions.get(session_id)

    def end_session(self, session_id: str):
        """End voice processing session"""
        if session_id in self.sessions:
            processor = self.sessions[session_id]
            asyncio.create_task(processor.stop_processing())
            del self.sessions[session_id]
            logger.info(f"Ended voice session: {session_id}")

    async def cleanup_expired_sessions(self):
        """Clean up expired sessions (run periodically)"""
        # In production, would track session creation times
        # For now, just log active sessions
        logger.info(f"Active voice sessions: {len(self.sessions)}")

    def get_session_stats(self) -> Dict[str, Any]:
        """Get statistics for all sessions"""
        return {
            "total_sessions": len(self.sessions),
            "active_sessions": sum(1 for s in self.sessions.values() if s.is_processing),
            "session_ids": list(self.sessions.keys())
        }

# Global instances
_voice_session_manager = None

def get_voice_session_manager() -> VoiceSessionManager:
    """Get global voice session manager"""
    global _voice_session_manager
    if _voice_session_manager is None:
        _voice_session_manager = VoiceSessionManager()
    return _voice_session_manager

def get_voice_processor(session_id: str) -> VoiceProcessor:
    """Get or create voice processor for session"""
    manager = get_voice_session_manager()
    processor = manager.get_session(session_id)
    if processor is None:
        processor = manager.create_session(session_id)
    return processor

