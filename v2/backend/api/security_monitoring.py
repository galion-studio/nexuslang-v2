"""
Security Monitoring API

Provides endpoints for:
- Security event dashboard
- Audit log queries
- Security metrics
- Active sessions
- Threat detection alerts
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import uuid

from ..core.security_middleware import get_audit_logger
from ..core.redis_client import get_redis
from ..api.auth import get_current_user
from ..models.user import User

router = APIRouter()


# ==================== MODELS ====================

class SecurityEvent(BaseModel):
    """Security event model."""
    id: str
    timestamp: str
    type: str
    severity: str
    user_id: Optional[str]
    ip_address: Optional[str]
    details: dict


class SecurityMetrics(BaseModel):
    """Security metrics summary."""
    total_events: int
    failed_logins: int
    successful_logins: int
    blocked_requests: int
    code_executions: int
    websocket_connections: int
    uptime_hours: float


class ActiveSession(BaseModel):
    """Active user session."""
    user_id: str
    ip_address: str
    user_agent: str
    last_activity: str
    duration_minutes: int


# ==================== ENDPOINTS ====================

@router.get("/events", response_model=List[SecurityEvent])
async def get_security_events(
    limit: int = 100,
    severity: Optional[str] = None,
    event_type: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Get recent security events.
    
    Requires authentication. Admins see all events.
    Regular users see only their own events.
    """
    # Get audit logger
    logger = get_audit_logger()
    events = logger.get_recent_events(limit=limit)
    
    # Filter by severity if specified
    if severity:
        events = [e for e in events if e.get("severity") == severity]
    
    # Filter by type if specified
    if event_type:
        events = [e for e in events if e.get("type") == event_type]
    
    # Non-admin users only see their own events
    # TODO: Implement role-based access control
    # For now, admins are users with is_verified=True (placeholder)
    if not current_user.is_verified:
        events = [e for e in events if e.get("user_id") == str(current_user.id)]
    
    # Convert to response model
    return [
        SecurityEvent(
            id=e.get("id", str(uuid.uuid4())),
            timestamp=e.get("timestamp", ""),
            type=e.get("type", "unknown"),
            severity=e.get("severity", "info"),
            user_id=e.get("user_id"),
            ip_address=e.get("ip_address"),
            details=e.get("details", {})
        )
        for e in events
    ]


@router.get("/metrics", response_model=SecurityMetrics)
async def get_security_metrics(
    current_user: User = Depends(get_current_user)
):
    """
    Get security metrics summary.
    
    Returns counts of various security events.
    """
    # Get audit logger
    logger = get_audit_logger()
    events = logger.get_recent_events(limit=10000)
    
    # Calculate metrics
    failed_logins = sum(1 for e in events if e.get("type") == "auth" and not e.get("details", {}).get("success"))
    successful_logins = sum(1 for e in events if e.get("type") == "auth" and e.get("details", {}).get("success"))
    blocked_requests = sum(1 for e in events if e.get("severity") == "error")
    code_executions = sum(1 for e in events if e.get("type") == "code_execution")
    websocket_connections = sum(1 for e in events if e.get("type") == "websocket_connect")
    
    return SecurityMetrics(
        total_events=len(events),
        failed_logins=failed_logins,
        successful_logins=successful_logins,
        blocked_requests=blocked_requests,
        code_executions=code_executions,
        websocket_connections=websocket_connections,
        uptime_hours=24.0  # Placeholder - implement proper uptime tracking
    )


@router.get("/failed-logins/{identifier}")
async def get_failed_login_attempts(
    identifier: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get failed login attempts for an email/IP.
    
    Useful for checking if account is close to lockout.
    """
    redis = await get_redis()
    failed_count = await redis.get_failed_login_count(identifier)
    is_locked, remaining = await redis.is_account_locked(identifier)
    
    return {
        "identifier": identifier,
        "failed_attempts": failed_count,
        "is_locked": is_locked,
        "remaining_attempts": remaining,
        "lockout_duration_minutes": 30 if is_locked else 0
    }


@router.post("/clear-lockout/{email}")
async def clear_account_lockout(
    email: str,
    current_user: User = Depends(get_current_user)
):
    """
    Clear account lockout for a user.
    
    Admin only. Useful for legitimate lockouts.
    """
    # TODO: Implement proper admin check
    # For now, require verified user
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    redis = await get_redis()
    await redis.clear_failed_logins(email)
    
    return {
        "message": f"Lockout cleared for {email}"
    }


@router.get("/rate-limit-status")
async def get_rate_limit_status(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's rate limit status.
    
    Shows how many requests remaining.
    """
    # This is informational - actual rate limiting happens in middleware
    return {
        "message": "Rate limits are enforced per-endpoint",
        "limits": {
            "auth_endpoints": "10 per 5 minutes",
            "code_execution": "30 per minute",
            "voice_endpoints": "20 per minute",
            "general_api": "100 per minute"
        },
        "note": "Check response headers for X-RateLimit-* information"
    }


@router.get("/threat-alerts")
async def get_threat_alerts(
    current_user: User = Depends(get_current_user)
):
    """
    Get recent security threat alerts.
    
    Identifies suspicious patterns:
    - Repeated failed logins
    - Unusual access patterns
    - Potential attacks
    """
    # Get recent failed login patterns
    logger = get_audit_logger()
    events = logger.get_recent_events(limit=1000)
    
    # Detect suspicious patterns
    alerts = []
    
    # Pattern 1: Multiple failed logins from same IP
    ip_failures = {}
    for event in events:
        if event.get("type") == "auth" and not event.get("details", {}).get("success"):
            ip = event.get("ip_address")
            if ip:
                ip_failures[ip] = ip_failures.get(ip, 0) + 1
    
    for ip, count in ip_failures.items():
        if count >= 5:
            alerts.append({
                "type": "brute_force_attempt",
                "severity": "high" if count >= 10 else "medium",
                "source_ip": ip,
                "failed_attempts": count,
                "message": f"Possible brute force attack from {ip} ({count} failed logins)"
            })
    
    # Pattern 2: Code execution errors (possible exploit attempts)
    code_errors = sum(1 for e in events 
                     if e.get("type") == "code_execution" 
                     and not e.get("details", {}).get("success"))
    
    if code_errors >= 10:
        alerts.append({
            "type": "suspicious_code_execution",
            "severity": "medium",
            "count": code_errors,
            "message": f"{code_errors} failed code executions - possible exploit attempts"
        })
    
    # Pattern 3: Rate limit violations
    rate_limit_violations = sum(1 for e in events if "rate limit" in str(e.get("details", {})).lower())
    
    if rate_limit_violations >= 5:
        alerts.append({
            "type": "rate_limit_abuse",
            "severity": "low",
            "count": rate_limit_violations,
            "message": f"{rate_limit_violations} rate limit violations detected"
        })
    
    return {
        "alert_count": len(alerts),
        "alerts": alerts,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/export-logs")
async def export_security_logs(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Export security logs for compliance/auditing.
    
    Returns logs in JSON format.
    """
    # TODO: Implement proper admin check
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    logger = get_audit_logger()
    events = logger.get_recent_events(limit=10000)
    
    # Filter by date range if specified
    if start_date:
        events = [e for e in events if e.get("timestamp", "") >= start_date]
    if end_date:
        events = [e for e in events if e.get("timestamp", "") <= end_date]
    
    return {
        "export_date": datetime.utcnow().isoformat(),
        "event_count": len(events),
        "events": events,
        "format": "json",
        "note": "Save this response for compliance records"
    }

