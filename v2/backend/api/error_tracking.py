"""
Error tracking and alerting API routes.
Provides access to error data, alerts, and error tracking configuration.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from ..api.auth import get_admin_user
from ..models.user import User
from ..services.error_tracking.error_tracker import get_error_tracker

router = APIRouter()


# Request/Response Models

class ErrorSummaryResponse(BaseModel):
    """Response model for error summary."""
    success: bool
    summary: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ErrorGroupsResponse(BaseModel):
    """Response model for error groups."""
    success: bool
    error_groups: List[Dict[str, Any]]
    total_groups: int
    error: Optional[str] = None


class ErrorDetailsResponse(BaseModel):
    """Response model for error details."""
    success: bool
    error_details: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ErrorTrendsResponse(BaseModel):
    """Response model for error trends."""
    success: bool
    trends: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class AlertRuleRequest(BaseModel):
    """Request model for adding alert rules."""
    name: str = Field(..., description="Alert rule name")
    condition_type: str = Field(..., description="Type of condition: error_rate, critical_errors, etc.")
    threshold: float = Field(..., description="Threshold value")
    severity: str = Field("warning", description="Alert severity: info, warning, error, critical")
    cooldown_minutes: int = Field(60, description="Cooldown period in minutes")


class AlertRulesResponse(BaseModel):
    """Response model for alert rules."""
    success: bool
    rules: List[Dict[str, Any]]
    total_rules: int
    error: Optional[str] = None


class NotificationConfigRequest(BaseModel):
    """Request model for notification configuration."""
    channel: str = Field(..., description="Notification channel: email, webhook")
    enabled: bool = Field(True, description="Enable/disable the channel")
    config: Dict[str, Any] = Field(..., description="Channel-specific configuration")


class NotificationConfigResponse(BaseModel):
    """Response model for notification configuration."""
    success: bool
    config: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class AlertsResponse(BaseModel):
    """Response model for alerts."""
    success: bool
    alerts: List[Dict[str, Any]]
    total_alerts: int
    error: Optional[str] = None


class HealthStatusResponse(BaseModel):
    """Response model for health status."""
    success: bool
    health_status: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# API Endpoints

@router.get("/summary", response_model=ErrorSummaryResponse)
async def get_error_summary(
    hours: int = Query(1, ge=1, le=168, description="Hours of data to summarize"),
    current_user: User = Depends(get_admin_user)  # Admin only
):
    """
    Get error summary statistics.

    Returns comprehensive error statistics including counts, rates, and trends.
    """
    try:
        tracker = get_error_tracker()
        summary = tracker.get_error_summary(hours=hours)

        return ErrorSummaryResponse(success=True, summary=summary)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error summary retrieval failed: {str(e)}"
        )


@router.get("/groups", response_model=ErrorGroupsResponse)
async def get_error_groups(
    limit: int = Query(50, ge=1, le=500, description="Maximum number of groups to return"),
    min_occurrences: int = Query(1, ge=1, description="Minimum occurrences to include"),
    current_user: User = Depends(get_admin_user)  # Admin only
):
    """
    Get error groups and patterns.

    Returns grouped error patterns with occurrence counts and frequencies.
    """
    try:
        tracker = get_error_tracker()
        all_groups = tracker.get_error_groups(limit=500)  # Get more to filter

        # Filter by minimum occurrences
        filtered_groups = [g for g in all_groups if g['count'] >= min_occurrences]

        return ErrorGroupsResponse(
            success=True,
            error_groups=filtered_groups[:limit],
            total_groups=len(filtered_groups)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error groups retrieval failed: {str(e)}"
        )


@router.get("/details/{error_id}", response_model=ErrorDetailsResponse)
async def get_error_details(
    error_id: str,
    current_user: User = Depends(get_admin_user)  # Admin only
):
    """
    Get detailed information about a specific error.

    Returns complete error information including traceback and context.
    """
    try:
        tracker = get_error_tracker()
        error_details = tracker.get_error_details(error_id)

        if not error_details:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Error with ID '{error_id}' not found"
            )

        return ErrorDetailsResponse(success=True, error_details=error_details)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error details retrieval failed: {str(e)}"
        )


@router.get("/trends", response_model=ErrorTrendsResponse)
async def get_error_trends(
    days: int = Query(7, ge=1, le=90, description="Days of trend data to analyze"),
    current_user: User = Depends(get_admin_user)  # Admin only
):
    """
    Get error trends over time.

    Returns time-series data showing error patterns and trends.
    """
    try:
        tracker = get_error_tracker()
        trends = tracker.get_error_trends(days=days)

        return ErrorTrendsResponse(success=True, trends=trends)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error trends retrieval failed: {str(e)}"
        )


@router.post("/rules", response_model=Dict[str, Any])
async def add_alert_rule(
    rule: AlertRuleRequest,
    current_user: User = Depends(get_admin_user)  # Admin only
):
    """
    Add a new alert rule.

    Creates custom alerting rules for error conditions.
    """
    try:
        tracker = get_error_tracker()

        # Convert condition type to actual condition function
        condition_map = {
            'error_rate': lambda data, threshold: data.get('error_rate', 0) > threshold,
            'critical_errors': lambda data, threshold: data.get('critical_errors_last_hour', 0) >= threshold,
            'repeated_errors': lambda data, threshold: data.get('repeated_error_groups', 0) >= threshold,
            'total_errors': lambda data, threshold: data.get('total_errors', 0) >= threshold
        }

        if rule.condition_type not in condition_map:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported condition type: {rule.condition_type}"
            )

        condition_func = condition_map[rule.condition_type]

        tracker.add_alert_rule(
            rule.name,
            condition_func,
            rule.threshold,
            rule.severity,
            rule.cooldown_minutes
        )

        return {
            "success": True,
            "message": f"Alert rule '{rule.name}' added successfully",
            "rule": {
                "name": rule.name,
                "condition_type": rule.condition_type,
                "threshold": rule.threshold,
                "severity": rule.severity,
                "cooldown_minutes": rule.cooldown_minutes
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Alert rule creation failed: {str(e)}"
        )


@router.get("/rules", response_model=AlertRulesResponse)
async def get_alert_rules(
    current_user: User = Depends(get_admin_user)  # Admin only
):
    """
    Get all configured alert rules.

    Returns information about active alerting rules and their configurations.
    """
    try:
        tracker = get_error_tracker()

        rules = []
        for rule in tracker.alert_rules:
            rules.append({
                "name": rule.name,
                "threshold": rule.threshold,
                "severity": rule.severity,
                "cooldown_minutes": rule.cooldown_minutes,
                "last_triggered": rule.last_triggered.isoformat() if rule.last_triggered else None
            })

        return AlertRulesResponse(
            success=True,
            rules=rules,
            total_rules=len(rules)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Alert rules retrieval failed: {str(e)}"
        )


@router.put("/notifications/{channel}")
async def configure_notifications(
    channel: str,
    config: NotificationConfigRequest,
    current_user: User = Depends(get_admin_user)  # Admin only
):
    """
    Configure notification settings.

    Sets up email, webhook, or other notification channels for alerts.
    """
    try:
        tracker = get_error_tracker()

        if channel not in ['email', 'webhook']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported notification channel: {channel}"
            )

        tracker.configure_notifications(channel, config.dict())

        return {
            "success": True,
            "message": f"Notification configuration updated for {channel}",
            "channel": channel,
            "enabled": config.enabled
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Notification configuration failed: {str(e)}"
        )


@router.get("/notifications/config")
async def get_notification_config(
    current_user: User = Depends(get_admin_user)  # Admin only
):
    """
    Get current notification configuration.

    Returns the current settings for all notification channels.
    """
    try:
        tracker = get_error_tracker()

        return {
            "success": True,
            "config": tracker.notification_config
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Notification config retrieval failed: {str(e)}"
        )


@router.get("/alerts", response_model=AlertsResponse)
async def get_recent_alerts(
    limit: int = Query(50, ge=1, le=500, description="Maximum number of alerts to return"),
    severity: Optional[str] = Query(None, description="Filter by severity: info, warning, error, critical"),
    current_user: User = Depends(get_admin_user)  # Admin only
):
    """
    Get recent alerts.

    Returns the most recent alerts generated by the system.
    """
    try:
        tracker = get_error_tracker()

        alerts = tracker.notifications_sent[-limit:]

        if severity:
            alerts = [a for a in alerts if a.get('severity') == severity]

        return AlertsResponse(
            success=True,
            alerts=alerts,
            total_alerts=len(alerts)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Recent alerts retrieval failed: {str(e)}"
        )


@router.get("/health", response_model=HealthStatusResponse)
async def get_error_tracking_health():
    """
    Get error tracking system health status.

    Returns health information about the error tracking and alerting system.
    """
    try:
        tracker = get_error_tracker()
        health_status = tracker.get_health_status()

        return HealthStatusResponse(success=True, health_status=health_status)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health status retrieval failed: {str(e)}"
        )


@router.post("/test-alert")
async def test_alert_system(
    rule_name: str = Query(..., description="Name of alert rule to test"),
    current_user: User = Depends(get_admin_user)  # Admin only
):
    """
    Test the alert system.

    Triggers a test alert to verify notification channels are working.
    """
    try:
        tracker = get_error_tracker()

        # Create a test alert
        test_alert = {
            'rule_name': f"test_{rule_name}",
            'severity': 'info',
            'threshold': 1,
            'current_value': 1,
            'timestamp': datetime.utcnow().isoformat(),
            'error_summary': {
                'total_errors': 1,
                'error_rate': 0.1
            }
        }

        # Send test notifications
        await tracker._send_notifications(test_alert)

        return {
            "success": True,
            "message": "Test alert sent to configured notification channels",
            "test_alert": test_alert
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Alert system test failed: {str(e)}"
        )


@router.get("/export")
async def export_error_data(
    format: str = Query("json", description="Export format: json, csv"),
    days: int = Query(7, ge=1, le=90, description="Days of data to export"),
    current_user: User = Depends(get_admin_user)  # Admin only
):
    """
    Export error data for external analysis.

    Allows administrators to export error data for further analysis.
    """
    try:
        tracker = get_error_tracker()
        exported_data = tracker.export_errors(format=format, days=days)

        if format == "json":
            return {
                "success": True,
                "data": exported_data,
                "format": "json",
                "days": days
            }
        elif format == "csv":
            return {
                "success": True,
                "data": exported_data,
                "format": "csv",
                "filename": f"errors_export_{datetime.utcnow().date()}.csv",
                "days": days
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
            detail=f"Error data export failed: {str(e)}"
        )


@router.post("/maintenance/cleanup")
async def cleanup_old_errors(
    background_tasks: BackgroundTasks,
    days_to_keep: int = Query(30, ge=1, le=365, description="Days of error data to retain"),
    current_user: User = Depends(get_admin_user)  # Admin only
):
    """
    Clean up old error data.

    Removes error data older than the specified retention period.
    """
    try:
        tracker = get_error_tracker()

        # Perform cleanup
        tracker.clear_errors(days_to_keep=days_to_keep)

        return {
            "success": True,
            "message": f"Cleaned up error data older than {days_to_keep} days",
            "retention_days": days_to_keep,
            "remaining_errors": len(tracker.errors),
            "remaining_groups": len(tracker.error_groups)
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error cleanup failed: {str(e)}"
        )


@router.get("/stats")
async def get_error_tracking_stats(
    current_user: User = Depends(get_admin_user)  # Admin only
):
    """
    Get error tracking system statistics.

    Returns comprehensive statistics about the error tracking system itself.
    """
    try:
        tracker = get_error_tracker()

        stats = {
            "total_errors_captured": len(tracker.errors),
            "error_groups": len(tracker.error_groups),
            "alert_rules": len(tracker.alert_rules),
            "notifications_sent": len(tracker.notifications_sent),
            "storage_limit": tracker.max_errors_stored,
            "group_size_limit": tracker.max_group_size,
            "notification_channels": list(tracker.notification_channels.keys()),
            "enabled_channels": [ch for ch, config in tracker.notification_config.items() if config.get('enabled', False)]
        }

        # Add time-based stats
        recent_summary = tracker.get_error_summary(hours=24)
        stats.update({
            "errors_last_24h": recent_summary["total_errors"],
            "error_rate_24h": recent_summary["error_rate"],
            "critical_errors_24h": recent_summary["critical_errors_last_hour"]
        })

        return {
            "success": True,
            "stats": stats,
            "generated_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error tracking stats retrieval failed: {str(e)}"
        )


@router.post("/capture")
async def manually_capture_error(
    error_type: str = Query(..., description="Error type"),
    message: str = Query(..., description="Error message"),
    severity: str = Query("error", description="Error severity"),
    context: Optional[str] = Query(None, description="JSON context string"),
    current_user: User = Depends(get_admin_user)  # Admin only
):
    """
    Manually capture an error event.

    Allows administrators to manually log errors for testing or monitoring purposes.
    """
    try:
        tracker = get_error_tracker()

        # Parse context if provided
        parsed_context = None
        if context:
            try:
                parsed_context = eval(context)  # Simple JSON parsing
            except:
                parsed_context = {"raw_context": context}

        error_id = tracker.capture_error(
            error_type=error_type,
            message=message,
            context=parsed_context,
            severity=severity
        )

        return {
            "success": True,
            "message": "Error captured successfully",
            "error_id": error_id,
            "error_type": error_type,
            "severity": severity
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Manual error capture failed: {str(e)}"
        )
