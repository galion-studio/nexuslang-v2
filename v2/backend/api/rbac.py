"""
RBAC (Role-Based Access Control) API
Admin endpoints for managing roles, permissions, and user access
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID

from ..services.auth.rbac_service import get_rbac_service, RBACService
from ..api.auth import get_current_user
from ..models.user import User
from ..models.rbac import Role, Permission, UserRole, FeatureFlag
from ..core.database import get_db
from ..core.errors import AuthorizationError, ResourceNotFoundError

router = APIRouter(prefix="/rbac", tags=["RBAC"])


# Request/Response Models
class RoleCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    display_name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    permissions: List[str] = Field(default_factory=list)


class RoleUpdate(BaseModel):
    display_name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    permissions: Optional[List[str]] = None


class PermissionCreate(BaseModel):
    resource: str = Field(..., min_length=1, max_length=100)
    action: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None


class UserRoleAssignment(BaseModel):
    user_id: str
    role_name: str
    expires_at: Optional[datetime] = None


class FeatureFlagCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    display_name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    enabled: bool = False
    rollout_percentage: int = Field(0, ge=0, le=100)


class FeatureFlagUpdate(BaseModel):
    display_name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    enabled: Optional[bool] = None
    rollout_percentage: Optional[int] = Field(None, ge=0, le=100)


# Dependencies
async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require admin access"""
    rbac_service = get_rbac_service()

    async for db in get_db():
        is_admin = await rbac_service.check_admin_access(str(current_user.id), db)
        if not is_admin:
            raise AuthorizationError("Admin access required")

    return current_user


