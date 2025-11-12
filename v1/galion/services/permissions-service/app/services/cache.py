"""
Redis caching service for permissions
"""

import redis
import json
import os
from typing import Optional, List, Dict

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CACHE_TTL = int(os.getenv("PERMISSIONS_CACHE_TTL", "300"))  # 5 minutes default

class CacheService:
    """Redis-based caching for permissions"""
    
    def __init__(self):
        try:
            # Parse Redis URL
            if REDIS_URL.startswith("redis://"):
                parts = REDIS_URL.replace("redis://", "").split("@")
                if len(parts) == 2:
                    auth_parts = parts[0].split(":")
                    host_parts = parts[1].split(":")
                    self.redis_client = redis.Redis(
                        host=host_parts[0],
                        port=int(host_parts[1]) if len(host_parts) > 1 else 6379,
                        password=auth_parts[1] if len(auth_parts) > 1 else None,
                        decode_responses=True
                    )
                else:
                    host_parts = parts[0].split(":")
                    self.redis_client = redis.Redis(
                        host=host_parts[0],
                        port=int(host_parts[1]) if len(host_parts) > 1 else 6379,
                        decode_responses=True
                    )
            else:
                self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
            
            # Test connection
            self.redis_client.ping()
            self.connected = True
        except Exception as e:
            print(f"Failed to connect to Redis: {e}")
            self.connected = False
            self.redis_client = None
    
    def _make_key(self, prefix: str, identifier: str) -> str:
        """Generate cache key"""
        return f"permissions:{prefix}:{identifier}"
    
    def get_user_permissions(self, user_id: str) -> Optional[List[Dict]]:
        """Get cached user permissions"""
        if not self.connected:
            return None
        
        try:
            key = self._make_key("user", user_id)
            data = self.redis_client.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            print(f"Cache get error: {e}")
        
        return None
    
    def set_user_permissions(self, user_id: str, permissions: List[Dict]) -> bool:
        """Cache user permissions"""
        if not self.connected:
            return False
        
        try:
            key = self._make_key("user", user_id)
            self.redis_client.setex(
                key,
                CACHE_TTL,
                json.dumps(permissions)
            )
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    def invalidate_user_permissions(self, user_id: str) -> bool:
        """Invalidate user permissions cache"""
        if not self.connected:
            return False
        
        try:
            key = self._make_key("user", user_id)
            self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Cache invalidate error: {e}")
            return False
    
    def check_permission(self, user_id: str, resource: str, action: str) -> Optional[bool]:
        """Check if user has specific permission (cached)"""
        permissions = self.get_user_permissions(user_id)
        if permissions is None:
            return None  # Cache miss
        
        # Check if permission exists in cached data
        for perm in permissions:
            if perm.get('resource') == resource and perm.get('action') == action:
                return True
        
        return False
    
    def invalidate_all_permissions(self) -> bool:
        """Invalidate all permission caches"""
        if not self.connected:
            return False
        
        try:
            # Delete all keys matching pattern
            pattern = "permissions:user:*"
            for key in self.redis_client.scan_iter(match=pattern):
                self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Cache invalidate all error: {e}")
            return False

# Singleton instance
cache_service = CacheService()

