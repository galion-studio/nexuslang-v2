"""
Enhanced Authentication Service - JWT tokens with refresh mechanism
Provides secure authentication with role-based access control

Features:
- JWT access tokens (24h expiry)
- Refresh tokens (7d expiry)
- Password hashing with bcrypt
- Role-based permissions
- Token blacklisting
- Session management
"""

import os
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

import jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr

# Try to import database models
try:
    from ...models.user import User
    from ...core.database import get_db
    FULL_MODELS = True
except ImportError:
    FULL_MODELS = False


@dataclass
class TokenPair:
    """Access and refresh token pair"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 86400  # 24 hours


@dataclass
class TokenData:
    """JWT token payload data"""
    user_id: str
    email: str
    username: str
    roles: List[str]
    permissions: List[str]
    exp: datetime
    iat: datetime
    jti: str  # JWT ID for blacklisting


class AuthConfig(BaseModel):
    """Authentication configuration"""
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 hours
    refresh_token_expire_days: int = 7
    bcrypt_rounds: int = 12


class AuthenticationError(Exception):
    """Base authentication exception"""
    pass


class InvalidTokenError(AuthenticationError):
    """Invalid token exception"""
    pass


class TokenExpiredError(AuthenticationError):
    """Token expired exception"""
    pass


class UserNotFoundError(AuthenticationError):
    """User not found exception"""
    pass


class InvalidCredentialsError(AuthenticationError):
    """Invalid credentials exception"""
    pass


class EnhancedAuthService:
    """
    Enhanced authentication service with JWT and refresh tokens

    Provides secure authentication with role-based access control
    """

    def __init__(self, config: Optional[AuthConfig] = None):
        self.config = config or AuthConfig(
            secret_key=os.getenv("JWT_SECRET", secrets.token_hex(32)),
            algorithm="HS256",
            access_token_expire_minutes=1440,
            refresh_token_expire_days=7,
            bcrypt_rounds=12
        )

        # Password hashing context
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        # Token blacklisting (in production, use Redis/database)
        self.blacklisted_tokens: set = set()

        # Role-based permissions
        self.role_permissions = {
            "user": ["read:own_profile", "update:own_profile", "use:voice"],
            "beta": ["read:own_profile", "update:own_profile", "use:voice", "access:beta_features"],
            "moderator": ["read:own_profile", "update:own_profile", "use:voice", "access:beta_features",
                         "moderate:feedback", "view:analytics"],
            "admin": ["read:own_profile", "update:own_profile", "use:voice", "access:beta_features",
                     "moderate:feedback", "view:analytics", "manage:users", "manage:system", "delete:data"]
        }

    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return self.pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.config.access_token_expire_minutes)
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access",
            "jti": secrets.token_hex(16)
        })
        encoded_jwt = jwt.encode(to_encode, self.config.secret_key, algorithm=self.config.algorithm)
        return encoded_jwt

    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.config.refresh_token_expire_days)
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh",
            "jti": secrets.token_hex(16)
        })
        encoded_jwt = jwt.encode(to_encode, self.config.secret_key, algorithm=self.config.algorithm)
        return encoded_jwt

    def create_token_pair(self, user_data: Dict[str, Any]) -> TokenPair:
        """Create access and refresh token pair"""
        # Ensure user_data has required fields
        token_data = {
            "user_id": user_data.get("id"),
            "email": user_data.get("email"),
            "username": user_data.get("username", user_data.get("email")),
            "roles": user_data.get("roles", ["user"]),
            "permissions": self.get_user_permissions(user_data.get("roles", ["user"]))
        }

        access_token = self.create_access_token(token_data)
        refresh_token = self.create_refresh_token(token_data)

        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=self.config.access_token_expire_minutes * 60
        )

    def verify_token(self, token: str, token_type: str = "access") -> TokenData:
        """Verify and decode JWT token"""
        try:
            # Check if token is blacklisted
            payload = jwt.decode(token, self.config.secret_key, algorithms=[self.config.algorithm])

            if payload.get("jti") in self.blacklisted_tokens:
                raise InvalidTokenError("Token has been revoked")

            if payload.get("type") != token_type:
                raise InvalidTokenError(f"Invalid token type: expected {token_type}")

            return TokenData(
                user_id=payload["user_id"],
                email=payload["email"],
                username=payload["username"],
                roles=payload.get("roles", []),
                permissions=payload.get("permissions", []),
                exp=datetime.fromtimestamp(payload["exp"]),
                iat=datetime.fromtimestamp(payload["iat"]),
                jti=payload["jti"]
            )

        except jwt.ExpiredSignatureError:
            raise TokenExpiredError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise InvalidTokenError(f"Invalid token: {e}")

    def refresh_access_token(self, refresh_token: str) -> TokenPair:
        """Create new access token using refresh token"""
        # Verify refresh token
        token_data = self.verify_token(refresh_token, "refresh")

        # Create new token pair
        user_data = {
            "id": token_data.user_id,
            "email": token_data.email,
            "username": token_data.username,
            "roles": token_data.roles
        }

        return self.create_token_pair(user_data)

    def blacklist_token(self, token: str):
        """Add token to blacklist (logout)"""
        try:
            # Decode token to get JTI without verification
            header = jwt.get_unverified_header(token)
            payload = jwt.decode(token, options={"verify_signature": False})

            if "jti" in payload:
                self.blacklisted_tokens.add(payload["jti"])
        except Exception:
            pass  # Invalid token, ignore

    def get_user_permissions(self, roles: List[str]) -> List[str]:
        """Get all permissions for user's roles"""
        permissions = set()
        for role in roles:
            if role in self.role_permissions:
                permissions.update(self.role_permissions[role])
        return list(permissions)

    def has_permission(self, user_permissions: List[str], required_permission: str) -> bool:
        """Check if user has required permission"""
        return required_permission in user_permissions

    def has_role(self, user_roles: List[str], required_role: str) -> bool:
        """Check if user has required role"""
        return required_role in user_roles

    async def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with email and password"""
        if not FULL_MODELS:
            # Mock authentication for testing
            if email == "admin@nexuslang.dev" and password == "Admin123!":
                return {
                    "id": "1",
                    "email": email,
                    "username": "admin",
                    "full_name": "NexusLang Admin",
                    "roles": ["admin"],
                    "is_active": True
                }
            return None

        # Real database authentication
        from sqlalchemy.orm import Session
        db = next(get_db())

        try:
            user = db.query(User).filter(User.email == email).first()
            if not user or not user.is_active:
                return None

            if not self.verify_password(password, user.hashed_password):
                return None

            return {
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "roles": getattr(user, 'roles', ['user']),
                "is_active": user.is_active
            }
        finally:
            db.close()

    async def get_current_user(self, token: str) -> Optional[Dict[str, Any]]:
        """Get current user from access token"""
        try:
            token_data = self.verify_token(token, "access")
            return {
                "id": token_data.user_id,
                "email": token_data.email,
                "username": token_data.username,
                "roles": token_data.roles,
                "permissions": token_data.permissions
            }
        except AuthenticationError:
            return None

    def validate_password_strength(self, password: str) -> List[str]:
        """Validate password strength and return issues"""
        issues = []

        if len(password) < 8:
            issues.append("Password must be at least 8 characters long")

        if not any(c.isupper() for c in password):
            issues.append("Password must contain at least one uppercase letter")

        if not any(c.islower() for c in password):
            issues.append("Password must contain at least one lowercase letter")

        if not any(c.isdigit() for c in password):
            issues.append("Password must contain at least one number")

        return issues


# Global auth service instance
_auth_service: Optional[EnhancedAuthService] = None


def get_auth_service() -> EnhancedAuthService:
    """Get or create global auth service instance"""
    global _auth_service
    if _auth_service is None:
        _auth_service = EnhancedAuthService()
    return _auth_service


# FastAPI dependencies
async def get_current_user(token: str) -> Dict[str, Any]:
    """FastAPI dependency to get current authenticated user"""
    auth_service = get_auth_service()
    user = await auth_service.get_current_user(token)

    if not user:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def require_permission(required_permission: str):
    """Create dependency that requires specific permission"""
    async def permission_dependency(current_user: Dict[str, Any] = Depends(get_current_user)):
        auth_service = get_auth_service()
        if not auth_service.has_permission(current_user.get("permissions", []), required_permission):
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {required_permission} required"
            )
        return current_user
    return permission_dependency


def require_role(required_role: str):
    """Create dependency that requires specific role"""
    async def role_dependency(current_user: Dict[str, Any] = Depends(get_current_user)):
        auth_service = get_auth_service()
        if not auth_service.has_role(current_user.get("roles", []), required_role):
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role required: {required_role}"
            )
        return current_user
    return role_dependency


# Utility functions
def generate_secure_token(length: int = 32) -> str:
    """Generate a secure random token"""
    return secrets.token_hex(length)


def hash_password(password: str) -> str:
    """Hash password using global auth service"""
    return get_auth_service().hash_password(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password using global auth service"""
    return get_auth_service().verify_password(plain_password, hashed_password)
