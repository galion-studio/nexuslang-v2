# 🎤 Voice Service

## Overview
The Voice Service enables voice interactions with Nexus Core, providing real-time speech recognition, natural language understanding, and voice synthesis. Talk to Nexus like you talk to JARVIS!

**Technology:** Python 3.11, FastAPI, WebSocket, OpenAI Whisper, ElevenLabs  
**Port:** 8003  
**Status:** Beta (AI Features)

## Core Responsibilities
- ✅ Speech-to-Text (STT) via OpenAI Whisper
- ✅ Text-to-Speech (TTS) via ElevenLabs
- ✅ Intent recognition with AI
- ✅ WebSocket streaming for real-time audio
- ✅ Voice command routing
- ✅ Multi-language support

## Architecture

### Technology Stack
```
Framework:    FastAPI (Python 3.11)
STT:          OpenAI Whisper API
TTS:          ElevenLabs API
AI:           OpenRouter (intent recognition)
Streaming:    WebSocket
```

### External APIs
- **OpenAI Whisper** - Speech-to-Text
- **ElevenLabs** - Text-to-Speech
- **OpenRouter** - Intent recognition (LLM)

## Features

### 1. Speech-to-Text (STT)
**Endpoint:** `POST /api/v1/voice/stt`

Convert audio to text using OpenAI Whisper.

**Supported Formats:**
- WAV, MP3, M4A, WebM, OGG
- Max file size: 25MB
- Sample rates: 8kHz - 48kHz

**Example:**
```bash
curl -X POST http://localhost:8003/api/v1/voice/stt \
  -F "file=@audio.wav" \
  -F "language=en"
```

### 2. Text-to-Speech (TTS)
**Endpoint:** `POST /api/v1/voice/tts`

Convert text to natural-sounding speech.

**Example:**
```bash
curl -X POST http://localhost:8003/api/v1/voice/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello from Nexus!", "voice": "default"}' \
  --output speech.mp3
```

### 3. WebSocket Streaming
**Endpoint:** `WS /api/v1/voice/stream`

Real-time bi-directional voice communication.

**Flow:**
1. Client connects to WebSocket
2. Client sends audio chunks (base64 encoded)
3. Server transcribes in real-time
4. Server detects intent
5. Server executes action
6. Server returns audio response

### 4. Supported Voice Commands

**User Profile:**
- "Show my profile"
- "Update my name to..."
- "What's my email?"

**Search:**
- "Search for users named John"
- "Find user with email..."
- "Show all users"

**Authentication:**
- "Log me out"
- "Who am I?"

## Configuration

### Environment Variables
```bash
# Server
PORT=8003
HOST=0.0.0.0

# APIs
OPENAI_API_KEY=sk-...
ELEVENLABS_API_KEY=...
OPENROUTER_API_KEY=sk-or-...

# Features
ENABLE_STT=true
ENABLE_TTS=true
ENABLE_INTENT=true

# Audio
MAX_AUDIO_SIZE_MB=25
SUPPORTED_FORMATS=wav,mp3,webm,ogg
```

## API Documentation

### Interactive Docs
- **Swagger UI:** http://localhost:8003/docs
- **HTML Docs:** [voice-service.html](../api-docs/voice-service.html)

## Monitoring

### Health Check
```bash
GET /health

Response:
{
  "status": "healthy",
  "service": "voice-service",
  "version": "1.0.0",
  "features": {
    "stt": true,
    "tts": true,
    "intent": true
  }
}
```

## Performance

| Metric | Value |
|--------|-------|
| STT Latency | ~2-5 seconds (depends on audio length) |
| TTS Latency | ~1-3 seconds |
| WebSocket Latency | < 100ms (streaming) |
| Max Concurrent Connections | 100 |

## Error Handling

| Status | Error | Description |
|--------|-------|-------------|
| 400 | Bad Request | Invalid audio format |
| 413 | Payload Too Large | Audio exceeds 25MB |
| 422 | Unprocessable Entity | Audio quality too low |
| 500 | Internal Server Error | STT/TTS API error |
| 503 | Service Unavailable | External API down |

## Development

### Local Setup
```bash
cd services/voice-service

# Install dependencies
pip install -r requirements.txt

# Set API keys
export OPENAI_API_KEY=sk-...
export ELEVENLABS_API_KEY=...

# Run service
uvicorn app.main:app --reload --port 8003
```

## Future Enhancements
- 🔜 Real-time voice cloning
- 🔜 Multi-speaker support
- 🔜 Voice emotion detection
- 🔜 Background noise cancellation
- 🔜 Voice biometrics authentication

---

**Last Updated:** November 9, 2024  
**Service Version:** 1.0.0  
**Status:** ✅ Beta

