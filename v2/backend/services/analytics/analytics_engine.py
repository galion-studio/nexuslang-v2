"""
Analytics Engine for NexusLang v2
==================================

Real-time event publishing and metrics aggregation.

Features:
- Async event publishing to PostgreSQL
- In-memory buffering for performance
- Automatic aggregation
- Background workers
- Cost tracking for AI usage
"""

from typing import Dict, Optional, Any, List
from datetime import datetime, timezone
from enum import Enum
import uuid
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from collections import defaultdict
import json

from core.database import get_db
from core.redis_client import get_redis


class EventType(str, Enum):
    """Standard event types for analytics."""
    # Authentication events
    USER_REGISTERED = "user_registered"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    PASSWORD_RESET = "password_reset"
    
    # AI events
    AI_QUERY = "ai_query"
    AI_CHAT = "ai_chat"
    AI_CODE_GENERATION = "ai_code_generation"
    AI_ERROR = "ai_error"
    
    # IDE events
    CODE_EXECUTED = "code_executed"
    FILE_CREATED = "file_created"
    FILE_UPDATED = "file_updated"
    FILE_DELETED = "file_deleted"
    PROJECT_CREATED = "project_created"
    PROJECT_OPENED = "project_opened"
    
    # Grokopedia events
    KNOWLEDGE_SEARCH = "knowledge_search"
    KNOWLEDGE_VIEWED = "knowledge_viewed"
    KNOWLEDGE_CREATED = "knowledge_created"
    
    # Community events
    POST_CREATED = "post_created"
    POST_VIEWED = "post_viewed"
    COMMENT_CREATED = "comment_created"
    
    # Billing events
    SUBSCRIPTION_CREATED = "subscription_created"
    SUBSCRIPTION_UPGRADED = "subscription_upgraded"
    CREDITS_PURCHASED = "credits_purchased"
    
    # System events
    API_CALL = "api_call"
    ERROR_OCCURRED = "error_occurred"
    SYSTEM_HEALTH_CHECK = "system_health_check"


class EventCategory(str, Enum):
    """Event categories for grouping."""
    AUTH = "auth"
    AI = "ai"
    IDE = "ide"
    GROKOPEDIA = "grokopedia"
    COMMUNITY = "community"
    BILLING = "billing"
    SYSTEM = "system"


