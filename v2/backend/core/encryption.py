"""
Multi-Layer Encryption System for Project Nexus
Provides AES-256 encryption for data at rest and field-level encryption for PII.

Encryption Strategy:
- Data at Rest: AES-256-GCM for database fields
- Field-Level: Encrypt sensitive PII (email, names, addresses)
- Key Management: Master key from environment, derived keys for different purposes
- Rotation: Support for key versioning and rotation

Usage:
    from core.encryption import encrypt_field, decrypt_field, encrypt_file
    
    # Encrypt sensitive field
    encrypted_email = encrypt_field(user_email, "email")
    
    # Decrypt when needed
    decrypted_email = decrypt_field(encrypted_email, "email")
"""

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import os
import sys
import base64
import json
from typing import Optional, Dict, Any
import hashlib
import secrets


# Master encryption key - MUST be set via environment variable
# This is the root of all encryption keys
MASTER_KEY = os.getenv("ENCRYPTION_MASTER_KEY")
if not MASTER_KEY or len(MASTER_KEY) < 64:
    print("❌ SECURITY ERROR: ENCRYPTION_MASTER_KEY must be set and at least 64 characters")
    print("   Generate with: openssl rand -hex 64")
    sys.exit(1)

# Key version for rotation support
KEY_VERSION = os.getenv("ENCRYPTION_KEY_VERSION", "v1")


