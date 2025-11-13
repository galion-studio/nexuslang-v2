#!/usr/bin/env python3
"""
Seed script for RBAC (Role-Based Access Control) system
Creates default roles, permissions, and feature flags for Galion Ecosystem
"""

import asyncio
import logging
from datetime import datetime

from ..core.database import get_db
from ..models.rbac import Role, Permission, FeatureFlag
from ..services.auth.rbac_service import Permissions, Roles

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Default permissions
DEFAULT_PERMISSIONS = [
    # User management
    {"resource": "users", "action": "read", "description": "View user profiles"},
    {"resource": "users", "action": "write", "description": "Edit user profiles"},
    {"resource": "users", "action": "delete", "description": "Delete user accounts"},
    {"resource": "users", "action": "admin", "description": "Full user administration"},

    # Content management
    {"resource": "content", "action": "read", "description": "View content"},
    {"resource": "content", "action": "write", "description": "Create and edit content"},
    {"resource": "content", "action": "delete", "description": "Delete content"},
    {"resource": "content", "action": "moderate", "description": "Moderate content"},

    # Grokopedia
    {"resource": "grokopedia", "action": "read", "description": "Read knowledge entries"},
    {"resource": "grokopedia", "action": "write", "description": "Create and edit entries"},
    {"resource": "grokopedia", "action": "verify", "description": "Verify knowledge entries"},
    {"resource": "grokopedia", "action": "admin", "description": "Full Grokopedia administration"},

    # AI services
    {"resource": "ai", "action": "read", "description": "Access AI services"},
    {"resource": "ai", "action": "write", "description": "Configure AI services"},
    {"resource": "ai", "action": "execute", "description": "Execute AI operations"},
    {"resource": "ai", "action": "admin", "description": "Full AI administration"},

    # Analytics
    {"resource": "analytics", "action": "read", "description": "View analytics"},
    {"resource": "analytics", "action": "admin", "description": "Full analytics administration"},

    # Admin panel
    {"resource": "admin", "action": "read", "description": "Access admin panel"},
    {"resource": "admin", "action": "write", "description": "Admin panel modifications"},
    {"resource": "admin", "action": "security", "description": "Security management"},

    # Beta features
    {"resource": "beta", "action": "access", "description": "Access beta features"},
    {"resource": "beta", "action": "test", "description": "Participate in beta testing"},
]


# Default roles with their permissions
DEFAULT_ROLES = [
    {
        "name": Roles.ADMIN,
        "display_name": "Administrator",
        "description": "Full system access and administration",
        "is_system": True,
        "permissions": [
            Permissions.USER_ADMIN,
            Permissions.CONTENT_MODERATE,
            Permissions.GROKOPEDIA_ADMIN,
            Permissions.AI_ADMIN,
            Permissions.ANALYTICS_ADMIN,
            Permissions.ADMIN_READ,
            Permissions.ADMIN_WRITE,
            Permissions.ADMIN_SECURITY,
            Permissions.BETA_ACCESS,
        ]
    },
    {
        "name": Roles.MODERATOR,
        "display_name": "Moderator",
        "description": "Content moderation and user management",
        "is_system": True,
        "permissions": [
            Permissions.USER_READ,
            Permissions.USER_WRITE,
            Permissions.CONTENT_READ,
            Permissions.CONTENT_WRITE,
            Permissions.CONTENT_MODERATE,
            Permissions.GROKOPEDIA_READ,
            Permissions.GROKOPEDIA_WRITE,
            Permissions.GROKOPEDIA_VERIFY,
            Permissions.ADMIN_READ,
        ]
    },
    {
        "name": Roles.EDITOR,
        "display_name": "Editor",
        "description": "Content creation and editing",
        "is_system": True,
        "permissions": [
            Permissions.CONTENT_READ,
            Permissions.CONTENT_WRITE,
            Permissions.GROKOPEDIA_READ,
            Permissions.GROKOPEDIA_WRITE,
        ]
    },
    {
        "name": Roles.CONTRIBUTOR,
        "display_name": "Contributor",
        "description": "Community contributor with write access",
        "is_system": True,
        "permissions": [
            Permissions.CONTENT_READ,
            Permissions.CONTENT_WRITE,
            Permissions.GROKOPEDIA_READ,
            Permissions.GROKOPEDIA_WRITE,
        ]
    },
    {
        "name": Roles.USER,
        "display_name": "User",
        "description": "Standard user with basic access",
        "is_system": True,
        "permissions": [
            Permissions.USER_READ,
            Permissions.CONTENT_READ,
            Permissions.GROKOPEDIA_READ,
            Permissions.AI_READ,
            Permissions.AI_EXECUTE,
        ]
    },
    {
        "name": Roles.BETA_TESTER,
        "display_name": "Beta Tester",
        "description": "Access to beta features and testing",
        "is_system": True,
        "permissions": [
            Permissions.USER_READ,
            Permissions.CONTENT_READ,
            Permissions.GROKOPEDIA_READ,
            Permissions.AI_READ,
            Permissions.AI_EXECUTE,
            Permissions.BETA_ACCESS,
            Permissions.BETA_TEST,
        ]
    },
    {
        "name": Roles.DEVELOPER,
        "display_name": "Developer",
        "description": "Developer access with API and advanced features",
        "is_system": True,
        "permissions": [
            Permissions.USER_READ,
            Permissions.CONTENT_READ,
            Permissions.CONTENT_WRITE,
            Permissions.GROKOPEDIA_READ,
            Permissions.GROKOPEDIA_WRITE,
            Permissions.AI_READ,
            Permissions.AI_WRITE,
            Permissions.AI_EXECUTE,
            Permissions.ANALYTICS_READ,
        ]
    },
]


