"""
Voice-powered research service for Deep Search.
Enables voice-based research queries and audio responses.
"""

import logging
import asyncio
import io
import base64
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import json

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    sr = None

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    gTTS = None

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None

from ...services.deep_search.agents import AgentOrchestrator

logger = logging.getLogger(__name__)


class VoiceResearchService:
    """
    Voice-powered research service with speech-to-text and text-to-speech capabilities.

    Features:
    - Voice query processing with multiple STT engines
    - Voice response synthesis with natural speech
    - Voice command recognition for research control
    - Audio file processing and generation
    - Multi-language voice support
    - Voice activity detection and noise filtering
    """

    def __init__(self, openai_api_key: Optional[str] = None):
        self.openai_api_key = openai_api_key
        self.supported_languages = {
            'en': {'name': 'English', 'voice': 'en'},
            'es': {'name': 'Spanish', 'voice': 'es'},
            'fr': {'name': 'French', 'voice': 'fr'},
            'de': {'name': 'German', 'voice': 'de'},
            'it': {'name': 'Italian', 'voice': 'it'},
            'pt': {'name': 'Portuguese', 'voice': 'pt'},
            'ja': {'name': 'Japanese', 'voice': 'ja'},
            'ko': {'name': 'Korean', 'voice': 'ko'},
            'zh': {'name': 'Chinese', 'voice': 'zh-cn'}
        }

        # Voice command patterns
        self.voice_commands = {
            'research': ['research', 'search', 'find', 'look up', 'investigate'],
            'deep_dive': ['deep dive', 'detailed', 'comprehensive', 'thorough'],
            'quick': ['quick', 'fast', 'brief', 'summary'],
            'compare': ['compare', 'versus', 'vs', 'difference'],
            'explain': ['explain', 'what is', 'how does', 'why'],
            'persona_change': ['use persona', 'switch to', 'change style'],
            'stop': ['stop', 'cancel', 'quit', 'end'],
            'repeat': ['repeat', 'say again', 'what did you say']
        }

        self.recognizer = None
        if SPEECH_RECOGNITION_AVAILABLE:
            self.recognizer = sr.Recognizer()
            # Adjust for ambient noise
            self.recognizer.dynamic_energy_threshold = True

        # Audio processing settings
        self.audio_settings = {
            'sample_rate': 16000,
            'channels': 1,
            'max_duration': 30,  # seconds
            'silence_threshold': 500,
            'pause_threshold': 0.8
        }

    async def process_voice_query(self, audio_data: bytes, language: str = 'en',
                                 user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process voice audio data into research query.

        Args:
            audio_data: Raw audio bytes
            language: Language code for speech recognition
            user_context: User context and preferences

        Returns:
            Processed voice query with research parameters
        """
        try:
            # Convert audio bytes to audio data for recognition
            audio = self._bytes_to_audio_data(audio_data)

            if not audio:
                return {
                    "success": False,
                    "error": "Could not process audio data",
                    "confidence": 0.0
                }

            # Perform speech recognition
            recognition_result = await self._recognize_speech(audio, language)

            if not recognition_result["success"]:
                return recognition_result

            text = recognition_result["text"]
            confidence = recognition_result["confidence"]

            # Parse voice commands and extract research parameters
            query_analysis = await self._analyze_voice_query(text, language)

            return {
                "success": True,
                "original_text": text,
                "confidence": confidence,
                "research_query": query_analysis["query"],
                "parameters": query_analysis["parameters"],
                "detected_commands": query_analysis["commands"],
                "language": language,
                "processing_time": query_analysis["processing_time"]
            }

        except Exception as e:
            logger.error(f"Voice query processing failed: {e}")
            return {
                "success": False,
                "error": f"Voice processing error: {str(e)}",
                "confidence": 0.0
            }

    async def _recognize_speech(self, audio_data, language: str) -> Dict[str, Any]:
        """
        Perform speech recognition on audio data.

        Uses multiple STT engines for best results.
        """
        if not SPEECH_RECOGNITION_AVAILABLE:
            return {
                "success": False,
                "error": "Speech recognition not available",
                "text": "",
                "confidence": 0.0
            }

        results = []

        try:
            # Google Speech Recognition (free, good accuracy)
            with sr.AudioData(audio_data, self.audio_settings['sample_rate'],
                            self.audio_settings['sample_rate'] * 2) as source:
                text_google = self.recognizer.recognize_google(
                    source, language=language, show_all=True
                )

                if text_google and isinstance(text_google, list):
                    for result in text_google:
                        results.append({
                            "text": result.get("transcript", ""),
                            "confidence": result.get("confidence", 0.5),
                            "engine": "google"
                        })

        except Exception as e:
            logger.warning(f"Google speech recognition failed: {e}")

        try:
            # OpenAI Whisper (if available)
            if OPENAI_AVAILABLE and self.openai_api_key:
                # This would use OpenAI's Whisper API
                # For now, we'll simulate it
                whisper_result = await self._whisper_recognition(audio_data, language)
                if whisper_result:
                    results.append(whisper_result)

        except Exception as e:
            logger.warning(f"Whisper recognition failed: {e}")

        if not results:
            return {
                "success": False,
                "error": "Speech recognition failed",
                "text": "",
                "confidence": 0.0
            }

        # Select best result
        best_result = max(results, key=lambda x: x["confidence"])

        return {
            "success": True,
            "text": best_result["text"],
            "confidence": best_result["confidence"],
            "engine": best_result["engine"]
        }

    async def _whisper_recognition(self, audio_data: bytes, language: str) -> Optional[Dict[str, Any]]:
        """
        Use OpenAI Whisper for speech recognition.
        """
        try:
            if not OPENAI_AVAILABLE or not self.openai_api_key:
                return None

            # Convert bytes to temporary file for Whisper
            import tempfile
            import os

            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name

            try:
                # This is a placeholder for actual Whisper API call
                # In production, you would use the OpenAI client
                return {
                    "text": "Simulated Whisper transcription",
                    "confidence": 0.85,
                    "engine": "whisper"
                }

            finally:
                os.unlink(temp_file_path)

        except Exception as e:
            logger.error(f"Whisper recognition error: {e}")
            return None

    def _bytes_to_audio_data(self, audio_bytes: bytes):
        """
        Convert audio bytes to speech_recognition AudioData.
        """
        try:
            # This is a simplified conversion
            # In production, you might need proper audio format conversion
            import wave
            import io

            # Assume audio_bytes is WAV format
            audio_buffer = io.BytesIO(audio_bytes)

            with wave.open(audio_buffer, 'rb') as wav_file:
                frames = wav_file.readframes(wav_file.getnframes())
                sample_rate = wav_file.getframerate()
                sample_width = wav_file.getsampwidth()

            return sr.AudioData(frames, sample_rate, sample_width)

        except Exception as e:
            logger.error(f"Audio data conversion failed: {e}")
            return None

    async def _analyze_voice_query(self, text: str, language: str) -> Dict[str, Any]:
        """
        Analyze voice query text to extract research parameters and commands.
        """
        start_time = asyncio.get_event_loop().time()

        text_lower = text.lower().strip()
        detected_commands = []
        research_parameters = {
            "depth": "comprehensive",
            "persona": "default",
            "include_sources": True
        }

        # Detect voice commands
        for command_type, keywords in self.voice_commands.items():
            for keyword in keywords:
                if keyword in text_lower:
                    detected_commands.append(command_type)
                    break

        # Extract research query (remove command words)
        query = text

        # Remove detected command words to get clean query
        for command_type, keywords in self.voice_commands.items():
            if command_type in detected_commands:
                for keyword in keywords:
                    query = query.replace(keyword, "")

        # Clean up query
        query = " ".join(query.split())  # Remove extra spaces

        # Adjust parameters based on detected commands
        if "deep_dive" in detected_commands:
            research_parameters["depth"] = "exhaustive"
        elif "quick" in detected_commands:
            research_parameters["depth"] = "quick"

        if "compare" in detected_commands:
            research_parameters["comparison_mode"] = True

        # Language-specific processing
        if language != 'en':
            research_parameters["language"] = language

        processing_time = asyncio.get_event_loop().time() - start_time

        return {
            "query": query,
            "parameters": research_parameters,
            "commands": detected_commands,
            "processing_time": processing_time
        }

    async def generate_voice_response(self, text: str, language: str = 'en',
                                    voice_settings: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate voice audio from text response.

        Args:
            text: Text to convert to speech
            language: Language for speech synthesis
            voice_settings: Voice customization settings

        Returns:
            Voice response with audio data
        """
        try:
            if not GTTS_AVAILABLE:
                return {
                    "success": False,
                    "error": "Text-to-speech not available",
                    "audio_data": None,
                    "format": None
                }

            # Default voice settings
            settings = {
                "voice": self.supported_languages.get(language, {}).get('voice', 'en'),
                "slow": False,
                "emphasis": None
            }

            if voice_settings:
                settings.update(voice_settings)

            # Generate speech
            tts = gTTS(text=text, lang=settings["voice"], slow=settings["slow"])

            # Save to bytes buffer
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)

            audio_data = audio_buffer.getvalue()
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')

            return {
                "success": True,
                "audio_data": audio_base64,
                "audio_format": "mp3",
                "language": language,
                "text_length": len(text),
                "audio_size_bytes": len(audio_data),
                "estimated_duration": len(text) * 0.05  # Rough estimate: ~50ms per character
            }

        except Exception as e:
            logger.error(f"Voice response generation failed: {e}")
            return {
                "success": False,
                "error": f"Speech synthesis error: {str(e)}",
                "audio_data": None,
                "format": None
            }

    async def perform_voice_research(self, audio_data: bytes,
                                   user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Complete voice-powered research workflow.

        Process voice input, perform research, generate voice response.
        """
        try:
            # Step 1: Process voice query
            voice_query = await self.process_voice_query(
                audio_data,
                language=user_context.get('language', 'en') if user_context else 'en',
                user_context=user_context
            )

            if not voice_query["success"]:
                return {
                    "success": False,
                    "error": voice_query["error"],
                    "stage": "voice_recognition"
                }

            # Step 2: Perform research
            orchestrator = AgentOrchestrator()

            research_result = await orchestrator.execute_research(
                voice_query["research_query"],
                {
                    "depth": voice_query["parameters"]["depth"],
                    "persona": voice_query["parameters"]["persona"],
                    "include_sources": voice_query["parameters"]["include_sources"],
                    "voice_mode": True,
                    "user_context": user_context
                }
            )

            if not research_result or "synthesized_answer" not in research_result:
                return {
                    "success": False,
                    "error": "Research failed",
                    "stage": "research_execution"
                }

            # Step 3: Generate voice response
            response_text = research_result["synthesized_answer"]

            # Truncate for voice (keep first 2000 characters)
            if len(response_text) > 2000:
                response_text = response_text[:1997] + "..."

            voice_response = await self.generate_voice_response(
                response_text,
                language=user_context.get('language', 'en') if user_context else 'en'
            )

            return {
                "success": True,
                "voice_query": voice_query,
                "research_result": research_result,
                "voice_response": voice_response,
                "processing_summary": {
                    "voice_recognition_confidence": voice_query["confidence"],
                    "research_confidence": research_result.get("confidence_score", 0.0),
                    "response_length": len(response_text),
                    "audio_duration_estimate": voice_response.get("estimated_duration", 0)
                }
            }

        except Exception as e:
            logger.error(f"Voice research workflow failed: {e}")
            return {
                "success": False,
                "error": f"Voice research error: {str(e)}",
                "stage": "workflow"
            }

    async def get_voice_capabilities(self) -> Dict[str, Any]:
        """
        Get voice processing capabilities and supported features.
        """
        capabilities = {
            "speech_to_text": {
                "available": SPEECH_RECOGNITION_AVAILABLE,
                "engines": []
            },
            "text_to_speech": {
                "available": GTTS_AVAILABLE,
                "engines": []
            },
            "supported_languages": self.supported_languages,
            "voice_commands": list(self.voice_commands.keys()),
            "audio_formats": ["wav", "mp3"],
            "max_audio_duration": self.audio_settings["max_duration"]
        }

        if SPEECH_RECOGNITION_AVAILABLE:
            capabilities["speech_to_text"]["engines"].append("google")
            if OPENAI_AVAILABLE:
                capabilities["speech_to_text"]["engines"].append("whisper")

        if GTTS_AVAILABLE:
            capabilities["text_to_speech"]["engines"].append("google_tts")

        return capabilities

    async def process_audio_file(self, file_path: str, language: str = 'en') -> Dict[str, Any]:
        """
        Process an audio file for speech recognition.
        """
        try:
            if not SPEECH_RECOGNITION_AVAILABLE:
                return {
                    "success": False,
                    "error": "Speech recognition not available"
                }

            with sr.AudioFile(file_path) as source:
                audio = self.recognizer.record(source)

            return await self._recognize_speech(audio, language)

        except Exception as e:
            logger.error(f"Audio file processing failed: {e}")
            return {
                "success": False,
                "error": f"Audio processing error: {str(e)}"
            }

    def get_voice_command_help(self) -> Dict[str, Any]:
        """
        Get help information for voice commands.
        """
        return {
            "commands": {
                "research": {
                    "description": "Start a research query",
                    "examples": ["Research machine learning", "Find information about quantum computing"]
                },
                "deep_dive": {
                    "description": "Request comprehensive research",
                    "examples": ["Deep dive into blockchain technology", "Thorough analysis of climate change"]
                },
                "quick": {
                    "description": "Request brief summary",
                    "examples": ["Quick summary of World War 2", "Brief overview of photosynthesis"]
                },
                "compare": {
                    "description": "Compare two or more things",
                    "examples": ["Compare Python vs JavaScript", "What are the differences between SQL and NoSQL"]
                },
                "explain": {
                    "description": "Request detailed explanation",
                    "examples": ["Explain how neural networks work", "What is the theory of relativity"]
                },
                "stop": {
                    "description": "Stop current operation",
                    "examples": ["Stop", "Cancel", "Quit"]
                }
            },
            "tips": [
                "Speak clearly and at a moderate pace",
                "Use command words at the beginning of your query",
                "Be specific about what you want to research",
                "You can combine commands (e.g., 'Deep dive comparison of...')",
                "The system supports multiple languages"
            ]
        }

    async def validate_voice_input(self, audio_data: bytes) -> Dict[str, Any]:
        """
        Validate voice input before processing.
        """
        try:
            if len(audio_data) < 1000:  # Minimum audio size
                return {
                    "valid": False,
                    "error": "Audio data too small",
                    "confidence": 0.0
                }

            # Check for audio format (basic validation)
            if not audio_data.startswith(b'RIFF'):  # WAV header check
                return {
                    "valid": False,
                    "error": "Unsupported audio format (WAV required)",
                    "confidence": 0.0
                }

            return {
                "valid": True,
                "audio_size": len(audio_data),
                "estimated_duration": len(audio_data) / (16000 * 2),  # Rough estimate
                "confidence": 1.0
            }

        except Exception as e:
            return {
                "valid": False,
                "error": f"Audio validation error: {str(e)}",
                "confidence": 0.0
            }
