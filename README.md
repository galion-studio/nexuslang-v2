# 🚀 Galion Voice API

**The first No-UI voice platform for the 22nd century**

Galion is a revolutionary voice-first platform that eliminates traditional user interfaces in favor of natural voice interaction. Built with cutting-edge AI and designed for the future.

## 🌟 Features

- 🎤 **Voice-First Interface** - No keyboard, no mouse, just voice
- 🤖 **AI-Powered Conversations** - Multi-provider AI integration (OpenAI, Anthropic, OpenRouter)
- 🔊 **High-Quality TTS** - Premium voice synthesis (OpenAI, ElevenLabs)
- 🔄 **Real-Time Streaming** - WebSocket-based voice communication
- 🏗️ **Microservices Architecture** - Scalable backend with FastAPI
- 🎨 **Modern Frontend** - Next.js with React and TypeScript
- 🐳 **Docker Ready** - Complete containerization for development and production
- 📊 **Monitoring** - Prometheus metrics and health checks
- 🔒 **Production Ready** - SSL, rate limiting, security headers

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 20+ (for local development)
- Python 3.11+ (for local development)

### 1. Clone the Repository

```bash
git clone https://github.com/galion-studio/nexuslang-v2.git
cd nexuslang-v2
```

### 2. Setup Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
# OPENAI_API_KEY=sk-proj-...
# OPENROUTER_API_KEY=sk-or-v1-...
# ELEVENLABS_API_KEY=sk_...
```

### 3. Start Development Environment

```bash
# Using Make (recommended)
make setup
make dev

# Or using Docker Compose directly
docker-compose up -d

# Or using scripts
./scripts/setup-dev.sh
```

### 4. Access Your Application

- **Voice Interface**: http://localhost:3003
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🏗️ Architecture

### Platforms

- **galion.app** - Main voice application (black screen, pulsing orb)
- **api.galion.app** - REST API and WebSocket endpoints
- **developer.galion.app** - IDE for NexusLang development

### Services

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   Database      │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│   (PostgreSQL)  │
│   localhost:3003│    │   localhost:8000│    │   localhost:5432│
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
                    ┌─────────────────┐
                    │   Redis Cache   │
                    │   localhost:6379│
                    └─────────────────┘
```

## 📚 Documentation

- [Getting Started](GET_STARTED_NOW.md) - Complete setup guide
- [API Documentation](v2/backend/README.md) - Backend API docs
- [Domain Setup](DOMAIN_SETUP.md) - Production deployment
- [Voice API Integration](galion-app/docs/VOICE_API_INTEGRATION.md) - Frontend integration
- [Deployment Guide](QUICK_DEPLOY.md) - Production deployment

## 🧪 Testing

```bash
# Run all tests
make test

# Run backend tests
make test-backend

# Run frontend tests
make test-frontend

# Check service health
make health
```

## 🚀 Deployment

### Development

```bash
make dev
```

### Production

```bash
# Using Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# Or using deployment script
./scripts/deploy-production.sh
```

### Manual Deployment

```bash
# Backend
cd v2/backend
pip install -r requirements.txt
python main_simple.py

# Frontend
cd galion-app
npm install
npm run dev
```

## 🔧 Development Commands

```bash
# Setup environment
make setup

# Start development
make dev

# Run tests
make test

# Format code
make format

# View logs
make logs

# Clean up
make clean

# Create backup
make backup
```

## 🔐 Environment Variables

See `.env.example` for all required configuration options.

### Required API Keys

- `OPENAI_API_KEY` - For STT and TTS
- `OPENROUTER_API_KEY` - For AI conversations
- `ELEVENLABS_API_KEY` - For premium TTS

## 📊 Monitoring

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001
- **Health Checks**: http://localhost:8000/health

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with ❤️ for the future of human-computer interaction
- Inspired by the vision of seamless voice-first computing
- Powered by cutting-edge AI technologies

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/galion-studio/nexuslang-v2/issues)
- **Discussions**: [GitHub Discussions](https://github.com/galion-studio/nexuslang-v2/discussions)
- **Documentation**: See our comprehensive docs in the `docs/` directory

---

**🌟 Ready to experience the future of computing? Start talking to Galion!**
