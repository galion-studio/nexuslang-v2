"""
Pydantic models for request/response validation
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID

# Role Models

class RoleCreate(BaseModel):
    """Create new role"""
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    is_system: bool = False

class RoleUpdate(BaseModel):
    """Update role"""
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None

class RoleResponse(BaseModel):
    """Role response model"""
    id: int
    name: str
    description: Optional[str] = None
    is_system: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class RoleWithPermissions(RoleResponse):
    """Role with its permissions"""
    permissions: List['PermissionResponse'] = []

# Permission Models

class PermissionCreate(BaseModel):
    """Create new permission"""
    resource: str = Field(..., max_length=100)
    action: str = Field(..., max_length=50)
    description: Optional[str] = None

class PermissionResponse(BaseModel):
    """Permission response model"""
    id: int
    resource: str
    action: str
    description: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# User Role Assignment Models

class UserRoleAssign(BaseModel):
    """Assign role to user"""
    role_id: int
    expires_at: Optional[datetime] = None

class UserRoleResponse(BaseModel):
    """User role assignment response"""
    id: int
    user_id: UUID
    role_id: int
    role_name: str
    assigned_by: Optional[UUID] = None
    assigned_at: datetime
    expires_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserPermissionsResponse(BaseModel):
    """User's effective permissions"""
    user_id: UUID
    roles: List[str] = []
    permissions: List[PermissionResponse] = []

# Permission Check Models

class PermissionCheckRequest(BaseModel):
    """Check if user has permission"""
    user_id: UUID
    resource: str
    action: str

class PermissionCheckResponse(BaseModel):
    """Result of permission check"""
    user_id: UUID
    resource: str
    action: str
    has_permission: bool
    roles: List[str] = []
    cached: bool = False

# Role-Permission Assignment

class RolePermissionAssign(BaseModel):
    """Assign permission to role"""
    permission_id: int

# Error Response

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None
    request_id: Optional[str] = None

