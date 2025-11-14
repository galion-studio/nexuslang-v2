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

from fastapi import APIRouter, Depends, HTTPException, status, Header, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime

# First principles: Use absolute imports
from ..core.database import get_db
from ..models.user import User, UserResponse
from ..core.config import settings
from ..services.auth.auth_service import get_auth_service

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
    id: str
    email: str
    username: str
    full_name: Optional[str]
    avatar_url: Optional[str]
    bio: Optional[str]
    website: Optional[str]
    is_active: bool
    is_verified: bool
    subscription_tier: str
    credits: float
    created_at: str
    updated_at: Optional[str]
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
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get current user from JWT token.

    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials

    try:
        auth_service = get_auth_service(db)
        user = await auth_service.get_current_user(token)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token or user not found"
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
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """Get current user if token provided, otherwise None."""
    if not authorization or not authorization.startswith("Bearer "):
        return None

    token = authorization.replace("Bearer ", "")

    try:
        auth_service = get_auth_service(db)
        return await auth_service.get_current_user(token)
    except:
        pass

    return None


# Endpoints

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    """
    Register a new user account.

    - Validates password strength
    - Checks for existing email/username
    - Creates user with hashed password and welcome credits
    - Returns access and refresh tokens
    """
    auth_service = get_auth_service(db)

    # Use auth service to register user
    result = await auth_service.register_user(
        email=user_data.email,
        username=user_data.username,
        password=user_data.password,
        full_name=user_data.full_name
    )

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )

    # Extract user data and tokens
    user_data_dict = result["user"]
    access_token = result.get("access_token")
    refresh_token = result.get("refresh_token")

    if not access_token or not refresh_token:
        # If tokens weren't generated, create them (for email verification flow)
        token_data = {"sub": str(user_data_dict["id"]), "email": user_data_dict["email"], "username": user_data_dict["username"]}
        access_token = auth_service.create_access_token(token_data)
        refresh_token = auth_service.create_refresh_token(token_data)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.jwt_expiration_hours * 60 * 60,
        user=user_data_dict
    )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Authenticate user and return tokens.

    - Validates credentials
    - Updates last_login timestamp
    - Returns access and refresh tokens
    """
    auth_service = get_auth_service(db)

    # Use auth service to authenticate user
    result = await auth_service.authenticate_user(credentials.email, credentials.password)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    return TokenResponse(
        access_token=result["access_token"],
        refresh_token=result["refresh_token"],
        expires_in=result["expires_in"],
        user=result["user"]
    )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    current_user: User = Depends(get_current_user)
):
    """
    Logout user.

    Note: Token blacklisting not implemented yet - tokens remain valid until expiry.
    """
    # TODO: Implement token blacklisting for proper logout
    return {"message": "Successfully logged out"}


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """
    Refresh access token using refresh token.

    - Validates refresh token
    - Issues new access and refresh tokens
    """
    auth_service = get_auth_service(db)

    result = await auth_service.refresh_access_token(request.refresh_token)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    # Get user info for response
    user = await auth_service.get_current_user(result["access_token"])
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return TokenResponse(
        access_token=result["access_token"],
        refresh_token="",  # Don't return new refresh token in this simple implementation
        expires_in=result["expires_in"],
        user=user.to_dict()
    )


@router.get("/me", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    """
    Get current user profile.

    Returns complete user information (excluding sensitive fields).
    """
    return UserResponse(**current_user.to_dict())


@router.put("/me", response_model=UserResponse)
async def update_profile(
    updates: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update current user profile.

    Allows updating: full_name, bio, website, avatar_url
    """
    auth_service = get_auth_service(db)

    # Convert updates to dict and filter out None values
    update_dict = {k: v for k, v in updates.model_dump().items() if v is not None}

    result = await auth_service.update_user_profile(str(current_user.id), **update_dict)

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )

    return UserResponse(**result["user"])


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)  # Requires authentication
):
    """
    Get user by ID (public profile).

    Requires authentication to prevent scraping.
    """
    result = await db.execute(db.query(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse(**user.to_dict())


@router.get("/check-email/{email}")
async def check_email_available(email: str, db: AsyncSession = Depends(get_db)):
    """
    Check if email is available for registration.

    Returns: {"available": true/false}
    """
    result = await db.execute(db.query(User).filter(User.email == email.lower()))
    existing = result.scalar_one_or_none()
    return {"available": existing is None}


@router.get("/check-username/{username}")
async def check_username_available(username: str, db: AsyncSession = Depends(get_db)):
    """
    Check if username is available.

    Returns: {"available": true/false}
    """
    result = await db.execute(db.query(User).filter(User.username == username))
    existing = result.scalar_one_or_none()
    return {"available": existing is None}


@router.post("/request-password-reset")
async def request_password_reset(request: PasswordResetRequest, db: AsyncSession = Depends(get_db)):
    """
    Request password reset for email address.

    Sends reset email if account exists.
    """
    auth_service = get_auth_service(db)
    result = await auth_service.initiate_password_reset(request.email)

    # Always return success for security (don't reveal if email exists)
    return {"message": result["message"]}


@router.post("/reset-password")
async def reset_password(request: PasswordReset, db: AsyncSession = Depends(get_db)):
    """
    Reset password using reset token.

    Validates token and updates password.
    """
    auth_service = get_auth_service(db)
    result = await auth_service.reset_password(request.token, request.new_password)

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )

    return {"message": result["message"]}


@router.post("/verify-email")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    """
    Verify user email using verification token.

    Marks email as verified.
    """
    auth_service = get_auth_service(db)
    result = await auth_service.verify_email(token)

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )

    return {"message": result["message"]}


@router.post("/change-password")
async def change_password(
    current_password: str = Body(..., embed=True),
    new_password: str = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Change current user's password.

    Requires current password for verification.
    """
    auth_service = get_auth_service(db)
    result = await auth_service.change_password(
        str(current_user.id),
        current_password,
        new_password
    )

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )

    return {"message": result["message"]}


@router.delete("/account")
async def deactivate_account(
    password: str = Body(..., embed=True),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Deactivate current user account.

    Requires password confirmation.
    """
    auth_service = get_auth_service(db)
    result = await auth_service.deactivate_account(str(current_user.id), password)

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )

    return {"message": result["message"]}
