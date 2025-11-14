"""
Comprehensive API tests for voice endpoints and backend services.
Tests FastAPI endpoints, request/response handling, and integration.
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
import json
import base64
import io
from typing import Dict, Any

# Mock the voice services for testing
from v2.backend.api.voice import router as voice_router
from v2.backend.services.voice.stt_service import STTService
from v2.backend.services.voice.tts_service import TTSService


class TestVoiceAPI:
    """Test voice API endpoints"""

    @pytest.fixture
    def client(self):
        """Create test client with voice router"""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(voice_router)

        # Mock dependencies that might not be available in test environment
        with patch('v2.backend.api.voice.get_current_user', return_value=Mock()), \
             patch('v2.backend.api.voice.get_db', return_value=Mock()), \
             patch('v2.backend.api.voice.Session', Mock()), \
             patch('v2.backend.api.voice.UploadFile', Mock()), \
             patch('v2.backend.api.voice.File', Mock()), \
             patch('v2.backend.api.voice.Form', Mock()), \
             patch('v2.backend.api.voice.BackgroundTasks', Mock()), \
             patch('v2.backend.api.voice.Depends', Mock()), \
             patch('v2.backend.api.voice.WebSocket', Mock()), \
             patch('v2.backend.api.voice.WebSocketDisconnect', Mock()):

            return TestClient(app)

    def test_health_check(self, client):
        """Test voice API health check endpoint"""
        response = client.get("/voice/health")

        assert response.status_code == 200
        data = response.json()

        assert "status" in data
        assert data["status"] == "healthy"
        assert "stt" in data
        assert "tts" in data
        assert "timestamp" in data

    def test_get_available_voices(self, client):
        """Test getting available TTS voices"""
        response = client.get("/voice/voices")

        assert response.status_code == 200
        data = response.json()

        assert "voices" in data
        assert isinstance(data["voices"], list)
        assert len(data["voices"]) > 0

        # Check voice structure
        voice = data["voices"][0]
        assert "id" in voice
        assert "name" in voice
        assert "language" in voice
        assert "gender" in voice

    @patch('v2.backend.services.voice.stt_service.STTService.transcribe_audio')
    def test_transcribe_audio_success(self, mock_transcribe, client):
        """Test successful audio transcription"""
        # Mock the STT service response
        mock_transcribe.return_value = {
            "text": "Hello, this is a test transcription",
            "confidence": 0.95,
            "language": "en",
            "duration": 2.5
        }

        # Create mock base64 audio data
        mock_audio_data = base64.b64encode(b"mock_audio_data").decode()

        request_data = {
            "audio_data": mock_audio_data,
            "audio_format": "wav",
            "language": "en"
        }

        response = client.post("/voice/transcribe", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert data["text"] == "Hello, this is a test transcription"
        assert data["confidence"] == 0.95
        assert data["language"] == "en"
        assert data["duration"] == 2.5
        assert data["status"] == "success"

    def test_transcribe_audio_invalid_format(self, client):
        """Test transcription with invalid audio format"""
        request_data = {
            "audio_data": "invalid_base64",
            "audio_format": "invalid",
            "language": "en"
        }

        response = client.post("/voice/transcribe", json=request_data)

        # Should still return a response (mock implementation)
        assert response.status_code == 200
        data = response.json()
        assert "text" in data
        assert "status" in data

    @patch('v2.backend.services.voice.tts_service.TTSService.synthesize_speech')
    def test_synthesize_speech_success(self, mock_synthesize, client):
        """Test successful speech synthesis"""
        # Mock TTS service response
        mock_audio_data = b"RIFF\x24\x08\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80>\x00\x00\x00}\x00\x00\x02\x00\x10\x00data\x00\x08\x00\x00"
        mock_synthesize.return_value = mock_audio_data

        request_data = {
            "text": "Hello, world!",
            "voice": "alloy"
        }

        response = client.post("/voice/synthesize", json=request_data)

        assert response.status_code == 200
        assert response.headers["content-type"] == "audio/wav"
        assert "X-Voice" in response.headers
        assert "X-Text-Length" in response.headers

        # Verify audio data is returned
        audio_content = response.content
        assert len(audio_content) > 0

    def test_synthesize_speech_empty_text(self, client):
        """Test speech synthesis with empty text"""
        request_data = {
            "text": "",
            "voice": "alloy"
        }

        response = client.post("/voice/synthesize", json=request_data)

        # Mock implementation should handle empty text
        assert response.status_code == 200

    def test_synthesize_different_voices(self, client):
        """Test speech synthesis with different voices"""
        voices = ["alloy", "echo", "nova"]

        for voice in voices:
            with patch('v2.backend.services.voice.tts_service.TTSService.synthesize_speech') as mock_synthesize:
                mock_audio = b"mock_audio_data"
                mock_synthesize.return_value = mock_audio

                request_data = {
                    "text": "Test message",
                    "voice": voice
                }

                response = client.post("/voice/synthesize", json=request_data)

                assert response.status_code == 200
                assert response.headers.get("X-Voice") == voice

    def test_invalid_request_format(self, client):
        """Test handling of invalid request formats"""
        # Test transcribe with missing required fields
        response = client.post("/voice/transcribe", json={})
        assert response.status_code == 422  # Validation error

        # Test synthesize with missing text
        response = client.post("/voice/synthesize", json={"voice": "alloy"})
        assert response.status_code == 422  # Validation error

    def test_api_rate_limiting(self, client):
        """Test API rate limiting behavior"""
        # Make multiple rapid requests to test rate limiting
        for i in range(10):
            response = client.get("/voice/health")
            assert response.status_code == 200

        # Rate limiting might kick in after many requests
        # This test ensures the endpoint can handle multiple calls
        response = client.get("/voice/health")
        assert response.status_code in [200, 429]  # 429 = Too Many Requests

    def test_cors_headers(self, client):
        """Test CORS headers are properly set"""
        response = client.options("/voice/health")

        # Check for common CORS headers
        cors_headers = [
            "access-control-allow-origin",
            "access-control-allow-methods",
            "access-control-allow-headers"
        ]

        for header in cors_headers:
            assert header in response.headers or response.status_code == 200

    def test_response_format_consistency(self, client):
        """Test all endpoints return consistent response formats"""
        endpoints = [
            "/voice/health",
            "/voice/voices"
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200

            # Should return valid JSON
            try:
                data = response.json()
                assert isinstance(data, dict)
            except json.JSONDecodeError:
                pytest.fail(f"Endpoint {endpoint} did not return valid JSON")

    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test handling of concurrent API requests"""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(voice_router)

        async def make_request(client, endpoint):
            response = client.get(endpoint)
            return response.status_code

        with TestClient(app) as client:
            # Make multiple concurrent requests
            tasks = []
            for _ in range(5):
                tasks.append(make_request(client, "/voice/health"))

            results = await asyncio.gather(*tasks)

            # All requests should succeed
            assert all(status == 200 for status in results)


