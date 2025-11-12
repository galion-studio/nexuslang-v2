"""
Authentication API routes.
Handles user registration, login, logout, and token management.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from typing import Optional
import uuid

from ..core.database import get_db
from ..core.security import (
    hash_password, verify_password, create_access_token, 
    decode_access_token, validate_password_strength, validate_username,
    blacklist_token
)
from ..models.user import User, Session as UserSession

router = APIRouter()
security = HTTPBearer()


# Request/Response Models
class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    username: str


class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    full_name: Optional[str]
    avatar_url: Optional[str]
    bio: Optional[str]
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Dependency to get current user from token
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Dependency to extract and validate current user from JWT token.
    
    Usage in endpoints:
        async def endpoint(current_user: User = Depends(get_current_user)):
            ...
    """
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Fetch user from database
    result = await db.execute(
        select(User).where(User.id == uuid.UUID(user_id))
    )
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    return user


# Optional user dependency (doesn't require auth)
async def get_optional_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Dependency to optionally extract user from JWT token.
    Returns None if no token provided or invalid.
    
    Usage in endpoints that work both authenticated and unauthenticated:
        async def endpoint(current_user: Optional[User] = Depends(get_optional_user)):
            if current_user:
                # User is authenticated
            else:
                # Anonymous user
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    token = authorization.replace("Bearer ", "")
    payload = decode_access_token(token)
    
    if not payload:
        return None
    
    user_id = payload.get("sub")
    if not user_id:
        return None
    
    # Fetch user from database
    result = await db.execute(
        select(User).where(User.id == uuid.UUID(user_id))
    )
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        return None
    
    return user


@router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """
    Register a new user account.
    
    - Validates email, username, and password
    - Creates user in database
    - Returns JWT access token
    """
    # Validate username
    username_valid, username_error = validate_username(request.username)
    if not username_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=username_error
        )
    
    # Validate password strength
    password_valid, password_error = validate_password_strength(request.password)
    if not password_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=password_error
        )
    
    # Check if email or username already exists
    # Use generic error message to prevent username enumeration
    result = await db.execute(
        select(User).where(User.email == request.email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed. Email or username may already be in use."
        )
    
    # Check if username already exists
    result = await db.execute(
        select(User).where(User.username == request.username)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed. Email or username may already be in use."
        )
    
    # Create new user
    user = User(
        email=request.email,
        username=request.username,
        password_hash=hash_password(request.password),
        full_name=request.full_name,
        is_verified=False,  # Could add email verification later
        is_active=True
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Generate access token
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )
    
    return TokenResponse(
        access_token=access_token,
        user_id=str(user.id),
        email=user.email,
        username=user.username
    )


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Login with email and password.
    
    Security features:
    - Account lockout after 5 failed attempts
    - Failed attempts tracked for 30 minutes
    - Clears failed attempts on successful login
    """
    from ..core.redis_client import get_redis
    
    # Check if account is locked
    redis = await get_redis()
    is_locked, remaining_attempts = await redis.is_account_locked(request.email)
    
    if is_locked:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Account temporarily locked due to too many failed login attempts. Please try again in 30 minutes or reset your password."
        )
    
    # Find user by email
    result = await db.execute(
        select(User).where(User.email == request.email)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        # Record failed attempt
        await redis.record_failed_login(request.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verify password
    if not verify_password(request.password, user.password_hash):
        # Record failed attempt
        failed_count = await redis.record_failed_login(request.email)
        remaining = max(0, 5 - failed_count)
        
        detail = "Incorrect email or password"
        if remaining <= 2 and remaining > 0:
            detail += f". {remaining} attempts remaining before account lockout."
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Clear failed login attempts on successful login
    await redis.clear_failed_logins(request.email)
    
    # Update last login using timezone-aware datetime
    from datetime import timezone
    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()
    
    # Generate access token
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )
    
    return TokenResponse(
        access_token=access_token,
        user_id=str(user.id),
        email=user.email,
        username=user.username
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user information.
    
    Requires valid JWT token in Authorization header.
    """
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        avatar_url=current_user.avatar_url,
        bio=current_user.bio,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at
    )


@router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Logout current user by blacklisting their token.
    
    This ensures the token cannot be used even if stolen after logout.
    Client should also discard the token immediately.
    """
    token = credentials.credentials
    
    # Add token to blacklist so it can't be reused
    blacklist_token(token)
    
    return {"message": "Logged out successfully. Token has been invalidated."}


@router.post("/verify-token")
async def verify_token(current_user: User = Depends(get_current_user)):
    """
    Verify if a token is valid.
    
    Returns user info if token is valid, otherwise returns 401.
    """
    return {
        "valid": True,
        "user_id": str(current_user.id),
        "email": current_user.email,
        "username": current_user.username
    }

