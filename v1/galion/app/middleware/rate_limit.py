"""
Rate limiting middleware for GALION APIs
Uses Redis for distributed rate limiting
"""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
import time


# Initialize limiter with Redis storage
def get_redis_url() -> str:
    """Get Redis URL from environment"""
    import os
    return os.getenv("REDIS_URL", "redis://localhost:6379/4")


limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["1000 per hour"],
    storage_uri=get_redis_url(),
    headers_enabled=True  # Add X-RateLimit-* headers to responses
)


def setup_rate_limiting(app):
    """
    Configure rate limiting for FastAPI application
    
    Usage in main.py:
        from app.middleware.rate_limit import setup_rate_limiting
        app = FastAPI()
        setup_rate_limiting(app)
    """
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Custom rate limit decorator for specific endpoints
def custom_rate_limit(rate: str):
    """
    Custom rate limit decorator
    
    Usage:
        @app.get("/api/v1/resource")
        @custom_rate_limit("100/minute")
        async def get_resource(request: Request):
            return {"data": "value"}
    
    Args:
        rate: Rate limit string (e.g., "100/minute", "1000/hour", "10000/day")
    """
    return limiter.limit(rate)


# Predefined rate limits for different endpoint types
class RateLimits:
    """Predefined rate limits for different endpoint categories"""
    
    # Authentication endpoints (stricter to prevent brute force)
    AUTH_LOGIN = "10/minute"          # 10 login attempts per minute
    AUTH_REGISTER = "5/minute"        # 5 registration attempts per minute
    AUTH_RESET_PASSWORD = "3/minute"  # 3 password reset requests per minute
    
    # API endpoints (general)
    API_READ = "200/minute"           # Read operations
    API_WRITE = "100/minute"          # Write operations
    API_DELETE = "50/minute"          # Delete operations
    
    # Voice endpoints (resource intensive)
    VOICE_STT = "60/minute"           # Speech-to-text (1 per second)
    VOICE_TTS = "60/minute"           # Text-to-speech (1 per second)
    VOICE_CHAT = "30/minute"          # Voice chat (every 2 seconds)
    
    # File upload endpoints
    FILE_UPLOAD = "20/minute"         # File uploads
    
    # Search endpoints (can be expensive)
    SEARCH = "30/minute"              # Search operations
    
    # Public endpoints (more lenient)
    PUBLIC_READ = "300/minute"        # Public read operations


async def check_rate_limit(
    request: Request,
    key: str,
    limit: int,
    window: int = 60
) -> bool:
    """
    Manual rate limit check using Redis
    
    Args:
        request: FastAPI request object
        key: Rate limit key (e.g., "voice_chat:{user_id}")
        limit: Max requests allowed
        window: Time window in seconds
        
    Returns:
        bool: True if request is allowed, False if rate limited
        
    Raises:
        HTTPException: If rate limit exceeded
    """
    from app.core.cache import get_redis
    
    redis = await get_redis()
    
    # Create rate limit key
    rate_key = f"rate_limit:{key}"
    
    # Get current count
    current = await redis.get(rate_key)
    
    if current is None:
        # First request in this window
        await redis.setex(rate_key, window, 1)
        return True
    
    current = int(current)
    
    if current >= limit:
        # Rate limit exceeded
        raise HTTPException(
            status_code=HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Max {limit} requests per {window} seconds.",
            headers={"Retry-After": str(window)}
        )
    
    # Increment counter
    await redis.incr(rate_key)
    return True


async def get_rate_limit_info(
    request: Request,
    key: str,
    limit: int,
    window: int = 60
) -> dict:
    """
    Get rate limit information for a key
    
    Args:
        request: FastAPI request object
        key: Rate limit key
        limit: Max requests allowed
        window: Time window in seconds
        
    Returns:
        dict: Rate limit info (remaining, reset_time, total)
    """
    from app.core.cache import get_redis
    
    redis = await get_redis()
    rate_key = f"rate_limit:{key}"
    
    # Get current count
    current = await redis.get(rate_key)
    current = int(current) if current else 0
    
    # Get TTL
    ttl = await redis.ttl(rate_key)
    ttl = max(ttl, 0)
    
    return {
        "limit": limit,
        "remaining": max(limit - current, 0),
        "reset_in_seconds": ttl,
        "reset_at": time.time() + ttl
    }


# Example usage in FastAPI route
"""
from fastapi import FastAPI, Request, Depends
from app.middleware.rate_limit import setup_rate_limiting, custom_rate_limit, RateLimits

app = FastAPI()
setup_rate_limiting(app)

# Using decorator
@app.post("/api/v1/auth/login")
@custom_rate_limit(RateLimits.AUTH_LOGIN)
async def login(request: Request, credentials: LoginCredentials):
    # Login logic here
    pass

# Using manual check
@app.post("/api/v1/voice/chat")
async def voice_chat(request: Request):
    await check_rate_limit(
        request,
        key=f"voice_chat:{request.state.user.id}",
        limit=30,
        window=60
    )
    # Voice chat logic here
    pass
"""

