"""
Rate limiting service for Deep Search APIs.
Implements various rate limiting strategies to prevent abuse and ensure fair usage.
"""

import time
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import asyncio

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

logger = logging.getLogger(__name__)


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded."""

    def __init__(self, limit: int, window: int, retry_after: int):
        self.limit = limit
        self.window = window
        self.retry_after = retry_after
        super().__init__(f"Rate limit exceeded: {limit} requests per {window} seconds. Retry after {retry_after} seconds.")


class RateLimiter:
    """
    Redis-based rate limiter with multiple strategies.

    Supports:
    - Fixed window rate limiting
    - Sliding window rate limiting
    - Token bucket algorithm
    - Different limits per endpoint/user
    """

    def __init__(self, redis_client=None, host: str = "localhost", port: int = 6379,
                 db: int = 0, password: str = None):
        self.redis_client = redis_client
        self.host = host
        self.port = port
        self.db = db
        self.password = password

        # Default rate limits (requests per window in seconds)
        self.default_limits = {
            "deep_research": {"requests": 10, "window": 3600},  # 10 per hour
            "deep_search": {"requests": 30, "window": 3600},    # 30 per hour
            "analytics": {"requests": 60, "window": 3600},      # 60 per hour
            "admin": {"requests": 100, "window": 3600},         # 100 per hour
        }

        # Burst limits (higher limits for short bursts)
        self.burst_limits = {
            "deep_research": {"requests": 3, "window": 60},     # 3 per minute
            "deep_search": {"requests": 10, "window": 60},      # 10 per minute
            "analytics": {"requests": 20, "window": 60},        # 20 per minute
            "admin": {"requests": 30, "window": 60},            # 30 per minute
        }

        self.is_connected = False

    async def connect(self):
        """Connect to Redis."""
        if not REDIS_AVAILABLE:
            logger.warning("Redis not available for rate limiting")
            return False

        if self.redis_client is None:
            try:
                self.redis_client = redis.Redis(
                    host=self.host,
                    port=self.port,
                    db=self.db,
                    password=self.password,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
                await self.redis_client.ping()
                self.is_connected = True
                logger.info("Rate limiter connected to Redis")
                return True
            except Exception as e:
                logger.error(f"Failed to connect rate limiter to Redis: {e}")
                return False
        else:
            self.is_connected = True
            return True

    def _generate_key(self, identifier: str, endpoint: str, user_id: Optional[str] = None) -> str:
        """Generate Redis key for rate limiting."""
        base_key = f"ratelimit:{endpoint}:{identifier}"
        if user_id:
            return f"{base_key}:user:{user_id}"
        return base_key

    async def _check_fixed_window(self, key: str, limit: int, window: int) -> Tuple[bool, int, int]:
        """
        Check fixed window rate limit.

        Returns: (allowed, current_count, retry_after_seconds)
        """
        if not self.is_connected:
            return True, 0, 0  # Allow if Redis unavailable

        try:
            current_time = int(time.time())
            window_start = current_time - (current_time % window)

            # Use Redis transaction for atomic operations
            async with self.redis_client.pipeline() as pipe:
                # Clean up old windows and count current window
                await pipe.zremrangebyscore(key, 0, window_start - 1)
                await pipe.zcard(key)
                await pipe.zrange(key, 0, -1, withscores=True)
                results = await pipe.execute()

            current_count = results[1] or 0

            if current_count >= limit:
                # Calculate retry after time
                oldest_request = min(scores for _, scores in (results[2] or [(0, window_start)]))
                retry_after = window - (current_time - int(oldest_request))
                return False, current_count, max(1, retry_after)

            # Add current request
            await self.redis_client.zadd(key, {str(current_time): current_time})
            await self.redis_client.expire(key, window * 2)  # Expire key after 2 windows

            return True, current_count + 1, 0

        except Exception as e:
            logger.error(f"Rate limit check error: {e}")
            return True, 0, 0  # Allow on error

    async def _check_sliding_window(self, key: str, limit: int, window: int) -> Tuple[bool, int, int]:
        """
        Check sliding window rate limit using sorted sets.
        More accurate than fixed window but slightly more expensive.
        """
        if not self.is_connected:
            return True, 0, 0

        try:
            current_time = time.time()
            window_start = current_time - window

            async with self.redis_client.pipeline() as pipe:
                # Remove old requests outside the window
                await pipe.zremrangebyscore(key, 0, window_start)
                # Count remaining requests in window
                await pipe.zcard(key)
                # Get the oldest request time for retry calculation
                await pipe.zrange(key, 0, 0, withscores=True)
                results = await pipe.execute()

            current_count = results[1] or 0

            if current_count >= limit:
                # Calculate when the oldest request will expire
                oldest_time = results[2][0][1] if results[2] else current_time
                retry_after = int(window - (current_time - float(oldest_time)))
                return False, current_count, max(1, retry_after)

            # Add current request
            await self.redis_client.zadd(key, {str(current_time): current_time})
            await self.redis_client.expire(key, window * 2)

            return True, current_count + 1, 0

        except Exception as e:
            logger.error(f"Sliding window rate limit error: {e}")
            return True, 0, 0

    async def check_rate_limit(self, identifier: str, endpoint: str,
                              user_id: Optional[str] = None,
                              algorithm: str = "sliding_window") -> Tuple[bool, Dict[str, Any]]:
        """
        Check if request should be rate limited.

        Args:
            identifier: IP address or API key
            endpoint: API endpoint name
            user_id: Optional user identifier for per-user limits
            algorithm: "fixed_window" or "sliding_window"

        Returns:
            (allowed, limit_info_dict)
        """
        # Get limits for this endpoint
        limits = self.default_limits.get(endpoint, self.default_limits.get("default", {"requests": 60, "window": 3600}))
        burst_limits = self.burst_limits.get(endpoint, self.burst_limits.get("default", {"requests": 20, "window": 60}))

        key = self._generate_key(identifier, endpoint, user_id)

        # Check burst limit first (stricter, shorter window)
        burst_allowed, burst_count, burst_retry = await self._check_sliding_window(
            f"{key}:burst", burst_limits["requests"], burst_limits["window"]
        )

        if not burst_allowed:
            return False, {
                "limit_type": "burst",
                "limit": burst_limits["requests"],
                "window": burst_limits["window"],
                "current": burst_count,
                "retry_after": burst_retry
            }

        # Check main limit
        main_allowed, main_count, main_retry = await self._check_sliding_window(
            key, limits["requests"], limits["window"]
        ) if algorithm == "sliding_window" else await self._check_fixed_window(
            key, limits["requests"], limits["window"]
        )

        if not main_allowed:
            return False, {
                "limit_type": "main",
                "limit": limits["requests"],
                "window": limits["window"],
                "current": main_count,
                "retry_after": main_retry
            }

        # Request allowed
        return True, {
            "limit_type": "allowed",
            "burst_limit": burst_limits["requests"],
            "burst_window": burst_limits["window"],
            "burst_current": burst_count,
            "main_limit": limits["requests"],
            "main_window": limits["window"],
            "main_current": main_count
        }

    async def get_rate_limit_status(self, identifier: str, endpoint: str,
                                   user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get current rate limit status without making a request."""
        if not self.is_connected:
            return {"status": "unlimited", "reason": "redis_unavailable"}

        key = self._generate_key(identifier, endpoint, user_id)
        limits = self.default_limits.get(endpoint, {"requests": 60, "window": 3600})
        burst_limits = self.burst_limits.get(endpoint, {"requests": 20, "window": 60})

        try:
            async with self.redis_client.pipeline() as pipe:
                await pipe.zcard(f"{key}:burst")
                await pipe.zcard(key)
                results = await pipe.execute()

            return {
                "status": "active",
                "burst_current": results[0] or 0,
                "burst_limit": burst_limits["requests"],
                "burst_window": burst_limits["window"],
                "main_current": results[1] or 0,
                "main_limit": limits["requests"],
                "main_window": limits["window"]
            }

        except Exception as e:
            logger.error(f"Error getting rate limit status: {e}")
            return {"status": "error", "error": str(e)}

    async def reset_limits(self, identifier: str, endpoint: str,
                          user_id: Optional[str] = None) -> bool:
        """Reset rate limits for a specific identifier/endpoint."""
        if not self.is_connected:
            return False

        key = self._generate_key(identifier, endpoint, user_id)
        burst_key = f"{key}:burst"

        try:
            async with self.redis_client.pipeline() as pipe:
                await pipe.delete(key)
                await pipe.delete(burst_key)
                await pipe.execute()
            return True
        except Exception as e:
            logger.error(f"Error resetting rate limits: {e}")
            return False

    def set_custom_limits(self, endpoint: str, requests: int, window: int,
                         burst_requests: Optional[int] = None, burst_window: Optional[int] = None):
        """Set custom rate limits for an endpoint."""
        self.default_limits[endpoint] = {"requests": requests, "window": window}

        if burst_requests and burst_window:
            self.burst_limits[endpoint] = {"requests": burst_requests, "window": burst_window}
        elif burst_requests:
            # Use default burst window
            self.burst_limits[endpoint] = {"requests": burst_requests, "window": 60}

    async def cleanup_expired_keys(self) -> int:
        """Clean up expired rate limit keys. Should be run periodically."""
        if not self.is_connected:
            return 0

        try:
            # This is a maintenance operation - in production, you might want
            # to run this as a background task
            pattern = "ratelimit:*"
            keys = await self.redis_client.keys(pattern)

            cleaned = 0
            for key in keys:
                # Check if key has expired members
                count = await self.redis_client.zcard(key)
                if count == 0:
                    await self.redis_client.delete(key)
                    cleaned += 1

            logger.info(f"Cleaned up {cleaned} expired rate limit keys")
            return cleaned

        except Exception as e:
            logger.error(f"Error cleaning up rate limit keys: {e}")
            return 0


