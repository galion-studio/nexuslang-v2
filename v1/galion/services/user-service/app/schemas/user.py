"""
Pydantic schemas for user data validation.
These define the shape of data coming in (requests) and going out (responses).
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
import uuid


class UserResponse(BaseModel):
    """
    Schema for user data in API responses.
    Only includes safe, public information.
    Never includes password_hash or other sensitive data.
    """
    id: uuid.UUID
    email: EmailStr
    name: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    role: str
    email_verified: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True  # Allows creating from SQLAlchemy models


class UserUpdate(BaseModel):
    """
    Schema for updating user profile.
    All fields are optional - only update what's provided.
    """
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="User's full name")
    bio: Optional[str] = Field(None, max_length=1000, description="User biography (max 1000 characters)")
    avatar_url: Optional[str] = Field(None, max_length=500, description="URL to profile picture")
    
    class Config:
        # Example for API documentation
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "bio": "Software engineer passionate about AI and distributed systems",
                "avatar_url": "https://example.com/avatars/johndoe.jpg"
            }
        }


class UserSearch(BaseModel):
    """
    Schema for user search queries.
    Supports searching by name, email, or role.
    """
    query: Optional[str] = Field(None, description="Search by name or email")
    role: Optional[str] = Field(None, description="Filter by role")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    limit: int = Field(10, ge=1, le=100, description="Maximum number of results (1-100)")
    offset: int = Field(0, ge=0, description="Number of results to skip")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "john",
                "role": "user",
                "is_active": True,
                "limit": 10,
                "offset": 0
            }
        }


class UserListResponse(BaseModel):
    """
    Schema for paginated user list response.
    """
    users: list[UserResponse]
    total: int
    limit: int
    offset: int