class AnalyticsEngine:
    """
    Core analytics engine for event tracking and metrics.
    """
    
    def __init__(self):
        """Initialize analytics engine."""
        self.buffer: List[Dict] = []  # In-memory event buffer
        self.buffer_size = 100  # Flush after 100 events
        self.buffer_lock = asyncio.Lock()
        self.session_cache: Dict[str, uuid.UUID] = {}  # Session ID cache
    
    async def publish_event(
        self,
        event_type: EventType | str,
        category: EventCategory | str,
        user_id: Optional[uuid.UUID] = None,
        session_id: Optional[uuid.UUID] = None,
        data: Dict[str, Any] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        endpoint: Optional[str] = None,
        http_method: Optional[str] = None,
        processing_time_ms: Optional[int] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        severity: str = "info"
    ):
        """
        Publish an event to the analytics system.
        
        This is the main entry point for all analytics tracking.
        Events are buffered and batch-inserted for performance.
        
        Args:
            event_type: Type of event (from EventType enum)
            category: Event category (from EventCategory enum)
            user_id: User who triggered the event (optional)
            session_id: Session ID for flow tracking (optional)
            data: Event-specific data (optional)
            ip_address: Client IP (optional)
            user_agent: Client user agent (optional)
            endpoint: API endpoint path (optional)
            http_method: HTTP method (optional)
            processing_time_ms: Time taken to process (optional)
            success: Whether operation succeeded
            error_message: Error details if failed (optional)
            severity: Event severity level (default: info)
        """
        event = {
            'id': uuid.uuid4(),
            'event_type': str(event_type),
            'category': str(category),
            'user_id': user_id,
            'session_id': session_id,
            'service': 'backend',
            'ip_address': ip_address,
            'user_agent': user_agent,
            'endpoint': endpoint,
            'http_method': http_method,
            'data': json.dumps(data or {}),
            'severity': severity,
            'success': success,
            'error_message': error_message,
            'timestamp': datetime.now(timezone.utc),
            'processing_time_ms': processing_time_ms
        }
        
        # Add to buffer
        async with self.buffer_lock:
            self.buffer.append(event)
            
            # Flush if buffer is full
            if len(self.buffer) >= self.buffer_size:
                await self._flush_buffer()
    
    async def _flush_buffer(self):
        """
        Flush buffered events to database.
        Called automatically when buffer is full or manually.
        """
        if not self.buffer:
            return
        
        # Get events to flush (clear buffer immediately to avoid blocking)
        events_to_flush = self.buffer.copy()
        self.buffer.clear()
        
        try:
            # Get database session
            async for db in get_db():
                # Batch insert events
                await db.execute(
                    text("""
                        INSERT INTO analytics.events (
                            id, event_type, category, user_id, session_id,
                            service, ip_address, user_agent, endpoint, http_method,
                            data, severity, success, error_message, timestamp,
                            processing_time_ms
                        ) VALUES (
                            :id, :event_type, :category, :user_id, :session_id,
                            :service, :ip_address, :user_agent, :endpoint, :http_method,
                            :data::jsonb, :severity, :success, :error_message, :timestamp,
                            :processing_time_ms
                        )
                    """),
                    events_to_flush
                )
                await db.commit()
                break  # Exit after first successful insert
                
        except Exception as e:
            print(f"⚠️  Analytics flush error: {e}")
            # Don't crash the app if analytics fail
    
    async def track_ai_usage(
        self,
        user_id: Optional[uuid.UUID],
        session_id: Optional[uuid.UUID],
        model: str,
        provider: str,
        request_type: str,
        prompt_tokens: int,
        completion_tokens: int,
        response_time_ms: int,
        success: bool = True,
        error_message: Optional[str] = None,
        prompt_sample: Optional[str] = None,
        response_sample: Optional[str] = None
    ):
        """
        Track AI model usage for cost and performance monitoring.
        
        Args:
            user_id: User making the request
            session_id: Session ID
            model: AI model used (e.g., 'anthropic/claude-3.5-sonnet')
            provider: Provider name (e.g., 'openrouter')
            request_type: Type of request (chat, completion, etc.)
            prompt_tokens: Number of input tokens
            completion_tokens: Number of output tokens
            response_time_ms: Response time in milliseconds
            success: Whether request succeeded
            error_message: Error details if failed
            prompt_sample: First 500 chars of prompt (for debugging)
            response_sample: First 500 chars of response
        """
        total_tokens = prompt_tokens + completion_tokens
        
        # Estimate cost (rough estimate - adjust based on actual pricing)
        # Default: 1 credit per 1K tokens
        estimated_cost_credits = max(1, total_tokens // 1000)
        
        # Different models have different costs
        cost_multipliers = {
            'anthropic/claude-3.5-sonnet': 3,
            'openai/gpt-4-turbo': 2,
            'openai/gpt-3.5-turbo': 1,
        }
        estimated_cost_credits *= cost_multipliers.get(model, 1)
        
        # Estimate USD cost (rough - $0.01 per 1K tokens average)
        estimated_cost_usd = (total_tokens / 1000) * 0.01
        
        try:
            async for db in get_db():
                await db.execute(
                    text("""
                        INSERT INTO analytics.ai_usage (
                            user_id, session_id, model, provider, request_type,
                            prompt_tokens, completion_tokens, total_tokens,
                            estimated_cost_credits, estimated_cost_usd,
                            response_time_ms, success, error_message,
                            prompt_sample, response_sample, timestamp
                        ) VALUES (
                            :user_id, :session_id, :model, :provider, :request_type,
                            :prompt_tokens, :completion_tokens, :total_tokens,
                            :estimated_cost_credits, :estimated_cost_usd,
                            :response_time_ms, :success, :error_message,
                            :prompt_sample, :response_sample, NOW()
                        )
                    """),
                    {
                        'user_id': user_id,
                        'session_id': session_id,
                        'model': model,
                        'provider': provider,
                        'request_type': request_type,
                        'prompt_tokens': prompt_tokens,
                        'completion_tokens': completion_tokens,
                        'total_tokens': total_tokens,
                        'estimated_cost_credits': estimated_cost_credits,
                        'estimated_cost_usd': estimated_cost_usd,
                        'response_time_ms': response_time_ms,
                        'success': success,
                        'error_message': error_message,
                        'prompt_sample': prompt_sample[:500] if prompt_sample else None,
                        'response_sample': response_sample[:500] if response_sample else None
                    }
                )
                await db.commit()
                break
        except Exception as e:
            print(f"⚠️  AI usage tracking error: {e}")
    
    async def track_api_performance(
        self,
        endpoint: str,
        http_method: str,
        response_time_ms: int,
        status_code: int,
        user_id: Optional[uuid.UUID] = None,
        error_type: Optional[str] = None,
        error_message: Optional[str] = None
    ):
        """
        Track API endpoint performance.
        
        Args:
            endpoint: API endpoint path
            http_method: HTTP method (GET, POST, etc.)
            response_time_ms: Response time in milliseconds
            status_code: HTTP status code
            user_id: User making request (optional)
            error_type: Type of error if failed
            error_message: Error details
        """
        success = 200 <= status_code < 400
        
        try:
            async for db in get_db():
                await db.execute(
                    text("""
                        INSERT INTO analytics.api_performance (
                            endpoint, http_method, response_time_ms, status_code,
                            success, error_type, error_message, user_id,
                            authenticated, timestamp
                        ) VALUES (
                            :endpoint, :http_method, :response_time_ms, :status_code,
                            :success, :error_type, :error_message, :user_id,
                            :authenticated, NOW()
                        )
                    """),
                    {
                        'endpoint': endpoint,
                        'http_method': http_method,
                        'response_time_ms': response_time_ms,
                        'status_code': status_code,
                        'success': success,
                        'error_type': error_type,
                        'error_message': error_message,
                        'user_id': user_id,
                        'authenticated': user_id is not None
                    }
                )
                await db.commit()
                break
        except Exception as e:
            print(f"⚠️  API performance tracking error: {e}")
    
    async def track_feature_usage(
        self,
        feature_name: str,
        feature_category: str,
        action: str,
        user_id: Optional[uuid.UUID] = None,
        session_id: Optional[uuid.UUID] = None,
        duration_seconds: Optional[int] = None,
        metadata: Dict[str, Any] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ):
        """
        Track usage of specific platform features.
        
        Args:
            feature_name: Feature identifier (e.g., 'ide_code_editor')
            feature_category: Category (ide, ai, community, etc.)
            action: User action (opened, closed, used, etc.)
            user_id: User performing action
            session_id: Session ID
            duration_seconds: How long feature was used
            metadata: Additional feature-specific data
            success: Whether action succeeded
            error_message: Error details if failed
        """
        try:
            async for db in get_db():
                await db.execute(
                    text("""
                        INSERT INTO analytics.feature_usage (
                            feature_name, feature_category, action,
                            user_id, session_id, duration_seconds,
                            metadata, success, error_message, timestamp
                        ) VALUES (
                            :feature_name, :feature_category, :action,
                            :user_id, :session_id, :duration_seconds,
                            :metadata::jsonb, :success, :error_message, NOW()
                        )
                    """),
                    {
                        'feature_name': feature_name,
                        'feature_category': feature_category,
                        'action': action,
                        'user_id': user_id,
                        'session_id': session_id,
                        'duration_seconds': duration_seconds,
                        'metadata': json.dumps(metadata or {}),
                        'success': success,
                        'error_message': error_message
                    }
                )
                await db.commit()
                break
        except Exception as e:
            print(f"⚠️  Feature usage tracking error: {e}")
    
    async def track_error(
        self,
        error_type: str,
        error_message: str,
        stack_trace: Optional[str] = None,
        user_id: Optional[uuid.UUID] = None,
        session_id: Optional[uuid.UUID] = None,
        endpoint: Optional[str] = None,
        http_method: Optional[str] = None,
        severity: str = "error",
        request_body: Dict = None,
        request_headers: Dict = None
    ):
        """
        Track errors for monitoring and debugging.
        
        Args:
            error_type: Type/class of error
            error_message: Error message
            stack_trace: Full stack trace (optional)
            user_id: User who encountered error
            session_id: Session ID
            endpoint: Endpoint where error occurred
            http_method: HTTP method
            severity: warning, error, or critical
            request_body: Request data (sanitized)
            request_headers: Request headers (sanitized)
        """
        try:
            async for db in get_db():
                await db.execute(
                    text("""
                        INSERT INTO analytics.errors (
                            error_type, error_message, stack_trace,
                            user_id, session_id, endpoint, http_method,
                            severity, request_body, request_headers,
                            service, timestamp
                        ) VALUES (
                            :error_type, :error_message, :stack_trace,
                            :user_id, :session_id, :endpoint, :http_method,
                            :severity, :request_body::jsonb, :request_headers::jsonb,
                            'backend', NOW()
                        )
                    """),
                    {
                        'error_type': error_type,
                        'error_message': error_message[:1000],  # Limit size
                        'stack_trace': stack_trace[:5000] if stack_trace else None,
                        'user_id': user_id,
                        'session_id': session_id,
                        'endpoint': endpoint,
                        'http_method': http_method,
                        'severity': severity,
                        'request_body': json.dumps(request_body or {}),
                        'request_headers': json.dumps(request_headers or {})
                    }
                )
                await db.commit()
                break
        except Exception as e:
            print(f"⚠️  Error tracking error (!): {e}")
    
    async def create_session(
        self,
        user_id: uuid.UUID,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> uuid.UUID:
        """
        Create a new user session for tracking.
        
        Args:
            user_id: User ID
            ip_address: Client IP
            user_agent: Client user agent
            
        Returns:
            Session ID (UUID)
        """
        session_id = uuid.uuid4()
        
        # Parse user agent for device info (simplified)
        device_type = "desktop"
        browser = "unknown"
        os_name = "unknown"
        
        if user_agent:
            user_agent_lower = user_agent.lower()
            if 'mobile' in user_agent_lower or 'android' in user_agent_lower:
                device_type = "mobile"
            elif 'tablet' in user_agent_lower or 'ipad' in user_agent_lower:
                device_type = "tablet"
            
            if 'chrome' in user_agent_lower:
                browser = "chrome"
            elif 'firefox' in user_agent_lower:
                browser = "firefox"
            elif 'safari' in user_agent_lower:
                browser = "safari"
            
            if 'windows' in user_agent_lower:
                os_name = "windows"
            elif 'mac' in user_agent_lower:
                os_name = "macos"
            elif 'linux' in user_agent_lower:
                os_name = "linux"
        
        try:
            async for db in get_db():
                await db.execute(
                    text("""
                        INSERT INTO analytics.user_sessions (
                            id, user_id, ip_address, user_agent,
                            device_type, browser, os, session_start
                        ) VALUES (
                            :id, :user_id, :ip_address, :user_agent,
                            :device_type, :browser, :os, NOW()
                        )
                    """),
                    {
                        'id': session_id,
                        'user_id': user_id,
                        'ip_address': ip_address,
                        'user_agent': user_agent,
                        'device_type': device_type,
                        'browser': browser,
                        'os': os_name
                    }
                )
                await db.commit()
                break
        except Exception as e:
            print(f"⚠️  Session creation error: {e}")
        
        return session_id
    
    async def close_session(self, session_id: uuid.UUID, exit_type: str = "normal"):
        """
        Close a user session.
        
        Args:
            session_id: Session ID to close
            exit_type: How session ended (normal, timeout, error)
        """
        try:
            async for db in get_db():
                await db.execute(
                    text("""
                        UPDATE analytics.user_sessions
                        SET 
                            session_end = NOW(),
                            duration_seconds = EXTRACT(EPOCH FROM (NOW() - session_start))::INTEGER,
                            exit_type = :exit_type
                        WHERE id = :session_id AND session_end IS NULL
                    """),
                    {
                        'session_id': session_id,
                        'exit_type': exit_type
                    }
                )
                await db.commit()
                break
        except Exception as e:
            print(f"⚠️  Session close error: {e}")
    
    async def get_dashboard_metrics(self, days: int = 30) -> Dict:
        """
        Get aggregated metrics for dashboard.
        
        Args:
            days: Number of days to include in metrics
            
        Returns:
            Dict with dashboard metrics
        """
        try:
            async for db in get_db():
                # Get total users
                result = await db.execute(text("SELECT COUNT(*) FROM users"))
                total_users = result.scalar() or 0
                
                # Get active users (last 24 hours)
                result = await db.execute(
                    text("""
                        SELECT COUNT(DISTINCT user_id)
                        FROM analytics.events
                        WHERE timestamp > NOW() - INTERVAL '24 hours'
                        AND user_id IS NOT NULL
                    """)
                )
                active_users_24h = result.scalar() or 0
                
                # Get total AI queries
                result = await db.execute(
                    text("""
                        SELECT COUNT(*), SUM(total_tokens), SUM(estimated_cost_credits)
                        FROM analytics.ai_usage
                        WHERE timestamp > NOW() - INTERVAL :days DAY
                    """),
                    {'days': days}
                )
                row = result.first()
                ai_queries = row[0] or 0
                total_tokens = row[1] or 0
                total_cost = row[2] or 0
                
                # Get API call count
                result = await db.execute(
                    text("""
                        SELECT COUNT(*)
                        FROM analytics.api_performance
                        WHERE timestamp > NOW() - INTERVAL :days DAY
                    """),
                    {'days': days}
                )
                api_calls = result.scalar() or 0
                
                # Get error rate
                result = await db.execute(
                    text("""
                        SELECT 
                            SUM(CASE WHEN success = false THEN 1 ELSE 0 END)::FLOAT / NULLIF(COUNT(*), 0) as error_rate
                        FROM analytics.api_performance
                        WHERE timestamp > NOW() - INTERVAL '24 hours'
                    """)
                )
                error_rate = result.scalar() or 0.0
                
                return {
                    'total_users': total_users,
                    'active_users_24h': active_users_24h,
                    'ai_queries': ai_queries,
                    'total_tokens': total_tokens,
                    'total_cost_credits': total_cost,
                    'api_calls': api_calls,
                    'error_rate': float(error_rate),
                    'period_days': days
                }
                
        except Exception as e:
            print(f"⚠️  Dashboard metrics error: {e}")
            return {}
    
    async def flush(self):
        """Manually flush event buffer."""
        async with self.buffer_lock:
            await self._flush_buffer()


# Global analytics engine instance
_analytics_engine: Optional[AnalyticsEngine] = None


def get_analytics_engine() -> AnalyticsEngine:
    """
    Get or create global analytics engine instance.
    
    Returns:
        AnalyticsEngine instance
    """
    global _analytics_engine
    
    if _analytics_engine is None:
        _analytics_engine = AnalyticsEngine()
    
    return _analytics_engine


# Convenience functions for quick access
async def track_event(event_type: str, user_id: Optional[uuid.UUID] = None, **kwargs):
    """Quick shortcut to track an event."""
    engine = get_analytics_engine()
    await engine.publish_event(event_type=event_type, user_id=user_id, **kwargs)


async def track_ai(model: str, prompt_tokens: int, completion_tokens: int, **kwargs):
    """Quick shortcut to track AI usage."""
    engine = get_analytics_engine()
    await engine.track_ai_usage(
        model=model,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        **kwargs
    )

