"""
Analytics Service for NexusLang v2
===================================

Comprehensive event tracking and metrics aggregation.
"""

from .analytics_engine import (
    AnalyticsEngine,
    get_analytics_engine,
    EventType,
    EventCategory
)

__all__ = [
    'AnalyticsEngine',
    'get_analytics_engine',
    'EventType',
    'EventCategory'
]

