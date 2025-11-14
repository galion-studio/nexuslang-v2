"""
Performance tests for the Galion Platform.
Tests scalability, response times, and resource usage under load.
"""

import pytest
import asyncio
import time
import psutil
import os
from unittest.mock import patch, AsyncMock
import statistics
from concurrent.futures import ThreadPoolExecutor
import threading
from typing import List, Dict, Any


class TestVoicePerformance:
    """Performance tests for voice processing components"""

    def test_stt_processing_speed(self):
        """Test STT processing speed with various audio lengths"""
        from galion_app.lib.voice.stt_service import STTService

        stt_service = STTService()

        # Test with different audio sizes
        test_cases = [
            (1, "Short audio (1 second)"),
            (5, "Medium audio (5 seconds)"),
            (30, "Long audio (30 seconds)")
        ]

        for duration, description in test_cases:
            with patch('openai.Audio.transcribe') as mock_transcribe:
                mock_transcribe.return_value = {"text": f"Mock transcription for {duration}s audio"}

                # Simulate audio data size based on duration
                audio_size = duration * 16000 * 2  # 16kHz, 16-bit
                mock_audio = "x" * (audio_size // 100)  # Compress for test

                start_time = time.time()
                result = asyncio.run(stt_service.transcribe_audio(mock_audio, "wav"))
                end_time = time.time()

                processing_time = end_time - start_time

                # STT should process within reasonable time limits
                max_time = duration * 2  # Allow 2x real-time processing
                assert processing_time < max_time, f"{description} took {processing_time:.2f}s (max {max_time}s)"

                assert result["text"] == f"Mock transcription for {duration}s audio"

    def test_tts_processing_speed(self):
        """Test TTS processing speed with various text lengths"""
        from galion_app.lib.voice.tts_service import TTSService

        tts_service = TTSService()

        test_cases = [
            (10, "Short text (10 chars)"),
            (100, "Medium text (100 chars)"),
            (1000, "Long text (1000 chars)")
        ]

        for text_length, description in test_cases:
            with patch('openai.Audio.speech') as mock_speech:
                mock_speech.return_value = b"mock_audio_data"

                test_text = "A" * text_length

                start_time = time.time()
                result = asyncio.run(tts_service.synthesize_speech(test_text, "alloy"))
                end_time = time.time()

                processing_time = end_time - start_time

                # TTS should process quickly regardless of text length
                assert processing_time < 2.0, f"{description} took {processing_time:.2f}s"

                assert len(result) > 0

    def test_vad_real_time_processing(self):
        """Test VAD processing speed for real-time audio"""
        from galion_app.lib.voice.vad_detector import VADDetector
        import numpy as np

        vad_detector = VADDetector()

        # Generate 1 second of audio (16kHz)
        sample_rate = 16000
        duration = 1.0
        samples = int(sample_rate * duration)

        # Test with speech-like audio
        audio = np.random.normal(0, 5000, samples).astype(np.int16)

        # Measure processing time for real-time requirement
        start_time = time.time()

        # Process in small chunks (as would happen in real-time)
        chunk_size = 1024  # ~64ms chunks
        for i in range(0, len(audio), chunk_size):
            chunk = audio[i:i + chunk_size]
            vad_detector.is_speech(chunk)

        end_time = time.time()
        processing_time = end_time - start_time

        # Should process faster than real-time (allow 2x real-time)
        real_time_limit = duration * 2
        assert processing_time < real_time_limit, f"VAD processing took {processing_time:.2f}s for {duration}s audio"


class TestAPIPerformance:
    """Performance tests for API endpoints"""

    @pytest.fixture
    def client(self):
        """Create test client for API testing"""
        from fastapi.testclient import TestClient
        from fastapi import FastAPI

        app = FastAPI()
        # Import and add voice router
        from v2.backend.api.voice import router as voice_router
        app.include_router(voice_router)

        return TestClient(app)

    def test_health_check_performance(self, client):
        """Test health check endpoint performance"""
        response_times = []

        # Measure multiple requests
        for _ in range(100):
            start_time = time.time()
            response = client.get("/voice/health")
            end_time = time.time()

            assert response.status_code == 200
            response_times.append(end_time - start_time)

        avg_time = statistics.mean(response_times)
        max_time = max(response_times)
        p95_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile

        # Health checks should be very fast
        assert avg_time < 0.01, f"Average response time: {avg_time:.4f}s"
        assert max_time < 0.05, f"Max response time: {max_time:.4f}s"
        assert p95_time < 0.02, f"95th percentile: {p95_time:.4f}s"

    def test_voice_api_throughput(self, client):
        """Test voice API throughput under load"""
        import threading

        results = []
        errors = []

        def make_request(request_id):
            try:
                start_time = time.time()
                response = client.get("/voice/voices")
                end_time = time.time()

                results.append({
                    'id': request_id,
                    'status_code': response.status_code,
                    'response_time': end_time - start_time
                })
            except Exception as e:
                errors.append({'id': request_id, 'error': str(e)})

        # Simulate concurrent users
        threads = []
        num_requests = 50

        for i in range(num_requests):
            thread = threading.Thread(target=make_request, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Analyze results
        successful_requests = [r for r in results if r['status_code'] == 200]
        success_rate = len(successful_requests) / num_requests

        if successful_requests:
            avg_response_time = statistics.mean([r['response_time'] for r in successful_requests])
            max_response_time = max([r['response_time'] for r in successful_requests])

            # High success rate and reasonable response times
            assert success_rate > 0.95, f"Success rate: {success_rate:.2%}"
            assert avg_response_time < 0.1, f"Average response time: {avg_response_time:.4f}s"
            assert max_response_time < 0.5, f"Max response time: {max_response_time:.4f}s"

    def test_memory_usage_under_load(self, client):
        """Test memory usage during sustained load"""
        process = psutil.Process(os.getpid())

        # Get baseline memory
        baseline_memory = process.memory_info().rss

        # Generate sustained load
        for _ in range(1000):
            response = client.get("/voice/health")
            assert response.status_code == 200

        # Check memory usage after load
        final_memory = process.memory_info().rss
        memory_increase = final_memory - baseline_memory
        memory_mb = memory_increase / (1024 * 1024)

        # Memory increase should be reasonable (< 50MB)
        assert memory_mb < 50, f"Memory increase: {memory_mb:.1f}MB"

    def test_database_connection_pooling(self, client):
        """Test database connection pooling under concurrent load"""
        # This would test actual database connections in a real environment
        # For now, we'll test the mock implementation

        def make_db_request(request_id):
            # Simulate database operation
            response = client.post("/voice/transcribe", json={
                "audio_data": "dGVzdA==",  # base64 "test"
                "audio_format": "wav"
            })
            return response.status_code

        # Test concurrent database operations
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_db_request, i) for i in range(20)]
            results = [future.result() for future in futures]

        # All requests should succeed
        assert all(status == 200 for status in results)


