"""
Redis-based caching service for Deep Search system.
Provides high-performance caching for research results and frequently accessed data.
"""

import json
import hashlib
import logging
from typing import Any, Dict, Optional, Union, List
from datetime import datetime, timedelta
import asyncio

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

from ..deep_search.agents import AgentResult

logger = logging.getLogger(__name__)


class RedisCache:
    """
    Redis-based caching service with TTL support and cache invalidation.

    Features:
    - Research result caching with intelligent TTL
    - Cache warming for frequently accessed queries
    - Cache invalidation strategies
    - Performance metrics tracking
    - Graceful fallback when Redis unavailable
    """

    def __init__(self, host: str = "localhost", port: int = 6379,
                 db: int = 0, password: str = None, decode_responses: bool = True):
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.decode_responses = decode_responses

        self.redis_client = None
        self.is_connected = False
        self.cache_metrics = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "errors": 0
        }

        # Cache TTL configurations (in seconds)
        self.ttl_config = {
            "research_results": 3600,  # 1 hour for research results
            "search_queries": 1800,    # 30 minutes for search queries
            "source_metadata": 7200,   # 2 hours for source metadata
            "persona_responses": 3600, # 1 hour for persona responses
            "validation_cache": 1800,  # 30 minutes for validation results
            "analytics_data": 300,     # 5 minutes for analytics
        }

    async def connect(self) -> bool:
        """Establish connection to Redis server."""
        if not REDIS_AVAILABLE:
            logger.warning("Redis not available. Caching will be disabled.")
            return False

        try:
            self.redis_client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=self.decode_responses,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                max_connections=20
            )

            # Test connection
            await self.redis_client.ping()
            self.is_connected = True
            logger.info(f"Connected to Redis at {self.host}:{self.port}")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.is_connected = False
            return False

    async def disconnect(self):
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()
            self.is_connected = False

    def _generate_cache_key(self, prefix: str, identifier: Union[str, Dict[str, Any]]) -> str:
        """Generate consistent cache key from identifier."""
        if isinstance(identifier, str):
            key_string = identifier
        elif isinstance(identifier, dict):
            # Sort keys for consistent hashing
            key_string = json.dumps(identifier, sort_keys=True)
        else:
            key_string = str(identifier)

        # Create hash for long keys
        if len(key_string) > 100:
            key_hash = hashlib.sha256(key_string.encode()).hexdigest()[:16]
            return f"{prefix}:{key_hash}"

        # Replace problematic characters
        safe_key = key_string.replace(" ", "_").replace(":", ";").replace("/", "|")
        return f"{prefix}:{safe_key}"

    async def get(self, key_prefix: str, identifier: Union[str, Dict[str, Any]]) -> Optional[Any]:
        """Retrieve value from cache."""
        if not self.is_connected:
            self.cache_metrics["errors"] += 1
            return None

        cache_key = self._generate_cache_key(key_prefix, identifier)

        try:
            value = await self.redis_client.get(cache_key)
            if value is None:
                self.cache_metrics["misses"] += 1
                return None

            # Parse JSON if it's a JSON string
            if isinstance(value, str) and (value.startswith("{") or value.startswith("[")):
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    pass  # Keep as string

            self.cache_metrics["hits"] += 1
            logger.debug(f"Cache hit for key: {cache_key}")
            return value

        except Exception as e:
            logger.error(f"Cache get error for key {cache_key}: {e}")
            self.cache_metrics["errors"] += 1
            return None

    async def set(self, key_prefix: str, identifier: Union[str, Dict[str, Any]],
                  value: Any, ttl: Optional[int] = None) -> bool:
        """Store value in cache with optional TTL."""
        if not self.is_connected:
            self.cache_metrics["errors"] += 1
            return False

        cache_key = self._generate_cache_key(key_prefix, identifier)

        # Use configured TTL if not provided
        if ttl is None:
            ttl = self.ttl_config.get(key_prefix, 3600)

        try:
            # Serialize complex objects
            if isinstance(value, (dict, list)):
                serialized_value = json.dumps(value)
            elif hasattr(value, '__dict__'):
                # Handle custom objects
                serialized_value = json.dumps({
                    'type': value.__class__.__name__,
                    'data': value.__dict__
                })
            else:
                serialized_value = str(value)

            success = await self.redis_client.set(cache_key, serialized_value, ex=ttl)
            if success:
                self.cache_metrics["sets"] += 1
                logger.debug(f"Cached value for key: {cache_key} (TTL: {ttl}s)")
            return bool(success)

        except Exception as e:
            logger.error(f"Cache set error for key {cache_key}: {e}")
            self.cache_metrics["errors"] += 1
            return False

    async def delete(self, key_prefix: str, identifier: Union[str, Dict[str, Any]]) -> bool:
        """Delete value from cache."""
        if not self.is_connected:
            self.cache_metrics["errors"] += 1
            return False

        cache_key = self._generate_cache_key(key_prefix, identifier)

        try:
            result = await self.redis_client.delete(cache_key)
            if result > 0:
                self.cache_metrics["deletes"] += 1
                logger.debug(f"Deleted cache key: {cache_key}")
            return result > 0

        except Exception as e:
            logger.error(f"Cache delete error for key {cache_key}: {e}")
            self.cache_metrics["errors"] += 1
            return False

    async def exists(self, key_prefix: str, identifier: Union[str, Dict[str, Any]]) -> bool:
        """Check if key exists in cache."""
        if not self.is_connected:
            return False

        cache_key = self._generate_cache_key(key_prefix, identifier)

        try:
            return bool(await self.redis_client.exists(cache_key))
        except Exception as e:
            logger.error(f"Cache exists check error for key {cache_key}: {e}")
            return False

    async def get_or_set(self, key_prefix: str, identifier: Union[str, Dict[str, Any]],
                        fetch_func, ttl: Optional[int] = None):
        """Get from cache or fetch and cache if not found."""
        # Try to get from cache first
        cached_value = await self.get(key_prefix, identifier)
        if cached_value is not None:
            return cached_value

        # Fetch new value
        try:
            value = await fetch_func()
            if value is not None:
                await self.set(key_prefix, identifier, value, ttl)
            return value
        except Exception as e:
            logger.error(f"Error fetching value for cache key {key_prefix}:{identifier}: {e}")
            return None

    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching a pattern."""
        if not self.is_connected:
            return 0

        try:
            # Get all keys matching pattern
            keys = await self.redis_client.keys(pattern)
            if not keys:
                return 0

            # Delete all matching keys
            deleted_count = await self.redis_client.delete(*keys)
            self.cache_metrics["deletes"] += deleted_count

            logger.info(f"Invalidated {deleted_count} cache keys matching pattern: {pattern}")
            return deleted_count

        except Exception as e:
            logger.error(f"Cache invalidation error for pattern {pattern}: {e}")
            return 0

    async def clear_all(self) -> bool:
        """Clear all cached data."""
        if not self.is_connected:
            return False

        try:
            await self.redis_client.flushdb()
            logger.info("Cleared all cached data")
            return True
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False

    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        if not self.is_connected:
            return {"status": "disconnected"}

        try:
            info = await self.redis_client.info()
            total_requests = self.cache_metrics["hits"] + self.cache_metrics["misses"]

            stats = {
                "status": "connected",
                "host": f"{self.host}:{self.port}",
                "metrics": self.cache_metrics.copy(),
                "hit_rate": (self.cache_metrics["hits"] / total_requests) if total_requests > 0 else 0,
                "redis_info": {
                    "connected_clients": info.get("connected_clients", 0),
                    "used_memory_human": info.get("used_memory_human", "0B"),
                    "total_connections_received": info.get("total_connections_received", 0),
                    "uptime_in_seconds": info.get("uptime_in_seconds", 0)
                }
            }

            return stats

        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"status": "error", "error": str(e)}

    # Deep Search specific caching methods

    async def get_research_result(self, query: str, persona: str = "default",
                                 depth: str = "comprehensive") -> Optional[Dict[str, Any]]:
        """Get cached research result."""
        cache_key = {
            "query": query,
            "persona": persona,
            "depth": depth
        }
        return await self.get("research_results", cache_key)

    async def set_research_result(self, query: str, persona: str, depth: str,
                                 result: Dict[str, Any]) -> bool:
        """Cache research result."""
        cache_key = {
            "query": query,
            "persona": persona,
            "depth": depth
        }
        return await self.set("research_results", cache_key, result)

    async def invalidate_research_cache(self, query: Optional[str] = None) -> int:
        """Invalidate research result cache."""
        if query:
            # Invalidate specific query cache
            pattern = f"research_results:*{query}*"
        else:
            # Invalidate all research results
            pattern = "research_results:*"

        return await self.invalidate_pattern(pattern)

    async def get_search_cache(self, search_query: str, filters: Dict[str, Any] = None) -> Optional[List[Dict[str, Any]]]:
        """Get cached search results."""
        cache_key = {
            "query": search_query,
            "filters": filters or {}
        }
        return await self.get("search_queries", cache_key)

    async def set_search_cache(self, search_query: str, filters: Dict[str, Any],
                              results: List[Dict[str, Any]]) -> bool:
        """Cache search results."""
        cache_key = {
            "query": search_query,
            "filters": filters
        }
        return await self.set("search_queries", cache_key, results)

    async def warm_cache(self, common_queries: List[str]) -> int:
        """Warm cache with commonly accessed queries."""
        warmed_count = 0

        for query in common_queries:
            # Check if already cached
            if not await self.exists("research_results", {"query": query}):
                # Pre-cache with a placeholder (will be updated on first real request)
                placeholder = {
                    "query": query,
                    "cached_at": datetime.utcnow().isoformat(),
                    "status": "warming"
                }
                success = await self.set("research_results", {"query": query}, placeholder, ttl=300)
                if success:
                    warmed_count += 1

        logger.info(f"Warmed cache with {warmed_count} common queries")
        return warmed_count


# Global cache instance
_cache_instance = None

async def get_cache() -> RedisCache:
    """Get global cache instance."""
    global _cache_instance

    if _cache_instance is None:
        _cache_instance = RedisCache()

        # Attempt to connect (non-blocking)
        connected = await _cache_instance.connect()
        if not connected:
            logger.warning("Redis cache unavailable - proceeding without caching")

    return _cache_instance

async def close_cache():
    """Close global cache connection."""
    global _cache_instance

    if _cache_instance:
        await _cache_instance.disconnect()
        _cache_instance = None
