"""
Configuration management using Pydantic settings.
Environment variables are automatically loaded and validated.
"""

from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List


class Settings(BaseSettings):
    """
    Application settings.
    Values come from environment variables or .env file.
    """
    
    # Application
    APP_NAME: str = "Nexus Auth Service"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # Database
    DATABASE_URL: str
    
    # JWT Authentication
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_SECONDS: int = 3600
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8080,http://127.0.0.1:3000"
    
    # Redis
    REDIS_URL: str
    
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str
    
    def get_allowed_origins(self) -> List[str]:
        """Parse ALLOWED_ORIGINS from comma-separated string"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(',')]
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    

# Global settings instance
settings = Settings()

