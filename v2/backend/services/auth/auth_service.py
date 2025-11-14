"""
Authentication Service
======================

Comprehensive authentication and user management service.

Features:
- User registration and login
- Password hashing and verification
- JWT token management
- Password reset functionality
- Email verification
- User profile management
- Session management
- Security monitoring
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import secrets
import hashlib
import jwt
from sqlalchemy.ext.asyncio import AsyncSession

# First principles: Absolute imports
from models.user import User
from core.config import settings
from core.database import get_db_session


class AuthService:
    """Authentication service for user management."""

    def __init__(self, db: AsyncSession):
        self.db = db

    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=settings.jwt_expiration_hours)

        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)
        return encoded_jwt

    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create JWT refresh token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.jwt_refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    async def register_user(self, email: str, username: str, password: str, **kwargs) -> Dict[str, Any]:
        """
        Register a new user with comprehensive validation.

        Args:
            email: User email
            username: Username
            password: Plain text password
            **kwargs: Additional user data

        Returns:
            User creation result
        """
        # Validate input
        if not email or not username or not password:
            return {"success": False, "error": "Email, username, and password are required"}

        if len(password) < 8:
            return {"success": False, "error": "Password must be at least 8 characters long"}

        # Check if user already exists
        result = await self.db.execute(
            self.db.query(User).filter(
                (User.email == email.lower()) | (User.username == username)
            )
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            if existing_user.email == email.lower():
                return {"success": False, "error": "Email already registered"}
            else:
                return {"success": False, "error": "Username already taken"}

        try:
            # Create new user
            hashed_password = self.hash_password(password)

            user = User(
                email=email.lower(),
                username=username,
                hashed_password=hashed_password,
                full_name=kwargs.get('full_name', ''),
                is_active=True,
                is_verified=False,
                credits=50.0,  # Welcome bonus credits
                subscription_tier='free'
            )

            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)

            # Generate verification token
            verification_token = secrets.token_urlsafe(32)
            user.verification_token = verification_token
            user.verification_token_expires = datetime.utcnow() + timedelta(hours=settings.email_verification_token_expiry_hours)
            await self.db.commit()

            # TODO: Send verification email

            return {
                "success": True,
                "user": user.to_dict(),
                "message": "User registered successfully. Please check your email for verification.",
                "verification_token": verification_token  # For development
            }

        except Exception as e:
            await self.db.rollback()
            return {"success": False, "error": f"Registration failed: {str(e)}"}

    async def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate user with email and password.

        Returns user data and tokens if successful, None if failed.
        """
        result = await self.db.execute(
            self.db.query(User).filter(User.email == email.lower())
        )
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            return None

        if not self.verify_password(password, user.hashed_password):
            return None

        # Update last login
        user.last_login = datetime.utcnow()
        await self.db.commit()

        # Generate tokens
        token_data = {"sub": str(user.id), "email": user.email, "username": user.username}
        access_token = self.create_access_token(token_data)
        refresh_token = self.create_refresh_token(token_data)

        return {
            "user": user.to_dict(),
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.jwt_expiration_hours * 60 * 60  # seconds
        }

    async def refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """Refresh access token using refresh token."""
        payload = self.verify_token(refresh_token)

        if not payload or payload.get("type") != "refresh":
            return None

        user_id = payload.get("sub")
        result = await self.db.execute(
            self.db.query(User).filter(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            return None

        # Generate new access token
        token_data = {"sub": str(user.id), "email": user.email, "username": user.username}
        new_access_token = self.create_access_token(token_data)

        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": settings.jwt_expiration_hours * 60 * 60
        }

    async def get_current_user(self, token: str) -> Optional[User]:
        """Get current user from JWT token."""
        payload = self.verify_token(token)

        if not payload or payload.get("type") != "access":
            return None

        user_id = payload.get("sub")
        result = await self.db.execute(
            self.db.query(User).filter(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            return None

        return user

    async def initiate_password_reset(self, email: str) -> Dict[str, Any]:
        """Initiate password reset process."""
        result = await self.db.execute(
            self.db.query(User).filter(User.email == email.lower())
        )
        user = result.scalar_one_or_none()

        if not user:
            # Don't reveal if email exists for security
            return {"success": True, "message": "If the email exists, a reset link has been sent."}

        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        user.reset_token = reset_token
        user.reset_token_expires = datetime.utcnow() + timedelta(hours=settings.password_reset_token_expiry_hours)

        await self.db.commit()

        # TODO: Send password reset email

        return {
            "success": True,
            "message": "Password reset link sent to your email.",
            "reset_token": reset_token  # For development
        }

    def reset_password(self, token: str, new_password: str) -> Dict[str, Any]:
        """Reset password using reset token."""
        if len(new_password) < 8:
            return {"success": False, "error": "Password must be at least 8 characters long"}

        user = self.db.query(User).filter(
            User.reset_token == token,
            User.reset_token_expires > datetime.utcnow()
        ).first()

        if not user:
            return {"success": False, "error": "Invalid or expired reset token"}

        # Update password
        user.hashed_password = self.hash_password(new_password)
        user.reset_token = None
        user.reset_token_expires = None
        self.db.commit()

        return {"success": True, "message": "Password reset successfully"}

    def verify_email(self, token: str) -> Dict[str, Any]:
        """Verify user email using verification token."""
        user = self.db.query(User).filter(
            User.verification_token == token,
            User.verification_token_expires > datetime.utcnow()
        ).first()

        if not user:
            return {"success": False, "error": "Invalid or expired verification token"}

        user.is_verified = True
        user.verification_token = None
        user.verification_token_expires = None
        self.db.commit()

        return {"success": True, "message": "Email verified successfully"}

    def update_user_profile(self, user_id: int, **updates) -> Dict[str, Any]:
        """Update user profile information."""
        user = self.db.query(User).filter(User.id == user_id).first()

        if not user:
            return {"success": False, "error": "User not found"}

        # Allowed fields for update
        allowed_fields = ['full_name', 'bio', 'website', 'avatar_url']

        for field, value in updates.items():
            if field in allowed_fields:
                setattr(user, field, value)

        user.updated_at = datetime.utcnow()
        self.db.commit()

        return {"success": True, "user": user.to_dict()}

    def change_password(self, user_id: int, current_password: str, new_password: str) -> Dict[str, Any]:
        """Change user password."""
        user = self.db.query(User).filter(User.id == user_id).first()

        if not user:
            return {"success": False, "error": "User not found"}

        if not self.verify_password(current_password, user.hashed_password):
            return {"success": False, "error": "Current password is incorrect"}

        if len(new_password) < 8:
            return {"success": False, "error": "New password must be at least 8 characters long"}

        user.hashed_password = self.hash_password(new_password)
        user.updated_at = datetime.utcnow()
        self.db.commit()

        return {"success": True, "message": "Password changed successfully"}

    def deactivate_account(self, user_id: int, password: str) -> Dict[str, Any]:
        """Deactivate user account."""
        user = self.db.query(User).filter(User.id == user_id).first()

        if not user:
            return {"success": False, "error": "User not found"}

        if not self.verify_password(password, user.hashed_password):
            return {"success": False, "error": "Password is incorrect"}

        user.is_active = False
        user.updated_at = datetime.utcnow()
        self.db.commit()

        return {"success": True, "message": "Account deactivated successfully"}

    def get_user_stats(self) -> Dict[str, Any]:
        """Get authentication statistics."""
        total_users = self.db.query(User).count()
        active_users = self.db.query(User).filter(User.is_active == True).count()
        verified_users = self.db.query(User).filter(User.is_verified == True).count()

        # Recent registrations (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_registrations = self.db.query(User).filter(
            User.created_at >= thirty_days_ago
        ).count()

        return {
            "total_users": total_users,
            "active_users": active_users,
            "verified_users": verified_users,
            "unverified_users": total_users - verified_users,
            "recent_registrations": recent_registrations,
            "verification_rate": (verified_users / total_users * 100) if total_users > 0 else 0
        }


# Global auth service instance
def get_auth_service(db) -> AuthService:
    """Get authentication service instance."""
    return AuthService(db)
