"""
Feature Flags API for controlling feature rollout
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime
import uuid

from ..core.database import get_db
from ..core.permissions import require_admin, FeatureFlagChecker
from ..models.user import User
from ..models.rbac import FeatureFlag
from ..api.auth import get_current_user

router = APIRouter()


# ============================================================
# REQUEST/RESPONSE MODELS
# ============================================================

class FeatureFlagCreate(BaseModel):
    name: str
    display_name: str
    description: Optional[str] = None
    enabled: bool = False
    rollout_percentage: int = 0
    target_roles: List[str] = []
    target_users: List[str] = []
    target_cohorts: List[str] = []


class FeatureFlagUpdate(BaseModel):
    display_name: Optional[str] = None
    description: Optional[str] = None
    enabled: Optional[bool] = None
    rollout_percentage: Optional[int] = None
    target_roles: Optional[List[str]] = None
    target_users: Optional[List[str]] = None
    target_cohorts: Optional[List[str]] = None


class FeatureFlagResponse(BaseModel):
    id: str
    name: str
    display_name: str
    description: Optional[str]
    enabled: bool
    rollout_percentage: int
    target_roles: List[str]
    target_users: List[str]
    target_cohorts: List[str]
    created_at: datetime
    updated_at: datetime


# ============================================================
# ADMIN ENDPOINTS
# ============================================================

@router.get("", response_model=List[FeatureFlagResponse])
async def list_feature_flags(
    current_user: User = Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    """
    List all feature flags.
    Requires admin role.
    """
    result = await db.execute(select(FeatureFlag).order_by(FeatureFlag.name))
    flags = result.scalars().all()
    
    return [
        FeatureFlagResponse(
            id=str(flag.id),
            name=flag.name,
            display_name=flag.display_name,
            description=flag.description,
            enabled=flag.enabled,
            rollout_percentage=flag.rollout_percentage,
            target_roles=flag.target_roles or [],
            target_users=flag.target_users or [],
            target_cohorts=flag.target_cohorts or [],
            created_at=flag.created_at,
            updated_at=flag.updated_at
        )
        for flag in flags
    ]


@router.post("", response_model=FeatureFlagResponse)
async def create_feature_flag(
    flag_data: FeatureFlagCreate,
    current_user: User = Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new feature flag.
    Requires admin role.
    """
    # Check if flag already exists
    result = await db.execute(
        select(FeatureFlag).where(FeatureFlag.name == flag_data.name)
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Feature flag '{flag_data.name}' already exists"
        )
    
    # Create feature flag
    flag = FeatureFlag(
        name=flag_data.name,
        display_name=flag_data.display_name,
        description=flag_data.description,
        enabled=flag_data.enabled,
        rollout_percentage=flag_data.rollout_percentage,
        target_roles=flag_data.target_roles,
        target_users=flag_data.target_users,
        target_cohorts=flag_data.target_cohorts
    )
    
    db.add(flag)
    await db.commit()
    await db.refresh(flag)
    
    return FeatureFlagResponse(
        id=str(flag.id),
        name=flag.name,
        display_name=flag.display_name,
        description=flag.description,
        enabled=flag.enabled,
        rollout_percentage=flag.rollout_percentage,
        target_roles=flag.target_roles or [],
        target_users=flag.target_users or [],
        target_cohorts=flag.target_cohorts or [],
        created_at=flag.created_at,
        updated_at=flag.updated_at
    )


@router.get("/{flag_name}", response_model=FeatureFlagResponse)
async def get_feature_flag(
    flag_name: str,
    current_user: User = Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific feature flag.
    Requires admin role.
    """
    result = await db.execute(
        select(FeatureFlag).where(FeatureFlag.name == flag_name)
    )
    flag = result.scalar_one_or_none()
    
    if not flag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feature flag '{flag_name}' not found"
        )
    
    return FeatureFlagResponse(
        id=str(flag.id),
        name=flag.name,
        display_name=flag.display_name,
        description=flag.description,
        enabled=flag.enabled,
        rollout_percentage=flag.rollout_percentage,
        target_roles=flag.target_roles or [],
        target_users=flag.target_users or [],
        target_cohorts=flag.target_cohorts or [],
        created_at=flag.created_at,
        updated_at=flag.updated_at
    )


@router.patch("/{flag_name}", response_model=FeatureFlagResponse)
async def update_feature_flag(
    flag_name: str,
    update_data: FeatureFlagUpdate,
    current_user: User = Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a feature flag.
    Requires admin role.
    """
    result = await db.execute(
        select(FeatureFlag).where(FeatureFlag.name == flag_name)
    )
    flag = result.scalar_one_or_none()
    
    if not flag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feature flag '{flag_name}' not found"
        )
    
    # Update fields
    if update_data.display_name is not None:
        flag.display_name = update_data.display_name
    
    if update_data.description is not None:
        flag.description = update_data.description
    
    if update_data.enabled is not None:
        flag.enabled = update_data.enabled
    
    if update_data.rollout_percentage is not None:
        flag.rollout_percentage = max(0, min(100, update_data.rollout_percentage))
    
    if update_data.target_roles is not None:
        flag.target_roles = update_data.target_roles
    
    if update_data.target_users is not None:
        flag.target_users = update_data.target_users
    
    if update_data.target_cohorts is not None:
        flag.target_cohorts = update_data.target_cohorts
    
    await db.commit()
    await db.refresh(flag)
    
    return FeatureFlagResponse(
        id=str(flag.id),
        name=flag.name,
        display_name=flag.display_name,
        description=flag.description,
        enabled=flag.enabled,
        rollout_percentage=flag.rollout_percentage,
        target_roles=flag.target_roles or [],
        target_users=flag.target_users or [],
        target_cohorts=flag.target_cohorts or [],
        created_at=flag.created_at,
        updated_at=flag.updated_at
    )


@router.delete("/{flag_name}")
async def delete_feature_flag(
    flag_name: str,
    current_user: User = Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a feature flag.
    Requires admin role.
    """
    result = await db.execute(
        select(FeatureFlag).where(FeatureFlag.name == flag_name)
    )
    flag = result.scalar_one_or_none()
    
    if not flag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feature flag '{flag_name}' not found"
        )
    
    await db.delete(flag)
    await db.commit()
    
    return {"message": f"Feature flag '{flag_name}' deleted"}


# ============================================================
# USER ENDPOINTS (Check feature availability)
# ============================================================

@router.get("/check/{flag_name}")
async def check_feature_flag(
    flag_name: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Check if a feature flag is enabled for the current user.
    Available to all authenticated users.
    """
    is_enabled = await FeatureFlagChecker.is_feature_enabled(
        flag_name, current_user, db
    )
    
    return {
        "feature": flag_name,
        "enabled": is_enabled
    }


@router.get("/check-multiple")
async def check_multiple_feature_flags(
    flags: str,  # Comma-separated list
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Check multiple feature flags at once.
    Available to all authenticated users.
    
    Query param: flags=voice_cloning,advanced_ide,beta_features
    """
    flag_names = [f.strip() for f in flags.split(',')]
    
    results = {}
    for flag_name in flag_names:
        is_enabled = await FeatureFlagChecker.is_feature_enabled(
            flag_name, current_user, db
        )
        results[flag_name] = is_enabled
    
    return results

