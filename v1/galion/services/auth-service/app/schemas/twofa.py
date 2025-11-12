"""
Pydantic schemas for Two-Factor Authentication (2FA).
These define the API contracts for 2FA operations.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class TwoFASetupResponse(BaseModel):
    """
    Response when initiating 2FA setup.
    Returns QR code and secret for authenticator app.
    """
    secret: str = Field(..., description="Base32 encoded TOTP secret")
    qr_code: str = Field(..., description="Base64 encoded QR code image")
    backup_codes: List[str] = Field(..., description="One-time backup codes for recovery")
    
    class Config:
        json_schema_extra = {
            "example": {
                "secret": "JBSWY3DPEHPK3PXP",
                "qr_code": "data:image/png;base64,iVBORw0KG...",
                "backup_codes": ["1234-5678", "9012-3456", "5678-9012"]
            }
        }


class TwoFAVerifyRequest(BaseModel):
    """
    Request to verify and enable 2FA.
    User must provide a valid TOTP code to activate.
    """
    code: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": "123456"
            }
        }


class TwoFALoginRequest(BaseModel):
    """
    Request to complete login with 2FA code.
    Used after initial username/password verification.
    """
    code: str = Field(..., min_length=6, max_length=6, description="6-digit TOTP code or backup code")
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": "123456"
            }
        }


class TwoFADisableRequest(BaseModel):
    """
    Request to disable 2FA.
    Requires current password for security.
    """
    password: str = Field(..., min_length=1)
    code: str = Field(..., min_length=6, max_length=6, description="Current TOTP code")
    
    class Config:
        json_schema_extra = {
            "example": {
                "password": "mySecurePassword123!",
                "code": "123456"
            }
        }


class TwoFAStatusResponse(BaseModel):
    """
    Response showing user's 2FA status.
    """
    enabled: bool
    verified_at: Optional[datetime] = None
    backup_codes_count: int = Field(default=0, description="Number of unused backup codes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "enabled": True,
                "verified_at": "2024-01-15T10:30:00Z",
                "backup_codes_count": 8
            }
        }


class BackupCodesResponse(BaseModel):
    """
    Response when regenerating backup codes.
    """
    backup_codes: List[str] = Field(..., description="New backup codes (save these!)")
    generated_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "backup_codes": ["1234-5678", "9012-3456", "5678-9012"],
                "generated_at": "2024-01-15T10:30:00Z"
            }
        }


