"""
Two-Factor Authentication (2FA) service.
Implements TOTP (Time-based One-Time Password) like GitHub, Google Authenticator, etc.

This module handles:
- TOTP secret generation and verification
- QR code generation for authenticator apps
- Backup/recovery codes generation and verification
"""

import pyotp
import qrcode
import secrets
import hashlib
import base64
from io import BytesIO
from typing import List, Tuple, Optional
from passlib.context import CryptContext

# Password context for hashing backup codes
# Using PBKDF2-SHA256 for consistency with main auth service
backup_code_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto",
    pbkdf2_sha256__default_rounds=100000  # Fewer rounds than passwords (backup codes are high entropy)
)


def generate_totp_secret() -> str:
    """
    Generate a random TOTP secret key.
    
    Returns a base32-encoded secret that can be used with any TOTP app
    (Google Authenticator, Authy, Microsoft Authenticator, etc.)
    
    Returns:
        str: Base32 encoded secret (16 characters)
    """
    return pyotp.random_base32()


def generate_qr_code(email: str, secret: str, issuer: str = "Nexus") -> str:
    """
    Generate a QR code for TOTP setup.
    
    Creates a QR code that can be scanned by authenticator apps.
    Uses the standard otpauth:// URI format.
    
    Args:
        email: User's email (displayed in authenticator app)
        secret: Base32 TOTP secret
        issuer: Service name (shown in authenticator app)
        
    Returns:
        str: Base64-encoded PNG image with data URI prefix
    """
    # Create TOTP URI following the standard format
    # Format: otpauth://totp/Issuer:email?secret=SECRET&issuer=Issuer
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(name=email, issuer_name=issuer)
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,  # Controls size (1 is smallest)
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(uri)
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64 for embedding in JSON response
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    # Return as data URI
    return f"data:image/png;base64,{img_str}"


def verify_totp_code(secret: str, code: str, valid_window: int = 1) -> bool:
    """
    Verify a TOTP code against a secret.
    
    TOTP codes change every 30 seconds. We allow a window of +/- 30 seconds
    to account for clock drift and user typing speed.
    
    Args:
        secret: Base32 encoded TOTP secret
        code: 6-digit code from authenticator app
        valid_window: Number of 30-second windows to check (1 = ±30 seconds)
        
    Returns:
        bool: True if code is valid, False otherwise
    """
    try:
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=valid_window)
    except Exception:
        return False


def generate_backup_codes(count: int = 10) -> List[str]:
    """
    Generate cryptographically secure backup/recovery codes.
    
    These are used when the user loses access to their authenticator app.
    Each code can be used only once.
    
    GitHub uses 16 codes, we'll default to 10.
    Format: XXXX-XXXX (8 alphanumeric characters with hyphen for readability)
    
    Args:
        count: Number of backup codes to generate
        
    Returns:
        List[str]: List of backup codes in format "XXXX-XXXX"
    """
    codes = []
    for _ in range(count):
        # Generate 8 random alphanumeric characters
        # Using secrets module for cryptographic randomness
        code = ''.join(secrets.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(8))
        # Format as XXXX-XXXX for readability
        formatted_code = f"{code[:4]}-{code[4:]}"
        codes.append(formatted_code)
    return codes


def hash_backup_code(code: str) -> str:
    """
    Hash a backup code for secure storage.
    
    We store hashed versions of backup codes, not plain text.
    This way if the database is compromised, backup codes are still protected.
    
    Args:
        code: Backup code to hash
        
    Returns:
        str: Hashed backup code
    """
    # Remove hyphen and convert to uppercase for consistency
    normalized = code.replace("-", "").upper()
    return backup_code_context.hash(normalized)


def verify_backup_code(code: str, hashed_codes: List[str]) -> Tuple[bool, Optional[str]]:
    """
    Verify a backup code against stored hashed codes.
    
    If valid, returns the hash that matched so it can be removed
    (backup codes are single-use).
    
    Args:
        code: Backup code to verify
        hashed_codes: List of hashed backup codes from database
        
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, matched_hash)
    """
    # Normalize the input code
    normalized = code.replace("-", "").upper()
    
    # Check against each stored hash
    for hashed in hashed_codes:
        try:
            if backup_code_context.verify(normalized, hashed):
                return True, hashed
        except Exception:
            continue
    
    return False, None


def get_current_totp_code(secret: str) -> str:
    """
    Get the current TOTP code for a secret.
    Useful for testing and debugging.
    
    Args:
        secret: Base32 encoded TOTP secret
        
    Returns:
        str: Current 6-digit TOTP code
    """
    totp = pyotp.TOTP(secret)
    return totp.now()


def validate_totp_code_format(code: str) -> bool:
    """
    Validate that a code is in the correct format.
    
    TOTP codes are 6 digits.
    Backup codes are 8 alphanumeric chars (with or without hyphen).
    
    Args:
        code: Code to validate
        
    Returns:
        bool: True if format is valid
    """
    # Remove hyphen for backup code check
    cleaned = code.replace("-", "")
    
    # Check if it's a 6-digit TOTP code
    if len(code) == 6 and code.isdigit():
        return True
    
    # Check if it's an 8-character backup code (alphanumeric)
    if len(cleaned) == 8 and cleaned.isalnum():
        return True
    
    return False


