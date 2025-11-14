"""
Load testing framework for Deep Search.
Simulates high-concurrency scenarios and measures system performance.
"""

import asyncio
import aiohttp
import time
import statistics
from typing import Dict, List, Any, Optional, Callable, AsyncGenerator
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
import logging
import random
from collections import defaultdict, deque

from ...core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class LoadTestConfig:
    """Configuration for a load test."""
    name: str
    description: str = ""
    test_type: str = "volume"  # volume, spike, stress, endurance, ramp
    duration_seconds: int = 300  # 5 minutes default
    concurrent_users: int = 10
    ramp_up_seconds: int = 30
    ramp_down_seconds: int = 30
    target_url: str = ""
    api_key: str = ""
    user_agents: Optional[List[str]] = None

    # Test-specific parameters
    requests_per_minute: int = 60  # For volume testing
    spike_multiplier: float = 5.0  # For spike testing
    spike_duration: int = 60  # Spike duration in seconds
    stress_cpu_threshold: float = 80.0  # CPU threshold for stress testing
    memory_threshold_mb: int = 512  # Memory threshold for stress testing

    # Request patterns
    request_weights: Optional[Dict[str, float]] = None  # endpoint -> weight
    custom_headers: Optional[Dict[str, str]] = None

    def __post_init__(self):
        if self.user_agents is None:
            self.user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1",
                "Mozilla/5.0 (Android 11; Mobile; rv:68.0) Gecko/68.0 Firefox/88.0"
            ]

        if self.request_weights is None:
            self.request_weights = {
                "/api/v2/ai/chat": 0.4,
                "/api/v2/grokopedia/deep-research": 0.3,
                "/api/v2/research/history": 0.1,
                "/api/v2/voice/transcribe": 0.1,
                "/api/v2/language/translate": 0.1
            }

        if self.custom_headers is None:
            self.custom_headers = {}


@dataclass
class RequestMetrics:
    """Metrics for a single request."""
    timestamp: float
    endpoint: str
    method: str
    status_code: int
    response_time: float
    response_size: int
    success: bool
    error_message: Optional[str] = None
    user_id: Optional[str] = None


@dataclass
class LoadTestResults:
    """Results of a load test."""
    test_id: str
    config: LoadTestConfig
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: float = 0.0

    # Request metrics
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    error_rate: float = 0.0

    # Response time metrics
    response_times: List[float] = None
    avg_response_time: float = 0.0
    min_response_time: float = 0.0
    max_response_time: float = 0.0
    p50_response_time: float = 0.0
    p95_response_time: float = 0.0
    p99_response_time: float = 0.0

    # Throughput metrics
    requests_per_second: float = 0.0
    throughput_over_time: List[Dict[str, Any]] = None

    # Error analysis
    error_breakdown: Dict[str, int] = None
    error_samples: List[Dict[str, Any]] = None

    # Resource usage (if available)
    system_metrics: List[Dict[str, Any]] = None

    # Performance thresholds
    met_thresholds: bool = True
    threshold_violations: List[str] = None

    def __post_init__(self):
        if self.response_times is None:
            self.response_times = []
        if self.throughput_over_time is None:
            self.throughput_over_time = []
        if self.error_breakdown is None:
            self.error_breakdown = defaultdict(int)
        if self.error_samples is None:
            self.error_samples = []
        if self.system_metrics is None:
            self.system_metrics = []
        if self.threshold_violations is None:
            self.threshold_violations = []


