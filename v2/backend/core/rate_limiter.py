"""
Rate Limiter Service - API rate limiting and abuse prevention
Implements configurable rate limits per user, IP, and endpoint

Uses Redis for distributed rate limiting with sliding window algorithm
"""

import asyncio
import time
import hashlib
from typing import Optional, Dict, Any, Tuple, List
from dataclasses import dataclass
from datetime import datetime, timedelta

try:
    import redis.asyncio as redis
except ImportError:
    # Fallback for when redis is not available
    redis = None


@dataclass
class RateLimit:
    """Rate limit configuration"""
    requests: int
    window_seconds: int
    block_duration_seconds: Optional[int] = None

    @property
    def window_duration(self) -> timedelta:
        return timedelta(seconds=self.window_seconds)

    @property
    def block_duration(self) -> Optional[timedelta]:
        return timedelta(seconds=self.block_duration_seconds) if self.block_duration_seconds else None


@dataclass
class RateLimitResult:
    """Result of rate limit check"""
    allowed: bool
    remaining_requests: int
    reset_time: datetime
    retry_after: Optional[int] = None


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded"""
    def __init__(self, retry_after: int, limit: int, window: int):
        self.retry_after = retry_after
        self.limit = limit
        self.window = window
        super().__init__(f"Rate limit exceeded. Retry after {retry_after} seconds")


class RateLimiter:
    """
    Distributed rate limiter using Redis

    Supports multiple rate limit types:
    - Per user ID
    - Per IP address
    - Per endpoint
    - Global limits
    """

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        default_limits: Optional[Dict[str, RateLimit]] = None
    ):
        self.redis_url = redis_url
        self.redis: Optional[redis.Redis] = None
        self.local_cache: Dict[str, Tuple[int, float]] = {}  # For when Redis is unavailable

        # Default rate limits
        self.default_limits = default_limits or {
            "user": RateLimit(requests=60, window_seconds=60),  # 60 req/min per user
            "ip": RateLimit(requests=30, window_seconds=60),    # 30 req/min per IP
            "endpoint": RateLimit(requests=100, window_seconds=60),  # 100 req/min per endpoint
            "global": RateLimit(requests=1000, window_seconds=60),   # 1000 req/min global
        }

        # Custom endpoint limits
        self.endpoint_limits: Dict[str, RateLimit] = {}

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()

    async def connect(self):
        """Connect to Redis"""
        if redis:
            try:
                self.redis = redis.from_url(self.redis_url)
                # Test connection
                await self.redis.ping()
            except Exception as e:
                print(f"Failed to connect to Redis: {e}")
                self.redis = None
        else:
            print("Redis not available, using local cache")

    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis:
            await self.redis.close()

    def set_endpoint_limit(self, endpoint: str, limit: RateLimit):
        """Set custom rate limit for specific endpoint"""
        self.endpoint_limits[endpoint] = limit

    def get_endpoint_limit(self, endpoint: str) -> RateLimit:
        """Get rate limit for endpoint"""
        return self.endpoint_limits.get(endpoint, self.default_limits["endpoint"])

    async def check_rate_limit(
        self,
        key: str,
        limit_type: str = "user",
        custom_limit: Optional[RateLimit] = None
    ) -> RateLimitResult:
        """
        Check if request is within rate limit

        Args:
            key: Identifier (user_id, ip_address, etc.)
            limit_type: Type of limit (user, ip, endpoint, global)
            custom_limit: Custom limit override

        Returns:
            RateLimitResult indicating if request is allowed
        """
        limit = custom_limit or self.default_limits.get(limit_type, self.default_limits["user"])

        if self.redis:
            return await self._check_redis_limit(key, limit)
        else:
            return self._check_local_limit(key, limit)

    async def _check_redis_limit(self, key: str, limit: RateLimit) -> RateLimitResult:
        """Check rate limit using Redis (sliding window)"""
        if not self.redis:
            return RateLimitResult(allowed=True, remaining_requests=limit.requests, reset_time=datetime.utcnow())

        current_time = time.time()
        window_start = current_time - limit.window_seconds

        # Redis key for this rate limit
        redis_key = f"ratelimit:{key}:{int(current_time // limit.window_seconds)}"

        try:
            # Use Redis pipeline for atomic operations
            async with self.redis.pipeline() as pipe:
                # Remove old requests outside the window
                await pipe.zremrangebyscore(redis_key, 0, window_start)
                # Count remaining requests in window
                await pipe.zcard(redis_key)
                # Get the oldest request time to calculate reset time
                await pipe.zrange(redis_key, 0, 0, withscores=True)

                results = await pipe.execute()

            request_count = results[1] or 0

            if request_count >= limit.requests:
                # Rate limit exceeded
                oldest_timestamp = results[2][0][1] if results[2] else current_time
                reset_time = datetime.fromtimestamp(oldest_timestamp + limit.window_seconds)
                retry_after = int((oldest_timestamp + limit.window_seconds) - current_time)

                return RateLimitResult(
                    allowed=False,
                    remaining_requests=0,
                    reset_time=reset_time,
                    retry_after=max(1, retry_after)
                )

            # Add current request
            await self.redis.zadd(redis_key, {str(current_time): current_time})
            # Set expiration for the key
            await self.redis.expire(redis_key, limit.window_seconds * 2)

            remaining = limit.requests - request_count - 1
            reset_time = datetime.fromtimestamp(current_time + limit.window_seconds)

            return RateLimitResult(
                allowed=True,
                remaining_requests=max(0, remaining),
                reset_time=reset_time
            )

        except Exception as e:
            print(f"Redis rate limit check failed: {e}")
            # Fallback to local cache
            return self._check_local_limit(key, limit)

    def _check_local_limit(self, key: str, limit: RateLimit) -> RateLimitResult:
        """Check rate limit using local cache (fixed window)"""
        current_time = time.time()
        window_start = current_time - limit.window_seconds

        # Get or create entry
        if key not in self.local_cache:
            self.local_cache[key] = (0, current_time)

        requests, last_reset = self.local_cache[key]

        # Reset counter if window has passed
        if current_time - last_reset >= limit.window_seconds:
            requests = 0
            last_reset = current_time

        if requests >= limit.requests:
            # Rate limit exceeded
            reset_time = datetime.fromtimestamp(last_reset + limit.window_seconds)
            retry_after = int((last_reset + limit.window_seconds) - current_time)

            return RateLimitResult(
                allowed=False,
                remaining_requests=0,
                reset_time=reset_time,
                retry_after=max(1, retry_after)
            )

        # Allow request
        requests += 1
        self.local_cache[key] = (requests, last_reset)

        remaining = limit.requests - requests
        reset_time = datetime.fromtimestamp(last_reset + limit.window_seconds)

        return RateLimitResult(
            allowed=True,
            remaining_requests=remaining,
            reset_time=reset_time
        )

    async def reset_limit(self, key: str):
        """Reset rate limit for a key"""
        if self.redis:
            # Remove all rate limit keys for this identifier
            pattern = f"ratelimit:{key}:*"
            keys = await self.redis.keys(pattern)
            if keys:
                await self.redis.delete(*keys)
        else:
            # Remove from local cache
            self.local_cache.pop(key, None)

    async def get_limit_status(self, key: str, limit_type: str = "user") -> Dict[str, Any]:
        """Get current rate limit status for a key"""
        limit = self.default_limits.get(limit_type, self.default_limits["user"])
        result = await self.check_rate_limit(key, limit_type)

        return {
            "key": key,
            "limit_type": limit_type,
            "requests_allowed": limit.requests,
            "window_seconds": limit.window_seconds,
            "remaining_requests": result.remaining_requests,
            "reset_time": result.reset_time.isoformat(),
            "is_blocked": not result.allowed,
            "retry_after": result.retry_after
        }

    async def cleanup_expired_limits(self):
        """Clean up expired rate limit entries (maintenance)"""
        if not self.redis:
            return

        try:
            # This is a maintenance operation that could be run periodically
            # For now, we'll rely on Redis TTL for cleanup
            pass
        except Exception as e:
            print(f"Failed to cleanup expired limits: {e}")


# Global rate limiter instance
_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """Get or create global rate limiter instance"""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter


# FastAPI dependency for rate limiting
async def rate_limit_dependency(
    request,
    rate_limiter: RateLimiter = None
) -> None:
    """
    FastAPI dependency for automatic rate limiting

    Usage:
        @router.get("/endpoint")
        async def endpoint(request: Request, _ = Depends(rate_limit_dependency)):
            ...
    """
    if not rate_limiter:
        rate_limiter = get_rate_limiter()

    # Get client IP
    client_ip = getattr(request.client, 'host', 'unknown') if request.client else 'unknown'

    # Get user ID if authenticated (this would need to be customized)
    user_id = getattr(request.state, 'user_id', None) if hasattr(request.state, 'user_id') else None

    # Check IP-based rate limit
    ip_result = await rate_limiter.check_rate_limit(f"ip:{client_ip}", "ip")
    if not ip_result.allowed:
        raise RateLimitExceeded(ip_result.retry_after, 30, 60)  # 30 req/min

    # Check user-based rate limit if authenticated
    if user_id:
        user_result = await rate_limiter.check_rate_limit(f"user:{user_id}", "user")
        if not user_result.allowed:
            raise RateLimitExceeded(user_result.retry_after, 60, 60)  # 60 req/min

    # Check endpoint-based rate limit
    endpoint = request.url.path
    endpoint_limit = rate_limiter.get_endpoint_limit(endpoint)
    endpoint_result = await rate_limiter.check_rate_limit(f"endpoint:{endpoint}", "endpoint", endpoint_limit)
    if not endpoint_result.allowed:
        raise RateLimitExceeded(endpoint_result.retry_after, endpoint_limit.requests, endpoint_limit.window_seconds)


# Utility functions for common rate limit patterns
def create_strict_limit() -> RateLimit:
    """Create a strict rate limit (10 req/min)"""
    return RateLimit(requests=10, window_seconds=60)

def create_moderate_limit() -> RateLimit:
    """Create a moderate rate limit (100 req/min)"""
    return RateLimit(requests=100, window_seconds=60)

def create_lenient_limit() -> RateLimit:
    """Create a lenient rate limit (1000 req/min)"""
    return RateLimit(requests=1000, window_seconds=60)

def create_burst_limit() -> RateLimit:
    """Create a burst limit (100 req/sec for 10 seconds)"""
    return RateLimit(requests=1000, window_seconds=10)
