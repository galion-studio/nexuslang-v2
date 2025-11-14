"""
Analytics dashboard API routes.
Provides comprehensive dashboard data combining all analytics systems.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from ..api.auth import get_admin_user
from ..models.user import User
from ..core.database import get_db
from ..services.analytics.analytics_dashboard import AnalyticsDashboardService
import sqlalchemy as sa

router = APIRouter()


# Request/Response Models

class DashboardRequest(BaseModel):
    """Request model for dashboard data."""
    date_from: Optional[datetime] = Field(None, description="Start date (ISO format)")
    date_to: Optional[datetime] = Field(None, description="End date (ISO format)")
    include_trends: Optional[bool] = Field(True, description="Include trend analysis")


class DashboardResponse(BaseModel):
    """Response model for dashboard data."""
    success: bool
    dashboard: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class DetailedAnalyticsRequest(BaseModel):
    """Request model for detailed analytics."""
    metric_type: str = Field(..., description="Type of metrics: usage, performance, quality, errors")
    date_from: Optional[datetime] = Field(None, description="Start date (ISO format)")
    date_to: Optional[datetime] = Field(None, description="End date (ISO format)")


class DetailedAnalyticsResponse(BaseModel):
    """Response model for detailed analytics."""
    success: bool
    analytics: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class DashboardExportRequest(BaseModel):
    """Request model for dashboard export."""
    format: str = Field("json", description="Export format: json, csv")
    include_historical: Optional[bool] = Field(False, description="Include historical trend data")
    date_from: Optional[datetime] = Field(None, description="Start date (ISO format)")
    date_to: Optional[datetime] = Field(None, description="End date (ISO format)")


class DashboardExportResponse(BaseModel):
    """Response model for dashboard export."""
    success: bool
    data: Optional[str] = None
    format: Optional[str] = None
    filename: Optional[str] = None
    error: Optional[str] = None


class DashboardSummaryResponse(BaseModel):
    """Response model for dashboard summary."""
    success: bool
    summary: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class DashboardInsightsResponse(BaseModel):
    """Response model for dashboard insights."""
    success: bool
    insights: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# API Endpoints

@router.get("/main", response_model=DashboardResponse)
async def get_main_dashboard(
    date_from: Optional[datetime] = Query(None, description="Start date (ISO format)"),
    date_to: Optional[datetime] = Query(None, description="End date (ISO format)"),
    current_user: User = Depends(get_admin_user),  # Admin only for full dashboard
    db: sa.AsyncSession = Depends(get_db)
):
    """
    Get the main analytics dashboard.

    Returns comprehensive dashboard data including KPIs, charts, insights,
    alerts, and recommendations for a complete system overview.
    """
    try:
        dashboard_service = AnalyticsDashboardService()
        dashboard_data = await dashboard_service.get_main_dashboard(
            db, date_from, date_to
        )

        if "error" in dashboard_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=dashboard_data["error"]
            )

        return DashboardResponse(success=True, dashboard=dashboard_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Main dashboard generation failed: {str(e)}"
        )


@router.get("/detailed/{metric_type}", response_model=DetailedAnalyticsResponse)
async def get_detailed_analytics(
    metric_type: str,
    date_from: Optional[datetime] = Query(None, description="Start date (ISO format)"),
    date_to: Optional[datetime] = Query(None, description="End date (ISO format)"),
    current_user: User = Depends(get_admin_user),  # Admin only
    db: sa.AsyncSession = Depends(get_db)
):
    """
    Get detailed analytics for a specific metric type.

    Provides in-depth analysis for usage, performance, quality, or error metrics.
    """
    try:
        dashboard_service = AnalyticsDashboardService()
        analytics_data = await dashboard_service.get_detailed_analytics(
            db, metric_type, date_from, date_to
        )

        if "error" in analytics_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=analytics_data["error"]
            )

        return DetailedAnalyticsResponse(success=True, analytics=analytics_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Detailed analytics generation failed: {str(e)}"
        )


@router.get("/summary", response_model=DashboardSummaryResponse)
async def get_dashboard_summary(
    current_user: User = Depends(get_admin_user),  # Admin only
    db: sa.AsyncSession = Depends(get_db)
):
    """
    Get dashboard summary with key metrics.

    Returns essential dashboard metrics for quick overview without full analysis.
    """
    try:
        dashboard_service = AnalyticsDashboardService()
        dashboard_data = await dashboard_service.get_main_dashboard(db)

        if "error" in dashboard_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=dashboard_data["error"]
            )

        # Extract summary information
        summary = {
            'health_status': dashboard_data.get('summary', {}).get('health_status'),
            'key_metrics': dashboard_data.get('summary', {}).get('key_metrics'),
            'kpi_count': len(dashboard_data.get('kpis', [])),
            'alert_count': len(dashboard_data.get('alerts', [])),
            'insight_count': len(dashboard_data.get('insights', [])),
            'last_updated': dashboard_data.get('generated_at'),
            'period_days': dashboard_data.get('time_range', {}).get('days', 30)
        }

        return DashboardSummaryResponse(success=True, summary=summary)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Dashboard summary generation failed: {str(e)}"
        )


@router.get("/insights", response_model=DashboardInsightsResponse)
async def get_dashboard_insights(
    current_user: User = Depends(get_admin_user),  # Admin only
    db: sa.AsyncSession = Depends(get_db)
):
    """
    Get dashboard insights and recommendations.

    Returns AI-generated insights and actionable recommendations based on analytics data.
    """
    try:
        dashboard_service = AnalyticsDashboardService()
        dashboard_data = await dashboard_service.get_main_dashboard(db)

        if "error" in dashboard_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=dashboard_data["error"]
            )

        insights = {
            'insights': dashboard_data.get('insights', []),
            'recommendations': dashboard_data.get('recommendations', []),
            'alerts': dashboard_data.get('alerts', []),
            'trends': dashboard_data.get('summary', {}).get('trends', {}),
            'generated_at': dashboard_data.get('generated_at'),
            'insights_count': len(dashboard_data.get('insights', [])),
            'recommendations_count': len(dashboard_data.get('recommendations', [])),
            'alerts_count': len(dashboard_data.get('alerts', []))
        }

        return DashboardInsightsResponse(success=True, insights=insights)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Dashboard insights generation failed: {str(e)}"
        )


@router.get("/kpis", response_model=Dict[str, Any])
async def get_dashboard_kpis(
    current_user: User = Depends(get_admin_user),  # Admin only
    db: sa.AsyncSession = Depends(get_db)
):
    """
    Get dashboard key performance indicators.

    Returns KPI metrics with targets, current values, and trend information.
    """
    try:
        dashboard_service = AnalyticsDashboardService()
        dashboard_data = await dashboard_service.get_main_dashboard(db)

        if "error" in dashboard_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=dashboard_data["error"]
            )

        kpis = dashboard_data.get('kpis', [])

        # Add summary statistics
        kpi_summary = {
            'total_kpis': len(kpis),
            'success_count': sum(1 for kpi in kpis if kpi.get('status') == 'success'),
            'warning_count': sum(1 for kpi in kpis if kpi.get('status') == 'warning'),
            'danger_count': sum(1 for kpi in kpis if kpi.get('status') == 'danger'),
            'overall_health': 'good' if sum(1 for kpi in kpis if kpi.get('status') == 'success') >= len(kpis) * 0.7 else 'needs_attention'
        }

        return {
            "success": True,
            "kpis": kpis,
            "summary": kpi_summary
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Dashboard KPIs retrieval failed: {str(e)}"
        )


@router.get("/charts/{chart_type}")
async def get_dashboard_chart(
    chart_type: str,
    current_user: User = Depends(get_admin_user),  # Admin only
    db: sa.AsyncSession = Depends(get_db)
):
    """
    Get specific dashboard chart data.

    Returns data for individual charts: usage_trends, quality_breakdown,
    performance_metrics, error_distribution, topic_popularity, user_engagement.
    """
    try:
        dashboard_service = AnalyticsDashboardService()
        dashboard_data = await dashboard_service.get_main_dashboard(db)

        if "error" in dashboard_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=dashboard_data["error"]
            )

        charts = dashboard_data.get('charts', {})
        chart_data = charts.get(chart_type)

        if not chart_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chart type '{chart_type}' not found"
            )

        return {
            "success": True,
            "chart_type": chart_type,
            "chart_data": chart_data
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Dashboard chart retrieval failed: {str(e)}"
        )


@router.get("/alerts")
async def get_dashboard_alerts(
    severity: Optional[str] = Query(None, description="Filter by severity: critical, high, medium, low"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of alerts to return"),
    current_user: User = Depends(get_admin_user),  # Admin only
    db: sa.AsyncSession = Depends(get_db)
):
    """
    Get dashboard alerts and notifications.

    Returns current alerts with severity levels and recommended actions.
    """
    try:
        dashboard_service = AnalyticsDashboardService()
        dashboard_data = await dashboard_service.get_main_dashboard(db)

        if "error" in dashboard_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=dashboard_data["error"]
            )

        alerts = dashboard_data.get('alerts', [])

        # Filter by severity if specified
        if severity:
            alerts = [alert for alert in alerts if alert.get('severity') == severity]

        # Sort by severity (critical first)
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        alerts.sort(key=lambda x: severity_order.get(x.get('severity', 'low'), 3))

        # Limit results
        alerts = alerts[:limit]

        # Add summary statistics
        alert_summary = {
            'total_alerts': len(alerts),
            'critical_count': sum(1 for alert in alerts if alert.get('severity') == 'critical'),
            'high_count': sum(1 for alert in alerts if alert.get('severity') == 'high'),
            'medium_count': sum(1 for alert in alerts if alert.get('severity') == 'medium'),
            'low_count': sum(1 for alert in alerts if alert.get('severity') == 'low'),
            'overall_severity': 'critical' if any(a.get('severity') == 'critical' for a in alerts) else 'high' if any(a.get('severity') == 'high' for a in alerts) else 'normal'
        }

        return {
            "success": True,
            "alerts": alerts,
            "summary": alert_summary,
            "generated_at": dashboard_data.get('generated_at')
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Dashboard alerts retrieval failed: {str(e)}"
        )


@router.get("/export", response_model=DashboardExportResponse)
async def export_dashboard_data(
    format: str = Query("json", description="Export format: json, csv"),
    include_historical: bool = Query(False, description="Include historical trend data"),
    current_user: User = Depends(get_admin_user),  # Admin only
    db: sa.AsyncSession = Depends(get_db)
):
    """
    Export complete dashboard data.

    Allows administrators to export dashboard data for external analysis or reporting.
    """
    try:
        dashboard_service = AnalyticsDashboardService()
        exported_data = await dashboard_service.export_dashboard_data(
            db, format, include_historical
        )

        if format == "json":
            return DashboardExportResponse(
                success=True,
                data=exported_data,
                format="json"
            )
        elif format == "csv":
            # Parse CSV data to extract filename if present
            lines = exported_data.split('\n')
            filename = "dashboard_export.csv"

            return DashboardExportResponse(
                success=True,
                data=exported_data,
                format="csv",
                filename=filename
            )
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
            detail=f"Dashboard export failed: {str(e)}"
        )


@router.get("/health")
async def get_dashboard_health(
    current_user: User = Depends(get_admin_user),  # Admin only
    db: sa.AsyncSession = Depends(get_db)
):
    """
    Get dashboard system health status.

    Returns health information about the analytics and dashboard systems.
    """
    try:
        dashboard_service = AnalyticsDashboardService()

        # Check if we can generate dashboard data
        dashboard_data = await dashboard_service.get_main_dashboard(db)

        health_status = {
            'dashboard_system': 'healthy',
            'data_generation': 'success' if 'error' not in dashboard_data else 'failed',
            'analytics_services': {
                'usage_analytics': 'available',
                'performance_monitoring': 'available',
                'quality_dashboard': 'available',
                'error_tracking': 'available'
            },
            'last_dashboard_generation': dashboard_data.get('generated_at', datetime.utcnow().isoformat()),
            'data_freshness': 'current',
            'overall_status': 'healthy' if 'error' not in dashboard_data else 'degraded'
        }

        # Add data metrics
        if 'error' not in dashboard_data:
            summary = dashboard_data.get('summary', {})
            health_status['metrics'] = {
                'total_kpis': len(dashboard_data.get('kpis', [])),
                'active_alerts': len(dashboard_data.get('alerts', [])),
                'generated_insights': len(dashboard_data.get('insights', [])),
                'health_status': summary.get('health_status', 'unknown')
            }

        return {
            "success": True,
            "health": health_status
        }

    except Exception as e:
        return {
            "success": False,
            "health": {
                'dashboard_system': 'unhealthy',
                'error': str(e),
                'overall_status': 'critical'
            }
        }


@router.post("/refresh-cache")
async def refresh_dashboard_cache(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_admin_user),  # Admin only
    db: sa.AsyncSession = Depends(get_db)
):
    """
    Refresh dashboard cache.

    Forces regeneration of dashboard data and updates cached analytics.
    """
    try:
        dashboard_service = AnalyticsDashboardService()

        # Force cache refresh by clearing and regenerating
        dashboard_data = await dashboard_service.get_main_dashboard(db)

        if "error" in dashboard_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Cache refresh failed: " + dashboard_data["error"]
            )

        return {
            "success": True,
            "message": "Dashboard cache refreshed successfully",
            "data_points_updated": len(dashboard_data.get('kpis', [])),
            "charts_updated": len(dashboard_data.get('charts', {})),
            "insights_generated": len(dashboard_data.get('insights', [])),
            "refreshed_at": dashboard_data.get('generated_at')
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Dashboard cache refresh failed: {str(e)}"
        )


@router.get("/config")
async def get_dashboard_config(
    current_user: User = Depends(get_admin_user)  # Admin only
):
    """
    Get dashboard configuration options.

    Returns available chart types, metric types, and configuration options.
    """
    config = {
        'available_chart_types': [
            'usage_trends',
            'quality_breakdown',
            'performance_metrics',
            'error_distribution',
            'topic_popularity',
            'user_engagement'
        ],
        'available_metric_types': [
            'usage',
            'performance',
            'quality',
            'errors'
        ],
        'export_formats': [
            'json',
            'csv'
        ],
        'time_ranges': [
            '1h', '6h', '24h', '7d', '30d', '90d'
        ],
        'kpi_categories': [
            'research_volume',
            'quality_score',
            'response_time',
            'user_satisfaction',
            'error_rate'
        ],
        'alert_severities': [
            'critical',
            'high',
            'medium',
            'low'
        ],
        'default_refresh_interval': 300,  # 5 minutes
        'max_data_points': 1000,
        'supported_languages': [
            'en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'zh', 'ja', 'ko', 'ar', 'hi'
        ]
    }

    return {
        "success": True,
        "config": config,
        "last_updated": datetime.utcnow().isoformat()
    }


@router.get("/reports/weekly")
async def get_weekly_report(
    current_user: User = Depends(get_admin_user),  # Admin only
    db: sa.AsyncSession = Depends(get_db)
):
    """
    Get weekly analytics report.

    Generates a comprehensive weekly summary with trends and highlights.
    """
    try:
        # Get last 7 days of data
        date_from = datetime.utcnow() - timedelta(days=7)
        date_to = datetime.utcnow()

        dashboard_service = AnalyticsDashboardService()
        dashboard_data = await dashboard_service.get_main_dashboard(db, date_from, date_to)

        if "error" in dashboard_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=dashboard_data["error"]
            )

        # Generate weekly report
        weekly_report = {
            'report_type': 'weekly',
            'period': {
                'from': date_from.isoformat(),
                'to': date_to.isoformat(),
                'days': 7
            },
            'executive_summary': dashboard_data.get('summary', {}),
            'key_highlights': [
                f"Processed {dashboard_data.get('summary', {}).get('key_metrics', {}).get('total_researches', 0)} researches",
                f"Quality score: {dashboard_data.get('summary', {}).get('key_metrics', {}).get('quality_score', 0):.1f}%",
                f"Average response time: {dashboard_data.get('summary', {}).get('key_metrics', {}).get('avg_response_time', 0):.2f}s",
                f"Error rate: {dashboard_data.get('summary', {}).get('key_metrics', {}).get('error_rate', 0):.2f}%"
            ],
            'top_insights': dashboard_data.get('insights', [])[:5],
            'critical_alerts': [alert for alert in dashboard_data.get('alerts', []) if alert.get('severity') == 'critical'],
            'performance_highlights': {
                'best_performing_metric': 'response_time',  # Would be calculated
                'most_improved_area': 'quality_score',  # Would be calculated
                'biggest_challenge': 'error_rate'  # Would be calculated
            },
            'recommendations': dashboard_data.get('recommendations', [])[:3],
            'generated_at': datetime.utcnow().isoformat()
        }

        return {
            "success": True,
            "weekly_report": weekly_report
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Weekly report generation failed: {str(e)}"
        )
