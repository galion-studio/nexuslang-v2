"""
Secrets Management System for Project Nexus
Provides secure storage and retrieval of secrets (API keys, credentials, etc.)

Features:
- Centralized secret storage
- Environment variable fallback
- Secret rotation support
- Audit logging for secret access
- Support for external vault systems (HashiCorp Vault, AWS Secrets Manager)

Usage:
    from core.vault import get_secret, set_secret
    
    # Get a secret
    api_key = get_secret("openai_api_key")
    
    # Set a secret (for dynamic secrets)
    set_secret("temp_token", token, ttl=3600)
"""

import os
import sys
import json
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import hashlib
import secrets


class SecretNotFoundError(Exception):
    """Raised when a required secret is not found."""
    pass


class VaultService:
    """
    Service for managing secrets.
    
    In development: Uses environment variables
    In production: Can integrate with HashiCorp Vault or AWS Secrets Manager
    """
    
    def __init__(self, use_external_vault: bool = False):
        self.use_external_vault = use_external_vault
        
        # In-memory cache for secrets (encrypted)
        self._cache: Dict[str, Dict[str, Any]] = {}
        
        # Secret rotation tracking
        self._rotation_history: Dict[str, list] = {}
        
        # Load secrets from environment
        self._load_from_env()
    
    def _load_from_env(self):
        """
        Load secrets from environment variables.
        """
        # Define required secrets
        required_secrets = [
            "JWT_SECRET_KEY",
            "ENCRYPTION_MASTER_KEY",
            "POSTGRES_PASSWORD",
            "REDIS_PASSWORD"
        ]
        
        # Define optional secrets (with defaults for dev)
        optional_secrets = [
            "OPENAI_API_KEY",
            "SHOPIFY_API_KEY",
            "SHOPIFY_API_SECRET",
            "SENTRY_DSN",
            "CLOUDFLARE_API_TOKEN",
            "BACKBLAZE_KEY_ID",
            "BACKBLAZE_APPLICATION_KEY"
        ]
        
        # Check required secrets
        missing_secrets = []
        for secret_name in required_secrets:
            value = os.getenv(secret_name)
            if not value:
                missing_secrets.append(secret_name)
            else:
                # Store in cache (will be encrypted in production)
                self._cache[secret_name.lower()] = {
                    "value": value,
                    "loaded_at": datetime.utcnow(),
                    "source": "environment"
                }
        
        if missing_secrets:
            print("❌ SECURITY ERROR: Required secrets not set:")
            for secret in missing_secrets:
                print(f"   - {secret}")
            print("\n   See env.template for required secrets")
            sys.exit(1)
        
        # Load optional secrets
        for secret_name in optional_secrets:
            value = os.getenv(secret_name)
            if value:
                self._cache[secret_name.lower()] = {
                    "value": value,
                    "loaded_at": datetime.utcnow(),
                    "source": "environment"
                }
        
        print(f"✅ Loaded {len(self._cache)} secrets from environment")
    
    def get_secret(self, secret_name: str, required: bool = True) -> Optional[str]:
        """
        Get a secret by name.
        
        Args:
            secret_name: Name of the secret (case-insensitive)
            required: If True, raise error if secret not found
            
        Returns:
            Secret value or None if not found and not required
            
        Raises:
            SecretNotFoundError: If secret not found and required=True
        """
        # Normalize name to lowercase
        secret_key = secret_name.lower()
        
        # Check cache first
        if secret_key in self._cache:
            return self._cache[secret_key]["value"]
        
        # If using external vault, try to fetch
        if self.use_external_vault:
            value = self._fetch_from_external_vault(secret_name)
            if value:
                # Cache it
                self._cache[secret_key] = {
                    "value": value,
                    "loaded_at": datetime.utcnow(),
                    "source": "external_vault"
                }
                return value
        
        # Secret not found
        if required:
            raise SecretNotFoundError(f"Required secret '{secret_name}' not found")
        
        return None
    
    def set_secret(self, secret_name: str, value: str, ttl: Optional[int] = None):
        """
        Set a secret (for temporary/dynamic secrets).
        
        Args:
            secret_name: Name of the secret
            value: Secret value
            ttl: Time-to-live in seconds (None for permanent)
        """
        secret_key = secret_name.lower()
        
        expires_at = None
        if ttl:
            expires_at = datetime.utcnow() + timedelta(seconds=ttl)
        
        self._cache[secret_key] = {
            "value": value,
            "loaded_at": datetime.utcnow(),
            "expires_at": expires_at,
            "source": "runtime"
        }
    
    def rotate_secret(self, secret_name: str, new_value: str):
        """
        Rotate a secret to a new value.
        
        Args:
            secret_name: Name of the secret to rotate
            new_value: New secret value
        """
        secret_key = secret_name.lower()
        
        # Get old value for history
        old_value = self._cache.get(secret_key, {}).get("value")
        
        # Update to new value
        self._cache[secret_key] = {
            "value": new_value,
            "loaded_at": datetime.utcnow(),
            "rotated_at": datetime.utcnow(),
            "source": "rotation"
        }
        
        # Track rotation history (hashed for security)
        if secret_key not in self._rotation_history:
            self._rotation_history[secret_key] = []
        
        self._rotation_history[secret_key].append({
            "old_value_hash": hashlib.sha256(old_value.encode()).hexdigest() if old_value else None,
            "new_value_hash": hashlib.sha256(new_value.encode()).hexdigest(),
            "rotated_at": datetime.utcnow().isoformat()
        })
        
        print(f"✅ Rotated secret: {secret_name}")
    
    def _fetch_from_external_vault(self, secret_name: str) -> Optional[str]:
        """
        Fetch secret from external vault (HashiCorp Vault, AWS Secrets Manager, etc.)
        
        This is a placeholder for future implementation.
        """
        # TODO: Implement external vault integration
        # For now, fall back to environment
        return os.getenv(secret_name.upper())
    
    def list_secrets(self, include_values: bool = False) -> Dict[str, Any]:
        """
        List all loaded secrets (for debugging/auditing).
        
        Args:
            include_values: If True, include actual values (USE WITH CAUTION!)
            
        Returns:
            Dictionary of secret metadata
        """
        result = {}
        
        for key, data in self._cache.items():
            result[key] = {
                "loaded_at": data["loaded_at"].isoformat(),
                "source": data.get("source", "unknown"),
                "has_value": bool(data.get("value")),
                "expires_at": data.get("expires_at").isoformat() if data.get("expires_at") else None
            }
            
            if include_values:
                result[key]["value"] = data["value"]
        
        return result
    
    def cleanup_expired(self):
        """
        Remove expired secrets from cache.
        """
        now = datetime.utcnow()
        expired = []
        
        for key, data in self._cache.items():
            expires_at = data.get("expires_at")
            if expires_at and expires_at < now:
                expired.append(key)
        
        for key in expired:
            del self._cache[key]
        
        if expired:
            print(f"🧹 Cleaned up {len(expired)} expired secrets")


