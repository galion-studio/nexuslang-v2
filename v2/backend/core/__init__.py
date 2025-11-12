"""
Core module initialization.
Exports security, database, and middleware components.
"""

from .config import settings
from .security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    blacklist_token,
    validate_password_strength,
    validate_username
)
from .database import get_db, init_db, close_db
from .redis_client import get_redis, close_redis
from .security_middleware import (
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
    AuditLoggingMiddleware,
    RequestValidationMiddleware,
    get_audit_logger
)

__all__ = [
    # Config
    "settings",
    
    # Security
    "hash_password",
    "verify_password",
    "create_access_token",
    "decode_access_token",
    "blacklist_token",
    "validate_password_strength",
    "validate_username",
    
    # Database
    "get_db",
    "init_db",
    "close_db",
    
    # Redis
    "get_redis",
    "close_redis",
    
    # Middleware
    "RateLimitMiddleware",
    "SecurityHeadersMiddleware",
    "AuditLoggingMiddleware",
    "RequestValidationMiddleware",
    "get_audit_logger"
]