# Default feature flags
DEFAULT_FEATURE_FLAGS = [
    {
        "name": "grokopedia_advanced_search",
        "display_name": "Advanced Grokopedia Search",
        "description": "Enable advanced search filters and semantic search",
        "enabled": True,
        "rollout_percentage": 100,
    },
    {
        "name": "ai_chat_beta",
        "display_name": "AI Chat Beta",
        "description": "Beta access to AI chat features",
        "enabled": True,
        "rollout_percentage": 50,
    },
    {
        "name": "developer_marketing_tools",
        "display_name": "Developer Marketing Tools",
        "description": "AI-powered marketing tools for developers",
        "enabled": True,
        "rollout_percentage": 25,
    },
    {
        "name": "knowledge_graph_visualization",
        "display_name": "Knowledge Graph Visualization",
        "description": "Interactive visualization of knowledge relationships",
        "enabled": False,
        "rollout_percentage": 0,
    },
    {
        "name": "multi_model_ai",
        "display_name": "Multi-Model AI Support",
        "description": "Support for multiple AI models and providers",
        "enabled": True,
        "rollout_percentage": 100,
    },
    {
        "name": "anti_raid_system",
        "display_name": "Anti-Raid Security System",
        "description": "Advanced security monitoring and DDoS protection",
        "enabled": True,
        "rollout_percentage": 100,
    },
]


async def seed_permissions(db):
    """Seed default permissions"""
    logger.info("Seeding permissions...")

    for perm_data in DEFAULT_PERMISSIONS:
        # Check if permission already exists
        existing = await db.execute(
            Permission.__table__.select().where(
                Permission.resource == perm_data["resource"],
                Permission.action == perm_data["action"]
            )
        )
        if existing.fetchone():
            logger.info(f"Permission {perm_data['resource']}:{perm_data['action']} already exists")
            continue

        # Create new permission
        permission = Permission(
            resource=perm_data["resource"],
            action=perm_data["action"],
            description=perm_data["description"]
        )
        db.add(permission)
        logger.info(f"Created permission: {perm_data['resource']}:{perm_data['action']}")

    await db.commit()


async def seed_roles(db):
    """Seed default roles"""
    logger.info("Seeding roles...")

    for role_data in DEFAULT_ROLES:
        # Check if role already exists
        existing = await db.execute(
            Role.__table__.select().where(Role.name == role_data["name"])
        )
        if existing.fetchone():
            logger.info(f"Role {role_data['name']} already exists")
            continue

        # Create new role
        role = Role(
            name=role_data["name"],
            display_name=role_data["display_name"],
            description=role_data["description"],
            permissions=role_data["permissions"],
            is_system=role_data["is_system"]
        )
        db.add(role)
        logger.info(f"Created role: {role_data['name']}")

    await db.commit()


async def seed_feature_flags(db):
    """Seed default feature flags"""
    logger.info("Seeding feature flags...")

    for flag_data in DEFAULT_FEATURE_FLAGS:
        # Check if feature flag already exists
        existing = await db.execute(
            FeatureFlag.__table__.select().where(FeatureFlag.name == flag_data["name"])
        )
        if existing.fetchone():
            logger.info(f"Feature flag {flag_data['name']} already exists")
            continue

        # Create new feature flag
        flag = FeatureFlag(
            name=flag_data["name"],
            display_name=flag_data["display_name"],
            description=flag_data["description"],
            enabled=flag_data["enabled"],
            rollout_percentage=flag_data["rollout_percentage"]
        )
        db.add(flag)
        logger.info(f"Created feature flag: {flag_data['name']}")

    await db.commit()


async def assign_admin_role(db):
    """Assign admin role to the first user (for bootstrapping)"""
    logger.info("Checking for admin role assignment...")

    # Find admin role
    admin_role = await db.execute(
        Role.__table__.select().where(Role.name == Roles.ADMIN)
    )
    admin_role = admin_role.fetchone()

    if not admin_role:
        logger.warning("Admin role not found, skipping admin assignment")
        return

    # Find first user
    from ..models.user import User
    first_user = await db.execute(
        User.__table__.select().limit(1)
    )
    first_user = first_user.fetchone()

    if not first_user:
        logger.info("No users found, skipping admin assignment")
        return

    # Check if user already has admin role
    from ..models.rbac import UserRole
    existing_assignment = await db.execute(
        UserRole.__table__.select().where(
            UserRole.user_id == first_user.id,
            UserRole.role_id == admin_role.id
        )
    )

    if existing_assignment.fetchone():
        logger.info("First user already has admin role")
        return

    # Assign admin role to first user
    from ..services.auth.rbac_service import get_rbac_service
    rbac_service = get_rbac_service()

    success = await rbac_service.assign_role(
        str(first_user.id),
        Roles.ADMIN,
        "system",  # assigned_by
        db
    )

    if success:
        logger.info(f"Assigned admin role to first user: {first_user.email}")
    else:
        logger.error("Failed to assign admin role to first user")


async def main():
    """Main seeding function"""
    logger.info("Starting RBAC seeding...")

    async for db in get_db():
        try:
            await seed_permissions(db)
            await seed_roles(db)
            await seed_feature_flags(db)
            await assign_admin_role(db)

            logger.info("RBAC seeding completed successfully!")

        except Exception as e:
            logger.error(f"Error during RBAC seeding: {e}")
            await db.rollback()
            raise
        finally:
            await db.close()


if __name__ == "__main__":
    asyncio.run(main())