# Role Management Endpoints
@router.post("/roles", response_model=Dict[str, Any])
async def create_role(
    role_data: RoleCreate,
    current_user: User = Depends(require_admin),
    rbac_service: RBACService = Depends(get_rbac_service),
    db: AsyncSession = Depends(get_db)
):
    """Create a new role"""
    try:
        # Check if role already exists
        from sqlalchemy import select
        stmt = select(Role).where(Role.name == role_data.name)
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            raise HTTPException(status_code=400, detail="Role already exists")

        # Create new role
        new_role = Role(
            name=role_data.name,
            display_name=role_data.display_name,
            description=role_data.description,
            permissions=role_data.permissions
        )

        db.add(new_role)
        await db.commit()
        await db.refresh(new_role)

        return {
            "id": str(new_role.id),
            "name": new_role.name,
            "display_name": new_role.display_name,
            "description": new_role.description,
            "permissions": new_role.permissions,
            "created_at": new_role.created_at.isoformat()
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create role: {str(e)}")


@router.get("/roles", response_model=List[Dict[str, Any]])
async def list_roles(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """List all roles"""
    try:
        from sqlalchemy import select
        stmt = select(Role).order_by(Role.name)
        result = await db.execute(stmt)
        roles = result.scalars().all()

        return [
            {
                "id": str(role.id),
                "name": role.name,
                "display_name": role.display_name,
                "description": role.description,
                "permissions": role.permissions,
                "is_system": role.is_system,
                "created_at": role.created_at.isoformat(),
                "updated_at": role.updated_at.isoformat() if role.updated_at else None
            }
            for role in roles
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list roles: {str(e)}")


@router.get("/roles/{role_id}", response_model=Dict[str, Any])
async def get_role(
    role_id: str,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific role"""
    try:
        from sqlalchemy import select
        stmt = select(Role).where(Role.id == UUID(role_id))
        result = await db.execute(stmt)
        role = result.scalar_one_or_none()

        if not role:
            raise HTTPException(status_code=404, detail="Role not found")

        return {
            "id": str(role.id),
            "name": role.name,
            "display_name": role.display_name,
            "description": role.description,
            "permissions": role.permissions,
            "is_system": role.is_system,
            "created_at": role.created_at.isoformat(),
            "updated_at": role.updated_at.isoformat() if role.updated_at else None
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get role: {str(e)}")


@router.put("/roles/{role_id}", response_model=Dict[str, Any])
async def update_role(
    role_id: str,
    role_data: RoleUpdate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Update a role"""
    try:
        from sqlalchemy import select
        stmt = select(Role).where(Role.id == UUID(role_id))
        result = await db.execute(stmt)
        role = result.scalar_one_or_none()

        if not role:
            raise HTTPException(status_code=404, detail="Role not found")

        if role.is_system:
            raise HTTPException(status_code=400, detail="Cannot modify system roles")

        # Update fields
        if role_data.display_name is not None:
            role.display_name = role_data.display_name
        if role_data.description is not None:
            role.description = role_data.description
        if role_data.permissions is not None:
            role.permissions = role_data.permissions

        await db.commit()
        await db.refresh(role)

        return {
            "id": str(role.id),
            "name": role.name,
            "display_name": role.display_name,
            "description": role.description,
            "permissions": role.permissions,
            "updated_at": role.updated_at.isoformat() if role.updated_at else None
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update role: {str(e)}")


@router.delete("/roles/{role_id}")
async def delete_role(
    role_id: str,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Delete a role"""
    try:
        from sqlalchemy import select
        stmt = select(Role).where(Role.id == UUID(role_id))
        result = await db.execute(stmt)
        role = result.scalar_one_or_none()

        if not role:
            raise HTTPException(status_code=404, detail="Role not found")

        if role.is_system:
            raise HTTPException(status_code=400, detail="Cannot delete system roles")

        await db.delete(role)
        await db.commit()

        return {"message": "Role deleted successfully"}

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete role: {str(e)}")


# User Role Management
@router.post("/users/{user_id}/roles")
async def assign_user_role(
    user_id: str,
    assignment: UserRoleAssignment,
    current_user: User = Depends(require_admin),
    rbac_service: RBACService = Depends(get_rbac_service),
    db: AsyncSession = Depends(get_db)
):
    """Assign a role to a user"""
    try:
        success = await rbac_service.assign_role(
            assignment.user_id,
            assignment.role_name,
            str(current_user.id),
            db,
            assignment.expires_at
        )

        if not success:
            raise HTTPException(status_code=400, detail="Failed to assign role")

        return {"message": f"Role '{assignment.role_name}' assigned to user successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to assign role: {str(e)}")


@router.delete("/users/{user_id}/roles/{role_name}")
async def revoke_user_role(
    user_id: str,
    role_name: str,
    current_user: User = Depends(require_admin),
    rbac_service: RBACService = Depends(get_rbac_service),
    db: AsyncSession = Depends(get_db)
):
    """Revoke a role from a user"""
    try:
        success = await rbac_service.revoke_role(user_id, role_name, db)

        if not success:
            raise HTTPException(status_code=404, detail="Role assignment not found")

        return {"message": f"Role '{role_name}' revoked from user successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to revoke role: {str(e)}")


@router.get("/users/{user_id}/roles", response_model=List[Dict[str, Any]])
async def get_user_roles(
    user_id: str,
    current_user: User = Depends(require_admin),
    rbac_service: RBACService = Depends(get_rbac_service),
    db: AsyncSession = Depends(get_db)
):
    """Get all roles for a user"""
    try:
        roles = await rbac_service.get_user_roles(user_id, db)

        return [
            {
                "id": str(role.id),
                "name": role.name,
                "display_name": role.display_name,
                "description": role.description,
                "permissions": role.permissions,
                "assigned_at": role.user_roles[0].assigned_at.isoformat() if role.user_roles else None,
                "expires_at": role.user_roles[0].expires_at.isoformat() if role.user_roles and role.user_roles[0].expires_at else None
            }
            for role in roles
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user roles: {str(e)}")


@router.get("/users/{user_id}/permissions", response_model=List[str])
async def get_user_permissions(
    user_id: str,
    current_user: User = Depends(require_admin),
    rbac_service: RBACService = Depends(get_rbac_service),
    db: AsyncSession = Depends(get_db)
):
    """Get all permissions for a user"""
    try:
        permissions = await rbac_service.get_user_permissions(user_id, db)
        return list(permissions)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user permissions: {str(e)}")


# Permission Management
@router.post("/permissions", response_model=Dict[str, Any])
async def create_permission(
    permission_data: PermissionCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Create a new permission"""
    try:
        from sqlalchemy import select
        # Check if permission already exists
        stmt = select(Permission).where(
            Permission.resource == permission_data.resource,
            Permission.action == permission_data.action
        )
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            raise HTTPException(status_code=400, detail="Permission already exists")

        new_permission = Permission(
            resource=permission_data.resource,
            action=permission_data.action,
            description=permission_data.description
        )

        db.add(new_permission)
        await db.commit()
        await db.refresh(new_permission)

        return {
            "id": str(new_permission.id),
            "resource": new_permission.resource,
            "action": new_permission.action,
            "description": new_permission.description,
            "created_at": new_permission.created_at.isoformat()
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create permission: {str(e)}")


@router.get("/permissions", response_model=List[Dict[str, Any]])
async def list_permissions(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """List all permissions"""
    try:
        from sqlalchemy import select
        stmt = select(Permission).order_by(Permission.resource, Permission.action)
        result = await db.execute(stmt)
        permissions = result.scalars().all()

        return [
            {
                "id": str(perm.id),
                "resource": perm.resource,
                "action": perm.action,
                "description": perm.description,
                "created_at": perm.created_at.isoformat()
            }
            for perm in permissions
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list permissions: {str(e)}")


# Feature Flag Management
@router.post("/feature-flags", response_model=Dict[str, Any])
async def create_feature_flag(
    flag_data: FeatureFlagCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Create a new feature flag"""
    try:
        from sqlalchemy import select
        # Check if flag already exists
        stmt = select(FeatureFlag).where(FeatureFlag.name == flag_data.name)
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            raise HTTPException(status_code=400, detail="Feature flag already exists")

        new_flag = FeatureFlag(
            name=flag_data.name,
            display_name=flag_data.display_name,
            description=flag_data.description,
            enabled=flag_data.enabled,
            rollout_percentage=flag_data.rollout_percentage
        )

        db.add(new_flag)
        await db.commit()
        await db.refresh(new_flag)

        return {
            "id": str(new_flag.id),
            "name": new_flag.name,
            "display_name": new_flag.display_name,
            "description": new_flag.description,
            "enabled": new_flag.enabled,
            "rollout_percentage": new_flag.rollout_percentage,
            "created_at": new_flag.created_at.isoformat()
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create feature flag: {str(e)}")


@router.get("/feature-flags", response_model=List[Dict[str, Any]])
async def list_feature_flags(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """List all feature flags"""
    try:
        from sqlalchemy import select
        stmt = select(FeatureFlag).order_by(FeatureFlag.name)
        result = await db.execute(stmt)
        flags = result.scalars().all()

        return [
            {
                "id": str(flag.id),
                "name": flag.name,
                "display_name": flag.display_name,
                "description": flag.description,
                "enabled": flag.enabled,
                "rollout_percentage": flag.rollout_percentage,
                "created_at": flag.created_at.isoformat(),
                "updated_at": flag.updated_at.isoformat() if flag.updated_at else None
            }
            for flag in flags
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list feature flags: {str(e)}")


@router.put("/feature-flags/{flag_id}", response_model=Dict[str, Any])
async def update_feature_flag(
    flag_id: str,
    flag_data: FeatureFlagUpdate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Update a feature flag"""
    try:
        from sqlalchemy import select
        stmt = select(FeatureFlag).where(FeatureFlag.id == UUID(flag_id))
        result = await db.execute(stmt)
        flag = result.scalar_one_or_none()

        if not flag:
            raise HTTPException(status_code=404, detail="Feature flag not found")

        # Update fields
        if flag_data.display_name is not None:
            flag.display_name = flag_data.display_name
        if flag_data.description is not None:
            flag.description = flag_data.description
        if flag_data.enabled is not None:
            flag.enabled = flag_data.enabled
        if flag_data.rollout_percentage is not None:
            flag.rollout_percentage = flag_data.rollout_percentage

        await db.commit()
        await db.refresh(flag)

        return {
            "id": str(flag.id),
            "name": flag.name,
            "display_name": flag.display_name,
            "description": flag.description,
            "enabled": flag.enabled,
            "rollout_percentage": flag.rollout_percentage,
            "updated_at": flag.updated_at.isoformat() if flag.updated_at else None
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update feature flag: {str(e)}")


@router.delete("/feature-flags/{flag_id}")
async def delete_feature_flag(
    flag_id: str,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Delete a feature flag"""
    try:
        from sqlalchemy import select
        stmt = select(FeatureFlag).where(FeatureFlag.id == UUID(flag_id))
        result = await db.execute(stmt)
        flag = result.scalar_one_or_none()

        if not flag:
            raise HTTPException(status_code=404, detail="Feature flag not found")

        await db.delete(flag)
        await db.commit()

        return {"message": "Feature flag deleted successfully"}

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete feature flag: {str(e)}")


# Utility endpoints
@router.get("/check-permission")
async def check_user_permission(
    resource: str = Query(..., description="Resource name"),
    action: str = Query(..., description="Action name"),
    current_user: User = Depends(get_current_user),
    rbac_service: RBACService = Depends(get_rbac_service),
    db: AsyncSession = Depends(get_db)
):
    """Check if current user has specific permission"""
    try:
        has_perm = await rbac_service.has_permission(str(current_user.id), resource, action, db)
        return {"has_permission": has_perm}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check permission: {str(e)}")


@router.get("/check-feature")
async def check_feature_flag(
    feature_name: str = Query(..., description="Feature flag name"),
    current_user: User = Depends(get_current_user),
    rbac_service: RBACService = Depends(get_rbac_service),
    db: AsyncSession = Depends(get_db)
):
    """Check if a feature is enabled for current user"""
    try:
        enabled = await rbac_service.is_feature_enabled(feature_name, str(current_user.id), db)
        return {"enabled": enabled}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check feature flag: {str(e)}")
