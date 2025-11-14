"""
Database optimization services for Deep Search system.
Provides query optimization, indexing, and performance monitoring.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import time
from sqlalchemy import text, Index, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import AsyncAdaptedQueuePool

logger = logging.getLogger(__name__)


class DatabaseOptimizer:
    """
    Database optimization and monitoring for Deep Search.

    Features:
    - Automatic index creation and maintenance
    - Query performance monitoring
    - Connection pool optimization
    - Query plan analysis
    - Slow query detection and alerting
    """

    def __init__(self, db_url: str = None, pool_size: int = 20, max_overflow: int = 30):
        self.db_url = db_url
        self.pool_size = pool_size
        self.max_overflow = max_overflow

        # Performance metrics
        self.query_metrics = {
            "total_queries": 0,
            "slow_queries": 0,
            "avg_query_time": 0.0,
            "peak_concurrent_queries": 0,
            "connection_pool_stats": {}
        }

        # Slow query threshold (seconds)
        self.slow_query_threshold = 2.0

        # Indexes to create for deep search
        self.required_indexes = [
            {
                "table": "knowledge_entries",
                "columns": ["title"],
                "name": "idx_knowledge_title"
            },
            {
                "table": "knowledge_entries",
                "columns": ["content"],
                "name": "idx_knowledge_content"
            },
            {
                "table": "knowledge_entries",
                "columns": ["verified"],
                "name": "idx_knowledge_verified"
            },
            {
                "table": "knowledge_entries",
                "columns": ["created_at"],
                "name": "idx_knowledge_created_at"
            },
            {
                "table": "knowledge_entries",
                "columns": ["updated_at"],
                "name": "idx_knowledge_updated_at"
            },
            {
                "table": "knowledge_entries",
                "columns": ["verified", "created_at"],
                "name": "idx_knowledge_verified_created"
            },
            {
                "table": "contributions",
                "columns": ["user_id", "created_at"],
                "name": "idx_contributions_user_created"
            },
            {
                "table": "contributions",
                "columns": ["entry_id", "created_at"],
                "name": "idx_contributions_entry_created"
            }
        ]

    async def optimize_connection_pool(self) -> AsyncAdaptedQueuePool:
        """Create optimized connection pool for high-performance queries."""
        try:
            engine = create_async_engine(
                self.db_url,
                poolclass=AsyncAdaptedQueuePool,
                pool_size=self.pool_size,
                max_overflow=self.max_overflow,
                pool_pre_ping=True,  # Verify connections before use
                pool_recycle=3600,   # Recycle connections every hour
                echo=False,          # Disable SQL logging in production
                future=True
            )

            logger.info(f"Optimized database connection pool created (size: {self.pool_size}, overflow: {self.max_overflow})")
            return engine
        except Exception as e:
            logger.error(f"Failed to create optimized connection pool: {e}")
            raise

    async def create_performance_indexes(self, session: AsyncSession) -> Dict[str, Any]:
        """Create performance indexes for deep search operations."""
        results = {"created": [], "existing": [], "errors": []}

        for index_info in self.required_indexes:
            try:
                table = index_info["table"]
                columns = index_info["columns"]
                index_name = index_info["name"]

                # Check if index already exists
                index_exists_query = text("""
                    SELECT 1 FROM pg_indexes
                    WHERE tablename = :table AND indexname = :index_name
                """)

                exists_result = await session.execute(
                    index_exists_query,
                    {"table": table, "index_name": index_name}
                )

                if exists_result.fetchone():
                    results["existing"].append(index_name)
                    continue

                # Create index
                columns_str = ", ".join(columns)
                create_index_query = text(f"""
                    CREATE INDEX CONCURRENTLY {index_name}
                    ON {table} ({columns_str})
                """)

                await session.execute(create_index_query)
                results["created"].append(index_name)
                logger.info(f"Created database index: {index_name}")

            except Exception as e:
                error_msg = f"Failed to create index {index_info['name']}: {e}"
                results["errors"].append(error_msg)
                logger.error(error_msg)

        await session.commit()
        return results

    async def analyze_query_performance(self, session: AsyncSession, query: str,
                                       parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze query performance and execution plan."""
        try:
            start_time = time.time()

            # Execute EXPLAIN ANALYZE
            explain_query = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}"
            result = await session.execute(text(explain_query), parameters or {})

            execution_time = time.time() - start_time
            plan_data = result.fetchone()

            analysis = {
                "query": query,
                "execution_time": execution_time,
                "plan": plan_data[0] if plan_data else None,
                "recommendations": []
            }

            # Analyze the execution plan for optimization opportunities
            if plan_data and isinstance(plan_data[0], list):
                analysis["recommendations"] = self._analyze_execution_plan(plan_data[0])

            return analysis

        except Exception as e:
            logger.error(f"Query performance analysis failed: {e}")
            return {"error": str(e)}

    def _analyze_execution_plan(self, plan: List[Dict[str, Any]]) -> List[str]:
        """Analyze execution plan and provide optimization recommendations."""
        recommendations = []

        def analyze_node(node: Dict[str, Any], depth: int = 0):
            node_type = node.get("Node Type", "")
            total_cost = node.get("Total Cost", 0)
            plan_rows = node.get("Plan Rows", 0)
            actual_rows = node.get("Actual Rows", 0)

            # Check for sequential scans on large tables
            if node_type == "Seq Scan" and plan_rows > 10000:
                recommendations.append(f"Consider adding index for sequential scan (estimated rows: {plan_rows})")

            # Check for inefficient joins
            if "Join" in node_type and total_cost > 1000:
                recommendations.append(f"Review join performance in {node_type} (cost: {total_cost})")

            # Check for missing statistics
            if actual_rows and plan_rows and abs(actual_rows - plan_rows) / max(plan_rows, 1) > 2:
                recommendations.append("Statistics may be outdated - consider ANALYZE")

            # Recursively analyze child nodes
            for child_key in ["Plans", "Inner Plans", "Outer Plans"]:
                if child_key in node:
                    for child in node[child_key]:
                        analyze_node(child, depth + 1)

        if plan:
            analyze_node(plan[0])

        return recommendations

    async def get_table_statistics(self, session: AsyncSession) -> Dict[str, Any]:
        """Get comprehensive table statistics for optimization."""
        try:
            # Get table sizes and row counts
            stats_query = text("""
                SELECT
                    schemaname,
                    tablename,
                    n_tup_ins as inserts,
                    n_tup_upd as updates,
                    n_tup_del as deletes,
                    n_live_tup as live_rows,
                    n_dead_tup as dead_rows,
                    last_vacuum,
                    last_autovacuum,
                    last_analyze,
                    last_autoanalyze
                FROM pg_stat_user_tables
                WHERE schemaname = 'public'
                ORDER BY tablename
            """)

            result = await session.execute(stats_query)
            tables_stats = result.fetchall()

            # Get index usage statistics
            index_stats_query = text("""
                SELECT
                    schemaname,
                    tablename,
                    indexname,
                    idx_scan as index_scans,
                    idx_tup_read as tuples_read,
                    idx_tup_fetch as tuples_fetched
                FROM pg_stat_user_indexes
                WHERE schemaname = 'public'
                ORDER BY tablename, indexname
            """)

            index_result = await session.execute(index_stats_query)
            index_stats = index_result.fetchall()

            return {
                "table_statistics": [dict(row) for row in tables_stats],
                "index_statistics": [dict(row) for row in index_stats],
                "generated_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to get table statistics: {e}")
            return {"error": str(e)}

    async def optimize_search_queries(self, session: AsyncSession) -> Dict[str, Any]:
        """Optimize search queries with better indexing and query structure."""
        optimizations = {
            "applied": [],
            "skipped": [],
            "errors": []
        }

        try:
            # Optimize full-text search queries
            search_optimization_query = text("""
                -- Create optimized search function if it doesn't exist
                CREATE OR REPLACE FUNCTION optimized_knowledge_search(
                    search_query TEXT,
                    limit_count INTEGER DEFAULT 10,
                    verified_only BOOLEAN DEFAULT FALSE
                )
                RETURNS TABLE(
                    id UUID,
                    title TEXT,
                    content TEXT,
                    similarity REAL,
                    verified BOOLEAN
                )
                LANGUAGE plpgsql
                AS $$
                BEGIN
                    RETURN QUERY
                    SELECT
                        ke.id,
                        ke.title,
                        ke.content,
                        (ts_rank_cd(to_tsvector('english', ke.title || ' ' || ke.content),
                                   plainto_tsquery('english', search_query)))::REAL as similarity,
                        ke.verified
                    FROM knowledge_entries ke
                    WHERE (NOT verified_only OR ke.verified = TRUE)
                      AND to_tsvector('english', ke.title || ' ' || ke.content) @@ plainto_tsquery('english', search_query)
                    ORDER BY similarity DESC, ke.created_at DESC
                    LIMIT limit_count;
                END;
                $$;
            """)

            await session.execute(search_optimization_query)
            optimizations["applied"].append("optimized_knowledge_search function")

            # Create partial indexes for better performance
            partial_index_queries = [
                text("CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_knowledge_verified_true ON knowledge_entries (created_at DESC) WHERE verified = TRUE"),
                text("CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_contributions_recent ON contributions (created_at DESC) WHERE created_at > NOW() - INTERVAL '30 days'")
            ]

            for query in partial_index_queries:
                try:
                    await session.execute(query)
                    optimizations["applied"].append("partial index optimization")
                except Exception as e:
                    optimizations["errors"].append(f"Partial index error: {e}")

            await session.commit()

        except Exception as e:
            optimizations["errors"].append(f"Search optimization failed: {e}")

        return optimizations

    async def monitor_slow_queries(self, session: AsyncSession, duration_threshold: float = 2.0) -> List[Dict[str, Any]]:
        """Monitor and log slow-running queries."""
        try:
            # Get currently running queries
            slow_queries_query = text("""
                SELECT
                    pid,
                    query,
                    state,
                    now() - query_start as duration,
                    client_addr,
                    usename
                FROM pg_stat_activity
                WHERE state = 'active'
                  AND now() - query_start > interval ':threshold seconds'
                  AND query NOT LIKE '%pg_stat_activity%'
                ORDER BY duration DESC
                LIMIT 10
            """)

            result = await session.execute(slow_queries_query, {"threshold": duration_threshold})
            slow_queries = result.fetchall()

            if slow_queries:
                self.query_metrics["slow_queries"] += len(slow_queries)
                logger.warning(f"Found {len(slow_queries)} slow queries running longer than {duration_threshold}s")

                return [{
                    "pid": row.pid,
                    "query": row.query[:200] + "..." if len(row.query) > 200 else row.query,
                    "state": row.state,
                    "duration": str(row.duration),
                    "client_addr": row.client_addr,
                    "username": row.usename
                } for row in slow_queries]

            return []

        except Exception as e:
            logger.error(f"Failed to monitor slow queries: {e}")
            return []

    async def get_performance_report(self, session: AsyncSession) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        try:
            # Get database performance metrics
            perf_query = text("""
                SELECT
                    schemaname,
                    tablename,
                    seq_scan as sequential_scans,
                    seq_tup_read as sequential_tuples_read,
                    idx_scan as index_scans,
                    idx_tup_fetch as index_tuples_fetched,
                    n_tup_ins as inserts,
                    n_tup_upd as updates,
                    n_tup_del as deletes
                FROM pg_stat_user_tables
                WHERE schemaname = 'public'
                ORDER BY seq_scan DESC
                LIMIT 20
            """)

            result = await session.execute(perf_query)
            table_perf = result.fetchall()

            # Analyze table performance
            performance_analysis = []
            for row in table_perf:
                analysis = {
                    "table": row.tablename,
                    "sequential_scans": row.sequential_scans,
                    "index_scans": row.index_scans,
                    "scan_ratio": (row.index_scans / max(row.sequential_scans, 1)),
                    "inserts": row.inserts,
                    "updates": row.updates,
                    "deletes": row.deletes,
                    "recommendations": []
                }

                # Performance recommendations
                if row.sequential_scans > row.index_scans * 10:
                    analysis["recommendations"].append("High sequential scan ratio - review indexing strategy")

                if row.updates > row.inserts * 5:
                    analysis["recommendations"].append("High update frequency - monitor index maintenance")

                performance_analysis.append(analysis)

            return {
                "table_performance": performance_analysis,
                "query_metrics": self.query_metrics.copy(),
                "slow_queries_detected": self.query_metrics["slow_queries"],
                "generated_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to generate performance report: {e}")
            return {"error": str(e)}

    async def vacuum_analyze_tables(self, session: AsyncSession, tables: List[str] = None) -> Dict[str, Any]:
        """Perform VACUUM ANALYZE on specified tables for optimization."""
        results = {"vacuumed": [], "errors": []}

        if tables is None:
            # Get all tables in public schema
            tables_query = text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
            tables_result = await session.execute(tables_query)
            tables = [row.tablename for row in tables_result.fetchall()]

        for table in tables:
            try:
                vacuum_query = text(f"VACUUM ANALYZE {table}")
                await session.execute(vacuum_query)
                results["vacuumed"].append(table)
                logger.info(f"VACUUM ANALYZE completed for table: {table}")
            except Exception as e:
                error_msg = f"Failed to VACUUM ANALYZE {table}: {e}"
                results["errors"].append(error_msg)
                logger.error(error_msg)

        await session.commit()
        return results

    async def get_connection_pool_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics."""
        # This would integrate with your connection pool monitoring
        # For now, return basic structure
        return {
            "pool_size": self.pool_size,
            "max_overflow": self.max_overflow,
            "estimated_connections": self.pool_size + min(self.max_overflow // 2, 10),
            "last_updated": datetime.utcnow().isoformat()
        }
