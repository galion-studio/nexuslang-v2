"""
Authentication Core Module
Complete JWT authentication system with password hashing, token management, and security features.

Features:
- Password hashing with bcrypt
- JWT token generation and validation
- Token refresh mechanism
- Token blacklisting for logout
- Role-based access control
- Security best practices
"""

from datetime import datetime, timedelta
from typing import Optional, Dict
from passlib.context import CryptContext
from jose import JWTError, jwt
import os
import redis
from fastapi import HTTPException, status

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET", "2xR7kP9mL4vN8qT3wH6yJ1zB5cfP0sG2dA9xK4pM7rL3vN8qW1tY6hJ5bC0fZ2sG")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
REFRESH_TOKEN_EXPIRE_DAYS = 7  # 7 days

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Redis client for token blacklist
try:
    redis_client = redis.Redis(
        host='localhost',
        port=6379,
        db=0,
        decode_responses=True,
        password=os.getenv("REDIS_PASSWORD", "7aHZpW9xR4mN8qL3vK6jT1yB5cZ0fG2s")
    )
    redis_client.ping()
except:
    # Fallback: no password
    try:
        redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        redis_client.ping()
    except:
        redis_client = None  # Redis unavailable


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
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
        hashed_password: Hashed password from database
    
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary containing claims (e.g., {"sub": "user@example.com"})
        expires_delta: Optional custom expiration time
    
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    Create a JWT refresh token with longer expiration.
    
    Args:
        data: Dictionary containing claims
    
    Returns:
        Encoded JWT refresh token string
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[Dict]:
    """
    Decode and validate a JWT token.
    
    Args:
        token: JWT token string
    
    Returns:
        Dictionary containing token payload if valid, None otherwise
    
    Raises:
        HTTPException: If token is invalid, expired, or blacklisted
    """
    try:
        # Check if token is blacklisted
        if is_token_blacklisted(token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Decode token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def blacklist_token(token: str, expires_in: int = None):
    """
    Add a token to the blacklist (for logout).
    
    Args:
        token: JWT token to blacklist
        expires_in: Optional expiration time in seconds (defaults to token expiry)
    """
    if redis_client is None:
        # Redis unavailable, log warning
        print("Warning: Redis unavailable, token blacklisting disabled")
        return
    
    try:
        # Decode token to get expiration
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp = payload.get("exp")
        
        if exp:
            # Calculate TTL (time until token expires)
            now = datetime.utcnow().timestamp()
            ttl = int(exp - now)
            
            if ttl > 0:
                # Store token hash in Redis with TTL
                redis_client.setex(
                    f"blacklist:{token}",
                    ttl,
                    "1"
                )
    except Exception as e:
        print(f"Error blacklisting token: {e}")


def is_token_blacklisted(token: str) -> bool:
    """
    Check if a token is blacklisted.
    
    Args:
        token: JWT token to check
    
    Returns:
        True if blacklisted, False otherwise
    """
    if redis_client is None:
        return False
    
    try:
        return redis_client.exists(f"blacklist:{token}") > 0
    except:
        return False


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password strength according to security requirements.
    
    Requirements:
    - At least 12 characters
    - Contains uppercase letter
    - Contains lowercase letter
    - Contains digit
    - Contains special character
    
    Args:
        password: Password to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < 12:
        return False, "Password must be at least 12 characters long"
    
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"
    
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        return False, "Password must contain at least one special character"
    
    return True, ""


def create_token_pair(user_data: dict) -> dict:
    """
    Create both access and refresh tokens for a user.
    
    Args:
        user_data: Dictionary containing user information (must include 'sub' key)
    
    Returns:
        Dictionary with access_token and refresh_token
    """
    access_token = create_access_token(user_data)
    refresh_token = create_refresh_token(user_data)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60  # seconds
    }


# Admin email configuration (from PROJECT_STATE_COMPLETE.md)
ADMIN_EMAILS = [
    "maci.grajczyk@gmail.com",
    "polskitygrys111@gmail.com",
    "frxdel@gmail.com",
    "legalizacija420@gmail.com",
    "info@galion.studio"
]


def is_admin_email(email: str) -> bool:
    """
    Check if an email belongs to an admin.
    
    Args:
        email: Email address to check
    
    Returns:
        True if email is in admin list, False otherwise
    """
    return email.lower() in [e.lower() for e in ADMIN_EMAILS]

