"""
Analytics API for NexusLang v2
===============================

Provides endpoints for accessing platform analytics and metrics.

Features:
- Dashboard overview metrics
- User activity analytics
- AI usage statistics
- Performance metrics
- Error tracking
- Export capabilities
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import uuid

from core.database import get_db
from api.auth import get_current_user
from models.user import User
from services.analytics import get_analytics_engine


# Create router
router = APIRouter()


# ==================== Response Models ====================

class DashboardMetrics(BaseModel):
    """Dashboard overview metrics."""
    # User metrics
    total_users: int
    active_users_24h: int
    active_users_7d: int
    new_users_today: int
    
    # Activity metrics
    total_events: int
    total_api_calls: int
    total_sessions: int
    
    # AI metrics
    total_ai_queries: int
    total_tokens_used: int
    total_ai_cost_credits: int
    
    # Performance metrics
    avg_response_time_ms: int
    error_rate: float
    uptime_percentage: float
    
    # Period
    period_days: int
    generated_at: datetime


class UserActivityMetrics(BaseModel):
    """User activity analytics."""
    user_id: uuid.UUID
    username: str
    total_sessions: int
    total_events: int
    total_ai_queries: int
    total_tokens_used: int
    last_active: datetime
    signup_date: datetime


class AIUsageMetrics(BaseModel):
    """AI usage statistics."""
    model: str
    provider: str
    total_queries: int
    total_tokens: int
    total_cost_credits: int
    avg_response_time_ms: int
    success_rate: float


class PerformanceMetrics(BaseModel):
    """API performance metrics."""
    endpoint: str
    http_method: str
    total_calls: int
    avg_response_time_ms: int
    p95_response_time_ms: int
    error_rate: float
    slowest_response_ms: int


class ErrorSummary(BaseModel):
    """Error tracking summary."""
    error_type: str
    occurrences: int
    affected_users: int
    last_occurrence: datetime
    resolved_count: int
    unresolved_count: int


# ==================== API Endpoints ====================

@router.get("/dashboard", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    days: int = Query(default=30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get dashboard overview metrics.
    
    Args:
        days: Number of days to include in metrics (1-365)
        
    Returns:
        Dashboard metrics including users, activity, AI usage, and performance
    """
    # Only allow admins to view analytics
    # TODO: Add role check when RBAC is implemented
    
    try:
        # Get comprehensive metrics
        result = await db.execute(
            text("""
                WITH period AS (
                    SELECT NOW() - INTERVAL :days DAY as start_date
                ),
                user_metrics AS (
                    SELECT 
                        COUNT(*) as total,
                        COUNT(*) FILTER (WHERE created_at > (SELECT start_date FROM period)) as new_today,
                        COUNT(DISTINCT e.user_id) FILTER (WHERE e.timestamp > NOW() - INTERVAL '24 hours') as active_24h,
                        COUNT(DISTINCT e.user_id) FILTER (WHERE e.timestamp > NOW() - INTERVAL '7 days') as active_7d
                    FROM users u
                    LEFT JOIN analytics.events e ON u.id = e.user_id
                ),
                activity_metrics AS (
                    SELECT 
                        COUNT(*) as total_events,
                        COUNT(DISTINCT session_id) as total_sessions
                    FROM analytics.events
                    WHERE timestamp > (SELECT start_date FROM period)
                ),
                api_metrics AS (
                    SELECT 
                        COUNT(*) as total_calls,
                        AVG(response_time_ms)::INTEGER as avg_response_time,
                        SUM(CASE WHEN success = false THEN 1 ELSE 0 END)::FLOAT / NULLIF(COUNT(*), 0) as error_rate
                    FROM analytics.api_performance
                    WHERE timestamp > (SELECT start_date FROM period)
                ),
                ai_metrics AS (
                    SELECT 
                        COUNT(*) as total_queries,
                        SUM(total_tokens) as total_tokens,
                        SUM(estimated_cost_credits) as total_cost
                    FROM analytics.ai_usage
                    WHERE timestamp > (SELECT start_date FROM period)
                )
                SELECT 
                    (SELECT total FROM user_metrics) as total_users,
                    (SELECT active_24h FROM user_metrics) as active_users_24h,
                    (SELECT active_7d FROM user_metrics) as active_7d,
                    (SELECT new_today FROM user_metrics) as new_users_today,
                    (SELECT total_events FROM activity_metrics) as total_events,
                    (SELECT total_calls FROM api_metrics) as total_api_calls,
                    (SELECT total_sessions FROM activity_metrics) as total_sessions,
                    (SELECT total_queries FROM ai_metrics) as total_ai_queries,
                    (SELECT total_tokens FROM ai_metrics) as total_tokens_used,
                    (SELECT total_cost FROM ai_metrics) as total_ai_cost_credits,
                    (SELECT avg_response_time FROM api_metrics) as avg_response_time_ms,
                    (SELECT error_rate FROM api_metrics) as error_rate
            """),
            {'days': days}
        )
        
        row = result.first()
        
        return DashboardMetrics(
            total_users=row.total_users or 0,
            active_users_24h=row.active_users_24h or 0,
            active_users_7d=row.active_7d or 0,
            new_users_today=row.new_users_today or 0,
            total_events=row.total_events or 0,
            total_api_calls=row.total_api_calls or 0,
            total_sessions=row.total_sessions or 0,
            total_ai_queries=row.total_ai_queries or 0,
            total_tokens_used=row.total_tokens_used or 0,
            total_ai_cost_credits=row.total_ai_cost_credits or 0,
            avg_response_time_ms=row.avg_response_time_ms or 0,
            error_rate=float(row.error_rate or 0.0),
            uptime_percentage=99.9,  # Calculate from system_health table
            period_days=days,
            generated_at=datetime.now(timezone.utc)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch dashboard metrics: {str(e)}")


@router.get("/users", response_model=List[UserActivityMetrics])
async def get_user_activity_metrics(
    limit: int = Query(default=100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user activity metrics.
    
    Args:
        limit: Maximum number of users to return
        
    Returns:
        List of user activity metrics sorted by last active
    """
    try:
        result = await db.execute(
            text("""
                SELECT 
                    u.id,
                    u.username,
                    COUNT(DISTINCT s.id) as total_sessions,
                    COUNT(e.id) as total_events,
                    COUNT(ai.id) as total_ai_queries,
                    SUM(ai.total_tokens) as total_tokens,
                    MAX(e.timestamp) as last_active,
                    u.created_at
                FROM users u
                LEFT JOIN analytics.user_sessions s ON u.id = s.user_id
                LEFT JOIN analytics.events e ON u.id = e.user_id
                LEFT JOIN analytics.ai_usage ai ON u.id = ai.user_id
                GROUP BY u.id, u.username, u.created_at
                ORDER BY last_active DESC NULLS LAST
                LIMIT :limit
            """),
            {'limit': limit}
        )
        
        users = []
        for row in result:
            users.append(UserActivityMetrics(
                user_id=row.id,
                username=row.username,
                total_sessions=row.total_sessions or 0,
                total_events=row.total_events or 0,
                total_ai_queries=row.total_ai_queries or 0,
                total_tokens_used=row.total_tokens or 0,
                last_active=row.last_active or row.created_at,
                signup_date=row.created_at
            ))
        
        return users
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch user metrics: {str(e)}")


@router.get("/ai", response_model=List[AIUsageMetrics])
async def get_ai_usage_metrics(
    days: int = Query(default=30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get AI usage statistics by model.
    
    Args:
        days: Number of days to include
        
    Returns:
        List of AI usage metrics per model
    """
    try:
        result = await db.execute(
            text("""
                SELECT 
                    model,
                    provider,
                    COUNT(*) as total_queries,
                    SUM(total_tokens) as total_tokens,
                    SUM(estimated_cost_credits) as total_cost,
                    AVG(response_time_ms)::INTEGER as avg_response_time,
                    SUM(CASE WHEN success THEN 1 ELSE 0 END)::FLOAT / NULLIF(COUNT(*), 0) as success_rate
                FROM analytics.ai_usage
                WHERE timestamp > NOW() - INTERVAL :days DAY
                GROUP BY model, provider
                ORDER BY total_queries DESC
            """),
            {'days': days}
        )
        
        metrics = []
        for row in result:
            metrics.append(AIUsageMetrics(
                model=row.model,
                provider=row.provider,
                total_queries=row.total_queries or 0,
                total_tokens=row.total_tokens or 0,
                total_cost_credits=row.total_cost or 0,
                avg_response_time_ms=row.avg_response_time or 0,
                success_rate=float(row.success_rate or 0.0)
            ))
        
        return metrics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch AI metrics: {str(e)}")


@router.get("/performance", response_model=List[PerformanceMetrics])
async def get_performance_metrics(
    days: int = Query(default=7, ge=1, le=90),
    limit: int = Query(default=50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get API performance metrics by endpoint.
    
    Args:
        days: Number of days to include
        limit: Maximum number of endpoints to return
        
    Returns:
        List of performance metrics per endpoint
    """
    try:
        result = await db.execute(
            text("""
                SELECT 
                    endpoint,
                    http_method,
                    COUNT(*) as total_calls,
                    AVG(response_time_ms)::INTEGER as avg_response_time,
                    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time_ms)::INTEGER as p95_response_time,
                    SUM(CASE WHEN success = false THEN 1 ELSE 0 END)::FLOAT / NULLIF(COUNT(*), 0) as error_rate,
                    MAX(response_time_ms) as slowest_response
                FROM analytics.api_performance
                WHERE timestamp > NOW() - INTERVAL :days DAY
                GROUP BY endpoint, http_method
                ORDER BY total_calls DESC
                LIMIT :limit
            """),
            {'days': days, 'limit': limit}
        )
        
        metrics = []
        for row in result:
            metrics.append(PerformanceMetrics(
                endpoint=row.endpoint,
                http_method=row.http_method,
                total_calls=row.total_calls or 0,
                avg_response_time_ms=row.avg_response_time or 0,
                p95_response_time_ms=row.p95_response_time or 0,
                error_rate=float(row.error_rate or 0.0),
                slowest_response_ms=row.slowest_response or 0
            ))
        
        return metrics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch performance metrics: {str(e)}")


@router.get("/errors", response_model=List[ErrorSummary])
async def get_error_summary(
    days: int = Query(default=7, ge=1, le=90),
    severity: Optional[str] = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get error tracking summary.
    
    Args:
        days: Number of days to include
        severity: Filter by severity (warning, error, critical)
        
    Returns:
        List of error summaries
    """
    try:
        # Build query with optional severity filter
        query = """
            SELECT 
                error_type,
                COUNT(*) as occurrences,
                COUNT(DISTINCT user_id) as affected_users,
                MAX(timestamp) as last_occurrence,
                SUM(CASE WHEN resolved THEN 1 ELSE 0 END) as resolved_count,
                SUM(CASE WHEN NOT resolved THEN 1 ELSE 0 END) as unresolved_count
            FROM analytics.errors
            WHERE timestamp > NOW() - INTERVAL :days DAY
        """
        
        params = {'days': days}
        
        if severity:
            query += " AND severity = :severity"
            params['severity'] = severity
        
        query += """
            GROUP BY error_type
            ORDER BY occurrences DESC
        """
        
        result = await db.execute(text(query), params)
        
        errors = []
        for row in result:
            errors.append(ErrorSummary(
                error_type=row.error_type,
                occurrences=row.occurrences or 0,
                affected_users=row.affected_users or 0,
                last_occurrence=row.last_occurrence,
                resolved_count=row.resolved_count or 0,
                unresolved_count=row.unresolved_count or 0
            ))
        
        return errors
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch error summary: {str(e)}")


@router.get("/events")
async def get_recent_events(
    limit: int = Query(default=100, ge=1, le=1000),
    event_type: Optional[str] = Query(default=None),
    category: Optional[str] = Query(default=None),
    user_id: Optional[uuid.UUID] = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get recent events with optional filtering.
    
    Args:
        limit: Maximum number of events to return
        event_type: Filter by event type
        category: Filter by category
        user_id: Filter by user ID
        
    Returns:
        List of recent events
    """
    try:
        # Build dynamic query based on filters
        query = "SELECT * FROM analytics.events WHERE 1=1"
        params = {}
        
        if event_type:
            query += " AND event_type = :event_type"
            params['event_type'] = event_type
        
        if category:
            query += " AND category = :category"
            params['category'] = category
        
        if user_id:
            query += " AND user_id = :user_id"
            params['user_id'] = user_id
        
        query += " ORDER BY timestamp DESC LIMIT :limit"
        params['limit'] = limit
        
        result = await db.execute(text(query), params)
        
        events = []
        for row in result:
            events.append({
                'id': str(row.id),
                'event_type': row.event_type,
                'category': row.category,
                'user_id': str(row.user_id) if row.user_id else None,
                'timestamp': row.timestamp.isoformat(),
                'data': row.data,
                'success': row.success,
                'severity': row.severity
            })
        
        return events
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch events: {str(e)}")


@router.get("/export")
async def export_analytics(
    format: str = Query(default="json", regex="^(json|csv)$"),
    days: int = Query(default=30, ge=1, le=365),
    table: str = Query(default="events"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Export analytics data in JSON or CSV format.
    
    Args:
        format: Export format (json or csv)
        days: Number of days of data to export
        table: Table to export (events, ai_usage, etc.)
        
    Returns:
        Exported data in requested format
    """
    # Validate table name (security - prevent SQL injection)
    allowed_tables = ['events', 'ai_usage', 'api_performance', 'feature_usage', 'errors']
    if table not in allowed_tables:
        raise HTTPException(status_code=400, detail=f"Invalid table. Allowed: {', '.join(allowed_tables)}")
    
    try:
        result = await db.execute(
            text(f"""
                SELECT * FROM analytics.{table}
                WHERE timestamp > NOW() - INTERVAL :days DAY
                ORDER BY timestamp DESC
                LIMIT 10000
            """),
            {'days': days}
        )
        
        rows = result.fetchall()
        
        if format == "json":
            data = []
            for row in rows:
                # Convert row to dict
                row_dict = dict(row._mapping)
                # Convert non-serializable types
                for key, value in row_dict.items():
                    if isinstance(value, (datetime, uuid.UUID)):
                        row_dict[key] = str(value)
                data.append(row_dict)
            
            return {"data": data, "count": len(data), "table": table}
        
        elif format == "csv":
            # Generate CSV
            import csv
            from io import StringIO
            
            output = StringIO()
            if rows:
                writer = csv.DictWriter(output, fieldnames=rows[0]._mapping.keys())
                writer.writeheader()
                
                for row in rows:
                    row_dict = dict(row._mapping)
                    # Convert to strings
                    for key, value in row_dict.items():
                        if isinstance(value, (datetime, uuid.UUID)):
                            row_dict[key] = str(value)
                    writer.writerow(row_dict)
            
            from fastapi.responses import StreamingResponse
            import io
            
            output.seek(0)
            return StreamingResponse(
                io.BytesIO(output.getvalue().encode()),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename=analytics_{table}_{datetime.now().strftime('%Y%m%d')}.csv"}
            )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export data: {str(e)}")


@router.post("/aggregate")
async def trigger_aggregation(
    date: Optional[str] = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Manually trigger metrics aggregation for a specific date.
    
    Args:
        date: Date to aggregate (YYYY-MM-DD), defaults to today
        
    Returns:
        Aggregation result
    """
    target_date = date if date else datetime.now().strftime('%Y-%m-%d')
    
    try:
        # Call aggregation function
        await db.execute(
            text("SELECT analytics.aggregate_daily_metrics(:target_date::DATE)"),
            {'target_date': target_date}
        )
        await db.commit()
        
        return {
            "success": True,
            "message": f"Metrics aggregated for {target_date}",
            "date": target_date
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Aggregation failed: {str(e)}")


@router.get("/realtime/stats")
async def get_realtime_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get real-time statistics (last 5 minutes).
    
    Returns:
        Real-time platform statistics
    """
    try:
        result = await db.execute(
            text("""
                WITH realtime_window AS (
                    SELECT NOW() - INTERVAL '5 minutes' as start_time
                )
                SELECT 
                    (SELECT COUNT(DISTINCT user_id) FROM analytics.events 
                     WHERE timestamp > (SELECT start_time FROM realtime_window) 
                     AND user_id IS NOT NULL) as active_users_now,
                    
                    (SELECT COUNT(*) FROM analytics.events 
                     WHERE timestamp > (SELECT start_time FROM realtime_window)) as events_last_5min,
                    
                    (SELECT COUNT(*) FROM analytics.ai_usage 
                     WHERE timestamp > (SELECT start_time FROM realtime_window)) as ai_queries_last_5min,
                    
                    (SELECT AVG(response_time_ms)::INTEGER FROM analytics.api_performance 
                     WHERE timestamp > (SELECT start_time FROM realtime_window)) as avg_response_time_5min
            """)
        )
        
        row = result.first()
        
        return {
            "active_users_now": row.active_users_now or 0,
            "events_last_5min": row.events_last_5min or 0,
            "ai_queries_last_5min": row.ai_queries_last_5min or 0,
            "avg_response_time_ms": row.avg_response_time_5min or 0,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch realtime stats: {str(e)}")

