"""
Two-Factor Authentication (2FA) API endpoints.
Implements GitHub-style TOTP authentication with backup codes.

Endpoints:
- POST /setup - Initiate 2FA setup (get QR code)
- POST /verify - Verify and enable 2FA
- POST /disable - Disable 2FA
- GET /status - Check 2FA status
- POST /backup-codes/regenerate - Generate new backup codes
- POST /validate - Validate 2FA code during login
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from app.database import get_db
from app.models.user import User
from app.schemas.twofa import (
    TwoFASetupResponse,
    TwoFAVerifyRequest,
    TwoFADisableRequest,
    TwoFAStatusResponse,
    BackupCodesResponse,
    TwoFALoginRequest
)
from app.services.twofa import (
    generate_totp_secret,
    generate_qr_code,
    verify_totp_code,
    generate_backup_codes,
    hash_backup_code,
    verify_backup_code
)
from app.services.auth import verify_password
from app.dependencies import get_current_user

router = APIRouter()


@router.post("/setup", response_model=dict)
async def setup_2fa(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Initiate 2FA setup for the authenticated user.
    
    This generates a TOTP secret and QR code that the user can scan
    with their authenticator app (Google Authenticator, Authy, etc.).
    
    Also generates backup codes for account recovery.
    
    Steps:
    1. Generate TOTP secret
    2. Generate QR code
    3. Generate backup codes
    4. Store secret temporarily (not enabled until verified)
    5. Return QR code and backup codes to user
    
    Returns:
        Secret, QR code, and backup codes
        
    Note: 2FA is not enabled until user verifies with /verify endpoint
    """
    
    # Check if 2FA is already enabled
    if current_user.totp_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is already enabled. Disable it first to set up again."
        )
    
    # Generate TOTP secret
    secret = generate_totp_secret()
    
    # Generate QR code
    qr_code = generate_qr_code(
        email=current_user.email,
        secret=secret,
        issuer="Nexus"
    )
    
    # Generate backup codes
    backup_codes = generate_backup_codes(count=10)
    hashed_codes = [hash_backup_code(code) for code in backup_codes]
    
    # Store secret and hashed backup codes (but don't enable yet)
    current_user.totp_secret = secret
    current_user.backup_codes = hashed_codes
    current_user.backup_codes_generated_at = datetime.utcnow()
    current_user.totp_enabled = False  # Not enabled until verified
    
    db.commit()
    
    return {
        "success": True,
        "data": {
            "secret": secret,
            "qr_code": qr_code,
            "backup_codes": backup_codes,
            "message": "Scan the QR code with your authenticator app, then verify with a code"
        }
    }


@router.post("/verify", response_model=dict)
async def verify_and_enable_2fa(
    verify_data: TwoFAVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verify TOTP code and enable 2FA.
    
    User must provide a valid TOTP code from their authenticator app
    to prove they've set it up correctly.
    
    Args:
        code: 6-digit TOTP code from authenticator app
        
    Returns:
        Success confirmation
        
    Raises:
        400: If no setup in progress or invalid code
    """
    
    # Check if setup was initiated
    if not current_user.totp_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No 2FA setup in progress. Call /setup first."
        )
    
    # Check if already enabled
    if current_user.totp_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is already enabled"
        )
    
    # Verify the TOTP code
    if not verify_totp_code(current_user.totp_secret, verify_data.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code"
        )
    
    # Enable 2FA
    current_user.totp_enabled = True
    current_user.totp_verified_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "success": True,
        "data": {
            "message": "Two-factor authentication enabled successfully",
            "enabled": True
        }
    }


@router.post("/disable", response_model=dict)
async def disable_2fa(
    disable_data: TwoFADisableRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Disable 2FA for the authenticated user.
    
    Requires current password and valid TOTP code for security.
    This is a sensitive operation that removes account protection.
    
    Args:
        password: User's current password
        code: Current valid TOTP code
        
    Returns:
        Success confirmation
        
    Raises:
        400: If 2FA not enabled
        401: If password or code is invalid
    """
    
    # Check if 2FA is enabled
    if not current_user.totp_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is not enabled"
        )
    
    # Verify password
    if not verify_password(disable_data.password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    
    # Verify TOTP code
    if not verify_totp_code(current_user.totp_secret, disable_data.code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid verification code"
        )
    
    # Disable 2FA and clear secrets
    current_user.totp_enabled = False
    current_user.totp_secret = None
    current_user.totp_verified_at = None
    current_user.backup_codes = []
    current_user.backup_codes_generated_at = None
    
    db.commit()
    
    return {
        "success": True,
        "data": {
            "message": "Two-factor authentication disabled successfully",
            "enabled": False
        }
    }


@router.get("/status", response_model=dict)
async def get_2fa_status(
    current_user: User = Depends(get_current_user)
):
    """
    Get current 2FA status for authenticated user.
    
    Returns information about whether 2FA is enabled and
    how many backup codes remain.
    
    Returns:
        2FA status information
    """
    
    # Count remaining backup codes
    backup_codes_count = len(current_user.backup_codes) if current_user.backup_codes else 0
    
    return {
        "success": True,
        "data": {
            "enabled": current_user.totp_enabled,
            "verified_at": current_user.totp_verified_at,
            "backup_codes_count": backup_codes_count
        }
    }


@router.post("/backup-codes/regenerate", response_model=dict)
async def regenerate_backup_codes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Regenerate backup/recovery codes.
    
    This invalidates all previous backup codes and generates new ones.
    User should save these in a secure location.
    
    Returns:
        New backup codes
        
    Raises:
        400: If 2FA not enabled
    """
    
    # Check if 2FA is enabled
    if not current_user.totp_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is not enabled"
        )
    
    # Generate new backup codes
    backup_codes = generate_backup_codes(count=10)
    hashed_codes = [hash_backup_code(code) for code in backup_codes]
    
    # Store new hashed codes
    current_user.backup_codes = hashed_codes
    current_user.backup_codes_generated_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "success": True,
        "data": {
            "backup_codes": backup_codes,
            "generated_at": current_user.backup_codes_generated_at,
            "message": "Save these codes in a secure location. Each can only be used once."
        }
    }


@router.post("/validate", response_model=dict)
async def validate_2fa_code(
    validate_data: TwoFALoginRequest,
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Validate 2FA code during login process.
    
    This endpoint is called after successful username/password login
    when the user has 2FA enabled. It validates the TOTP code or backup code.
    
    Args:
        code: 6-digit TOTP code or backup code
        user_id: User ID (from initial login response)
        
    Returns:
        Validation result
        
    Raises:
        401: If code is invalid
        
    Note: This endpoint is typically used internally by the login flow
    """
    
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.totp_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid request"
        )
    
    code = validate_data.code
    
    # Try TOTP code first
    if verify_totp_code(user.totp_secret, code):
        return {
            "success": True,
            "data": {
                "valid": True,
                "method": "totp"
            }
        }
    
    # Try backup code
    is_valid, matched_hash = verify_backup_code(code, user.backup_codes or [])
    if is_valid:
        # Remove used backup code
        user.backup_codes = [h for h in user.backup_codes if h != matched_hash]
        db.commit()
        
        return {
            "success": True,
            "data": {
                "valid": True,
                "method": "backup_code",
                "remaining_backup_codes": len(user.backup_codes)
            }
        }
    
    # Invalid code
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid verification code"
    )