class EncryptionService:
    """
    Service for encrypting and decrypting data.
    Uses AES-256-GCM for authenticated encryption.
    """
    
    def __init__(self):
        # Master key bytes
        self.master_key = MASTER_KEY.encode('utf-8')
        self.backend = default_backend()
        
        # Cache for derived keys (context-specific)
        self._key_cache: Dict[str, bytes] = {}
    
    def _derive_key(self, context: str, salt: Optional[bytes] = None) -> bytes:
        """
        Derive a context-specific key from master key using PBKDF2.
        
        Args:
            context: Purpose of the key (e.g., "email", "pii", "files")
            salt: Optional salt (generated if not provided)
            
        Returns:
            32-byte derived key
        """
        # Use cached key if available
        cache_key = f"{context}:{KEY_VERSION}"
        if cache_key in self._key_cache:
            return self._key_cache[cache_key]
        
        # Generate deterministic salt from context and version
        # This allows key recovery without storing salt
        if salt is None:
            salt_input = f"{context}:{KEY_VERSION}".encode('utf-8')
            salt = hashlib.sha256(salt_input).digest()
        
        # Derive key using PBKDF2
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,  # 256 bits for AES-256
            salt=salt,
            iterations=100000,  # OWASP recommended minimum
            backend=self.backend
        )
        
        derived_key = kdf.derive(self.master_key)
        
        # Cache the derived key
        self._key_cache[cache_key] = derived_key
        
        return derived_key
    
    def encrypt_field(self, data: str, context: str = "default") -> str:
        """
        Encrypt a text field using AES-256-GCM.
        
        Args:
            data: Plain text to encrypt
            context: Context for key derivation (e.g., "email", "pii")
            
        Returns:
            Base64-encoded encrypted data with version prefix
        """
        if not data:
            return data
        
        # Get context-specific key
        key = self._derive_key(context)
        
        # Generate random IV (96 bits for GCM)
        iv = secrets.token_bytes(12)
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(iv),
            backend=self.backend
        )
        encryptor = cipher.encryptor()
        
        # Encrypt data
        data_bytes = data.encode('utf-8')
        ciphertext = encryptor.update(data_bytes) + encryptor.finalize()
        
        # Get authentication tag
        tag = encryptor.tag
        
        # Package: version + iv + tag + ciphertext
        # This allows future key rotation
        package = {
            "v": KEY_VERSION,
            "iv": base64.b64encode(iv).decode('utf-8'),
            "tag": base64.b64encode(tag).decode('utf-8'),
            "data": base64.b64encode(ciphertext).decode('utf-8'),
            "ctx": context
        }
        
        # Return as base64-encoded JSON
        package_json = json.dumps(package)
        return base64.b64encode(package_json.encode('utf-8')).decode('utf-8')
    
    def decrypt_field(self, encrypted_data: str, context: str = "default") -> str:
        """
        Decrypt a field encrypted with encrypt_field.
        
        Args:
            encrypted_data: Base64-encoded encrypted data
            context: Context for key derivation (must match encryption context)
            
        Returns:
            Decrypted plain text
        """
        if not encrypted_data:
            return encrypted_data
        
        try:
            # Decode package
            package_json = base64.b64decode(encrypted_data)
            package = json.loads(package_json)
            
            # Extract components
            version = package["v"]
            iv = base64.b64decode(package["iv"])
            tag = base64.b64decode(package["tag"])
            ciphertext = base64.b64decode(package["data"])
            stored_context = package.get("ctx", context)
            
            # Get key (using version from package for rotation support)
            key = self._derive_key(stored_context)
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(key),
                modes.GCM(iv, tag),
                backend=self.backend
            )
            decryptor = cipher.decryptor()
            
            # Decrypt data
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            
            return plaintext.decode('utf-8')
            
        except Exception as e:
            # Log error but don't expose details
            print(f"⚠️  Decryption failed: {type(e).__name__}")
            raise ValueError("Failed to decrypt data")
    
    def encrypt_file(self, file_path: str, output_path: Optional[str] = None) -> str:
        """
        Encrypt a file using AES-256.
        
        Args:
            file_path: Path to file to encrypt
            output_path: Output path (defaults to file_path + ".enc")
            
        Returns:
            Path to encrypted file
        """
        if output_path is None:
            output_path = f"{file_path}.enc"
        
        # Read file
        with open(file_path, 'rb') as f:
            data = f.read()
        
        # Get file encryption key
        key = self._derive_key("files")
        
        # Generate IV
        iv = secrets.token_bytes(12)
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(iv),
            backend=self.backend
        )
        encryptor = cipher.encryptor()
        
        # Encrypt
        ciphertext = encryptor.update(data) + encryptor.finalize()
        tag = encryptor.tag
        
        # Write encrypted file (version + iv + tag + ciphertext)
        with open(output_path, 'wb') as f:
            f.write(KEY_VERSION.encode('utf-8').ljust(8))  # 8 bytes for version
            f.write(iv)  # 12 bytes
            f.write(tag)  # 16 bytes
            f.write(ciphertext)
        
        return output_path
    
    def decrypt_file(self, encrypted_path: str, output_path: Optional[str] = None) -> str:
        """
        Decrypt a file encrypted with encrypt_file.
        
        Args:
            encrypted_path: Path to encrypted file
            output_path: Output path (defaults to removing .enc extension)
            
        Returns:
            Path to decrypted file
        """
        if output_path is None:
            if encrypted_path.endswith('.enc'):
                output_path = encrypted_path[:-4]
            else:
                output_path = f"{encrypted_path}.dec"
        
        # Read encrypted file
        with open(encrypted_path, 'rb') as f:
            version = f.read(8).decode('utf-8').strip()
            iv = f.read(12)
            tag = f.read(16)
            ciphertext = f.read()
        
        # Get key
        key = self._derive_key("files")
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(iv, tag),
            backend=self.backend
        )
        decryptor = cipher.decryptor()
        
        # Decrypt
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        # Write decrypted file
        with open(output_path, 'wb') as f:
            f.write(plaintext)
        
        return output_path
    
    def hash_password(self, password: str) -> str:
        """
        Hash a password for storage (delegated to passlib for bcrypt).
        This is for compatibility with existing security.py.
        """
        from .security import hash_password
        return hash_password(password)
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """
        Verify a password against a hash.
        This is for compatibility with existing security.py.
        """
        from .security import verify_password
        return verify_password(password, hashed)


# Global encryption service instance
_encryption_service: Optional[EncryptionService] = None


def get_encryption_service() -> EncryptionService:
    """
    Get the global encryption service instance.
    Creates it if it doesn't exist.
    """
    global _encryption_service
    if _encryption_service is None:
        _encryption_service = EncryptionService()
    return _encryption_service


