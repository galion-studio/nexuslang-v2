"""
RBAC service - core permission checking logic
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Dict, Optional
from uuid import UUID
from datetime import datetime

from app.database import UserRole, Role, Permission, RolePermission
from app.services.cache import cache_service

class RBACService:
    """Role-Based Access Control service"""
    
    def get_user_permissions(self, db: Session, user_id: UUID) -> List[Dict]:
        """
        Get all effective permissions for a user
        
        Returns list of permissions with role context
        """
        # Check cache first
        cached = cache_service.get_user_permissions(str(user_id))
        if cached is not None:
            return cached
        
        # Query from database
        query = db.query(
            Permission.id,
            Permission.resource,
            Permission.action,
            Permission.description,
            Role.name.label('role_name')
        ).join(
            RolePermission, Permission.id == RolePermission.permission_id
        ).join(
            Role, RolePermission.role_id == Role.id
        ).join(
            UserRole, Role.id == UserRole.role_id
        ).filter(
            UserRole.user_id == user_id,
            and_(
                UserRole.expires_at.is_(None) |
                (UserRole.expires_at > datetime.utcnow())
            )
        ).distinct()
        
        results = query.all()
        
        # Convert to dict list
        permissions = [
            {
                'id': row.id,
                'resource': row.resource,
                'action': row.action,
                'description': row.description,
                'role_name': row.role_name
            }
            for row in results
        ]
        
        # Cache results
        cache_service.set_user_permissions(str(user_id), permissions)
        
        return permissions
    
    def has_permission(
        self,
        db: Session,
        user_id: UUID,
        resource: str,
        action: str
    ) -> tuple[bool, List[str]]:
        """
        Check if user has specific permission
        
        Returns: (has_permission, list_of_roles)
        """
        # Try cache first
        cached_result = cache_service.check_permission(str(user_id), resource, action)
        if cached_result is not None:
            # Get roles from full permissions (already cached)
            permissions = cache_service.get_user_permissions(str(user_id))
            roles = list(set([p['role_name'] for p in permissions if p['resource'] == resource and p['action'] == action]))
            return cached_result, roles
        
        # Query database
        query = db.query(
            Role.name
        ).join(
            UserRole, Role.id == UserRole.role_id
        ).join(
            RolePermission, Role.id == RolePermission.role_id
        ).join(
            Permission, RolePermission.permission_id == Permission.id
        ).filter(
            UserRole.user_id == user_id,
            Permission.resource == resource,
            Permission.action == action,
            and_(
                UserRole.expires_at.is_(None) |
                (UserRole.expires_at > datetime.utcnow())
            )
        ).distinct()
        
        roles = [row.name for row in query.all()]
        has_perm = len(roles) > 0
        
        return has_perm, roles
    
    def get_user_roles(self, db: Session, user_id: UUID) -> List[Dict]:
        """Get all roles assigned to a user"""
        query = db.query(UserRole, Role).join(
            Role, UserRole.role_id == Role.id
        ).filter(
            UserRole.user_id == user_id,
            and_(
                UserRole.expires_at.is_(None) |
                (UserRole.expires_at > datetime.utcnow())
            )
        )
        
        results = []
        for user_role, role in query.all():
            results.append({
                'id': user_role.id,
                'role_id': role.id,
                'role_name': role.name,
                'assigned_by': user_role.assigned_by,
                'assigned_at': user_role.assigned_at,
                'expires_at': user_role.expires_at
            })
        
        return results
    
    def assign_role_to_user(
        self,
        db: Session,
        user_id: UUID,
        role_id: int,
        assigned_by: UUID,
        expires_at: Optional[datetime] = None
    ) -> UserRole:
        """Assign a role to a user"""
        # Check if already assigned
        existing = db.query(UserRole).filter(
            UserRole.user_id == user_id,
            UserRole.role_id == role_id
        ).first()
        
        if existing:
            # Update expiration if provided
            if expires_at:
                existing.expires_at = expires_at
            db.commit()
            return existing
        
        # Create new assignment
        user_role = UserRole(
            user_id=user_id,
            role_id=role_id,
            assigned_by=assigned_by,
            expires_at=expires_at
        )
        
        db.add(user_role)
        db.commit()
        db.refresh(user_role)
        
        # Invalidate cache
        cache_service.invalidate_user_permissions(str(user_id))
        
        return user_role
    
    def remove_role_from_user(self, db: Session, user_id: UUID, role_id: int) -> bool:
        """Remove a role from a user"""
        user_role = db.query(UserRole).filter(
            UserRole.user_id == user_id,
            UserRole.role_id == role_id
        ).first()
        
        if not user_role:
            return False
        
        db.delete(user_role)
        db.commit()
        
        # Invalidate cache
        cache_service.invalidate_user_permissions(str(user_id))
        
        return True

# Singleton instance
rbac_service = RBACService()

