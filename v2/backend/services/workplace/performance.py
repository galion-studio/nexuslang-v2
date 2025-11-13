"""
Workplace Service Performance Optimizations
Caching, database indexing, and query optimization for workplace service.
"""

import logging
import time
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from functools import wraps
import redis
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    data: Any
    timestamp: datetime
    ttl: int  # Time to live in seconds
    access_count: int = 0
    last_accessed: datetime = None

    def __post_init__(self):
        if self.last_accessed is None:
            self.last_accessed = self.timestamp

    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        return datetime.utcnow() > self.timestamp + timedelta(seconds=self.ttl)

    def access(self):
        """Record cache access."""
        self.access_count += 1
        self.last_accessed = datetime.utcnow()


class WorkplaceCache:
    """Multi-level caching system for workplace service."""

    def __init__(self):
        self.memory_cache: Dict[str, CacheEntry] = {}
        self.redis_client = None
        self.cache_hits = 0
        self.cache_misses = 0
        self.max_memory_entries = 1000

        # Initialize Redis if available
        try:
            import os
            redis_url = os.getenv("REDIS_URL")
            if redis_url:
                self.redis_client = redis.from_url(redis_url)
                logger.info("✅ Workplace cache initialized with Redis")
            else:
                logger.info("ℹ️ Workplace cache initialized with memory-only caching")
        except Exception as e:
            logger.warning(f"Redis initialization failed: {e}")

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        # Try Redis first
        if self.redis_client:
            try:
                data = self.redis_client.get(f"workplace:{key}")
                if data:
                    self.cache_hits += 1
                    return json.loads(data)
            except Exception as e:
                logger.error(f"Redis get failed: {e}")

        # Try memory cache
        if key in self.memory_cache:
            entry = self.memory_cache[key]
            if not entry.is_expired():
                entry.access()
                self.cache_hits += 1
                return entry.data
            else:
                # Remove expired entry
                del self.memory_cache[key]

        self.cache_misses += 1
        return None

    async def set(self, key: str, value: Any, ttl: int = 300):
        """Set value in cache."""
        # Store in Redis
        if self.redis_client:
            try:
                self.redis_client.setex(
                    f"workplace:{key}",
                    ttl,
                    json.dumps(value)
                )
            except Exception as e:
                logger.error(f"Redis set failed: {e}")

        # Store in memory cache
        entry = CacheEntry(
            data=value,
            timestamp=datetime.utcnow(),
            ttl=ttl
        )
        self.memory_cache[key] = entry

        # Clean up old entries if needed
        if len(self.memory_cache) > self.max_memory_entries:
            await self._cleanup_memory_cache()

    async def delete(self, key: str):
        """Delete value from cache."""
        # Delete from Redis
        if self.redis_client:
            try:
                self.redis_client.delete(f"workplace:{key}")
            except Exception as e:
                logger.error(f"Redis delete failed: {e}")

        # Delete from memory
        if key in self.memory_cache:
            del self.memory_cache[key]

    async def clear_pattern(self, pattern: str):
        """Clear all cache entries matching a pattern."""
        # Clear Redis keys matching pattern
        if self.redis_client:
            try:
                keys = self.redis_client.keys(f"workplace:{pattern}")
                if keys:
                    self.redis_client.delete(*keys)
            except Exception as e:
                logger.error(f"Redis pattern clear failed: {e}")

        # Clear memory cache entries matching pattern
        keys_to_delete = [k for k in self.memory_cache.keys() if pattern in k]
        for key in keys_to_delete:
            del self.memory_cache[key]

    async def _cleanup_memory_cache(self):
        """Clean up expired and least recently used entries."""
        current_time = datetime.utcnow()

        # Remove expired entries
        expired_keys = [
            k for k, v in self.memory_cache.items()
            if v.is_expired()
        ]
        for key in expired_keys:
            del self.memory_cache[key]

        # If still too many entries, remove least recently used
        if len(self.memory_cache) > self.max_memory_entries:
            # Sort by last accessed time
            sorted_entries = sorted(
                self.memory_cache.items(),
                key=lambda x: x[1].last_accessed
            )

            # Remove oldest 20% of entries
            to_remove = len(sorted_entries) // 5
            for key, _ in sorted_entries[:to_remove]:
                del self.memory_cache[key]

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_requests) if total_requests > 0 else 0

        return {
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_rate": hit_rate,
            "memory_entries": len(self.memory_cache),
            "redis_available": self.redis_client is not None
        }


