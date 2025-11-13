"""
Performance monitoring and optimization for Galion Ecosystem
Includes response time tracking, database query monitoring, and optimization suggestions
"""

import time
import logging
from typing import Callable, Dict, Any, Optional
from functools import wraps
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
import asyncio
from collections import defaultdict, deque

from fastapi import Request, Response
from sqlalchemy import event
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Monitor application performance metrics"""

    def __init__(self):
        self.request_times: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.endpoint_stats: Dict[str, Dict[str, Any]] = {}
        self.db_query_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'count': 0,
            'total_time': 0.0,
            'avg_time': 0.0,
            'slow_queries': []
        })
        self.cache_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'hits': 0,
            'misses': 0,
            'hit_rate': 0.0
        })

    def record_request_time(self, endpoint: str, method: str, duration: float, status_code: int):
        """Record API request timing"""
        key = f"{method}:{endpoint}"
        self.request_times[key].append((duration, status_code, datetime.now()))

        # Update endpoint statistics
        if key not in self.endpoint_stats:
            self.endpoint_stats[key] = {
                'count': 0,
                'total_time': 0.0,
                'avg_time': 0.0,
                'min_time': float('inf'),
                'max_time': 0.0,
                'status_codes': defaultdict(int),
                'slow_requests': []
            }

        stats = self.endpoint_stats[key]
        stats['count'] += 1
        stats['total_time'] += duration
        stats['avg_time'] = stats['total_time'] / stats['count']
        stats['min_time'] = min(stats['min_time'], duration)
        stats['max_time'] = max(stats['max_time'], duration)
        stats['status_codes'][status_code] += 1

        # Track slow requests (>1 second)
        if duration > 1.0:
            stats['slow_requests'].append({
                'duration': duration,
                'timestamp': datetime.now(),
                'status_code': status_code
            })
            # Keep only last 50 slow requests
            if len(stats['slow_requests']) > 50:
                stats['slow_requests'].pop(0)

    def record_db_query(self, query: str, duration: float):
        """Record database query timing"""
        # Normalize query for grouping (remove parameters)
        normalized_query = ' '.join(query.split())

        stats = self.db_query_stats[normalized_query]
        stats['count'] += 1
        stats['total_time'] += duration
        stats['avg_time'] = stats['total_time'] / stats['count']

        # Track slow queries (>100ms)
        if duration > 0.1:
            stats['slow_queries'].append({
                'duration': duration,
                'timestamp': datetime.now(),
                'query': query[:500]  # Truncate long queries
            })
            # Keep only last 20 slow queries per query type
            if len(stats['slow_queries']) > 20:
                stats['slow_queries'].pop(0)

    def record_cache_hit(self, cache_type: str):
        """Record cache hit"""
        self.cache_stats[cache_type]['hits'] += 1
        self._update_cache_hit_rate(cache_type)

    def record_cache_miss(self, cache_type: str):
        """Record cache miss"""
        self.cache_stats[cache_type]['misses'] += 1
        self._update_cache_hit_rate(cache_type)

    def _update_cache_hit_rate(self, cache_type: str):
        """Update cache hit rate"""
        stats = self.cache_stats[cache_type]
        total = stats['hits'] + stats['misses']
        if total > 0:
            stats['hit_rate'] = stats['hits'] / total

    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'endpoints': {},
            'database': {},
            'cache': dict(self.cache_stats),
            'recommendations': []
        }

        # Endpoint performance
        for endpoint, stats in self.endpoint_stats.items():
            report['endpoints'][endpoint] = {
                'requests_per_second': self._calculate_rps(endpoint),
                'avg_response_time': round(stats['avg_time'], 3),
                'min_response_time': round(stats['min_time'], 3),
                'max_response_time': round(stats['max_time'], 3),
                'total_requests': stats['count'],
                'status_codes': dict(stats['status_codes']),
                'slow_request_count': len(stats['slow_requests'])
            }

        # Database performance
        for query, stats in self.db_query_stats.items():
            report['database'][query[:100] + '...' if len(query) > 100 else query] = {
                'execution_count': stats['count'],
                'avg_time': round(stats['avg_time'], 4),
                'total_time': round(stats['total_time'], 2),
                'slow_query_count': len(stats['slow_queries'])
            }

        # Generate recommendations
        report['recommendations'] = self._generate_recommendations()

        return report

    def _calculate_rps(self, endpoint: str) -> float:
        """Calculate requests per second for endpoint"""
        times = self.request_times[endpoint]
        if len(times) < 2:
            return 0.0

        # Use last 100 requests for calculation
        recent_times = list(times)[-100:]
        if len(recent_times) < 2:
            return 0.0

        time_span = (recent_times[-1][2] - recent_times[0][2]).total_seconds()
        if time_span <= 0:
            return 0.0

        return len(recent_times) / time_span

    def _generate_recommendations(self) -> list:
        """Generate performance optimization recommendations"""
        recommendations = []

        # Check for slow endpoints
        for endpoint, stats in self.endpoint_stats.items():
            if stats['avg_time'] > 2.0:
                recommendations.append({
                    'type': 'endpoint_optimization',
                    'priority': 'high',
                    'message': f"Endpoint {endpoint} has slow average response time ({stats['avg_time']:.2f}s)",
                    'suggestion': 'Consider adding caching, database indexing, or query optimization'
                })

        # Check for slow database queries
        for query, stats in self.db_query_stats.items():
            if stats['avg_time'] > 0.5:
                recommendations.append({
                    'type': 'database_optimization',
                    'priority': 'high',
                    'message': f"Database query is slow ({stats['avg_time']:.3f}s avg)",
                    'suggestion': 'Add database indexes or optimize query'
                })

        # Check cache hit rates
        for cache_type, stats in self.cache_stats.items():
            if stats['hit_rate'] < 0.5 and (stats['hits'] + stats['misses']) > 100:
                recommendations.append({
                    'type': 'cache_optimization',
                    'priority': 'medium',
                    'message': f"Cache {cache_type} has low hit rate ({stats['hit_rate']:.1%})",
                    'suggestion': 'Review cache TTL settings or cache key strategy'
                })

        # Check for high error rates
        for endpoint, stats in self.endpoint_stats.items():
            total_requests = stats['count']
            error_count = sum(count for code, count in stats['status_codes'].items() if code >= 400)
            if total_requests > 100 and (error_count / total_requests) > 0.1:
                recommendations.append({
                    'type': 'error_rate',
                    'priority': 'high',
                    'message': f"Endpoint {endpoint} has high error rate ({error_count/total_requests:.1%})",
                    'suggestion': 'Investigate and fix underlying issues'
                })

        return recommendations


# Global performance monitor
_performance_monitor: Optional[PerformanceMonitor] = None

def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor


# FastAPI middleware for request timing
@asynccontextmanager
async def performance_middleware(request: Request, call_next):
    """FastAPI middleware to monitor request performance"""
    monitor = get_performance_monitor()
    start_time = time.time()

    # Extract endpoint info
    endpoint = str(request.url.path)
    method = request.method

    try:
        response: Response = await call_next(request)
        duration = time.time() - start_time

        # Record performance metrics
        monitor.record_request_time(endpoint, method, duration, response.status_code)

        # Add performance headers
        response.headers['X-Response-Time'] = f"{duration:.3f}s"

        # Log slow requests
        if duration > 1.0:
            logger.warning(f"Slow request: {method} {endpoint} took {duration:.3f}s")

        return response

    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Request failed: {method} {endpoint} after {duration:.3f}s - {e}")
        monitor.record_request_time(endpoint, method, duration, 500)
        raise


# SQLAlchemy event listeners for database monitoring
def setup_db_monitoring(engine: Engine):
    """Setup SQLAlchemy event listeners for database query monitoring"""
    monitor = get_performance_monitor()

    @event.listens_for(engine, "before_execute")
    def before_execute(conn, clauseelement, multiparams, params):
        conn._query_start_time = time.time()

    @event.listens_for(engine, "after_execute")
    def after_execute(conn, clauseelement, multiparams, params, result):
        if hasattr(conn, '_query_start_time'):
            duration = time.time() - conn._query_start_time
            query_str = str(clauseelement)

            # Record query performance
            monitor.record_db_query(query_str, duration)

            # Log slow queries
            if duration > 0.1:  # 100ms
                logger.warning(f"Slow query ({duration:.3f}s): {query_str[:200]}...")


# Database optimization utilities
class DatabaseOptimizer:
    """Utilities for database performance optimization"""

    def __init__(self, engine: Engine):
        self.engine = engine

    async def analyze_query_performance(self) -> Dict[str, Any]:
        """Analyze query performance and suggest optimizations"""
        monitor = get_performance_monitor()
        report = monitor.get_performance_report()

        suggestions = []

        # Analyze slow queries
        for query, stats in report['database'].items():
            if stats['avg_time'] > 0.1:
                suggestions.append({
                    'type': 'query_optimization',
                    'query': query,
                    'current_avg_time': stats['avg_time'],
                    'suggestion': self._suggest_query_optimization(query)
                })

        return {
            'slow_queries': suggestions,
            'index_suggestions': await self._analyze_missing_indexes(),
            'table_stats': await self._get_table_statistics()
        }

    def _suggest_query_optimization(self, query: str) -> str:
        """Suggest optimizations for a slow query"""
        suggestions = []

        # Check for common optimization opportunities
        if 'SELECT *' in query.upper():
            suggestions.append('Avoid SELECT * - specify only needed columns')

        if 'WHERE' in query.upper() and 'ORDER BY' in query.upper():
            suggestions.append('Consider adding indexes on WHERE and ORDER BY columns')

        if 'JOIN' in query.upper() and 'ON' in query.upper():
            suggestions.append('Ensure foreign key columns are indexed')

        if 'LIKE' in query.upper() and not query.upper().count('LIKE') == query.upper().count('%'):
            suggestions.append('Leading wildcards in LIKE queries cannot use indexes efficiently')

        return '; '.join(suggestions) if suggestions else 'Review query execution plan'

    async def _analyze_missing_indexes(self) -> list:
        """Analyze and suggest missing indexes"""
        # This would require database-specific queries
        # Simplified implementation
        return [
            'Consider adding indexes on frequently queried columns',
            'Add composite indexes for multi-column WHERE clauses',
            'Consider partial indexes for filtered queries'
        ]

    async def _get_table_statistics(self) -> Dict[str, Any]:
        """Get table statistics for performance analysis"""
        # This would query system tables for row counts, sizes, etc.
        return {
            'total_tables': 'Analysis not implemented',
            'largest_tables': [],
            'index_usage': 'Analysis not implemented'
        }


# Cache optimization utilities
class CacheOptimizer:
    """Utilities for cache performance optimization"""

    def __init__(self, cache_manager):
        self.cache_manager = cache_manager

    async def analyze_cache_performance(self) -> Dict[str, Any]:
        """Analyze cache performance and suggest optimizations"""
        monitor = get_performance_monitor()
        report = monitor.get_performance_report()

        analysis = {
            'overall_hit_rate': 0.0,
            'cache_types': {},
            'recommendations': []
        }

        total_hits = 0
        total_requests = 0

        for cache_type, stats in report['cache'].items():
            hits = stats['hits']
            misses = stats['misses']
            total = hits + misses

            if total > 0:
                hit_rate = hits / total
                analysis['cache_types'][cache_type] = {
                    'hit_rate': hit_rate,
                    'hits': hits,
                    'misses': misses,
                    'total_requests': total
                }

                total_hits += hits
                total_requests += total

                # Generate recommendations
                if hit_rate < 0.7:
                    analysis['recommendations'].append({
                        'cache_type': cache_type,
                        'issue': f'Low hit rate ({hit_rate:.1%})',
                        'suggestion': 'Increase TTL, review cache invalidation strategy, or add more data to cache'
                    })
                elif hit_rate > 0.95:
                    analysis['recommendations'].append({
                        'cache_type': cache_type,
                        'issue': f'Very high hit rate ({hit_rate:.1%})',
                        'suggestion': 'Consider increasing TTL to reduce cache pressure'
                    })

        if total_requests > 0:
            analysis['overall_hit_rate'] = total_hits / total_requests

        return analysis

    async def optimize_cache_settings(self) -> Dict[str, Any]:
        """Suggest optimal cache settings based on usage patterns"""
        return {
            'recommended_ttl_adjustments': {},
            'cache_size_recommendations': 'Monitor cache memory usage',
            'eviction_policy_suggestions': 'Consider LRU for most cache types'
        }


# Decorators for performance monitoring
def monitor_performance(operation_name: str):
    """Decorator to monitor function performance"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            monitor = get_performance_monitor()
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time

                # Log slow operations
                if duration > 1.0:
                    logger.warning(f"Slow operation '{operation_name}': {duration:.3f}s")

                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"Operation '{operation_name}' failed after {duration:.3f}s: {e}")
                raise

        return wrapper
    return decorator


