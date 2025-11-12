"""
Security Configuration Validation
Ensures all security-critical settings are properly configured before startup.
Implements fail-fast principle: Better to crash than run insecurely.
"""

import os
import sys
from typing import List, Tuple


class SecurityValidationError(Exception):
    """Raised when security validation fails."""
    pass


def validate_secret(
    env_var: str,
    min_length: int,
    disallowed_values: List[str],
    description: str
) -> Tuple[bool, str]:
    """
    Validate a secret meets security requirements.
    
    Args:
        env_var: Environment variable name
        min_length: Minimum required length
        disallowed_values: List of forbidden values (defaults, placeholders)
        description: Human-readable description for error messages
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    value = os.getenv(env_var)
    
    # Check if set
    if not value:
        return False, f"{env_var} is not set in environment"
    
    # Check length
    if len(value) < min_length:
        return False, f"{env_var} is too short (minimum {min_length} characters)"
    
    # Check against disallowed values
    for disallowed in disallowed_values:
        if value == disallowed or disallowed in value.lower():
            return False, f"{env_var} is set to a default/placeholder value"
    
    return True, ""


def validate_all_secrets() -> None:
    """
    Validate all security-critical configuration on startup.
    Exits the application if any validation fails.
    
    This implements Musk's principle: Question every requirement.
    We REQUIRE secure configuration - no compromises.
    """
    
    print("\n" + "="*60)
    print("🔒 SECURITY VALIDATION - Checking Configuration")
    print("="*60)
    
    errors = []
    warnings = []
    
    # Validate JWT_SECRET
    is_valid, error = validate_secret(
        env_var="JWT_SECRET",
        min_length=32,
        disallowed_values=[
            "jwt-secret-key-for-development",
            "change-me",
            "change_me",
            "your-secret",
            "secret",
            "dev-secret"
        ],
        description="JWT signing key"
    )
    if not is_valid:
        errors.append(f"❌ JWT_SECRET: {error}")
    else:
        print("✅ JWT_SECRET: Validated")
    
    # Validate SECRET_KEY (for general encryption)
    secret_key = os.getenv("SECRET_KEY")
    if secret_key and len(secret_key) < 32:
        errors.append(f"❌ SECRET_KEY: Too short (minimum 32 characters)")
    elif secret_key and any(bad in secret_key.lower() for bad in ["change-me", "dev-secret", "secret-key"]):
        errors.append(f"❌ SECRET_KEY: Using default/placeholder value")
    elif secret_key:
        print("✅ SECRET_KEY: Validated")
    
    # Validate DATABASE_URL in production
    environment = os.getenv("ENVIRONMENT", "development")
    db_url = os.getenv("DATABASE_URL")
    
    if environment == "production":
        if not db_url:
            errors.append("❌ DATABASE_URL: Not set (required in production)")
        elif "sqlite" in db_url:
            warnings.append("⚠️  DATABASE_URL: Using SQLite in production (PostgreSQL recommended)")
        elif db_url and "postgresql" in db_url:
            print("✅ DATABASE_URL: Production database configured")
    
    # Check for sensitive data in logs
    debug_mode = os.getenv("DEBUG", "false").lower()
    if environment == "production" and debug_mode == "true":
        warnings.append("⚠️  DEBUG: Enabled in production (may leak sensitive data)")
    
    # Validate OpenAI/OpenRouter API keys if AI features enabled
    openai_key = os.getenv("OPENAI_API_KEY")
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    
    if not openai_key and not openrouter_key:
        warnings.append("⚠️  AI Keys: Neither OPENAI_API_KEY nor OPENROUTER_API_KEY set")
        warnings.append("   AI features will be disabled")
    else:
        if openai_key and openai_key.startswith("sk-proj-"):
            print("✅ OPENAI_API_KEY: Valid format")
        if openrouter_key and openrouter_key.startswith("sk-or-v1-"):
            print("✅ OPENROUTER_API_KEY: Valid format")
    
    # Validate CORS origins in production
    cors_origins = os.getenv("CORS_ORIGINS", "")
    if environment == "production":
        if "localhost" in cors_origins.lower():
            warnings.append("⚠️  CORS_ORIGINS: Contains localhost in production")
        elif cors_origins and ("developer.galion.app" in cors_origins or "nexuslang" in cors_origins):
            print("✅ CORS_ORIGINS: Production domains configured")
    
    # Print warnings
    if warnings:
        print("\n" + "-"*60)
        print("⚠️  WARNINGS (non-critical but should be addressed):")
        print("-"*60)
        for warning in warnings:
            print(warning)
    
    # Handle errors (critical - must exit)
    if errors:
        print("\n" + "="*60)
        print("❌ CRITICAL ERRORS - Cannot start with insecure configuration!")
        print("="*60)
        for error in errors:
            print(error)
        print("\n" + "="*60)
        print("🔧 HOW TO FIX:")
        print("="*60)
        print("1. Generate secure secrets:")
        print("   export JWT_SECRET=$(openssl rand -hex 64)")
        print("   export SECRET_KEY=$(openssl rand -hex 32)")
        print("\n2. Set in your .env file or environment:")
        print("   JWT_SECRET=<your-64-char-hex>")
        print("   SECRET_KEY=<your-32-char-hex>")
        print("\n3. Restart the server")
        print("="*60)
        
        # Exit to prevent insecure operation
        sys.exit(1)
    
    # Success!
    print("\n" + "="*60)
    print("✅ SECURITY VALIDATION PASSED")
    print("="*60)
    print(f"Environment: {environment}")
    print(f"Debug Mode: {debug_mode}")
    print("Server is secure and ready to start!")
    print("="*60 + "\n")


def generate_secure_config_example() -> str:
    """
    Generate example secure configuration.
    Used for documentation and setup scripts.
    """
    import secrets
    
    jwt_secret = secrets.token_hex(64)
    secret_key = secrets.token_hex(32)
    postgres_password = secrets.token_hex(16)
    redis_password = secrets.token_hex(16)
    
    return f"""# Secure Configuration (Generated)
# Copy these values to your .env file

# CRITICAL: Security Keys (never commit these!)
JWT_SECRET={jwt_secret}
SECRET_KEY={secret_key}

# Database
POSTGRES_PASSWORD={postgres_password}
DATABASE_URL=postgresql+asyncpg://nexus:{postgres_password}@postgres:5432/nexus_v2

# Redis
REDIS_PASSWORD={redis_password}
REDIS_URL=redis://:{redis_password}@redis:6379/0

# API Keys (replace with your actual keys)
OPENAI_API_KEY=sk-proj-your-key-here
OPENROUTER_API_KEY=sk-or-v1-your-key-here

# Production Settings
ENVIRONMENT=production
DEBUG=false
CORS_ORIGINS=https://developer.galion.app,https://api.developer.galion.app
"""


if __name__ == "__main__":
    # Can be run standalone to validate configuration
    print("Running security validation check...")
    validate_all_secrets()
    print("✅ All checks passed!")

