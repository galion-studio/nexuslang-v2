# 🎙️ VOICE IMPLEMENTATION - BUILD & IMPLEMENT NOW

## 🚀 TRANSPARENT BUILD PROCESS

**Following Elon Musk's Principle**: "The best part is no part. The best process is no process."

This guide shows EXACTLY what we're building, line by line, with ZERO ambiguity.

---

## 📋 BUILD CHECKLIST

### ✅ PHASE 1: FOUNDATION (Start Here)

- [ ] Create voice service directory structure
- [ ] Install dependencies
- [ ] Setup FastAPI with WebSocket
- [ ] Integrate Whisper API (STT)
- [ ] Integrate ElevenLabs API (TTS)
- [ ] Test: Record audio → Get voice response
- [ ] Add to docker-compose
- [ ] Update API Gateway

### 🟡 PHASE 2: INTELLIGENCE

- [ ] Add GPT-4 intent classification
- [ ] Build action router
- [ ] Integrate with existing services
- [ ] Add conversation context
- [ ] Test all voice commands

### 🟡 PHASE 3: PRODUCTION

- [ ] Add authentication
- [ ] Add rate limiting
- [ ] Add analytics tracking
- [ ] Security audit
- [ ] Performance optimization
- [ ] Documentation

---

## 🛠️ STEP-BY-STEP IMPLEMENTATION

### **STEP 1: Create Directory Structure**

```bash
# Create voice service directories
mkdir -p services/voice-service/app/api/v1
mkdir -p services/voice-service/app/services
mkdir -p services/voice-service/app/models
mkdir -p services/voice-service/app/schemas
mkdir -p services/voice-service/app/middleware
mkdir -p services/voice-service/app/utils
mkdir -p services/voice-service/tests
mkdir -p services/voice-service/audio_samples
```

---

### **STEP 2: Create requirements.txt**

```txt
# services/voice-service/requirements.txt

# Core Framework
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6
websockets==12.0

# Audio Processing
pydub==0.25.1
soundfile==0.12.1
numpy==1.26.3
scipy==1.12.0

# AI & ML
openai==1.10.0
elevenlabs==0.2.26
httpx==0.26.0

# Database & Cache
sqlalchemy==2.0.25
asyncpg==0.29.0
redis==5.0.1
psycopg2-binary==2.9.9

# Event Streaming
aiokafka==0.10.0

# Authentication
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
pydantic==2.5.3
pydantic-settings==2.1.0

# Monitoring
prometheus-client==0.19.0

# Utilities
python-dotenv==1.0.0
```

---

### **STEP 3: Create Configuration**

```python
# services/voice-service/app/config.py

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
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
    ELEVENLABS_VOICE_ID: str = "21m00Tcm4TlvDq8ikWAM"  # Default voice
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
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

---

### **STEP 4: Create Main Application**

```python
# services/voice-service/app/main.py

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.api.v1 import voice, stt, tts
from prometheus_client import make_asgi_app

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info(f"Starting {settings.SERVICE_NAME} v{settings.SERVICE_VERSION}")
    yield
    logger.info(f"Shutting down {settings.SERVICE_NAME}")


