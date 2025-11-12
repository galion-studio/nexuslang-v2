"""
Analytics Middleware for NexusLang v2
======================================

Automatically tracks all API requests for analytics.

Features:
- Transparent request/response tracking
- Performance monitoring
- Error tracking
- User session management
- Zero performance impact (async background processing)
"""

import time
import uuid
from typing import Callable, Optional
from datetime import datetime, timezone

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from services.analytics import get_analytics_engine, EventType, EventCategory


class AnalyticsMiddleware(BaseHTTPMiddleware):
    """
    Middleware that automatically tracks all API requests.
    
    Tracks:
    - Request/response times
    - HTTP status codes
    - User activity
    - Error rates
    - Endpoint usage
    """
    
    def __init__(self, app: ASGIApp):
        """
        Initialize analytics middleware.
        
        Args:
            app: ASGI application
        """
        super().__init__(app)
        self.analytics = get_analytics_engine()
        
        # Endpoints to exclude from tracking (too noisy)
        self.excluded_paths = {
            '/health',
            '/metrics',
            '/favicon.ico'
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and track analytics.
        
        Args:
            request: Incoming request
            call_next: Next middleware/handler
            
        Returns:
            Response from handler
        """
        # Skip excluded paths
        if request.url.path in self.excluded_paths:
            return await call_next(request)
        
        # Start timing
        start_time = time.time()
        
        # Extract request info
        user_id = None
        session_id = None
        
        # Try to get user from request state (set by auth middleware)
        if hasattr(request.state, 'user_id'):
            user_id = request.state.user_id
        
        # Try to get session ID from header or create new one
        session_id_header = request.headers.get('X-Session-ID')
        if session_id_header:
            try:
                session_id = uuid.UUID(session_id_header)
            except ValueError:
                session_id = None
        
        # Get client info
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get('user-agent', '')
        
        # Process request
        response = None
        error_occurred = False
        error_message = None
        status_code = 500
        
        try:
            response = await call_next(request)
            status_code = response.status_code
            
        except Exception as e:
            # Track error
            error_occurred = True
            error_message = str(e)
            status_code = 500
            
            # Re-raise to let error handlers deal with it
            raise
        
        finally:
            # Calculate response time
            end_time = time.time()
            response_time_ms = int((end_time - start_time) * 1000)
            
            # Determine success
            success = 200 <= status_code < 400
            
            # Determine category from endpoint
            category = self._get_category_from_endpoint(request.url.path)
            event_type = EventType.API_CALL
            
            # Track API performance (don't await - fire and forget)
            asyncio.create_task(
                self.analytics.track_api_performance(
                    endpoint=request.url.path,
                    http_method=request.method,
                    response_time_ms=response_time_ms,
                    status_code=status_code,
                    user_id=user_id,
                    error_type=type(error_occurred).__name__ if error_occurred else None,
                    error_message=error_message
                )
            )
            
            # Track general event (don't await)
            asyncio.create_task(
                self.analytics.publish_event(
                    event_type=event_type,
                    category=category,
                    user_id=user_id,
                    session_id=session_id,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    endpoint=request.url.path,
                    http_method=request.method,
                    processing_time_ms=response_time_ms,
                    success=success,
                    error_message=error_message,
                    severity='error' if error_occurred else 'info',
                    data={
                        'status_code': status_code,
                        'query_params': str(request.query_params) if request.query_params else None
                    }
                )
            )
        
        return response
    
    def _get_category_from_endpoint(self, path: str) -> EventCategory:
        """
        Determine event category from endpoint path.
        
        Args:
            path: Request path
            
        Returns:
            EventCategory
        """
        if '/auth' in path:
            return EventCategory.AUTH
        elif '/ai' in path:
            return EventCategory.AI
        elif '/ide' in path:
            return EventCategory.IDE
        elif '/grokopedia' in path:
            return EventCategory.GROKOPEDIA
        elif '/community' in path:
            return EventCategory.COMMUNITY
        elif '/billing' in path:
            return EventCategory.BILLING
        else:
            return EventCategory.SYSTEM


# Import asyncio for create_task
import asyncio

