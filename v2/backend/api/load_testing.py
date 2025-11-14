"""
Load testing API routes.
Provides comprehensive load testing capabilities for performance validation.
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import asyncio
import json

from ..api.auth import get_admin_user
from ..models.user import User
from ..services.load_testing.load_tester import LoadTester, LoadTestConfig, LoadTestResults

router = APIRouter()


# Request/Response Models

class LoadTestConfigurationRequest(BaseModel):
    """Request model for creating load test configurations."""
    name: str = Field(..., min_length=1, max_length=100, description="Test name")
    description: Optional[str] = Field("", description="Test description")
    test_type: str = Field("volume", description="Test type: volume, spike, stress, endurance, ramp")
    duration_seconds: Optional[int] = Field(300, ge=30, le=3600, description="Test duration in seconds")
    concurrent_users: Optional[int] = Field(10, ge=1, le=1000, description="Number of concurrent users")
    ramp_up_seconds: Optional[int] = Field(30, ge=0, le=300, description="Ramp up time in seconds")
    ramp_down_seconds: Optional[int] = Field(30, ge=0, le=300, description="Ramp down time in seconds")
    requests_per_minute: Optional[int] = Field(60, ge=1, le=10000, description="Requests per minute for volume testing")
    spike_multiplier: Optional[float] = Field(5.0, ge=1.0, le=20.0, description="Spike load multiplier")
    spike_duration: Optional[int] = Field(60, ge=10, le=300, description="Spike duration in seconds")
    request_weights: Optional[Dict[str, float]] = Field(None, description="Endpoint request weights")
    custom_headers: Optional[Dict[str, str]] = Field(None, description="Custom request headers")


class LoadTestConfigurationResponse(BaseModel):
    """Response model for load test configuration."""
    configuration: Dict[str, Any]
    validation_status: str  # valid, warning, invalid
    validation_messages: List[str]
    estimated_duration: int
    estimated_requests: int


class LoadTestExecutionResponse(BaseModel):
    """Response model for load test execution."""
    test_id: str
    status: str  # queued, running, completed, failed
    start_time: Optional[str] = None
    progress: Optional[float] = None
    message: str


class LoadTestResultsResponse(BaseModel):
    """Response model for load test results."""
    test_id: str
    configuration: Dict[str, Any]
    summary: Dict[str, Any]
    response_time_metrics: Dict[str, Any]
    error_analysis: Dict[str, Any]
    threshold_analysis: Dict[str, Any]
    recommendations: List[str]
    execution_time: str
    report_generated_at: str


class LoadTestStatusResponse(BaseModel):
    """Response model for load test status."""
    test_id: str
    status: str
    progress: float
    start_time: str
    current_requests: int
    current_errors: int
    avg_response_time: float
    requests_per_second: float


class ActiveTestsResponse(BaseModel):
    """Response model for active tests."""
    active_tests: List[Dict[str, Any]]
    total_active: int


class TestHistoryResponse(BaseModel):
    """Response model for test history."""
    tests: List[Dict[str, Any]]
    total_tests: int
    pagination: Dict[str, Any]


class PerformanceThresholdsResponse(BaseModel):
    """Response model for performance thresholds."""
    thresholds: Dict[str, float]
    last_updated: str


class UpdateThresholdsRequest(BaseModel):
    """Request model for updating performance thresholds."""
    max_response_time: Optional[float] = Field(None, ge=0.1, le=60.0, description="Maximum response time in seconds")
    max_error_rate: Optional[float] = Field(None, ge=0.0, le=1.0, description="Maximum error rate (0.0-1.0)")
    min_requests_per_second: Optional[float] = Field(None, ge=0.1, le=1000.0, description="Minimum requests per second")
    max_cpu_usage: Optional[float] = Field(None, ge=0.0, le=100.0, description="Maximum CPU usage percentage")
    max_memory_usage: Optional[float] = Field(None, ge=0.0, le=100.0, description="Maximum memory usage percentage")


class TestReportResponse(BaseModel):
    """Response model for test reports."""
    test_id: str
    report: Dict[str, Any]
    export_formats: List[str]


# Global load tester instance
load_tester = LoadTester()


@router.post("/configure", response_model=LoadTestConfigurationResponse)
async def configure_load_test(
    config_request: LoadTestConfigurationRequest,
    current_user: User = Depends(get_admin_user)  # Admin only
):
    """
    Configure and validate a load test.

    Allows administrators to set up and validate load test configurations
    before execution.
    """
    try:
        # Convert request to LoadTestConfig
        config_dict = config_request.dict()
        config = LoadTestConfig(**config_dict)

        # Validate configuration
        validation_messages = []
        validation_status = "valid"

        # Check test type
        valid_test_types = ["volume", "spike", "stress", "endurance", "ramp"]
        if config.test_type not in valid_test_types:
            validation_messages.append(f"Invalid test type. Must be one of: {', '.join(valid_test_types)}")
            validation_status = "invalid"

        # Check duration limits
        if config.duration_seconds < 30:
            validation_messages.append("Test duration must be at least 30 seconds")
            validation_status = "warning"

        # Check concurrent users
        if config.concurrent_users > 500:
            validation_messages.append("High concurrent user count may impact system stability")
            validation_status = "warning"

        # Validate request weights
        if config.request_weights:
            total_weight = sum(config.request_weights.values())
            if abs(total_weight - 1.0) > 0.01:
                validation_messages.append("Request weights must sum to approximately 1.0")
                validation_status = "warning"

        # Estimate test metrics
        requests_per_second = config.requests_per_minute / 60.0
        estimated_requests = int(requests_per_second * config.duration_seconds)
        estimated_duration = config.duration_seconds

        # Adjust for ramp up/down in ramp tests
        if config.test_type == "ramp":
            estimated_duration = config.duration_seconds
            # For ramp tests, average load is roughly half of peak
            estimated_requests = int((requests_per_second / 2) * config.duration_seconds)

        return LoadTestConfigurationResponse(
            configuration=config_dict,
            validation_status=validation_status,
            validation_messages=validation_messages,
            estimated_duration=estimated_duration,
            estimated_requests=estimated_requests
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Test configuration failed: {str(e)}"
        )


@router.post("/run", response_model=LoadTestExecutionResponse)
async def run_load_test(
    background_tasks: BackgroundTasks,
    config_request: LoadTestConfigurationRequest,
    current_user: User = Depends(get_admin_user)  # Admin only
):
    """
    Execute a load test.

    Starts a load test in the background with the specified configuration.
    """
    try:
        # Convert request to LoadTestConfig
        config_dict = config_request.dict()
        config = LoadTestConfig(**config_dict)

        # Validate basic configuration
        if config.test_type not in ["volume", "spike", "stress", "endurance", "ramp"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid test type"
            )

        # Run test in background
        background_tasks.add_task(execute_load_test_background, config)

        # Generate test ID for tracking
        test_id = f"test_{int(datetime.utcnow().timestamp())}_{config.name.replace(' ', '_').lower()}"

        return LoadTestExecutionResponse(
            test_id=test_id,
            status="queued",
            message=f"Load test '{config.name}' has been queued for execution",
            start_time=datetime.utcnow().isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Test execution failed: {str(e)}"
        )


async def execute_load_test_background(config: LoadTestConfig):
    """Execute load test in background."""
    try:
        # Update test status to running
        test_id = f"test_{int(datetime.utcnow().timestamp())}_{config.name.replace(' ', '_').lower()}"
        logger.info(f"Starting background load test: {test_id}")

        # Execute the test
        results = await load_tester.run_load_test(config)

        logger.info(f"Background load test completed: {test_id} - {results.successful_requests}/{results.total_requests} successful")

        # Here you could send notifications, update dashboards, etc.

    except Exception as e:
        logger.error(f"Background load test failed: {e}")


@router.get("/status/{test_id}", response_model=LoadTestStatusResponse)
async def get_load_test_status(
    test_id: str,
    current_user: User = Depends(get_admin_user)  # Admin only
):
    """
    Get the current status of a load test.

    Returns real-time progress and metrics for an active test.
    """
    try:
        # Check if test is in active tests
        if test_id in load_tester.active_tests:
            results = load_tester.active_tests[test_id]
            elapsed = (datetime.utcnow() - results.start_time).total_seconds()
            progress = min(100.0, (elapsed / results.config.duration_seconds) * 100)

            return LoadTestStatusResponse(
                test_id=test_id,
                status="running",
                progress=progress,
                start_time=results.start_time.isoformat(),
                current_requests=results.total_requests,
                current_errors=results.failed_requests,
                avg_response_time=results.avg_response_time if results.response_times else 0.0,
                requests_per_second=results.requests_per_second
            )

        # Check if test is in history
        if test_id in load_tester.results_history:
            results = load_tester.results_history[test_id]
            return LoadTestStatusResponse(
                test_id=test_id,
                status="completed",
                progress=100.0,
                start_time=results.start_time.isoformat(),
                current_requests=results.total_requests,
                current_errors=results.failed_requests,
                avg_response_time=results.avg_response_time,
                requests_per_second=results.requests_per_second
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


@router.get("/results/{test_id}", response_model=LoadTestResultsResponse)
async def get_load_test_results(
    test_id: str,
    current_user: User = Depends(get_admin_user)  # Admin only
):
    """
    Get detailed results for a completed load test.

    Returns comprehensive metrics, analysis, and recommendations.
    """
    try:
        # Get test results
        report = load_tester.generate_test_report(test_id)
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test results not found"
            )

        return LoadTestResultsResponse(
            test_id=test_id,
            configuration=report["configuration"],
            summary=report["summary"],
            response_time_metrics=report["response_time_metrics"],
            error_analysis=report["error_analysis"],
            threshold_analysis=report["threshold_analysis"],
            recommendations=report["recommendations"],
            execution_time=f"{report['summary']['duration']:.1f}s",
            report_generated_at=datetime.utcnow().isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Results retrieval failed: {str(e)}"
        )


@router.get("/active", response_model=ActiveTestsResponse)
async def get_active_tests():
    """
    Get all currently active load tests.

    Returns information about running load tests and their progress.
    """
    try:
        active_tests = []
        for test_id, results in load_tester.active_tests.items():
            elapsed = (datetime.utcnow() - results.start_time).total_seconds()
            progress = min(100.0, (elapsed / results.config.duration_seconds) * 100)

            active_tests.append({
                "test_id": test_id,
                "name": results.config.name,
                "type": results.config.test_type,
                "start_time": results.start_time.isoformat(),
                "progress": progress,
                "current_requests": results.total_requests,
                "current_errors": results.failed_requests,
                "requests_per_second": results.requests_per_second
            })

        return ActiveTestsResponse(
            active_tests=active_tests,
            total_active=len(active_tests)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Active tests retrieval failed: {str(e)}"
        )


@router.get("/history", response_model=TestHistoryResponse)
async def get_test_history(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    test_type: Optional[str] = Query(None, description="Filter by test type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    current_user: User = Depends(get_admin_user)  # Admin only
):
    """
    Get load test history with pagination and filtering.

    Returns historical test results and performance data.
    """
    try:
        # Get test history
        all_tests = load_tester.get_test_history()

        # Apply filters
        filtered_tests = all_tests
        if test_type:
            filtered_tests = [t for t in filtered_tests if t["type"] == test_type]

        if status:
            filtered_tests = [t for t in filtered_tests if t["status"] == status]

        # Sort by start time (newest first)
        filtered_tests.sort(key=lambda x: x["start_time"], reverse=True)

        # Pagination
        total_tests = len(filtered_tests)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_tests = filtered_tests[start_idx:end_idx]

        return TestHistoryResponse(
            tests=paginated_tests,
            total_tests=total_tests,
            pagination={
                "page": page,
                "per_page": per_page,
                "total_pages": (total_tests + per_page - 1) // per_page,
                "has_next": end_idx < total_tests,
                "has_prev": page > 1
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Test history retrieval failed: {str(e)}"
        )


@router.get("/thresholds", response_model=PerformanceThresholdsResponse)
async def get_performance_thresholds():
    """
    Get current performance thresholds.

    Returns the configured performance thresholds for load tests.
    """
    try:
        thresholds = load_tester.get_performance_thresholds()

        return PerformanceThresholdsResponse(
            thresholds=thresholds,
            last_updated=datetime.utcnow().isoformat()
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Thresholds retrieval failed: {str(e)}"
        )


@router.put("/thresholds", response_model=PerformanceThresholdsResponse)
async def update_performance_thresholds(
    thresholds_request: UpdateThresholdsRequest,
    current_user: User = Depends(get_admin_user)  # Admin only
):
    """
    Update performance thresholds.

    Allows administrators to adjust performance expectations for load tests.
    """
    try:
        # Convert request to dict, filtering out None values
        updates = {k: v for k, v in thresholds_request.dict().items() if v is not None}

        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No threshold updates provided"
            )

        load_tester.update_performance_thresholds(updates)

        # Return updated thresholds
        thresholds = load_tester.get_performance_thresholds()

        return PerformanceThresholdsResponse(
            thresholds=thresholds,
            last_updated=datetime.utcnow().isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Thresholds update failed: {str(e)}"
        )


@router.get("/report/{test_id}", response_model=TestReportResponse)
async def get_test_report(
    test_id: str,
    format: str = Query("json", description="Export format: json, csv, pdf"),
    current_user: User = Depends(get_admin_user)  # Admin only
):
    """
    Get a detailed test report.

    Returns comprehensive test analysis and recommendations.
    """
    try:
        report = load_tester.generate_test_report(test_id)
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test report not found"
            )

        if format == "json":
            return TestReportResponse(
                test_id=test_id,
                report=report,
                export_formats=["json", "csv"]
            )
        elif format == "csv":
            # Convert report to CSV format
            csv_data = generate_csv_report(report)

            return {
                "test_id": test_id,
                "report": csv_data,
                "export_formats": ["csv"],
                "filename": f"load_test_report_{test_id}_{datetime.utcnow().date()}.csv"
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
            detail=f"Report generation failed: {str(e)}"
        )


def generate_csv_report(report: Dict[str, Any]) -> str:
    """Generate a CSV format report."""
    lines = []

    # Header
    lines.append("Load Test Report")
    lines.append(f"Test ID: {report['test_id']}")
    lines.append(f"Generated: {datetime.utcnow().isoformat()}")
    lines.append("")

    # Summary
    lines.append("SUMMARY")
    summary = report["summary"]
    lines.append(f"Duration (s): {summary['duration']}")
    lines.append(f"Total Requests: {summary['total_requests']}")
    lines.append(f"Successful Requests: {summary['successful_requests']}")
    lines.append(f"Failed Requests: {summary['failed_requests']}")
    lines.append(f"Error Rate: {summary['error_rate']:.3f}")
    lines.append(f"Requests/sec: {summary['requests_per_second']:.2f}")
    lines.append("")

    # Response Time Metrics
    lines.append("RESPONSE TIME METRICS (seconds)")
    rt_metrics = report["response_time_metrics"]
    lines.append(f"Average: {rt_metrics['average']:.3f}")
    lines.append(f"Minimum: {rt_metrics['minimum']:.3f}")
    lines.append(f"Maximum: {rt_metrics['maximum']:.3f}")
    lines.append(f"P50 (median): {rt_metrics['p50']:.3f}")
    lines.append(f"P95: {rt_metrics['p95']:.3f}")
    lines.append(f"P99: {rt_metrics['p99']:.3f}")
    lines.append("")

    # Threshold Analysis
    lines.append("THRESHOLD ANALYSIS")
    threshold = report["threshold_analysis"]
    lines.append(f"Met Thresholds: {threshold['met_thresholds']}")
    if threshold["violations"]:
        lines.append("Violations:")
        for violation in threshold["violations"]:
            lines.append(f"  - {violation}")
    lines.append("")

    # Recommendations
    lines.append("RECOMMENDATIONS")
    for rec in report["recommendations"]:
        lines.append(f"  - {rec}")

    return "\n".join(lines)


@router.post("/cancel/{test_id}")
async def cancel_load_test(
    test_id: str,
    current_user: User = Depends(get_admin_user)  # Admin only
):
    """
    Cancel an active load test.

    Stops a running load test and provides partial results.
    """
    try:
        if test_id not in load_tester.active_tests:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test not found or not active"
            )

        # Note: In a real implementation, you'd need to implement proper cancellation
        # This is a simplified version
        results = load_tester.active_tests[test_id]
        results.end_time = datetime.utcnow()
        results.duration = (results.end_time - results.start_time).total_seconds()

        # Move to history
        load_tester.results_history[test_id] = results
        del load_tester.active_tests[test_id]

        return {
            "success": True,
            "test_id": test_id,
            "status": "cancelled",
            "partial_results": {
                "duration": results.duration,
                "total_requests": results.total_requests,
                "successful_requests": results.successful_requests,
                "avg_response_time": results.avg_response_time
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Test cancellation failed: {str(e)}"
        )


@router.get("/presets")
async def get_test_presets():
    """
    Get predefined load test configurations.

    Returns common test scenarios and configurations for quick setup.
    """
    try:
        presets = {
            "basic_volume_test": {
                "name": "Basic Volume Test",
                "description": "Test system with constant moderate load",
                "test_type": "volume",
                "duration_seconds": 300,
                "concurrent_users": 20,
                "requests_per_minute": 120,
                "request_weights": {
                    "/api/v2/ai/chat": 0.5,
                    "/api/v2/grokopedia/deep-research": 0.3,
                    "/api/v2/research/history": 0.2
                }
            },
            "spike_test": {
                "name": "Traffic Spike Test",
                "description": "Test system resilience to sudden traffic spikes",
                "test_type": "spike",
                "duration_seconds": 600,
                "concurrent_users": 50,
                "requests_per_minute": 60,
                "spike_multiplier": 8.0,
                "spike_duration": 120
            },
            "stress_test": {
                "name": "Stress Test",
                "description": "Gradually increase load until system limits are reached",
                "test_type": "stress",
                "duration_seconds": 900,
                "concurrent_users": 100,
                "requests_per_minute": 300
            },
            "endurance_test": {
                "name": "Endurance Test",
                "description": "Test system stability over extended period",
                "test_type": "endurance",
                "duration_seconds": 1800,  # 30 minutes
                "concurrent_users": 30,
                "requests_per_minute": 90
            },
            "api_load_test": {
                "name": "API Load Test",
                "description": "Comprehensive test of all API endpoints",
                "test_type": "volume",
                "duration_seconds": 600,
                "concurrent_users": 25,
                "requests_per_minute": 150,
                "request_weights": {
                    "/api/v2/ai/chat": 0.3,
                    "/api/v2/grokopedia/deep-research": 0.25,
                    "/api/v2/research/history": 0.15,
                    "/api/v2/voice/transcribe": 0.1,
                    "/api/v2/language/translate": 0.1,
                    "/api/v2/citations/generate": 0.05,
                    "/api/v2/personas/list": 0.05
                }
            }
        }

        return {
            "presets": presets,
            "total_presets": len(presets),
            "categories": {
                "performance": ["basic_volume_test", "endurance_test"],
                "resilience": ["spike_test", "stress_test"],
                "comprehensive": ["api_load_test"]
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Preset retrieval failed: {str(e)}"
        )


@router.get("/metrics/summary")
async def get_load_testing_summary(
    days: int = Query(7, ge=1, le=90, description="Days to look back"),
    current_user: User = Depends(get_admin_user)  # Admin only
):
    """
    Get load testing analytics summary.

    Returns aggregated metrics and trends from recent load tests.
    """
    try:
        # Get test history
        all_tests = load_tester.get_test_history()

        # Filter by time range
        cutoff_date = datetime.utcnow().timestamp() - (days * 24 * 60 * 60)
        recent_tests = [t for t in all_tests if datetime.fromisoformat(t["start_time"]).timestamp() > cutoff_date]

        if not recent_tests:
            return {
                "summary": {
                    "total_tests": 0,
                    "avg_response_time": 0.0,
                    "avg_error_rate": 0.0,
                    "avg_requests_per_second": 0.0,
                    "tests_passed": 0,
                    "tests_failed": 0
                },
                "trends": [],
                "generated_at": datetime.utcnow().isoformat()
            }

        # Calculate summary metrics
        total_tests = len(recent_tests)
        avg_response_time = sum(t["avg_response_time"] for t in recent_tests) / total_tests
        avg_error_rate = sum(t["error_rate"] for t in recent_tests) / total_tests
        avg_rps = sum(t["requests_per_second"] for t in recent_tests) / total_tests

        tests_passed = sum(1 for t in recent_tests if t["met_thresholds"])
        tests_failed = total_tests - tests_passed

        # Group by test type for trends
        type_stats = {}
        for test in recent_tests:
            test_type = test["type"]
            if test_type not in type_stats:
                type_stats[test_type] = {
                    "count": 0,
                    "total_requests": 0,
                    "avg_response_time": 0.0,
                    "avg_error_rate": 0.0
                }

            type_stats[test_type]["count"] += 1
            type_stats[test_type]["total_requests"] += test["total_requests"]
            type_stats[test_type]["avg_response_time"] += test["avg_response_time"]
            type_stats[test_type]["avg_error_rate"] += test["error_rate"]

        # Calculate averages
        for stats in type_stats.values():
            if stats["count"] > 0:
                stats["avg_response_time"] /= stats["count"]
                stats["avg_error_rate"] /= stats["count"]

        return {
            "summary": {
                "total_tests": total_tests,
                "avg_response_time": round(avg_response_time, 3),
                "avg_error_rate": round(avg_error_rate, 4),
                "avg_requests_per_second": round(avg_rps, 2),
                "tests_passed": tests_passed,
                "tests_failed": tests_failed,
                "success_rate": round(tests_passed / total_tests * 100, 1) if total_tests > 0 else 0
            },
            "trends": type_stats,
            "time_range_days": days,
            "generated_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Load testing summary failed: {str(e)}"
        )
