"""
Email Verification API

Flow:
1. User registers → unverified account
2. Verification email sent with token
3. User clicks link with token
4. Account verified → full access granted
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
import secrets

from ..core.database import get_db
from ..core.redis_client import get_redis
from ..models.user import User
from ..api.auth import get_current_user

router = APIRouter()


# ==================== MODELS ====================

class VerificationResponse(BaseModel):
    """Response for verification request."""
    message: str
    token: str = None  # For development only


# ==================== ENDPOINTS ====================

@router.post("/send")
async def send_verification_email(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Send verification email to current user.
    
    Can be called:
    - Automatically on registration
    - Manually if user requests resend
    """
    # Check if already verified
    if current_user.is_verified:
        return {
            "message": "Email already verified"
        }
    
    # Generate secure verification token
    verification_token = secrets.token_urlsafe(32)
    
    # Store token in Redis with 24-hour expiry
    redis = await get_redis()
    await redis.set_cache(
        f"email_verification:{verification_token}",
        {
            "user_id": str(current_user.id),
            "email": current_user.email,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        ttl_seconds=86400  # 24 hours
    )
    
    # In production: Send email with verification link
    # verification_link = f"https://your-domain.com/verify-email?token={verification_token}"
    # await send_verification_email(current_user.email, verification_link)
    
    # For development: Return token in response
    if __debug__:
        return VerificationResponse(
            message="Verification email sent (dev mode)",
            token=verification_token
        )
    
    return VerificationResponse(
        message="Verification email sent. Please check your inbox."
    )


@router.post("/verify")
async def verify_email(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Verify email with token from email link.
    
    Security:
    - One-time use token
    - Expires after 24 hours
    - Updates user verification status
    """
    # Get and validate token from Redis
    redis = await get_redis()
    verification_data = await redis.get_cache(f"email_verification:{token}")
    
    if not verification_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    # Get user
    user_id = verification_data["user_id"]
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found"
        )
    
    # Mark as verified
    user.is_verified = True
    user.updated_at = datetime.now(timezone.utc)
    await db.commit()
    
    # Delete the verification token (one-time use)
    await redis.delete_cache(f"email_verification:{token}")
    
    return {
        "message": "Email verified successfully! You now have full access."
    }


@router.get("/status")
async def get_verification_status(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's email verification status.
    """
    return {
        "is_verified": current_user.is_verified,
        "email": current_user.email,
        "message": "Email verified" if current_user.is_verified else "Email not verified"
    }

