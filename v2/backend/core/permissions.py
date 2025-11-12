"""
Permission checking and role management for RBAC
Provides decorators and utilities for checking user permissions
"""

from functools import wraps
from typing import List, Optional, Callable
from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from .database import get_db
from ..models.user import User
from ..models.rbac import Role, UserRole, FeatureFlag, BetaTesterProfile
from ..api.auth import get_current_user
import logging

logger = logging.getLogger(__name__)


class PermissionDeniedError(HTTPException):
    """Custom exception for permission denied"""
    
    def __init__(self, detail: str = "Permission denied"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


class PermissionChecker:
    """Service for checking user permissions"""
    
    @staticmethod
    async def get_user_roles(user: User, db: AsyncSession) -> List[Role]:
        """
        Get all roles for a user.
        
        Args:
            user: User object
            db: Database session
            
        Returns:
            List of Role objects
        """
        result = await db.execute(
            select(Role)
            .join(UserRole)
            .where(UserRole.user_id == user.id)
            .where((UserRole.expires_at.is_(None)) | (UserRole.expires_at > db.func.now()))
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_user_permissions(user: User, db: AsyncSession) -> List[str]:
        """
        Get all permissions for a user (flattened from roles).
        
        Args:
            user: User object
            db: Database session
            
        Returns:
            List of permission strings (e.g., ["users:read", "nexuslang:execute"])
        """
        roles = await PermissionChecker.get_user_roles(user, db)
        
        # Flatten permissions from all roles
        all_permissions = []
        for role in roles:
            if isinstance(role.permissions, list):
                all_permissions.extend(role.permissions)
        
        # Remove duplicates
        return list(set(all_permissions))
    
    @staticmethod
    def check_permission(user_permissions: List[str], required_permission: str) -> bool:
        """
        Check if user has a specific permission.
        
        Permission format: "resource:action" (e.g., "users:read")
        Wildcards supported: "*:*" (all), "users:*" (all user actions)
        
        Args:
            user_permissions: List of user's permissions
            required_permission: Required permission string
            
        Returns:
            True if user has permission, False otherwise
        """
        # Check for wildcard permission (super admin)
        if "*:*" in user_permissions:
            return True
        
        # Parse required permission
        try:
            resource, action = required_permission.split(':')
        except ValueError:
            logger.warning(f"Invalid permission format: {required_permission}")
            return False
        
        # Check for resource wildcard (e.g., "users:*")
        resource_wildcard = f"{resource}:*"
        if resource_wildcard in user_permissions:
            return True
        
        # Check for exact permission
        if required_permission in user_permissions:
            return True
        
        return False
    
    @staticmethod
    async def user_has_permission(user: User, permission: str, db: AsyncSession) -> bool:
        """
        Check if user has a specific permission.
        
        Args:
            user: User object
            permission: Required permission (e.g., "users:read")
            db: Database session
            
        Returns:
            True if user has permission, False otherwise
        """
        user_permissions = await PermissionChecker.get_user_permissions(user, db)
        return PermissionChecker.check_permission(user_permissions, permission)
    
    @staticmethod
    async def user_has_role(user: User, role_name: str, db: AsyncSession) -> bool:
        """
        Check if user has a specific role.
        
        Args:
            user: User object
            role_name: Name of the role
            db: Database session
            
        Returns:
            True if user has role, False otherwise
        """
        roles = await PermissionChecker.get_user_roles(user, db)
        return any(role.name == role_name for role in roles)
    
    @staticmethod
    async def user_has_any_role(user: User, role_names: List[str], db: AsyncSession) -> bool:
        """
        Check if user has any of the specified roles.
        
        Args:
            user: User object
            role_names: List of role names
            db: Database session
            
        Returns:
            True if user has at least one role, False otherwise
        """
        roles = await PermissionChecker.get_user_roles(user, db)
        user_role_names = {role.name for role in roles}
        return bool(user_role_names.intersection(set(role_names)))


# Dependency for requiring specific permission
def require_permission(permission: str):
    """
    Dependency that checks if current user has a specific permission.
    
    Usage:
        @router.get("/users")
        async def list_users(
            user: User = Depends(require_permission("users:read"))
        ):
            ...
    """
    async def permission_checker(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> User:
        has_permission = await PermissionChecker.user_has_permission(
            current_user, permission, db
        )
        
        if not has_permission:
            logger.warning(
                f"Permission denied: {current_user.username} tried to access '{permission}'"
            )
            raise PermissionDeniedError(
                detail=f"You don't have permission: {permission}"
            )
        
        return current_user
    
    return permission_checker


# Dependency for requiring specific role
def require_role(role_name: str):
    """
    Dependency that checks if current user has a specific role.
    
    Usage:
        @router.get("/admin")
        async def admin_dashboard(
            user: User = Depends(require_role("admin"))
        ):
            ...
    """
    async def role_checker(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> User:
        has_role = await PermissionChecker.user_has_role(
            current_user, role_name, db
        )
        
        if not has_role:
            logger.warning(
                f"Role check failed: {current_user.username} tried to access role '{role_name}'"
            )
            raise PermissionDeniedError(
                detail=f"You must be a {role_name} to access this resource"
            )
        
        return current_user
    
    return role_checker


# Dependency for requiring any of multiple roles
def require_any_role(*role_names: str):
    """
    Dependency that checks if current user has any of the specified roles.
    
    Usage:
        @router.get("/beta-features")
        async def beta_features(
            user: User = Depends(require_any_role("admin", "beta_tester"))
        ):
            ...
    """
    async def role_checker(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> User:
        has_any_role = await PermissionChecker.user_has_any_role(
            current_user, list(role_names), db
        )
        
        if not has_any_role:
            logger.warning(
                f"Role check failed: {current_user.username} tried to access roles '{role_names}'"
            )
            raise PermissionDeniedError(
                detail=f"You must be one of: {', '.join(role_names)}"
            )
        
        return current_user
    
    return role_checker


# Feature flag checker
class FeatureFlagChecker:
    """Service for checking feature flags"""
    
    @staticmethod
    async def is_feature_enabled(
        feature_name: str,
        user: Optional[User] = None,
        db: AsyncSession = None
    ) -> bool:
        """
        Check if a feature flag is enabled for a user.
        
        Args:
            feature_name: Name of the feature flag
            user: User object (optional)
            db: Database session
            
        Returns:
            True if feature is enabled, False otherwise
        """
        if not db:
            # If no database session, assume feature is disabled
            return False
        
        # Get feature flag
        result = await db.execute(
            select(FeatureFlag).where(FeatureFlag.name == feature_name)
        )
        feature = result.scalar_one_or_none()
        
        if not feature:
            # Feature flag doesn't exist, assume disabled
            return False
        
        # If feature is globally disabled, return False
        if not feature.enabled:
            return False
        
        # If no user context, check if feature is globally enabled
        if not user:
            return feature.rollout_percentage == 100
        
        # Check if user is specifically targeted
        if str(user.id) in feature.target_users:
            return True
        
        # Check if user's role is targeted
        user_roles = await PermissionChecker.get_user_roles(user, db)
        user_role_names = {role.name for role in user_roles}
        if user_role_names.intersection(set(feature.target_roles)):
            return True
        
        # Check if user's cohort is targeted (for beta testers)
        result = await db.execute(
            select(BetaTesterProfile).where(BetaTesterProfile.user_id == user.id)
        )
        beta_profile = result.scalar_one_or_none()
        
        if beta_profile and beta_profile.cohort in feature.target_cohorts:
            return True
        
        # Check rollout percentage (deterministic based on user ID)
        if feature.rollout_percentage > 0:
            # Use user ID hash to determine if they're in rollout
            user_hash = hash(str(user.id))
            if (user_hash % 100) < feature.rollout_percentage:
                return True
        
        return False


# Dependency for requiring feature flag
def require_feature(feature_name: str):
    """
    Dependency that checks if a feature flag is enabled for current user.
    
    Usage:
        @router.post("/voice/clone")
        async def clone_voice(
            user: User = Depends(require_feature("voice_cloning"))
        ):
            ...
    """
    async def feature_checker(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> User:
        is_enabled = await FeatureFlagChecker.is_feature_enabled(
            feature_name, current_user, db
        )
        
        if not is_enabled:
            logger.info(
                f"Feature not enabled: {current_user.username} tried to access '{feature_name}'"
            )
            raise PermissionDeniedError(
                detail=f"Feature '{feature_name}' is not available for your account"
            )
        
        return current_user
    
    return feature_checker


# Utility functions for role management
async def assign_role(user: User, role_name: str, db: AsyncSession, assigned_by: Optional[User] = None):
    """
    Assign a role to a user.
    
    Args:
        user: User to assign role to
        role_name: Name of the role
        db: Database session
        assigned_by: User who assigned the role (for audit)
    """
    # Get role
    result = await db.execute(
        select(Role).where(Role.name == role_name)
    )
    role = result.scalar_one_or_none()
    
    if not role:
        raise ValueError(f"Role '{role_name}' not found")
    
    # Check if user already has role
    result = await db.execute(
        select(UserRole).where(
            UserRole.user_id == user.id,
            UserRole.role_id == role.id
        )
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        return  # User already has role
    
    # Create user_role
    user_role = UserRole(
        user_id=user.id,
        role_id=role.id,
        assigned_by=assigned_by.id if assigned_by else None
    )
    
    db.add(user_role)
    await db.commit()
    
    logger.info(f"Assigned role '{role_name}' to user {user.username}")


async def remove_role(user: User, role_name: str, db: AsyncSession):
    """
    Remove a role from a user.
    
    Args:
        user: User to remove role from
        role_name: Name of the role
        db: Database session
    """
    # Get role
    result = await db.execute(
        select(Role).where(Role.name == role_name)
    )
    role = result.scalar_one_or_none()
    
    if not role:
        raise ValueError(f"Role '{role_name}' not found")
    
    # Delete user_role
    result = await db.execute(
        select(UserRole).where(
            UserRole.user_id == user.id,
            UserRole.role_id == role.id
        )
    )
    user_role = result.scalar_one_or_none()
    
    if user_role:
        await db.delete(user_role)
        await db.commit()
        logger.info(f"Removed role '{role_name}' from user {user.username}")


# Example combined decorators
def require_admin():
    """Shortcut for requiring admin role"""
    return require_any_role("super_admin", "admin")


def require_beta_access():
    """Shortcut for requiring beta tester or higher"""
    return require_any_role("super_admin", "admin", "beta_tester", "developer")

