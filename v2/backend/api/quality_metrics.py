"""
Quality metrics dashboard API routes.
Provides comprehensive quality assessment and metrics for the research system.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from ..api.auth import get_admin_user
from ..models.user import User
from ..core.database import get_db
from ..services.quality_metrics.quality_dashboard import QualityMetricsDashboard
import sqlalchemy as sa

router = APIRouter()


# Request/Response Models

class QualityDashboardRequest(BaseModel):
    """Request model for quality dashboard."""
    date_from: Optional[datetime] = Field(None, description="Start date for analysis")
    date_to: Optional[datetime] = Field(None, description="End date for analysis")
    include_trends: Optional[bool] = Field(True, description="Include trend analysis")


class QualityDashboardResponse(BaseModel):
    """Response model for quality dashboard."""
    success: bool
    dashboard_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class QualityReportRequest(BaseModel):
    """Request model for quality reports."""
    date_from: Optional[datetime] = Field(None, description="Start date for report")
    date_to: Optional[datetime] = Field(None, description="End date for report")
    format: Optional[str] = Field("detailed", description="Report format: summary, detailed, executive")
    include_recommendations: Optional[bool] = Field(True, description="Include recommendations")


class QualityReportResponse(BaseModel):
    """Response model for quality reports."""
    success: bool
    report: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class QualityMetricsResponse(BaseModel):
    """Response model for specific quality metrics."""
    success: bool
    metrics: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class QualityComparisonRequest(BaseModel):
    """Request model for quality comparison."""
    baseline_period: Dict[str, datetime] = Field(..., description="Baseline period start and end dates")
    comparison_period: Dict[str, datetime] = Field(..., description="Comparison period start and end dates")
    metrics: Optional[List[str]] = Field(None, description="Specific metrics to compare")


class QualityComparisonResponse(BaseModel):
    """Response model for quality comparison."""
    success: bool
    comparison: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class QualityThresholdsResponse(BaseModel):
    """Response model for quality thresholds."""
    success: bool
    thresholds: Optional[Dict[str, Any]] = None
    current_scores: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# API Endpoints

@router.get("/dashboard", response_model=QualityDashboardResponse)
async def get_quality_dashboard(
    date_from: Optional[datetime] = Query(None, description="Start date (ISO format)"),
    date_to: Optional[datetime] = Query(None, description="End date (ISO format)"),
    current_user: User = Depends(get_admin_user),  # Admin only for quality dashboard
    db: sa.AsyncSession = Depends(get_db)
):
    """
    Get comprehensive quality dashboard.

    Returns detailed analysis of system quality including research quality,
    user satisfaction, content quality, system reliability, and performance metrics.
    """
    try:
        quality_dashboard = QualityMetricsDashboard()
        dashboard_data = await quality_dashboard.get_quality_dashboard(
            db, date_from, date_to
        )

        if "error" in dashboard_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=dashboard_data["error"]
            )

        return QualityDashboardResponse(success=True, dashboard_data=dashboard_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Quality dashboard generation failed: {str(e)}"
        )


@router.get("/report", response_model=QualityReportResponse)
async def get_quality_report(
    date_from: Optional[datetime] = Query(None, description="Start date (ISO format)"),
    date_to: Optional[datetime] = Query(None, description="End date (ISO format)"),
    format: str = Query("detailed", description="Report format: summary, detailed, executive"),
    current_user: User = Depends(get_admin_user),  # Admin only
    db: sa.AsyncSession = Depends(get_db)
):
    """
    Generate a formatted quality report.

    Creates comprehensive quality assessment reports in various formats
    for different audiences (executive, technical, summary).
    """
    try:
        quality_dashboard = QualityMetricsDashboard()

        # Get dashboard data
        dashboard_data = await quality_dashboard.get_quality_dashboard(
            db, date_from, date_to
        )

        if "error" in dashboard_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=dashboard_data["error"]
            )

        # Generate formatted report
        report = quality_dashboard.get_quality_report(dashboard_data, format)

        return QualityReportResponse(success=True, report=report)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Quality report generation failed: {str(e)}"
        )


@router.get("/metrics/{metric_type}", response_model=QualityMetricsResponse)
async def get_specific_quality_metrics(
    metric_type: str,
    date_from: Optional[datetime] = Query(None, description="Start date (ISO format)"),
    date_to: Optional[datetime] = Query(None, description="End date (ISO format)"),
    current_user: User = Depends(get_admin_user),  # Admin only
    db: sa.AsyncSession = Depends(get_db)
):
    """
    Get specific quality metrics.

    Returns detailed metrics for a specific quality aspect
    (research_quality, user_satisfaction, content_quality, system_reliability, performance_quality).
    """
    try:
        quality_dashboard = QualityMetricsDashboard()

        # Get full dashboard and extract specific metric
        dashboard_data = await quality_dashboard.get_quality_dashboard(
            db, date_from, date_to
        )

        if "error" in dashboard_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=dashboard_data["error"]
            )

        # Extract requested metric
        metric_data = dashboard_data.get(metric_type)
        if not metric_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Metric type '{metric_type}' not found"
            )

        return QualityMetricsResponse(success=True, metrics=metric_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Quality metrics retrieval failed: {str(e)}"
        )


@router.get("/metrics", response_model=QualityMetricsResponse)
async def get_all_quality_metrics(
    current_user: User = Depends(get_admin_user),  # Admin only
    db: sa.AsyncSession = Depends(get_db)
):
    """
    Get all quality metrics summary.

    Returns a summary of all quality metrics with current scores and assessments.
    """
    try:
        quality_dashboard = QualityMetricsDashboard()

        # Get dashboard data
        dashboard_data = await quality_dashboard.get_quality_dashboard(db)

        if "error" in dashboard_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=dashboard_data["error"]
            )

        # Extract key metrics
        metrics_summary = {
            'overall_score': dashboard_data.get('overall_quality_score'),
            'quality_grade': dashboard_data.get('quality_grade'),
            'quality_breakdown': dashboard_data.get('quality_breakdown', {}),
            'last_updated': dashboard_data.get('generated_at'),
            'assessment_summary': {
                component: data.get('assessment', {})
                for component, data in dashboard_data.items()
                if isinstance(data, dict) and 'assessment' in data
            }
        }

        return QualityMetricsResponse(success=True, metrics=metrics_summary)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Quality metrics summary failed: {str(e)}"
        )


@router.post("/compare", response_model=QualityComparisonResponse)
async def compare_quality_periods(
    baseline_from: datetime = Query(..., description="Baseline period start date"),
    baseline_to: datetime = Query(..., description="Baseline period end date"),
    comparison_from: datetime = Query(..., description="Comparison period start date"),
    comparison_to: datetime = Query(..., description="Comparison period end date"),
    current_user: User = Depends(get_admin_user),  # Admin only
    db: sa.AsyncSession = Depends(get_db)
):
    """
    Compare quality metrics between two time periods.

    Allows administrators to track quality improvements or declines
    over time by comparing different periods.
    """
    try:
        quality_dashboard = QualityMetricsDashboard()

        # Get baseline period data
        baseline_data = await quality_dashboard.get_quality_dashboard(
            db, baseline_from, baseline_to
        )

        # Get comparison period data
        comparison_data = await quality_dashboard.get_quality_dashboard(
            db, comparison_from, comparison_to
        )

        if "error" in baseline_data or "error" in comparison_data:
            error_msg = baseline_data.get("error", comparison_data.get("error", "Unknown error"))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Quality comparison failed: {error_msg}"
            )

        # Calculate differences
        comparison_result = {
            'baseline_period': {
                'from': baseline_from.isoformat(),
                'to': baseline_to.isoformat(),
                'overall_score': baseline_data.get('overall_quality_score'),
                'grade': baseline_data.get('quality_grade')
            },
            'comparison_period': {
                'from': comparison_from.isoformat(),
                'to': comparison_to.isoformat(),
                'overall_score': comparison_data.get('overall_quality_score'),
                'grade': comparison_data.get('quality_grade')
            },
            'changes': {},
            'improvements': [],
            'declines': []
        }

        # Compare component scores
        baseline_breakdown = baseline_data.get('quality_breakdown', {})
        comparison_breakdown = comparison_data.get('quality_breakdown', {})

        for component in baseline_breakdown:
            baseline_score = baseline_breakdown.get(component, 0)
            comparison_score = comparison_breakdown.get(component, 0)
            change = comparison_score - baseline_score

            comparison_result['changes'][component] = {
                'baseline': baseline_score,
                'comparison': comparison_score,
                'change': change,
                'change_percent': (change / baseline_score * 100) if baseline_score > 0 else 0
            }

            if change > 0.05:  # Improvement threshold
                comparison_result['improvements'].append(component)
            elif change < -0.05:  # Decline threshold
                comparison_result['declines'].append(component)

        # Overall change
        baseline_overall = baseline_data.get('overall_quality_score', 0)
        comparison_overall = comparison_data.get('overall_quality_score', 0)
        overall_change = comparison_overall - baseline_overall

        comparison_result['overall_change'] = {
            'baseline': baseline_overall,
            'comparison': comparison_overall,
            'change': overall_change,
            'change_percent': (overall_change / baseline_overall * 100) if baseline_overall > 0 else 0,
            'trend': 'improving' if overall_change > 0 else 'declining' if overall_change < 0 else 'stable'
        }

        return QualityComparisonResponse(success=True, comparison=comparison_result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Quality comparison failed: {str(e)}"
        )


@router.get("/thresholds", response_model=QualityThresholdsResponse)
async def get_quality_thresholds(
    current_user: User = Depends(get_admin_user),  # Admin only
    db: sa.AsyncSession = Depends(get_db)
):
    """
    Get quality thresholds and current performance.

    Shows the target quality thresholds and how current performance compares.
    """
    try:
        quality_dashboard = QualityMetricsDashboard()

        # Get current dashboard data
        dashboard_data = await quality_dashboard.get_quality_dashboard(db)

        if "error" in dashboard_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=dashboard_data["error"]
            )

        thresholds_info = {
            'thresholds': quality_dashboard.quality_thresholds,
            'scoring_weights': quality_dashboard.scoring_weights,
            'current_scores': dashboard_data.get('quality_breakdown', {}),
            'overall_target': 0.85,  # Target overall score
            'current_overall': dashboard_data.get('overall_quality_score'),
            'threshold_compliance': {}
        }

        # Check threshold compliance
        current_breakdown = dashboard_data.get('quality_breakdown', {})
        for metric, threshold in quality_dashboard.quality_thresholds.items():
            current_score = current_breakdown.get(metric.replace('_', '_quality').replace('_quality_quality', '_quality'), 0)
            thresholds_info['threshold_compliance'][metric] = {
                'threshold': threshold,
                'current': current_score,
                'compliant': current_score >= threshold,
                'gap': threshold - current_score if current_score < threshold else 0
            }

        return QualityThresholdsResponse(
            success=True,
            thresholds=thresholds_info['thresholds'],
            current_scores=thresholds_info['current_scores']
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Quality thresholds retrieval failed: {str(e)}"
        )


@router.get("/insights", response_model=Dict[str, Any])
async def get_quality_insights(
    current_user: User = Depends(get_admin_user),  # Admin only
    db: sa.AsyncSession = Depends(get_db)
):
    """
    Get quality insights and recommendations.

    Provides actionable insights based on quality metrics analysis.
    """
    try:
        quality_dashboard = QualityMetricsDashboard()

        # Get dashboard data
        dashboard_data = await quality_dashboard.get_quality_dashboard(db)

        if "error" in dashboard_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=dashboard_data["error"]
            )

        insights = {
            'overall_assessment': {
                'grade': dashboard_data.get('quality_grade'),
                'score': dashboard_data.get('overall_quality_score'),
                'status': 'good' if dashboard_data.get('overall_quality_score', 0) > 0.8 else 'needs_improvement'
            },
            'key_insights': dashboard_data.get('insights', []),
            'recommendations': dashboard_data.get('recommendations', []),
            'strengths': [
                component for component, data in dashboard_data.items()
                if isinstance(data, dict) and data.get('score', 0) > 0.85
            ],
            'improvement_areas': [
                component for component, data in dashboard_data.items()
                if isinstance(data, dict) and data.get('score', 0) < 0.75
            ],
            'generated_at': dashboard_data.get('generated_at')
        }

        return {"success": True, "insights": insights}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Quality insights retrieval failed: {str(e)}"
        )


@router.get("/export")
async def export_quality_data(
    format: str = Query("json", description="Export format: json, csv"),
    include_historical: bool = Query(False, description="Include historical data"),
    date_from: Optional[datetime] = Query(None, description="Start date (ISO format)"),
    date_to: Optional[datetime] = Query(None, description="End date (ISO format)"),
    current_user: User = Depends(get_admin_user),  # Admin only
    db: sa.AsyncSession = Depends(get_db)
):
    """
    Export quality metrics data for external analysis.

    Allows administrators to export quality data for further analysis or reporting.
    """
    try:
        quality_dashboard = QualityMetricsDashboard()

        # Get dashboard data
        dashboard_data = await quality_dashboard.get_quality_dashboard(
            db, date_from, date_to
        )

        if "error" in dashboard_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=dashboard_data["error"]
            )

        if format == "json":
            return {
                "success": True,
                "data": dashboard_data,
                "format": "json"
            }
        elif format == "csv":
            # Convert to CSV format (simplified)
            csv_lines = ["metric,value,timestamp"]
            for key, value in dashboard_data.items():
                if isinstance(value, (int, float)):
                    csv_lines.append(f"{key},{value},{dashboard_data.get('generated_at', '')}")

            csv_data = "\n".join(csv_lines)

            return {
                "success": True,
                "data": csv_data,
                "format": "csv",
                "filename": f"quality_metrics_{datetime.utcnow().date()}.csv"
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
            detail=f"Quality data export failed: {str(e)}"
        )


@router.get("/alerts")
async def get_quality_alerts(
    current_user: User = Depends(get_admin_user),  # Admin only
    db: sa.AsyncSession = Depends(get_db)
):
    """
    Get quality-related alerts and warnings.

    Identifies areas where quality metrics fall below acceptable thresholds.
    """
    try:
        quality_dashboard = QualityMetricsDashboard()

        # Get current dashboard data
        dashboard_data = await quality_dashboard.get_quality_dashboard(db)

        if "error" in dashboard_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=dashboard_data["error"]
            )

        alerts = []
        breakdown = dashboard_data.get('quality_breakdown', {})

        # Check each component against thresholds
        for component, score in breakdown.items():
            threshold_key = component.replace('_quality', '').replace('_', '_')
            threshold = quality_dashboard.quality_thresholds.get(threshold_key, 0.8)

            if score < threshold:
                severity = "critical" if score < 0.6 else "warning" if score < 0.7 else "info"

                alerts.append({
                    'component': component,
                    'severity': severity,
                    'message': f"{component.replace('_', ' ').title()} quality ({score:.2f}) below threshold ({threshold})",
                    'current_score': score,
                    'threshold': threshold,
                    'gap': threshold - score,
                    'timestamp': dashboard_data.get('generated_at')
                })

        # Overall quality alert
        overall_score = dashboard_data.get('overall_quality_score', 0)
        if overall_score < 0.75:
            alerts.insert(0, {
                'component': 'overall_quality',
                'severity': 'critical',
                'message': f"Overall quality score ({overall_score:.2f}) indicates critical issues",
                'current_score': overall_score,
                'threshold': 0.8,
                'gap': 0.8 - overall_score,
                'timestamp': dashboard_data.get('generated_at')
            })

        return {
            "success": True,
            "alerts": alerts,
            "total_alerts": len(alerts),
            "critical_count": sum(1 for a in alerts if a['severity'] == 'critical'),
            "warning_count": sum(1 for a in alerts if a['severity'] == 'warning')
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Quality alerts retrieval failed: {str(e)}"
        )
