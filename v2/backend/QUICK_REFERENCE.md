# ⚡ QUICK REFERENCE - Galion Voice API

**Essential commands and information at a glance**

---

## 🚀 Start Commands

```bash
# Backend
cd v2/backend
python main.py

# Frontend
cd galion-app
npm run dev

# Redis
docker run -d -p 6379:6379 redis

# Interactive Demo
python v2/backend/demo_voice_api.py
```

---

## 🔑 Environment Variables

Create `v2/backend/.env`:

```bash
# Required API Keys
OPENAI_API_KEY=sk-proj-...
OPENROUTER_API_KEY=sk-or-v1-...
ELEVENLABS_API_KEY=sk_...

# AI Settings
DEFAULT_AI_PROVIDER=openrouter
DEFAULT_AI_MODEL=anthropic/claude-3.5-sonnet

# TTS Settings
DEFAULT_TTS_PROVIDER=openai
DEFAULT_VOICE=alloy

# Server
HOST=0.0.0.0
PORT=8000
```

---

## 📡 API Endpoints

### REST Endpoints
- `GET /health` - Health check
- `GET /docs` - API documentation
- `POST /api/v1/stt` - Speech-to-text
- `POST /api/v1/tts` - Text-to-speech

### WebSocket
- `WS /ws/voice` - Real-time voice streaming

---

## 🎤 WebSocket Protocol

### Client → Server

```json
{
  "type": "audio_chunk",
  "audio": "base64_encoded_audio",
  "format": "webm",
  "sample_rate": 16000
}
```

### Server → Client

```json
{
  "type": "transcription",
  "text": "User said this"
}

{
  "type": "ai_response",
  "text": "AI says this",
  "audio": "base64_audio"
}
```

---

## 🧪 Testing

```bash
# Run all tests
pytest v2/backend/tests/

# Test specific module
pytest v2/backend/tests/test_voice_integration.py

# Interactive demo
python v2/backend/demo_voice_api.py
```

---

## 📊 Monitoring

View metrics at:
- `http://localhost:8000/metrics` - Prometheus metrics
- `http://localhost:8000/health` - Health status

---

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| Redis connection error | Start Redis: `docker run -d -p 6379:6379 redis` |
| API key errors | Check `.env` file, restart backend |
| Port in use | Change PORT in `.env` |
| Module not found | `pip install -r requirements.txt` |

---

## 📦 Project Structure

```
v2/backend/
├── api/                    # API endpoints
├── services/voice/         # Voice processing
│   ├── conversation_manager.py  # AI integration
│   ├── stt_service.py          # Speech-to-text
│   ├── tts_service.py          # Text-to-speech
│   ├── error_handler.py        # Error handling
│   └── monitoring.py           # Metrics
├── main.py                 # FastAPI app
└── requirements.txt        # Dependencies
```

---

## 🔐 Security Notes

- `.env` is in `.gitignore` - safe from git
- Never commit API keys
- Use environment variables in production
- Enable HTTPS for production

---

## 📚 Full Documentation

- `GET_STARTED_NOW.md` - Setup guide
- `PHASE_2_COMPLETE_SUMMARY.md` - Feature list
- `ULTIMATE_VOICE_API_COMPLETE.md` - Full overview
- `v2/backend/ENVIRONMENT_SETUP.md` - Detailed setup

---

**Need more help? Check all `.md` files in the project!**

