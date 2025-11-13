"""
Security utilities for authentication and authorization.
Handles password hashing, JWT tokens, and user verification.
"""

from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
import os
import sys

# Password hashing context using bcrypt for secure password storage
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
# SECURITY: No fallbacks! Fail fast if secrets are missing.
from .config import settings

SECRET_KEY = os.getenv("JWT_SECRET")

# CRITICAL: Fail fast if JWT_SECRET is not set or is weak
if not SECRET_KEY:
    print("❌ CRITICAL ERROR: JWT_SECRET environment variable is not set!")
    print("   This is required for security. Generate with: openssl rand -hex 64")
    print("   Exiting to prevent insecure operation...")
    sys.exit(1)

if SECRET_KEY == "jwt-secret-key-for-development" or SECRET_KEY == "change-me-in-production":
    print("❌ CRITICAL ERROR: JWT_SECRET is set to a default/placeholder value!")
    print("   This is a security vulnerability. Generate a secure secret:")
    print("   openssl rand -hex 64")
    print("   Exiting to prevent insecure operation...")
    sys.exit(1)

if len(SECRET_KEY) < 32:
    print("❌ CRITICAL ERROR: JWT_SECRET is too short (must be at least 32 characters)!")
    print("   Generate a secure secret: openssl rand -hex 64")
    print("   Exiting to prevent insecure operation...")
    sys.exit(1)

print("✅ JWT_SECRET validated - secure key in use")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 24 * 60  # 24 hours

# Token blacklist for logout (using in-memory set for now, should use Redis in production)
_token_blacklist = set()


def hash_password(password: str) -> str:
    """
    Hash a password for secure storage.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password string
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Stored password hash
        
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Data to encode in the token (typically user_id, email)
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and verify a JWT access token.
    Checks both validity and blacklist status.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token data if valid, None if invalid/expired/blacklisted
    """
    try:
        # Check if token is blacklisted (logged out)
        if token in _token_blacklist:
            return None
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def blacklist_token(token: str) -> None:
    """
    Blacklist a token (for logout functionality).
    In production, use Redis with TTL matching token expiry.
    
    Args:
        token: JWT token to blacklist
    """
    _token_blacklist.add(token)


def validate_password_strength(password: str) -> tuple[bool, Optional[str]]:
    """
    Validate password meets STRONG security requirements.
    
    Updated requirements (2025 security standards):
    - Minimum 12 characters (increased from 8)
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    - No common passwords (basic check)
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Length check - minimum 12 characters for modern security
    if len(password) < 12:
        return False, "Password must be at least 12 characters long"
    
    # Character diversity checks
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"
    
    # Special character requirement
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        return False, f"Password must contain at least one special character ({special_chars})"
    
    # Check against common weak passwords
    common_weak_passwords = [
        "password", "123456", "qwerty", "admin", "letmein",
        "welcome", "monkey", "dragon", "master", "sunshine",
        "password123", "admin123", "welcome123"
    ]
    if password.lower() in common_weak_passwords:
        return False, "This password is too common. Please choose a stronger password"
    
    return True, None


def validate_username(username: str) -> tuple[bool, Optional[str]]:
    """
    Validate username meets requirements.
    
    Args:
        username: Username to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    
    if len(username) > 50:
        return False, "Username must be at most 50 characters long"
    
    if not username.replace('_', '').replace('-', '').isalnum():
        return False, "Username can only contain letters, numbers, hyphens, and underscores"
    
    return True, None