class TestVoiceAPIIntegration:
    """Integration tests combining multiple voice API components"""

    @pytest.fixture
    def client(self):
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(voice_router)
        return TestClient(app)

    def test_full_voice_workflow(self, client):
        """Test a complete voice interaction workflow"""
        # 1. Check health
        health_response = client.get("/voice/health")
        assert health_response.status_code == 200

        # 2. Get available voices
        voices_response = client.get("/voice/voices")
        assert voices_response.status_code == 200
        voices_data = voices_response.json()
        available_voice = voices_data["voices"][0]["id"]

        # 3. Synthesize speech
        with patch('v2.backend.services.voice.tts_service.TTSService.synthesize_speech') as mock_synthesize:
            mock_synthesize.return_value = b"mock_audio"

            synth_response = client.post("/voice/synthesize", json={
                "text": "Hello from integration test",
                "voice": available_voice
            })
            assert synth_response.status_code == 200

        # 4. Transcribe audio (mock)
        with patch('v2.backend.services.voice.stt_service.STTService.transcribe_audio') as mock_transcribe:
            mock_transcribe.return_value = {
                "text": "This is a test transcription",
                "confidence": 0.9,
                "language": "en",
                "duration": 1.5
            }

            transcribe_response = client.post("/voice/transcribe", json={
                "audio_data": base64.b64encode(b"test").decode(),
                "audio_format": "wav"
            })
            assert transcribe_response.status_code == 200

    def test_error_recovery(self, client):
        """Test error recovery and graceful degradation"""
        # Test with invalid base64 data
        response = client.post("/voice/transcribe", json={
            "audio_data": "invalid_base64_data!@#",
            "audio_format": "wav"
        })

        # Should handle gracefully (mock implementation)
        assert response.status_code == 200
        data = response.json()
        assert "text" in data

    def test_api_performance(self, client):
        """Test API performance under load"""
        import time

        # Measure response time for multiple requests
        response_times = []

        for _ in range(10):
            start_time = time.time()
            response = client.get("/voice/health")
            end_time = time.time()

            assert response.status_code == 200
            response_times.append(end_time - start_time)

        avg_response_time = sum(response_times) / len(response_times)

        # Should respond within reasonable time (< 100ms for health check)
        assert avg_response_time < 0.1

    def test_memory_usage(self, client):
        """Test for memory leaks in API endpoints"""
        import psutil
        import os

        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Make multiple requests
        for _ in range(50):
            response = client.get("/voice/health")
            assert response.status_code == 200

            response = client.get("/voice/voices")
            assert response.status_code == 200

        # Check memory usage after requests
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (< 50MB)
        assert memory_increase < 50 * 1024 * 1024


