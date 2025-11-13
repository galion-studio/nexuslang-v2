"""
High-performance caching system for Galion Ecosystem
Supports Redis, in-memory, and hybrid caching strategies
"""

import asyncio
import json
import hashlib
import logging
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime, timedelta
from functools import wraps
import pickle

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    redis = None
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)


class CacheBackend:
    """Abstract cache backend interface"""

    async def get(self, key: str) -> Optional[Any]:
        raise NotImplementedError

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        raise NotImplementedError

    async def delete(self, key: str) -> bool:
        raise NotImplementedError

    async def exists(self, key: str) -> bool:
        raise NotImplementedError

    async def clear(self) -> bool:
        raise NotImplementedError

    async def get_ttl(self, key: str) -> Optional[int]:
        raise NotImplementedError


class RedisCacheBackend(CacheBackend):
    """Redis-based cache backend"""

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0,
                 password: Optional[str] = None, **kwargs):
        if not REDIS_AVAILABLE:
            raise ImportError("redis package is required for RedisCacheBackend")

        self.redis_url = f"redis://:{password}@{host}:{port}/{db}" if password else f"redis://{host}:{port}/{db}"
        self._client: Optional[redis.Redis] = None

    async def _get_client(self) -> redis.Redis:
        if self._client is None:
            self._client = redis.from_url(self.redis_url, decode_responses=False)
        return self._client

    async def get(self, key: str) -> Optional[Any]:
        try:
            client = await self._get_client()
            data = await client.get(key)
            if data is None:
                return None

            # Try to deserialize JSON first, then pickle
            try:
                return json.loads(data.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                return pickle.loads(data)
        except Exception as e:
            logger.error(f"Redis get error for key {key}: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        try:
            client = await self._get_client()

            # Serialize value - try JSON first, then pickle
            try:
                data = json.dumps(value, default=str).encode('utf-8')
            except (TypeError, ValueError):
                data = pickle.dumps(value)

            if ttl:
                return await client.setex(key, ttl, data)
            else:
                return await client.set(key, data)
        except Exception as e:
            logger.error(f"Redis set error for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        try:
            client = await self._get_client()
            return bool(await client.delete(key))
        except Exception as e:
            logger.error(f"Redis delete error for key {key}: {e}")
            return False

    async def exists(self, key: str) -> bool:
        try:
            client = await self._get_client()
            return bool(await client.exists(key))
        except Exception as e:
            logger.error(f"Redis exists error for key {key}: {e}")
            return False

    async def clear(self) -> bool:
        try:
            client = await self._get_client()
            return bool(await client.flushdb())
        except Exception as e:
            logger.error(f"Redis clear error: {e}")
            return False

    async def get_ttl(self, key: str) -> Optional[int]:
        try:
            client = await self._get_client()
            ttl = await client.ttl(key)
            return ttl if ttl > 0 else None
        except Exception as e:
            logger.error(f"Redis TTL error for key {key}: {e}")
            return None


class MemoryCacheBackend(CacheBackend):
    """In-memory cache backend using dict"""

    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}

    async def get(self, key: str) -> Optional[Any]:
        entry = self._cache.get(key)
        if not entry:
            return None

        # Check TTL
        expires_at = entry.get('expires_at')
        if expires_at and datetime.now() > expires_at:
            await self.delete(key)
            return None

        return entry['value']

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        expires_at = None
        if ttl:
            expires_at = datetime.now() + timedelta(seconds=ttl)

        self._cache[key] = {
            'value': value,
            'expires_at': expires_at,
            'created_at': datetime.now()
        }
        return True

    async def delete(self, key: str) -> bool:
        return self._cache.pop(key, None) is not None

    async def exists(self, key: str) -> bool:
        entry = self._cache.get(key)
        if not entry:
            return False

        # Check TTL
        expires_at = entry.get('expires_at')
        if expires_at and datetime.now() > expires_at:
            await self.delete(key)
            return False

        return True

    async def clear(self) -> bool:
        self._cache.clear()
        return True

    async def get_ttl(self, key: str) -> Optional[int]:
        entry = self._cache.get(key)
        if not entry:
            return None

        expires_at = entry.get('expires_at')
        if not expires_at:
            return None

        remaining = (expires_at - datetime.now()).total_seconds()
        return max(0, int(remaining)) if remaining > 0 else None


class HybridCacheBackend(CacheBackend):
    """Hybrid cache with L1 (memory) and L2 (Redis) layers"""

    def __init__(self, redis_backend: RedisCacheBackend, l1_ttl: int = 300):
        self.l1_cache = MemoryCacheBackend()
        self.l2_cache = redis_backend
        self.l1_ttl = l1_ttl  # L1 cache TTL

    async def get(self, key: str) -> Optional[Any]:
        # Try L1 cache first
        value = await self.l1_cache.get(key)
        if value is not None:
            return value

        # Try L2 cache
        value = await self.l2_cache.get(key)
        if value is not None:
            # Populate L1 cache
            await self.l1_cache.set(key, value, self.l1_ttl)
            return value

        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        # Set in both caches
        l1_success = await self.l1_cache.set(key, value, min(ttl or 3600, self.l1_ttl))
        l2_success = await self.l2_cache.set(key, value, ttl)
        return l1_success and l2_success

    async def delete(self, key: str) -> bool:
        l1_success = await self.l1_cache.delete(key)
        l2_success = await self.l2_cache.delete(key)
        return l1_success or l2_success  # Consider success if at least one succeeds

    async def exists(self, key: str) -> bool:
        return await self.l1_cache.exists(key) or await self.l2_cache.exists(key)

    async def clear(self) -> bool:
        l1_success = await self.l1_cache.clear()
        l2_success = await self.l2_cache.clear()
        return l1_success and l2_success

    async def get_ttl(self, key: str) -> Optional[int]:
        # Return the shorter TTL
        l1_ttl = await self.l1_cache.get_ttl(key)
        l2_ttl = await self.l2_cache.get_ttl(key)

        if l1_ttl is None and l2_ttl is None:
            return None
        elif l1_ttl is None:
            return l2_ttl
        elif l2_ttl is None:
            return l1_ttl
        else:
            return min(l1_ttl, l2_ttl)


class CacheManager:
    """High-level cache manager with multiple strategies"""

    def __init__(self, backend: CacheBackend):
        self.backend = backend
        self._strategies: Dict[str, Dict[str, Any]] = {}

    def register_strategy(self, name: str, ttl: int, key_prefix: str = "",
                         serializer: Optional[Callable] = None,
                         deserializer: Optional[Callable] = None):
        """Register a caching strategy"""
        self._strategies[name] = {
            'ttl': ttl,
            'key_prefix': key_prefix,
            'serializer': serializer,
            'deserializer': deserializer
        }

    def _make_key(self, strategy: str, *args, **kwargs) -> str:
        """Generate cache key from strategy and arguments"""
        strategy_config = self._strategies.get(strategy, {})
        prefix = strategy_config.get('key_prefix', '')

        # Create hash from arguments
        key_data = {
            'args': args,
            'kwargs': {k: v for k, v in kwargs.items() if k != 'use_cache'}
        }
        key_hash = hashlib.md5(json.dumps(key_data, sort_keys=True, default=str).encode()).hexdigest()

        return f"{prefix}:{strategy}:{key_hash}"

    async def get(self, strategy: str, *args, **kwargs) -> Optional[Any]:
        """Get cached value for strategy"""
        key = self._make_key(strategy, *args, **kwargs)
        return await self.backend.get(key)

    async def set(self, strategy: str, value: Any, *args, **kwargs) -> bool:
        """Set cached value for strategy"""
        strategy_config = self._strategies.get(strategy, {})
        ttl = strategy_config.get('ttl', 300)

        key = self._make_key(strategy, *args, **kwargs)
        return await self.backend.set(key, value, ttl)

    async def delete_strategy(self, strategy: str) -> bool:
        """Delete all keys for a strategy (pattern-based)"""
        # Note: This is a simplified version. In production, you might want
        # to maintain a key registry or use Redis SCAN for pattern deletion
        logger.warning(f"delete_strategy not fully implemented for strategy: {strategy}")
        return False

    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate keys matching a pattern"""
        # Simplified implementation - in production use Redis SCAN
        logger.warning(f"invalidate_pattern not implemented for pattern: {pattern}")
        return 0

    # Decorators for automatic caching
    def cached(self, strategy: str):
        """Decorator for automatic caching of function results"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                use_cache = kwargs.pop('use_cache', True)

                if not use_cache:
                    return await func(*args, **kwargs)

                # Try to get from cache
                cached_result = await self.get(strategy, *args, **kwargs)
                if cached_result is not None:
                    return cached_result

                # Execute function
                result = await func(*args, **kwargs)

                # Cache result
                await self.set(strategy, result, *args, **kwargs)

                return result

            return wrapper
        return decorator


# Global cache manager instance
_cache_manager: Optional[CacheManager] = None

def get_cache_manager() -> CacheManager:
    """Get global cache manager instance"""
    global _cache_manager
    if _cache_manager is None:
        # Try Redis first, fallback to memory
        if REDIS_AVAILABLE:
            try:
                redis_backend = RedisCacheBackend()
                # Test connection
                asyncio.create_task(redis_backend._get_client())
                backend = HybridCacheBackend(redis_backend)
                logger.info("Using Redis + Memory hybrid cache")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}, falling back to memory cache")
                backend = MemoryCacheBackend()
        else:
            logger.info("Redis not available, using memory cache")
            backend = MemoryCacheBackend()

        _cache_manager = CacheManager(backend)

        # Register default strategies
        _cache_manager.register_strategy(
            'grokopedia_search',
            ttl=600,  # 10 minutes
            key_prefix='grokopedia'
        )
        _cache_manager.register_strategy(
            'grokopedia_entry',
            ttl=1800,  # 30 minutes
            key_prefix='grokopedia'
        )
        _cache_manager.register_strategy(
            'user_permissions',
            ttl=3600,  # 1 hour
            key_prefix='auth'
        )
        _cache_manager.register_strategy(
            'api_response',
            ttl=300,  # 5 minutes
            key_prefix='api'
        )

    return _cache_manager


# Convenience functions
async def cache_get(key: str) -> Optional[Any]:
    """Direct cache get"""
    manager = get_cache_manager()
    return await manager.backend.get(key)

async def cache_set(key: str, value: Any, ttl: Optional[int] = None) -> bool:
    """Direct cache set"""
    manager = get_cache_manager()
    return await manager.backend.set(key, value, ttl)

async def cache_delete(key: str) -> bool:
    """Direct cache delete"""
    manager = get_cache_manager()
    return await manager.backend.delete(key)

async def cache_exists(key: str) -> bool:
    """Check if key exists in cache"""
    manager = get_cache_manager()
    return await manager.backend.exists(key)

async def cache_clear() -> bool:
    """Clear all cache"""
    manager = get_cache_manager()
    return await manager.backend.clear()


# Cache warming utilities
class CacheWarmer:
    """Utility for warming caches on startup"""

    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
        self.warmup_tasks: List[Callable] = []

    def register_warmup_task(self, task: Callable):
        """Register a cache warmup task"""
        self.warmup_tasks.append(task)

    async def warmup_all(self):
        """Execute all warmup tasks"""
        logger.info("Starting cache warmup...")

        tasks = []
        for task in self.warmup_tasks:
            tasks.append(task())

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

        logger.info("Cache warmup completed")

# Global cache warmer instance
_cache_warmer: Optional[CacheWarmer] = None

def get_cache_warmer() -> CacheWarmer:
    """Get global cache warmer instance"""
    global _cache_warmer
    if _cache_warmer is None:
        _cache_warmer = CacheWarmer(get_cache_manager())
    return _cache_warmer
