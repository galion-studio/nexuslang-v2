#!/usr/bin/env python3
"""
Sentry Integration Setup for Project Nexus
Configures error tracking, performance monitoring, and alerting
"""

import os
import sys
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
import logging

# Sentry DSN from environment
SENTRY_DSN = os.getenv("SENTRY_DSN")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if not SENTRY_DSN:
    print("⚠️  SENTRY_DSN not set, skipping Sentry initialization")
    sys.exit(0)


def init_sentry():
    """
    Initialize Sentry with all integrations
    """
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=ENVIRONMENT,
        
        # Enable performance monitoring
        traces_sample_rate=0.1 if ENVIRONMENT == "production" else 1.0,
        
        # Enable profiling
        profiles_sample_rate=0.1 if ENVIRONMENT == "production" else 1.0,
        
        # Integrations
        integrations=[
            FastApiIntegration(
                transaction_style="endpoint",  # Group by endpoint
                failed_request_status_codes=[500, 501, 502, 503, 504, 505],
            ),
            SqlalchemyIntegration(),
            RedisIntegration(),
            LoggingIntegration(
                level=logging.INFO,  # Capture info and above as breadcrumbs
                event_level=logging.ERROR  # Send errors as events
            ),
        ],
        
        # Release tracking (use git commit hash)
        release=os.getenv("GIT_COMMIT", "unknown"),
        
        # Performance monitoring options
        _experiments={
            "profiles_sample_rate": 0.1,
        },
        
        # Send default PII (Personally Identifiable Information)
        send_default_pii=False,  # GDPR compliance
        
        # Before send hook (sanitize sensitive data)
        before_send=before_send_hook,
        
        # Before breadcrumb hook (filter sensitive breadcrumbs)
        before_breadcrumb=before_breadcrumb_hook,
    )
    
    print(f"✅ Sentry initialized for environment: {ENVIRONMENT}")


def before_send_hook(event, hint):
    """
    Hook to modify events before sending to Sentry.
    Used to sanitize sensitive data.
    """
    # Remove sensitive headers
    if 'request' in event:
        headers = event['request'].get('headers', {})
        sensitive_headers = ['Authorization', 'Cookie', 'X-API-Key']
        for header in sensitive_headers:
            if header in headers:
                headers[header] = '[Filtered]'
    
    # Remove sensitive query parameters
    if 'request' in event and 'query_string' in event['request']:
        query = event['request']['query_string']
        if 'token' in query.lower() or 'key' in query.lower():
            event['request']['query_string'] = '[Filtered]'
    
    # Add custom tags
    event.setdefault('tags', {})
    event['tags']['project'] = 'nexus'
    
    return event


def before_breadcrumb_hook(crumb, hint):
    """
    Hook to filter breadcrumbs before adding to event.
    """
    # Don't log database queries with sensitive data
    if crumb.get('category') == 'query':
        query = crumb.get('message', '').lower()
        if any(word in query for word in ['password', 'secret', 'token']):
            return None
    
    return crumb


# Context managers for custom spans
class SentrySpan:
    """
    Context manager for creating custom performance spans
    
    Usage:
        with SentrySpan("database", "query_users"):
            # Your code here
            pass
    """
    
    def __init__(self, op: str, description: str):
        self.op = op
        self.description = description
        self.span = None
    
    def __enter__(self):
        from sentry_sdk import start_span
        self.span = start_span(op=self.op, description=self.description)
        self.span.__enter__()
        return self.span
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.span:
            self.span.__exit__(exc_type, exc_val, exc_tb)


# Helper functions for error tracking
def capture_exception(error: Exception, **kwargs):
    """
    Capture an exception and send to Sentry
    
    Args:
        error: Exception to capture
        **kwargs: Additional context (user_id, tags, etc.)
    """
    with sentry_sdk.push_scope() as scope:
        # Add user context
        if 'user_id' in kwargs:
            scope.set_user({"id": kwargs['user_id']})
        
        # Add custom tags
        for key, value in kwargs.items():
            if key != 'user_id':
                scope.set_tag(key, value)
        
        sentry_sdk.capture_exception(error)


def capture_message(message: str, level: str = "info", **kwargs):
    """
    Capture a message and send to Sentry
    
    Args:
        message: Message to capture
        level: Severity level (debug, info, warning, error, fatal)
        **kwargs: Additional context
    """
    with sentry_sdk.push_scope() as scope:
        # Add context
        for key, value in kwargs.items():
            scope.set_context(key, value)
        
        sentry_sdk.capture_message(message, level)


def set_user_context(user_id: str, email: str = None, username: str = None):
    """
    Set user context for all future events
    
    Args:
        user_id: User ID
        email: User email (optional)
        username: Username (optional)
    """
    sentry_sdk.set_user({
        "id": user_id,
        "email": email,
        "username": username
    })


def set_context(key: str, value: dict):
    """
    Set custom context for all future events
    
    Args:
        key: Context key
        value: Context data (dict)
    """
    sentry_sdk.set_context(key, value)


# Example usage
if __name__ == "__main__":
    # Initialize Sentry
    init_sentry()
    
    # Test error capture
    try:
        1 / 0
    except Exception as e:
        capture_exception(e, user_id="test_user", component="test")
    
    # Test message capture
    capture_message("Test message from Sentry setup", level="info")
    
    print("✅ Sentry test complete! Check your Sentry dashboard.")