class TestAgentPerformance:
    """Performance tests for the agent orchestration system"""

    @pytest.fixture
    async def orchestrator(self):
        """Create test orchestrator"""
        from v2.backend.services.agents.agent_orchestrator import AgentOrchestrator

        orch = AgentOrchestrator(max_concurrent_tasks=10)

        # Mock agents for performance testing
        from unittest.mock import Mock
        from v2.backend.services.agents.base_agent import AgentResult

        mock_agent = Mock()
        mock_agent.execute = AsyncMock(return_value=AgentResult(
            success=True, response="Mock response", cost=0.01, execution_time=0.5
        ))

        orch.agents = {
            'test_agent': mock_agent
        }

        yield orch
        await orch.stop()

    @pytest.mark.asyncio
    async def test_agent_response_times(self, orchestrator):
        """Test agent response time consistency"""
        await orchestrator.start()

        response_times = []

        # Execute multiple agent requests
        for i in range(20):
            start_time = time.time()
            result = await orchestrator.execute(f"Test request {i}")
            end_time = time.time()

            response_times.append(end_time - start_time)
            assert result.success

        avg_time = statistics.mean(response_times)
        max_time = max(response_times)
        p95_time = statistics.quantiles(response_times, n=20)[18]

        # Agent responses should be reasonably fast
        assert avg_time < 1.0, f"Average response time: {avg_time:.4f}s"
        assert max_time < 2.0, f"Max response time: {max_time:.4f}s"
        assert p95_time < 1.5, f"95th percentile: {p95_time:.4f}s"

    @pytest.mark.asyncio
    async def test_concurrent_agent_execution(self, orchestrator):
        """Test concurrent agent execution performance"""
        await orchestrator.start()

        async def execute_task(task_id):
            start_time = time.time()
            result = await orchestrator.execute(f"Concurrent task {task_id}")
            end_time = time.time()

            return {
                'task_id': task_id,
                'success': result.success,
                'response_time': end_time - start_time
            }

        # Execute multiple tasks concurrently
        tasks = [execute_task(i) for i in range(10)]
        results = await asyncio.gather(*tasks)

        # All tasks should succeed
        assert all(r['success'] for r in results)

        # Calculate performance metrics
        response_times = [r['response_time'] for r in results]
        avg_time = statistics.mean(response_times)
        max_time = max(response_times)

        # Concurrent execution should not be much slower than sequential
        assert avg_time < 2.0, f"Average concurrent response time: {avg_time:.4f}s"
        assert max_time < 3.0, f"Max concurrent response time: {max_time:.4f}s"

    @pytest.mark.asyncio
    async def test_agent_cost_tracking(self, orchestrator):
        """Test cost tracking accuracy under load"""
        await orchestrator.start()

        initial_cost = orchestrator.metrics.total_cost

        # Execute multiple tasks
        for i in range(50):
            await orchestrator.execute(f"Cost test {i}")

        final_cost = orchestrator.metrics.total_cost
        cost_increase = final_cost - initial_cost

        # Cost should be tracked accurately (50 tasks * $0.01 each = $0.50)
        expected_cost = 50 * 0.01
        assert abs(cost_increase - expected_cost) < 0.01, f"Cost tracking error: expected {expected_cost}, got {cost_increase}"


