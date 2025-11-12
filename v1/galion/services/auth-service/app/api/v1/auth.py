"""
Authentication endpoints (register, login, token refresh).
These are the public-facing APIs for user authentication.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid
import secrets
from typing import Dict, Optional

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.services.auth import hash_password, create_access_token, verify_password
from app.services.twofa import verify_totp_code, verify_backup_code
from app.events import publish_user_registered, publish_user_login

router = APIRouter()

# In-memory storage for QR sessions (use Redis in production)
# Structure: {session_id: {"created_at": datetime, "authenticated": bool, "user_id": str, "expires_at": datetime}}
qr_sessions: Dict[str, dict] = {}


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, request: Request, db: Session = Depends(get_db)):
    """
    Register a new user account.
    
    Process:
    1. Validate input (Pydantic does this automatically)
    2. Check if email already exists
    3. Hash the password (never store plain passwords!)
    4. Create user in database
    5. Return success response
    
    Args:
        user_data: User registration data (email, password, name)
        db: Database session (injected by FastAPI)
        
    Returns:
        Success response with user data (without password)
        
    Raises:
        400 Bad Request: If email already registered
    """
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user with hashed password
    new_user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        name=user_data.name,
        date_of_birth=user_data.date_of_birth,
        age_verified=True,  # Auto-verified during registration
        age_verified_at=datetime.utcnow(),
        role="user",  # Default role
        status="active",
        badge_name="Explorer",  # Free tier badge
        subscription_status="free"
    )
    
    # Save to database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # Get the generated ID and timestamps
    
    # Publish user registration event for analytics
    publish_user_registered(
        user_id=str(new_user.id),
        email=new_user.email,
        name=new_user.name
    )
    
    # Return success response (never include password!)
    return {
        "success": True,
        "data": {
            "user": UserResponse.model_validate(new_user),
            "message": "Registration successful"
        }
    }


@router.post("/login")
async def login(login_data: UserLogin, request: Request, db: Session = Depends(get_db)):
    """
    Login user and return JWT token.
    
    Process:
    1. Find user by email
    2. Verify password hash
    3. Check account status
    4. Check if 2FA is enabled
    5. If 2FA enabled: Return requires_2fa response
    6. If no 2FA: Create JWT token and return
    7. Update last_login_at
    8. Return token and user data
    
    Args:
        email: User's email
        password: User's password (plain text, over HTTPS)
        db: Database session
        
    Returns:
        JWT token, expiration, and user data
        OR requires_2fa flag with user_id for 2FA flow
        
    Raises:
        401 Unauthorized: Invalid credentials
        403 Forbidden: Account suspended or locked
    """
    
    # Find user by email
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Verify password
    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Check account status
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account is {user.status}"
        )
    
    # Check if 2FA is enabled - GitHub-style flow
    if user.totp_enabled:
        return {
            "success": True,
            "data": {
                "requires_2fa": True,
                "user_id": str(user.id),
                "message": "Please provide your 2FA code"
            }
        }
    
    # No 2FA - create JWT token and complete login
    token_data = create_access_token(user.id, user.email, user.role)
    
    # Update last login timestamp
    user.last_login_at = datetime.utcnow()
    db.commit()
    
    # Publish login event for analytics
    publish_user_login(
        user_id=str(user.id),
        email=user.email,
        ip_address=request.client.host if request.client else None
    )
    
    return {
        "success": True,
        "data": {
            "token": token_data["token"],
            "expires_in": token_data["expires_in"],
            "user": UserResponse.model_validate(user)
        }
    }


@router.post("/login/2fa")
async def login_with_2fa(
    user_id: str,
    code: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Complete login with 2FA code.
    
    This endpoint is called after the initial login when 2FA is required.
    User provides the 6-digit TOTP code or a backup code.
    
    Process:
    1. Verify user_id and that 2FA is enabled
    2. Validate TOTP code or backup code
    3. Create JWT token
    4. Update last_login_at
    5. Return token and user data
    
    Args:
        user_id: User ID from initial login response
        code: 6-digit TOTP code or backup code
        request: Request object for IP logging
        db: Database session
        
    Returns:
        JWT token, expiration, and user data
        
    Raises:
        400: If 2FA not enabled for user
        401: If code is invalid
    """
    
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid request"
        )
    
    # Check if 2FA is enabled
    if not user.totp_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is not enabled for this user"
        )
    
    # Check account status
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account is {user.status}"
        )
    
    # Try TOTP code first
    is_valid = False
    used_backup = False
    
    if verify_totp_code(user.totp_secret, code):
        is_valid = True
    else:
        # Try backup code
        backup_valid, matched_hash = verify_backup_code(code, user.backup_codes or [])
        if backup_valid:
            is_valid = True
            used_backup = True
            # Remove used backup code
            user.backup_codes = [h for h in user.backup_codes if h != matched_hash]
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid verification code"
        )
    
    # Create JWT token
    token_data = create_access_token(user.id, user.email, user.role)
    
    # Update last login timestamp
    user.last_login_at = datetime.utcnow()
    db.commit()
    
    # Publish login event for analytics
    publish_user_login(
        user_id=str(user.id),
        email=user.email,
        ip_address=request.client.host if request.client else None
    )
    
    response_data = {
        "token": token_data["token"],
        "expires_in": token_data["expires_in"],
        "user": UserResponse.model_validate(user)
    }
    
    # Warn if backup code was used and running low
    if used_backup:
        remaining = len(user.backup_codes)
        response_data["warning"] = f"Backup code used. {remaining} codes remaining."
        if remaining <= 2:
            response_data["warning"] += " Consider regenerating backup codes."
    
    return {
        "success": True,
        "data": response_data
    }