# Create FastAPI app
app = FastAPI(
    title="Nexus Core Voice Service",
    description="Voice interface with STT, TTS, and intelligent intent routing",
    version=settings.SERVICE_VERSION,
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(voice.router, prefix="/api/v1/voice", tags=["voice"])
app.include_router(stt.router, prefix="/api/v1/voice", tags=["stt"])
app.include_router(tts.router, prefix="/api/v1/voice", tags=["tts"])

# Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Nexus Core Voice Service",
        "version": settings.SERVICE_VERSION,
        "endpoints": {
            "voice_stream": "/api/v1/voice/stream",
            "stt": "/api/v1/voice/stt",
            "tts": "/api/v1/voice/tts",
            "health": "/health",
            "metrics": "/metrics"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
```

---

### **STEP 5: Create STT Service**

```python
# services/voice-service/app/services/stt_service.py

import openai
from typing import Optional
import io
import logging
from pydub import AudioSegment

from app.config import settings

logger = logging.getLogger(__name__)

class STTService:
    """Speech-to-Text service using OpenAI Whisper"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_WHISPER_MODEL
    
    async def transcribe(
        self,
        audio_data: bytes,
        language: Optional[str] = None,
        format: str = "webm"
    ) -> dict:
        """
        Transcribe audio to text using Whisper
        
        Args:
            audio_data: Raw audio bytes
            language: ISO-639-1 language code (e.g., 'en', 'es')
            format: Audio format (webm, wav, mp3, etc.)
        
        Returns:
            dict: {
                "text": "transcribed text",
                "language": "en",
                "confidence": 0.95
            }
        """
        try:
            # Convert audio to appropriate format if needed
            if format != "wav":
                audio_data = self._convert_to_wav(audio_data, format)
            
            # Create file-like object
            audio_file = io.BytesIO(audio_data)
            audio_file.name = "audio.wav"
            
            # Transcribe using Whisper
            logger.info(f"Transcribing audio with Whisper (language: {language or 'auto'})")
            
            transcription = self.client.audio.transcriptions.create(
                model=self.model,
                file=audio_file,
                language=language,
                response_format="verbose_json"
            )
            
            result = {
                "text": transcription.text,
                "language": transcription.language,
                "confidence": self._calculate_confidence(transcription)
            }
            
            logger.info(f"Transcription successful: {result['text'][:50]}...")
            return result
            
        except Exception as e:
            logger.error(f"STT error: {e}")
            raise
    
    def _convert_to_wav(self, audio_data: bytes, from_format: str) -> bytes:
        """Convert audio to WAV format"""
        try:
            audio = AudioSegment.from_file(io.BytesIO(audio_data), format=from_format)
            
            # Convert to mono, 16kHz
            audio = audio.set_channels(settings.AUDIO_CHANNELS)
            audio = audio.set_frame_rate(settings.AUDIO_SAMPLE_RATE)
            
            # Export as WAV
            buffer = io.BytesIO()
            audio.export(buffer, format="wav")
            return buffer.getvalue()
        except Exception as e:
            logger.error(f"Audio conversion error: {e}")
            raise
    
    def _calculate_confidence(self, transcription) -> float:
        """Calculate confidence score from Whisper response"""
        # Whisper doesn't provide confidence directly
        # Use heuristics: word count, no hallucination markers
        text = transcription.text
        
        if not text or text.strip() == "":
            return 0.0
        
        # Basic heuristic
        confidence = 0.95
        
        # Reduce confidence for very short responses
        if len(text.split()) < 3:
            confidence -= 0.1
        
        # Reduce for common hallucination patterns
        hallucination_markers = ["thank you for watching", "subscribe", "[music]"]
        for marker in hallucination_markers:
            if marker.lower() in text.lower():
                confidence -= 0.2
        
        return max(0.0, min(1.0, confidence))


# Singleton instance
stt_service = STTService()
```

---

### **STEP 6: Create TTS Service**

```python
# services/voice-service/app/services/tts_service.py

from elevenlabs import generate, Voice, VoiceSettings
from typing import Optional, AsyncGenerator
import logging

from app.config import settings

logger = logging.getLogger(__name__)

class TTSService:
    """Text-to-Speech service using ElevenLabs"""
    
    def __init__(self):
        self.api_key = settings.ELEVENLABS_API_KEY
        self.voice_id = settings.ELEVENLABS_VOICE_ID
        self.model = settings.ELEVENLABS_MODEL
    
    async def synthesize(
        self,
        text: str,
        voice_id: Optional[str] = None,
        speed: float = 1.0,
        stability: float = 0.5,
        similarity_boost: float = 0.75,
        stream: bool = False
    ) -> bytes | AsyncGenerator[bytes, None]:
        """
        Convert text to speech using ElevenLabs
        
        Args:
            text: Text to convert to speech
            voice_id: ElevenLabs voice ID (uses default if None)
            speed: Speaking rate (0.5 - 2.0)
            stability: Voice stability (0.0 - 1.0)
            similarity_boost: Voice similarity (0.0 - 1.0)
            stream: Stream audio chunks if True
        
        Returns:
            bytes or AsyncGenerator[bytes]: Audio data
        """
        try:
            voice_id = voice_id or self.voice_id
            
            logger.info(f"Generating TTS for text: {text[:50]}...")
            
            # Generate audio
            audio = generate(
                text=text,
                voice=Voice(
                    voice_id=voice_id,
                    settings=VoiceSettings(
                        stability=stability,
                        similarity_boost=similarity_boost
                    )
                ),
                model=self.model,
                api_key=self.api_key,
                stream=stream
            )
            
            if stream:
                return self._stream_audio(audio)
            else:
                logger.info(f"TTS generation successful, audio size: {len(audio)} bytes")
                return audio
                
        except Exception as e:
            logger.error(f"TTS error: {e}")
            raise
    
    async def _stream_audio(self, audio_generator) -> AsyncGenerator[bytes, None]:
        """Stream audio chunks"""
        try:
            for chunk in audio_generator:
                yield chunk
        except Exception as e:
            logger.error(f"TTS streaming error: {e}")
            raise
    
    def get_available_voices(self) -> list:
        """Get list of available voices"""
        # This would query ElevenLabs API for available voices
        # For now, return defaults
        return [
            {"id": "21m00Tcm4TlvDq8ikWAM", "name": "Rachel", "category": "professional"},
            {"id": "MF3mGyEYCl7XYWbV9V6O", "name": "Adam", "category": "casual"},
            {"id": "ErXwobaYiN019PkySvjV", "name": "Antoni", "category": "technical"}
        ]


# Singleton instance
tts_service = TTSService()
```

---

### **STEP 7: Create Intent Service**

```python
# services/voice-service/app/services/intent_service.py

import httpx
import json
import logging
from typing import Dict, Optional

from app.config import settings

logger = logging.getLogger(__name__)

class IntentService:
    """Intent classification and entity extraction using GPT-4"""
    
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.model = settings.OPENROUTER_MODEL
        self.base_url = "https://openrouter.ai/api/v1"
        
        # Intent definitions
        self.intents = {
            "login": {
                "description": "User wants to login",
                "entities": ["email", "password"],
                "examples": ["login as john@example.com", "sign in", "log me in"]
            },
            "register": {
                "description": "User wants to register",
                "entities": ["email", "password", "name"],
                "examples": ["create account", "sign up", "register"]
            },
            "get_profile": {
                "description": "User wants to see their profile",
                "entities": [],
                "examples": ["show my profile", "my account", "who am i"]
            },
            "search_content": {
                "description": "User wants to search content",
                "entities": ["query"],
                "examples": ["search for AI", "find articles about", "look up"]
            },
            "research": {
                "description": "User wants deep research",
                "entities": ["query", "depth"],
                "examples": ["research quantum computing", "deep search", "investigate"]
            },
            "help": {
                "description": "User needs help",
                "entities": [],
                "examples": ["help", "what can you do", "commands"]
            }
        }
    
    async def classify_intent(
        self,
        text: str,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Classify user intent and extract entities
        
        Args:
            text: User's spoken text
            context: Conversation context
        
        Returns:
            dict: {
                "intent": "get_profile",
                "entities": {"name": "John"},
                "confidence": 0.95,
                "needs_clarification": false,
                "clarification_question": null
            }
        """
        try:
            # Build system prompt with intent definitions
            system_prompt = self._build_system_prompt()
            
            # Build user prompt
            user_prompt = f"User said: '{text}'"
            if context:
                user_prompt += f"\n\nContext: {json.dumps(context)}"
            
            # Call GPT-4 via OpenRouter
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "temperature": 0.3,
                        "max_tokens": 300
                    },
                    timeout=30.0
                )
            
            response.raise_for_status()
            result = response.json()
            
            # Parse intent from response
            intent_data = json.loads(result["choices"][0]["message"]["content"])
            
            logger.info(f"Intent classified: {intent_data['intent']} (confidence: {intent_data['confidence']})")
            
            return intent_data
            
        except Exception as e:
            logger.error(f"Intent classification error: {e}")
            # Return default "help" intent on error
            return {
                "intent": "help",
                "entities": {},
                "confidence": 0.5,
                "needs_clarification": True,
                "clarification_question": "I didn't understand that. Could you rephrase?"
            }
    
    def _build_system_prompt(self) -> str:
        """Build system prompt with intent definitions"""
        prompt = """You are Nexus Core's voice assistant. Classify user commands into intents and extract entities.

Available intents:\n"""
        
        for intent_name, intent_data in self.intents.items():
            prompt += f"\n- {intent_name}: {intent_data['description']}"
            prompt += f"\n  Entities: {', '.join(intent_data['entities']) if intent_data['entities'] else 'none'}"
            prompt += f"\n  Examples: {', '.join(intent_data['examples'][:2])}"
        
        prompt += """

Return ONLY valid JSON in this exact format:
{
    "intent": "intent_name",
    "entities": {"entity_name": "value"},
    "confidence": 0.95,
    "needs_clarification": false,
    "clarification_question": null
}

If you're not sure, set needs_clarification to true and provide a clarification_question."""
        
        return prompt


