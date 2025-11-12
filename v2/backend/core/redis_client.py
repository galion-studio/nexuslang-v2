"""
Redis Client for Distributed Security Features

Provides:
- Distributed rate limiting
- Token blacklisting with TTL
- Account lockout tracking
- Session management
- Cache for security checks

Uses Redis for scalability across multiple server instances.
"""

import redis.asyncio as aioredis
from typing import Optional, Any
import json
from datetime import timedelta
from core.config import settings


class RedisClient:
    """
    Async Redis client for security features.
    
    Handles connection pooling and provides high-level methods
    for security-related operations.
    """
    
    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None
        self._connected = False
    
    async def connect(self):
        """Initialize Redis connection pool."""
        try:
            self.redis = await aioredis.from_url(
                settings.REDIS_URL,
                password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
                encoding="utf-8",
                decode_responses=True,
                max_connections=20
            )
            # Test connection
            await self.redis.ping()
            self._connected = True
            print("✅ Redis connected for security features")
        except Exception as e:
            print(f"⚠️  Redis connection failed: {e}")
            print("   Falling back to in-memory features (not distributed)")
            self._connected = False
    
    async def close(self):
        """Close Redis connection."""
        if self.redis:
            await self.redis.close()
            self._connected = False
            print("✅ Redis connection closed")
    
    @property
    def is_connected(self) -> bool:
        """Check if Redis is connected."""
        return self._connected
    
    # ==================== RATE LIMITING ====================
    
    async def check_rate_limit(
        self,
        key: str,
        max_requests: int,
        window_seconds: int
    ) -> tuple[bool, dict]:
        """
        Check and update rate limit using sliding window.
        
        Args:
            key: Unique identifier (e.g., "ratelimit:ip:127.0.0.1")
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds
        
        Returns:
            (allowed, info_dict)
        """
        if not self._connected:
            return True, {"limit": max_requests, "remaining": max_requests, "reset": 0}
        
        try:
            current_time = await self.redis.time()
            current = int(current_time[0])
            
            # Use sorted set for sliding window
            pipe = self.redis.pipeline()
            
            # Remove old entries
            pipe.zremrangebyscore(key, 0, current - window_seconds)
            
            # Count current requests
            pipe.zcard(key)
            
            # Add current request
            pipe.zadd(key, {str(current): current})
            
            # Set expiry
            pipe.expire(key, window_seconds)
            
            results = await pipe.execute()
            count = results[1]
            
            # Check if over limit
            if count >= max_requests:
                return False, {
                    "limit": max_requests,
                    "remaining": 0,
                    "reset": current + window_seconds
                }
            
            return True, {
                "limit": max_requests,
                "remaining": max_requests - count - 1,
                "reset": current + window_seconds
            }
        
        except Exception as e:
            print(f"Redis rate limit error: {e}")
            return True, {"limit": max_requests, "remaining": max_requests, "reset": 0}
    
    # ==================== TOKEN BLACKLIST ====================
    
    async def blacklist_token(self, token: str, expires_in_seconds: int = 86400):
        """
        Blacklist a JWT token with automatic expiry.
        
        Args:
            token: JWT token to blacklist
            expires_in_seconds: How long to keep in blacklist (default 24h)
        """
        if not self._connected:
            return
        
        try:
            key = f"blacklist:token:{token}"
            await self.redis.setex(key, expires_in_seconds, "1")
        except Exception as e:
            print(f"Redis blacklist error: {e}")
    
    async def is_token_blacklisted(self, token: str) -> bool:
        """
        Check if token is blacklisted.
        
        Args:
            token: JWT token to check
        
        Returns:
            True if blacklisted, False otherwise
        """
        if not self._connected:
            return False
        
        try:
            key = f"blacklist:token:{token}"
            result = await self.redis.exists(key)
            return result > 0
        except Exception as e:
            print(f"Redis blacklist check error: {e}")
            return False
    
    # ==================== ACCOUNT LOCKOUT ====================
    
    async def record_failed_login(self, identifier: str) -> int:
        """
        Record a failed login attempt.
        
        Args:
            identifier: Email or IP address
        
        Returns:
            Number of failed attempts
        """
        if not self._connected:
            return 0
        
        try:
            key = f"failed_login:{identifier}"
            pipe = self.redis.pipeline()
            pipe.incr(key)
            pipe.expire(key, 1800)  # 30 minutes
            results = await pipe.execute()
            return results[0]
        except Exception as e:
            print(f"Redis failed login error: {e}")
            return 0
    
    async def get_failed_login_count(self, identifier: str) -> int:
        """Get number of failed login attempts."""
        if not self._connected:
            return 0
        
        try:
            key = f"failed_login:{identifier}"
            count = await self.redis.get(key)
            return int(count) if count else 0
        except Exception as e:
            print(f"Redis get failed login error: {e}")
            return 0
    
    async def clear_failed_logins(self, identifier: str):
        """Clear failed login attempts after successful login."""
        if not self._connected:
            return
        
        try:
            key = f"failed_login:{identifier}"
            await self.redis.delete(key)
        except Exception as e:
            print(f"Redis clear failed login error: {e}")
    
    async def is_account_locked(self, identifier: str, max_attempts: int = 5) -> tuple[bool, int]:
        """
        Check if account is locked due to failed attempts.
        
        Returns:
            (is_locked, remaining_attempts)
        """
        failed_count = await self.get_failed_login_count(identifier)
        is_locked = failed_count >= max_attempts
        remaining = max(0, max_attempts - failed_count)
        return is_locked, remaining
    
    # ==================== SESSION MANAGEMENT ====================
    
    async def create_session(
        self,
        user_id: str,
        session_data: dict,
        ttl_seconds: int = 86400
    ) -> str:
        """
        Create a user session with automatic expiry.
        
        Args:
            user_id: User ID
            session_data: Session data to store
            ttl_seconds: Time to live in seconds
        
        Returns:
            Session ID
        """
        if not self._connected:
            return ""
        
        try:
            import secrets
            session_id = secrets.token_urlsafe(32)
            key = f"session:{session_id}"
            
            data = {
                "user_id": user_id,
                **session_data
            }
            
            await self.redis.setex(
                key,
                ttl_seconds,
                json.dumps(data)
            )
            
            return session_id
        except Exception as e:
            print(f"Redis session create error: {e}")
            return ""
    
    async def get_session(self, session_id: str) -> Optional[dict]:
        """Get session data."""
        if not self._connected:
            return None
        
        try:
            key = f"session:{session_id}"
            data = await self.redis.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            print(f"Redis session get error: {e}")
            return None
    
    async def delete_session(self, session_id: str):
        """Delete a session."""
        if not self._connected:
            return
        
        try:
            key = f"session:{session_id}"
            await self.redis.delete(key)
        except Exception as e:
            print(f"Redis session delete error: {e}")
    
    # ==================== CACHE ====================
    
    async def set_cache(self, key: str, value: Any, ttl_seconds: int = 300):
        """Set cache value with TTL."""
        if not self._connected:
            return
        
        try:
            await self.redis.setex(
                f"cache:{key}",
                ttl_seconds,
                json.dumps(value)
            )
        except Exception as e:
            print(f"Redis cache set error: {e}")
    
    async def get_cache(self, key: str) -> Optional[Any]:
        """Get cache value."""
        if not self._connected:
            return None
        
        try:
            data = await self.redis.get(f"cache:{key}")
            return json.loads(data) if data else None
        except Exception as e:
            print(f"Redis cache get error: {e}")
            return None
    
    async def delete_cache(self, key: str):
        """Delete cache value."""
        if not self._connected:
            return
        
        try:
            await self.redis.delete(f"cache:{key}")
        except Exception as e:
            print(f"Redis cache delete error: {e}")


# Global Redis client instance
_redis_client: Optional[RedisClient] = None


async def get_redis() -> RedisClient:
    """Get or create global Redis client."""
    global _redis_client
    if _redis_client is None:
        _redis_client = RedisClient()
        await _redis_client.connect()
    return _redis_client


async def close_redis():
    """Close global Redis connection."""
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None

