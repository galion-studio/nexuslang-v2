"""
Load testing for Galion Agent System using Locust.

This script simulates real-world load patterns and measures system performance
under various stress conditions.
"""

import json
import random
import time
from typing import Dict, Any, List
from locust import HttpUser, TaskSet, task, between, events
from locust.exception import StopUser


class GalionAPITasks(TaskSet):
    """Task set for testing Galion API endpoints."""

    def on_start(self):
        """Setup before starting tasks."""
        self.auth_token = None
        self.test_agents = []
        self.test_tasks = []

    @task(1)
    def health_check(self):
        """Test health check endpoint."""
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed: {response.status_code}")

    @task(2)
    def get_agents(self):
        """Test getting agents list."""
        with self.client.get("/agents", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    response.success()
                    # Store some agent names for later use
                    if len(data) > 0 and len(self.test_agents) < 5:
                        self.test_agents.extend([agent.get('name') for agent in data[:5]])
                else:
                    response.failure("Invalid response format")
            else:
                response.failure(f"Get agents failed: {response.status_code}")

    @task(2)
    def get_agent_status(self):
        """Test getting agent status."""
        if not self.test_agents:
            return

        agent_name = random.choice(self.test_agents)

        with self.client.get(f"/agents/status/{agent_name}", catch_response=True) as response:
            if response.status_code in [200, 404]:  # 404 is acceptable if agent doesn't exist
                response.success()
            else:
                response.failure(f"Get agent status failed: {response.status_code}")

    @task(3)
    def create_task(self):
        """Test creating tasks."""
        task_data = {
            "description": f"Load test task {random.randint(1, 10000)}",
            "priority": random.choice(["low", "normal", "high"]),
            "requirements": ["test"],
            "metadata": {
                "load_test": True,
                "user_id": random.randint(1, 100),
                "timestamp": time.time()
            }
        }

        with self.client.post("/agents/execute", json=task_data, catch_response=True) as response:
            if response.status_code in [200, 201, 202]:  # Various success codes
                response.success()
                # Store task ID for potential follow-up
                if response.status_code == 200:
                    data = response.json()
                    task_id = data.get('task_id')
                    if task_id and len(self.test_tasks) < 10:
                        self.test_tasks.append(task_id)
            elif response.status_code == 429:  # Rate limited
                response.success()  # Rate limiting is expected under load
            else:
                response.failure(f"Create task failed: {response.status_code}")

    @task(1)
    def get_task_status(self):
        """Test getting task queue status."""
        with self.client.get("/tasks/queue/status", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if all(key in data for key in ['queue_size', 'active_tasks', 'max_concurrent']):
                    response.success()
                else:
                    response.failure("Invalid queue status format")
            else:
                response.failure(f"Get task status failed: {response.status_code}")

    @task(2)
    def integration_status(self):
        """Test integration status endpoints."""
        with self.client.get("/integrations/status", catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if 'integrations' in data and 'total_integrations' in data:
                    response.success()
                else:
                    response.failure("Invalid integration status format")
            else:
                response.failure(f"Get integration status failed: {response.status_code}")

    @task(1)
    def api_docs_access(self):
        """Test API documentation access."""
        with self.client.get("/docs", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"API docs access failed: {response.status_code}")

    @task(1)
    def openapi_schema(self):
        """Test OpenAPI schema access."""
        with self.client.get("/openapi.json", catch_response=True) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'paths' in data and 'components' in data:
                        response.success()
                    else:
                        response.failure("Invalid OpenAPI schema")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"OpenAPI schema access failed: {response.status_code}")


class GalionUser(HttpUser):
    """Load testing user for Galion API."""

    # Wait between 1-3 seconds between tasks
    wait_time = between(1, 3)

    # Tasks to perform
    tasks = [GalionAPITasks]

    # Request timeout
    timeout = 30

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_start_time = time.time()


class DataIntensiveUser(HttpUser):
    """User that performs data-intensive operations."""

    wait_time = between(2, 5)

    @task
    def large_task_creation(self):
        """Create tasks with large payloads."""
        large_data = {
            "description": "Data-intensive load test task",
            "priority": "normal",
            "requirements": ["data_processing", "analysis"],
            "metadata": {
                "load_test": True,
                "data_size": "large",
                "payload": "x" * 10000,  # 10KB of data
                "nested_data": {
                    "level1": {
                        "level2": {
                            "level3": list(range(100))
                        }
                    }
                }
            }
        }

        with self.client.post("/agents/execute", json=large_data, catch_response=True) as response:
            if response.status_code in [200, 201, 202]:
                response.success()
            elif response.elapsed.total_seconds() > 10:  # Timeout for large payloads
                response.failure("Large payload timeout")
            else:
                response.failure(f"Large task creation failed: {response.status_code}")


class BurstLoadUser(HttpUser):
    """User that creates burst loads."""

    wait_time = between(0.1, 0.5)  # Very fast requests

    @task
    def rapid_requests(self):
        """Make rapid requests to stress the system."""
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Burst request failed: {response.status_code}")


# Custom event handlers for monitoring
@events.request.add_listener
def on_request(request_type, name, response_time, response_length, response,
               context, exception, **kwargs):
    """Monitor individual requests."""
    if exception:
        # Log failures for analysis
        print(f"Request failed: {name} - {exception}")
    elif response and response.status_code >= 400:
        # Log errors
        print(f"Request error: {name} - {response.status_code}")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Setup when test starts."""
    print("🚀 Starting Galion load test")
    print(f"Target: {environment.host}")
    print(f"Users: {environment.parsed_options.num_users}")
    print(f"Spawn rate: {environment.parsed_options.spawn_rate}")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Cleanup when test stops."""
    print("✅ Load test completed")
    print("Generating performance report...")


@events.spawning_complete.add_listener
def on_spawning_complete(user_count, **kwargs):
    """Called when all users have spawned."""
    print(f"🎯 All {user_count} users spawned and active")


# Custom metrics and monitoring
class LoadTestMetrics:
    """Custom metrics for load testing."""

    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.response_times = []
        self.status_codes = {}

    def record_request(self, response_time: float, status_code: int, success: bool):
        """Record a request."""
        self.request_count += 1
        if not success:
            self.error_count += 1

        self.response_times.append(response_time)
        self.status_codes[status_code] = self.status_codes.get(status_code, 0) + 1

    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary."""
        if not self.response_times:
            return {}

        return {
            "total_requests": self.request_count,
            "error_count": self.error_count,
            "error_rate": (self.error_count / self.request_count * 100) if self.request_count > 0 else 0,
            "avg_response_time": sum(self.response_times) / len(self.response_times),
            "min_response_time": min(self.response_times),
            "max_response_time": max(self.response_times),
            "status_codes": self.status_codes
        }


# Global metrics instance
load_metrics = LoadTestMetrics()


@events.request.add_listener
def record_metrics(request_type, name, response_time, response_length, response,
                  context, exception, **kwargs):
    """Record custom metrics."""
    success = exception is None and (response.status_code < 400 if response else False)
    load_metrics.record_request(response_time, response.status_code if response else 0, success)


@events.test_stop.add_listener
def print_metrics(environment, **kwargs):
    """Print custom metrics summary."""
    summary = load_metrics.get_summary()
    if summary:
        print("\n📊 Load Test Metrics Summary")
        print("=" * 40)
        print(f"Total Requests: {summary['total_requests']}")
        print(".2f")
        print(".2f")
        print(".3f")
        print(".3f")
        print(".3f")
        print(f"Status Codes: {summary['status_codes']}")
        print("=" * 40)


# Test scenarios for different load patterns
class SteadyLoadTest:
    """Steady load test configuration."""

    def __init__(self):
        self.user_class = GalionUser
        self.spawn_rate = 10
        self.user_count = 100
        self.test_duration = 300  # 5 minutes


class SpikeLoadTest:
    """Spike load test configuration."""

    def __init__(self):
        self.user_class = BurstLoadUser
        self.spawn_rate = 50
        self.user_count = 200
        self.test_duration = 60  # 1 minute


class DataIntensiveLoadTest:
    """Data-intensive load test configuration."""

    def __init__(self):
        self.user_class = DataIntensiveUser
        self.spawn_rate = 5
        self.user_count = 50
        self.test_duration = 180  # 3 minutes


# Utility functions for running tests programmatically
def run_load_test_scenario(scenario_class, host: str = "http://localhost:8010"):
    """Run a specific load test scenario."""
    import subprocess
    import sys

    scenario = scenario_class()

    cmd = [
        sys.executable, "-m", "locust",
        "-f", __file__,
        "--host", host,
        "--users", str(scenario.user_count),
        "--spawn-rate", str(scenario.spawn_rate),
        "--run-time", f"{scenario.test_duration}s",
        "--headless",
        "--only-summary"
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=scenario.test_duration + 60)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Test timed out"


if __name__ == "__main__":
    # Allow running tests programmatically
    import sys

    if len(sys.argv) > 1:
        scenario_name = sys.argv[1]

        scenarios = {
            "steady": SteadyLoadTest,
            "spike": SpikeLoadTest,
            "data-intensive": DataIntensiveLoadTest
        }

        if scenario_name in scenarios:
            host = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:8010"
            success, stdout, stderr = run_load_test_scenario(scenarios[scenario_name], host)

            if success:
                print("✅ Load test completed successfully")
                print(stdout)
            else:
                print("❌ Load test failed")
                print(stderr)
                sys.exit(1)
        else:
            print(f"Unknown scenario: {scenario_name}")
            print(f"Available scenarios: {list(scenarios.keys())}")
            sys.exit(1)
    else:
        # Run with Locust UI
        print("Starting Locust UI...")
        print("Open http://localhost:8089 to access the web interface")
        print("Available user classes: GalionUser, DataIntensiveUser, BurstLoadUser")
