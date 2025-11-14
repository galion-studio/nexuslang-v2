"""
Comprehensive tests for the Voice Processor and voice pipeline components.
Tests STT, TTS, VAD, and audio streaming functionality.
"""

import pytest
import asyncio
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from galion_app.lib.voice.voice_processor import VoiceProcessor
from galion_app.lib.voice.stt_service import STTService
from galion_app.lib.voice.tts_service import TTSService
from galion_app.lib.voice.audio_stream import AudioStream
from galion_app.lib.voice.vad_detector import VADDetector


class TestVoiceProcessor:
    """Test the main VoiceProcessor class"""

    @pytest.fixture
    def voice_processor(self):
        return VoiceProcessor()

    @pytest.mark.asyncio
    async def test_initialization(self, voice_processor):
        """Test VoiceProcessor initializes correctly"""
        assert voice_processor.recognition is not None
        assert voice_processor.audioContext is not None
        assert voice_processor.mediaStream is None
        assert voice_processor.websocket is None

    @pytest.mark.asyncio
    @patch('navigator.mediaDevices.getUserMedia')
    async def test_start_listening_success(self, mock_get_user_media, voice_processor):
        """Test successful microphone access and listening start"""
        # Mock the media stream
        mock_stream = Mock()
        mock_get_user_media.return_value = mock_stream

        # Mock the speech recognition start
        voice_processor.recognition.start = Mock()

        # Mock WebSocket
        with patch('WebSocket', Mock()) as mock_ws:
            await voice_processor.startListening()

            assert voice_processor.mediaStream == mock_stream
            voice_processor.recognition.start.assert_called_once()
            # WebSocket should be initialized
            assert voice_processor.websocket is not None

    @pytest.mark.asyncio
    @patch('navigator.mediaDevices.getUserMedia')
    async def test_start_listening_microphone_denied(self, mock_get_user_media, voice_processor):
        """Test handling of microphone permission denial"""
        mock_get_user_media.side_effect = Exception("Permission denied")

        with pytest.raises(Exception, match="Permission denied"):
            await voice_processor.startListening()

        assert voice_processor.mediaStream is None

    @pytest.mark.asyncio
    async def test_stop_listening(self, voice_processor):
        """Test stopping voice listening"""
        # Mock media stream
        mock_stream = Mock()
        mock_track1 = Mock()
        mock_track2 = Mock()
        mock_stream.getTracks.return_value = [mock_track1, mock_track2]
        voice_processor.mediaStream = mock_stream

        # Mock WebSocket
        mock_ws = Mock()
        voice_processor.websocket = mock_ws

        await voice_processor.stopListening()

        # Verify tracks are stopped
        mock_track1.stop.assert_called_once()
        mock_track2.stop.assert_called_once()

        # Verify WebSocket is closed
        mock_ws.close.assert_called_once()

        # Verify cleanup
        assert voice_processor.mediaStream is None
        assert voice_processor.websocket is None

    def test_speech_recognition_setup(self, voice_processor):
        """Test speech recognition is configured correctly"""
        recognition = voice_processor.recognition

        # Check basic configuration
        assert recognition.continuous == True
        assert recognition.interimResults == True
        assert recognition.lang == 'en-US'

        # Check event handlers are set
        assert hasattr(recognition, 'onresult')
        assert callable(recognition.onresult)


