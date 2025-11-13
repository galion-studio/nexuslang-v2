"""
NexusLang v2 - Voice Integration
Native voice-to-voice capabilities for NexusLang.
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass
import httpx
import asyncio
from io import BytesIO


@dataclass
class VoiceConfig:
    """
    Configuration for voice synthesis and recognition.
    """
    # STT (Speech-to-Text) settings
    stt_model: str = "whisper-base"
    stt_language: str = "en"
    stt_timeout: int = 30
    
    # TTS (Text-to-Speech) settings
    tts_model: str = "coqui-tts"
    tts_voice_id: str = "galion-default"
    tts_speed: float = 1.0
    tts_emotion: Optional[str] = None
    
    # API settings
    api_url: str = "http://localhost:8000/api/v2/voice"


class VoiceClient:
    """
    Client for voice services (STT and TTS).
    """
    
    def __init__(self, config: Optional[VoiceConfig] = None):
        self.config = config or VoiceConfig()
        self.session_id = None
    
    async def speech_to_text(
        self,
        audio_data: bytes,
        language: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Convert speech to text using Whisper.
        
        Args:
            audio_data: Audio bytes (WAV, MP3, etc.)
            language: Language code (default from config)
            timeout: Timeout in seconds
        
        Returns:
            Dict with 'text' and 'confidence'
        """
        lang = language or self.config.stt_language
        timeout_val = timeout or self.config.stt_timeout
        
        async with httpx.AsyncClient(timeout=timeout_val) as client:
            files = {'audio': ('audio.wav', audio_data, 'audio/wav')}
            response = await client.post(
                f"{self.config.api_url}/stt",
                files=files,
                data={'language': lang}
            )
            response.raise_for_status()
            return response.json()
    
    async def text_to_speech(
        self,
        text: str,
        voice_id: Optional[str] = None,
        emotion: Optional[str] = None,
        speed: Optional[float] = None
    ) -> bytes:
        """
        Convert text to speech using TTS.
        
        Args:
            text: Text to synthesize
            voice_id: Voice model ID
            emotion: Emotion/tone (happy, sad, neutral, etc.)
            speed: Speech speed multiplier
        
        Returns:
            Audio bytes (WAV format)
        """
        voice = voice_id or self.config.tts_voice_id
        emo = emotion or self.config.tts_emotion
        spd = speed or self.config.tts_speed
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.config.api_url}/tts",
                json={
                    'text': text,
                    'voice_id': voice,
                    'emotion': emo,
                    'speed': spd
                }
            )
            response.raise_for_status()
            
            # Return audio URL or bytes
            result = response.json()
            audio_url = result.get('audio_url')
            
            if audio_url:
                # Download audio
                audio_response = await client.get(audio_url)
                return audio_response.content
            
            return b''
    
    async def clone_voice(
        self,
        audio_samples: list[bytes],
        voice_name: str
    ) -> str:
        """
        Clone a voice from audio samples.
        
        Args:
            audio_samples: List of audio bytes (multiple samples)
            voice_name: Name for the cloned voice
        
        Returns:
            voice_id of the cloned voice
        """
        async with httpx.AsyncClient(timeout=120.0) as client:
            files = [
                ('samples', (f'sample_{i}.wav', sample, 'audio/wav'))
                for i, sample in enumerate(audio_samples)
            ]
            
            response = await client.post(
                f"{self.config.api_url}/clone",
                files=files,
                data={'name': voice_name}
            )
            response.raise_for_status()
            result = response.json()
            
            return result['voice_id']


# Global voice client instance
_voice_client = None


def get_voice_client() -> VoiceClient:
    """Get or create the global voice client."""
    global _voice_client
    if _voice_client is None:
        _voice_client = VoiceClient()
    return _voice_client


def say(text: str, emotion: Optional[str] = None, voice_id: Optional[str] = None, speed: float = 1.0):
    """
    Text-to-speech function for NexusLang.
    
    Example:
        say("Hello world!")
        say("I'm excited!", emotion="happy")
        say("Speaking slowly...", speed=0.8)
    """
    client = get_voice_client()
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        audio_data = loop.run_until_complete(
            client.text_to_speech(text, voice_id, emotion, speed)
        )
        
        # Play audio (platform-specific)
        _play_audio(audio_data)
        
    finally:
        loop.close()


