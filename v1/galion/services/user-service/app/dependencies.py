"""
Dependency injection for authentication and authorization.
Shared dependencies that can be used across different endpoints.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from app.config import settings
from app.database import get_db
from app.models.user import User


# Security scheme for JWT tokens
# This adds the lock icon in Swagger UI
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the currently authenticated user.
    
    Extracts JWT token from Authorization header, verifies it,
    and returns the user from database.
    
    Usage:
        @app.get("/profile")
        def get_profile(current_user: User = Depends(get_current_user)):
            return current_user
    
    Raises:
        HTTPException: If token is invalid or user not found
    """
    # Extract token from credentials
    token = credentials.credentials
    
    # Create exception for invalid authentication
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT token
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        # Extract user email from token payload
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # Fetch user from database
    user = db.query(User).filter(User.email == email).first()
    
    if user is None:
        raise credentials_exception
    
    # Check if user account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )
    
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to ensure user is active.
    Use this for endpoints that require an active user.
    
    This is an example of dependency chaining:
    1. get_current_user validates token and fetches user
    2. get_current_active_user checks if user is active
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to ensure user has admin role.
    Use this for admin-only endpoints.
    
    Example:
        @app.delete("/users/{user_id}")
        def delete_user(
            user_id: str,
            admin: User = Depends(get_current_admin_user)
        ):
            # Only admins can reach here
            pass
    """
    if current_user.role not in ["admin", "superadmin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

