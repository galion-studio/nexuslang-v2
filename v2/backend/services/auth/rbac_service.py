"""
RBAC (Role-Based Access Control) Service
Comprehensive authorization system for Galion Ecosystem
"""

from typing import List, Dict, Any, Optional, Set
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
import logging
from functools import wraps
from datetime import datetime

from ...models.rbac import Role, Permission, UserRole, FeatureFlag
from ...models.user import User
from ...core.errors import AuthorizationError, ResourceNotFoundError
from ...core.database import get_db

logger = logging.getLogger(__name__)


class RBACService:
    """Role-Based Access Control Service"""

    def __init__(self):
        self._permissions_cache: Dict[str, Set[str]] = {}
        self._roles_cache: Dict[str, Role] = {}

    async def get_user_roles(self, user_id: str, db: AsyncSession) -> List[Role]:
        """Get all active roles for a user"""
        try:
            stmt = (
                select(Role)
                .join(UserRole)
                .where(
                    and_(
                        UserRole.user_id == user_id,
                        or_(
                            UserRole.expires_at.is_(None),
                            UserRole.expires_at > datetime.utcnow()
                        )
                    )
                )
                .options(selectinload(Role.user_roles))
            )

            result = await db.execute(stmt)
            roles = result.scalars().all()

            return list(roles)
        except Exception as e:
            logger.error(f"Failed to get user roles for {user_id}: {e}")
            return []

    async def get_user_permissions(self, user_id: str, db: AsyncSession) -> Set[str]:
        """Get all permissions for a user based on their roles"""
        roles = await self.get_user_roles(user_id, db)
        permissions = set()

        for role in roles:
            if isinstance(role.permissions, list):
                permissions.update(role.permissions)
            elif isinstance(role.permissions, dict):
                # Handle nested permission structure
                for resource, actions in role.permissions.items():
                    if isinstance(actions, list):
                        for action in actions:
                            permissions.add(f"{resource}:{action}")
                    else:
                        permissions.add(f"{resource}:{actions}")

        return permissions

    async def has_permission(self, user_id: str, resource: str, action: str, db: AsyncSession) -> bool:
        """Check if user has specific permission"""
        permissions = await self.get_user_permissions(user_id, db)
        required_permission = f"{resource}:{action}"

        return required_permission in permissions

    async def has_any_permission(self, user_id: str, permissions: List[str], db: AsyncSession) -> bool:
        """Check if user has any of the specified permissions"""
        user_permissions = await self.get_user_permissions(user_id, db)

        for permission in permissions:
            if permission in user_permissions:
                return True

        return False

    async def has_all_permissions(self, user_id: str, permissions: List[str], db: AsyncSession) -> bool:
        """Check if user has all of the specified permissions"""
        user_permissions = await self.get_user_permissions(user_id, db)

        for permission in permissions:
            if permission not in user_permissions:
                return False

        return True

    async def has_role(self, user_id: str, role_name: str, db: AsyncSession) -> bool:
        """Check if user has specific role"""
        roles = await self.get_user_roles(user_id, db)

        return any(role.name == role_name for role in roles)

    async def assign_role(self, user_id: str, role_name: str, assigned_by: str,
                         db: AsyncSession, expires_at: Optional[datetime] = None) -> bool:
        """Assign a role to a user"""
        try:
            # Get the role
            stmt = select(Role).where(Role.name == role_name)
            result = await db.execute(stmt)
            role = result.scalar_one_or_none()

            if not role:
                raise ResourceNotFoundError("role", role_name)

            # Check if assignment already exists
            existing_stmt = select(UserRole).where(
                and_(UserRole.user_id == user_id, UserRole.role_id == role.id)
            )
            existing_result = await db.execute(existing_stmt)
            existing = existing_result.scalar_one_or_none()

            if existing:
                # Update existing assignment
                existing.expires_at = expires_at
                existing.assigned_at = datetime.utcnow()
                existing.assigned_by = assigned_by
            else:
                # Create new assignment
                user_role = UserRole(
                    user_id=user_id,
                    role_id=role.id,
                    assigned_by=assigned_by,
                    expires_at=expires_at
                )
                db.add(user_role)

            await db.commit()
            logger.info(f"Role '{role_name}' assigned to user {user_id} by {assigned_by}")
            return True

        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to assign role '{role_name}' to user {user_id}: {e}")
            return False

    async def revoke_role(self, user_id: str, role_name: str, db: AsyncSession) -> bool:
        """Revoke a role from a user"""
        try:
            stmt = select(UserRole).join(Role).where(
                and_(
                    UserRole.user_id == user_id,
                    Role.name == role_name
                )
            )

            result = await db.execute(stmt)
            user_role = result.scalar_one_or_none()

            if user_role:
                await db.delete(user_role)
                await db.commit()
                logger.info(f"Role '{role_name}' revoked from user {user_id}")
                return True

            return False

        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to revoke role '{role_name}' from user {user_id}: {e}")
            return False

    async def is_feature_enabled(self, feature_name: str, user_id: Optional[str] = None,
                               db: AsyncSession = None) -> bool:
        """Check if a feature is enabled for a user or globally"""
        try:
            stmt = select(FeatureFlag).where(FeatureFlag.name == feature_name)
            result = await db.execute(stmt)
            flag = result.scalar_one_or_none()

            if not flag:
                return False

            # Check global enablement
            if not flag.enabled:
                return False

            # Check rollout percentage
            if flag.rollout_percentage < 100:
                # Simple user-based rollout (can be improved with more sophisticated logic)
                if user_id:
                    user_hash = hash(user_id) % 100
                    if user_hash >= flag.rollout_percentage:
                        return False

            return True

        except Exception as e:
            logger.error(f"Failed to check feature flag '{feature_name}': {e}")
            return False

    async def get_user_accessible_resources(self, user_id: str, resource_type: str,
                                          db: AsyncSession) -> List[str]:
        """Get list of resources user can access for a given type"""
        permissions = await self.get_user_permissions(user_id, db)

        accessible_resources = []
        for permission in permissions:
            if permission.startswith(f"{resource_type}:"):
                parts = permission.split(":")
                if len(parts) >= 3:
                    action = parts[1]
                    resource = ":".join(parts[2:])
                    if action in ["read", "write", "delete", "admin"]:
                        accessible_resources.append(resource)

        return list(set(accessible_resources))

    async def check_admin_access(self, user_id: str, db: AsyncSession) -> bool:
        """Check if user has admin access"""
        return await self.has_role(user_id, "admin", db)

    async def check_moderator_access(self, user_id: str, db: AsyncSession) -> bool:
        """Check if user has moderator access"""
        return await self.has_any_role(user_id, ["admin", "moderator"], db)

    async def has_any_role(self, user_id: str, role_names: List[str], db: AsyncSession) -> bool:
        """Check if user has any of the specified roles"""
        roles = await self.get_user_roles(user_id, db)
        user_role_names = {role.name for role in roles}

        return bool(user_role_names.intersection(set(role_names)))


