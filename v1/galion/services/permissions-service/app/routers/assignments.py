"""
User-Role assignment endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db, Role
from app.models import UserRoleAssign, UserRoleResponse
from app.middleware.auth import get_current_admin_user
from app.services.rbac import rbac_service

router = APIRouter()

@router.post("/users/{user_id}/roles", response_model=UserRoleResponse, status_code=201)
async def assign_role_to_user(
    user_id: UUID,
    role_assign: UserRoleAssign,
    current_user: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Assign role to user (Admin only)"""
    # Verify role exists
    role = db.query(Role).filter(Role.id == role_assign.role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # Assign role
    user_role = rbac_service.assign_role_to_user(
        db,
        user_id,
        role_assign.role_id,
        current_user["user_id"],
        role_assign.expires_at
    )
    
    return UserRoleResponse(
        id=user_role.id,
        user_id=user_role.user_id,
        role_id=user_role.role_id,
        role_name=role.name,
        assigned_by=user_role.assigned_by,
        assigned_at=user_role.assigned_at,
        expires_at=user_role.expires_at
    )

@router.get("/users/{user_id}/roles", response_model=List[UserRoleResponse])
async def get_user_roles(
    user_id: UUID,
    current_user: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get user's roles (Admin only)"""
    roles_data = rbac_service.get_user_roles(db, user_id)
    
    return [
        UserRoleResponse(
            id=r['id'],
            user_id=user_id,
            role_id=r['role_id'],
            role_name=r['role_name'],
            assigned_by=r['assigned_by'],
            assigned_at=r['assigned_at'],
            expires_at=r['expires_at']
        )
        for r in roles_data
    ]

@router.delete("/users/{user_id}/roles/{role_id}", status_code=204)
async def remove_role_from_user(
    user_id: UUID,
    role_id: int,
    current_user: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Remove role from user (Admin only)"""
    success = rbac_service.remove_role_from_user(db, user_id, role_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Role assignment not found")
    
    return None