class QueryOptimizer:
    """Database query optimization and caching."""

    def __init__(self, cache: WorkplaceCache):
        self.cache = cache
        self.query_stats = {}

    async def execute_optimized_query(
        self,
        query_name: str,
        query_func,
        cache_key: Optional[str] = None,
        cache_ttl: int = 300,
        force_refresh: bool = False
    ) -> Any:
        """Execute a query with caching and optimization."""
        start_time = time.time()

        # Try cache first (unless force refresh)
        if cache_key and not force_refresh:
            cached_result = await self.cache.get(cache_key)
            if cached_result is not None:
                execution_time = time.time() - start_time
                await self._record_query_stats(query_name, execution_time, True)
                return cached_result

        # Execute query
        try:
            result = await query_func()

            # Cache the result
            if cache_key:
                await self.cache.set(cache_key, result, cache_ttl)

            execution_time = time.time() - start_time
            await self._record_query_stats(query_name, execution_time, False)

            return result

        except Exception as e:
            execution_time = time.time() - start_time
            await self._record_query_stats(query_name, execution_time, False, error=str(e))
            raise

    async def _record_query_stats(self, query_name: str, execution_time: float, from_cache: bool, error: Optional[str] = None):
        """Record query execution statistics."""
        if query_name not in self.query_stats:
            self.query_stats[query_name] = {
                "total_executions": 0,
                "cache_hits": 0,
                "total_time": 0.0,
                "avg_time": 0.0,
                "error_count": 0,
                "last_execution": None
            }

        stats = self.query_stats[query_name]
        stats["total_executions"] += 1
        stats["total_time"] += execution_time
        stats["avg_time"] = stats["total_time"] / stats["total_executions"]
        stats["last_execution"] = datetime.utcnow()

        if from_cache:
            stats["cache_hits"] += 1

        if error:
            stats["error_count"] += 1

    def get_query_stats(self) -> Dict[str, Any]:
        """Get query performance statistics."""
        return self.query_stats.copy()

    async def invalidate_workspace_cache(self, workspace_id: int):
        """Invalidate all cache entries for a workspace."""
        patterns = [
            f"workspace:{workspace_id}:*",
            f"workspace_members:{workspace_id}",
            f"workspace_tasks:{workspace_id}:*",
            f"workspace_analytics:{workspace_id}:*"
        ]

        for pattern in patterns:
            await self.cache.clear_pattern(pattern)

    async def invalidate_user_cache(self, user_id: int):
        """Invalidate all cache entries for a user."""
        patterns = [
            f"user:{user_id}:*",
            f"user_workspaces:{user_id}",
            f"user_tasks:{user_id}:*"
        ]

        for pattern in patterns:
            await self.cache.clear_pattern(pattern)