def listen(timeout: int = 30, language: str = "en") -> str:
    """
    Speech-to-text function for NexusLang.
    
    Example:
        let response = listen()
        let answer = listen(timeout=10)
    """
    client = get_voice_client()
    
    # Record audio from microphone
    audio_data = _record_audio(duration=timeout)
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(
            client.speech_to_text(audio_data, language, timeout)
        )
        return result.get('text', '')
    finally:
        loop.close()


def clone_voice(samples_paths: list[str], voice_name: str) -> str:
    """
    Clone a voice from audio samples.
    
    Example:
        let my_voice = clone_voice(["sample1.wav", "sample2.wav"], "my_voice")
    """
    client = get_voice_client()
    
    # Load audio samples
    samples = []
    for path in samples_paths:
        with open(path, 'rb') as f:
            samples.append(f.read())
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        voice_id = loop.run_until_complete(
            client.clone_voice(samples, voice_name)
        )
        return voice_id
    finally:
        loop.close()


# Platform-specific audio handling

def _play_audio(audio_data: bytes):
    """
    Play audio data (platform-specific).
    Uses different backends depending on OS.
    """
    try:
        import pyaudio
        import wave
        from io import BytesIO
        
        # Parse WAV data
        wav_file = BytesIO(audio_data)
        wf = wave.open(wav_file, 'rb')
        
        # Initialize PyAudio
        p = pyaudio.PyAudio()
        
        # Open stream
        stream = p.open(
            format=p.get_format_from_width(wf.getsampwidth()),
            channels=wf.getnchannels(),
            rate=wf.getframerate(),
            output=True
        )
        
        # Play audio
        data = wf.readframes(1024)
        while data:
            stream.write(data)
            data = wf.readframes(1024)
        
        # Cleanup
        stream.stop_stream()
        stream.close()
        p.terminate()
        
    except ImportError:
        # Fallback: save to temp file and use system player
        import tempfile
        import os
        import subprocess
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            f.write(audio_data)
            temp_path = f.name
        
        try:
            if os.name == 'nt':  # Windows
                os.startfile(temp_path)
            elif os.name == 'posix':  # Linux/Mac
                subprocess.run(['aplay' if os.uname().sysname == 'Linux' else 'afplay', temp_path])
        finally:
            # Clean up temp file after a delay
            pass


def _record_audio(duration: int = 30) -> bytes:
    """
    Record audio from microphone (platform-specific).
    
    Args:
        duration: Maximum recording duration in seconds
    
    Returns:
        Audio bytes (WAV format)
    """
    try:
        import pyaudio
        import wave
        from io import BytesIO
        
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000  # 16kHz for Whisper
        
        p = pyaudio.PyAudio()
        
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )
        
        print("🎤 Listening...")
        
        frames = []
        for _ in range(0, int(RATE / CHUNK * duration)):
            data = stream.read(CHUNK)
            frames.append(data)
        
        print("✅ Recording complete")
        
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        # Convert to WAV
        wav_buffer = BytesIO()
        wf = wave.open(wav_buffer, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        return wav_buffer.getvalue()
        
    except ImportError:
        print("❌ PyAudio not installed. Voice input not available.")
        print("   Install with: pip install pyaudio")
        return b''
    except Exception as e:
        print(f"❌ Recording error: {e}")
        return b''


# Voice utility functions

def get_available_voices() -> list[str]:
    """
    Get list of available voice models.
    """
    # TODO: Implement API call to get available voices
    return ["galion-default", "galion-1", "galion-2"]


def get_supported_languages() -> list[str]:
    """
    Get list of supported languages.
    """
    return ["en", "es", "fr", "de", "zh", "ja", "ko"]


def get_supported_emotions() -> list[str]:
    """
    Get list of supported emotion/tone options.
    """
    return ["neutral", "happy", "sad", "excited", "angry", "calm", "friendly", "professional"]

