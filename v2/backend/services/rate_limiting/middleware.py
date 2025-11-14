"""
FastAPI middleware for rate limiting Deep Search APIs.
"""

import logging
from typing import Callable
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
import time

from .rate_limiter import get_rate_limiter, RateLimitExceeded

logger = logging.getLogger(__name__)


class RateLimitMiddleware:
    """
    FastAPI middleware for automatic rate limiting.

    Applies rate limits based on:
    - Client IP address
    - API endpoint
    - User authentication (if available)
    """

    def __init__(self, app: Callable, exclude_paths: list = None):
        self.app = app
        self.exclude_paths = exclude_paths or ["/health", "/metrics", "/docs", "/openapi.json"]

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Create ASGI request object for easier handling
        request = Request(scope, receive)

        # Skip rate limiting for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            await self.app(scope, receive, send)
            return

        try:
            # Get client identifier (IP address)
            client_ip = self._get_client_ip(request)

            # Determine endpoint type
            endpoint = self._classify_endpoint(request.url.path)

            # Get user ID if authenticated (you might want to customize this)
            user_id = self._get_user_id(request)

            # Check rate limit
            rate_limiter = await get_rate_limiter()
            allowed, limit_info = await rate_limiter.check_rate_limit(
                client_ip, endpoint, user_id
            )

            if not allowed:
                # Rate limit exceeded
                response_data = {
                    "error": "rate_limit_exceeded",
                    "message": f"Rate limit exceeded: {limit_info.get('limit', 0)} requests per {limit_info.get('window', 60)} seconds",
                    "limit": limit_info.get("limit", 0),
                    "window": limit_info.get("window", 60),
                    "retry_after": limit_info.get("retry_after", 60),
                    "current": limit_info.get("current", 0)
                }

                response = JSONResponse(
                    status_code=429,
                    content=response_data,
                    headers={
                        "Retry-After": str(limit_info.get("retry_after", 60)),
                        "X-RateLimit-Limit": str(limit_info.get("limit", 0)),
                        "X-RateLimit-Remaining": str(max(0, limit_info.get("limit", 0) - limit_info.get("current", 0))),
                        "X-RateLimit-Reset": str(int(time.time()) + limit_info.get("retry_after", 60))
                    }
                )

                await response(scope, receive, send)
                return

            # Add rate limit headers to successful requests
            original_send = send

            async def send_with_headers(message):
                if message["type"] == "http.response.start":
                    headers = message.get("headers", [])
                    # Add rate limit headers
                    headers.extend([
                        (b"X-RateLimit-Limit", str(limit_info.get("main_limit", 0)).encode()),
                        (b"X-RateLimit-Remaining", str(max(0, limit_info.get("main_limit", 0) - limit_info.get("main_current", 0))).encode()),
                        (b"X-RateLimit-Reset", str(int(time.time()) + limit_info.get("main_window", 3600))).encode()),
                        (b"X-RateLimit-Burst-Limit", str(limit_info.get("burst_limit", 0)).encode()),
                        (b"X-RateLimit-Burst-Remaining", str(max(0, limit_info.get("burst_limit", 0) - limit_info.get("burst_current", 0))).encode()),
                    ])
                    message["headers"] = headers

                await original_send(message)

            await self.app(scope, receive, send_with_headers)

        except Exception as e:
            logger.error(f"Rate limiting middleware error: {e}")
            # On error, allow the request to proceed
            await self.app(scope, receive, send)

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request."""
        # Check X-Forwarded-For header (for proxies/load balancers)
        x_forwarded_for = request.headers.get("X-Forwarded-For")
        if x_forwarded_for:
            # Take the first IP in case of multiple
            return x_forwarded_for.split(",")[0].strip()

        # Check X-Real-IP header
        x_real_ip = request.headers.get("X-Real-IP")
        if x_real_ip:
            return x_real_ip

        # Fall back to direct client IP
        client = request.client
        if client:
            return client.host

        # Final fallback
        return "unknown"

    def _classify_endpoint(self, path: str) -> str:
        """Classify API endpoint for rate limiting."""
        if path.startswith("/api/v2/grokopedia/deep-research"):
            return "deep_research"
        elif path.startswith("/api/v2/ai/deep-search"):
            return "deep_search"
        elif path.startswith("/api/v2/analytics"):
            return "analytics"
        elif path.startswith("/api/v2/admin"):
            return "admin"
        else:
            return "default"

    def _get_user_id(self, request: Request) -> str:
        """Extract user ID from request (if authenticated)."""
        # This is a placeholder - implement based on your auth system
        # You might get this from JWT tokens, session cookies, etc.

        # Example: from Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            # You would decode the JWT here to get user ID
            # For now, return a placeholder
            return "authenticated_user"

        # Return None for unauthenticated requests
        return None


def create_rate_limit_middleware(exclude_paths: list = None):
    """
    Factory function to create rate limiting middleware.

    Usage:
        app.add_middleware(create_rate_limit_middleware())
    """
    exclude_paths = exclude_paths or ["/health", "/metrics", "/docs", "/openapi.json"]

    def middleware_factory(app):
        return RateLimitMiddleware(app, exclude_paths)

    return middleware_factory


# Exception handler for rate limit exceeded
async def rate_limit_exception_handler(request: Request, exc: RateLimitExceeded):
    """Handle RateLimitExceeded exceptions."""
    return JSONResponse(
        status_code=429,
        content={
            "error": "rate_limit_exceeded",
            "message": str(exc),
            "retry_after": exc.retry_after,
            "limit": exc.limit,
            "window": exc.window
        },
        headers={
            "Retry-After": str(exc.retry_after),
            "X-RateLimit-Limit": str(exc.limit),
            "X-RateLimit-Window": str(exc.window)
        }
    )
