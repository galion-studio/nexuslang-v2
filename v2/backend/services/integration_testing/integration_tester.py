"""
Integration testing framework for Deep Search.
End-to-end testing of complete user workflows and system integration.
"""

import asyncio
import aiohttp
import time
import json
import logging
from typing import Dict, List, Any, Optional, Callable, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import random
import uuid
from collections import defaultdict

from ...core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class TestScenario:
    """Represents a complete test scenario with multiple steps."""
    name: str
    description: str
    category: str  # research, collaboration, voice, multilingual, admin
    steps: List[Dict[str, Any]] = field(default_factory=list)
    setup_requirements: List[str] = field(default_factory=list)
    expected_outcomes: List[str] = field(default_factory=list)
    timeout_seconds: int = 300
    priority: str = "medium"  # high, medium, low


@dataclass
class TestStepResult:
    """Result of executing a single test step."""
    step_name: str
    step_type: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: float = 0.0
    success: bool = False
    response_data: Optional[Any] = None
    error_message: Optional[str] = None
    assertions_passed: List[str] = field(default_factory=list)
    assertions_failed: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IntegrationTestResult:
    """Complete result of an integration test."""
    test_id: str
    scenario: TestScenario
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: float = 0.0
    overall_success: bool = False
    step_results: List[TestStepResult] = field(default_factory=list)
    setup_success: bool = True
    teardown_success: bool = True
    test_data: Dict[str, Any] = field(default_factory=dict)  # Shared data between steps
    error_summary: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)


