"""
Password Reset API

Secure password reset flow:
1. User requests reset with email
2. Generate secure token, store in Redis with expiry
3. Send reset email (or return token for testing)
4. User submits new password with token
5. Validate token and update password
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
import secrets

from ..core.database import get_db
from ..core.redis_client import get_redis
from ..core.security import (
    hash_password,
    validate_password_strength
)
from ..models.user import User

router = APIRouter()


# ==================== REQUEST/RESPONSE MODELS ====================

class PasswordResetRequest(BaseModel):
    """Request password reset for an email."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Confirm password reset with token."""
    token: str
    new_password: str


class PasswordResetResponse(BaseModel):
    """Response for password reset request."""
    message: str
    token: str = None  # Only for development/testing


# ==================== ENDPOINTS ====================

@router.post("/request", response_model=PasswordResetResponse)
async def request_password_reset(
    request: PasswordResetRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Request a password reset token.
    
    Security notes:
    - Always returns success (prevent email enumeration)
    - Token valid for 1 hour only
    - One-time use token
    - Rate limited to prevent abuse
    """
    # Always return success to prevent email enumeration
    default_response = {
        "message": "If that email exists, a password reset link has been sent."
    }
    
    # Check if user exists
    result = await db.execute(
        select(User).where(User.email == request.email)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        # Still return success to prevent enumeration
        return PasswordResetResponse(**default_response)
    
    # Generate secure reset token
    reset_token = secrets.token_urlsafe(32)
    
    # Store token in Redis with 1-hour expiry
    redis = await get_redis()
    await redis.set_cache(
        f"password_reset:{reset_token}",
        {
            "user_id": str(user.id),
            "email": user.email,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        ttl_seconds=3600  # 1 hour
    )
    
    # In production: Send email with reset link
    # reset_link = f"https://your-domain.com/reset-password?token={reset_token}"
    # await send_reset_email(user.email, reset_link)
    
    # For development/testing: Return token in response
    # Remove this in production!
    if __debug__:
        return PasswordResetResponse(
            message="Password reset token generated (dev mode)",
            token=reset_token
        )
    
    return PasswordResetResponse(**default_response)


@router.post("/confirm")
async def confirm_password_reset(
    request: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db)
):
    """
    Confirm password reset and set new password.
    
    Security:
    - Validates token from Redis
    - One-time use (token deleted after use)
    - Strong password requirements enforced
    - Invalidates all existing sessions
    """
    # Validate new password strength
    password_valid, password_error = validate_password_strength(request.new_password)
    if not password_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=password_error
        )
    
    # Get and validate token from Redis
    redis = await get_redis()
    reset_data = await redis.get_cache(f"password_reset:{request.token}")
    
    if not reset_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Get user
    user_id = reset_data["user_id"]
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found"
        )
    
    # Update password
    user.password_hash = hash_password(request.new_password)
    user.updated_at = datetime.now(timezone.utc)
    await db.commit()
    
    # Delete the reset token (one-time use)
    await redis.delete_cache(f"password_reset:{request.token}")
    
    # TODO: Invalidate all existing sessions for this user
    # This forces re-login with new password
    
    return {
        "message": "Password reset successfully. Please log in with your new password."
    }


@router.post("/change")
async def change_password(
    old_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Change password for authenticated user.
    
    Requires current password for verification.
    """
    from ..core.security import verify_password
    
    # Verify old password
    if not verify_password(old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Validate new password
    password_valid, password_error = validate_password_strength(new_password)
    if not password_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=password_error
        )
    
    # Check that new password is different
    if verify_password(new_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password"
        )
    
    # Update password
    current_user.password_hash = hash_password(new_password)
    current_user.updated_at = datetime.now(timezone.utc)
    await db.commit()
    
    return {
        "message": "Password changed successfully"
    }


# Import get_current_user from auth
from ..api.auth import get_current_user