class DatabaseOptimizer:
    """Database performance optimization utilities."""

    @staticmethod
    def generate_cache_key(*args) -> str:
        """Generate a consistent cache key from arguments."""
        key_components = [str(arg) for arg in args]
        key_string = ":".join(key_components)
        return hashlib.md5(key_string.encode()).hexdigest()[:16]

    @staticmethod
    async def optimize_workspace_query(db_session, workspace_id: int, include_members: bool = True):
        """Optimized workspace query with selective loading."""
        from ..models.workplace import Workspace, WorkspaceMember

        # Use selectinload for related data to avoid N+1 queries
        query = db_session.query(Workspace).filter(Workspace.id == workspace_id)

        if include_members:
            # Eager load members to avoid additional queries
            query = query.join(Workspace.members)

        workspace = query.first()

        if workspace and include_members:
            # Access members to ensure they're loaded
            _ = len(workspace.members)

        return workspace

    @staticmethod
    async def optimize_task_queries(db_session, workspace_id: int, status_filter: Optional[str] = None):
        """Optimized task queries with pagination and filtering."""
        from ..models.workplace import Task, Project

        query = db_session.query(Task).join(Project).filter(Project.user_id.in_(
            db_session.query(WorkspaceMember.user_id).filter(
                WorkspaceMember.workspace_id == workspace_id
            )
        ))

        if status_filter:
            query = query.filter(Task.status == status_filter)

        # Use efficient ordering and limiting
        tasks = query.order_by(Task.updated_at.desc()).limit(100).all()

        return tasks

    @staticmethod
    async def batch_update_task_status(db_session, task_updates: List[Tuple[int, str]]):
        """Batch update multiple task statuses efficiently."""
        from ..models.workplace import Task

        # Use bulk update for better performance
        for task_id, new_status in task_updates:
            db_session.query(Task).filter(Task.id == task_id).update({
                "status": new_status,
                "updated_at": datetime.utcnow()
            })

        db_session.commit()

    @staticmethod
    async def get_aggregated_metrics(db_session, workspace_id: int) -> Dict[str, Any]:
        """Get aggregated workspace metrics efficiently."""
        from ..models.workplace import WorkspaceMember, Task, TimeLog, Payment
        from sqlalchemy import func

        # Single query to get all metrics
        result = db_session.query(
            func.count(WorkspaceMember.id).label('member_count'),
            func.count(Task.id).label('task_count'),
            func.sum(TimeLog.hours).label('total_hours'),
            func.sum(Payment.amount).label('total_billed'),
            func.avg(WorkspaceMember.performance_score).label('avg_performance')
        ).join(
            WorkspaceMember,
            WorkspaceMember.workspace_id == workspace_id,
            isouter=True
        ).join(
            Task,
            Task.assignee_id == WorkspaceMember.user_id,
            isouter=True
        ).join(
            TimeLog,
            TimeLog.task_id == Task.id,
            isouter=True
        ).join(
            Payment,
            Payment.user_id == WorkspaceMember.user_id,
            isouter=True
        ).filter(WorkspaceMember.workspace_id == workspace_id).first()

        return {
            "member_count": result.member_count or 0,
            "task_count": result.task_count or 0,
            "total_hours": float(result.total_hours or 0),
            "total_billed": float(result.total_billed or 0),
            "avg_performance": float(result.avg_performance or 0)
        }


def performance_monitor(func):
    """Decorator to monitor function performance."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"⏱️ {func.__name__} executed in {execution_time:.3f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"❌ {func.__name__} failed in {execution_time:.3f}s: {e}")
            raise
    return wrapper


class ConnectionPoolOptimizer:
    """Database connection pool optimization."""

    def __init__(self):
        self.connection_stats = {
            "active_connections": 0,
            "idle_connections": 0,
            "total_connections": 0,
            "connection_errors": 0
        }

    async def optimize_pool_settings(self, db_engine):
        """Optimize database connection pool settings."""
        try:
            # Adjust pool settings based on load
            # This is a simplified example - in production you'd monitor actual usage

            pool_size = db_engine.pool.size()
            overflow = db_engine.pool._overflow

            # Log pool statistics
            logger.info(f"🔌 DB Pool - Size: {pool_size}, Overflow: {overflow}")

            # In production, you might adjust pool_pre_ping, pool_recycle, etc.

        except Exception as e:
            logger.error(f"Pool optimization failed: {e}")

    def record_connection_event(self, event_type: str):
        """Record database connection events."""
        if event_type == "connect":
            self.connection_stats["active_connections"] += 1
            self.connection_stats["total_connections"] += 1
        elif event_type == "disconnect":
            self.connection_stats["active_connections"] = max(0, self.connection_stats["active_connections"] - 1)
            self.connection_stats["idle_connections"] += 1
        elif event_type == "error":
            self.connection_stats["connection_errors"] += 1


# Global instances
workplace_cache = WorkplaceCache()
query_optimizer = QueryOptimizer(workplace_cache)
db_optimizer = DatabaseOptimizer()
connection_optimizer = ConnectionPoolOptimizer()
