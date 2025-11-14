"""
Integration testing API routes.
Provides comprehensive integration testing capabilities for end-to-end validation.
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import asyncio
import json

from ..api.auth import get_admin_user
from ..models.user import User
from ..services.integration_testing.integration_tester import IntegrationTester

router = APIRouter()


# Request/Response Models

class RunIntegrationTestRequest(BaseModel):
    """Request model for running integration tests."""
    scenario_name: str = Field(..., description="Name of the test scenario to run")
    user_context: Optional[Dict[str, Any]] = Field(None, description="Optional user context for the test")
    timeout_override: Optional[int] = Field(None, ge=30, le=3600, description="Override test timeout in seconds")


class IntegrationTestExecutionResponse(BaseModel):
    """Response model for integration test execution."""
    test_id: str
    scenario_name: str
    status: str  # queued, running, completed, failed
    start_time: Optional[str] = None
    estimated_duration: Optional[int] = None
    message: str


class IntegrationTestStatusResponse(BaseModel):
    """Response model for integration test status."""
    test_id: str
    scenario_name: str
    status: str
    progress: float
    start_time: str
    current_step: Optional[str] = None
    completed_steps: int
    total_steps: int
    duration: float
    success_rate: float


class IntegrationTestResultsResponse(BaseModel):
    """Response model for integration test results."""
    test_id: str
    scenario_name: str
    scenario_description: str
    execution_summary: Dict[str, Any]
    step_results: List[Dict[str, Any]]
    performance_metrics: Dict[str, Any]
    error_analysis: Dict[str, Any]
    recommendations: List[str]
    test_data_summary: Dict[str, Any]
    generated_at: str


class IntegrationTestScenarioResponse(BaseModel):
    """Response model for test scenario details."""
    name: str
    description: str
    category: str
    step_count: int
    expected_outcomes: List[str]
    setup_requirements: List[str]
    priority: str
    timeout_seconds: int


class TestScenariosResponse(BaseModel):
    """Response model for available test scenarios."""
    scenarios: List[Dict[str, Any]]
    total_scenarios: int
    categories: List[str]


class TestHistoryResponse(BaseModel):
    """Response model for integration test history."""
    tests: List[Dict[str, Any]]
    total_tests: int
    pagination: Dict[str, Any]
    summary_stats: Dict[str, Any]


class RunMultipleTestsRequest(BaseModel):
    """Request model for running multiple integration tests."""
    scenario_names: List[str] = Field(..., min_length=1, description="List of scenario names to run")
    parallel_execution: Optional[bool] = Field(False, description="Run tests in parallel")
    user_context: Optional[Dict[str, Any]] = Field(None, description="User context for all tests")


class MultipleTestsExecutionResponse(BaseModel):
    """Response model for multiple test execution."""
    execution_id: str
    test_ids: List[str]
    scenario_names: List[str]
    parallel_execution: bool
    estimated_total_duration: int
    start_time: str
    status: str


class TestExecutionSummary(BaseModel):
    """Summary of test execution."""
    execution_id: str
    total_tests: int
    completed_tests: int
    successful_tests: int
    failed_tests: int
    running_tests: int
    total_duration: float
    average_duration: float
    success_rate: float
    start_time: str
    end_time: Optional[str] = None


# Global integration tester instance
integration_tester = IntegrationTester()

# Track multiple test executions
multiple_executions = {}


@router.post("/run", response_model=IntegrationTestExecutionResponse)
async def run_integration_test(
    background_tasks: BackgroundTasks,
    request: RunIntegrationTestRequest,
    current_user: User = Depends(get_admin_user)  # Admin only
):
    """
    Execute an integration test scenario.

    Runs a complete end-to-end test scenario in the background,
    validating all components work together correctly.
    """
    try:
        # Validate scenario exists
        if request.scenario_name not in integration_tester.test_scenarios:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown test scenario: {request.scenario_name}"
            )

        scenario = integration_tester.test_scenarios[request.scenario_name]

        # Run test in background
        background_tasks.add_task(
            execute_integration_test_background,
            request.scenario_name,
            request.user_context,
            request.timeout_override
        )

        # Generate test ID for tracking
        test_id = f"integration_test_{int(datetime.utcnow().timestamp())}_{request.scenario_name}"

        return IntegrationTestExecutionResponse(
            test_id=test_id,
            scenario_name=request.scenario_name,
            status="queued",
            estimated_duration=request.timeout_override or scenario.timeout_seconds,
            message=f"Integration test '{request.scenario_name}' has been queued for execution",
            start_time=datetime.utcnow().isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Test execution failed: {str(e)}"
        )


async def execute_integration_test_background(
    scenario_name: str,
    user_context: Optional[Dict[str, Any]],
    timeout_override: Optional[int]
):
    """Execute integration test in background."""
    try:
        logger.info(f"Starting background integration test: {scenario_name}")

        # Execute the test
        result = await integration_tester.run_integration_test(scenario_name, user_context)

        logger.info(f"Background integration test completed: {scenario_name} - {result.overall_success}")

        # Here you could send notifications, update dashboards, etc.

    except Exception as e:
        logger.error(f"Background integration test failed: {e}")


@router.post("/run-multiple", response_model=MultipleTestsExecutionResponse)
async def run_multiple_integration_tests(
    background_tasks: BackgroundTasks,
    request: RunMultipleTestsRequest,
    current_user: User = Depends(get_admin_user)  # Admin only
):
    """
    Execute multiple integration test scenarios.

    Runs several test scenarios, either sequentially or in parallel,
    providing comprehensive system validation.
    """
    try:
        # Validate all scenarios exist
        invalid_scenarios = [name for name in request.scenario_names
                           if name not in integration_tester.test_scenarios]
        if invalid_scenarios:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown test scenarios: {', '.join(invalid_scenarios)}"
            )

        execution_id = f"multi_test_{int(datetime.utcnow().timestamp())}"
        test_ids = []

        # Estimate total duration
        total_duration = 0
        for scenario_name in request.scenario_names:
            scenario = integration_tester.test_scenarios[scenario_name]
            total_duration += scenario.timeout_seconds

        if request.parallel_execution:
            # In parallel, total duration is the max of all scenarios
            total_duration = max(scenario.timeout_seconds for scenario_name in request.scenario_names
                               for scenario in [integration_tester.test_scenarios[scenario_name]])

        # Queue tests for execution
        for scenario_name in request.scenario_names:
            test_id = f"{execution_id}_{scenario_name}"
            test_ids.append(test_id)

            if request.parallel_execution:
                background_tasks.add_task(
                    execute_integration_test_background,
                    scenario_name,
                    request.user_context,
                    None
                )
            else:
                # Sequential execution - would need more complex orchestration
                background_tasks.add_task(
                    execute_integration_test_background,
                    scenario_name,
                    request.user_context,
                    None
                )

        # Track multiple execution
        multiple_executions[execution_id] = {
            "test_ids": test_ids,
            "scenario_names": request.scenario_names,
            "parallel_execution": request.parallel_execution,
            "start_time": datetime.utcnow(),
            "status": "running"
        }

        return MultipleTestsExecutionResponse(
            execution_id=execution_id,
            test_ids=test_ids,
            scenario_names=request.scenario_names,
            parallel_execution=request.parallel_execution,
            estimated_total_duration=total_duration,
            start_time=datetime.utcnow().isoformat(),
            status="running"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Multiple test execution failed: {str(e)}"
        )


@router.get("/status/{test_id}", response_model=IntegrationTestStatusResponse)
async def get_integration_test_status(
    test_id: str,
    current_user: User = Depends(get_admin_user)  # Admin only
):
    """
    Get the current status of an integration test.

    Returns real-time progress and current step information.
    """
    try:
        # Check if test is in active tests
        if hasattr(integration_tester, 'active_tests') and test_id in integration_tester.active_tests:
            result = integration_tester.active_tests[test_id]
            elapsed = (datetime.utcnow() - result.start_time).total_seconds()
            progress = min(100.0, (elapsed / result.scenario.timeout_seconds) * 100)

            completed_steps = sum(1 for step in result.step_results if step.success or step.end_time)
            current_step = None
            if completed_steps < len(result.step_results):
                current_step = result.step_results[completed_steps].step_name if result.step_results else None

            return IntegrationTestStatusResponse(
                test_id=test_id,
                scenario_name=result.scenario.name,
                status="running",
                progress=progress,
                start_time=result.start_time.isoformat(),
                current_step=current_step,
                completed_steps=completed_steps,
                total_steps=len(result.scenario.steps),
                duration=elapsed,
                success_rate=completed_steps / len(result.scenario.steps) if result.step_results else 0.0
            )

        # Check if test is in completed results
        if test_id in integration_tester.test_results:
            result = integration_tester.test_results[test_id]
            completed_steps = sum(1 for step in result.step_results if step.success)
            success_rate = completed_steps / len(result.step_results) if result.step_results else 0.0

            return IntegrationTestStatusResponse(
                test_id=test_id,
                scenario_name=result.scenario.name,
                status="completed",
                progress=100.0,
                start_time=result.start_time.isoformat(),
                completed_steps=completed_steps,
                total_steps=len(result.step_results),
                duration=result.duration,
                success_rate=success_rate
            )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test not found"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Status retrieval failed: {str(e)}"
        )


@router.get("/status/multiple/{execution_id}", response_model=TestExecutionSummary)
async def get_multiple_test_status(
    execution_id: str,
    current_user: User = Depends(get_admin_user)  # Admin only
):
    """
    Get the status of a multiple test execution.

    Returns aggregated status for a batch of integration tests.
    """
    try:
        if execution_id not in multiple_executions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Multiple test execution not found"
            )

        execution = multiple_executions[execution_id]
        test_ids = execution["test_ids"]

        # Check status of individual tests
        completed_tests = 0
        successful_tests = 0
        failed_tests = 0
        running_tests = 0
        total_duration = 0.0

        for test_id in test_ids:
            if test_id in integration_tester.test_results:
                result = integration_tester.test_results[test_id]
                completed_tests += 1
                total_duration += result.duration
                if result.overall_success:
                    successful_tests += 1
                else:
                    failed_tests += 1
            elif hasattr(integration_tester, 'active_tests') and test_id in integration_tester.active_tests:
                running_tests += 1

        total_tests = len(test_ids)
        success_rate = (successful_tests / completed_tests * 100) if completed_tests > 0 else 0.0
        average_duration = total_duration / completed_tests if completed_tests > 0 else 0.0

        status = "running"
        end_time = None
        if completed_tests + failed_tests == total_tests:
            status = "completed"
            end_time = datetime.utcnow().isoformat()

        return TestExecutionSummary(
            execution_id=execution_id,
            total_tests=total_tests,
            completed_tests=completed_tests,
            successful_tests=successful_tests,
            failed_tests=failed_tests,
            running_tests=running_tests,
            total_duration=total_duration,
            average_duration=average_duration,
            success_rate=success_rate,
            start_time=execution["start_time"].isoformat(),
            end_time=end_time
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Multiple test status retrieval failed: {str(e)}"
        )


@router.get("/results/{test_id}", response_model=IntegrationTestResultsResponse)
async def get_integration_test_results(
    test_id: str,
    current_user: User = Depends(get_admin_user)  # Admin only
):
    """
    Get detailed results for a completed integration test.

    Returns comprehensive test analysis including step-by-step results,
    performance metrics, and recommendations.
    """
    try:
        # Get test results
        report = integration_tester.generate_test_report(test_id)
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test results not found"
            )

        return IntegrationTestResultsResponse(
            test_id=test_id,
            scenario_name=report["scenario"]["name"],
            scenario_description=report["scenario"]["description"],
            execution_summary=report["execution_summary"],
            step_results=report["step_results"],
            performance_metrics=report["performance_metrics"],
            error_analysis=report["error_analysis"],
            recommendations=report["recommendations"],
            test_data_summary={},  # Would contain sanitized test data
            generated_at=datetime.utcnow().isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Results retrieval failed: {str(e)}"
        )


@router.get("/scenarios", response_model=TestScenariosResponse)
async def get_available_scenarios():
    """
    Get all available integration test scenarios.

    Returns comprehensive list of test scenarios organized by category.
    """
    try:
        scenarios = integration_tester.get_available_scenarios()
        categories = list(set(s["category"] for s in scenarios))

        return TestScenariosResponse(
            scenarios=scenarios,
            total_scenarios=len(scenarios),
            categories=categories
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scenario retrieval failed: {str(e)}"
        )


@router.get("/scenarios/{scenario_name}", response_model=IntegrationTestScenarioResponse)
async def get_scenario_details(
    scenario_name: str,
    current_user: User = Depends(get_admin_user)  # Admin only
):
    """
    Get detailed information about a specific test scenario.

    Returns complete scenario configuration and requirements.
    """
    try:
        if scenario_name not in integration_tester.test_scenarios:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test scenario not found"
            )

        scenario = integration_tester.test_scenarios[scenario_name]

        return IntegrationTestScenarioResponse(
            name=scenario.name,
            description=scenario.description,
            category=scenario.category,
            step_count=len(scenario.steps),
            expected_outcomes=scenario.expected_outcomes,
            setup_requirements=scenario.setup_requirements,
            priority=scenario.priority,
            timeout_seconds=scenario.timeout_seconds
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scenario details retrieval failed: {str(e)}"
        )


@router.get("/history", response_model=TestHistoryResponse)
async def get_test_history(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    category: Optional[str] = Query(None, description="Filter by category"),
    success_only: Optional[bool] = Query(None, description="Filter by success status"),
    current_user: User = Depends(get_admin_user)  # Admin only
):
    """
    Get integration test history with pagination and filtering.

    Returns historical test results with comprehensive filtering options.
    """
    try:
        # Get test history
        all_tests = integration_tester.get_test_history()

        # Apply filters
        filtered_tests = all_tests
        if category:
            filtered_tests = [t for t in filtered_tests if t["category"] == category]

        if success_only is not None:
            filtered_tests = [t for t in filtered_tests if t["overall_success"] == success_only]

        # Sort by start time (newest first)
        filtered_tests.sort(key=lambda x: x["start_time"], reverse=True)

        # Pagination
        total_tests = len(filtered_tests)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_tests = filtered_tests[start_idx:end_idx]

        # Calculate summary stats
        total_completed = len([t for t in all_tests if t.get("end_time")])
        total_successful = len([t for t in all_tests if t["overall_success"]])
        success_rate = (total_successful / total_completed * 100) if total_completed > 0 else 0

        summary_stats = {
            "total_tests": len(all_tests),
            "completed_tests": total_completed,
            "successful_tests": total_successful,
            "failed_tests": total_completed - total_successful,
            "success_rate": round(success_rate, 1),
            "categories": list(set(t["category"] for t in all_tests))
        }

        return TestHistoryResponse(
            tests=paginated_tests,
            total_tests=total_tests,
            pagination={
                "page": page,
                "per_page": per_page,
                "total_pages": (total_tests + per_page - 1) // per_page,
                "has_next": end_idx < total_tests,
                "has_prev": page > 1
            },
            summary_stats=summary_stats
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Test history retrieval failed: {str(e)}"
        )


@router.get("/health-check")
async def run_health_check():
    """
    Run a basic health check for integration testing.

    Performs quick validation that the integration testing system is operational.
    """
    try:
        # Basic health checks
        checks = {
            "scenarios_loaded": len(integration_tester.test_scenarios) > 0,
            "service_available": True,
            "api_accessible": True,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Quick API connectivity test
        try:
            import aiohttp
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.get(f"{integration_tester.base_url}/api/v2/health") as response:
                    checks["api_response"] = response.status == 200
        except:
            checks["api_response"] = False

        all_passed = all(checks.values())

        return {
            "status": "healthy" if all_passed else "degraded",
            "checks": checks,
            "integration_testing_ready": all_passed,
            "available_scenarios": len(integration_tester.test_scenarios),
            "timestamp": checks["timestamp"]
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "integration_testing_ready": False,
            "timestamp": datetime.utcnow().isoformat()
        }


@router.post("/validate-scenario/{scenario_name}")
async def validate_test_scenario(
    scenario_name: str,
    current_user: User = Depends(get_admin_user)  # Admin only
):
    """
    Validate a test scenario configuration.

    Checks that a scenario is properly configured and ready to run.
    """
    try:
        if scenario_name not in integration_tester.test_scenarios:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test scenario not found"
            )

        scenario = integration_tester.test_scenarios[scenario_name]

        # Validation checks
        validation_results = {
            "scenario_exists": True,
            "has_steps": len(scenario.steps) > 0,
            "has_expected_outcomes": len(scenario.expected_outcomes) > 0,
            "valid_timeout": scenario.timeout_seconds > 0,
            "valid_category": scenario.category in ["research", "collaboration", "voice", "multilingual", "admin", "performance"],
            "valid_priority": scenario.priority in ["high", "medium", "low"]
        }

        # Check step configurations
        step_validation = []
        for i, step in enumerate(scenario.steps):
            step_checks = {
                "has_name": bool(step.get("name")),
                "has_type": step.get("type") in ["api_call", "api_call_multiple", "api_call_sequence"],
                "has_endpoint": bool(step.get("endpoint")) if step.get("type") == "api_call" else True,
                "has_method": step.get("method") in ["GET", "POST", "PUT", "DELETE"] if step.get("type") == "api_call" else True,
                "has_assertions": len(step.get("assertions", [])) > 0
            }
            step_validation.append({
                "step_index": i,
                "step_name": step.get("name", f"step_{i}"),
                "valid": all(step_checks.values()),
                "checks": step_checks
            })

        validation_results["steps_valid"] = all(s["valid"] for s in step_validation)
        validation_results["step_validation"] = step_validation

        overall_valid = all(validation_results.values())

        return {
            "scenario_name": scenario_name,
            "valid": overall_valid,
            "validation_results": validation_results,
            "ready_to_run": overall_valid,
            "issues": [k for k, v in validation_results.items() if isinstance(v, bool) and not v]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scenario validation failed: {str(e)}"
        )


@router.get("/export-results/{test_id}")
async def export_test_results(
    test_id: str,
    format: str = Query("json", description="Export format: json, csv, xml"),
    include_raw_data: bool = Query(False, description="Include raw response data"),
    current_user: User = Depends(get_admin_user)  # Admin only
):
    """
    Export integration test results.

    Provides test results in various formats for external analysis.
    """
    try:
        report = integration_tester.generate_test_report(test_id)
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test results not found"
            )

        if format == "json":
            return {
                "success": True,
                "format": "json",
                "data": report,
                "exported_at": datetime.utcnow().isoformat()
            }
        elif format == "csv":
            # Convert to CSV format
            csv_data = generate_results_csv(report, include_raw_data)

            return {
                "success": True,
                "format": "csv",
                "data": csv_data,
                "filename": f"integration_test_results_{test_id}_{datetime.utcnow().date()}.csv",
                "exported_at": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported export format: {format}"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Results export failed: {str(e)}"
        )


def generate_results_csv(report: Dict[str, Any], include_raw_data: bool = False) -> str:
    """Generate CSV format for test results."""
    lines = []

    # Header
    lines.append("Integration Test Results Export")
    lines.append(f"Test ID: {report['test_id']}")
    lines.append(f"Scenario: {report['scenario']['name']}")
    lines.append(f"Generated: {datetime.utcnow().isoformat()}")
    lines.append("")

    # Execution Summary
    lines.append("EXECUTION SUMMARY")
    summary = report["execution_summary"]
    lines.append(f"Start Time: {summary['start_time']}")
    lines.append(f"End Time: {summary.get('end_time', 'N/A')}")
    lines.append(f"Duration: {summary['duration']:.2f}s")
    lines.append(f"Overall Success: {summary['overall_success']}")
    lines.append(f"Setup Success: {summary['setup_success']}")
    lines.append(f"Teardown Success: {summary['teardown_success']}")
    lines.append("")

    # Step Results
    lines.append("STEP RESULTS")
    lines.append("Step Name,Type,Duration,Success,Assertions Passed,Assertions Failed")
    for step in report["step_results"]:
        lines.append(f"{step['step_name']},{step['step_type']},{step['duration']:.3f},{step['success']},{len(step['assertions_passed'])},{len(step['assertions_failed'])}")
    lines.append("")

    # Performance Metrics
    lines.append("PERFORMANCE METRICS")
    perf = report["performance_metrics"]
    if perf:
        lines.append(f"Total Duration: {perf.get('total_duration', 0):.2f}s")
        lines.append(f"Average Step Duration: {perf.get('average_step_duration', 0):.3f}s")
        lines.append(f"Min Step Duration: {perf.get('min_step_duration', 0):.3f}s")
        lines.append(f"Max Step Duration: {perf.get('max_step_duration', 0):.3f}s")
        lines.append(f"Successful Steps: {perf.get('successful_steps', 0)}")
        lines.append(f"Total Steps: {perf.get('total_steps', 0)}")
    lines.append("")

    # Error Analysis
    lines.append("ERROR ANALYSIS")
    errors = report["error_analysis"]
    lines.append(f"Total Errors: {errors.get('total_errors', 0)}")
    for error_type, count in errors.get("error_summary", {}).items():
        lines.append(f"{error_type}: {count}")
    lines.append("")

    return "\n".join(lines)


@router.post("/cleanup")
async def cleanup_test_data(
    days_to_keep: int = Query(30, ge=1, le=365, description="Days of test data to keep"),
    current_user: User = Depends(get_admin_user)  # Admin only
):
    """
    Clean up old integration test data.

    Removes test results and data older than the specified retention period.
    """
    try:
        cutoff_date = datetime.utcnow().timestamp() - (days_to_keep * 24 * 60 * 60)

        # Clean up old test results
        old_test_ids = []
        for test_id, result in integration_tester.test_results.items():
            if result.start_time.timestamp() < cutoff_date:
                old_test_ids.append(test_id)

        for test_id in old_test_ids:
            del integration_tester.test_results[test_id]

        # Clean up old multiple executions
        old_execution_ids = []
        for execution_id, execution in multiple_executions.items():
            if execution["start_time"].timestamp() < cutoff_date:
                old_execution_ids.append(execution_id)

        for execution_id in old_execution_ids:
            del multiple_executions[execution_id]

        return {
            "success": True,
            "cleaned_test_results": len(old_test_ids),
            "cleaned_executions": len(old_execution_ids),
            "retention_days": days_to_keep,
            "message": f"Cleaned up integration test data older than {days_to_keep} days"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Test data cleanup failed: {str(e)}"
        )
