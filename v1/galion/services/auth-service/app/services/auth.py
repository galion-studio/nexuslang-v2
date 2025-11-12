"""
Authentication service with password hashing and JWT token management.
This is the core security module for user authentication.
"""

from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Optional
import uuid

from app.config import settings

# Password hashing context using PBKDF2-SHA256
# Using PBKDF2 instead of bcrypt to avoid C extension initialization issues
# PBKDF2 is NIST-approved and used by Django, very secure
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto",
    pbkdf2_sha256__default_rounds=260000  # OWASP recommended minimum
)


def hash_password(password: str) -> str:
    """
    Hash a password using PBKDF2-SHA256.
    
    PBKDF2 is intentionally slow to make brute force attacks impractical.
    260,000 rounds = ~300ms on modern hardware (OWASP recommended).
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password string (safe to store in database)
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its PBKDF2 hash.
    
    This is constant-time comparison to prevent timing attacks.
    
    Args:
        plain_password: Password to check
        hashed_password: Stored hash from database
        
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: str, email: str, role: str) -> dict:
    """
    Create a JWT access token for authenticated user.
    
    JWT structure:
    - Header: Algorithm and token type
    - Payload: User data and expiration
    - Signature: Ensures token hasn't been tampered with
    
    Args:
        user_id: User's unique identifier
        email: User's email
        role: User's role (for authorization)
        
    Returns:
        Dict with token, expiration time, and expires_at timestamp
    """
    expires_at = datetime.utcnow() + timedelta(seconds=settings.JWT_EXPIRATION_SECONDS)
    
    # JWT payload - keep it small (transmitted with every request)
    payload = {
        "user_id": str(user_id),
        "email": email,
        "role": role,
        "exp": expires_at,  # Expiration time
        "iat": datetime.utcnow(),  # Issued at
        "jti": str(uuid.uuid4())  # JWT ID for tracking/revocation
    }
    
    # Encode the payload with our secret key
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    return {
        "token": token,
        "expires_in": settings.JWT_EXPIRATION_SECONDS,
        "expires_at": expires_at
    }


def verify_token(token: str) -> Optional[dict]:
    """
    Verify and decode a JWT token.
    
    This checks:
    1. Token signature is valid (not tampered with)
    2. Token hasn't expired
    3. Token was issued by us (our secret key)
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded payload if valid, None if invalid or expired
    """
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        # Token is invalid, expired, or tampered with
        return None