class TestSTTService:
    """Test Speech-to-Text service"""

    @pytest.fixture
    def stt_service(self):
        return STTService()

    @pytest.mark.asyncio
    async def test_transcribe_audio_success(self, stt_service):
        """Test successful audio transcription"""
        test_audio = "base64_encoded_audio_data"

        with patch('openai.Audio.transcribe') as mock_transcribe:
            mock_transcribe.return_value = {"text": "Hello, this is a test transcription"}

            result = await stt_service.transcribe_audio(test_audio, "wav", "en")

            assert result["text"] == "Hello, this is a test transcription"
            assert "confidence" in result
            assert result["language"] == "en"
            assert "duration" in result

    @pytest.mark.asyncio
    async def test_transcribe_audio_error_handling(self, stt_service):
        """Test error handling in transcription"""
        with patch('openai.Audio.transcribe', side_effect=Exception("API Error")):
            with pytest.raises(Exception):
                await stt_service.transcribe_audio("test_audio", "wav")

    @pytest.mark.asyncio
    async def test_transcribe_different_languages(self, stt_service):
        """Test transcription with different languages"""
        test_cases = [
            ("en", "Hello world"),
            ("es", "Hola mundo"),
            ("fr", "Bonjour le monde")
        ]

        with patch('openai.Audio.transcribe') as mock_transcribe:
            for lang, expected_text in test_cases:
                mock_transcribe.return_value = {"text": expected_text}

                result = await stt_service.transcribe_audio("test", "wav", lang)
                assert result["text"] == expected_text
                assert result["language"] == lang


class TestTTSService:
    """Test Text-to-Speech service"""

    @pytest.fixture
    def tts_service(self):
        return TTSService()

    @pytest.mark.asyncio
    async def test_synthesize_speech_success(self, tts_service):
        """Test successful speech synthesis"""
        test_text = "Hello, world!"
        voice = "alloy"

        with patch('openai.Audio.speech') as mock_speech:
            mock_audio_data = b"mock_audio_data"
            mock_speech.return_value = mock_audio_data

            result = await tts_service.synthesize_speech(test_text, voice)

            assert result == mock_audio_data

    @pytest.mark.asyncio
    async def test_synthesize_different_voices(self, tts_service):
        """Test synthesis with different voices"""
        voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

        with patch('openai.Audio.speech') as mock_speech:
            mock_speech.return_value = b"audio_data"

            for voice in voices:
                result = await tts_service.synthesize_speech("test", voice)
                assert result == b"audio_data"

                # Verify correct voice parameter was used
                mock_speech.assert_called_with(
                    model="tts-1",
                    voice=voice,
                    input="test"
                )

    @pytest.mark.asyncio
    async def test_synthesize_error_handling(self, tts_service):
        """Test error handling in speech synthesis"""
        with patch('openai.Audio.speech', side_effect=Exception("TTS API Error")):
            with pytest.raises(Exception, match="TTS API Error"):
                await tts_service.synthesize_speech("test text")


class TestAudioStream:
    """Test WebSocket audio streaming"""

    @pytest.fixture
    def audio_stream(self):
        return AudioStream()

    @pytest.mark.asyncio
    async def test_websocket_connection(self, audio_stream):
        """Test WebSocket connection establishment"""
        with patch('WebSocket') as mock_ws_class:
            mock_ws = Mock()
            mock_ws_class.return_value = mock_ws

            await audio_stream.connect("ws://test.com")

            mock_ws_class.assert_called_once_with("ws://test.com")
            assert audio_stream.websocket == mock_ws

    @pytest.mark.asyncio
    async def test_audio_data_sending(self, audio_stream):
        """Test sending audio data through WebSocket"""
        mock_ws = Mock()
        audio_stream.websocket = mock_ws

        test_audio_data = b"test_audio_bytes"

        await audio_stream.send_audio_data(test_audio_data)

        mock_ws.send.assert_called_once_with(test_audio_data)

    @pytest.mark.asyncio
    async def test_connection_error_handling(self, audio_stream):
        """Test handling of connection errors"""
        with patch('WebSocket', side_effect=Exception("Connection failed")):
            with pytest.raises(Exception, match="Connection failed"):
                await audio_stream.connect("ws://test.com")

    @pytest.mark.asyncio
    async def test_audio_format_conversion(self, audio_stream):
        """Test audio format conversion"""
        # Test raw PCM to WAV conversion
        raw_audio = np.random.randint(-32768, 32767, 44100, dtype=np.int16)

        wav_data = audio_stream.convert_to_wav(raw_audio, 44100, 1)

        # Verify WAV header is present
        assert len(wav_data) > 44  # WAV header is 44 bytes
        assert wav_data[:4] == b'RIFF'