# Convenience functions for common operations
def encrypt_field(data: str, context: str = "default") -> str:
    """Encrypt a text field."""
    return get_encryption_service().encrypt_field(data, context)


def decrypt_field(encrypted_data: str, context: str = "default") -> str:
    """Decrypt a text field."""
    return get_encryption_service().decrypt_field(encrypted_data, context)


def encrypt_file(file_path: str, output_path: Optional[str] = None) -> str:
    """Encrypt a file."""
    return get_encryption_service().encrypt_file(file_path, output_path)


def decrypt_file(encrypted_path: str, output_path: Optional[str] = None) -> str:
    """Decrypt a file."""
    return get_encryption_service().decrypt_file(encrypted_path, output_path)


def encrypt_pii(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Encrypt PII fields in a dictionary.
    
    Args:
        data: Dictionary with PII fields
        
    Returns:
        Dictionary with encrypted PII fields
    """
    # Define PII fields that should be encrypted
    pii_fields = ['email', 'full_name', 'phone', 'address', 'ssn', 'credit_card']
    
    encrypted_data = data.copy()
    service = get_encryption_service()
    
    for field in pii_fields:
        if field in encrypted_data and encrypted_data[field]:
            encrypted_data[field] = service.encrypt_field(
                str(encrypted_data[field]), 
                context="pii"
            )
    
    return encrypted_data


def decrypt_pii(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Decrypt PII fields in a dictionary.
    
    Args:
        data: Dictionary with encrypted PII fields
        
    Returns:
        Dictionary with decrypted PII fields
    """
    # Define PII fields that might be encrypted
    pii_fields = ['email', 'full_name', 'phone', 'address', 'ssn', 'credit_card']
    
    decrypted_data = data.copy()
    service = get_encryption_service()
    
    for field in pii_fields:
        if field in decrypted_data and decrypted_data[field]:
            try:
                decrypted_data[field] = service.decrypt_field(
                    decrypted_data[field], 
                    context="pii"
                )
            except (ValueError, KeyError):
                # Field might not be encrypted, leave as is
                pass
    
    return decrypted_data


# Key rotation support
def rotate_encryption_key(old_version: str, new_version: str):
    """
    Rotate encryption keys.
    
    This would need to:
    1. Re-encrypt all encrypted data with new key
    2. Update KEY_VERSION
    3. Keep old keys for decryption during transition
    
    Note: This is a placeholder for future implementation.
    Actual key rotation requires careful planning and database migration.
    """
    raise NotImplementedError("Key rotation requires careful planning and should be done during maintenance window")


if __name__ == "__main__":
    # Self-test
    print("🔐 Encryption Service Self-Test")
    print("=" * 50)
    
    # Test field encryption
    test_data = "user@example.com"
    print(f"\n1. Testing field encryption...")
    print(f"   Original: {test_data}")
    
    encrypted = encrypt_field(test_data, "email")
    print(f"   Encrypted: {encrypted[:50]}...")
    
    decrypted = decrypt_field(encrypted, "email")
    print(f"   Decrypted: {decrypted}")
    
    assert decrypted == test_data, "Field encryption/decryption failed!"
    print("   ✅ Field encryption working!")
    
    # Test PII encryption
    print(f"\n2. Testing PII encryption...")
    test_pii = {
        "email": "user@example.com",
        "full_name": "John Doe",
        "username": "johndoe"  # Not PII, shouldn't be encrypted
    }
    print(f"   Original: {test_pii}")
    
    encrypted_pii = encrypt_pii(test_pii)
    print(f"   Encrypted email: {encrypted_pii['email'][:50]}...")
    print(f"   Username (not encrypted): {encrypted_pii['username']}")
    
    decrypted_pii = decrypt_pii(encrypted_pii)
    print(f"   Decrypted: {decrypted_pii}")
    
    assert decrypted_pii['email'] == test_pii['email'], "PII encryption failed!"
    print("   ✅ PII encryption working!")
    
    print("\n" + "=" * 50)
    print("✅ All encryption tests passed!")
    print("\n⚠️  Remember to set ENCRYPTION_MASTER_KEY in production!")
    print("   Generate with: openssl rand -hex 64")

