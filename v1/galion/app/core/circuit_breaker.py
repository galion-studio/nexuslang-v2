"""
Circuit Breaker Pattern Implementation
Prevents cascading failures when external services fail
"""
from circuitbreaker import circuit, CircuitBreakerError
from functools import wraps
from typing import Any, Callable, Optional
import asyncio
import time
from enum import Enum


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


# ==================== OpenAI Circuit Breaker ====================

@circuit(
    failure_threshold=5,      # Open after 5 failures
    recovery_timeout=60,      # Try again after 60 seconds
    expected_exception=Exception,
    name="openai_circuit"
)
async def call_openai_api(
    prompt: str,
    model: str = "gpt-4-turbo",
    max_tokens: int = 150,
    temperature: float = 0.7
) -> dict:
    """
    Circuit breaker protected OpenAI API call
    
    If 5 consecutive failures occur, circuit opens for 60 seconds.
    This prevents overwhelming a failing service and wasting resources.
    
    Args:
        prompt: The user prompt
        model: OpenAI model to use
        max_tokens: Maximum tokens in response
        temperature: Response randomness (0-1)
        
    Returns:
        dict: OpenAI API response
        
    Raises:
        CircuitBreakerError: If circuit is open
        Exception: If API call fails
    """
    import openai
    from app.core.config import settings
    
    client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    response = await client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=temperature
    )
    
    return {
        "text": response.choices[0].message.content,
        "model": response.model,
        "usage": response.usage.dict()
    }


@circuit(
    failure_threshold=5,
    recovery_timeout=60,
    expected_exception=Exception,
    name="openai_whisper_circuit"
)
async def call_whisper_api(audio_file: bytes, language: str = "en") -> dict:
    """
    Circuit breaker protected Whisper STT API call
    
    Args:
        audio_file: Audio file bytes
        language: Language code
        
    Returns:
        dict: Transcription result
        
    Raises:
        CircuitBreakerError: If circuit is open
    """
    import openai
    from app.core.config import settings
    
    client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    # Whisper API requires file-like object
    from io import BytesIO
    audio_buffer = BytesIO(audio_file)
    audio_buffer.name = "audio.webm"
    
    response = await client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_buffer,
        language=language,
        response_format="json"
    )
    
    return {
        "text": response.text,
        "language": language
    }


# ==================== ElevenLabs Circuit Breaker ====================

