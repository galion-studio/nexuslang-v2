"""
Admin API endpoints for user management, roles, and system administration
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import List, Optional
from datetime import datetime
import uuid

from ..core.database import get_db
from ..core.permissions import require_admin, PermissionChecker, assign_role, remove_role
from ..models.user import User
from ..models.rbac import Role, UserRole, BetaTesterProfile, UserFeedback, AuditLog

router = APIRouter()


# ============================================================
# REQUEST/RESPONSE MODELS
# ============================================================

class UserListItem(BaseModel):
    id: str
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login_at: Optional[datetime]
    roles: List[str]


class UserDetail(BaseModel):
    id: str
    email: str
    username: str
    full_name: Optional[str]
    avatar_url: Optional[str]
    bio: Optional[str]
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime]
    roles: List[str]
    permissions: List[str]


class AssignRoleRequest(BaseModel):
    user_id: str
    role_name: str


class UpdateUserRequest(BaseModel):
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None


class InviteBetaTesterRequest(BaseModel):
    user_id: str
    cohort: str


class SystemStats(BaseModel):
    total_users: int
    active_users: int
    beta_testers: int
    total_feedback: int
    critical_bugs: int


# ============================================================
# USER MANAGEMENT
# ============================================================

@router.get("/users", response_model=List[UserListItem])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    current_user: User = Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    """
    List all users with pagination and search.
    Requires admin role.
    """
    query = select(User).options(
        selectinload(User.user_roles).selectinload(UserRole.role)
    )
    
    # Add search filter
    if search:
        query = query.where(
            or_(
                User.email.ilike(f"%{search}%"),
                User.username.ilike(f"%{search}%"),
                User.full_name.ilike(f"%{search}%")
            )
        )
    
    # Add pagination
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    users = result.scalars().all()
    
    # Format response
    user_list = []
    for user in users:
        roles = await PermissionChecker.get_user_roles(user, db)
        user_list.append(UserListItem(
            id=str(user.id),
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at,
            last_login_at=user.last_login_at,
            roles=[role.name for role in roles]
        ))
    
    return user_list


@router.get("/users/{user_id}", response_model=UserDetail)
async def get_user(
    user_id: str,
    current_user: User = Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed information about a specific user.
    Requires admin role.
    """
    result = await db.execute(
        select(User).where(User.id == uuid.UUID(user_id))
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get roles and permissions
    roles = await PermissionChecker.get_user_roles(user, db)
    permissions = await PermissionChecker.get_user_permissions(user, db)
    
    return UserDetail(
        id=str(user.id),
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        avatar_url=user.avatar_url,
        bio=user.bio,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at,
        updated_at=user.updated_at,
        last_login_at=user.last_login_at,
        roles=[role.name for role in roles],
        permissions=permissions
    )


@router.patch("/users/{user_id}")
async def update_user(
    user_id: str,
    update_data: UpdateUserRequest,
    current_user: User = Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    """
    Update user properties (activate/deactivate, verify, etc.)
    Requires admin role.
    """
    result = await db.execute(
        select(User).where(User.id == uuid.UUID(user_id))
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update fields
    if update_data.is_active is not None:
        user.is_active = update_data.is_active
    
    if update_data.is_verified is not None:
        user.is_verified = update_data.is_verified
    
    await db.commit()
    await db.refresh(user)
    
    return {"message": "User updated successfully", "user_id": str(user.id)}


# ============================================================
# ROLE MANAGEMENT
# ============================================================

@router.post("/users/{user_id}/roles")
async def assign_user_role(
    user_id: str,
    request: AssignRoleRequest,
    current_user: User = Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    """
    Assign a role to a user.
    Requires admin role.
    """
    # Get target user
    result = await db.execute(
        select(User).where(User.id == uuid.UUID(user_id))
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    try:
        await assign_role(user, request.role_name, db, assigned_by=current_user)
        return {"message": f"Role '{request.role_name}' assigned to user"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/users/{user_id}/roles/{role_name}")
async def remove_user_role(
    user_id: str,
    role_name: str,
    current_user: User = Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    """
    Remove a role from a user.
    Requires admin role.
    """
    # Get target user
    result = await db.execute(
        select(User).where(User.id == uuid.UUID(user_id))
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    try:
        await remove_role(user, role_name, db)
        return {"message": f"Role '{role_name}' removed from user"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ============================================================
# BETA TESTER MANAGEMENT
# ============================================================

@router.post("/beta-testers/invite")
async def invite_beta_tester(
    request: InviteBetaTesterRequest,
    current_user: User = Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    """
    Invite a user to be a beta tester.
    Requires admin role.
    """
    # Get user
    result = await db.execute(
        select(User).where(User.id == uuid.UUID(request.user_id))
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if already a beta tester
    result = await db.execute(
        select(BetaTesterProfile).where(BetaTesterProfile.user_id == user.id)
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a beta tester"
        )
    
    # Create beta tester profile
    beta_profile = BetaTesterProfile(
        user_id=user.id,
        cohort=request.cohort,
        invited_by=current_user.id,
        invited_at=datetime.utcnow(),
        status='invited'
    )
    
    db.add(beta_profile)
    
    # Assign beta_tester role
    await assign_role(user, 'beta_tester', db, assigned_by=current_user)
    
    await db.commit()
    
    return {"message": "Beta tester invitation created", "profile_id": str(beta_profile.id)}


@router.get("/beta-testers")
async def list_beta_testers(
    cohort: Optional[str] = None,
    current_user: User = Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    """
    List all beta testers with optional cohort filter.
    Requires admin role.
    """
    query = select(BetaTesterProfile).options(
        selectinload(BetaTesterProfile.user)
    )
    
    if cohort:
        query = query.where(BetaTesterProfile.cohort == cohort)
    
    result = await db.execute(query)
    profiles = result.scalars().all()
    
    return [
        {
            "id": str(profile.id),
            "user_id": str(profile.user_id),
            "username": profile.user.username,
            "email": profile.user.email,
            "cohort": profile.cohort,
            "status": profile.status,
            "feedback_count": profile.feedback_count,
            "bugs_reported": profile.bugs_reported,
            "invited_at": profile.invited_at,
            "accepted_at": profile.accepted_at
        }
        for profile in profiles
    ]


# ============================================================
# SYSTEM STATISTICS
# ============================================================

@router.get("/stats", response_model=SystemStats)
async def get_system_stats(
    current_user: User = Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    """
    Get system-wide statistics.
    Requires admin role.
    """
    # Total users
    result = await db.execute(select(func.count(User.id)))
    total_users = result.scalar()
    
    # Active users (logged in last 30 days)
    from datetime import timedelta
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    result = await db.execute(
        select(func.count(User.id)).where(User.last_login_at >= thirty_days_ago)
    )
    active_users = result.scalar()
    
    # Beta testers
    result = await db.execute(
        select(func.count(BetaTesterProfile.id))
        .where(BetaTesterProfile.status == 'active')
    )
    beta_testers = result.scalar()
    
    # Total feedback
    result = await db.execute(select(func.count(UserFeedback.id)))
    total_feedback = result.scalar()
    
    # Critical bugs
    result = await db.execute(
        select(func.count(UserFeedback.id))
        .where(UserFeedback.feedback_type == 'bug')
        .where(UserFeedback.severity == 'critical')
        .where(UserFeedback.status != 'resolved')
    )
    critical_bugs = result.scalar()
    
    return SystemStats(
        total_users=total_users or 0,
        active_users=active_users or 0,
        beta_testers=beta_testers or 0,
        total_feedback=total_feedback or 0,
        critical_bugs=critical_bugs or 0
    )


# ============================================================
# FEEDBACK MANAGEMENT
# ============================================================

@router.get("/feedback")
async def list_feedback(
    feedback_type: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    """
    List all user feedback with filters.
    Requires admin role.
    """
    query = select(UserFeedback).options(
        selectinload(UserFeedback.user)
    )
    
    if feedback_type:
        query = query.where(UserFeedback.feedback_type == feedback_type)
    
    if status:
        query = query.where(UserFeedback.status == status)
    
    query = query.order_by(UserFeedback.created_at.desc())
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    feedback_items = result.scalars().all()
    
    return [
        {
            "id": str(item.id),
            "user": {
                "id": str(item.user.id),
                "username": item.user.username,
                "email": item.user.email
            },
            "feature_name": item.feature_name,
            "feedback_type": item.feedback_type,
            "title": item.title,
            "description": item.description,
            "severity": item.severity,
            "status": item.status,
            "created_at": item.created_at
        }
        for item in feedback_items
    ]


@router.patch("/feedback/{feedback_id}")
async def update_feedback(
    feedback_id: str,
    status: str,
    current_user: User = Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    """
    Update feedback status.
    Requires admin role.
    """
    result = await db.execute(
        select(UserFeedback).where(UserFeedback.id == uuid.UUID(feedback_id))
    )
    feedback = result.scalar_one_or_none()
    
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found"
        )
    
    feedback.status = status
    
    if status == 'resolved':
        feedback.resolved_at = datetime.utcnow()
    
    await db.commit()
    
    return {"message": "Feedback updated", "feedback_id": str(feedback.id)}

