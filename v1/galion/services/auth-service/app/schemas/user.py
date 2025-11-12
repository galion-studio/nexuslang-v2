"""
Pydantic schemas for user data validation.
These define the shape of data going in and out of APIs.
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from typing import Optional, Dict
from datetime import datetime, date
import uuid


class UserCreate(BaseModel):
    """
    Schema for creating a new user.
    Used in registration endpoint.
    
    Age Verification: Users must be 18+ to register.
    """
    email: EmailStr  # Automatically validates email format
    password: str = Field(..., min_length=8, max_length=100)
    name: str = Field(..., min_length=1, max_length=255)
    date_of_birth: date = Field(..., description="Date of birth - must be 18 or older")
    
    @field_validator('date_of_birth')
    @classmethod
    def validate_age(cls, v: date) -> date:
        """Validate that user is at least 18 years old."""
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        
        if age < 18:
            raise ValueError('You must be at least 18 years old to register')
        
        if age > 120:
            raise ValueError('Invalid date of birth')
        
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "name": "John Doe",
                "password": "SecurePassword123!",
                "date_of_birth": "1995-06-15"
            }
        }


class UserLogin(BaseModel):
    """
    Schema for user login.
    Used in login endpoint.
    """
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=100)
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePassword123!"
            }
        }


class UserResponse(BaseModel):
    """
    Schema for user responses.
    This is what clients receive (never includes password or full DOB!).
    """
    id: uuid.UUID
    email: str
    name: str
    role: str
    status: str
    email_verified: bool
    age_verified: bool
    badge_name: Optional[str] = None
    subscription_status: str = "free"
    created_at: datetime
    
    # ConfigDict allows Pydantic to work with SQLAlchemy models
    model_config = ConfigDict(from_attributes=True)

