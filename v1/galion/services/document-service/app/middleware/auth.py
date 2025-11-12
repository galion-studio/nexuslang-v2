"""
Authentication middleware - extracts user info from JWT token
"""

from fastapi import Header, HTTPException, Depends
from typing import Optional
from uuid import UUID

async def get_current_user(
    x_user_email: Optional[str] = Header(None),
    x_user_id: Optional[str] = Header(None)
) -> dict:
    """
    Get current user from headers (set by API Gateway)
    
    The API Gateway validates the JWT and passes user info via headers.
    """
    if not x_user_email or not x_user_id:
        raise HTTPException(
            status_code=401,
            detail="Authentication required"
        )
    
    try:
        user_id = UUID(x_user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid user ID")
    
    return {
        "user_id": user_id,
        "email": x_user_email
    }

async def get_current_admin_user(
    current_user: dict = Depends(get_current_user),
    x_user_role: Optional[str] = Header(None)
) -> dict:
    """
    Verify that current user is an admin
    """
    if x_user_role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    
    return current_user

