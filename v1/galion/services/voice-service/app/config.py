"""
Configuration settings for Voice Service
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Voice Service Configuration"""
    
    # Service Info
    SERVICE_NAME: str = "voice-service"
    SERVICE_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8003
    
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str
    
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str
    KAFKA_TOPIC_VOICE_EVENTS: str = "voice-events"
    
    # Authentication
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    
    # OpenAI (Whisper STT)
    OPENAI_API_KEY: str
    OPENAI_WHISPER_MODEL: str = "whisper-1"
    
    # ElevenLabs (TTS)
    ELEVENLABS_API_KEY: str
    ELEVENLABS_VOICE_ID: str = "21m00Tcm4TlvDq8ikWAM"  # Rachel - professional voice
    ELEVENLABS_MODEL: str = "eleven_monolingual_v1"
    
    # OpenRouter (Intent Classification)
    OPENROUTER_API_KEY: str
    OPENROUTER_MODEL: str = "openai/gpt-4-turbo"
    
    # Voice Settings
    VOICE_MAX_AUDIO_SIZE_MB: int = 10
    VOICE_MAX_DURATION_SECONDS: int = 30
    VOICE_RATE_LIMIT_PER_HOUR: int = 100
    
    # Audio Processing
    AUDIO_SAMPLE_RATE: int = 16000
    AUDIO_CHANNELS: int = 1
    AUDIO_FORMAT: str = "wav"
    
    # API Gateway URLs
    AUTH_SERVICE_URL: str = "http://auth-service:8000"
    USER_SERVICE_URL: str = "http://user-service:8001"
    CONTENT_SERVICE_URL: str = "http://content-service:8002"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

