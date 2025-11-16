# 🚀 Galion Backend API

FastAPI-based backend for the Galion Voice API platform.

## Features

- 🚀 **FastAPI** - High-performance async web framework
- 🎤 **Voice Processing** - Real-time audio streaming and processing
- 🤖 **AI Integration** - Multi-provider AI conversations (OpenAI, Anthropic, OpenRouter)
- 🔊 **Text-to-Speech** - High-quality voice synthesis
- 🔄 **WebSocket Support** - Real-time bidirectional communication
- 📊 **Monitoring** - Prometheus metrics and health checks
- 🔒 **Security** - Rate limiting, CORS, input validation
- 🐳 **Docker Ready** - Containerized deployment

## Quick Start

### Using Docker (Recommended)

```bash
cd v2/backend
docker build -t galion-backend .
docker run -p 8000:8000 --env-file .env galion-backend
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
python main_simple.py
```

## API Endpoints

### REST Endpoints

- `GET /health` - Health check
- `GET /docs` - Interactive API documentation
- `GET /metrics` - Prometheus metrics

### WebSocket Endpoints

- `WS /ws/voice` - Voice streaming and AI conversations

### Message Protocol

#### Client → Server

```json
{
  "type": "audio_chunk",
  "audio": "base64_encoded_audio_data",
  "format": "webm",
  "sample_rate": 16000
}
```

#### Server → Client

```json
{
  "type": "transcription",
  "text": "Transcribed speech text"
}

{
  "type": "ai_response",
  "text": "AI generated response",
  "audio": "base64_encoded_audio_response"
}

{
  "type": "error",
  "message": "Error description"
}
```

## Configuration

### Environment Variables

See `.env.example` for complete configuration options.

### Required API Keys

```bash
OPENAI_API_KEY=sk-proj-...
OPENROUTER_API_KEY=sk-or-v1-...
ELEVENLABS_API_KEY=sk_...
```

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Code Quality

```bash
# Format code
black .
isort .

# Lint code
flake8 .
```

### API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.

## Architecture

### Core Components

- **Voice Processing**: Audio streaming, VAD, noise reduction
- **AI Integration**: Conversation management across multiple providers
- **Session Management**: Redis-based session storage
- **Monitoring**: Performance metrics and health checks
- **Security**: Rate limiting, input validation, CORS

### Service Structure

```
v2/backend/
├── api/                    # API endpoints
├── services/voice/         # Voice processing services
│   ├── audio_utils.py      # Audio processing utilities
│   ├── stt_service.py      # Speech-to-text
│   ├── tts_service.py      # Text-to-speech
│   ├── conversation_manager.py  # AI conversations
│   ├── error_handler.py    # Error handling
│   └── monitoring.py       # Metrics collection
├── core/                   # Core functionality
├── main_simple.py          # FastAPI application
├── requirements.txt        # Python dependencies
└── tests/                  # Test suite
```

## Deployment

### Docker Production

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "main_simple.py"]
```

### Systemd Service

```ini
[Unit]
Description=Galion Voice API
After=network.target

[Service]
User=galion
WorkingDirectory=/opt/galion/backend
ExecStart=/opt/galion/venv/bin/python main_simple.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## Monitoring

### Health Checks

```bash
curl http://localhost:8000/health
```

### Metrics

```bash
curl http://localhost:8000/metrics
```

### Logs

```bash
# View application logs
journalctl -u galion-backend -f

# View nginx logs
tail -f /var/log/nginx/galion_access.log
tail -f /var/log/nginx/galion_error.log
```

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   lsof -i :8000
   kill -9 <PID>
   ```

2. **API key errors**
   - Check `.env` file exists
   - Verify API keys are valid
   - Restart the service

3. **WebSocket connection fails**
   - Check nginx configuration
   - Verify SSL certificates
   - Check firewall settings

4. **High memory usage**
   - Monitor with `htop` or `docker stats`
   - Check for memory leaks in voice processing
   - Consider increasing server resources

### Debug Mode

Enable debug logging:

```bash
export LOG_LEVEL=DEBUG
python main_simple.py
```

## Contributing

1. Follow the existing code style
2. Add tests for new features
3. Update documentation
4. Create a pull request

## License

MIT License - see LICENSE file for details.
