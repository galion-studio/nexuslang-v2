#!/usr/bin/env python3
"""
Performance Benchmark Script

This script runs comprehensive performance benchmarks on your
Galion autonomous agent system to measure:
- Response times
- Throughput
- Resource usage
- Scalability
"""

import requests
import json
import time
import threading
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any, Optional
import psutil
import os

# Configuration
BASE_URL = "http://localhost:8010"
TIMEOUT = 120  # seconds for complex tasks
CONCURRENT_USERS = 5  # simultaneous users
TEST_DURATION = 60  # seconds for load testing

class PerformanceBenchmark:
    """Performance benchmarking class."""

    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.response_times: List[float] = []
        self.errors: List[str] = []
        self.start_time = 0
        self.end_time = 0

    def make_request(self, method: str, endpoint: str, data: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Make an HTTP request and measure response time."""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()

        try:
            if method.upper() == "GET":
                response = requests.get(url, timeout=TIMEOUT)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, timeout=TIMEOUT)
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()
            result = response.json()

            # Record response time
            response_time = time.time() - start_time
            self.response_times.append(response_time)

            return result

        except Exception as e:
            response_time = time.time() - start_time
            self.response_times.append(response_time)
            self.errors.append(str(e))
            return None

    def benchmark_health_check(self, iterations: int = 100) -> Dict[str, Any]:
        """Benchmark basic health check endpoint."""
        print(f"🔄 Running health check benchmark ({iterations} iterations)...")

        self.response_times = []
        self.errors = []

        for i in range(iterations):
            self.make_request("GET", "/health")

        return self._calculate_stats("Health Check")

    def benchmark_simple_tasks(self, iterations: int = 10) -> Dict[str, Any]:
        """Benchmark simple task execution."""
        print(f"🔄 Running simple task benchmark ({iterations} iterations)...")

        self.response_times = []
        self.errors = []

        simple_tasks = [
            "Write a Python function to reverse a string",
            "Create a JavaScript function to check if a number is prime",
            "Write a SQL query to find users created in the last 30 days",
            "Create a CSS class for a responsive card component"
        ]

        for i in range(iterations):
            task_data = {
                "prompt": simple_tasks[i % len(simple_tasks)],
                "require_approval": False
            }

            task_result = self.make_request("POST", "/api/v1/agents/execute", task_data)

            if task_result and "task_id" in task_result:
                task_id = task_result["task_id"]

                # Wait for completion (with timeout)
                start_wait = time.time()
                while time.time() - start_wait < 30:  # 30 second timeout
                    status_result = self.make_request("GET", f"/api/v1/agents/status/{task_id}")
                    if status_result and status_result.get("status") in ["completed", "failed"]:
                        break
                    time.sleep(1)

        return self._calculate_stats("Simple Tasks")

    def benchmark_concurrent_load(self, concurrent_users: int = CONCURRENT_USERS, duration: int = TEST_DURATION) -> Dict[str, Any]:
        """Benchmark concurrent load handling."""
        print(f"🔄 Running concurrent load test ({concurrent_users} users, {duration}s)...")

        self.response_times = []
        self.errors = []

        def user_simulation(user_id: int):
            """Simulate a single user making requests."""
            end_time = time.time() + duration

            while time.time() < end_time:
                # Mix of health checks and simple tasks
                if user_id % 3 == 0:
                    self.make_request("GET", "/health")
                else:
                    task_data = {
                        "prompt": f"Write a hello world function in Python - user {user_id}",
                        "require_approval": False
                    }
                    task_result = self.make_request("POST", "/api/v1/agents/execute", task_data)

                    if task_result and "task_id" in task_result:
                        # Don't wait for completion in load test
                        pass

                # Random delay between requests (0.1-1 second)
                time.sleep(0.1 + (user_id * 0.1) % 0.9)

        # Run concurrent users
        threads = []
        for user_id in range(concurrent_users):
            thread = threading.Thread(target=user_simulation, args=(user_id,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        return self._calculate_stats("Concurrent Load")

    def benchmark_complex_tasks(self, iterations: int = 3) -> Dict[str, Any]:
        """Benchmark complex multi-step tasks."""
        print(f"🔄 Running complex task benchmark ({iterations} iterations)...")

        self.response_times = []
        self.errors = []

        complex_tasks = [
            {
                "prompt": "Build a complete REST API for a blog system with posts, comments, and user authentication",
                "context": {"tech_stack": ["Node.js", "Express", "MongoDB", "JWT"]},
                "require_approval": False
            },
            {
                "prompt": "Create a data visualization dashboard for sales analytics with multiple chart types",
                "context": {"framework": "React", "charts": ["Chart.js", "D3.js"], "data_source": "REST API"},
                "require_approval": False
            },
            {
                "prompt": "Design and implement a microservices architecture for an e-commerce platform",
                "context": {"services": ["user", "product", "order", "payment", "notification"], "deployment": "Docker"},
                "require_approval": False
            }
        ]

        for i in range(iterations):
            task_data = complex_tasks[i % len(complex_tasks)]

            task_result = self.make_request("POST", "/api/v1/agents/execute", task_data)

            if task_result and "task_id" in task_result:
                task_id = task_result["task_id"]

                # Wait for completion (longer timeout for complex tasks)
                start_wait = time.time()
                while time.time() - start_wait < 120:  # 2 minute timeout
                    status_result = self.make_request("GET", f"/api/v1/agents/status/{task_id}")
                    if status_result and status_result.get("status") in ["completed", "failed"]:
                        break
                    time.sleep(2)

        return self._calculate_stats("Complex Tasks")

    def monitor_system_resources(self) -> Dict[str, Any]:
        """Monitor system resource usage."""
        print("🔄 Monitoring system resources...")

        # Get CPU and memory usage
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        # Get process info if available
        process_info = {}
        try:
            current_process = psutil.Process(os.getpid())
            process_info = {
                "cpu_percent": current_process.cpu_percent(),
                "memory_mb": current_process.memory_info().rss / 1024 / 1024,
                "threads": current_process.num_threads()
            }
        except:
            pass

        return {
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used_gb": memory.used / 1024 / 1024 / 1024,
                "memory_total_gb": memory.total / 1024 / 1024 / 1024,
                "disk_percent": disk.percent,
                "disk_used_gb": disk.used / 1024 / 1024 / 1024,
                "disk_total_gb": disk.total / 1024 / 1024 / 1024
            },
            "process": process_info
        }

    def _calculate_stats(self, test_name: str) -> Dict[str, Any]:
        """Calculate statistics for a test."""
        if not self.response_times:
            return {
                "test": test_name,
                "error": "No response times recorded"
            }

        return {
            "test": test_name,
            "total_requests": len(self.response_times),
            "errors": len(self.errors),
            "success_rate": ((len(self.response_times) - len(self.errors)) / len(self.response_times)) * 100,
            "response_time": {
                "min": min(self.response_times),
                "max": max(self.response_times),
                "avg": statistics.mean(self.response_times),
                "median": statistics.median(self.response_times),
                "p95": statistics.quantiles(self.response_times, n=20)[18] if len(self.response_times) >= 20 else max(self.response_times),
                "p99": statistics.quantiles(self.response_times, n=100)[98] if len(self.response_times) >= 100 else max(self.response_times)
            }
        }

def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{'='*80}")
    print(f" {text}")
    print(f"{'='*80}")

def print_stats(stats: Dict[str, Any]):
    """Print formatted statistics."""
    if "error" in stats:
        print(f"❌ {stats['test']}: {stats['error']}")
        return

    print(f"\n📊 {stats['test']} Results:")
    print(f"   Total Requests: {stats['total_requests']}")
    print(f"   Errors: {stats['errors']}")
    print(".1f")
    print("   Response Time (seconds):"
    rt = stats['response_time']
    print(".3f")
    print(".3f")
    print(".3f")
    print(".3f")
    print(".3f")
    print(".3f")

def print_system_resources(resources: Dict[str, Any]):
    """Print system resource usage."""
    print("
💻 System Resources:"    sys = resources['system']
    print(".1f"    print(".1f"    print(".1f"    print(".1f"

    if resources['process']:
        proc = resources['process']
        print("
🔧 Process Resources:"        print(".1f"        print(".1f"        print(f"   Threads: {proc['threads']}")

def main():
    """Main benchmark function."""
    print("🚀 GALION PERFORMANCE BENCHMARK")
    print("="*80)
    print(f"Target System: {BASE_URL}")
    print("This benchmark will test various aspects of your system performance.")
    print("Make sure your Galion system is running before proceeding!")
    print("="*80)

    # Test connection first
    print("\n🔍 Testing connection...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            raise Exception("Bad status code")
        print("✅ Connection successful!")
    except Exception as e:
        print(f"❌ Cannot connect to Galion system: {e}")
        print("Please start your system first: python main.py")
        return

    benchmark = PerformanceBenchmark()

    # Get initial system resources
    initial_resources = benchmark.monitor_system_resources()
    print_system_resources(initial_resources)

    # Run benchmarks
    results = []

    try:
        # Health check benchmark
        results.append(benchmark.benchmark_health_check(iterations=50))

        # Simple tasks benchmark
        results.append(benchmark.benchmark_simple_tasks(iterations=5))

        # Complex tasks benchmark
        results.append(benchmark.benchmark_complex_tasks(iterations=2))

        # Concurrent load test
        results.append(benchmark.benchmark_concurrent_load(
            concurrent_users=CONCURRENT_USERS,
            duration=TEST_DURATION
        ))

    except KeyboardInterrupt:
        print("\n\n⚠️  Benchmark interrupted by user.")
        return

    # Get final system resources
    final_resources = benchmark.monitor_system_resources()

    # Print results
    print_header("BENCHMARK RESULTS")

    for result in results:
        print_stats(result)

    print_system_resources(final_resources)

    # Overall assessment
    print_header("PERFORMANCE ASSESSMENT")

    total_requests = sum(r['total_requests'] for r in results if 'total_requests' in r)
    total_errors = sum(r['errors'] for r in results if 'errors' in r)
    avg_response_times = [r['response_time']['avg'] for r in results if 'response_time' in r]

    if avg_response_times:
        overall_success_rate = ((total_requests - total_errors) / total_requests) * 100 if total_requests > 0 else 0
        overall_avg_response = statistics.mean(avg_response_times)

        print(".1f"        print(".3f"
        if overall_success_rate >= 95 and overall_avg_response < 5:
            print("🎉 Excellent performance! Your system is production-ready.")
        elif overall_success_rate >= 90 and overall_avg_response < 10:
            print("✅ Good performance! Minor optimizations may help.")
        elif overall_success_rate >= 80:
            print("⚠️  Acceptable performance. Consider optimizations for production.")
        else:
            print("❌ Performance issues detected. Check system configuration.")

    print("\n💡 Optimization Tips:")
    print("• Increase concurrent_users for higher throughput testing")
    print("• Add more agents for better parallel processing")
    print("• Optimize database queries and caching")
    print("• Consider horizontal scaling for production loads")
    print("• Monitor memory usage during extended runs")

if __name__ == "__main__":
    main()
