# 🔧 Nexus Backend - FastAPI Application Server

**Advanced AI-powered backend system with multi-agent orchestration**

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [API Documentation](#api-documentation)
- [Configuration](#configuration)
- [Development](#development)
- [Deployment](#deployment)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

The Nexus Backend is a high-performance FastAPI application that powers the entire Project Nexus platform. It provides:

- 🤖 Multi-agent AI orchestration
- 🔬 Scientific research APIs (Grokopedia)
- 💬 NexusLang programming interface
- 🎤 Voice AI processing
- 📊 Analytics and monitoring
- 🔐 Authentication and authorization

### Tech Stack

- **FastAPI** 0.100+ - Modern Python web framework
- **Python** 3.8+ - Programming language
- **PostgreSQL** 13+ - Primary database
- **Redis** 6+ - Caching and sessions
- **SQLAlchemy** - ORM
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation

---

## ✨ Features

### Core APIs

1. **Grokopedia** - Deep scientific knowledge system
   - First principles analysis
   - Multi-domain research
   - Knowledge integration
   - Citation management

2. **NexusLang** - Natural language programming
   - Code generation from English
   - Multi-language support
   - AI-assisted development
   - Real-time compilation

3. **Voice AI** - Speech processing
   - Speech-to-text (STT)
   - Text-to-speech (TTS)
   - Voice training
   - Real-time processing

4. **Research Tools**
   - Research templates
   - History tracking
   - Collaboration features
   - Export capabilities

### System Features

- **Multi-Agent System** - Coordinated AI specialists
- **Authentication** - JWT-based auth with RBAC
- **Rate Limiting** - Protect against abuse
- **Caching** - Redis-based performance optimization
- **Monitoring** - Health checks and metrics
- **Error Tracking** - Comprehensive error handling

---

## 🏗️ Architecture

### Directory Structure

```
v2/backend/
├── api/                    # API endpoints
│   ├── __init__.py
│   ├── grokopedia.py      # Scientific knowledge API
│   ├── nexuslang.py       # NexusLang compiler API
│   ├── voice.py           # Voice processing API
│   ├── auth.py            # Authentication
│   ├── users.py           # User management
│   ├── research_templates.py
│   ├── research_history.py
│   └── ...
│
├── core/                   # Core utilities
│   ├── __init__.py
│   ├── config.py          # Configuration
│   ├── database.py        # Database connection
│   ├── auth.py            # Auth utilities
│   ├── cache.py           # Redis caching
│   ├── security.py        # Security utilities
│   ├── monitoring.py      # Health checks
│   └── ...
│
├── models/                 # Database models
│   ├── __init__.py
│   ├── user.py
│   ├── research.py
│   ├── knowledge.py
│   └── ...
│
├── services/               # Business logic
│   ├── agents/            # AI agent system
│   │   ├── agent_orchestrator.py
│   │   ├── scientific_agents.py
│   │   └── ...
│   ├── auth/              # Authentication
│   ├── voice/             # Voice processing
│   ├── integrations/      # External integrations
│   ├── deep_search/       # Deep search engine
│   └── ...
│
├── migrations/             # Database migrations
│   ├── 001_initial_schema.sql
│   ├── 002_beta_testing.sql
│   └── ...
│
├── scripts/                # Utility scripts
│   ├── setup_database.py
│   ├── seed_database.py
│   └── ...
│
├── tests/                  # Test files
│   ├── test_api_grokopedia.py
│   ├── test_auth.py
│   └── ...
│
├── main.py                 # Application entry point
├── main_simple.py          # Simplified server
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker configuration
└── README.md              # This file
```

### Request Flow

```
Client Request
     │
     ▼
[NGINX/Reverse Proxy]
     │
     ▼
[FastAPI Application]
     │
     ├──→ [Middleware] (CORS, Auth, Rate Limiting)
     │
     ├──→ [API Router] (Route to endpoint)
     │
     ├──→ [Service Layer] (Business logic)
     │         │
     │         ├──→ [AI Agents] (Multi-agent processing)
     │         │
     │         ├──→ [Database] (PostgreSQL)
     │         │
     │         └──→ [Cache] (Redis)
     │
     └──→ [Response] (JSON formatted)
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- PostgreSQL 13 or higher
- Redis 6 or higher
- pip (Python package manager)

### Installation

```bash
# Navigate to backend directory
cd v2/backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Set up database
python scripts/setup_database.py

# Run database migrations
psql -U postgres -d nexus < migrations/001_initial_schema.sql
```

### Running the Server

#### Development Mode

```bash
# Standard server
python main.py

# Or with uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Simplified server (fewer dependencies)
python main_simple.py
```

#### Production Mode

```bash
# Single worker
uvicorn main:app --host 0.0.0.0 --port 8000

# Multiple workers (recommended)
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# With SSL (production)
uvicorn main:app --host 0.0.0.0 --port 443 \
  --ssl-keyfile=/path/to/key.pem \
  --ssl-certfile=/path/to/cert.pem
```

### Verify Installation

```bash
# Health check
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","timestamp":"2025-11-14T20:00:00Z",...}

# API documentation
open http://localhost:8000/docs
```

---

## 📚 API Documentation

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Main Endpoints

#### Core Endpoints

```
GET  /                    # Root information
GET  /health             # Health check
GET  /system-info        # System information
```

#### Grokopedia (Scientific Knowledge)

```
POST /api/v1/grokopedia/scientific-query
     # Submit scientific query

POST /api/v1/grokopedia/first-principles-analysis
     # Analyze topic with first principles

POST /api/v1/grokopedia/scientific-validation
     # Validate scientific claims

GET  /api/v1/grokopedia/scientific-capabilities
     # Get system capabilities

GET  /api/v1/grokopedia/scientific-health
     # Check Grokopedia health
```

#### NexusLang (Programming)

```
POST /api/v1/nexuslang/compile
     # Compile NexusLang to target language

POST /api/v1/nexuslang/execute
     # Execute NexusLang code

GET  /api/v1/nexuslang/examples
     # Get example code
```

#### Voice AI

```
POST /api/v1/voice/speech-to-text
     # Convert speech to text

POST /api/v1/voice/text-to-speech
     # Convert text to speech

POST /api/v1/voice/train
     # Train voice model
```

#### Authentication

```
POST /api/v1/auth/register
     # Register new user

POST /api/v1/auth/login
     # Login user

POST /api/v1/auth/refresh
     # Refresh access token

POST /api/v1/auth/logout
     # Logout user
```

### API Example

```python
import requests

# Submit scientific query
response = requests.post(
    "http://localhost:8000/api/v1/grokopedia/scientific-query",
    json={
        "query": "Explain quantum entanglement using first principles",
        "domain": "physics",
        "depth": "extremely_deep"
    },
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)

result = response.json()
print(result["analysis"])
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```bash
# Server Configuration
HOST=0.0.0.0
PORT=8000
WORKERS=4
DEBUG=false
LOG_LEVEL=info

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/nexus
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=40

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_CACHE_TTL=3600

# Security
SECRET_KEY=your-secret-key-here-change-this
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=60
REFRESH_TOKEN_EXPIRATION_DAYS=30

# AI/ML APIs
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# CORS
ALLOWED_ORIGINS=http://localhost:3000,https://galion.studio

# Monitoring
SENTRY_DSN=your-sentry-dsn
ENABLE_METRICS=true

# File Storage
UPLOAD_DIR=/path/to/uploads
MAX_UPLOAD_SIZE=10485760  # 10MB
```

### Configuration Class

```python
# core/config.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    debug: bool = False
    
    # Database
    database_url: str
    
    # Redis
    redis_url: str
    
    # Security
    secret_key: str
    jwt_algorithm: str = "HS256"
    
    class Config:
        env_file = ".env"

settings = Settings()
```

---

## 💻 Development

### Setting Up Development Environment

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run linters
black .
flake8
mypy .

# Run formatters
isort .
autopep8 --in-place --recursive .
```

### Code Style

We follow PEP 8 and use these tools:

- **Black** - Code formatting
- **isort** - Import sorting
- **Flake8** - Linting
- **MyPy** - Type checking

### Adding New Endpoints

1. **Create API router** in `api/`:

```python
# api/my_feature.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel

router = APIRouter()

class MyRequest(BaseModel):
    data: str

@router.post("/my-endpoint")
async def my_endpoint(request: MyRequest):
    return {"result": process_data(request.data)}
```

2. **Include router** in `main.py`:

```python
from api.my_feature import router as my_feature_router

app.include_router(
    my_feature_router,
    prefix="/api/v1/my-feature",
    tags=["my-feature"]
)
```

3. **Add tests** in `tests/`:

```python
# tests/test_my_feature.py
def test_my_endpoint():
    response = client.post("/api/v1/my-feature/my-endpoint", json={
        "data": "test"
    })
    assert response.status_code == 200
```

### Database Migrations

```bash
# Create new migration
cat > migrations/003_my_feature.sql << 'EOF'
-- Migration: Add my_feature table
CREATE TABLE my_feature (
    id SERIAL PRIMARY KEY,
    data TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
EOF

# Apply migration
psql -U postgres -d nexus < migrations/003_my_feature.sql
```

---

## 🐳 Deployment

### Docker

```bash
# Build image
docker build -t nexus-backend .

# Run container
docker run -d \
  --name nexus-backend \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  -e REDIS_URL=redis://... \
  nexus-backend
```

### Docker Compose

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/nexus
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: nexus
      POSTGRES_PASSWORD: password
  
  redis:
    image: redis:6
```

### RunPod

```bash
# On RunPod SSH terminal
cd /workspace/project-nexus/v2/backend

# Set environment
export PYTHONPATH=/workspace/project-nexus:/workspace/project-nexus/v2
export PORT=8080

# Start server
python -m uvicorn main:app --host 0.0.0.0 --port 8080 --workers 2
```

See [RUNPOD_SSH_INSTRUCTIONS.md](../../RUNPOD_SSH_INSTRUCTIONS.md) for complete guide.

---

## 🧪 Testing

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_api_grokopedia.py

# Specific test
pytest tests/test_api_grokopedia.py::test_scientific_query

# With coverage
pytest --cov=. --cov-report=html

# Watch mode (requires pytest-watch)
ptw
```

### Writing Tests

```python
# tests/test_my_feature.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_my_endpoint_success():
    """Test successful request"""
    response = client.post("/api/v1/my-feature/endpoint", json={
        "data": "test"
    })
    assert response.status_code == 200
    assert response.json()["success"] == True

def test_my_endpoint_validation_error():
    """Test validation error"""
    response = client.post("/api/v1/my-feature/endpoint", json={})
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_async_function():
    """Test async function"""
    result = await my_async_function()
    assert result is not None
```

---

## 🔧 Troubleshooting

### Common Issues

#### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 PID
```

#### Database Connection Error

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -U postgres -d nexus -c "SELECT 1;"

# Check DATABASE_URL in .env
cat .env | grep DATABASE_URL
```

#### Import Errors

```bash
# Set PYTHONPATH
export PYTHONPATH=/path/to/project-nexus:/path/to/project-nexus/v2

# Or add to .env
echo "PYTHONPATH=/path/to/project-nexus:/path/to/project-nexus/v2" >> .env
```

#### Redis Connection Error

```bash
# Check Redis is running
redis-cli ping

# Should return: PONG

# Check REDIS_URL in .env
cat .env | grep REDIS_URL
```

### Debug Mode

```bash
# Enable debug mode
export DEBUG=true
export LOG_LEVEL=debug

# Run with debug logging
python main.py
```

### Logs

```bash
# View application logs
tail -f logs/application.log

# View error logs
tail -f logs/error.log

# View access logs
tail -f logs/access.log
```

---

## 📊 Performance

### Optimization Tips

1. **Use Redis caching** for frequently accessed data
2. **Database connection pooling** - Configure pool size
3. **Async operations** - Use async/await where possible
4. **Query optimization** - Use indexes and efficient queries
5. **Rate limiting** - Protect against abuse
6. **Load balancing** - Multiple workers
7. **CDN** - For static assets

### Monitoring

```bash
# Health check endpoint
curl http://localhost:8000/health

# System info
curl http://localhost:8000/system-info

# Metrics (if enabled)
curl http://localhost:8000/metrics
```

---

## 📄 License

MIT License - see LICENSE file for details.

---

## 🙏 Support

- **Documentation**: See [main README](../../README.md)
- **Issues**: [GitHub Issues](https://github.com/galion-studio/nexuslang-v2/issues)
- **Email**: support@galion.studio

---

**Built with ❤️ by the Galion Studio team**

**Version**: 2.0.0  
**Last Updated**: November 14, 2025

