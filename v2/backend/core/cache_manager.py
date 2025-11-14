"""
Cache Manager Service - Redis-based caching with TTL and invalidation
Provides intelligent caching strategies for API responses and database queries

Supports:
- Response caching with TTL
- Query result caching
- Cache warming
- Cache invalidation patterns
- Cache statistics and monitoring
"""

import asyncio
import json
import hashlib
import time
from typing import Optional, Dict, Any, List, Callable, Awaitable, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import wraps

try:
    import redis.asyncio as redis
except ImportError:
    redis = None


@dataclass
class CacheConfig:
    """Cache configuration"""
    ttl_seconds: int = 300  # 5 minutes default
    max_memory_mb: int = 512
    compression: bool = False
    key_prefix: str = "galion"
    enable_monitoring: bool = True


@dataclass
class CacheEntry:
    """Cache entry metadata"""
    key: str
    value: Any
    created_at: datetime
    ttl_seconds: int
    hits: int = 0
    size_bytes: int = 0


class CacheManager:
    """
    Redis-based cache manager with intelligent caching strategies

    Features:
    - TTL-based caching
    - Cache invalidation patterns
    - Cache warming
    - Memory management
    - Performance monitoring
    """

    def __init__(self, redis_url: str = "redis://localhost:6379", config: Optional[CacheConfig] = None):
        self.redis_url = redis_url
        self.config = config or CacheConfig()
        self.redis: Optional[redis.Redis] = None
        self.local_cache: Dict[str, CacheEntry] = {}  # Fallback when Redis unavailable
        self.cache_stats: Dict[str, int] = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "errors": 0
        }

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
                await self.redis.ping()
                # Configure Redis memory limits
                await self._configure_redis()
            except Exception as e:
                print(f"Failed to connect to Redis: {e}")
                self.redis = None
        else:
            print("Redis not available, using local cache")

    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis:
            await self.redis.close()

    async def _configure_redis(self):
        """Configure Redis settings"""
        if not self.redis:
            return

        try:
            # Set max memory and policy
            max_memory = self.config.max_memory_mb * 1024 * 1024  # Convert MB to bytes
            await self.redis.config_set("maxmemory", str(max_memory))
            await self.redis.config_set("maxmemory-policy", "allkeys-lru")
        except Exception as e:
            print(f"Failed to configure Redis: {e}")

    def _make_key(self, *parts) -> str:
        """Create a cache key from parts"""
        key_parts = [self.config.key_prefix] + [str(part) for part in parts]
        return ":".join(key_parts)

    def _serialize_value(self, value: Any) -> str:
        """Serialize value for caching"""
        if isinstance(value, (dict, list)):
            return json.dumps(value, default=str)
        elif isinstance(value, (int, float, bool)):
            return str(value)
        else:
            return str(value)

    def _deserialize_value(self, value: str) -> Any:
        """Deserialize cached value"""
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value

    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        try:
            if self.redis:
                value = await self.redis.get(key)
                if value is not None:
                    self.cache_stats["hits"] += 1
                    return self._deserialize_value(value.decode('utf-8'))
            else:
                # Use local cache
                entry = self.local_cache.get(key)
                if entry and entry.created_at.timestamp() + entry.ttl_seconds > time.time():
                    entry.hits += 1
                    self.cache_stats["hits"] += 1
                    return entry.value

            self.cache_stats["misses"] += 1
            return None

        except Exception as e:
            self.cache_stats["errors"] += 1
            print(f"Cache get error: {e}")
            return None

    async def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool:
        """
        Set value in cache

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: TTL in seconds (uses config default if None)

        Returns:
            True if successful, False otherwise
        """
        try:
            ttl = ttl_seconds or self.config.ttl_seconds
            serialized_value = self._serialize_value(value)

            if self.redis:
                success = await self.redis.setex(key, ttl, serialized_value)
                if success:
                    self.cache_stats["sets"] += 1
                return bool(success)
            else:
                # Use local cache
                entry = CacheEntry(
                    key=key,
                    value=value,
                    created_at=datetime.utcnow(),
                    ttl_seconds=ttl,
                    size_bytes=len(serialized_value)
                )
                self.local_cache[key] = entry
                self.cache_stats["sets"] += 1

                # Clean up expired entries periodically
                await self._cleanup_local_cache()
                return True

        except Exception as e:
            self.cache_stats["errors"] += 1
            print(f"Cache set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """
        Delete value from cache

        Args:
            key: Cache key

        Returns:
            True if deleted, False otherwise
        """
        try:
            if self.redis:
                result = await self.redis.delete(key)
                if result > 0:
                    self.cache_stats["deletes"] += 1
                return result > 0
            else:
                if key in self.local_cache:
                    del self.local_cache[key]
                    self.cache_stats["deletes"] += 1
                    return True
                return False

        except Exception as e:
            self.cache_stats["errors"] += 1
            print(f"Cache delete error: {e}")
            return False

    async def delete_pattern(self, pattern: str) -> int:
        """
        Delete keys matching pattern

        Args:
            pattern: Key pattern (e.g., "user:*")

        Returns:
            Number of keys deleted
        """
        try:
            if self.redis:
                keys = await self.redis.keys(self._make_key(pattern))
                if keys:
                    result = await self.redis.delete(*keys)
                    self.cache_stats["deletes"] += result
                    return result
                return 0
            else:
                # Local cache pattern matching (simple implementation)
                matching_keys = [k for k in self.local_cache.keys() if pattern in k]
                for key in matching_keys:
                    del self.local_cache[key]
                deleted_count = len(matching_keys)
                self.cache_stats["deletes"] += deleted_count
                return deleted_count

        except Exception as e:
            self.cache_stats["errors"] += 1
            print(f"Cache delete pattern error: {e}")
            return 0

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            if self.redis:
                return bool(await self.redis.exists(key))
            else:
                entry = self.local_cache.get(key)
                if entry and entry.created_at.timestamp() + entry.ttl_seconds > time.time():
                    return True
                elif entry:
                    # Remove expired entry
                    del self.local_cache[key]
                return False
        except Exception as e:
            print(f"Cache exists error: {e}")
            return False

    async def get_ttl(self, key: str) -> Optional[int]:
        """Get remaining TTL for key in seconds"""
        try:
            if self.redis:
                ttl = await self.redis.ttl(key)
                return ttl if ttl > 0 else None
            else:
                entry = self.local_cache.get(key)
                if entry:
                    remaining = int(entry.created_at.timestamp() + entry.ttl_seconds - time.time())
                    return max(0, remaining) if remaining > 0 else None
                return None
        except Exception as e:
            print(f"Cache TTL error: {e}")
            return None

    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment numeric value in cache"""
        try:
            if self.redis:
                return await self.redis.incrby(key, amount)
            else:
                # Local cache increment (not thread-safe)
                entry = self.local_cache.get(key)
                if entry and isinstance(entry.value, (int, float)):
                    entry.value += amount
                    return int(entry.value)
                else:
                    await self.set(key, amount)
                    return amount
        except Exception as e:
            print(f"Cache increment error: {e}")
            return None

    async def _cleanup_local_cache(self):
        """Clean up expired entries from local cache"""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.local_cache.items()
            if entry.created_at.timestamp() + entry.ttl_seconds <= current_time
        ]

        for key in expired_keys:
            del self.local_cache[key]

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        stats = dict(self.cache_stats)

        if self.redis:
            stats["backend"] = "redis"
            stats["local_entries"] = 0
        else:
            stats["backend"] = "local"
            stats["local_entries"] = len(self.local_cache)

        # Calculate hit rate
        total_requests = stats["hits"] + stats["misses"]
        stats["hit_rate"] = (stats["hits"] / total_requests * 100) if total_requests > 0 else 0

        return stats

    async def clear_all(self) -> bool:
        """Clear all cache entries"""
        try:
            if self.redis:
                await self.redis.flushdb()
            else:
                self.local_cache.clear()
            return True
        except Exception as e:
            print(f"Cache clear error: {e}")
            return False

    async def warm_cache(self, warmers: List[Callable[[], Awaitable[None]]]):
        """
        Warm cache with predefined data

        Args:
            warmers: List of async functions that populate cache
        """
        try:
            await asyncio.gather(*[warmer() for warmer in warmers])
            print(f"Cache warming completed for {len(warmers)} warmers")
        except Exception as e:
            print(f"Cache warming failed: {e}")


# Global cache manager instance
_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """Get or create global cache manager instance"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


# Decorator for caching function results
def cached(ttl_seconds: Optional[int] = None, key_prefix: str = ""):
    """
    Decorator to cache function results

    Usage:
        @cached(ttl_seconds=300)
        async def expensive_function(param1, param2):
            return compute_result(param1, param2)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache = get_cache_manager()

            # Create cache key from function name and arguments
            key_parts = [key_prefix or func.__name__]
            key_parts.extend([str(arg) for arg in args])
            key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])

            cache_key = cache._make_key(*key_parts)

            # Try to get from cache first
            cached_result = await cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache.set(cache_key, result, ttl_seconds)
            return result

        return wrapper
    return decorator


# Cache invalidation helpers
async def invalidate_user_cache(user_id: str):
    """Invalidate all cache entries for a user"""
    cache = get_cache_manager()
    await cache.delete_pattern(f"user:{user_id}")

async def invalidate_endpoint_cache(endpoint: str):
    """Invalidate cache for a specific endpoint"""
    cache = get_cache_manager()
    await cache.delete_pattern(f"endpoint:{endpoint}")

async def invalidate_all_cache():
    """Invalidate all cache entries"""
    cache = get_cache_manager()
    await cache.clear_all()
