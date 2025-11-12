"""
Admin Configuration
Defines admin users and their permissions
"""

from typing import List, Dict
from enum import Enum

class AdminRole(str, Enum):
    """Admin role levels"""
    OWNER = "owner"
    CEO = "ceo"
    ADMIN = "admin"
    MODERATOR = "moderator"


class AdminUser:
    """Admin user configuration"""
    def __init__(
        self,
        email: str,
        role: AdminRole,
        name: str,
        permissions: List[str]
    ):
        self.email = email
        self.role = role
        self.name = name
        self.permissions = permissions


# Primary admin user - Maciej Grajczyk
PRIMARY_ADMIN = AdminUser(
    email="maci.grajczyk@gmail.com",
    role=AdminRole.OWNER,
    name="Maciej Grajczyk",
    permissions=["*"]  # All permissions
)

# All admin emails for Maciej Grajczyk
ADMIN_EMAILS = [
    "maci.grajczyk@gmail.com",      # Primary
    "polskitygrys111@gmail.com",     # Secondary
    "frxdel@gmail.com",              # Secondary
    "legalizacija420@gmail.com",     # Secondary
    "info@galion.studio",            # Business
]

# Business emails (Zoho Mail)
BUSINESS_EMAILS = {
    "info": "info@galion.studio",
    "marketing": "marketing@galion.studio",  # Future
    "developer": "developer@galion.studio",   # Future
    "shop": "shop@galion.studio",             # Future
    "support": "support@galion.studio",       # Future
}

# Email forwarding configuration
EMAIL_FORWARDING = {
    "info@galion.studio": ["maci.grajczyk@gmail.com"],
    "support@galion.studio": ["maci.grajczyk@gmail.com"],
    "developer@galion.studio": ["maci.grajczyk@gmail.com"],
}


def is_admin(email: str) -> bool:
    """Check if email belongs to an admin user"""
    return email.lower() in [e.lower() for e in ADMIN_EMAILS]


def get_admin_role(email: str) -> AdminRole:
    """Get admin role for email"""
    if email.lower() in [e.lower() for e in ADMIN_EMAILS]:
        return AdminRole.OWNER
    return None


def has_permission(email: str, permission: str) -> bool:
    """Check if admin has specific permission"""
    if not is_admin(email):
        return False
    
    # Owner has all permissions
    if email.lower() == PRIMARY_ADMIN.email.lower():
        return True
    
    # All admin emails have full access for now
    return True


# Admin dashboard permissions
ADMIN_PERMISSIONS = [
    "view_users",
    "edit_users",
    "delete_users",
    "view_analytics",
    "manage_subscriptions",
    "manage_credits",
    "view_logs",
    "manage_content",
    "manage_api_keys",
    "system_settings",
]