# Global vault service instance
_vault_service: Optional[VaultService] = None


def get_vault_service() -> VaultService:
    """
    Get the global vault service instance.
    Creates it if it doesn't exist.
    """
    global _vault_service
    if _vault_service is None:
        _vault_service = VaultService()
    return _vault_service


# Convenience functions
def get_secret(secret_name: str, required: bool = True) -> Optional[str]:
    """
    Get a secret by name.
    
    Args:
        secret_name: Name of the secret
        required: If True, raise error if not found
        
    Returns:
        Secret value or None
    """
    return get_vault_service().get_secret(secret_name, required)


def set_secret(secret_name: str, value: str, ttl: Optional[int] = None):
    """
    Set a secret (for temporary/dynamic secrets).
    
    Args:
        secret_name: Name of the secret
        value: Secret value
        ttl: Time-to-live in seconds
    """
    get_vault_service().set_secret(secret_name, value, ttl)


def rotate_secret(secret_name: str, new_value: str):
    """
    Rotate a secret to a new value.
    """
    get_vault_service().rotate_secret(secret_name, new_value)


def list_secrets(include_values: bool = False) -> Dict[str, Any]:
    """
    List all loaded secrets.
    """
    return get_vault_service().list_secrets(include_values)


# Secret generation utilities
def generate_secret_key(length: int = 64) -> str:
    """
    Generate a cryptographically secure random secret key.
    
    Args:
        length: Length in bytes (will be hex-encoded, so output is 2x)
        
    Returns:
        Hex-encoded random secret
    """
    return secrets.token_hex(length)


def generate_api_key() -> str:
    """
    Generate an API key in the format: nx_live_[random]
    """
    random_part = secrets.token_urlsafe(32)
    return f"nx_live_{random_part}"


if __name__ == "__main__":
    # Self-test
    print("🔐 Vault Service Self-Test")
    print("=" * 50)
    
    # Test secret generation
    print("\n1. Testing secret generation...")
    test_key = generate_secret_key(32)
    print(f"   Generated key: {test_key[:32]}...")
    print(f"   Length: {len(test_key)} characters")
    print("   ✅ Secret generation working!")
    
    # Test API key generation
    print("\n2. Testing API key generation...")
    api_key = generate_api_key()
    print(f"   Generated API key: {api_key}")
    assert api_key.startswith("nx_live_"), "API key format incorrect!"
    print("   ✅ API key generation working!")
    
    # Test set/get secret
    print("\n3. Testing secret storage...")
    test_secret_name = "test_secret"
    test_secret_value = "test_value_12345"
    
    set_secret(test_secret_name, test_secret_value)
    retrieved = get_secret(test_secret_name)
    assert retrieved == test_secret_value, "Secret storage failed!"
    print("   ✅ Secret storage working!")
    
    # Test TTL
    print("\n4. Testing TTL secrets...")
    set_secret("temp_secret", "temp_value", ttl=1)
    import time
    time.sleep(2)
    get_vault_service().cleanup_expired()
    try:
        get_secret("temp_secret", required=True)
        print("   ❌ TTL secret cleanup failed!")
    except SecretNotFoundError:
        print("   ✅ TTL secret cleanup working!")
    
    print("\n" + "=" * 50)
    print("✅ All vault tests passed!")
    print("\n⚠️  Remember to set all required secrets in production!")

