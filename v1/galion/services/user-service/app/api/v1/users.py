"""
User management API endpoints.
Handles user profile operations, search, and admin functions.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import uuid

from app.database import get_db
from app.dependencies import get_current_user, get_current_admin_user
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate, UserSearch, UserListResponse
from app.services.user import UserService
from app.events import (
    publish_profile_updated, publish_profile_viewed, 
    publish_user_search, publish_user_deactivated, publish_user_activated
)


# Create API router
router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """
    Get current user's profile.
    
    Returns the authenticated user's complete profile information.
    Requires valid JWT token in Authorization header.
    """
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_my_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's profile.
    
    Allows users to update their own profile information:
    - Name
    - Bio
    - Avatar URL
    
    Only provided fields will be updated.
    """
    # Get fields that were actually updated
    fields_updated = [
        field for field, value in update_data.model_dump(exclude_unset=True).items()
    ]
    
    updated_user = UserService.update_user(db, current_user, update_data)
    
    # Publish profile update event
    if fields_updated:
        publish_profile_updated(str(current_user.id), fields_updated)
    
    return updated_user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user by ID.
    
    Retrieve public profile information for any user by their ID.
    Requires authentication but not admin privileges.
    """
    user = UserService.get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Publish profile view event
    publish_profile_viewed(str(current_user.id), str(user_id))
    
    return user


@router.post("/search", response_model=UserListResponse)
async def search_users(
    search: UserSearch,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Search for users.
    
    Search by:
    - Text query (searches name and email)
    - Role filter
    - Active status filter
    
    Supports pagination with limit and offset.
    """
    users, total = UserService.search_users(db, search)
    
    # Publish search event for analytics
    publish_user_search(
        user_id=str(current_user.id),
        query=search.query or "",
        results_count=total
    )
    
    return {
        "users": users,
        "total": total,
        "limit": search.limit,
        "offset": search.offset
    }


@router.get("/", response_model=UserListResponse)
async def list_users(
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of all users.
    
    Returns users ordered by creation date (newest first).
    Supports pagination.
    """
    users, total = UserService.get_users_list(db, limit, offset)
    
    return {
        "users": users,
        "total": total,
        "limit": limit,
        "offset": offset
    }


# Admin-only endpoints


@router.put("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(
    user_id: uuid.UUID,
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Deactivate a user account (Admin only).
    
    Deactivated users cannot log in or access the system.
    This is a soft delete - data is preserved.
    """
    user = UserService.get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Prevent admins from deactivating themselves
    if user.id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )
    
    updated_user = UserService.deactivate_user(db, user)
    
    # Publish deactivation event
    publish_user_deactivated(str(admin.id), str(user_id))
    
    return updated_user


@router.put("/{user_id}/activate", response_model=UserResponse)
async def activate_user(
    user_id: uuid.UUID,
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Activate a user account (Admin only).
    
    Reactivates a previously deactivated account.
    """
    user = UserService.get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    updated_user = UserService.activate_user(db, user)
    
    # Publish activation event
    publish_user_activated(str(admin.id), str(user_id))
    
    return updated_user

