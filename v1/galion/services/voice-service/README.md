# 🎙️ Nexus Core Voice Service

**Talk to Nexus like you talk to JARVIS**

The Voice Service provides real-time speech-to-text, text-to-speech, and intelligent intent routing for Nexus Core.

---

## ✨ Features

- **🎤 Speech-to-Text**: Convert voice to text using OpenAI Whisper
- **🔊 Text-to-Speech**: Generate natural-sounding voice responses with ElevenLabs
- **🧠 Intent Understanding**: Classify user intents with GPT-4
- **🎯 Action Routing**: Execute actions across all Nexus services
- **⚡ Real-time**: WebSocket-based streaming for low latency
- **🔒 Secure**: JWT authentication for all voice endpoints
- **📊 Monitored**: Prometheus metrics and health checks

---

## 🚀 Quick Start

### Prerequisites
- OpenAI API key (for Whisper)
- ElevenLabs API key (for TTS)
- OpenRouter API key (for intent classification)

### 1. Add API Keys to .env
```bash
OPENAI_API_KEY=sk-your-key-here
ELEVENLABS_API_KEY=your-key-here
OPENROUTER_API_KEY=your-key-here
```

### 2. Build and Run
```bash
docker-compose build voice-service
docker-compose up -d voice-service
```

### 3. Test
```bash
# Check health
curl http://localhost:8003/health

# Try WebSocket (with JWT token)
wscat -c "ws://localhost:8003/api/v1/voice/stream?token=YOUR_JWT"
```

---

## 📡 API Endpoints

### WebSocket: Voice Streaming
```
WS /api/v1/voice/stream?token=JWT_TOKEN
```
Real-time voice interaction with full pipeline (STT → Intent → Action → TTS)

### POST: Speech-to-Text
```
POST /api/v1/voice/stt
Content-Type: multipart/form-data

audio: <audio_file>
language: en (optional)
```

### POST: Text-to-Speech
```
POST /api/v1/voice/tts
Content-Type: application/json

{
  "text": "Hello from Nexus Core",
  "voice_id": null,
  "speed": 1.0
}
```

### GET: Available Voices
```
GET /api/v1/voice/voices
```

---

## 🎤 Voice Commands

### Authentication
- "Login as user@example.com password mypass"
- "Show my profile"
- "Logout"

### Search
- "Search for articles about AI"
- "Find users named Sarah"

### Research
- "Research quantum computing"

### Help
- "Help"
- "What can you do"
- "System status"

See [VOICE_COMMANDS_REFERENCE.md](../../VOICE_COMMANDS_REFERENCE.md) for complete list.

---

## 🏗️ Architecture

```
Audio Input → WebSocket → Voice Service
                              ↓
                   ┌──────────┼──────────┐
                   ↓          ↓          ↓
                Whisper    GPT-4    ElevenLabs
                  STT     Intent       TTS
                   ↓          ↓          ↓
                Text → Action Router → Audio
                              ↓
                       Other Services
                    (Auth, User, Content)
```

---

## 🛠️ Tech Stack

- **Framework**: FastAPI (async, WebSocket)
- **STT**: OpenAI Whisper API
- **TTS**: ElevenLabs API
- **NLU**: GPT-4 via OpenRouter
- **Audio**: pydub, soundfile
- **Database**: PostgreSQL (for voice logs)
- **Cache**: Redis (for context)
- **Events**: Kafka (for analytics)

---

## 📊 Monitoring

### Prometheus Metrics
```
/metrics
```

Metrics exposed:
- `voice_requests_total` - Total voice requests
- `voice_latency_seconds` - Request latency by phase
- `active_voice_sessions` - Current active sessions
- `intent_accuracy` - Intent recognition accuracy

### Health Check
```
GET /health
```

Returns service status and feature availability.

---

## 🧪 Development

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run with hot reload
python -m uvicorn app.main:app --reload --port 8003
```

### Testing
```bash
# Run tests
pytest tests/

# Test STT
curl -X POST http://localhost:8003/api/v1/voice/stt \
  -F "audio=@test.wav"

# Test TTS
curl -X POST http://localhost:8003/api/v1/voice/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello World"}' \
  --output test_output.mp3
```

---

## 🔒 Security

- **Authentication**: JWT required for all endpoints
- **Rate Limiting**: 100 requests/hour per user
- **Audio Size Limit**: 10MB max
- **Duration Limit**: 30 seconds max
- **Data Privacy**: Audio not stored (unless opted-in)

---

## 💰 Cost Estimates

**Per 1000 voice interactions** (avg 10s query, 50-word response):
- Whisper STT: $0.06 (10s × $0.006/min)
- GPT-4 Intent: ~$2
- ElevenLabs TTS: $15 (50 words × $0.30/1000 chars)
- **Total**: ~$17 per 1000 interactions

**Cost optimization**:
- Use OpenAI TTS instead: $1.50 (67% cheaper)
- Cache common responses
- Batch intent classification

---

## 📚 Documentation

- [Voice Quickstart](../../VOICE_QUICKSTART.md)
- [Voice Commands Reference](../../VOICE_COMMANDS_REFERENCE.md)
- [Voice API Reference](../../VOICE_API_REFERENCE.md)
- [First Principles Plan](../../VOICE_FIRST_PRINCIPLES_PLAN.md)

---

## 🐛 Troubleshooting

### Service won't start
```bash
# Check logs
docker logs nexus-voice

# Check API keys
docker exec nexus-voice printenv | grep API_KEY
```

### Poor STT accuracy
- Use high-quality microphone
- Minimize background noise
- Speak clearly at normal pace
- Use push-to-talk mode

### Slow responses
- Check internet speed
- Verify API service status
- Use shorter commands
- Monitor latency metrics

---

## 🤝 Contributing

Voice Service follows Nexus Core's contribution guidelines. See main repo README.

---

## 📄 License

Part of Nexus Core platform.

---

**Status**: ✅ Production Ready

**Version**: 1.0.0

**Built with**: Elon Musk's First Principles

