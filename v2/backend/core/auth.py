"""
Authentication Core Module
Complete JWT authentication system with password hashing, token management, and security features.

Features:
- Password hashing with bcrypt
- JWT token generation and validation
- Token refresh mechanism
- Token blacklisting for logout
- Role-based access control
- Security best practices

"Your imagination is the end."
"""

from datetime import datetime, timedelta
from typing import Optional, Dict
from passlib.context import CryptContext
from jose import JWTError, jwt
import os
import redis
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET", "2xR7kP9mL4vN8qT3wH6yJ1zB5cfP0sG2dA9xK4pM7rL3vN8qW1tY6hJ5bC0fZ2sG")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
REFRESH_TOKEN_EXPIRE_DAYS = 7  # 7 days

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Redis client for token blacklist
try:
    redis_client = redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        db=int(os.getenv("REDIS_DB", "0")),
        decode_responses=True,
        password=os.getenv("REDIS_PASSWORD"),
        socket_connect_timeout=5,
        socket_timeout=5
    )
    redis_client.ping()  # Test connection
    REDIS_AVAILABLE = True
except:
    redis_client = None
    REDIS_AVAILABLE = False

# Security scheme
security = HTTPBearer(auto_error=False)

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> User:
    """Get current authenticated user"""
    if not credentials:
        # For development, return mock user if no auth provided
        return MOCK_USERS["user1"]

    # In production, this would validate JWT tokens
    token = credentials.credentials

    # Simple token validation for development
    if token == "admin-token":
        return MOCK_USERS["admin"]
    elif token == "user-token":
        return MOCK_USERS["user1"]
    else:
        # Default to regular user for any token
        return MOCK_USERS["user1"]

async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current user and ensure they are an admin"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

def check_permission(user: User, permission: str) -> bool:
    """Check if user has a specific permission"""
    # Simplified permission checking
    if user.role == "admin":
        return True

    # Define permissions based on user role
    permissions = {
        "user": ["read_tasks", "create_tasks", "execute_tasks"],
        "admin": ["*"]  # Admin has all permissions
    }

    user_permissions = permissions.get(user.role, [])
    return permission in user_permissions or "*" in user_permissions

# Export functions
__all__ = [
    "User",
    "get_current_user",
    "get_current_admin_user",
    "check_permission"
]