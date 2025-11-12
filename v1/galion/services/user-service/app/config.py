"""
Configuration management using Pydantic settings.
Environment variables are automatically loaded and validated.
"""

from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List


class Settings(BaseSettings):
    """
    Application settings for User Service.
    Values come from environment variables or .env file.
    """
    
    # Application
    APP_NAME: str = "Nexus User Service"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # Database - shared with auth service
    DATABASE_URL: str
    
    # JWT Authentication - must match auth service settings
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_SECONDS: int = 3600
    
    # CORS - stored as string, parsed below
    _allowed_origins: str = "http://localhost:3000,http://localhost:8000"
    
    # Redis for caching
    REDIS_URL: str
    
    # Kafka for event streaming
    KAFKA_BOOTSTRAP_SERVERS: str
    
    @property
    def ALLOWED_ORIGINS(self) -> List[str]:
        """Parse ALLOWED_ORIGINS from comma-separated string"""
        if hasattr(self, '_allowed_origins'):
            return [origin.strip() for origin in self._allowed_origins.split(',')]
        return ["http://localhost:3000", "http://localhost:8000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        # Map ALLOWED_ORIGINS env var to _allowed_origins field
        fields = {
            '_allowed_origins': {
                'env': 'ALLOWED_ORIGINS'
            }
        }


# Global settings instance
settings = Settings()

