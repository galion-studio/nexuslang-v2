"""
Performance tests for Galion Agent System.

These tests measure system performance under load and stress conditions.
"""

import pytest
import asyncio
import time
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor
import statistics

from v2.backend.services.agents.agent_orchestrator import AgentOrchestrator
from v2.backend.services.integrations import IntegrationManager


@pytest.mark.performance
class TestPerformance:
    """Performance test suite."""

    @pytest.fixture
    async def orchestrator(self, tmp_path):
        """Create orchestrator for performance testing."""
        state_file = tmp_path / "perf_state.json"
        orchestrator = AgentOrchestrator(shared_state_path=str(state_file))

        # Mock expensive components for performance testing
        orchestrator.db_manager = None
        orchestrator.cache_manager = None

        yield orchestrator
        await orchestrator.cleanup()

    async def measure_execution_time(self, coro, iterations: int = 10) -> Dict[str, float]:
        """Measure execution time for a coroutine."""
        times = []

        for _ in range(iterations):
            start_time = time.time()
            await coro
            end_time = time.time()
            times.append(end_time - start_time)

        return {
            'min': min(times),
            'max': max(times),
            'avg': statistics.mean(times),
            'median': statistics.median(times),
            'stdev': statistics.stdev(times) if len(times) > 1 else 0,
            'iterations': iterations
        }

    async def test_orchestrator_initialization_performance(self):
        """Test orchestrator initialization performance."""
        async def init_orchestrator():
            orchestrator = AgentOrchestrator()
            await orchestrator.cleanup()

        metrics = await self.measure_execution_time(init_orchestrator, 5)

        # Should initialize in under 1 second
        assert metrics['avg'] < 1.0, f"Initialization too slow: {metrics['avg']}s"
        assert metrics['max'] < 2.0, f"Max initialization time too high: {metrics['max']}s"

    async def test_task_queue_performance(self, orchestrator):
        """Test task queue performance under load."""
        async def queue_operations():
            # Add multiple tasks
            task_ids = []
            for i in range(100):
                task = {
                    "task_id": f"perf_task_{i}",
                    "description": f"Performance test task {i}",
                    "priority": "normal"
                }
                task_id = await orchestrator.task_queue.add_task(task)
                task_ids.append(task_id)

            # Retrieve tasks
            retrieved_count = 0
            for _ in range(100):
                task = await orchestrator.task_queue.get_next_task()
                if task:
                    retrieved_count += 1

            return retrieved_count

        metrics = await self.measure_execution_time(queue_operations, 3)

        # Should handle 100 tasks efficiently
        assert metrics['avg'] < 5.0, f"Queue operations too slow: {metrics['avg']}s"

    async def test_integration_manager_performance(self):
        """Test integration manager performance."""
        async def integration_operations():
            manager = IntegrationManager()

            # Register multiple integrations
            for i in range(10):
                config = {"webhook_url": f"https://test{i}.example.com"}
                manager.register_integration(f"test_webhook_{i}", "webhook", config)

            # Get statuses
            statuses = await manager.get_all_statuses()

            await manager.cleanup()
            return len(statuses)

        metrics = await self.measure_execution_time(integration_operations, 3)

        # Should handle multiple integrations efficiently
        assert metrics['avg'] < 3.0, f"Integration operations too slow: {metrics['avg']}s"

    async def test_concurrent_task_processing(self, orchestrator):
        """Test concurrent task processing performance."""
        async def process_tasks_concurrently():
            tasks = []

            # Create concurrent task processors
            async def process_task(task_id: int):
                task = {
                    "task_id": f"concurrent_task_{task_id}",
                    "description": f"Concurrent task {task_id}",
                    "priority": "normal"
                }

                # Simulate task processing
                await asyncio.sleep(0.01)  # Small delay to simulate work
                return task_id

            # Launch multiple concurrent tasks
            for i in range(50):
                task = process_task(i)
                tasks.append(task)

            # Wait for all to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            successful_results = [r for r in results if not isinstance(r, Exception)]

            return len(successful_results)

        metrics = await self.measure_execution_time(process_tasks_concurrently, 3)

        # Should handle concurrent tasks efficiently
        assert metrics['avg'] < 10.0, f"Concurrent processing too slow: {metrics['avg']}s"

    async def test_memory_usage_stability(self, orchestrator):
        """Test memory usage stability under load."""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        async def memory_intensive_operations():
            # Perform memory-intensive operations
            tasks = []
            for i in range(1000):
                task = {
                    "task_id": f"memory_task_{i}",
                    "description": f"Memory test task {i}",
                    "priority": "normal",
                    "metadata": {"large_data": "x" * 1000}  # 1KB per task
                }
                tasks.append(orchestrator.task_queue.add_task(task))

            # Wait for all tasks to be queued
            await asyncio.gather(*tasks)

            # Clear queue
            cleared_count = 0
            while await orchestrator.task_queue.get_next_task():
                cleared_count += 1

            return cleared_count

        await memory_intensive_operations()

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (< 50MB)
        assert memory_increase < 50, f"Excessive memory usage: +{memory_increase:.1f}MB"

    async def test_api_response_times(self):
        """Test API response time performance."""
        from fastapi.testclient import TestClient
        from v2.backend.main import app

        client = TestClient(app)

        async def api_call():
            # Test health endpoint
            start_time = time.time()
            response = client.get("/health")
            end_time = time.time()

            assert response.status_code == 200
            return end_time - start_time

        metrics = await self.measure_execution_time(api_call, 20)

        # API should respond quickly
        assert metrics['avg'] < 0.1, f"API response too slow: {metrics['avg']}s"
        assert metrics['max'] < 0.5, f"Max API response time too high: {metrics['max']}s"

    async def test_integration_load_test(self):
        """Test integration framework under load."""
        async def integration_load():
            manager = IntegrationManager()

            # Register many integrations
            for i in range(20):
                config = {"webhook_url": f"https://loadtest{i}.example.com"}
                manager.register_integration(f"load_webhook_{i}", "webhook", config)

            # Perform operations on all integrations
            operations = []
            for i in range(20):
                operation = manager.execute_operation(
                    f"load_webhook_{i}",
                    "send_notification",
                    title=f"Load Test {i}",
                    message=f"Test message {i}"
                )
                operations.append(operation)

            # Wait for all operations to complete
            results = await asyncio.gather(*operations, return_exceptions=True)
            successful_results = [r for r in results if not isinstance(r, Exception)]

            await manager.cleanup()
            return len(successful_results)

        metrics = await self.measure_execution_time(integration_load, 2)

        # Should handle load efficiently
        assert metrics['avg'] < 15.0, f"Integration load test too slow: {metrics['avg']}s"

    def test_cpu_usage_during_operations(self, orchestrator):
        """Test CPU usage during intensive operations."""
        import psutil
        import os

        process = psutil.Process(os.getpid())

        # Measure CPU usage during intensive operations
        cpu_before = process.cpu_percent(interval=0.1)

        # Perform CPU-intensive operations synchronously for measurement
        def cpu_intensive_work():
            results = []
            for i in range(100000):
                result = i * i  # Simple CPU work
                results.append(result)
            return results

        with ThreadPoolExecutor() as executor:
            future = executor.submit(cpu_intensive_work)
            results = future.result()

        cpu_after = process.cpu_percent(interval=0.1)

        # CPU usage should be reasonable (not constantly at 100%)
        cpu_increase = cpu_after - cpu_before
        assert cpu_increase < 50, f"Excessive CPU usage: +{cpu_increase:.1f}%"

    async def test_scalability_with_agents(self, orchestrator):
        """Test system scalability as agent count increases."""
        async def scalability_test():
            # Simulate increasing agent load
            agent_counts = [1, 5, 10, 20]

            for count in agent_counts:
                # Simulate agent operations
                operations = []
                for i in range(count):
                    # Simulate agent task processing
                    operation = asyncio.sleep(0.001)  # Minimal delay
                    operations.append(operation)

                start_time = time.time()
                await asyncio.gather(*operations)
                end_time = time.time()

                processing_time = end_time - start_time

                # Processing time should scale reasonably
                # Allow some overhead but not exponential growth
                max_expected_time = count * 0.01  # 10ms per agent
                assert processing_time < max_expected_time, \
                    f"Poor scalability at {count} agents: {processing_time:.3f}s"

        await scalability_test()

    @pytest.mark.slow
    async def test_long_running_stability(self):
        """Test system stability during long-running operations."""
        async def long_running_test():
            orchestrator = AgentOrchestrator()

            start_time = time.time()

            # Run operations for 30 seconds
            while time.time() - start_time < 30:
                # Add tasks periodically
                for i in range(10):
                    task = {
                        "task_id": f"stability_task_{int(time.time())}_{i}",
                        "description": f"Stability test task {i}",
                        "priority": "normal"
                    }
                    await orchestrator.task_queue.add_task(task)

                # Process some tasks
                processed = 0
                for _ in range(10):
                    task = await orchestrator.task_queue.get_next_task()
                    if task:
                        processed += 1

                # Small delay to prevent overwhelming the system
                await asyncio.sleep(0.1)

            await orchestrator.cleanup()
            return processed

        metrics = await self.measure_execution_time(long_running_test, 1)

        # Should complete without errors
        assert metrics['max'] < 35.0, f"Long-running test took too long: {metrics['max']}s"

    async def test_error_handling_performance(self, orchestrator):
        """Test error handling performance under failure conditions."""
        async def error_handling_test():
            error_count = 0
            success_count = 0

            # Test various error scenarios
            for i in range(100):
                try:
                    # Test with invalid integration
                    result = await orchestrator.execute_integration_operation(
                        "non_existent_integration", "invalid_operation"
                    )

                    if result is None:
                        error_count += 1
                    else:
                        success_count += 1

                except Exception:
                    error_count += 1

            return {"errors": error_count, "successes": success_count}

        metrics = await self.measure_execution_time(error_handling_test, 3)

        # Error handling should be fast
        assert metrics['avg'] < 2.0, f"Error handling too slow: {metrics['avg']}s"

    def test_memory_leak_detection(self, orchestrator):
        """Test for memory leaks during repeated operations."""
        import gc
        import psutil
        import os

        process = psutil.Process(os.getpid())

        # Force garbage collection before test
        gc.collect()

        initial_objects = len(gc.get_objects())
        initial_memory = process.memory_info().rss

        # Perform repeated operations
        async def repeated_operations():
            for i in range(100):
                task = {
                    "task_id": f"leak_test_{i}",
                    "description": f"Memory leak test {i}",
                    "priority": "normal"
                }
                await orchestrator.task_queue.add_task(task)

                # Retrieve and discard
                await orchestrator.task_queue.get_next_task()

        asyncio.run(repeated_operations())

        # Force garbage collection
        gc.collect()

        final_objects = len(gc.get_objects())
        final_memory = process.memory_info().rss

        # Check for significant memory leaks
        memory_increase = (final_memory - initial_memory) / 1024 / 1024  # MB
        object_increase = final_objects - initial_objects

        # Allow some increase but not excessive
        assert memory_increase < 10, f"Memory leak detected: +{memory_increase:.1f}MB"
        assert object_increase < 1000, f"Object leak detected: +{object_increase} objects"