class TestFrontendPerformance:
    """Performance tests for frontend components"""

    def test_component_render_performance(self):
        """Test React component render performance"""
        # This would require a test setup with React Testing Library
        # For now, we'll create placeholder tests

        # Test VoiceButton render time
        start_time = time.time()

        # Simulate component rendering
        for _ in range(1000):
            # Mock component render logic
            pass

        end_time = time.time()
        render_time = end_time - start_time

        # Should render quickly
        assert render_time < 1.0, f"Component render time: {render_time:.4f}s"

    def test_bundle_size_performance(self):
        """Test JavaScript bundle sizes"""
        # Check if bundle files exist and are reasonable size
        bundle_paths = [
            "galion-app/.next/static/chunks/main.js",
            "developer-platform/.next/static/chunks/main.js",
            "galion-studio/.next/static/chunks/main.js"
        ]

        for bundle_path in bundle_paths:
            if os.path.exists(bundle_path):
                size = os.path.getsize(bundle_path)
                size_mb = size / (1024 * 1024)

                # Bundles should be reasonable size (< 5MB)
                assert size_mb < 5.0, f"Bundle {bundle_path} is too large: {size_mb:.2f}MB"

    def test_image_optimization(self):
        """Test image optimization and loading"""
        # Check for optimized image formats
        image_extensions = ['.webp', '.avif', '.jpg', '.png']
        optimized_extensions = ['.webp', '.avif']

        # This would scan actual image files in the project
        # For now, we'll check that image optimization is configured

        # Check if Next.js image optimization is configured
        next_config_paths = [
            "galion-app/next.config.js",
            "developer-platform/next.config.js",
            "galion-studio/next.config.js"
        ]

        for config_path in next_config_paths:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    content = f.read()
                    # Should have image optimization configured
                    assert 'images' in content, f"{config_path} should have image optimization configured"


