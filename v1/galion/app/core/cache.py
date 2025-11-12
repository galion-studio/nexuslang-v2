"""
Multi-layer caching implementation for GALION
Optimized for high performance and scalability
"""
from functools import wraps
import hashlib
import json
from typing import Any, Callable, Optional
import asyncio
from redis import asyncio as aioredis

# Redis client instance (initialized in main app)
redis_client: Optional[aioredis.Redis] = None


def init_redis(redis_url: str):
    """Initialize Redis connection"""
    global redis_client
    redis_client = aioredis.from_url(
        redis_url,
        encoding="utf-8",
        decode_responses=True,
        max_connections=50
    )


async def get_redis() -> aioredis.Redis:
    """Get Redis client instance"""
    if redis_client is None:
        raise RuntimeError("Redis client not initialized. Call init_redis() first.")
    return redis_client


def cache_response(ttl: int = 300, key_prefix: str = ""):
    """
    Decorator for caching function responses in Redis
    
    Args:
        ttl: Time to live in seconds (default: 5 minutes)
        key_prefix: Optional prefix for cache key
        
    Usage:
        @cache_response(ttl=600, key_prefix="user")
        async def get_user_profile(user_id: str):
            return await db.query(...)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            redis = await get_redis()
            
            # Generate cache key from function name and arguments
            key_parts = [key_prefix, func.__name__]
            
            # Add positional args to key
            if args:
                key_parts.extend(str(arg) for arg in args)
            
            # Add keyword args to key (sorted for consistency)
            if kwargs:
                kwargs_str = json.dumps(kwargs, sort_keys=True)
                kwargs_hash = hashlib.md5(kwargs_str.encode()).hexdigest()
                key_parts.append(kwargs_hash)
            
            cache_key = ":".join(filter(None, key_parts))
            
            # Try to get from cache
            try:
                cached = await redis.get(cache_key)
                if cached:
                    return json.loads(cached)
            except Exception as e:
                # If cache fails, continue to function execution
                print(f"Cache read error: {e}")
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            try:
                await redis.setex(
                    cache_key,
                    ttl,
                    json.dumps(result, default=str)  # default=str handles datetime, etc.
                )
            except Exception as e:
                # If cache write fails, still return result
                print(f"Cache write error: {e}")
            
            return result
        return wrapper
    return decorator


async def invalidate_cache(pattern: str):
    """
    Invalidate cache entries matching pattern
    
    Args:
        pattern: Redis key pattern (e.g., "user:*", "task:123:*")
        
    Usage:
        await invalidate_cache("user:123:*")  # Invalidate all user 123 caches
    """
    redis = await get_redis()
    try:
        # Find all keys matching pattern
        cursor = 0
        while True:
            cursor, keys = await redis.scan(cursor, match=pattern, count=100)
            if keys:
                await redis.delete(*keys)
            if cursor == 0:
                break
    except Exception as e:
        print(f"Cache invalidation error: {e}")


class CacheManager:
    """
    Cache manager for manual cache operations
    """
    
    @staticmethod
    async def get(key: str) -> Optional[Any]:
        """Get value from cache"""
        redis = await get_redis()
        try:
            value = await redis.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    @staticmethod
    async def set(key: str, value: Any, ttl: int = 300):
        """Set value in cache with TTL"""
        redis = await get_redis()
        try:
            await redis.setex(
                key,
                ttl,
                json.dumps(value, default=str)
            )
        except Exception as e:
            print(f"Cache set error: {e}")
    
    @staticmethod
    async def delete(key: str):
        """Delete key from cache"""
        redis = await get_redis()
        try:
            await redis.delete(key)
        except Exception as e:
            print(f"Cache delete error: {e}")
    
    @staticmethod
    async def exists(key: str) -> bool:
        """Check if key exists in cache"""
        redis = await get_redis()
        try:
            return await redis.exists(key) > 0
        except Exception as e:
            print(f"Cache exists error: {e}")
            return False
    
    @staticmethod
    async def increment(key: str, amount: int = 1) -> int:
        """Increment counter in cache"""
        redis = await get_redis()
        try:
            return await redis.incrby(key, amount)
        except Exception as e:
            print(f"Cache increment error: {e}")
            return 0
    
    @staticmethod
    async def get_stats() -> dict:
        """Get cache statistics"""
        redis = await get_redis()
        try:
            info = await redis.info()
            return {
                "used_memory_human": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients"),
                "total_commands_processed": info.get("total_commands_processed"),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": round(
                    info.get("keyspace_hits", 0) / 
                    max(info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0), 1) * 100,
                    2
                )
            }
        except Exception as e:
            print(f"Cache stats error: {e}")
            return {}


# Predefined cache keys and TTLs
class CacheKeys:
    """Centralized cache key definitions"""
    
    # User-related caches
    USER_PROFILE = "user:profile:{user_id}"  # TTL: 5 minutes
    USER_SESSION = "user:session:{session_id}"  # TTL: 24 hours
    USER_PERMISSIONS = "user:permissions:{user_id}"  # TTL: 15 minutes
    
    # Task-related caches (GALION.STUDIO)
    TASK_DETAIL = "task:detail:{task_id}"  # TTL: 1 minute
    TASK_LIST = "task:list:{project_id}"  # TTL: 30 seconds
    PROJECT_TASKS = "project:{project_id}:tasks"  # TTL: 1 minute
    
    # Conversation caches (GALION.APP)
    CONVERSATION = "conversation:{conversation_id}"  # TTL: 5 minutes
    CONVERSATION_HISTORY = "conversation:{conversation_id}:history"  # TTL: 1 hour
    
    # Rate limiting keys
    RATE_LIMIT = "rate_limit:{ip}:{endpoint}"  # TTL: 60 seconds


class CacheTTL:
    """Centralized TTL definitions (in seconds)"""
    ONE_MINUTE = 60
    FIVE_MINUTES = 300
    FIFTEEN_MINUTES = 900
    ONE_HOUR = 3600
    SIX_HOURS = 21600
    ONE_DAY = 86400
    ONE_WEEK = 604800