# Singleton instance
intent_service = IntentService()
```

---

### **STEP 8: Create Voice WebSocket Endpoint**

```python
# services/voice-service/app/api/v1/voice.py

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
import json
import logging
from typing import Optional

from app.services.stt_service import stt_service
from app.services.tts_service import tts_service
from app.services.intent_service import intent_service
from app.middleware.auth import verify_websocket_token

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/stream")
async def voice_stream(
    websocket: WebSocket,
    token: Optional[str] = None
):
    """
    WebSocket endpoint for real-time voice interaction
    
    Flow:
    1. Client connects with JWT token
    2. Client sends binary audio chunks
    3. Server transcribes (STT)
    4. Server classifies intent
    5. Server executes action
    6. Server generates response text
    7. Server converts to speech (TTS)
    8. Server sends audio back to client
    """
    await websocket.accept()
    
    try:
        # Verify authentication
        user_email = await verify_websocket_token(websocket, token)
        if not user_email:
            await websocket.close(code=1008, reason="Unauthorized")
            return
        
        logger.info(f"Voice WebSocket connected for user: {user_email}")
        
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "message": "Voice assistant ready. Start speaking!"
        })
        
        # Audio buffer for streaming
        audio_buffer = bytearray()
        
        while True:
            # Receive audio data from client
            data = await websocket.receive()
            
            if "bytes" in data:
                # Binary audio data
                audio_chunk = data["bytes"]
                audio_buffer.extend(audio_chunk)
                
                # Send acknowledgment
                await websocket.send_json({
                    "type": "receiving",
                    "buffer_size": len(audio_buffer)
                })
                
            elif "text" in data:
                # Text command (audio stream complete or text fallback)
                message = json.loads(data["text"])
                
                if message.get("type") == "audio_complete":
                    # Process complete audio
                    await process_voice_command(
                        websocket,
                        user_email,
                        bytes(audio_buffer),
                        message.get("format", "webm")
                    )
                    audio_buffer.clear()
                
                elif message.get("type") == "text_fallback":
                    # Process text command directly
                    await process_text_command(
                        websocket,
                        user_email,
                        message.get("text", "")
                    )
    
    except WebSocketDisconnect:
        logger.info(f"Voice WebSocket disconnected for user: {user_email}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })


async def process_voice_command(
    websocket: WebSocket,
    user_email: str,
    audio_data: bytes,
    audio_format: str
):
    """Process voice command through full pipeline"""
    try:
        # 1. Speech-to-Text
        await websocket.send_json({"type": "status", "message": "Transcribing..."})
        
        stt_result = await stt_service.transcribe(audio_data, format=audio_format)
        transcript = stt_result["text"]
        
        await websocket.send_json({
            "type": "transcript",
            "text": transcript,
            "confidence": stt_result["confidence"]
        })
        
        # 2. Intent Classification
        await websocket.send_json({"type": "status", "message": "Understanding..."})
        
        intent_result = await intent_service.classify_intent(transcript)
        
        await websocket.send_json({
            "type": "intent",
            "intent": intent_result["intent"],
            "entities": intent_result["entities"],
            "confidence": intent_result["confidence"]
        })
        
        # 3. Execute Action (placeholder - will route to services)
        await websocket.send_json({"type": "status", "message": "Processing..."})
        
        response_text = await execute_intent(
            user_email,
            intent_result["intent"],
            intent_result["entities"]
        )
        
        await websocket.send_json({
            "type": "response",
            "text": response_text
        })
        
        # 4. Text-to-Speech
        await websocket.send_json({"type": "status", "message": "Generating voice..."})
        
        audio_response = await tts_service.synthesize(response_text)
        
        # Send audio
        await websocket.send_json({"type": "audio_start"})
        await websocket.send_bytes(audio_response)
        await websocket.send_json({"type": "audio_complete"})
        
    except Exception as e:
        logger.error(f"Voice processing error: {e}")
        await websocket.send_json({
            "type": "error",
            "message": "Sorry, I encountered an error processing your request."
        })


async def process_text_command(
    websocket: WebSocket,
    user_email: str,
    text: str
):
    """Process text command (skip STT)"""
    try:
        # Intent classification
        intent_result = await intent_service.classify_intent(text)
        
        await websocket.send_json({
            "type": "intent",
            "intent": intent_result["intent"],
            "entities": intent_result["entities"]
        })
        
        # Execute action
        response_text = await execute_intent(
            user_email,
            intent_result["intent"],
            intent_result["entities"]
        )
        
        await websocket.send_json({
            "type": "response",
            "text": response_text
        })
        
        # TTS
        audio_response = await tts_service.synthesize(response_text)
        await websocket.send_json({"type": "audio_start"})
        await websocket.send_bytes(audio_response)
        await websocket.send_json({"type": "audio_complete"})
        
    except Exception as e:
        logger.error(f"Text processing error: {e}")
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })


