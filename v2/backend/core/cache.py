"""
Redis Caching Layer for NexusLang v2
High-performance caching for API responses and frequently accessed data
"""

import json
import redis
import pickle
from typing import Any, Optional, Union
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    """Redis-based caching manager with automatic serialization"""

    def __init__(self, host: str = "redis", port: int = 6379, password: str = None,
                 db: int = 0, decode_responses: bool = False):
        self.redis_client = redis.Redis(
            host=host,
            port=port,
            password=password,
            db=db,
            decode_responses=decode_responses,
            socket_timeout=5,
            socket_connect_timeout=5,
            retry_on_timeout=True,
            max_connections=20
        )

        # Test connection
        try:
            self.redis_client.ping()
            logger.info("✓ Redis cache connected successfully")
        except redis.ConnectionError as e:
            logger.warning(f"✗ Redis cache connection failed: {e}")
            logger.warning("Caching will be disabled")
            self.redis_client = None

    def _serialize(self, data: Any) -> str:
        """Serialize data for Redis storage"""
        if isinstance(data, (str, int, float, bool)):
            return str(data)
        elif isinstance(data, (list, dict)):
            return json.dumps(data, default=str)
        else:
            # Use pickle for complex objects
            return pickle.dumps(data)

    def _deserialize(self, data: str, is_pickle: bool = False) -> Any:
        """Deserialize data from Redis storage"""
        if is_pickle:
            return pickle.loads(data.encode() if isinstance(data, str) else data)
        try:
            return json.loads(data)
        except (json.JSONDecodeError, TypeError):
            return data

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.redis_client:
            return None

        try:
            value = self.redis_client.get(key)
            if value is None:
                return None

            # Check if it's a pickled object (starts with special marker)
            if isinstance(value, str) and value.startswith("__PICKLE__"):
                return self._deserialize(value[10:], is_pickle=True)
            else:
                return self._deserialize(value)

        except Exception as e:
            logger.warning(f"Cache get error for key '{key}': {e}")
            return None

    def set(self, key: str, value: Any, ttl_seconds: int = 300) -> bool:
        """Set value in cache with TTL"""
        if not self.redis_client:
            return False

        try:
            serialized_value = self._serialize(value)

            # Mark pickled objects
            if isinstance(serialized_value, bytes):
                serialized_value = "__PICKLE__" + serialized_value.decode('latin-1')

            return self.redis_client.setex(key, ttl_seconds, serialized_value)

        except Exception as e:
            logger.warning(f"Cache set error for key '{key}': {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.redis_client:
            return False

        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logger.warning(f"Cache delete error for key '{key}': {e}")
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        if not self.redis_client:
            return False

        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            logger.warning(f"Cache exists error for key '{key}': {e}")
            return False

    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        if not self.redis_client:
            return 0

        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.warning(f"Cache clear pattern error for '{pattern}': {e}")
            return 0

    def get_cache_info(self) -> dict:
        """Get cache statistics and info"""
        if not self.redis_client:
            return {"status": "disabled", "reason": "connection failed"}

        try:
            info = self.redis_client.info()
            return {
                "status": "connected",
                "used_memory": info.get("used_memory_human", "unknown"),
                "connected_clients": info.get("connected_clients", 0),
                "total_keys": self.redis_client.dbsize(),
                "uptime_days": info.get("uptime_in_days", 0)
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

# Global cache instance
_cache_instance = None

def get_cache_manager() -> CacheManager:
    """Get global cache manager instance"""
    global _cache_instance
    if _cache_instance is None:
        # Initialize with Redis URL
        import os
        redis_url = os.getenv("REDIS_URL", "redis://:dev_redis_2025@redis:6379/0")

        # Parse Redis URL
        from urllib.parse import urlparse
        parsed = urlparse(redis_url)

        host = parsed.hostname or "redis"
        port = parsed.port or 6379
        password = parsed.password or None
        db = int(parsed.path.lstrip('/')) if parsed.path and parsed.path != '/' else 0

        _cache_instance = CacheManager(host=host, port=port, password=password, db=db)

    return _cache_instance

# Cache decorators for easy use

def cached(ttl_seconds: int = 300, key_prefix: str = ""):
    """Decorator to cache function results"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            cache = get_cache_manager()

            # Create cache key from function name and arguments
            key_parts = [key_prefix or func.__name__]
            key_parts.extend([str(arg) for arg in args])
            key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
            cache_key = ":".join(key_parts)

            # Try to get from cache first
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_result

            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl_seconds)
            logger.debug(f"Cache miss for {cache_key}, stored result")

            return result

        return wrapper
    return decorator

def cache_invalidate_pattern(pattern: str):
    """Decorator to invalidate cache patterns after function execution"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            # Invalidate cache after successful execution
            cache = get_cache_manager()
            invalidated = cache.clear_pattern(pattern)
            if invalidated > 0:
                logger.debug(f"Invalidated {invalidated} cache keys matching '{pattern}'")

            return result

        return wrapper
    return decorator

# Utility functions for common caching patterns

def cache_user_data(user_id: str, data: dict, ttl: int = 600):
    """Cache user data"""
    cache = get_cache_manager()
    cache_key = f"user:{user_id}:data"
    return cache.set(cache_key, data, ttl)

def get_cached_user_data(user_id: str):
    """Get cached user data"""
    cache = get_cache_manager()
    cache_key = f"user:{user_id}:data"
    return cache.get(cache_key)

def cache_project_data(project_id: str, data: dict, ttl: int = 300):
    """Cache project data"""
    cache = get_cache_manager()
    cache_key = f"project:{project_id}:data"
    return cache.set(cache_key, data, ttl)

def get_cached_project_data(project_id: str):
    """Get cached project data"""
    cache = get_cache_manager()
    cache_key = f"project:{project_id}:data"
    return cache.get(cache_key)

def invalidate_user_cache(user_id: str):
    """Invalidate all user-related cache"""
    cache = get_cache_manager()
    pattern = f"user:{user_id}:*"
    return cache.clear_pattern(pattern)

def invalidate_project_cache(project_id: str):
    """Invalidate all project-related cache"""
    cache = get_cache_manager()
    pattern = f"project:{project_id}:*"
    return cache.clear_pattern(pattern)