class LoadTester:
    """
    Comprehensive load testing framework for Deep Search.

    Features:
    - Multiple test types (volume, spike, stress, endurance, ramp)
    - Realistic user simulation with varied request patterns
    - Detailed performance metrics and analysis
    - Integration with performance monitoring
    - Automated threshold checking and alerting
    """

    def __init__(self, base_url: str = None, api_key: str = None):
        self.base_url = base_url or settings.API_BASE_URL
        self.api_key = api_key or settings.API_KEY
        self.active_tests = {}
        self.results_history = {}

        # Default performance thresholds
        self.performance_thresholds = {
            "max_response_time": 5.0,  # seconds
            "max_error_rate": 0.05,    # 5%
            "min_requests_per_second": 10.0,
            "max_cpu_usage": 80.0,     # percentage
            "max_memory_usage": 80.0   # percentage
        }

        # Test scenarios for different endpoints
        self.test_scenarios = self._initialize_scenarios()

    def _initialize_scenarios(self) -> Dict[str, Dict[str, Any]]:
        """Initialize test scenarios for different endpoints."""
        return {
            "/api/v2/ai/chat": {
                "method": "POST",
                "payload_generator": self._generate_chat_payload,
                "expected_status": 200,
                "timeout": 30.0
            },
            "/api/v2/grokopedia/deep-research": {
                "method": "POST",
                "payload_generator": self._generate_research_payload,
                "expected_status": 200,
                "timeout": 60.0
            },
            "/api/v2/research/history": {
                "method": "GET",
                "payload_generator": self._generate_history_payload,
                "expected_status": 200,
                "timeout": 10.0
            },
            "/api/v2/voice/transcribe": {
                "method": "POST",
                "payload_generator": self._generate_voice_payload,
                "expected_status": 200,
                "timeout": 20.0
            },
            "/api/v2/language/translate": {
                "method": "POST",
                "payload_generator": self._generate_translate_payload,
                "expected_status": 200,
                "timeout": 15.0
            }
        }

    async def run_load_test(self, config: LoadTestConfig) -> LoadTestResults:
        """
        Run a load test with the specified configuration.

        Args:
            config: Load test configuration

        Returns:
            Comprehensive test results
        """
        test_id = f"test_{int(time.time())}_{config.name.replace(' ', '_').lower()}"
        logger.info(f"Starting load test: {config.name} (ID: {test_id})")

        results = LoadTestResults(
            test_id=test_id,
            config=config,
            start_time=datetime.utcnow()
        )

        self.active_tests[test_id] = results

        try:
            # Run the appropriate test type
            if config.test_type == "volume":
                await self._run_volume_test(results)
            elif config.test_type == "spike":
                await self._run_spike_test(results)
            elif config.test_type == "stress":
                await self._run_stress_test(results)
            elif config.test_type == "endurance":
                await self._run_endurance_test(results)
            elif config.test_type == "ramp":
                await self._run_ramp_test(results)
            else:
                raise ValueError(f"Unknown test type: {config.test_type}")

            # Calculate final metrics
            self._calculate_final_metrics(results)

            # Check performance thresholds
            self._check_thresholds(results)

            logger.info(f"Load test completed: {config.name} - {results.successful_requests}/{results.total_requests} successful")

        except Exception as e:
            logger.error(f"Load test failed: {e}")
            results.error_breakdown["test_failure"] += 1
            results.threshold_violations.append(f"Test execution failed: {str(e)}")

        finally:
            results.end_time = datetime.utcnow()
            results.duration = (results.end_time - results.start_time).total_seconds()
            self.results_history[test_id] = results

        return results

    async def _run_volume_test(self, results: LoadTestResults):
        """Run a volume test with constant load."""
        config = results.config
        start_time = time.time()
        end_time = start_time + config.duration_seconds

        # Calculate request timing
        requests_per_second = config.requests_per_minute / 60.0
        interval = 1.0 / requests_per_second if requests_per_second > 0 else 1.0

        request_times = []
        current_time = start_time

        while current_time < end_time:
            request_times.append(current_time)
            current_time += interval

        # Execute requests
        semaphore = asyncio.Semaphore(config.concurrent_users)

        async def execute_request(request_time: float):
            async with semaphore:
                # Wait until the scheduled time
                delay = max(0, request_time - time.time())
                await asyncio.sleep(delay)

                # Execute the request
                metrics = await self._execute_single_request(config)
                return metrics

        # Run all requests concurrently
        tasks = [execute_request(rt) for rt in request_times]
        request_metrics = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for metric in request_metrics:
            if isinstance(metric, Exception):
                results.error_breakdown["async_error"] += 1
                continue

            results.total_requests += 1
            results.response_times.append(metric.response_time)

            if metric.success:
                results.successful_requests += 1
            else:
                results.failed_requests += 1
                error_key = f"http_{metric.status_code}" if metric.status_code else "unknown_error"
                results.error_breakdown[error_key] += 1

                if len(results.error_samples) < 10:  # Limit error samples
                    results.error_samples.append({
                        "endpoint": metric.endpoint,
                        "status_code": metric.status_code,
                        "error_message": metric.error_message,
                        "response_time": metric.response_time
                    })

    async def _run_spike_test(self, results: LoadTestResults):
        """Run a spike test with sudden load increases."""
        config = results.config

        # Normal load period
        normal_requests_per_second = config.requests_per_minute / 60.0

        # Spike period
        spike_requests_per_second = normal_requests_per_second * config.spike_multiplier

        # Test phases
        phases = [
            {"duration": config.duration_seconds // 3, "rps": normal_requests_per_second, "name": "normal"},
            {"duration": config.spike_duration, "rps": spike_requests_per_second, "name": "spike"},
            {"duration": config.duration_seconds // 3, "rps": normal_requests_per_second, "name": "recovery"}
        ]

        for phase in phases:
            await self._run_test_phase(results, phase["duration"], phase["rps"], phase["name"])

    async def _run_stress_test(self, results: LoadTestResults):
        """Run a stress test that gradually increases load until system breaks."""
        config = results.config

        current_rps = 10.0  # Start low
        max_rps = 200.0     # Maximum to test
        increment = 10.0    # RPS increment per phase
        phase_duration = 60  # Seconds per phase

        while current_rps <= max_rps:
            logger.info(f"Stress test phase: {current_rps} RPS")
            await self._run_test_phase(results, phase_duration, current_rps, f"stress_{current_rps}")

            # Check if system is under too much stress
            if len(results.response_times) > 10:
                recent_responses = results.response_times[-10:]
                avg_response_time = statistics.mean(recent_responses)

                if avg_response_time > 10.0:  # Too slow
                    logger.warning(f"System under stress at {current_rps} RPS - stopping")
                    break

            current_rps += increment

    async def _run_endurance_test(self, results: LoadTestResults):
        """Run an endurance test with sustained load over time."""
        config = results.config

        # Run with constant load for the full duration
        requests_per_second = config.requests_per_minute / 60.0
        await self._run_test_phase(results, config.duration_seconds, requests_per_second, "endurance")

    async def _run_ramp_test(self, results: LoadTestResults):
        """Run a ramp test that gradually increases load."""
        config = results.config

        ramp_up_steps = 10
        ramp_down_steps = 5

        # Calculate RPS progression
        min_rps = 5.0
        max_rps = config.requests_per_minute / 60.0
        step_duration = config.ramp_up_seconds / ramp_up_steps

        # Ramp up
        for step in range(ramp_up_steps):
            progress = (step + 1) / ramp_up_steps
            current_rps = min_rps + (max_rps - min_rps) * progress
            await self._run_test_phase(results, step_duration, current_rps, f"ramp_up_{step+1}")

        # Sustained load
        sustained_duration = config.duration_seconds - config.ramp_up_seconds - config.ramp_down_seconds
        if sustained_duration > 0:
            await self._run_test_phase(results, sustained_duration, max_rps, "sustained")

        # Ramp down
        if config.ramp_down_seconds > 0:
            step_duration = config.ramp_down_seconds / ramp_down_steps
            for step in range(ramp_down_steps, 0, -1):
                progress = step / ramp_down_steps
                current_rps = min_rps + (max_rps - min_rps) * progress
                await self._run_test_phase(results, step_duration, current_rps, f"ramp_down_{ramp_down_steps-step+1}")

    async def _run_test_phase(self, results: LoadTestResults, duration: float,
                             requests_per_second: float, phase_name: str):
        """Run a single test phase."""
        start_time = time.time()
        end_time = start_time + duration

        # Calculate request timing
        interval = 1.0 / requests_per_second if requests_per_second > 0 else 1.0

        request_times = []
        current_time = start_time

        while current_time < end_time:
            request_times.append(current_time)
            current_time += interval

        # Execute requests for this phase
        semaphore = asyncio.Semaphore(results.config.concurrent_users)

        async def execute_request(request_time: float):
            async with semaphore:
                delay = max(0, request_time - time.time())
                await asyncio.sleep(delay)

                metrics = await self._execute_single_request(results.config)
                return metrics

        tasks = [execute_request(rt) for rt in request_times]
        request_metrics = await asyncio.gather(*tasks, return_exceptions=True)

        # Process phase results
        for metric in request_metrics:
            if isinstance(metric, Exception):
                results.error_breakdown["async_error"] += 1
                continue

            results.total_requests += 1
            results.response_times.append(metric.response_time)

            if metric.success:
                results.successful_requests += 1
            else:
                results.failed_requests += 1
                error_key = f"http_{metric.status_code}" if metric.status_code else "unknown_error"
                results.error_breakdown[error_key] += 1

    async def _execute_single_request(self, config: LoadTestConfig) -> RequestMetrics:
        """Execute a single HTTP request and collect metrics."""
        # Select random endpoint based on weights
        endpoint = random.choices(
            list(config.request_weights.keys()),
            weights=list(config.request_weights.values())
        )[0]

        scenario = self.test_scenarios.get(endpoint, {})
        if not scenario:
            # Fallback for unknown endpoints
            scenario = {
                "method": "GET",
                "payload_generator": lambda: {},
                "expected_status": 200,
                "timeout": 10.0
            }

        method = scenario["method"]
        payload = scenario["payload_generator"]()
        expected_status = scenario["expected_status"]
        timeout = scenario.get("timeout", 10.0)

        # Generate headers
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": random.choice(config.user_agents)
        }
        headers.update(config.custom_headers)

        start_time = time.time()
        success = False
        status_code = 0
        response_size = 0
        error_message = None

        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
                url = f"{self.base_url}{endpoint}"

                if method == "GET":
                    async with session.get(url, headers=headers) as response:
                        status_code = response.status
                        response_text = await response.text()
                        response_size = len(response_text)

                elif method == "POST":
                    async with session.post(url, json=payload, headers=headers) as response:
                        status_code = response.status
                        response_text = await response.text()
                        response_size = len(response_text)

                success = status_code == expected_status

        except asyncio.TimeoutError:
            error_message = "Request timeout"
            status_code = 408
        except aiohttp.ClientError as e:
            error_message = f"Client error: {str(e)}"
            status_code = 0
        except Exception as e:
            error_message = f"Unexpected error: {str(e)}"
            status_code = 0

        response_time = time.time() - start_time

        return RequestMetrics(
            timestamp=start_time,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            response_time=response_time,
            response_size=response_size,
            success=success,
            error_message=error_message,
            user_id=f"user_{random.randint(1, 1000)}"  # Simulated user ID
        )

    def _calculate_final_metrics(self, results: LoadTestResults):
        """Calculate final metrics from collected data."""
        if not results.response_times:
            return

        # Response time statistics
        results.avg_response_time = statistics.mean(results.response_times)
        results.min_response_time = min(results.response_times)
        results.max_response_time = max(results.response_times)

        if len(results.response_times) >= 2:
            results.p50_response_time = statistics.median(results.response_times)
            results.p95_response_time = statistics.quantiles(results.response_times, n=20)[18]  # 95th percentile
            results.p99_response_time = statistics.quantiles(results.response_times, n=100)[98]  # 99th percentile

        # Throughput
        if results.duration > 0:
            results.requests_per_second = results.total_requests / results.duration

        # Error rate
        if results.total_requests > 0:
            results.error_rate = results.failed_requests / results.total_requests

    def _check_thresholds(self, results: LoadTestResults):
        """Check if performance thresholds were met."""
        violations = []

        if results.avg_response_time > self.performance_thresholds["max_response_time"]:
            violations.append(".2f")

        if results.error_rate > self.performance_thresholds["max_error_rate"]:
            violations.append(".1%")

        if results.requests_per_second < self.performance_thresholds["min_requests_per_second"]:
            violations.append(".1f")

        results.threshold_violations = violations
        results.met_thresholds = len(violations) == 0

    # Payload generators for different endpoints

    def _generate_chat_payload(self) -> Dict[str, Any]:
        """Generate a realistic chat payload."""
        messages = [
            {"role": "user", "content": "Explain quantum computing in simple terms"}
        ]
        return {
            "messages": messages,
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 500
        }

    def _generate_research_payload(self) -> Dict[str, Any]:
        """Generate a realistic deep research payload."""
        queries = [
            "What are the latest developments in artificial intelligence?",
            "How does machine learning work?",
            "What are the benefits of renewable energy?",
            "Explain blockchain technology",
            "What is the future of quantum computing?"
        ]

        return {
            "query": random.choice(queries),
            "persona": random.choice(["default", "technical", "isaac"]),
            "depth": random.choice(["quick", "comprehensive", "exhaustive"]),
            "include_sources": random.choice([True, False]),
            "max_sources": random.randint(5, 15)
        }

    def _generate_history_payload(self) -> Dict[str, Any]:
        """Generate a research history payload."""
        return {
            "user_id": f"user_{random.randint(1, 1000)}",
            "limit": 10,
            "offset": 0
        }

    def _generate_voice_payload(self) -> Dict[str, Any]:
        """Generate a voice transcription payload."""
        return {
            "audio_data": "base64_encoded_audio_data_placeholder",
            "language": random.choice(["en", "es", "fr", "de", "zh"]),
            "format": "wav"
        }

    def _generate_translate_payload(self) -> Dict[str, Any]:
        """Generate a translation payload."""
        return {
            "text": "Hello, how are you today?",
            "source_language": "en",
            "target_language": random.choice(["es", "fr", "de", "zh", "ja"]),
            "preserve_formatting": True
        }

    def get_test_history(self) -> List[Dict[str, Any]]:
        """Get history of all completed load tests."""
        return [
            {
                "test_id": test_id,
                "name": results.config.name,
                "type": results.config.test_type,
                "start_time": results.start_time.isoformat(),
                "duration": results.duration,
                "total_requests": results.total_requests,
                "successful_requests": results.successful_requests,
                "avg_response_time": results.avg_response_time,
                "error_rate": results.error_rate,
                "met_thresholds": results.met_thresholds
            }
            for test_id, results in self.results_history.items()
        ]

    def get_performance_thresholds(self) -> Dict[str, float]:
        """Get current performance thresholds."""
        return self.performance_thresholds.copy()

    def update_performance_thresholds(self, thresholds: Dict[str, float]):
        """Update performance thresholds."""
        self.performance_thresholds.update(thresholds)
        logger.info(f"Updated performance thresholds: {thresholds}")

    def generate_test_report(self, test_id: str) -> Optional[Dict[str, Any]]:
        """Generate a detailed test report."""
        if test_id not in self.results_history:
            return None

        results = self.results_history[test_id]

        report = {
            "test_id": test_id,
            "configuration": asdict(results.config),
            "summary": {
                "duration": results.duration,
                "total_requests": results.total_requests,
                "successful_requests": results.successful_requests,
                "failed_requests": results.failed_requests,
                "error_rate": results.error_rate,
                "requests_per_second": results.requests_per_second
            },
            "response_time_metrics": {
                "average": results.avg_response_time,
                "minimum": results.min_response_time,
                "maximum": results.max_response_time,
                "p50": results.p50_response_time,
                "p95": results.p95_response_time,
                "p99": results.p99_response_time
            },
            "error_analysis": {
                "error_breakdown": dict(results.error_breakdown),
                "error_samples": results.error_samples[:5]  # Limit samples in report
            },
            "threshold_analysis": {
                "met_thresholds": results.met_thresholds,
                "violations": results.threshold_violations
            },
            "recommendations": self._generate_recommendations(results)
        }

        return report

    def _generate_recommendations(self, results: LoadTestResults) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []

        if results.avg_response_time > 2.0:
            recommendations.append("Consider implementing caching for frequently accessed endpoints")

        if results.error_rate > 0.01:
            recommendations.append("Investigate and fix the root causes of failed requests")

        if results.p95_response_time > 5.0:
            recommendations.append("Optimize database queries and consider connection pooling")

        if not results.met_thresholds:
            recommendations.append("Review and adjust performance thresholds based on system capabilities")

        if results.requests_per_second < 50:
            recommendations.append("Consider horizontal scaling or performance optimization")

        return recommendations