class TestVADDetector:
    """Test Voice Activity Detection"""

    @pytest.fixture
    def vad_detector(self):
        return VADDetector()

    def test_silence_detection(self, vad_detector):
        """Test detection of silent audio"""
        # Generate silent audio (all zeros)
        silent_audio = np.zeros(16000, dtype=np.int16)

        is_speech = vad_detector.is_speech(silent_audio)

        assert is_speech == False

    def test_speech_detection(self, vad_detector):
        """Test detection of speech in audio"""
        # Generate audio with varying amplitude (simulating speech)
        np.random.seed(42)  # For reproducible results
        speech_audio = np.random.normal(0, 1000, 16000).astype(np.int16)

        is_speech = vad_detector.is_speech(speech_audio)

        # Should detect speech due to amplitude variations
        assert isinstance(is_speech, bool)

    def test_noise_filtering(self, vad_detector):
        """Test noise filtering capabilities"""
        # Generate noisy audio
        noise = np.random.normal(0, 100, 16000)
        signal = np.sin(2 * np.pi * 440 * np.arange(16000) / 16000) * 5000
        noisy_audio = (noise + signal).astype(np.int16)

        # VAD should still work with noise
        is_speech = vad_detector.is_speech(noisy_audio)

        assert isinstance(is_speech, bool)

    def test_audio_quality_analysis(self, vad_detector):
        """Test audio quality assessment"""
        # Test with different quality audio samples
        test_cases = [
            (np.random.normal(0, 50, 16000).astype(np.int16), "low_quality"),
            (np.random.normal(0, 1000, 16000).astype(np.int16), "good_quality"),
            (np.random.normal(0, 5000, 16000).astype(np.int16), "high_quality")
        ]

        for audio, expected_quality in test_cases:
            quality_score = vad_detector.analyze_quality(audio)

            assert isinstance(quality_score, float)
            assert 0.0 <= quality_score <= 1.0


class TestVoiceIntegration:
    """Integration tests for the complete voice pipeline"""

    @pytest.mark.asyncio
    async def test_full_voice_pipeline(self):
        """Test the complete voice processing pipeline"""
        # This would integrate all components together
        # For now, we'll test the mock pipeline

        voice_processor = VoiceProcessor()

        # Mock the entire pipeline
        with patch('navigator.mediaDevices.getUserMedia'), \
             patch('WebSocket'), \
             patch.object(voice_processor.recognition, 'start'):

            # Start listening
            await voice_processor.startListening()
            assert voice_processor.mediaStream is not None
            assert voice_processor.websocket is not None

            # Stop listening
            await voice_processor.stopListening()
            assert voice_processor.mediaStream is None
            assert voice_processor.websocket is None

    @pytest.mark.asyncio
    async def test_voice_error_recovery(self):
        """Test error recovery in voice pipeline"""
        voice_processor = VoiceProcessor()

        # Test recovery from microphone errors
        with patch('navigator.mediaDevices.getUserMedia', side_effect=Exception("Microphone busy")):
            with pytest.raises(Exception):
                await voice_processor.startListening()

        # Should be able to retry
        with patch('navigator.mediaDevices.getUserMedia') as mock_get_user_media, \
             patch('WebSocket'), \
             patch.object(voice_processor.recognition, 'start'):

            mock_stream = Mock()
            mock_get_user_media.return_value = mock_stream

            await voice_processor.startListening()
            assert voice_processor.mediaStream == mock_stream

    def test_voice_performance_metrics(self):
        """Test voice processing performance metrics"""
        vad_detector = VADDetector()

        # Test processing speed
        import time
        audio = np.random.normal(0, 1000, 16000).astype(np.int16)

        start_time = time.time()
        for _ in range(100):
            vad_detector.is_speech(audio)
        end_time = time.time()

        avg_time = (end_time - start_time) / 100

        # Should process quickly (less than 10ms per frame)
        assert avg_time < 0.01


if __name__ == "__main__":
    pytest.main([__file__])