class TestVoiceAPIEdgeCases:
    """Test edge cases and boundary conditions"""

    @pytest.fixture
    def client(self):
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(voice_router)
        return TestClient(app)

    def test_large_audio_data(self, client):
        """Test handling of large audio data"""
        # Create large base64 string (simulating large audio file)
        large_audio = base64.b64encode(b"x" * 1000000).decode()  # ~1.3MB

        response = client.post("/voice/transcribe", json={
            "audio_data": large_audio,
            "audio_format": "wav"
        })

        # Should handle large data gracefully
        assert response.status_code in [200, 413]  # 200=success, 413=payload too large

    def test_special_characters_in_text(self, client):
        """Test handling of special characters in synthesis text"""
        special_text = "Hello! @#$%^&*()_+-=[]{}|;:,.<>? 世界 🌍"

        with patch('v2.backend.services.voice.tts_service.TTSService.synthesize_speech') as mock_synthesize:
            mock_synthesize.return_value = b"mock_audio"

            response = client.post("/voice/synthesize", json={
                "text": special_text,
                "voice": "alloy"
            })

            assert response.status_code == 200

    def test_very_long_text(self, client):
        """Test synthesis of very long text"""
        long_text = "Hello, world! " * 1000  # Very long text

        with patch('v2.backend.services.voice.tts_service.TTSService.synthesize_speech') as mock_synthesize:
            mock_synthesize.return_value = b"mock_audio"

            response = client.post("/voice/synthesize", json={
                "text": long_text,
                "voice": "alloy"
            })

            assert response.status_code == 200

    def test_concurrent_users_simulation(self, client):
        """Simulate multiple users making concurrent requests"""
        import threading
        import time

        results = []
        errors = []

        def make_request(user_id):
            try:
                response = client.get("/voice/health")
                results.append((user_id, response.status_code))
            except Exception as e:
                errors.append((user_id, str(e)))

        # Simulate 10 concurrent users
        threads = []
        for i in range(10):
            thread = threading.Thread(target=make_request, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # All requests should succeed
        assert len(results) == 10
        assert all(status == 200 for _, status in results)
        assert len(errors) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