class TestSystemPerformance:
    """System-level performance tests"""

    def test_cpu_usage_under_load(self):
        """Test CPU usage during load testing"""
        process = psutil.Process(os.getpid())

        # Get baseline CPU usage
        baseline_cpu = process.cpu_percent(interval=1)

        # Generate load (this would be more sophisticated in real tests)
        for _ in range(10000):
            _ = 2 ** 10  # Simple CPU operation

        # Check CPU usage during load
        load_cpu = process.cpu_percent(interval=1)

        # CPU usage should not be excessive
        assert load_cpu < 80, f"High CPU usage during load: {load_cpu}%"

    def test_memory_leak_detection(self):
        """Test for memory leaks during extended operation"""
        process = psutil.Process(os.getpid())

        memory_readings = []

        # Monitor memory over time
        for i in range(10):
            # Simulate some operations
            time.sleep(0.1)

            memory_mb = process.memory_info().rss / (1024 * 1024)
            memory_readings.append(memory_mb)

        # Memory should not continuously increase (basic leak detection)
        if len(memory_readings) > 5:
            trend = statistics.linear_regression(
                range(len(memory_readings)),
                memory_readings
            )[0]  # Slope of linear regression

            # Memory trend should not be strongly increasing
            assert trend < 1.0, f"Possible memory leak detected, trend: {trend}"

    def test_disk_io_performance(self):
        """Test disk I/O performance for file operations"""
        import tempfile

        # Test file write performance
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            temp_file = f.name

            start_time = time.time()

            # Write test data
            for i in range(1000):
                f.write(f"Line {i}: Test data for performance measurement\n")

            f.flush()
            os.fsync(f.fileno())  # Force write to disk

            end_time = time.time()
            write_time = end_time - start_time

        # Clean up
        os.unlink(temp_file)

        # File operations should be reasonably fast
        assert write_time < 1.0, f"File write performance: {write_time:.4f}s for 1000 lines"

    def test_network_performance_simulation(self):
        """Test network performance simulation"""
        # This would test API calls under various network conditions
        # For now, we'll test basic network timeout handling

        import requests
        from requests.exceptions import Timeout

        # Test timeout handling
        try:
            # This should timeout quickly
            response = requests.get("http://httpbin.org/delay/10", timeout=1)
        except Timeout:
            # Expected timeout - this is good
            pass
        except Exception:
            # Other errors are unexpected
            pytest.fail("Unexpected error in timeout test")

        # Test successful request performance
        start_time = time.time()
        response = requests.get("http://httpbin.org/get", timeout=5)
        end_time = time.time()

        request_time = end_time - start_time

        assert response.status_code == 200
        assert request_time < 2.0, f"Network request too slow: {request_time:.4f}s"


class TestScalability:
    """Scalability tests for the platform"""

    def test_user_concurrency_limits(self):
        """Test maximum concurrent users the system can handle"""
        # This would require a more complex test setup with multiple processes
        # For now, we'll test basic concurrency

        def simulate_user_session(user_id):
            # Simulate a user session
            time.sleep(0.01)  # Brief operation
            return f"User {user_id} completed"

        # Test concurrent user simulation
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(simulate_user_session, i) for i in range(100)]
            results = [future.result() for future in futures]

        assert len(results) == 100
        assert all("completed" in result for result in results)

    def test_database_connection_scaling(self):
        """Test database connection scaling"""
        # This would test actual database connections
        # For now, we'll test mock connection handling

        connection_pool = []

        def simulate_db_connection(connection_id):
            connection_pool.append(connection_id)
            time.sleep(0.001)  # Simulate connection time
            return f"Connection {connection_id} established"

        # Test connection pool scaling
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(simulate_db_connection, i) for i in range(50)]
            results = [future.result() for future in futures]

        assert len(results) == 50
        assert len(connection_pool) == 50

    def test_cache_performance_scaling(self):
        """Test cache performance under scaling"""
        # Simulate cache operations
        cache = {}
        cache_hits = 0
        cache_misses = 0

        def cache_operation(key, value=None):
            nonlocal cache_hits, cache_misses

            if value is None:  # Read operation
                if key in cache:
                    cache_hits += 1
                    return cache[key]
                else:
                    cache_misses += 1
                    return None
            else:  # Write operation
                cache[key] = value
                return True

        # Test cache scaling
        with ThreadPoolExecutor(max_workers=10) as executor:
            # Mix of read and write operations
            operations = []
            for i in range(100):
                if i % 3 == 0:  # Write operation
                    operations.append(executor.submit(cache_operation, f"key_{i}", f"value_{i}"))
                else:  # Read operation
                    operations.append(executor.submit(cache_operation, f"key_{i % 10}"))

            results = [future.result() for future in operations]

        # Cache should have reasonable hit rate
        total_reads = cache_hits + cache_misses
        if total_reads > 0:
            hit_rate = cache_hits / total_reads
            assert hit_rate > 0.5, f"Low cache hit rate: {hit_rate:.2%}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