# Global RBAC service instance
_rbac_service: Optional[RBACService] = None

def get_rbac_service() -> RBACService:
    global _rbac_service
    if _rbac_service is None:
        _rbac_service = RBACService()
    return _rbac_service


# Permission decorators for FastAPI endpoints
def require_permission(resource: str, action: str):
    """Decorator to require specific permission for endpoint"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract current_user from kwargs (assuming it's injected by Depends)
            current_user = kwargs.get('current_user')
            if not current_user:
                raise AuthorizationError("User not authenticated")

            # Get DB session
            db = None
            for arg in args:
                if hasattr(arg, 'execute'):  # SQLAlchemy session
                    db = arg
                    break

            if not db:
                # Try to get from kwargs
                db = kwargs.get('db')

            if not db:
                raise AuthorizationError("Database session not available")

            rbac_service = get_rbac_service()
            has_perm = await rbac_service.has_permission(str(current_user.id), resource, action, db)

            if not has_perm:
                raise AuthorizationError(f"Permission denied: {resource}:{action}")

            return await func(*args, **kwargs)

        return wrapper
    return decorator


def require_any_permission(permissions: List[str]):
    """Decorator to require any of the specified permissions"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                raise AuthorizationError("User not authenticated")

            db = None
            for arg in args:
                if hasattr(arg, 'execute'):
                    db = arg
                    break

            if not db:
                db = kwargs.get('db')

            if not db:
                raise AuthorizationError("Database session not available")

            rbac_service = get_rbac_service()
            has_perm = await rbac_service.has_any_permission(str(current_user.id), permissions, db)

            if not has_perm:
                raise AuthorizationError(f"Permission denied: any of {permissions}")

            return await func(*args, **kwargs)

        return wrapper
    return decorator


def require_role(role_name: str):
    """Decorator to require specific role"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                raise AuthorizationError("User not authenticated")

            db = None
            for arg in args:
                if hasattr(arg, 'execute'):
                    db = arg
                    break

            if not db:
                db = kwargs.get('db')

            if not db:
                raise AuthorizationError("Database session not available")

            rbac_service = get_rbac_service()
            has_role = await rbac_service.has_role(str(current_user.id), role_name, db)

            if not has_role:
                raise AuthorizationError(f"Role required: {role_name}")

            return await func(*args, **kwargs)

        return wrapper
    return decorator


def require_admin():
    """Decorator to require admin role"""
    return require_role("admin")


# Permission constants
class Permissions:
    """Permission constants for consistent usage"""

    # User management
    USER_READ = "users:read"
    USER_WRITE = "users:write"
    USER_DELETE = "users:delete"
    USER_ADMIN = "users:admin"

    # Content management
    CONTENT_READ = "content:read"
    CONTENT_WRITE = "content:write"
    CONTENT_DELETE = "content:delete"
    CONTENT_MODERATE = "content:moderate"

    # Grokopedia
    GROKOPEDIA_READ = "grokopedia:read"
    GROKOPEDIA_WRITE = "grokopedia:write"
    GROKOPEDIA_VERIFY = "grokopedia:verify"
    GROKOPEDIA_ADMIN = "grokopedia:admin"

    # AI services
    AI_READ = "ai:read"
    AI_WRITE = "ai:write"
    AI_EXECUTE = "ai:execute"
    AI_ADMIN = "ai:admin"

    # Analytics
    ANALYTICS_READ = "analytics:read"
    ANALYTICS_ADMIN = "analytics:admin"

    # Admin panel
    ADMIN_READ = "admin:read"
    ADMIN_WRITE = "admin:write"
    ADMIN_SECURITY = "admin:security"

    # Beta features
    BETA_ACCESS = "beta:access"
    BETA_TEST = "beta:test"


# Role constants
class Roles:
    """Role constants for consistent usage"""

    ADMIN = "admin"
    MODERATOR = "moderator"
    EDITOR = "editor"
    CONTRIBUTOR = "contributor"
    USER = "user"
    BETA_TESTER = "beta_tester"
    DEVELOPER = "developer"
