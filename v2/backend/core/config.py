"""
Configuration management for Galion Platform Backend
Loads environment variables and provides application settings.

"Your imagination is the end."
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Basic Application Settings
    app_name: str = "Galion Platform"
    app_version: str = "2.2.0"
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="development", env="ENVIRONMENT")

    # Server Settings
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8010, env="PORT")
    workers: int = Field(default=1, env="WORKERS")

    # Database Settings
    database_url: str = Field(default="postgresql://localhost/galion_dev", env="DATABASE_URL")
    db_pool_size: int = Field(default=10, env="DB_POOL_SIZE")
    db_max_overflow: int = Field(default=20, env="DB_MAX_OVERFLOW")
    db_pool_recycle: int = Field(default=3600, env="DB_POOL_RECYCLE")

    # Redis Settings
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    redis_pool_size: int = Field(default=10, env="REDIS_POOL_SIZE")

    # Security Settings
    secret_key: str = Field(default="your-secret-key-change-in-production", env="SECRET_KEY")
    jwt_secret: str = Field(default="your-jwt-secret-change-in-production", env="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expiration_hours: int = Field(default=24, env="JWT_EXPIRATION_HOURS")  # 24 hours
    jwt_refresh_token_expire_days: int = Field(default=7, env="JWT_REFRESH_TOKEN_EXPIRE_DAYS")
    password_reset_token_expiry_hours: int = Field(default=24, env="PASSWORD_RESET_TOKEN_EXPIRY_HOURS")
    email_verification_token_expiry_hours: int = Field(default=48, env="EMAIL_VERIFICATION_TOKEN_EXPIRY_HOURS")

    # CORS Settings
    cors_origins: List[str] = Field(default=["*"], env="CORS_ORIGINS")
    cors_allow_credentials: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    cors_allow_methods: List[str] = Field(default=["*"], env="CORS_ALLOW_METHODS")
    cors_allow_headers: List[str] = Field(default=["*"], env="CORS_ALLOW_HEADERS")

    # Trusted Hosts (for production)
    allowed_hosts: List[str] = Field(default=[], env="ALLOWED_HOSTS")

    # API Keys
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")

    # Agent System Configuration
    max_concurrent_executions: int = Field(default=10, env="MAX_CONCURRENT_EXECUTIONS")
    agent_timeout_seconds: int = Field(default=3600, env="AGENT_TIMEOUT_SECONDS")
    tool_rate_limit_per_minute: int = Field(default=60, env="TOOL_RATE_LIMIT_PER_MINUTE")
    cost_limit_per_execution: float = Field(default=0.50, env="COST_LIMIT_PER_EXECUTION")
    cost_limit_per_hour: float = Field(default=25.00, env="COST_LIMIT_PER_HOUR")

    # WebSocket Configuration
    ws_heartbeat_interval: int = Field(default=30, env="WS_HEARTBEAT_INTERVAL")
    ws_max_connections_per_user: int = Field(default=5, env="WS_MAX_CONNECTIONS_PER_USER")
    ws_message_queue_size: int = Field(default=1000, env="WS_MESSAGE_QUEUE_SIZE")

    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    log_max_file_size: str = Field(default="100MB", env="LOG_MAX_FILE_SIZE")
    log_backup_count: int = Field(default=5, env="LOG_BACKUP_COUNT")

    # Performance Tuning
    worker_processes: int = Field(default=4, env="WORKER_PROCESSES")
    max_requests_per_worker: int = Field(default=1000, env="MAX_REQUESTS_PER_WORKER")
    worker_timeout: int = Field(default=30, env="WORKER_TIMEOUT")
    memory_limit: str = Field(default="1GB", env="MEMORY_LIMIT")

    # Feature Flags
    enable_agent_collaboration: bool = Field(default=True, env="ENABLE_AGENT_COLLABORATION")
    enable_real_time_monitoring: bool = Field(default=True, env="ENABLE_REAL_TIME_MONITORING")
    enable_human_loop: bool = Field(default=True, env="ENABLE_HUMAN_LOOP")
    enable_context_learning: bool = Field(default=True, env="ENABLE_CONTEXT_LEARNING")
    enable_advanced_nlp: bool = Field(default=True, env="ENABLE_ADVANCED_NLP")

    # External Service URLs
    grafana_url: Optional[str] = Field(default=None, env="GRAFANA_URL")
    prometheus_url: Optional[str] = Field(default=None, env="PROMETHEUS_URL")

    # File Upload Settings
    max_upload_size: int = Field(default=100 * 1024 * 1024, env="MAX_UPLOAD_SIZE")  # 100MB
    allowed_file_types: List[str] = Field(default=[
        "image/jpeg", "image/png", "image/gif",
        "application/pdf", "text/plain",
        "application/json", "application/xml"
    ], env="ALLOWED_FILE_TYPES")

    # Cache Settings
    cache_ttl: int = Field(default=3600, env="CACHE_TTL")  # 1 hour
    cache_max_size: int = Field(default=1000, env="CACHE_MAX_SIZE")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Global settings instance
settings = Settings()

# Utility functions
def is_production() -> bool:
    """Check if running in production environment"""
    return settings.environment.lower() == "production"

def is_development() -> bool:
    """Check if running in development environment"""
    return settings.environment.lower() == "development"

def get_database_config() -> dict:
    """Get database configuration dictionary"""
    return {
        "url": settings.database_url,
        "pool_size": settings.db_pool_size,
        "max_overflow": settings.db_max_overflow,
        "pool_recycle": settings.db_pool_recycle,
        "echo": settings.debug
    }

def get_redis_config() -> dict:
    """Get Redis configuration dictionary"""
    return {
        "url": settings.redis_url,
        "pool_size": settings.redis_pool_size,
        "decode_responses": True
    }

def get_cors_config() -> dict:
    """Get CORS configuration dictionary"""
    return {
        "allow_origins": settings.cors_origins,
        "allow_credentials": settings.cors_allow_credentials,
        "allow_methods": settings.cors_allow_methods,
        "allow_headers": settings.cors_allow_headers
    }

def validate_configuration() -> List[str]:
    """Validate configuration and return list of issues"""
    issues = []

    # Check required API keys
    if not settings.openai_api_key and settings.enable_advanced_nlp:
        issues.append("OPENAI_API_KEY is required when advanced NLP is enabled")

    # Check database URL
    if not settings.database_url:
        issues.append("DATABASE_URL is required")

    # Check Redis URL
    if not settings.redis_url:
        issues.append("REDIS_URL is required")

    # Check security settings for production
    if is_production():
        if settings.secret_key == "your-secret-key-change-in-production":
            issues.append("SECRET_KEY must be changed from default in production")

        if settings.jwt_secret == "your-jwt-secret-change-in-production":
            issues.append("JWT_SECRET must be changed from default in production")

        if "*" in settings.cors_origins:
            issues.append("CORS_ORIGINS should not be '*' in production")

    # Check agent system configuration
    if settings.max_concurrent_executions < 1:
        issues.append("MAX_CONCURRENT_EXECUTIONS must be at least 1")

    if settings.agent_timeout_seconds < 60:
        issues.append("AGENT_TIMEOUT_SECONDS must be at least 60 seconds")

    return issues

# Validate configuration on import
config_issues = validate_configuration()
if config_issues:
    print("⚠️ Configuration Issues Detected:")
    for issue in config_issues:
        print(f"   - {issue}")
    print("Please fix these issues before running the application.")
    if is_production():
        print("🚨 Production deployment blocked due to configuration issues!")
        exit(1)

# Export settings
__all__ = ["settings", "is_production", "is_development", "get_database_config", "get_redis_config", "get_cors_config"]