@router.post("/qr/create")
async def create_qr_session():
    """
    Create a new QR code login session.
    
    This endpoint generates a unique session ID that will be embedded in the QR code.
    The QR code is displayed on the web login page, and when scanned by a mobile app,
    it initiates the authentication flow.
    
    Returns:
        session_id: Unique identifier for this QR login session
        qr_data: Data to encode in the QR code (URL with session_id)
        expires_in: Session expiration time in seconds
    """
    # Generate unique session ID
    session_id = str(uuid.uuid4())
    
    # Create session with 5-minute expiration
    expires_at = datetime.utcnow() + timedelta(minutes=5)
    qr_sessions[session_id] = {
        "created_at": datetime.utcnow(),
        "expires_at": expires_at,
        "authenticated": False,
        "user_id": None,
        "token": None,
        "user_data": None
    }
    
    # Clean up expired sessions (simple cleanup)
    _cleanup_expired_sessions()
    
    return {
        "success": True,
        "data": {
            "session_id": session_id,
            "qr_data": f"galion://qr-login?session={session_id}",
            "expires_in": 300  # 5 minutes
        }
    }


@router.get("/qr/status/{session_id}")
async def check_qr_session_status(session_id: str):
    """
    Check the status of a QR login session.
    
    This endpoint is polled by the web browser to check if the user has
    scanned and authenticated via the mobile app.
    
    Args:
        session_id: The QR session ID
        
    Returns:
        authenticated: Boolean indicating if authentication is complete
        user: User data if authenticated
        access_token: JWT token if authenticated
        
    Raises:
        404: If session not found or expired
    """
    # Check if session exists
    session = qr_sessions.get(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or expired"
        )
    
    # Check if session expired
    if session["expires_at"] < datetime.utcnow():
        del qr_sessions[session_id]
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session expired"
        )
    
    # Return session status
    if session["authenticated"]:
        return {
            "success": True,
            "data": {
                "authenticated": True,
                "user": session["user_data"],
                "access_token": session["token"]
            }
        }
    else:
        return {
            "success": True,
            "data": {
                "authenticated": False
            }
        }


@router.post("/qr/verify")
async def verify_qr_session(
    session_id: str,
    token: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Verify and authenticate a QR login session.
    
    This endpoint is called by the mobile app after the user scans the QR code
    and confirms the login. The mobile app sends its authentication token
    to verify the user's identity.
    
    Args:
        session_id: The QR session ID from the scanned QR code
        token: The user's existing authentication token from mobile app
        request: Request object for IP logging
        db: Database session
        
    Returns:
        success: Boolean indicating if verification was successful
        
    Raises:
        404: If session not found or expired
        401: If token is invalid
    """
    # Check if session exists
    session = qr_sessions.get(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or expired"
        )
    
    # Check if session expired
    if session["expires_at"] < datetime.utcnow():
        del qr_sessions[session_id]
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session expired"
        )
    
    # Verify the user's token (simplified - in production, use proper JWT verification)
    # For now, we'll accept the token as a user identifier
    # In a real implementation, you would:
    # 1. Decode and verify the JWT token
    # 2. Extract user_id from token
    # 3. Load user from database
    
    # For demonstration, we'll create a simple token validation
    # You should implement proper JWT verification here
    try:
        # This is a placeholder - implement proper token verification
        # For now, treat token as user_id (for testing purposes)
        user = db.query(User).filter(User.id == token).first()
        if not user:
            # Try to find by a simple pattern
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )
    
    # Create new JWT token for web session
    token_data = create_access_token(user.id, user.email, user.role)
    
    # Update last login timestamp
    user.last_login_at = datetime.utcnow()
    db.commit()
    
    # Update session with authentication data
    qr_sessions[session_id].update({
        "authenticated": True,
        "user_id": str(user.id),
        "token": token_data["token"],
        "user_data": UserResponse.model_validate(user).model_dump()
    })
    
    # Publish login event for analytics
    publish_user_login(
        user_id=str(user.id),
        email=user.email,
        ip_address=request.client.host if request.client else None
    )
    
    return {
        "success": True,
        "data": {
            "message": "QR login verified successfully"
        }
    }


def _cleanup_expired_sessions():
    """Remove expired QR sessions from memory."""
    now = datetime.utcnow()
    expired = [sid for sid, session in qr_sessions.items() if session["expires_at"] < now]
    for sid in expired:
        del qr_sessions[sid]

