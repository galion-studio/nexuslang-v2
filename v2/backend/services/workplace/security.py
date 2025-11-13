"""
Workplace Service Security
Enhanced security features including rate limiting, input validation, and access control.
"""

import logging
import time
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict
import re

logger = logging.getLogger(__name__)


@dataclass
class RateLimitRule:
    """Rate limiting rule configuration."""
    requests_per_minute: int
    requests_per_hour: int
    burst_limit: int
    cooldown_seconds: int


@dataclass
class SecurityEvent:
    """Security event for logging."""
    event_type: str
    user_id: Optional[int]
    workspace_id: Optional[int]
    ip_address: str
    user_agent: str
    details: Dict[str, Any]
    timestamp: datetime
    severity: str  # low, medium, high, critical


class WorkplaceSecurityManager:
    """Enhanced security manager for workplace service."""

    def __init__(self):
        self.rate_limits = defaultdict(lambda: defaultdict(dict))
        self.security_events = []
        self.suspicious_activities = defaultdict(list)
        self.input_validation_rules = self._initialize_validation_rules()

        # Default rate limiting rules
        self.default_rules = {
            "sync_broadcast": RateLimitRule(30, 300, 10, 60),  # 30/min, 300/hour
            "ai_insights": RateLimitRule(10, 100, 5, 30),       # 10/min, 100/hour
            "time_logging": RateLimitRule(20, 200, 8, 30),      # 20/min, 200/hour
            "task_assignment": RateLimitRule(15, 150, 6, 30),   # 15/min, 150/hour
            "billing_generation": RateLimitRule(5, 50, 2, 60),  # 5/min, 50/hour
            "code_review": RateLimitRule(5, 30, 2, 60),         # 5/min, 30/hour
        }

    def _initialize_validation_rules(self) -> Dict[str, Any]:
        """Initialize input validation rules."""
        return {
            "workspace_name": {
                "pattern": r"^[a-zA-Z0-9\s\-_]{1,255}$",
                "max_length": 255,
                "min_length": 1,
                "allowed_chars": "alphanumeric, spaces, hyphens, underscores"
            },
            "task_title": {
                "pattern": r"^[a-zA-Z0-9\s\-_.,!?()]{1,500}$",
                "max_length": 500,
                "min_length": 1,
                "allowed_chars": "alphanumeric, spaces, punctuation"
            },
            "time_description": {
                "pattern": r"^[a-zA-Z0-9\s\-_.,!?()@#$%&*+=]{5,1000}$",
                "max_length": 1000,
                "min_length": 5,
                "allowed_chars": "alphanumeric, spaces, common symbols"
            },
            "code_content": {
                "max_length": 100000,  # 100KB limit
                "allowed_languages": ["python", "javascript", "typescript", "java", "cpp", "c", "go", "rust", "php", "ruby"],
                "dangerous_patterns": [
                    r"rm\s+-rf\s+/",  # Dangerous shell commands
                    r"os\.system\(.*rm.*\)",  # Python dangerous commands
                    r"eval\(.*\)",  # Code injection attempts
                    r"exec\(.*\)",  # Code execution attempts
                ]
            },
            "email": {
                "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
                "max_length": 255
            }
        }

    async def check_rate_limit(
        self,
        user_id: int,
        endpoint: str,
        ip_address: str
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if request exceeds rate limits.

        Returns:
            (allowed: bool, limit_info: dict)
        """
        current_time = time.time()
        rule = self.default_rules.get(endpoint, RateLimitRule(10, 100, 5, 30))

        # Create composite key for rate limiting (user + IP)
        rate_key = f"{user_id}:{ip_address}"

        if rate_key not in self.rate_limits:
            self.rate_limits[rate_key] = {
                "minute_requests": [],
                "hour_requests": [],
                "burst_count": 0,
                "cooldown_until": 0
            }

        limits = self.rate_limits[rate_key]

        # Clean old requests
        minute_ago = current_time - 60
        hour_ago = current_time - 3600

        limits["minute_requests"] = [t for t in limits["minute_requests"] if t > minute_ago]
        limits["hour_requests"] = [t for t in limits["hour_requests"] if t > hour_ago]

        # Check cooldown
        if current_time < limits["cooldown_until"]:
            remaining_cooldown = limits["cooldown_until"] - current_time
            return False, {
                "allowed": False,
                "reason": "cooldown_active",
                "retry_after": int(remaining_cooldown),
                "limit_info": {
                    "requests_per_minute": rule.requests_per_minute,
                    "requests_per_hour": rule.requests_per_hour
                }
            }

        # Check rate limits
        minute_count = len(limits["minute_requests"])
        hour_count = len(limits["hour_requests"])
        burst_count = limits["burst_count"]

        if minute_count >= rule.requests_per_minute:
            limits["cooldown_until"] = current_time + rule.cooldown_seconds
            await self._log_security_event(
                "rate_limit_exceeded",
                user_id,
                None,
                ip_address,
                "",
                {"endpoint": endpoint, "limit": "per_minute", "count": minute_count},
                "medium"
            )
            return False, {
                "allowed": False,
                "reason": "rate_limit_minute",
                "retry_after": rule.cooldown_seconds,
                "limit_info": {
                    "requests_per_minute": rule.requests_per_minute,
                    "current_minute": minute_count
                }
            }

        if hour_count >= rule.requests_per_hour:
            limits["cooldown_until"] = current_time + rule.cooldown_seconds
            await self._log_security_event(
                "rate_limit_exceeded",
                user_id,
                None,
                ip_address,
                "",
                {"endpoint": endpoint, "limit": "per_hour", "count": hour_count},
                "high"
            )
            return False, {
                "allowed": False,
                "reason": "rate_limit_hour",
                "retry_after": rule.cooldown_seconds,
                "limit_info": {
                    "requests_per_hour": rule.requests_per_hour,
                    "current_hour": hour_count
                }
            }

        if burst_count >= rule.burst_limit:
            limits["cooldown_until"] = current_time + rule.cooldown_seconds
            return False, {
                "allowed": False,
                "reason": "burst_limit",
                "retry_after": rule.cooldown_seconds,
                "limit_info": {
                    "burst_limit": rule.burst_limit,
                    "current_burst": burst_count
                }
            }

        # Record the request
        limits["minute_requests"].append(current_time)
        limits["hour_requests"].append(current_time)
        limits["burst_count"] += 1

        return True, {
            "allowed": True,
            "remaining_minute": rule.requests_per_minute - minute_count - 1,
            "remaining_hour": rule.requests_per_hour - hour_count - 1,
            "remaining_burst": rule.burst_limit - burst_count - 1
        }

    def validate_input(self, input_type: str, value: str) -> Tuple[bool, str]:
        """
        Validate input against security rules.

        Returns:
            (valid: bool, error_message: str)
        """
        if input_type not in self.input_validation_rules:
            return True, ""  # No validation rule defined

        rules = self.input_validation_rules[input_type]

        # Length checks
        if len(value) > rules.get("max_length", float('inf')):
            return False, f"Input exceeds maximum length of {rules['max_length']} characters"

        if len(value) < rules.get("min_length", 0):
            return False, f"Input must be at least {rules['min_length']} characters long"

        # Pattern validation
        if "pattern" in rules:
            if not re.match(rules["pattern"], value):
                return False, f"Input contains invalid characters. Allowed: {rules.get('allowed_chars', 'see documentation')}"

        # Dangerous pattern detection
        if "dangerous_patterns" in rules:
            for pattern in rules["dangerous_patterns"]:
                if re.search(pattern, value, re.IGNORECASE):
                    return False, "Input contains potentially dangerous content"

        # Language validation for code
        if input_type == "code_content" and "language" in rules:
            # This would be passed as a parameter, but for now we assume it's validated elsewhere

        return True, ""

    def sanitize_input(self, input_type: str, value: str) -> str:
        """Sanitize input to prevent injection attacks."""
        if input_type == "task_title" or input_type == "workspace_name":
            # Basic HTML escaping
            value = value.replace("&", "&amp;")
            value = value.replace("<", "&lt;")
            value = value.replace(">", "&gt;")
            value = value.replace('"', "&quot;")
            value = value.replace("'", "&#x27;")

        elif input_type == "time_description":
            # Allow more characters but still escape HTML
            value = value.replace("&", "&amp;")
            value = value.replace("<", "&lt;")
            value = value.replace(">", "&gt;")

        return value.strip()

    async def detect_suspicious_activity(
        self,
        user_id: int,
        ip_address: str,
        user_agent: str,
        activity: str,
        details: Dict[str, Any]
    ) -> bool:
        """
        Detect suspicious activity patterns.

        Returns:
            True if suspicious activity detected
        """
        # Track activities per user/IP
        activity_key = f"{user_id}:{ip_address}"
        self.suspicious_activities[activity_key].append({
            "activity": activity,
            "timestamp": datetime.utcnow(),
            "details": details,
            "user_agent": user_agent
        })

        # Keep only recent activities (last hour)
        cutoff = datetime.utcnow() - timedelta(hours=1)
        self.suspicious_activities[activity_key] = [
            act for act in self.suspicious_activities[activity_key]
            if act["timestamp"] > cutoff
        ]

        recent_activities = self.suspicious_activities[activity_key]

        # Check for suspicious patterns
        suspicious_patterns = {
            "rapid_api_calls": len([a for a in recent_activities if "api" in a["activity"]]) > 50,
            "failed_auth_attempts": len([a for a in recent_activities if "auth_fail" in a["activity"]]) > 5,
            "unusual_endpoints": any("unusual" in str(a["details"]) for a in recent_activities),
            "large_payloads": any(a["details"].get("payload_size", 0) > 1000000 for a in recent_activities),  # 1MB
        }

        if any(suspicious_patterns.values()):
            await self._log_security_event(
                "suspicious_activity_detected",
                user_id,
                None,
                ip_address,
                user_agent,
                {"patterns": suspicious_patterns, "recent_activities": len(recent_activities)},
                "high"
            )
            return True

        return False

    async def _log_security_event(
        self,
        event_type: str,
        user_id: Optional[int],
        workspace_id: Optional[int],
        ip_address: str,
        user_agent: str,
        details: Dict[str, Any],
        severity: str
    ):
        """Log a security event."""
        event = SecurityEvent(
            event_type=event_type,
            user_id=user_id,
            workspace_id=workspace_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details,
            timestamp=datetime.utcnow(),
            severity=severity
        )

        self.security_events.append(event)

        # Keep only recent events (last 1000)
        if len(self.security_events) > 1000:
            self.security_events = self.security_events[-1000:]

        # Log to system logger
        logger.warning(f"🔒 SECURITY EVENT: {event_type} | User: {user_id} | IP: {ip_address} | Severity: {severity}")

        # In production, you might want to:
        # - Send to security monitoring system
        # - Trigger alerts for high-severity events
        # - Store in dedicated security database

    def get_security_events(
        self,
        user_id: Optional[int] = None,
        severity: Optional[str] = None,
        limit: int = 100
    ) -> List[SecurityEvent]:
        """Get security events with optional filtering."""
        events = self.security_events

        if user_id is not None:
            events = [e for e in events if e.user_id == user_id]

        if severity:
            events = [e for e in events if e.severity == severity]

        return events[-limit:]

    def get_rate_limit_status(self, user_id: int, ip_address: str) -> Dict[str, Any]:
        """Get current rate limit status for a user/IP."""
        rate_key = f"{user_id}:{ip_address}"
        if rate_key in self.rate_limits:
            limits = self.rate_limits[rate_key]
            return {
                "minute_requests": len(limits["minute_requests"]),
                "hour_requests": len(limits["hour_requests"]),
                "burst_count": limits["burst_count"],
                "cooldown_remaining": max(0, limits["cooldown_until"] - time.time())
            }
        return {"status": "no_limits_recorded"}

    async def validate_workspace_access(
        self,
        user_id: int,
        workspace_id: int,
        required_role: Optional[str] = None,
        db_session = None
    ) -> Tuple[bool, str]:
        """
        Enhanced workspace access validation.

        Returns:
            (has_access: bool, reason: str)
        """
        try:
            from ..models.workplace import Workspace, WorkspaceMember

            # Check if workspace exists
            workspace = db_session.query(Workspace).filter(Workspace.id == workspace_id).first()
            if not workspace:
                return False, "workspace_not_found"

            # Check if user is owner
            if workspace.owner_id == user_id:
                return True, "owner_access"

            # Check membership and role
            member = db_session.query(WorkspaceMember).filter(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == user_id
            ).first()

            if not member:
                return False, "not_a_member"

            if required_role:
                role_hierarchy = {"viewer": 1, "member": 2, "admin": 3, "owner": 4}
                user_level = role_hierarchy.get(member.role, 0)
                required_level = role_hierarchy.get(required_role, 999)

                if user_level < required_level:
                    return False, f"insufficient_role_{member.role}_required_{required_role}"

            return True, "member_access"

        except Exception as e:
            logger.error(f"Workspace access validation failed: {e}")
            return False, "validation_error"

    def generate_secure_token(self, length: int = 32) -> str:
        """Generate a cryptographically secure token."""
        return secrets.token_urlsafe(length)

    def hash_sensitive_data(self, data: str) -> str:
        """Hash sensitive data for logging."""
        return hashlib.sha256(data.encode()).hexdigest()[:16]  # First 16 chars for brevity


# Global security manager instance
workplace_security = WorkplaceSecurityManager()


def create_security_middleware():
    """Create security middleware for FastAPI."""
    from fastapi import Request, Response, HTTPException
    from fastapi.responses import JSONResponse

    async def security_middleware(request: Request, call_next):
        # Get user info from request
        user_id = getattr(request.state, 'user_id', None)
        ip_address = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("User-Agent", "")

        # Determine endpoint for rate limiting
        endpoint = request.url.path.split("/")[-1] or "unknown"

        # Check rate limits
        if user_id:
            allowed, limit_info = await workplace_security.check_rate_limit(
                user_id, endpoint, ip_address
            )

            if not allowed:
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "rate_limit_exceeded",
                        "message": "Too many requests. Please try again later.",
                        "retry_after": limit_info.get("retry_after", 60),
                        "limit_info": limit_info.get("limit_info", {})
                    }
                )

        # Check for suspicious activity
        if user_id:
            is_suspicious = await workplace_security.detect_suspicious_activity(
                user_id, ip_address, user_agent, f"api_call_{endpoint}",
                {"method": request.method, "path": request.url.path}
            )

            if is_suspicious:
                logger.warning(f"Suspicious activity detected for user {user_id} from {ip_address}")

        try:
            response = await call_next(request)
            return response

        except Exception as e:
            # Log security-related errors
            await workplace_security._log_security_event(
                "api_error",
                user_id,
                None,
                ip_address,
                user_agent,
                {"error": str(e), "endpoint": endpoint},
                "low"
            )
            raise

    return security_middleware
