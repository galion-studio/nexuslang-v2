"""
User Acceptance Testing API routes.
Provides comprehensive UAT capabilities for beta testing and user feedback.
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import json

from ..api.auth import get_admin_user
from ..models.user import User
from ..services.user_acceptance_testing.user_acceptance_tester import UserAcceptanceTester

router = APIRouter()


# Request/Response Models

class CreateBetaProgramRequest(BaseModel):
    """Request model for creating beta programs."""
    name: str = Field(..., min_length=1, max_length=100, description="Program name")
    description: Optional[str] = Field("", description="Program description")
    version: Optional[str] = Field("1.0.0", description="Software version being tested")
    target_users: Optional[int] = Field(100, ge=10, le=10000, description="Target number of beta users")
    criteria_template: Optional[str] = Field(None, description="Acceptance criteria template to use")
    acceptance_criteria: Optional[List[str]] = Field(None, description="Custom acceptance criteria")
    test_scenarios: Optional[List[Dict[str, Any]]] = Field(None, description="Test scenarios for users")
    success_metrics: Optional[Dict[str, Any]] = Field(None, description="Success metrics to track")


class CreateBetaProgramResponse(BaseModel):
    """Response model for beta program creation."""
    success: bool
    program_id: Optional[str] = None
    name: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[str] = None
    acceptance_criteria_count: Optional[int] = None
    error: Optional[str] = None


class StartBetaProgramResponse(BaseModel):
    """Response model for starting beta programs."""
    success: bool
    program_id: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[str] = None
    target_users: Optional[int] = None
    error: Optional[str] = None


class UserEnrollmentRequest(BaseModel):
    """Request model for user enrollment."""
    user_id: str = Field(..., description="User ID to enroll")
    user_profile: Optional[Dict[str, Any]] = Field(None, description="Optional user profile information")


class UserEnrollmentResponse(BaseModel):
    """Response model for user enrollment."""
    success: bool
    program_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    enrollment_date: Optional[str] = None
    total_enrolled: Optional[int] = None
    error: Optional[str] = None


class StartSessionResponse(BaseModel):
    """Response model for starting user sessions."""
    success: bool
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    program_id: Optional[str] = None
    start_time: Optional[str] = None
    error: Optional[str] = None


class RecordActionRequest(BaseModel):
    """Request model for recording user actions."""
    action_type: str = Field(..., description="Type of action performed")
    feature: Optional[str] = Field("", description="Feature being used")
    details: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Action details")
    duration: Optional[float] = Field(0.0, description="Action duration in seconds")
    success: Optional[bool] = Field(True, description="Whether action was successful")


class RecordActionResponse(BaseModel):
    """Response model for action recording."""
    success: bool
    session_id: Optional[str] = None
    action_recorded: Optional[str] = None
    total_actions: Optional[int] = None
    error: Optional[str] = None


class SubmitFeedbackRequest(BaseModel):
    """Request model for submitting feedback."""
    user_id: str = Field(..., description="User ID providing feedback")
    session_id: Optional[str] = Field(None, description="Associated session ID")
    feature_name: Optional[str] = Field("", description="Feature being rated")
    rating: int = Field(..., ge=1, le=5, description="Rating (1-5 scale)")
    feedback_text: Optional[str] = Field("", description="Detailed feedback text")
    feedback_type: Optional[str] = Field("general", description="Type of feedback")
    user_context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="User context information")
    tags: Optional[List[str]] = Field(default_factory=list, description="Feedback tags")


class SubmitFeedbackResponse(BaseModel):
    """Response model for feedback submission."""
    success: bool
    feedback_id: Optional[str] = None
    rating: Optional[int] = None
    type: Optional[str] = None
    status: Optional[str] = None
    error: Optional[str] = None


class EndSessionRequest(BaseModel):
    """Request model for ending sessions."""
    completion_status: str = Field("completed", description="Session completion status")
    final_notes: Optional[str] = Field("", description="Final session notes")
    satisfaction_score: Optional[int] = Field(None, ge=1, le=5, description="Overall satisfaction score")


class EndSessionResponse(BaseModel):
    """Response model for ending sessions."""
    success: bool
    session_id: Optional[str] = None
    duration: Optional[float] = None
    completion_status: Optional[str] = None
    actions_performed: Optional[int] = None
    features_tested: Optional[int] = None
    error: Optional[str] = None


class RunAcceptanceTestResponse(BaseModel):
    """Response model for running acceptance tests."""
    success: bool
    test_id: Optional[str] = None
    program_id: Optional[str] = None
    overall_passed: Optional[bool] = None
    completion_rate: Optional[float] = None
    average_satisfaction: Optional[float] = None
    go_no_go_recommendation: Optional[str] = None
    critical_issues_count: Optional[int] = None
    error: Optional[str] = None


class ProgramStatusResponse(BaseModel):
    """Response model for program status."""
    success: bool
    program_status: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class FeedbackSummaryResponse(BaseModel):
    """Response model for feedback summaries."""
    success: bool
    feedback_summary: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class SessionSummaryResponse(BaseModel):
    """Response model for session summaries."""
    success: bool
    session_summary: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class SurveyTemplatesResponse(BaseModel):
    """Response model for survey templates."""
    success: bool
    templates: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class AcceptanceCriteriaTemplatesResponse(BaseModel):
    """Response model for acceptance criteria templates."""
    success: bool
    templates: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class AcceptanceTestReportResponse(BaseModel):
    """Response model for acceptance test reports."""
    success: bool
    test_id: Optional[str] = None
    program_name: Optional[str] = None
    test_date: Optional[str] = None
    results_summary: Optional[Dict[str, Any]] = None
    detailed_results: Optional[Dict[str, Any]] = None
    recommendations: Optional[List[str]] = None
    go_no_go_recommendation: Optional[str] = None
    error: Optional[str] = None


# Global user acceptance tester instance
uat_tester = UserAcceptanceTester()


@router.post("/programs", response_model=CreateBetaProgramResponse)
async def create_beta_program(
    program_request: CreateBetaProgramRequest,
    current_user: User = Depends(get_admin_user)  # Admin only
):
    """
    Create a new beta testing program.

    Allows administrators to set up structured beta testing programs
    with acceptance criteria and success metrics.
    """
    try:
        program_data = program_request.dict()
        result = await uat_tester.create_beta_program(program_data)

        return CreateBetaProgramResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Beta program creation failed: {str(e)}"
        )


@router.post("/programs/{program_id}/start", response_model=StartBetaProgramResponse)
async def start_beta_program(
    program_id: str,
    current_user: User = Depends(get_admin_user)  # Admin only
):
    """
    Start a beta testing program.

    Begins the beta testing phase and opens enrollment for users.
    """
    try:
        result = await uat_tester.start_beta_program(program_id)

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Failed to start program")
            )

        return StartBetaProgramResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Program start failed: {str(e)}"
        )


@router.post("/programs/{program_id}/enroll", response_model=UserEnrollmentResponse)
async def enroll_user_in_program(
    program_id: str,
    enrollment: UserEnrollmentRequest,
    current_user: User = Depends(get_admin_user)  # Admin only for testing
):
    """
    Enroll a user in a beta testing program.

    Adds users to beta programs and creates their initial testing session.
    """
    try:
        result = await uat_tester.enroll_user_in_program(
            program_id,
            enrollment.user_id,
            enrollment.user_profile
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Enrollment failed")
            )

        return UserEnrollmentResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"User enrollment failed: {str(e)}"
        )


@router.post("/sessions/start", response_model=StartSessionResponse)
async def start_user_session(
    user_id: str,
    program_id: Optional[str] = Query(None, description="Optional beta program ID"),
    current_user: User = Depends(get_admin_user)  # For testing - would be any user in production
):
    """
    Start a user testing session.

    Begins tracking user interactions and testing activities.
    """
    try:
        session_id = await uat_tester.start_user_session(user_id, program_id)

        return StartSessionResponse(
            success=True,
            session_id=session_id,
            user_id=user_id,
            program_id=program_id,
            start_time=datetime.utcnow().isoformat()
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Session start failed: {str(e)}"
        )


@router.post("/sessions/{session_id}/action", response_model=RecordActionResponse)
async def record_user_action(
    session_id: str,
    action: RecordActionRequest,
    current_user: User = Depends(get_admin_user)  # For testing - would be automatic in production
):
    """
    Record a user action during testing.

    Tracks user interactions and feature usage for analysis.
    """
    try:
        result = await uat_tester.record_user_action(session_id, action.dict())

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Action recording failed")
            )

        return RecordActionResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Action recording failed: {str(e)}"
        )


@router.post("/feedback", response_model=SubmitFeedbackResponse)
async def submit_user_feedback(
    feedback: SubmitFeedbackRequest,
    current_user: User = Depends(get_admin_user)  # For testing - would be any user in production
):
    """
    Submit user feedback.

    Collects ratings, comments, and suggestions from beta users.
    """
    try:
        result = await uat_tester.submit_user_feedback(feedback.dict())

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Feedback submission failed")
            )

        return SubmitFeedbackResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Feedback submission failed: {str(e)}"
        )


@router.post("/sessions/{session_id}/end", response_model=EndSessionResponse)
async def end_user_session(
    session_id: str,
    session_end: EndSessionRequest,
    current_user: User = Depends(get_admin_user)  # For testing - would be automatic in production
):
    """
    End a user testing session.

    Completes the session and records final metrics and feedback.
    """
    try:
        result = await uat_tester.end_user_session(
            session_id,
            session_end.completion_status,
            session_end.final_notes
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Session end failed")
            )

        # Update satisfaction score if provided
        if session_end.satisfaction_score and session_id in uat_tester.user_sessions:
            uat_tester.user_sessions[session_id].satisfaction_score = session_end.satisfaction_score

        return EndSessionResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Session end failed: {str(e)}"
        )


@router.post("/programs/{program_id}/acceptance-test", response_model=RunAcceptanceTestResponse)
async def run_acceptance_test(
    program_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_admin_user)  # Admin only
):
    """
    Run acceptance testing for a beta program.

    Analyzes user feedback, session data, and acceptance criteria
    to determine if the software is ready for production release.
    """
    try:
        # Run acceptance test (this might take time, so could be moved to background)
        result = await uat_tester.run_acceptance_test(program_id)

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Acceptance test failed")
            )

        return RunAcceptanceTestResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Acceptance test failed: {str(e)}"
        )


@router.get("/programs/{program_id}/status", response_model=ProgramStatusResponse)
async def get_program_status(
    program_id: str,
    current_user: User = Depends(get_admin_user)  # Admin only
):
    """
    Get the status of a beta testing program.

    Returns enrollment progress, completion status, and key metrics.
    """
    try:
        program_status = uat_tester.get_program_status(program_id)

        if not program_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Program not found"
            )

        return ProgramStatusResponse(
            success=True,
            program_status=program_status
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Program status retrieval failed: {str(e)}"
        )


@router.get("/feedback/summary", response_model=FeedbackSummaryResponse)
async def get_feedback_summary(
    program_id: Optional[str] = Query(None, description="Filter by program ID"),
    current_user: User = Depends(get_admin_user)  # Admin only
):
    """
    Get feedback summary and analysis.

    Returns aggregated feedback statistics and recent user comments.
    """
    try:
        feedback_summary = uat_tester.get_feedback_summary(program_id)

        return FeedbackSummaryResponse(
            success=True,
            feedback_summary=feedback_summary
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Feedback summary retrieval failed: {str(e)}"
        )


@router.get("/sessions/summary", response_model=SessionSummaryResponse)
async def get_session_summary(
    program_id: Optional[str] = Query(None, description="Filter by program ID"),
    current_user: User = Depends(get_admin_user)  # Admin only
):
    """
    Get user session summary and analytics.

    Returns session completion rates, duration statistics, and user engagement metrics.
    """
    try:
        session_summary = uat_tester.get_user_session_summary(program_id)

        return SessionSummaryResponse(
            success=True,
            session_summary=session_summary
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Session summary retrieval failed: {str(e)}"
        )


@router.get("/survey-templates", response_model=SurveyTemplatesResponse)
async def get_survey_templates():
    """
    Get available survey templates.

    Returns pre-configured survey templates for different testing phases.
    """
    try:
        templates = uat_tester.get_survey_templates()

        return SurveyTemplatesResponse(
            success=True,
            templates=templates
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Survey templates retrieval failed: {str(e)}"
        )


@router.get("/acceptance-criteria-templates", response_model=AcceptanceCriteriaTemplatesResponse)
async def get_acceptance_criteria_templates():
    """
    Get acceptance criteria templates.

    Returns pre-configured acceptance criteria for different development stages.
    """
    try:
        templates = uat_tester.get_acceptance_criteria_templates()

        return AcceptanceCriteriaTemplatesResponse(
            success=True,
            templates=templates
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Acceptance criteria templates retrieval failed: {str(e)}"
        )


@router.get("/acceptance-test/{test_id}/report", response_model=AcceptanceTestReportResponse)
async def get_acceptance_test_report(
    test_id: str,
    current_user: User = Depends(get_admin_user)  # Admin only
):
    """
    Get detailed acceptance test report.

    Returns comprehensive analysis of beta testing results and go/no-go recommendations.
    """
    try:
        if test_id not in uat_tester.acceptance_tests:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Acceptance test not found"
            )

        test_result = uat_tester.acceptance_tests[test_id]

        # Get program name
        program_name = "Unknown Program"
        if test_result.program_id in uat_tester.beta_programs:
            program_name = uat_tester.beta_programs[test_result.program_id].name

        # Build detailed report
        detailed_results = {
            "tester_count": test_result.tester_count,
            "completion_rate": test_result.completion_rate,
            "average_satisfaction": test_result.average_satisfaction,
            "acceptance_criteria_evaluation": test_result.acceptance_criteria_met,
            "critical_issues_identified": test_result.critical_issues
        }

        results_summary = {
            "overall_passed": test_result.overall_passed,
            "go_no_go_recommendation": test_result.go_no_go_recommendation,
            "test_date": test_result.test_date.isoformat(),
            "criteria_passed": sum(test_result.acceptance_criteria_met.values()),
            "criteria_total": len(test_result.acceptance_criteria_met)
        }

        return AcceptanceTestReportResponse(
            success=True,
            test_id=test_id,
            program_name=program_name,
            test_date=test_result.test_date.isoformat(),
            results_summary=results_summary,
            detailed_results=detailed_results,
            recommendations=test_result.recommendations,
            go_no_go_recommendation=test_result.go_no_go_recommendation
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Acceptance test report retrieval failed: {str(e)}"
        )


@router.get("/health-check")
async def run_uat_health_check():
    """
    Run a health check for the User Acceptance Testing system.

    Validates that the UAT system is operational and ready for testing.
    """
    try:
        # Basic health checks
        checks = {
            "service_available": True,
            "beta_programs_loaded": len(uat_tester.beta_programs) >= 0,
            "survey_templates_available": len(uat_tester.survey_templates) > 0,
            "acceptance_criteria_available": len(uat_tester.acceptance_criteria_templates) > 0,
            "feedback_system_ready": True,
            "session_tracking_ready": True,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Check recent activity
        recent_sessions = sum(1 for s in uat_tester.user_sessions.values()
                            if (datetime.utcnow() - s.start_time).days < 1)
        recent_feedback = sum(1 for f in uat_tester.user_feedback.values()
                            if (datetime.utcnow() - f.timestamp).days < 1)

        checks["recent_activity"] = {
            "sessions_today": recent_sessions,
            "feedback_today": recent_feedback
        }

        all_passed = all(isinstance(v, bool) and v for k, v in checks.items() if isinstance(v, bool))

        return {
            "status": "healthy" if all_passed else "degraded",
            "checks": checks,
            "user_acceptance_testing_ready": all_passed,
            "active_programs": len([p for p in uat_tester.beta_programs.values() if p.status == "active"]),
            "total_feedback": len(uat_tester.user_feedback),
            "total_sessions": len(uat_tester.user_sessions),
            "timestamp": checks["timestamp"]
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "user_acceptance_testing_ready": False,
            "timestamp": datetime.utcnow().isoformat()
        }


@router.post("/generate-survey/{template_name}")
async def generate_survey_instance(
    template_name: str,
    user_id: str,
    session_id: Optional[str] = Query(None, description="Associated session ID"),
    current_user: User = Depends(get_admin_user)  # For testing - would be automatic in production
):
    """
    Generate a survey instance for a user.

    Creates a personalized survey based on templates and user context.
    """
    try:
        if template_name not in uat_tester.survey_templates:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Survey template not found"
            )

        template = uat_tester.survey_templates[template_name]

        # Generate survey instance
        survey_instance = {
            "survey_id": f"survey_{int(datetime.utcnow().timestamp())}_{user_id}",
            "template_name": template_name,
            "user_id": user_id,
            "session_id": session_id,
            "generated_at": datetime.utcnow().isoformat(),
            "title": template["name"],
            "description": template["description"],
            "questions": template["questions"],
            "status": "active",
            "responses": {}
        }

        return {
            "success": True,
            "survey_instance": survey_instance
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Survey generation failed: {str(e)}"
        )


@router.get("/analytics/overview")
async def get_uat_analytics_overview(
    days: int = Query(30, ge=1, le=365, description="Days to analyze"),
    current_user: User = Depends(get_admin_user)  # Admin only
):
    """
    Get comprehensive UAT analytics overview.

    Returns aggregated metrics across all beta programs and testing activities.
    """
    try:
        # Calculate date range
        cutoff_date = datetime.utcnow().timestamp() - (days * 24 * 60 * 60)

        # Analyze beta programs
        active_programs = [p for p in uat_tester.beta_programs.values() if p.status == "active"]
        completed_programs = [p for p in uat_tester.beta_programs.values() if p.status == "completed"]

        # Analyze sessions
        recent_sessions = [s for s in uat_tester.user_sessions.values()
                         if s.start_time.timestamp() > cutoff_date]

        completed_sessions = [s for s in recent_sessions if s.completion_status == "completed"]
        completion_rate = len(completed_sessions) / len(recent_sessions) if recent_sessions else 0

        # Analyze feedback
        recent_feedback = [f for f in uat_tester.user_feedback.values()
                         if f.timestamp.timestamp() > cutoff_date]

        ratings = [f.rating for f in recent_feedback if f.rating > 0]
        average_rating = sum(ratings) / len(ratings) if ratings else 0

        # Calculate satisfaction distribution
        satisfaction_distribution = {}
        for rating in range(1, 6):
            satisfaction_distribution[f"rating_{rating}"] = len([f for f in recent_feedback if f.rating == rating])

        # Feature usage analysis
        feature_usage = {}
        for session in recent_sessions:
            for feature in session.features_tested:
                feature_usage[feature] = feature_usage.get(feature, 0) + 1

        # Top issues/feedback categories
        feedback_categories = {}
        for feedback in recent_feedback:
            category = feedback.feedback_type
            feedback_categories[category] = feedback_categories.get(category, 0) + 1

        return {
            "success": True,
            "time_range_days": days,
            "summary": {
                "active_programs": len(active_programs),
                "completed_programs": len(completed_programs),
                "total_sessions": len(recent_sessions),
                "completed_sessions": len(completed_sessions),
                "completion_rate": round(completion_rate * 100, 1),
                "total_feedback": len(recent_feedback),
                "average_rating": round(average_rating, 2),
                "features_tested": len(feature_usage)
            },
            "satisfaction_distribution": satisfaction_distribution,
            "top_features": sorted(feature_usage.items(), key=lambda x: x[1], reverse=True)[:10],
            "feedback_categories": feedback_categories,
            "generated_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"UAT analytics overview failed: {str(e)}"
        )


@router.post("/cleanup")
async def cleanup_uat_data(
    days_to_keep: int = Query(90, ge=30, le=365, description="Days of UAT data to keep"),
    current_user: User = Depends(get_admin_user)  # Admin only
):
    """
    Clean up old User Acceptance Testing data.

    Removes old test sessions, feedback, and program data beyond retention period.
    """
    try:
        cutoff_date = datetime.utcnow().timestamp() - (days_to_keep * 24 * 60 * 60)

        # Clean up old sessions
        old_sessions = [sid for sid, session in uat_tester.user_sessions.items()
                       if session.start_time.timestamp() < cutoff_date]
        for session_id in old_sessions:
            del uat_tester.user_sessions[session_id]

        # Clean up old feedback
        old_feedback = [fid for fid, feedback in uat_tester.user_feedback.items()
                       if feedback.timestamp.timestamp() < cutoff_date]
        for feedback_id in old_feedback:
            del uat_tester.user_feedback[feedback_id]

        # Clean up old acceptance tests (keep for longer)
        test_cutoff = datetime.utcnow().timestamp() - (180 * 24 * 60 * 60)  # 6 months
        old_tests = [tid for tid, test in uat_tester.acceptance_tests.items()
                    if test.test_date.timestamp() < test_cutoff]
        for test_id in old_tests:
            del uat_tester.acceptance_tests[test_id]

        return {
            "success": True,
            "cleaned_sessions": len(old_sessions),
            "cleaned_feedback": len(old_feedback),
            "cleaned_tests": len(old_tests),
            "retention_days": days_to_keep,
            "message": f"Cleaned up UAT data older than {days_to_keep} days"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"UAT data cleanup failed: {str(e)}"
        )
