"""
A/B testing API routes.
Provides comprehensive A/B testing capabilities for data-driven optimization.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from ..api.auth import get_admin_user
from ..models.user import User
from ..core.database import get_db
from ..services.ab_testing.ab_testing import ABTestingService
import sqlalchemy as sa

router = APIRouter()


# Request/Response Models

class TestVariantConfig(BaseModel):
    """Configuration for a test variant."""
    id: str = Field(..., description="Unique variant identifier")
    name: str = Field(..., description="Human-readable variant name")
    config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Variant-specific configuration")
    weight: Optional[float] = Field(1.0, description="Traffic allocation weight")
    is_control: Optional[bool] = Field(False, description="Whether this is the control variant")


class CreateTestRequest(BaseModel):
    """Request model for creating A/B tests."""
    name: str = Field(..., min_length=1, max_length=200, description="Test name")
    description: Optional[str] = Field("", description="Test description")
    test_type: str = Field(..., description="Test type: ui, algorithm, feature, personalization, research_strategy")
    variants: List[TestVariantConfig] = Field(..., min_length=2, description="Test variants (minimum 2)")
    config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Test configuration")
    target_metric: Optional[str] = Field("conversion_rate", description="Primary metric to optimize")
    min_participants: Optional[int] = Field(100, ge=10, le=10000, description="Minimum participants required")
    confidence_level: Optional[float] = Field(0.95, ge=0.5, le=0.99, description="Statistical confidence level")
    max_duration_days: Optional[int] = Field(30, ge=1, le=365, description="Maximum test duration in days")


class CreateTestResponse(BaseModel):
    """Response model for test creation."""
    success: bool
    test_id: Optional[str] = None
    name: Optional[str] = None
    status: Optional[str] = None
    variant_count: Optional[int] = None
    created_at: Optional[str] = None
    error: Optional[str] = None


class StartTestResponse(BaseModel):
    """Response model for test start."""
    success: bool
    test_id: Optional[str] = None
    status: Optional[str] = None
    started_at: Optional[str] = None
    error: Optional[str] = None


class VariantAssignmentResponse(BaseModel):
    """Response model for variant assignment."""
    success: bool
    test_id: Optional[str] = None
    variant_id: Optional[str] = None
    new_assignment: Optional[bool] = None
    cached: Optional[bool] = None
    existing: Optional[bool] = None
    error: Optional[str] = None


class ConversionRecordRequest(BaseModel):
    """Request model for recording conversions."""
    user_id: str = Field(..., description="User ID")
    conversion_type: str = Field("primary", description="Type of conversion: primary, secondary, custom")
    score: Optional[float] = Field(1.0, description="Conversion score/weight")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional conversion metadata")


class ConversionRecordResponse(BaseModel):
    """Response model for conversion recording."""
    success: bool
    test_id: Optional[str] = None
    variant_id: Optional[str] = None
    conversion_type: Optional[str] = None
    score: Optional[float] = None
    error: Optional[str] = None


class TestResultsResponse(BaseModel):
    """Response model for test results."""
    success: bool
    test_id: Optional[str] = None
    test_name: Optional[str] = None
    status: Optional[str] = None
    target_metric: Optional[str] = None
    variant_metrics: Optional[Dict[str, Any]] = None
    statistical_analysis: Optional[Dict[str, Any]] = None
    winner: Optional[Dict[str, Any]] = None
    total_participants: Optional[int] = None
    total_conversions: Optional[int] = None
    generated_at: Optional[str] = None
    error: Optional[str] = None


class StopTestResponse(BaseModel):
    """Response model for test stop."""
    success: bool
    test_id: Optional[str] = None
    status: Optional[str] = None
    final_results: Optional[Dict[str, Any]] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None


class ActiveTestsResponse(BaseModel):
    """Response model for active tests."""
    success: bool
    tests: List[Dict[str, Any]]
    total_active: int
    error: Optional[str] = None


class TestTemplatesResponse(BaseModel):
    """Response model for test templates."""
    success: bool
    templates: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class TestValidationResponse(BaseModel):
    """Response model for test validation."""
    valid: bool
    errors: Optional[List[str]] = None
    warnings: Optional[List[str]] = None


# API Endpoints

@router.post("/tests", response_model=CreateTestResponse)
async def create_ab_test(
    test_request: CreateTestRequest,
    current_user: User = Depends(get_admin_user),  # Admin only
    db: sa.AsyncSession = Depends(get_db)
):
    """
    Create a new A/B test.

    Allows administrators to set up controlled experiments to optimize
    user experience and system performance.
    """
    try:
        ab_testing = ABTestingService()

        test_data = test_request.dict()
        test_data["created_by"] = current_user.id

        result = await ab_testing.create_test(db, test_data)

        return CreateTestResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"A/B test creation failed: {str(e)}"
        )


@router.post("/tests/{test_id}/start", response_model=StartTestResponse)
async def start_ab_test(
    test_id: str,
    current_user: User = Depends(get_admin_user),  # Admin only
    db: sa.AsyncSession = Depends(get_db)
):
    """
    Start an A/B test.

    Begins the test and starts allocating users to variants.
    """
    try:
        ab_testing = ABTestingService()
        result = await ab_testing.start_test(db, test_id)

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to start test")
            )

        return StartTestResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Test start failed: {str(e)}"
        )


@router.post("/tests/{test_id}/stop", response_model=StopTestResponse)
async def stop_ab_test(
    test_id: str,
    current_user: User = Depends(get_admin_user),  # Admin only
    db: sa.AsyncSession = Depends(get_db)
):
    """
    Stop an A/B test.

    Ends the test and provides final results and winner determination.
    """
    try:
        ab_testing = ABTestingService()
        result = await ab_testing.stop_test(db, test_id)

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to stop test")
            )

        return StopTestResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Test stop failed: {str(e)}"
        )


@router.get("/tests/{test_id}/variant", response_model=VariantAssignmentResponse)
async def get_user_variant(
    test_id: str,
    user_context: Optional[str] = Query(None, description="JSON string of user context"),
    current_user: User = Depends(get_admin_user),  # For testing - would be any user in production
    db: sa.AsyncSession = Depends(get_db)
):
    """
    Get variant assignment for a user in an A/B test.

    Returns which test variant the user should experience.
    """
    try:
        ab_testing = ABTestingService()

        # Parse user context
        context = {}
        if user_context:
            try:
                context = eval(user_context)  # Simple JSON parsing
            except:
                context = {"raw_context": user_context}

        # For testing purposes, use current_user.id as the user_id
        # In production, this would come from the request
        result = await ab_testing.assign_variant(db, test_id, current_user.id, context)

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Variant assignment failed")
            )

        return VariantAssignmentResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Variant assignment failed: {str(e)}"
        )


@router.post("/tests/{test_id}/convert", response_model=ConversionRecordResponse)
async def record_conversion(
    test_id: str,
    conversion: ConversionRecordRequest,
    current_user: User = Depends(get_admin_user),  # Admin only for testing
    db: sa.AsyncSession = Depends(get_db)
):
    """
    Record a conversion event for an A/B test.

    Tracks when users complete desired actions in the test.
    """
    try:
        ab_testing = ABTestingService()

        # For testing, use the provided user_id
        # In production, this would be automatically determined
        result = await ab_testing.record_conversion(
            db,
            test_id,
            conversion.user_id,
            conversion.conversion_type,
            conversion.score,
            conversion.metadata
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Conversion recording failed")
            )

        return ConversionRecordResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Conversion recording failed: {str(e)}"
        )


@router.get("/tests/{test_id}/results", response_model=TestResultsResponse)
async def get_test_results(
    test_id: str,
    current_user: User = Depends(get_admin_user),  # Admin only
    db: sa.AsyncSession = Depends(get_db)
):
    """
    Get comprehensive results for an A/B test.

    Returns statistical analysis, winner determination, and performance metrics.
    """
    try:
        ab_testing = ABTestingService()
        result = await ab_testing.get_test_results(db, test_id)

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Results retrieval failed")
            )

        return TestResultsResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Test results retrieval failed: {str(e)}"
        )


@router.get("/tests/active", response_model=ActiveTestsResponse)
async def get_active_tests():
    """
    Get all currently active A/B tests.

    Returns information about running experiments and their status.
    """
    try:
        ab_testing = ABTestingService()
        active_tests = ab_testing.get_active_tests()

        return ActiveTestsResponse(
            success=True,
            tests=active_tests,
            total_active=len(active_tests)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Active tests retrieval failed: {str(e)}"
        )


@router.get("/templates", response_model=TestTemplatesResponse)
async def get_test_templates():
    """
    Get available A/B test templates.

    Returns pre-configured test setups for common scenarios.
    """
    try:
        ab_testing = ABTestingService()
        templates = ab_testing.get_test_templates()

        return TestTemplatesResponse(success=True, templates=templates)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Test templates retrieval failed: {str(e)}"
        )


@router.post("/validate")
async def validate_test_config(test_request: CreateTestRequest):
    """
    Validate an A/B test configuration.

    Checks test setup for correctness before creation.
    """
    try:
        ab_testing = ABTestingService()

        # Convert to dict for validation
        test_data = test_request.dict()

        # This would call the validation method from the service
        # For now, return a basic validation response
        validation_result = ab_testing._validate_test_data(test_data)

        return {
            "valid": validation_result["valid"],
            "errors": validation_result["errors"],
            "warnings": []
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Test validation failed: {str(e)}"
        )


@router.get("/tests/{test_id}/status")
async def get_test_status(
    test_id: str,
    current_user: User = Depends(get_admin_user),  # Admin only
    db: sa.AsyncSession = Depends(get_db)
):
    """
    Get the current status of an A/B test.

    Returns test progress, participant counts, and current metrics.
    """
    try:
        # Get test from database
        test = await db.get(ABTest, test_id)
        if not test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test not found"
            )

        # Get participant count
        from sqlalchemy import func
        participant_count_result = await db.execute(
            sa.select(func.count(ABTestParticipant.id)).where(ABTestParticipant.test_id == test_id)
        )
        participant_count = participant_count_result.scalar() or 0

        # Calculate progress
        progress = min(100, (participant_count / test.min_participants) * 100) if test.min_participants > 0 else 0

        # Get current metrics if test is active
        current_metrics = {}
        if test.status == "active":
            ab_testing = ABTestingService()
            results = await ab_testing.get_test_results(db, test_id)
            if results["success"]:
                current_metrics = {
                    "total_participants": results.get("total_participants", 0),
                    "variant_metrics": results.get("variant_metrics", {}),
                    "has_winner": results.get("winner") is not None
                }

        return {
            "success": True,
            "test_id": test_id,
            "name": test.name,
            "status": test.status,
            "progress": round(progress, 1),
            "participant_count": participant_count,
            "min_participants": test.min_participants,
            "started_at": test.started_at.isoformat() if test.started_at else None,
            "current_metrics": current_metrics
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Test status retrieval failed: {str(e)}"
        )


@router.get("/analytics/summary")
async def get_ab_testing_summary(
    current_user: User = Depends(get_admin_user),  # Admin only
    db: sa.AsyncSession = Depends(get_db)
):
    """
    Get A/B testing analytics summary.

    Returns high-level statistics about all tests and their performance.
    """
    try:
        # Get test counts by status
        from sqlalchemy import func

        status_counts_result = await db.execute(
            sa.select(ABTest.status, func.count(ABTest.id)).group_by(ABTest.status)
        )
        status_counts = dict(status_counts_result.all())

        # Get total participants across all tests
        total_participants_result = await db.execute(
            sa.select(func.count(ABTestParticipant.id.distinct()))
        )
        total_participants = total_participants_result.scalar() or 0

        # Get total conversions
        total_conversions_result = await db.execute(
            sa.select(func.count(ABTestResult.id))
        )
        total_conversions = total_conversions_result.scalar() or 0

        # Calculate conversion rate
        conversion_rate = (total_conversions / total_participants * 100) if total_participants > 0 else 0

        # Get recent test activity (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_tests_result = await db.execute(
            sa.select(func.count(ABTest.id)).where(ABTest.created_at >= thirty_days_ago)
        )
        recent_tests = recent_tests_result.scalar() or 0

        return {
            "success": True,
            "summary": {
                "total_tests": sum(status_counts.values()),
                "active_tests": status_counts.get("active", 0),
                "completed_tests": status_counts.get("completed", 0),
                "draft_tests": status_counts.get("draft", 0),
                "total_participants": total_participants,
                "total_conversions": total_conversions,
                "overall_conversion_rate": round(conversion_rate, 2),
                "recent_tests_created": recent_tests,
                "generated_at": datetime.utcnow().isoformat()
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"A/B testing summary failed: {str(e)}"
        )


@router.post("/maintenance/cleanup")
async def cleanup_old_tests(
    background_tasks: BackgroundTasks,
    days_to_keep: int = Query(90, ge=30, le=365, description="Days to keep completed test data"),
    current_user: User = Depends(get_admin_user),  # Admin only
    db: sa.AsyncSession = Depends(get_db)
):
    """
    Clean up old completed A/B tests.

    Removes test data older than the specified retention period.
    """
    try:
        ab_testing = ABTestingService()
        await ab_testing.cleanup_completed_tests(db, days_to_keep)

        return {
            "success": True,
            "message": f"Cleaned up A/B test data older than {days_to_keep} days",
            "retention_days": days_to_keep
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Test cleanup failed: {str(e)}"
        )


@router.get("/export")
async def export_ab_testing_data(
    format: str = Query("json", description="Export format: json, csv"),
    include_participants: bool = Query(False, description="Include participant data (sensitive)"),
    current_user: User = Depends(get_admin_user),  # Admin only
    db: sa.AsyncSession = Depends(get_db)
):
    """
    Export A/B testing data for analysis.

    Allows administrators to export test data for external analysis.
    """
    try:
        # Get all tests
        tests_result = await db.execute(sa.select(ABTest))
        tests = tests_result.scalars().all()

        export_data = {
            "export_timestamp": datetime.utcnow().isoformat(),
            "total_tests": len(tests),
            "tests": []
        }

        for test in tests:
            test_data = {
                "id": test.id,
                "name": test.name,
                "status": test.status,
                "type": test.test_type,
                "created_at": test.created_at.isoformat(),
                "participants": test.total_participants,
                "winner": test.winner_variant_id
            }

            # Include participants if requested (admin only)
            if include_participants:
                participants_result = await db.execute(
                    sa.select(ABTestParticipant).where(ABTestParticipant.test_id == test.id)
                )
                participants = participants_result.scalars().all()
                test_data["participant_details"] = [
                    {
                        "user_id": p.user_id,
                        "variant_id": p.variant_id,
                        "assigned_at": p.assigned_at.isoformat()
                    }
                    for p in participants
                ]

            export_data["tests"].append(test_data)

        if format == "json":
            return {
                "success": True,
                "data": export_data,
                "format": "json"
            }
        elif format == "csv":
            # Convert to CSV format (simplified)
            csv_lines = ["test_id,name,status,type,created_at,participants,winner"]
            for test in export_data["tests"]:
                csv_lines.append(f"{test['id']},{test['name']},{test['status']},{test['type']},{test['created_at']},{test['participants']},{test.get('winner', '')}")

            csv_data = "\n".join(csv_lines)

            return {
                "success": True,
                "data": csv_data,
                "format": "csv",
                "filename": f"ab_testing_export_{datetime.utcnow().date()}.csv"
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
            detail=f"A/B testing export failed: {str(e)}"
        )
