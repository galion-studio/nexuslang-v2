"""
Cache services for Deep Search system.
Provides Redis-based caching with fallback support.
"""

from .redis_cache import RedisCache, get_cache, close_cache

__all__ = [
    'RedisCache',
    'get_cache',
    'close_cache'
]