class IntegrationTester:
    """
    Comprehensive integration testing framework for Deep Search.

    Features:
    - End-to-end workflow testing
    - Cross-service integration validation
    - Realistic user journey simulation
    - Automated assertion checking
    - Performance monitoring during tests
    - Detailed reporting and analysis
    - Test data management and cleanup
    """

    def __init__(self, base_url: str = None, api_key: str = None):
        self.base_url = base_url or settings.API_BASE_URL
        self.api_key = api_key or settings.API_KEY
        self.active_tests = {}
        self.test_results = {}
        self.test_data_store = {}  # Store test data for cleanup

        # Initialize test scenarios
        self.test_scenarios = self._initialize_scenarios()

        # Session management for authenticated requests
        self.user_sessions = {}

    def _initialize_scenarios(self) -> Dict[str, TestScenario]:
        """Initialize comprehensive test scenarios for all major workflows."""
        return {
            "basic_research_workflow": TestScenario(
                name="Basic Research Workflow",
                description="Complete research workflow from query to results",
                category="research",
                setup_requirements=["authenticated_user"],
                expected_outcomes=[
                    "Research query processed successfully",
                    "Search results retrieved and analyzed",
                    "Response generated with proper citations",
                    "Research history saved"
                ],
                steps=[
                    {
                        "name": "deep_research_request",
                        "type": "api_call",
                        "endpoint": "/api/v2/grokopedia/deep-research",
                        "method": "POST",
                        "payload": {
                            "query": "What are the latest developments in artificial intelligence?",
                            "persona": "technical",
                            "depth": "comprehensive",
                            "include_sources": True
                        },
                        "assertions": [
                            {"type": "status_code", "expected": 200},
                            {"type": "response_time", "max_seconds": 30.0},
                            {"type": "json_field_exists", "field": "synthesized_answer"},
                            {"type": "json_field_exists", "field": "sources_used"},
                            {"type": "json_field_length", "field": "sources_used", "min_length": 3}
                        ]
                    },
                    {
                        "name": "verify_research_history",
                        "type": "api_call",
                        "endpoint": "/api/v2/research/history",
                        "method": "GET",
                        "assertions": [
                            {"type": "status_code", "expected": 200},
                            {"type": "json_field_exists", "field": "entries"},
                            {"type": "json_array_contains", "field": "entries", "contains_key": "query"}
                        ]
                    },
                    {
                        "name": "generate_citation",
                        "type": "api_call",
                        "endpoint": "/api/v2/citations/generate",
                        "method": "POST",
                        "payload": {
                            "source_data": {
                                "title": "Artificial Intelligence Advances",
                                "authors": ["John Smith", "Jane Doe"],
                                "year": 2024,
                                "publisher": "Tech Journal"
                            },
                            "style": "apa"
                        },
                        "assertions": [
                            {"type": "status_code", "expected": 200},
                            {"type": "json_field_exists", "field": "citation"}
                        ]
                    }
                ]
            ),

            "collaborative_research_session": TestScenario(
                name="Collaborative Research Session",
                description="Multi-user collaborative research workflow",
                category="collaboration",
                setup_requirements=["multiple_users", "websocket_support"],
                expected_outcomes=[
                    "Collaboration session created successfully",
                    "Multiple users can join session",
                    "Real-time updates shared between users",
                    "Session data persists correctly"
                ],
                steps=[
                    {
                        "name": "create_session",
                        "type": "api_call",
                        "endpoint": "/api/v2/collaboration/sessions",
                        "method": "POST",
                        "payload": {
                            "name": "AI Research Collaboration",
                            "description": "Team research on AI advancements",
                            "max_participants": 5
                        },
                        "assertions": [
                            {"type": "status_code", "expected": 200},
                            {"type": "json_field_exists", "field": "session_id"}
                        ]
                    },
                    {
                        "name": "join_session_user2",
                        "type": "api_call",
                        "endpoint": "/api/v2/collaboration/sessions/{session_id}/join",
                        "method": "POST",
                        "user": "user2",
                        "assertions": [
                            {"type": "status_code", "expected": 200},
                            {"type": "json_field_value", "field": "status", "expected": "joined"}
                        ]
                    },
                    {
                        "name": "update_session_data",
                        "type": "api_call",
                        "endpoint": "/api/v2/collaboration/sessions/{session_id}",
                        "method": "PUT",
                        "payload": {
                            "research_context": {
                                "current_topic": "Machine Learning Ethics",
                                "shared_findings": ["Finding 1", "Finding 2"]
                            }
                        },
                        "assertions": [
                            {"type": "status_code", "expected": 200}
                        ]
                    },
                    {
                        "name": "get_session_state",
                        "type": "api_call",
                        "endpoint": "/api/v2/collaboration/sessions/{session_id}",
                        "method": "GET",
                        "assertions": [
                            {"type": "status_code", "expected": 200},
                            {"type": "json_field_exists", "field": "participants"},
                            {"type": "json_field_exists", "field": "research_context"}
                        ]
                    }
                ]
            ),

            "voice_research_workflow": TestScenario(
                name="Voice Research Workflow",
                description="Complete voice-powered research interaction",
                category="voice",
                setup_requirements=["voice_api_access"],
                expected_outcomes=[
                    "Audio transcription works correctly",
                    "Voice query processed as text research",
                    "Audio response generated successfully",
                    "Voice session maintained properly"
                ],
                steps=[
                    {
                        "name": "transcribe_audio",
                        "type": "api_call",
                        "endpoint": "/api/v2/voice/transcribe",
                        "method": "POST",
                        "payload": {
                            "audio_data": "base64_encoded_audio_placeholder",
                            "language": "en",
                            "format": "wav"
                        },
                        "assertions": [
                            {"type": "status_code", "expected": 200},
                            {"type": "json_field_exists", "field": "transcription"},
                            {"type": "json_field_exists", "field": "confidence"}
                        ]
                    },
                    {
                        "name": "process_voice_query",
                        "type": "api_call",
                        "endpoint": "/api/v2/voice/query",
                        "method": "POST",
                        "payload": {
                            "transcription": "What are the benefits of renewable energy?",
                            "voice_preferences": {
                                "response_format": "audio",
                                "voice_type": "natural"
                            }
                        },
                        "assertions": [
                            {"type": "status_code", "expected": 200},
                            {"type": "json_field_exists", "field": "text_response"}
                        ]
                    },
                    {
                        "name": "generate_audio_response",
                        "type": "api_call",
                        "endpoint": "/api/v2/voice/synthesize",
                        "method": "POST",
                        "payload": {
                            "text": "Renewable energy provides clean power and reduces carbon emissions.",
                            "voice_type": "professional",
                            "language": "en"
                        },
                        "assertions": [
                            {"type": "status_code", "expected": 200},
                            {"type": "response_header_exists", "header": "content-type"},
                            {"type": "response_size", "min_bytes": 1000}
                        ]
                    }
                ]
            ),

            "multilingual_research_workflow": TestScenario(
                name="Multilingual Research Workflow",
                description="Research across multiple languages with translation",
                category="multilingual",
                setup_requirements=["translation_api_access"],
                expected_outcomes=[
                    "Text translation works in both directions",
                    "Research conducted in target language",
                    "Results translated back to source language",
                    "Cultural context preserved in translations"
                ],
                steps=[
                    {
                        "name": "translate_query",
                        "type": "api_call",
                        "endpoint": "/api/v2/language/translate",
                        "method": "POST",
                        "payload": {
                            "text": "How does quantum computing work?",
                            "source_language": "en",
                            "target_language": "es",
                            "preserve_formatting": True
                        },
                        "assertions": [
                            {"type": "status_code", "expected": 200},
                            {"type": "json_field_exists", "field": "translated_text"},
                            {"type": "json_field_exists", "field": "confidence"}
                        ]
                    },
                    {
                        "name": "research_in_target_language",
                        "type": "api_call",
                        "endpoint": "/api/v2/grokopedia/deep-research",
                        "method": "POST",
                        "payload": {
                            "query": "¿Cómo funciona la computación cuántica?",
                            "persona": "technical",
                            "depth": "comprehensive",
                            "language": "es"
                        },
                        "assertions": [
                            {"type": "status_code", "expected": 200},
                            {"type": "json_field_exists", "field": "synthesized_answer"}
                        ]
                    },
                    {
                        "name": "translate_results_back",
                        "type": "api_call",
                        "endpoint": "/api/v2/language/translate",
                        "method": "POST",
                        "payload": {
                            "text": "{previous_response.synthesized_answer}",
                            "source_language": "es",
                            "target_language": "en"
                        },
                        "assertions": [
                            {"type": "status_code", "expected": 200},
                            {"type": "json_field_exists", "field": "translated_text"}
                        ]
                    }
                ]
            ),

            "admin_workflow_management": TestScenario(
                name="Admin Workflow Management",
                description="Administrative management of system workflows",
                category="admin",
                setup_requirements=["admin_user"],
                expected_outcomes=[
                    "User management functions work correctly",
                    "System analytics accessible",
                    "Configuration changes applied",
                    "Audit logs maintained"
                ],
                steps=[
                    {
                        "name": "get_system_analytics",
                        "type": "api_call",
                        "endpoint": "/api/v2/analytics/summary",
                        "method": "GET",
                        "assertions": [
                            {"type": "status_code", "expected": 200},
                            {"type": "json_field_exists", "field": "usage_stats"},
                            {"type": "json_field_exists", "field": "performance_metrics"}
                        ]
                    },
                    {
                        "name": "create_custom_persona",
                        "type": "api_call",
                        "endpoint": "/api/v2/personas/create",
                        "method": "POST",
                        "payload": {
                            "name": "Test Persona",
                            "description": "Test custom persona for integration testing",
                            "configuration": {
                                "writing_style": "formal",
                                "tone": "professional",
                                "specializations": ["technology", "science"]
                            }
                        },
                        "assertions": [
                            {"type": "status_code", "expected": 200},
                            {"type": "json_field_exists", "field": "persona_id"}
                        ]
                    },
                    {
                        "name": "run_ab_test",
                        "type": "api_call",
                        "endpoint": "/api/v2/ab-testing/tests",
                        "method": "POST",
                        "payload": {
                            "name": "Integration Test A/B",
                            "test_type": "ui_variation",
                            "variants": [
                                {"id": "control", "name": "Control UI", "is_control": True},
                                {"id": "variant", "name": "New UI", "is_control": False}
                            ]
                        },
                        "assertions": [
                            {"type": "status_code", "expected": 200},
                            {"type": "json_field_exists", "field": "test_id"}
                        ]
                    },
                    {
                        "name": "check_error_logs",
                        "type": "api_call",
                        "endpoint": "/api/v2/errors/logs",
                        "method": "GET",
                        "query_params": {"limit": 10},
                        "assertions": [
                            {"type": "status_code", "expected": 200},
                            {"type": "json_field_exists", "field": "logs"}
                        ]
                    }
                ]
            ),

            "performance_and_load_integration": TestScenario(
                name="Performance and Load Integration",
                description="Integration testing of performance monitoring and load handling",
                category="performance",
                setup_requirements=["performance_monitoring_enabled"],
                expected_outcomes=[
                    "Performance metrics collected correctly",
                    "Load testing integrates with monitoring",
                    "Rate limiting works as expected",
                    "Caching improves performance"
                ],
                steps=[
                    {
                        "name": "check_performance_metrics",
                        "type": "api_call",
                        "endpoint": "/api/v2/performance/metrics",
                        "method": "GET",
                        "assertions": [
                            {"type": "status_code", "expected": 200},
                            {"type": "json_field_exists", "field": "response_times"},
                            {"type": "json_field_exists", "field": "resource_usage"}
                        ]
                    },
                    {
                        "name": "test_rate_limiting",
                        "type": "api_call_multiple",
                        "endpoint": "/api/v2/ai/chat",
                        "method": "POST",
                        "count": 15,  # Exceed rate limit
                        "delay_between_calls": 0.1,
                        "payload": {
                            "messages": [{"role": "user", "content": "Hello"}],
                            "model": "gpt-4"
                        },
                        "assertions": [
                            {"type": "some_requests_fail", "expected_status": 429},
                            {"type": "response_time_variation", "max_coefficient": 2.0}
                        ]
                    },
                    {
                        "name": "test_caching_behavior",
                        "type": "api_call_sequence",
                        "calls": [
                            {
                                "name": "first_call",
                                "endpoint": "/api/v2/grokopedia/deep-research",
                                "method": "POST",
                                "payload": {"query": "What is machine learning?", "depth": "quick"}
                            },
                            {
                                "name": "cached_call",
                                "endpoint": "/api/v2/grokopedia/deep-research",
                                "method": "POST",
                                "payload": {"query": "What is machine learning?", "depth": "quick"}
                            }
                        ],
                        "assertions": [
                            {"type": "cached_call_faster", "min_speedup": 2.0},
                            {"type": "both_calls_succeed"}
                        ]
                    },
                    {
                        "name": "run_load_test_integration",
                        "type": "api_call",
                        "endpoint": "/api/v2/load-testing/run",
                        "method": "POST",
                        "payload": {
                            "name": "Integration Load Test",
                            "test_type": "volume",
                            "duration_seconds": 30,
                            "requests_per_minute": 60
                        },
                        "assertions": [
                            {"type": "status_code", "expected": 200},
                            {"type": "json_field_exists", "field": "test_id"}
                        ]
                    }
                ]
            )
        }

    async def run_integration_test(self, scenario_name: str, user_context: Optional[Dict[str, Any]] = None) -> IntegrationTestResult:
        """
        Run a complete integration test scenario.

        Args:
            scenario_name: Name of the scenario to run
            user_context: Optional user context for the test

        Returns:
            Complete test results
        """
        if scenario_name not in self.test_scenarios:
            raise ValueError(f"Unknown test scenario: {scenario_name}")

        scenario = self.test_scenarios[scenario_name]
        test_id = f"integration_test_{int(time.time())}_{scenario_name}"

        logger.info(f"Starting integration test: {scenario.name} (ID: {test_id})")

        result = IntegrationTestResult(
            test_id=test_id,
            scenario=scenario,
            start_time=datetime.utcnow(),
            test_data={"scenario_name": scenario_name}
        )

        self.active_tests[test_id] = result

        try:
            # Setup phase
            await self._setup_test_environment(result, user_context)

            if not result.setup_success:
                logger.error(f"Setup failed for test {test_id}")
                return result

            # Execute test steps
            for step_config in scenario.steps:
                step_result = await self._execute_test_step(step_config, result.test_data, user_context)
                result.step_results.append(step_result)

                if not step_result.success:
                    logger.warning(f"Step {step_result.step_name} failed in test {test_id}")
                    break

            # Teardown phase
            await self._teardown_test_environment(result)

            # Analyze results
            self._analyze_test_results(result)

        except Exception as e:
            logger.error(f"Integration test failed: {e}")
            result.error_summary["test_failure"] = str(e)

        finally:
            result.end_time = datetime.utcnow()
            result.duration = (result.end_time - result.start_time).total_seconds()
            self.test_results[test_id] = result

        logger.info(f"Integration test completed: {scenario.name} - {result.overall_success}")

        return result

    async def _setup_test_environment(self, result: IntegrationTestResult, user_context: Optional[Dict[str, Any]]) -> None:
        """Set up the test environment before running steps."""
        try:
            scenario = result.scenario

            # Create test users if needed
            if "authenticated_user" in scenario.setup_requirements:
                user_id = await self._create_test_user()
                result.test_data["user_id"] = user_id

            if "multiple_users" in scenario.setup_requirements:
                user_ids = []
                for i in range(3):  # Create 3 test users
                    user_id = await self._create_test_user(f"test_user_{i}")
                    user_ids.append(user_id)
                result.test_data["user_ids"] = user_ids

            if "admin_user" in scenario.setup_requirements:
                admin_id = await self._create_test_admin()
                result.test_data["admin_id"] = admin_id

            # Initialize any required services
            if "websocket_support" in scenario.setup_requirements:
                # Note: WebSocket testing would require additional setup
                result.test_data["websocket_enabled"] = True

            result.setup_success = True
            logger.info(f"Test environment setup completed for {result.scenario.name}")

        except Exception as e:
            logger.error(f"Test setup failed: {e}")
            result.setup_success = False
            result.error_summary["setup_error"] = str(e)

    async def _teardown_test_environment(self, result: IntegrationTestResult) -> None:
        """Clean up the test environment after test completion."""
        try:
            # Clean up test users
            if "user_id" in result.test_data:
                await self._cleanup_test_user(result.test_data["user_id"])

            if "user_ids" in result.test_data:
                for user_id in result.test_data["user_ids"]:
                    await self._cleanup_test_user(user_id)

            if "admin_id" in result.test_data:
                await self._cleanup_test_user(result.test_data["admin_id"])

            # Clean up test data
            if "session_id" in result.test_data:
                await self._cleanup_session(result.test_data["session_id"])

            result.teardown_success = True
            logger.info(f"Test environment cleanup completed for {result.scenario.name}")

        except Exception as e:
            logger.error(f"Test teardown failed: {e}")
            result.teardown_success = False
            result.error_summary["teardown_error"] = str(e)

    async def _execute_test_step(self, step_config: Dict[str, Any], test_data: Dict[str, Any],
                               user_context: Optional[Dict[str, Any]]) -> TestStepResult:
        """Execute a single test step."""
        step_result = TestStepResult(
            step_name=step_config["name"],
            step_type=step_config["type"],
            start_time=datetime.utcnow()
        )

        try:
            if step_config["type"] == "api_call":
                await self._execute_api_call_step(step_config, test_data, step_result)
            elif step_config["type"] == "api_call_multiple":
                await self._execute_multiple_api_calls_step(step_config, test_data, step_result)
            elif step_config["type"] == "api_call_sequence":
                await self._execute_api_sequence_step(step_config, test_data, step_result)
            else:
                raise ValueError(f"Unknown step type: {step_config['type']}")

            # Run assertions
            await self._run_assertions(step_config.get("assertions", []), step_result)

            step_result.success = len(step_result.assertions_failed) == 0

        except Exception as e:
            logger.error(f"Step execution failed: {e}")
            step_result.error_message = str(e)
            step_result.success = False

        finally:
            step_result.end_time = datetime.utcnow()
            step_result.duration = (step_result.end_time - step_result.start_time).total_seconds()

        return step_result

    async def _execute_api_call_step(self, step_config: Dict[str, Any], test_data: Dict[str, Any],
                                   step_result: TestStepResult) -> None:
        """Execute a single API call step."""
        endpoint = step_config["endpoint"]
        method = step_config["method"]

        # Replace placeholders in endpoint
        for key, value in test_data.items():
            endpoint = endpoint.replace(f"{{{key}}}", str(value))

        # Prepare payload
        payload = step_config.get("payload", {})
        if isinstance(payload, dict):
            # Replace placeholders in payload
            payload_str = json.dumps(payload)
            for key, value in test_data.items():
                payload_str = payload_str.replace(f"{{{key}}}", str(value))
            payload = json.loads(payload_str)

        # Prepare headers
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Determine user for request
        user_id = step_config.get("user", "default")
        if user_id != "default" and user_id in test_data.get("user_ids", []):
            headers["X-Test-User-ID"] = user_id

        # Execute request
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
            url = f"{self.base_url}{endpoint}"

            if method == "GET":
                query_params = step_config.get("query_params", {})
                async with session.get(url, headers=headers, params=query_params) as response:
                    step_result.response_data = await self._process_response(response)
            elif method == "POST":
                async with session.post(url, json=payload, headers=headers) as response:
                    step_result.response_data = await self._process_response(response)
            elif method == "PUT":
                async with session.put(url, json=payload, headers=headers) as response:
                    step_result.response_data = await self._process_response(response)
            elif method == "DELETE":
                async with session.delete(url, headers=headers) as response:
                    step_result.response_data = await self._process_response(response)

    async def _execute_multiple_api_calls_step(self, step_config: Dict[str, Any], test_data: Dict[str, Any],
                                             step_result: TestStepResult) -> None:
        """Execute multiple API calls in sequence."""
        count = step_config["count"]
        delay = step_config.get("delay_between_calls", 0.0)

        results = []
        for i in range(count):
            call_config = step_config.copy()
            call_config["name"] = f"{step_config['name']}_{i+1}"
            call_config["type"] = "api_call"

            call_result = await self._execute_test_step(call_config, test_data, None)
            results.append(call_result)

            if delay > 0:
                await asyncio.sleep(delay)

        step_result.response_data = results
        step_result.metadata["call_count"] = count
        step_result.metadata["individual_results"] = [r.__dict__ for r in results]

    async def _execute_api_sequence_step(self, step_config: Dict[str, Any], test_data: Dict[str, Any],
                                       step_result: TestStepResult) -> None:
        """Execute a sequence of API calls."""
        calls = step_config["calls"]
        results = {}

        for call_config in calls:
            call_name = call_config["name"]
            call_config_full = call_config.copy()
            call_config_full["type"] = "api_call"

            call_result = await self._execute_test_step(call_config_full, test_data, None)
            results[call_name] = call_result

        step_result.response_data = results
        step_result.metadata["sequence_results"] = {k: v.__dict__ for k, v in results.items()}

    async def _process_response(self, response: aiohttp.ClientResponse) -> Dict[str, Any]:
        """Process an HTTP response for testing."""
        try:
            response_data = await response.text()
            try:
                json_data = json.loads(response_data)
            except json.JSONDecodeError:
                json_data = {"raw_response": response_data}

            return {
                "status_code": response.status,
                "headers": dict(response.headers),
                "data": json_data,
                "response_size": len(response_data)
            }
        except Exception as e:
            return {
                "status_code": response.status,
                "error": str(e),
                "headers": dict(response.headers) if hasattr(response, 'headers') else {}
            }

    async def _run_assertions(self, assertions: List[Dict[str, Any]], step_result: TestStepResult) -> None:
        """Run assertions on step results."""
        for assertion in assertions:
            assertion_type = assertion["type"]

            try:
                if assertion_type == "status_code":
                    expected = assertion["expected"]
                    actual = step_result.response_data.get("status_code")
                    if actual == expected:
                        step_result.assertions_passed.append(f"Status code is {expected}")
                    else:
                        step_result.assertions_failed.append(f"Status code {actual} != {expected}")

                elif assertion_type == "response_time":
                    max_time = assertion["max_seconds"]
                    if step_result.duration <= max_time:
                        step_result.assertions_passed.append(f"Response time {step_result.duration:.2f}s <= {max_time}s")
                    else:
                        step_result.assertions_failed.append(f"Response time {step_result.duration:.2f}s > {max_time}s")

                elif assertion_type == "json_field_exists":
                    field = assertion["field"]
                    data = step_result.response_data.get("data", {})
                    if self._check_json_field_exists(data, field):
                        step_result.assertions_passed.append(f"JSON field '{field}' exists")
                    else:
                        step_result.assertions_failed.append(f"JSON field '{field}' missing")

                elif assertion_type == "json_field_value":
                    field = assertion["field"]
                    expected = assertion["expected"]
                    data = step_result.response_data.get("data", {})
                    actual = self._get_json_field_value(data, field)
                    if actual == expected:
                        step_result.assertions_passed.append(f"Field '{field}' = '{expected}'")
                    else:
                        step_result.assertions_failed.append(f"Field '{field}' = '{actual}' != '{expected}'")

                elif assertion_type == "json_array_contains":
                    field = assertion["field"]
                    contains_key = assertion["contains_key"]
                    data = step_result.response_data.get("data", {})
                    array_data = self._get_json_field_value(data, field)
                    if isinstance(array_data, list) and any(contains_key in str(item) for item in array_data):
                        step_result.assertions_passed.append(f"Array '{field}' contains items with '{contains_key}'")
                    else:
                        step_result.assertions_failed.append(f"Array '{field}' missing items with '{contains_key}'")

                elif assertion_type == "response_header_exists":
                    header = assertion["header"]
                    headers = step_result.response_data.get("headers", {})
                    if header.lower() in [h.lower() for h in headers.keys()]:
                        step_result.assertions_passed.append(f"Response header '{header}' exists")
                    else:
                        step_result.assertions_failed.append(f"Response header '{header}' missing")

                elif assertion_type == "some_requests_fail":
                    # For multiple calls, check that some failed with expected status
                    expected_status = assertion["expected_status"]
                    if isinstance(step_result.response_data, list):
                        failed_count = sum(1 for r in step_result.response_data
                                         if r.response_data.get("status_code") == expected_status)
                        if failed_count > 0:
                            step_result.assertions_passed.append(f"{failed_count} requests failed with status {expected_status}")
                        else:
                            step_result.assertions_failed.append(f"No requests failed with status {expected_status}")

                # Add more assertion types as needed...

            except Exception as e:
                step_result.assertions_failed.append(f"Assertion error: {str(e)}")

    def _check_json_field_exists(self, data: Any, field_path: str) -> bool:
        """Check if a field exists in JSON data (supports nested paths)."""
        try:
            keys = field_path.split('.')
            current = data
            for key in keys:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    return False
            return True
        except:
            return False

    def _get_json_field_value(self, data: Any, field_path: str) -> Any:
        """Get a field value from JSON data (supports nested paths)."""
        try:
            keys = field_path.split('.')
            current = data
            for key in keys:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    return None
            return current
        except:
            return None

    async def _create_test_user(self, username: str = None) -> str:
        """Create a test user for integration testing."""
        # This would typically call your user creation API
        # For now, return a mock user ID
        user_id = str(uuid.uuid4())
        self.test_data_store[user_id] = {"type": "user", "username": username or f"test_user_{user_id}"}
        return user_id

    async def _create_test_admin(self) -> str:
        """Create a test admin user."""
        admin_id = str(uuid.uuid4())
        self.test_data_store[admin_id] = {"type": "admin", "username": f"admin_{admin_id}"}
        return admin_id

    async def _cleanup_test_user(self, user_id: str) -> None:
        """Clean up a test user."""
        if user_id in self.test_data_store:
            del self.test_data_store[user_id]

    async def _cleanup_session(self, session_id: str) -> None:
        """Clean up a test session."""
        # This would typically call your session cleanup API
        pass

    def _analyze_test_results(self, result: IntegrationTestResult) -> None:
        """Analyze the overall test results."""
        successful_steps = sum(1 for step in result.step_results if step.success)
        total_steps = len(result.step_results)

        result.overall_success = (
            result.setup_success and
            result.teardown_success and
            successful_steps == total_steps
        )

        # Calculate performance metrics
        if result.step_results:
            durations = [step.duration for step in result.step_results if step.success]
            if durations:
                result.performance_metrics = {
                    "total_duration": result.duration,
                    "average_step_duration": sum(durations) / len(durations),
                    "min_step_duration": min(durations),
                    "max_step_duration": max(durations),
                    "successful_steps": successful_steps,
                    "total_steps": total_steps
                }

        # Summarize errors
        error_counts = defaultdict(int)
        for step in result.step_results:
            if not step.success:
                if step.error_message:
                    error_counts["execution_errors"] += 1
                if step.assertions_failed:
                    error_counts["assertion_failures"] += len(step.assertions_failed)

        result.error_summary.update(dict(error_counts))

    def get_available_scenarios(self) -> List[Dict[str, Any]]:
        """Get all available test scenarios."""
        return [
            {
                "name": scenario.name,
                "description": scenario.description,
                "category": scenario.category,
                "step_count": len(scenario.steps),
                "expected_outcomes": scenario.expected_outcomes,
                "priority": scenario.priority,
                "timeout_seconds": scenario.timeout_seconds
            }
            for scenario in self.test_scenarios.values()
        ]

    def get_test_history(self) -> List[Dict[str, Any]]:
        """Get history of all completed integration tests."""
        return [
            {
                "test_id": result.test_id,
                "scenario_name": result.scenario.name,
                "category": result.scenario.category,
                "start_time": result.start_time.isoformat(),
                "duration": result.duration,
                "overall_success": result.overall_success,
                "successful_steps": sum(1 for step in result.step_results if step.success),
                "total_steps": len(result.step_results),
                "setup_success": result.setup_success,
                "teardown_success": result.teardown_success
            }
            for result in self.test_results.values()
        ]

    def generate_test_report(self, test_id: str) -> Optional[Dict[str, Any]]:
        """Generate a detailed test report."""
        if test_id not in self.test_results:
            return None

        result = self.test_results[test_id]

        report = {
            "test_id": test_id,
            "scenario": {
                "name": result.scenario.name,
                "description": result.scenario.description,
                "category": result.scenario.category,
                "expected_outcomes": result.scenario.expected_outcomes
            },
            "execution_summary": {
                "start_time": result.start_time.isoformat(),
                "end_time": result.end_time.isoformat() if result.end_time else None,
                "duration": result.duration,
                "overall_success": result.overall_success,
                "setup_success": result.setup_success,
                "teardown_success": result.teardown_success
            },
            "step_results": [
                {
                    "step_name": step.step_name,
                    "step_type": step.step_type,
                    "duration": step.duration,
                    "success": step.success,
                    "assertions_passed": step.assertions_passed,
                    "assertions_failed": step.assertions_failed,
                    "error_message": step.error_message
                }
                for step in result.step_results
            ],
            "performance_metrics": result.performance_metrics,
            "error_analysis": {
                "error_summary": result.error_summary,
                "total_errors": sum(result.error_summary.values())
            },
            "recommendations": self._generate_test_recommendations(result)
        }

        return report

    def _generate_test_recommendations(self, result: IntegrationTestResult) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []

        if not result.setup_success:
            recommendations.append("Fix test environment setup issues before running integration tests")

        if not result.teardown_success:
            recommendations.append("Improve test cleanup procedures to prevent resource leaks")

        failed_steps = [step for step in result.step_results if not step.success]
        if failed_steps:
            recommendations.append(f"Address failures in {len(failed_steps)} test steps")

        if result.performance_metrics.get("average_step_duration", 0) > 10.0:
            recommendations.append("Optimize API response times for better user experience")

        error_count = sum(result.error_summary.values())
        if error_count > 5:
            recommendations.append("Review and fix systemic issues causing multiple test failures")

        if not result.overall_success:
            recommendations.append("Test scenario requires attention before production deployment")

        return recommendations