# Performance profiling utilities
class PerformanceProfiler:
    """Advanced performance profiling utilities"""

    def __init__(self):
        self.profiles: Dict[str, Dict[str, Any]] = {}

    def start_profile(self, name: str):
        """Start profiling a code block"""
        self.profiles[name] = {
            'start_time': time.time(),
            'start_memory': self._get_memory_usage(),
            'checkpoints': []
        }

    def checkpoint(self, name: str, checkpoint_name: str):
        """Add a checkpoint to profiling"""
        if name in self.profiles:
            profile = self.profiles[name]
            elapsed = time.time() - profile['start_time']
            memory = self._get_memory_usage()

            profile['checkpoints'].append({
                'name': checkpoint_name,
                'elapsed_time': elapsed,
                'memory_usage': memory,
                'timestamp': datetime.now()
            })

    def end_profile(self, name: str) -> Dict[str, Any]:
        """End profiling and return results"""
        if name not in self.profiles:
            return {}

        profile = self.profiles[name]
        end_time = time.time()
        end_memory = self._get_memory_usage()

        profile.update({
            'end_time': end_time,
            'end_memory': end_memory,
            'total_time': end_time - profile['start_time'],
            'memory_delta': end_memory - profile['start_memory']
        })

        result = dict(profile)
        del self.profiles[name]

        return result

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # MB
        except ImportError:
            return 0.0


# Global profiler instance
_performance_profiler: Optional[PerformanceProfiler] = None

def get_performance_profiler() -> PerformanceProfiler:
    """Get global performance profiler instance"""
    global _performance_profiler
    if _performance_profiler is None:
        _performance_profiler = PerformanceProfiler()
    return _performance_profiler
