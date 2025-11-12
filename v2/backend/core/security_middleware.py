"""
Security Middleware Suite for NexusLang v2
Implements rate limiting, security headers, audit logging, and request validation.

Built with first principles approach: simple, effective, minimal complexity.
"""

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable, Dict, Optional
import time
import hashlib
import uuid
from collections import defaultdict
from datetime import datetime, timezone
import json


# ==================== RATE LIMITING ====================

class RateLimiter:
    """
    Simple in-memory rate limiter.
    
    For production: Use Redis for distributed rate limiting.
    This implementation is intentionally simple but effective.
    """
    
    def __init__(self):
        # Store: {client_id: [(timestamp, count), ...]}
        self.requests: Dict[str, list] = defaultdict(list)
        # Cleanup old entries periodically
        self.last_cleanup = time.time()
    
    def _cleanup_old_entries(self, now: float, window_seconds: int = 60):
        """Remove entries older than window. Run periodically to prevent memory bloat."""
        if now - self.last_cleanup > 300:  # Cleanup every 5 minutes
            cutoff = now - window_seconds
            for client_id in list(self.requests.keys()):
                self.requests[client_id] = [
                    (ts, count) for ts, count in self.requests[client_id]
                    if ts > cutoff
                ]
                if not self.requests[client_id]:
                    del self.requests[client_id]
            self.last_cleanup = now
    
    def is_allowed(
        self, 
        client_id: str, 
        max_requests: int = 60, 
        window_seconds: int = 60
    ) -> tuple[bool, dict]:
        """
        Check if request is allowed under rate limit.
        
        Args:
            client_id: Unique identifier (IP, user_id, or combo)
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
        
        Returns:
            (allowed, info_dict) where info_dict contains limit/remaining/reset
        """
        now = time.time()
        cutoff = now - window_seconds
        
        # Cleanup old entries periodically
        self._cleanup_old_entries(now, window_seconds)
        
        # Get requests in current window
        recent_requests = [
            (ts, count) for ts, count in self.requests[client_id]
            if ts > cutoff
        ]
        
        # Calculate total requests in window
        total_requests = sum(count for _, count in recent_requests)
        
        # Check if under limit
        if total_requests >= max_requests:
            return False, {
                "limit": max_requests,
                "remaining": 0,
                "reset": int(cutoff + window_seconds)
            }
        
        # Add this request
        self.requests[client_id] = recent_requests + [(now, 1)]
        
        return True, {
            "limit": max_requests,
            "remaining": max_requests - total_requests - 1,
            "reset": int(now + window_seconds)
        }


# Global rate limiter instance
_rate_limiter = RateLimiter()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware with sensible defaults.
    
    Different limits for different endpoint types:
    - Auth endpoints: Stricter (prevent brute force)
    - Code execution: Medium (prevent abuse)
    - General API: Relaxed (normal use)
    """
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Skip rate limiting for health checks and docs
        if request.url.path in ["/health", "/", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        # Determine rate limit based on endpoint
        path = request.url.path
        if "/auth/login" in path or "/auth/register" in path:
            max_requests, window = 10, 300  # 10 per 5 minutes (prevent brute force)
        elif "/nexuslang/execute" in path:
            max_requests, window = 30, 60  # 30 per minute (prevent abuse)
        elif "/voice/" in path:
            max_requests, window = 20, 60  # 20 per minute (voice is expensive)
        else:
            max_requests, window = 100, 60  # 100 per minute (general API)
        
        # Get client identifier (IP address + user agent hash for uniqueness)
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "")
        ua_hash = hashlib.md5(user_agent.encode()).hexdigest()[:8]
        client_id = f"{client_ip}:{ua_hash}"
        
        # Check rate limit
        allowed, info = _rate_limiter.is_allowed(client_id, max_requests, window)
        
        if not allowed:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Try again after {info['reset'] - int(time.time())} seconds.",
                    "limit": info["limit"],
                    "reset": info["reset"]
                },
                headers={
                    "X-RateLimit-Limit": str(info["limit"]),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(info["reset"]),
                    "Retry-After": str(info["reset"] - int(time.time()))
                }
            )
        
        # Process request and add rate limit headers
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
        response.headers["X-RateLimit-Reset"] = str(info["reset"])
        
        return response


# ==================== SECURITY HEADERS ====================

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add security headers to all responses.
    
    These headers protect against common web vulnerabilities:
    - XSS attacks
    - Clickjacking
    - MIME sniffing
    - Man-in-the-middle attacks
    """
    
    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)
        
        # Prevent browsers from MIME-sniffing a response away from declared content-type
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Prevent page from being displayed in iframe (clickjacking protection)
        response.headers["X-Frame-Options"] = "DENY"
        
        # Enable browser's XSS protection (legacy but harmless)
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Force HTTPS for 1 year (31536000 seconds)
        # Only in production - dev often uses HTTP
        if not request.url.hostname in ["localhost", "127.0.0.1"]:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Content Security Policy - restrict what resources can be loaded
        # Adjust based on your frontend needs
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "  # Relaxed for dev, tighten for production
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https:; "
            "frame-ancestors 'none';"
        )
        
        # Permissions Policy - control what browser features can be used
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=(), "
            "magnetometer=(), "
            "gyroscope=(), "
            "accelerometer=()"
        )
        
        # Referrer Policy - control referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response