async def execute_intent(user_email: str, intent: str, entities: dict) -> str:
    """
    Execute intent by calling appropriate service
    (Placeholder - will be implemented with full service integration)
    """
    # TODO: Integrate with actual services
    
    responses = {
        "get_profile": f"Your profile shows you're logged in as {user_email}.",
        "help": "I can help you with login, search, research, and managing your profile. What would you like to do?",
        "search_content": f"Searching for: {entities.get('query', 'content')}...",
        "research": f"Starting research on: {entities.get('query', 'topic')}...",
        "login": "Please provide your email and password.",
        "register": "Let's create your account. What's your email?"
    }
    
    return responses.get(intent, "I'm not sure how to help with that yet.")
```

---

## 📝 NEXT STEPS

1. **Create the files** listed above
2. **Update `.env`** with API keys:
   ```
   OPENAI_API_KEY=your_openai_key
   ELEVENLABS_API_KEY=your_elevenlabs_key
   OPENROUTER_API_KEY=your_openrouter_key
   ```
3. **Build Docker container**:
   ```bash
   cd services/voice-service
   docker build -t nexus-voice:latest .
   ```
4. **Add to docker-compose.yml**
5. **Test WebSocket**:
   ```bash
   wscat -c "ws://localhost:8003/api/v1/voice/stream"
   ```

---

## ✅ VERIFICATION

After implementation, verify:
- [ ] Voice service starts successfully
- [ ] WebSocket accepts connections
- [ ] Audio can be sent/received
- [ ] STT transcribes correctly
- [ ] Intent classification works
- [ ] TTS generates audio
- [ ] End-to-end latency < 3 seconds

---

**Status**: 📝 DOCUMENTATION COMPLETE, READY TO BUILD

**Next**: Start creating the actual service files.