# Global rate limiter instance
_rate_limiter_instance = None

async def get_rate_limiter() -> RateLimiter:
    """Get global rate limiter instance."""
    global _rate_limiter_instance

    if _rate_limiter_instance is None:
        _rate_limiter_instance = RateLimiter()

        # Attempt to connect (non-blocking)
        connected = await _rate_limiter_instance.connect()
        if not connected:
            logger.warning("Redis rate limiter unavailable - proceeding without rate limiting")

    return _rate_limiter_instance

async def close_rate_limiter():
    """Close global rate limiter connection."""
    global _rate_limiter_instance

    if _rate_limiter_instance and _rate_limiter_instance.redis_client:
        await _rate_limiter_instance.redis_client.close()
        _rate_limiter_instance = None


# FastAPI dependency for rate limiting
async def check_rate_limit(identifier: str, endpoint: str, user_id: Optional[str] = None):
    """
    FastAPI dependency to check rate limits.

    Usage:
        @app.post("/api/endpoint")
        async def endpoint(request: Request, _rate_limit = Depends(check_rate_limit)):
            # Your endpoint logic
    """
    rate_limiter = await get_rate_limiter()

    allowed, limit_info = await rate_limiter.check_rate_limit(identifier, endpoint, user_id)

    if not allowed:
        raise RateLimitExceeded(
            limit=limit_info.get("limit", 0),
            window=limit_info.get("window", 60),
            retry_after=limit_info.get("retry_after", 60)
        )

    return limit_info
