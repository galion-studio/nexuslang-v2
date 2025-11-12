"""
Configuration management for NexusLang v2 Backend.
Loads settings from environment variables.
"""

from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Uses Pydantic for validation and type checking.
    """
    
    # Application
    APP_NAME: str = "NexusLang v2"
    APP_VERSION: str = "2.0.0-beta"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Security - NO DEFAULT SECRETS (fail fast if not set properly)
    # These must be set via environment variables with secure values
    # Generate with: openssl rand -hex 64
    SECRET_KEY: str = ""
    JWT_SECRET: str = ""
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # Database (defaults to SQLite for easy development, PostgreSQL for RunPod)
    # For RunPod: Uses shared Galion PostgreSQL with separate database
    # Set DATABASE_URL environment variable for production
    DATABASE_URL: str = "sqlite+aiosqlite:///./nexuslang_dev.db"
    POSTGRES_USER: str = "nexus"
    POSTGRES_PASSWORD: str = ""  # MUST be set via environment variable
    POSTGRES_DB: str = "nexuslang_v2"  # Separate from Galion's database
    POSTGRES_HOST: str = "postgres"  # Use "galion-postgres" to connect to existing Galion PostgreSQL
    POSTGRES_PORT: int = 5432
    
    # Redis (optional but recommended for production) - For distributed features
    REDIS_URL: str = "redis://localhost:6379/1"  # DB 1 for NexusLang
    REDIS_PASSWORD: str = ""
    REDIS_HOST: str = "localhost"  # Use "galion-redis" if connecting to existing Galion Redis
    REDIS_PORT: int = 6379
    REDIS_DB: int = 1  # Separate DB from other services
    
    # Elasticsearch
    ELASTICSEARCH_URL: str = "http://elasticsearch:9200"
    
    # AI Configuration - OpenRouter as Primary Gateway (99% of use cases)
    # OpenRouter provides access to 30+ AI models through one unified API
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_APP_NAME: str = "NexusLang v2"
    OPENROUTER_SITE_URL: str = "https://developer.galion.app"
    
    # AI Provider Selection - OpenRouter is primary
    AI_PROVIDER: str = "openrouter"  # 99% of use cases
    
    # Default AI models (all accessed via OpenRouter)
    DEFAULT_AI_MODEL: str = "anthropic/claude-3.5-sonnet"  # Best reasoning
    FALLBACK_AI_MODEL: str = "openai/gpt-4-turbo"  # Fallback
    FAST_AI_MODEL: str = "openai/gpt-3.5-turbo"  # Quick tasks
    CODE_AI_MODEL: str = "meta-llama/codellama-70b-instruct"  # Code generation
    
    # OpenAI (optional - only for direct access or fallback)
    # Not required if using OpenRouter
    OPENAI_API_KEY: str = ""
    OPENAI_ORG_ID: str = ""
    
    # Shopify (optional)
    SHOPIFY_API_KEY: str = ""
    SHOPIFY_API_SECRET: str = ""
    SHOPIFY_ACCESS_TOKEN: str = ""
    SHOPIFY_WEBHOOK_SECRET: str = ""
    SHOPIFY_STORE_URL: str = ""
    
    # Billing
    FREE_TIER_CREDITS: int = 100
    PRO_TIER_CREDITS: int = 10000
    ENTERPRISE_TIER_CREDITS: int = 999999
    CREDIT_COST_PER_1K_TOKENS: int = 1
    
    # Voice
    WHISPER_MODEL: str = "base"
    WHISPER_DEVICE: str = "cpu"
    TTS_MODEL: str = "tts_models/en/ljspeech/tacotron2-DDC"
    TTS_DEVICE: str = "cpu"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    CORS_ALLOW_CREDENTIALS: bool = True
    
    # Rate Limiting (per endpoint type)
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    RATE_LIMIT_PER_DAY: int = 10000
    RATE_LIMIT_AUTH_REQUESTS: int = 10  # Login/register per 5 minutes
    RATE_LIMIT_CODE_EXEC: int = 30  # Code execution per minute
    RATE_LIMIT_VOICE: int = 20  # Voice endpoints per minute
    
    # Account Security
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 30
    PASSWORD_RESET_TOKEN_EXPIRY_HOURS: int = 1
    EMAIL_VERIFICATION_TOKEN_EXPIRY_HOURS: int = 24
    
    # Feature Flags
    ENABLE_GROKOPEDIA: bool = True
    ENABLE_VOICE: bool = True
    ENABLE_COMMUNITY: bool = True
    ENABLE_BILLING: bool = True
    
    # Storage (S3-compatible)
    S3_ENDPOINT: str = ""
    S3_BUCKET: str = "nexuslang-storage"
    S3_ACCESS_KEY: str = ""
    S3_SECRET_KEY: str = ""
    
    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "noreply@nexuslang.dev"
    
    # Monitoring
    SENTRY_DSN: str = ""
    SENTRY_ENVIRONMENT: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create global settings instance
settings = Settings()

