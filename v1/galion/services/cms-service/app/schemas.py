"""
Pydantic Schemas for Request/Response Validation
These define what data we accept and return in our API
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# ===== USER SCHEMAS =====

class UserBase(BaseModel):
    """Base user information shared across schemas"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    """Schema for creating a new user - includes password"""
    password: str = Field(..., min_length=6)

class UserResponse(UserBase):
    """Schema for returning user data - no password!"""
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    
    class Config:
        from_attributes = True  # Allows converting SQLAlchemy models to Pydantic

class UserLogin(BaseModel):
    """Schema for login requests"""
    username: str
    password: str

# ===== CATEGORY SCHEMAS =====

class CategoryBase(BaseModel):
    """Base category information"""
    name: str = Field(..., max_length=100)
    slug: str = Field(..., max_length=100)
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    """Schema for creating a category"""
    pass

class CategoryUpdate(BaseModel):
    """Schema for updating a category - all fields optional"""
    name: Optional[str] = Field(None, max_length=100)
    slug: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None

class CategoryResponse(CategoryBase):
    """Schema for returning category data"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# ===== CONTENT SCHEMAS =====

class ContentBase(BaseModel):
    """Base content information"""
    title: str = Field(..., max_length=200)
    slug: str = Field(..., max_length=200)
    content: str
    excerpt: Optional[str] = None
    content_type: str = Field(default="post")
    status: str = Field(default="draft")
    category_id: Optional[int] = None
    meta_title: Optional[str] = Field(None, max_length=200)
    meta_description: Optional[str] = None
    featured_image: Optional[str] = None

class ContentCreate(ContentBase):
    """Schema for creating content"""
    pass

class ContentUpdate(BaseModel):
    """Schema for updating content - all fields optional"""
    title: Optional[str] = Field(None, max_length=200)
    slug: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = None
    excerpt: Optional[str] = None
    content_type: Optional[str] = None
    status: Optional[str] = None
    category_id: Optional[int] = None
    meta_title: Optional[str] = Field(None, max_length=200)
    meta_description: Optional[str] = None
    featured_image: Optional[str] = None

class ContentResponse(ContentBase):
    """Schema for returning content data"""
    id: int
    author_id: int
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    views: int
    
    # Include nested author and category info
    author: UserResponse
    category: Optional[CategoryResponse] = None
    
    class Config:
        from_attributes = True

# ===== AUTH SCHEMAS =====

class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Schema for decoded token data"""
    username: Optional[str] = None

