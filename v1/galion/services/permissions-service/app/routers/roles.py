"""
Role management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db, Role, Permission, RolePermission
from app.models import RoleCreate, RoleUpdate, RoleResponse, RoleWithPermissions, PermissionResponse
from app.middleware.auth import get_current_admin_user
from app.services.cache import cache_service

router = APIRouter()

@router.get("", response_model=List[RoleResponse])
async def list_roles(
    db: Session = Depends(get_db)
):
    """List all roles"""
    roles = db.query(Role).order_by(Role.name).all()
    return roles

@router.get("/{role_id}", response_model=RoleWithPermissions)
async def get_role(
    role_id: int,
    db: Session = Depends(get_db)
):
    """Get role by ID with its permissions"""
    role = db.query(Role).filter(Role.id == role_id).first()
    
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # Get permissions
    permissions = db.query(Permission).join(
        RolePermission, Permission.id == RolePermission.permission_id
    ).filter(
        RolePermission.role_id == role_id
    ).all()
    
    return RoleWithPermissions(
        id=role.id,
        name=role.name,
        description=role.description,
        is_system=role.is_system,
        created_at=role.created_at,
        updated_at=role.updated_at,
        permissions=[PermissionResponse.model_validate(p) for p in permissions]
    )

@router.post("", response_model=RoleResponse, status_code=201)
async def create_role(
    role_create: RoleCreate,
    current_user: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create new role (Admin only)"""
    # Check if role exists
    existing = db.query(Role).filter(Role.name == role_create.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Role already exists")
    
    # Create role
    role = Role(
        name=role_create.name,
        description=role_create.description,
        is_system=role_create.is_system
    )
    
    db.add(role)
    db.commit()
    db.refresh(role)
    
    # Invalidate all caches
    cache_service.invalidate_all_permissions()
    
    return role

@router.put("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    role_update: RoleUpdate,
    current_user: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update role (Admin only)"""
    role = db.query(Role).filter(Role.id == role_id).first()
    
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    if role.is_system:
        raise HTTPException(status_code=400, detail="Cannot modify system role")
    
    # Update fields
    if role_update.name:
        # Check if new name conflicts
        existing = db.query(Role).filter(
            Role.name == role_update.name,
            Role.id != role_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Role name already exists")
        role.name = role_update.name
    
    if role_update.description is not None:
        role.description = role_update.description
    
    db.commit()
    db.refresh(role)
    
    # Invalidate all caches
    cache_service.invalidate_all_permissions()
    
    return role

@router.delete("/{role_id}", status_code=204)
async def delete_role(
    role_id: int,
    current_user: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Delete role (Admin only)"""
    role = db.query(Role).filter(Role.id == role_id).first()
    
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    if role.is_system:
        raise HTTPException(status_code=400, detail="Cannot delete system role")
    
    db.delete(role)
    db.commit()
    
    # Invalidate all caches
    cache_service.invalidate_all_permissions()
    
    return None

