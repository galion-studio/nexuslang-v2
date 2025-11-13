"""
Authentication API Endpoints
Complete REST API for user authentication, registration, login, logout, and profile management.

Endpoints:
- POST /register - Create new user account
- POST /login - Authenticate user and get tokens
- POST /logout - Logout and blacklist token
- POST /refresh - Refresh access token
- GET /me - Get current user profile
- PUT /me - Update user profile
- POST /verify-email - Verify email address
- POST /request-password-reset - Request password reset
- POST /reset-password - Reset password with token
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from ..services.auth.auth_service import get_auth_service, AuthService
from ..core.database import get_db
from ..models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


# Request/Response Models
class UserRegister(BaseModel):
    """User registration request."""
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    password: str = Field(..., min_length=12, description="Password (min 12 characters)")
    full_name: Optional[str] = Field(None, max_length=255, description="Full name")


class UserLogin(BaseModel):
    """User login request."""
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., description="Password")


class TokenResponse(BaseModel):
    """Token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class UserResponse(BaseModel):
    """User profile response."""
    id: int
    email: str
    username: str
    full_name: Optional[str]
    avatar_url: Optional[str]
    bio: Optional[str]
    website: Optional[str]
    is_verified: bool
    is_admin: bool
    subscription_tier: str
    subscription_status: str
    credits: float
    created_at: str
    last_login: Optional[str]


class UserUpdate(BaseModel):
    """User profile update request."""
    full_name: Optional[str] = None
    bio: Optional[str] = None
    website: Optional[str] = None
    avatar_url: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    """Refresh token request."""
    refresh_token: str


class PasswordResetRequest(BaseModel):
    """Password reset request."""
    email: EmailStr


class PasswordReset(BaseModel):
    """Password reset with token."""
    token: str
    new_password: str = Field(..., min_length=12)


# Dependency to get current user from token
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current user from JWT token.
    
    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials
    
    try:
        payload = decode_token(token)
        email = payload.get("sub")
        
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        user = db.query(User).filter(User.email == email).first()
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is disabled"
            )
        
        return user
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication error: {str(e)}"
        )


# Optional: Get current user but allow None
async def get_current_user_optional(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user if token provided, otherwise None."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    token = authorization.replace("Bearer ", "")
    
    try:
        payload = decode_token(token)
        email = payload.get("sub")
        if email:
            return db.query(User).filter(User.email == email).first()
    except:
        pass
    
    return None


# Endpoints

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user account.

    - Validates password strength
    - Checks for existing email/username
    - Creates user with hashed password and welcome credits
    - Returns access and refresh tokens
    """
    auth_service = get_auth_service(db)

    # Register user using auth service
    result = auth_service.register_user(
        email=user_data.email,
        username=user_data.username,
        password=user_data.password,
        full_name=user_data.full_name or ""
    )

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )

    # Authenticate user immediately to get tokens
    auth_result = auth_service.authenticate_user(user_data.email, user_data.password)

    if not auth_result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration successful but login failed"
        )

    return auth_result


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return tokens.

    - Validates credentials
    - Updates last_login timestamp
    - Returns access and refresh tokens
    """
    auth_service = get_auth_service(db)

    # Authenticate user
    auth_result = auth_service.authenticate_user(credentials.email, credentials.password)

    if not auth_result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    return auth_result


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user: User = Depends(get_current_user)
):
    """
    Logout user and blacklist current token.
    
    Token will no longer be valid for authentication.
    """
    token = credentials.credentials
    blacklist_token(token)
    
    return {"message": "Successfully logged out"}


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    Refresh access token using refresh token.
    
    - Validates refresh token
    - Issues new access and refresh tokens
    """
    try:
        payload = decode_token(request.refresh_token)
        
        # Verify it's a refresh token
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        email = payload.get("sub")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Get user
        user = db.query(User).filter(User.email == email).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new token pair
        tokens = create_token_pair({"sub": user.email})
        
        # Blacklist old refresh token
        blacklist_token(request.refresh_token)
        
        return {
            **tokens,
            "user": user.to_dict()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token refresh failed: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    """
    Get current user profile.
    
    Returns complete user information (excluding sensitive fields).
    """
    return current_user.to_dict()


@router.put("/me", response_model=UserResponse)
async def update_profile(
    updates: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user profile.
    
    Allows updating: full_name, bio, website, avatar_url
    """
    # Update fields if provided
    if updates.full_name is not None:
        current_user.full_name = updates.full_name
    
    if updates.bio is not None:
        current_user.bio = updates.bio
    
    if updates.website is not None:
        current_user.website = updates.website
    
    if updates.avatar_url is not None:
        current_user.avatar_url = updates.avatar_url
    
    current_user.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(current_user)
    
    return current_user.to_dict()


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # Requires authentication
):
    """
    Get user by ID (public profile).
    
    Requires authentication to prevent scraping.
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user.to_dict()


@router.get("/check-email/{email}")
async def check_email_available(email: str, db: Session = Depends(get_db)):
    """
    Check if email is available for registration.
    
    Returns: {"available": true/false}
    """
    existing = db.query(User).filter(User.email == email).first()
    return {"available": existing is None}


@router.get("/check-username/{username}")
async def check_username_available(username: str, db: Session = Depends(get_db)):
    """
    Check if username is available.
    
    Returns: {"available": true/false}
    """
    existing = db.query(User).filter(User.username == username).first()
    return {"available": existing is None}
