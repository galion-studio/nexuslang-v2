"""
Analytics Engine
Real-time tracking and analytics for all user actions and system performance.

Features:
- Request tracking
- User behavior analytics
- Performance metrics
- Cost tracking
- Real-time WebSocket updates
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import logging

logger = logging.getLogger(__name__)


class AnalyticsEngine:
    """
    Real-time analytics and tracking engine.
    
    Tracks:
    - API requests
    - User actions
    - System performance
    - Credit usage
    - Errors
    """
    
    def __init__(self):
        self.metrics = {
            "requests_total": 0,
            "requests_success": 0,
            "requests_error": 0,
            "response_times": [],
            "active_users": set(),
            "credits_used_total": 0.0
        }
        self.event_log = []
    
    def track_request(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        response_time: float,
        user_id: Optional[int] = None,
        credits_used: float = 0.0
    ):
        """
        Track an API request.
        
        Args:
            endpoint: API endpoint path
            method: HTTP method
            status_code: Response status code
            response_time: Response time in seconds
            user_id: User ID if authenticated
            credits_used: Credits consumed by this request
        """
        self.metrics["requests_total"] += 1
        
        if 200 <= status_code < 300:
            self.metrics["requests_success"] += 1
        else:
            self.metrics["requests_error"] += 1
        
        self.metrics["response_times"].append(response_time)
        
        # Keep only last 1000 response times
        if len(self.metrics["response_times"]) > 1000:
            self.metrics["response_times"] = self.metrics["response_times"][-1000:]
        
        if user_id:
            self.metrics["active_users"].add(user_id)
        
        self.metrics["credits_used_total"] += credits_used
        
        # Log event
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "request",
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "response_time": response_time,
            "user_id": user_id,
            "credits_used": credits_used
        }
        
        self.event_log.append(event)
        
        # Keep only last 10000 events
        if len(self.event_log) > 10000:
            self.event_log = self.event_log[-10000:]
    
    def track_user_action(
        self,
        user_id: int,
        action: str,
        metadata: Optional[Dict] = None
    ):
        """
        Track a user action.
        
        Args:
            user_id: User ID
            action: Action type (login, logout, code_execute, image_generate, etc.)
            metadata: Additional action metadata
        """
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "user_action",
            "user_id": user_id,
            "action": action,
            "metadata": metadata or {}
        }
        
        self.event_log.append(event)
    
    def get_stats(self) -> Dict:
        """
        Get current analytics statistics.
        
        Returns dict with all current metrics.
        """
        response_times = self.metrics["response_times"]
        
        if response_times:
            avg_response = sum(response_times) / len(response_times)
            p95_response = sorted(response_times)[int(len(response_times) * 0.95)]
            p99_response = sorted(response_times)[int(len(response_times) * 0.99)]
        else:
            avg_response = p95_response = p99_response = 0
        
        success_rate = (
            (self.metrics["requests_success"] / max(self.metrics["requests_total"], 1)) * 100
        )
        
        return {
            "requests": {
                "total": self.metrics["requests_total"],
                "success": self.metrics["requests_success"],
                "error": self.metrics["requests_error"],
                "success_rate": round(success_rate, 2)
            },
            "performance": {
                "avg_response_time": round(avg_response * 1000, 2),  # ms
                "p95_response_time": round(p95_response * 1000, 2),
                "p99_response_time": round(p99_response * 1000, 2)
            },
            "users": {
                "active": len(self.metrics["active_users"])
            },
            "credits": {
                "total_used": round(self.metrics["credits_used_total"], 2)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_recent_events(self, limit: int = 100) -> List[Dict]:
        """Get recent events from the log."""
        return self.event_log[-limit:]
    
    def reset_metrics(self):
        """Reset all metrics (for testing or period boundaries)."""
        self.metrics = {
            "requests_total": 0,
            "requests_success": 0,
            "requests_error": 0,
            "response_times": [],
            "active_users": set(),
            "credits_used_total": 0.0
        }
        logger.info("Analytics metrics reset")


# Global analytics instance
_analytics_instance = None

def get_analytics() -> AnalyticsEngine:
    """Get global analytics instance (singleton)."""
    global _analytics_instance
    if _analytics_instance is None:
        _analytics_instance = AnalyticsEngine()
    return _analytics_instance