@circuit(
    failure_threshold=3,      # More sensitive, TTS failures are critical
    recovery_timeout=30,      # Shorter timeout for faster recovery
    expected_exception=Exception,
    name="elevenlabs_circuit"
)
async def call_elevenlabs_api(
    text: str,
    voice: str = "Rachel",
    model_id: str = "eleven_multilingual_v2"
) -> bytes:
    """
    Circuit breaker protected ElevenLabs TTS API call
    
    Args:
        text: Text to synthesize
        voice: Voice ID or name
        model_id: ElevenLabs model
        
    Returns:
        bytes: Audio data
        
    Raises:
        CircuitBreakerError: If circuit is open
    """
    from elevenlabs import AsyncElevenLabs
    from app.core.config import settings
    
    client = AsyncElevenLabs(api_key=settings.ELEVENLABS_API_KEY)
    
    audio_generator = await client.generate(
        text=text,
        voice=voice,
        model=model_id,
        voice_settings={
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    )
    
    # Collect audio chunks
    chunks = []
    async for chunk in audio_generator:
        chunks.append(chunk)
    
    return b"".join(chunks)


# ==================== Graceful Degradation ====================

async def get_ai_response_with_fallback(
    prompt: str,
    user_id: Optional[str] = None
) -> dict:
    """
    Get AI response with graceful degradation
    
    Fallback strategy:
    1. Try OpenAI GPT-4
    2. If circuit is open, try cached response
    3. If no cache, return friendly error message
    
    Args:
        prompt: User prompt
        user_id: User ID for cache key
        
    Returns:
        dict: AI response with source indicator
    """
    try:
        # Try primary service
        response = await call_openai_api(prompt)
        return {
            "text": response["text"],
            "source": "openai",
            "success": True
        }
        
    except CircuitBreakerError:
        # Circuit is open, try fallback
        print("OpenAI circuit breaker is open, using fallback")
        
        # Try to get cached similar response
        cached = await get_cached_response(prompt)
        if cached:
            return {
                "text": cached,
                "source": "cache",
                "success": True,
                "warning": "Using cached response due to service issues"
            }
        
        # No cache available, return friendly message
        return {
            "text": "I'm experiencing some technical difficulties right now. Please try again in a moment.",
            "source": "fallback",
            "success": False,
            "error": "Service temporarily unavailable"
        }
        
    except Exception as e:
        print(f"AI service error: {e}")
        return {
            "text": "I encountered an error processing your request. Please try again.",
            "source": "error",
            "success": False,
            "error": str(e)
        }


async def get_voice_response_with_fallback(
    text: str,
    voice: str = "Rachel"
) -> dict:
    """
    Get voice synthesis with graceful degradation
    
    Fallback strategy:
    1. Try ElevenLabs
    2. If circuit is open, return text-only response
    
    Args:
        text: Text to synthesize
        voice: Voice to use
        
    Returns:
        dict: Voice response or text fallback
    """
    try:
        # Try primary TTS service
        audio_data = await call_elevenlabs_api(text, voice)
        return {
            "audio": audio_data,
            "text": text,
            "source": "elevenlabs",
            "success": True
        }
        
    except CircuitBreakerError:
        print("ElevenLabs circuit breaker is open, returning text-only")
        return {
            "audio": None,
            "text": text,
            "source": "text_only",
            "success": True,
            "warning": "Voice synthesis temporarily unavailable, showing text"
        }
        
    except Exception as e:
        print(f"TTS service error: {e}")
        return {
            "audio": None,
            "text": text,
            "source": "error",
            "success": False,
            "error": str(e),
            "warning": "Voice synthesis failed, showing text"
        }


async def get_cached_response(prompt: str) -> Optional[str]:
    """
    Get cached response for similar prompts
    
    This is a simple fallback mechanism. In production, you might use:
    - Semantic search in vector database
    - Pre-generated responses for common queries
    - Simpler local model (e.g., distilled GPT-2)
    
    Args:
        prompt: User prompt
        
    Returns:
        Optional[str]: Cached response if found
    """
    from app.core.cache import CacheManager
    
    # Simple cache key based on prompt
    cache_key = f"ai_response:{prompt[:100]}"  # Use first 100 chars
    
    cached = await CacheManager.get(cache_key)
    return cached.get("text") if cached else None


# ==================== Circuit Breaker Status ====================

def get_circuit_breaker_status() -> dict:
    """
    Get status of all circuit breakers
    
    Returns:
        dict: Status of each circuit breaker
    """
    from circuitbreaker import CircuitBreaker
    
    circuits = {
        "openai": CircuitBreaker.get("openai_circuit"),
        "whisper": CircuitBreaker.get("openai_whisper_circuit"),
        "elevenlabs": CircuitBreaker.get("elevenlabs_circuit")
    }
    
    status = {}
    for name, cb in circuits.items():
        if cb:
            status[name] = {
                "state": cb.current_state,
                "failure_count": cb.failure_count,
                "last_failure_time": cb.last_failure_time,
                "opened_at": cb.opened_at
            }
        else:
            status[name] = {"state": "not_initialized"}
    
    return status


# ==================== Monitoring Endpoint ====================

async def circuit_breaker_health() -> dict:
    """
    Health check for circuit breakers
    
    Returns:
        dict: Circuit breaker health status
    """
    status = get_circuit_breaker_status()
    
    # Check if any circuit is open
    any_open = any(
        cb.get("state") == CircuitState.OPEN.value 
        for cb in status.values()
    )
    
    return {
        "healthy": not any_open,
        "circuits": status,
        "timestamp": time.time()
    }

