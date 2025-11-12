"""
Permission management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db, Permission, RolePermission
from app.models import (
    PermissionCreate,
    PermissionResponse,
    RolePermissionAssign,
    PermissionCheckRequest,
    PermissionCheckResponse,
    UserPermissionsResponse
)
from app.middleware.auth import get_current_user, get_current_admin_user
from app.services.rbac import rbac_service
from app.services.cache import cache_service

router = APIRouter()

@router.get("", response_model=List[PermissionResponse])
async def list_permissions(
    resource: str = None,
    db: Session = Depends(get_db)
):
    """List all permissions, optionally filtered by resource"""
    query = db.query(Permission)
    
    if resource:
        query = query.filter(Permission.resource == resource)
    
    permissions = query.order_by(Permission.resource, Permission.action).all()
    return permissions

@router.post("", response_model=PermissionResponse, status_code=201)
async def create_permission(
    perm_create: PermissionCreate,
    current_user: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create new permission (Admin only)"""
    # Check if permission exists
    existing = db.query(Permission).filter(
        Permission.resource == perm_create.resource,
        Permission.action == perm_create.action
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Permission already exists")
    
    # Create permission
    permission = Permission(
        resource=perm_create.resource,
        action=perm_create.action,
        description=perm_create.description
    )
    
    db.add(permission)
    db.commit()
    db.refresh(permission)
    
    return permission

@router.post("/roles/{role_id}/permissions", status_code=201)
async def assign_permission_to_role(
    role_id: int,
    perm_assign: RolePermissionAssign,
    current_user: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Assign permission to role (Admin only)"""
    # Verify role exists
    from app.database import Role
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # Verify permission exists
    permission = db.query(Permission).filter(Permission.id == perm_assign.permission_id).first()
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    
    # Check if already assigned
    existing = db.query(RolePermission).filter(
        RolePermission.role_id == role_id,
        RolePermission.permission_id == perm_assign.permission_id
    ).first()
    
    if existing:
        return {"message": "Permission already assigned to role"}
    
    # Create assignment
    role_perm = RolePermission(
        role_id=role_id,
        permission_id=perm_assign.permission_id
    )
    
    db.add(role_perm)
    db.commit()
    
    # Invalidate all caches
    cache_service.invalidate_all_permissions()
    
    return {"message": "Permission assigned to role successfully"}

@router.delete("/roles/{role_id}/permissions/{permission_id}", status_code=204)
async def remove_permission_from_role(
    role_id: int,
    permission_id: int,
    current_user: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Remove permission from role (Admin only)"""
    role_perm = db.query(RolePermission).filter(
        RolePermission.role_id == role_id,
        RolePermission.permission_id == permission_id
    ).first()
    
    if not role_perm:
        raise HTTPException(status_code=404, detail="Permission assignment not found")
    
    db.delete(role_perm)
    db.commit()
    
    # Invalidate all caches
    cache_service.invalidate_all_permissions()
    
    return None

@router.post("/check", response_model=PermissionCheckResponse)
async def check_permission(
    check_request: PermissionCheckRequest,
    db: Session = Depends(get_db)
):
    """Check if user has specific permission"""
    has_perm, roles = rbac_service.has_permission(
        db,
        check_request.user_id,
        check_request.resource,
        check_request.action
    )
    
    # Check if result was cached
    cached = cache_service.check_permission(
        str(check_request.user_id),
        check_request.resource,
        check_request.action
    ) is not None
    
    return PermissionCheckResponse(
        user_id=check_request.user_id,
        resource=check_request.resource,
        action=check_request.action,
        has_permission=has_perm,
        roles=roles,
        cached=cached
    )

@router.get("/me", response_model=UserPermissionsResponse)
async def get_my_permissions(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's permissions"""
    user_id = current_user["user_id"]
    
    # Get all permissions
    permissions = rbac_service.get_user_permissions(db, user_id)
    
    # Get roles
    roles_data = rbac_service.get_user_roles(db, user_id)
    role_names = [r['role_name'] for r in roles_data]
    
    # Build permission responses
    perm_responses = []
    seen = set()
    for p in permissions:
        key = (p['resource'], p['action'])
        if key not in seen:
            seen.add(key)
            perm_responses.append(PermissionResponse(
                id=p['id'],
                resource=p['resource'],
                action=p['action'],
                description=p.get('description'),
                created_at=p.get('created_at', None)
            ))
    
    return UserPermissionsResponse(
        user_id=user_id,
        roles=role_names,
        permissions=perm_responses
    )