# ==================== AUDIT LOGGING ====================

class AuditLogger:
    """
    Centralized audit logging for security events.
    
    Logs:
    - Authentication attempts (success/failure)
    - Authorization failures
    - Code execution
    - Admin actions
    - Data access
    
    In production: Send to centralized logging system (ELK, Splunk, etc.)
    """
    
    def __init__(self):
        self.events = []  # In-memory for demo, use proper logging in production
    
    def log_event(
        self,
        event_type: str,
        user_id: Optional[str],
        request: Request,
        details: dict,
        severity: str = "info"
    ):
        """
        Log a security event.
        
        Args:
            event_type: Type of event (auth, exec, access, etc.)
            user_id: User ID if authenticated
            request: FastAPI request object
            details: Event-specific details
            severity: info, warning, error, critical
        """
        event = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": event_type,
            "severity": severity,
            "user_id": user_id,
            "ip_address": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
            "method": request.method,
            "path": request.url.path,
            "details": details
        }
        
        # Log to stdout (can be collected by logging infrastructure)
        print(f"[AUDIT] {json.dumps(event)}")
        
        # Keep in memory for queries (in production, use database)
        self.events.append(event)
        
        # Limit memory usage
        if len(self.events) > 10000:
            self.events = self.events[-5000:]  # Keep last 5000
    
    def get_recent_events(self, limit: int = 100) -> list:
        """Get recent audit events."""
        return self.events[-limit:]


# Global audit logger instance
_audit_logger = AuditLogger()


def get_audit_logger() -> AuditLogger:
    """Get global audit logger instance."""
    return _audit_logger


class AuditLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log security-relevant requests.
    
    Logs all authentication, code execution, and sensitive operations.
    """
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Log sensitive endpoints
        path = request.url.path
        
        # Extract user ID from token if present
        user_id = None
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            from ..core.security import decode_access_token
            token = auth_header[7:]
            payload = decode_access_token(token)
            if payload:
                user_id = payload.get("sub")
        
        # Track if we should log this request
        should_log = False
        event_type = "request"
        severity = "info"
        
        if "/auth/" in path:
            should_log = True
            event_type = "auth"
        elif "/nexuslang/execute" in path:
            should_log = True
            event_type = "code_execution"
            severity = "warning"  # Code execution is always noteworthy
        elif "/admin/" in path:
            should_log = True
            event_type = "admin_action"
            severity = "warning"
        
        # Execute request
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time
        
        # Log after response (we know status code)
        if should_log:
            _audit_logger.log_event(
                event_type=event_type,
                user_id=user_id,
                request=request,
                details={
                    "status_code": response.status_code,
                    "duration_ms": round(duration * 1000, 2),
                    "success": 200 <= response.status_code < 300
                },
                severity=severity if response.status_code < 400 else "error"
            )
        
        return response


# ==================== REQUEST VALIDATION ====================

class RequestValidationMiddleware(BaseHTTPMiddleware):
    """
    Validate and sanitize incoming requests.
    
    - Check request size limits
    - Validate content types
    - Add request ID for tracing
    """
    
    MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10MB default
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Add unique request ID for tracing
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Check content length
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.MAX_REQUEST_SIZE:
            return JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content={
                    "error": "Request too large",
                    "max_size_mb": self.MAX_REQUEST_SIZE / (1024 * 1024)
                }
            )
        
        # Validate content type for POST/PUT/PATCH
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("content-type", "")
            valid_types = ["application/json", "multipart/form-data", "application/x-www-form-urlencoded"]
            
            # Check if content type is valid (handle charset suffix)
            is_valid = any(ct in content_type for ct in valid_types)
            
            if not is_valid and content_type:  # Only check if content-type is provided
                return JSONResponse(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    content={
                        "error": "Unsupported content type",
                        "supported_types": valid_types
                    }
                )
        
        # Process request
        response = await call_next(request)
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response


# ==================== HELPER FUNCTIONS ====================

def get_rate_limit_info(client_id: str) -> dict:
    """Get current rate limit info for a client."""
    allowed, info = _rate_limiter.is_allowed(client_id, max_requests=1000000, window_seconds=1)
    return info

