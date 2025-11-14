# 🧠 Nexus Lang V2 - Master Documentation

**Advanced Scientific Knowledge Enhancement Platform with AI-Powered Multi-Agent System**

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Platform Components](#platform-components)
- [Documentation Index](#documentation-index)
- [Quick Start Guides](#quick-start-guides)
- [Core Features](#core-features)
- [API Reference](#api-reference)
- [Deployment Options](#deployment-options)
- [Development Workflow](#development-workflow)
- [Integration Guide](#integration-guide)
- [Troubleshooting](#troubleshooting)
- [Resources](#resources)

---

## 🎯 Overview

Nexus Lang V2 is a next-generation scientific knowledge platform that combines:

- 🤖 **Multi-Agent AI System** - Coordinated specialist agents
- 🔬 **Grokopedia** - Deep scientific knowledge engine
- 💬 **NexusLang** - Natural language programming
- 🎤 **Voice AI** - Speech-to-text and text-to-speech
- 📊 **Research Tools** - Templates, history, collaboration
- 🌐 **Full-Stack Platform** - Backend, frontend, mobile

### Philosophy

We believe in **extremely deep understanding** through:
- First principles thinking
- Multi-domain knowledge synthesis
- Cross-agent collaboration
- Transparent reasoning processes
- Scientific rigor and validation

---

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         NEXUS LANG V2 PLATFORM                      │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                          CLIENT LAYER                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │   Web App    │  │  Mobile App  │  │     CLI      │             │
│  │  (Next.js)   │  │ (React Native)│  │   (Python)   │             │
│  │              │  │              │  │              │             │
│  │  📖 frontend/│  │              │  │              │             │
│  │     README   │  │              │  │              │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        API GATEWAY                                  │
│                    FastAPI + NGINX + CORS                           │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        BACKEND SERVICES                             │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  CORE APIs                        📖 backend/README         │  │
│  │  ├── Grokopedia (Scientific)                               │  │
│  │  ├── NexusLang (Programming)                               │  │
│  │  ├── Voice AI (STT/TTS)                                    │  │
│  │  ├── Research Tools                                        │  │
│  │  └── User Management                                       │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  AI AGENT SYSTEM                  📖 SCIENTIFIC_README     │  │
│  │  ├── Agent Orchestrator                                    │  │
│  │  ├── Scientific Agents (Physics, Chemistry, etc.)          │  │
│  │  ├── First Principles Engine                               │  │
│  │  ├── Knowledge Integrator                                  │  │
│  │  └── Deep Search Engine                                    │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  SUPPORTING SERVICES                                        │  │
│  │  ├── Authentication & Authorization                         │  │
│  │  ├── Rate Limiting & Caching                               │  │
│  │  ├── Analytics & Monitoring                                │  │
│  │  ├── Background Jobs                                       │  │
│  │  └── Error Tracking                                        │  │
│  └─────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         DATA LAYER                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │  PostgreSQL  │  │     Redis    │  │  Vector DB   │             │
│  │   (Primary)  │  │    (Cache)   │  │ (Embeddings) │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
└─────────────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer | Technologies |
|-------|-------------|
| **Frontend** | Next.js 13+, React 18+, TypeScript, Tailwind CSS |
| **Backend** | FastAPI, Python 3.8+, Uvicorn, SQLAlchemy |
| **AI/ML** | OpenAI GPT-4, LangChain, Transformers, Vector DBs |
| **Database** | PostgreSQL 13+, Redis 6+ |
| **DevOps** | Docker, Kubernetes, GitHub Actions, RunPod |
| **Monitoring** | Prometheus, Grafana, Sentry |

---

## 🧩 Platform Components

### Backend Service
**Location**: `v2/backend/`  
**Documentation**: [Backend README](./backend/README.md)

The heart of Nexus Lang V2 - a FastAPI application providing:

- 🔌 **REST APIs** - Comprehensive API endpoints
- 🤖 **AI Agents** - Multi-agent orchestration system
- 🔬 **Grokopedia** - Scientific knowledge engine
- 💬 **NexusLang** - Natural language to code compiler
- 🎤 **Voice AI** - Speech processing services
- 🔐 **Security** - Authentication, authorization, rate limiting
- 📊 **Analytics** - Usage tracking and insights

**Key Files**:
- `main.py` - Full-featured server
- `main_simple.py` - Simplified, reliable server
- `api/` - API endpoint definitions
- `services/` - Business logic and AI agents
- `models/` - Database models
- `core/` - Core utilities

**Quick Start**:
```bash
cd v2/backend
pip install -r requirements.txt
python main.py
```

---

### Frontend Application
**Location**: `v2/frontend/`  
**Documentation**: [Frontend README](./frontend/README.md)

Modern web interface built with Next.js:

- 🎨 **Beautiful UI** - Modern, responsive design
- 🖥️ **IDE Integration** - Monaco editor for NexusLang
- 💬 **Chat Interface** - Conversational AI interaction
- 📊 **Dashboards** - Analytics and research tools
- 👥 **Collaboration** - Team features
- 📱 **Responsive** - Works on all devices

**Key Directories**:
- `app/` - Next.js 13 App Router pages
- `components/` - Reusable React components
- `lib/` - Utilities, hooks, API clients
- `public/` - Static assets
- `styles/` - Global styles

**Quick Start**:
```bash
cd v2/frontend
npm install
npm run dev
```

---

### Shared Libraries
**Location**: `v2/shared/`

Common utilities and libraries used across the platform:

- 📚 **Utilities** - Shared helper functions
- 🔧 **Types** - Common TypeScript/Python types
- 🎨 **UI Components** - Shared components
- 🔌 **API Contracts** - Shared API definitions

---

## 📚 Documentation Index

### Core Documentation

| Document | Description | Location |
|----------|-------------|----------|
| **Main README** | Platform overview | [../README.md](../README.md) |
| **This Document** | V2 master guide | You are here |
| **Backend Guide** | Backend development | [backend/README.md](./backend/README.md) |
| **Frontend Guide** | Frontend development | [frontend/README.md](./frontend/README.md) |

### Deployment Documentation

| Document | Description | Location |
|----------|-------------|----------|
| **RunPod Deployment** | Complete RunPod guide | [../RUNPOD_DEPLOYMENT_README.md](../RUNPOD_DEPLOYMENT_README.md) |
| **RunPod SSH Guide** | SSH deployment steps | [../RUNPOD_SSH_INSTRUCTIONS.md](../RUNPOD_SSH_INSTRUCTIONS.md) |
| **Quick Reference** | Command quick reference | [../RUNPOD_QUICK_REFERENCE.md](../RUNPOD_QUICK_REFERENCE.md) |
| **Troubleshooting** | Fix common issues | [../RUNPOD_WEB_SERVER_FIX.md](../RUNPOD_WEB_SERVER_FIX.md) |
| **Copy-Paste Deploy** | One-command deployment | [../RUNPOD_COPY_PASTE_DEPLOY.txt](../RUNPOD_COPY_PASTE_DEPLOY.txt) |
| **RunPod README** | RunPod-specific docs | [../runpod/README.md](../runpod/README.md) |

### Scientific & AI Documentation

| Document | Description | Location |
|----------|-------------|----------|
| **Scientific Knowledge** | Grokopedia guide | [SCIENTIFIC_KNOWLEDGE_README.md](./SCIENTIFIC_KNOWLEDGE_README.md) |
| **Scientific API Ref** | API reference | [SCIENTIFIC_API_REFERENCE.md](./SCIENTIFIC_API_REFERENCE.md) |
| **Integration Guide** | Integration docs | [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md) |
| **Enhancement Summary** | Feature overview | [SCIENTIFIC_ENHANCEMENT_FINAL_SUMMARY.md](./SCIENTIFIC_ENHANCEMENT_FINAL_SUMMARY.md) |

### Additional Resources

| Document | Description | Location |
|----------|-------------|----------|
| **Scripts Guide** | Utility scripts | [../scripts/README.md](../scripts/README.md) |
| **API Reference** | API documentation | [../API_REFERENCE.md](../API_REFERENCE.md) |

---

## 🚀 Quick Start Guides

### For Users

#### Using the Web Application

1. **Access the platform**:
   - Development: http://localhost:3000
   - Production: https://galion.studio

2. **Create an account**:
   - Register with email
   - Verify your account
   - Complete profile

3. **Start researching**:
   - Navigate to Research Dashboard
   - Submit scientific queries
   - Explore results
   - Save and share findings

#### Using the API

```python
import requests

# Submit a scientific query
response = requests.post(
    "https://galion.studio/api/v1/grokopedia/scientific-query",
    json={
        "query": "Explain quantum entanglement",
        "domain": "physics",
        "depth": "extremely_deep"
    },
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)

result = response.json()
print(result["analysis"])
```

---

### For Developers

#### Setting Up Local Environment

**Step 1: Clone Repository**
```bash
git clone https://github.com/galion-studio/nexuslang-v2.git
cd nexuslang-v2/v2
```

**Step 2: Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your configuration
python main.py
```
📖 **Detailed guide**: [Backend README](./backend/README.md)

**Step 3: Frontend Setup**
```bash
cd frontend
npm install
cp .env.local.example .env.local
# Edit .env.local with your configuration
npm run dev
```
📖 **Detailed guide**: [Frontend README](./frontend/README.md)

**Step 4: Verify Installation**
```bash
# Backend health check
curl http://localhost:8000/health

# Frontend
# Open http://localhost:3000 in browser
```

---

### For DevOps

#### Quick Deploy to RunPod

```bash
# One command deployment
cd /workspace && \
git clone https://github.com/galion-studio/nexuslang-v2.git project-nexus && \
cd project-nexus && \
git checkout clean-nexuslang && \
chmod +x runpod-diagnose-and-fix.sh && \
./runpod-diagnose-and-fix.sh
```

📖 **Detailed guide**: [RunPod SSH Instructions](../RUNPOD_SSH_INSTRUCTIONS.md)

---

## ✨ Core Features

### 1. Grokopedia - Scientific Knowledge Engine

**What it does**:
- Deep scientific analysis across multiple domains
- First principles breakdown of complex topics
- Multi-agent collaboration for comprehensive understanding
- Citation management and source tracking

**Key APIs**:
- `POST /api/v1/grokopedia/scientific-query` - Submit queries
- `POST /api/v1/grokopedia/first-principles-analysis` - Analyze with first principles
- `POST /api/v1/grokopedia/scientific-validation` - Validate claims

**Documentation**: [Scientific Knowledge README](./SCIENTIFIC_KNOWLEDGE_README.md)

**Example**:
```python
# Submit scientific query
response = api.grokopedia.scientific_query(
    query="How does CRISPR work?",
    domain="biology",
    depth="extremely_deep"
)
```

---

### 2. NexusLang - Natural Language Programming

**What it does**:
- Convert English descriptions to code
- Support multiple target languages (Python, JavaScript, etc.)
- AI-assisted code generation
- Real-time compilation and execution

**Key APIs**:
- `POST /api/v1/nexuslang/compile` - Compile natural language to code
- `POST /api/v1/nexuslang/execute` - Execute NexusLang code
- `GET /api/v1/nexuslang/examples` - Get example code

**Example**:
```python
# Compile NexusLang to Python
response = api.nexuslang.compile(
    source="Create a function that sorts a list of numbers",
    target_language="python"
)
print(response.code)
```

---

### 3. Voice AI - Speech Processing

**What it does**:
- Speech-to-text (STT) conversion
- Text-to-speech (TTS) synthesis
- Voice training and customization
- Real-time processing

**Key APIs**:
- `POST /api/v1/voice/speech-to-text` - Convert speech to text
- `POST /api/v1/voice/text-to-speech` - Convert text to speech
- `POST /api/v1/voice/train` - Train voice model

**Example**:
```python
# Convert speech to text
with open("audio.wav", "rb") as f:
    response = api.voice.speech_to_text(audio=f)
    print(response.text)
```

---

### 4. Multi-Agent System

**What it does**:
- Coordinated AI specialists for different domains
- Parallel processing of complex queries
- Agent collaboration and consensus
- Transparent reasoning chains

**Agents**:
- 🔬 **Physics Agent** - Physics and cosmology
- ⚗️ **Chemistry Agent** - Chemical processes
- 🧮 **Mathematics Agent** - Mathematical analysis
- 🧬 **Biology Agent** - Life sciences
- ⚖️ **Law Agent** - Legal analysis
- 📜 **History Agent** - Historical context
- 💻 **Computer Science Agent** - Technical analysis

**Architecture**: [Agent System Docs](./backend/services/agents/)

---

### 5. Research Tools

**Features**:
- 📝 **Research Templates** - Pre-built research workflows
- 📚 **Research History** - Track your research journey
- 👥 **Collaboration** - Team research features
- 📊 **Analytics** - Insights and trends
- 📤 **Export** - Multiple export formats

**APIs**:
- `GET /api/v1/research/templates` - List templates
- `POST /api/v1/research/execute` - Execute research workflow
- `GET /api/v1/research/history` - Get research history

---

## 📖 API Reference

### Complete API Documentation

When running locally:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### API Categories

| Category | Endpoints | Documentation |
|----------|-----------|---------------|
| **Core** | Health, system info | [Backend README](./backend/README.md#api-documentation) |
| **Grokopedia** | Scientific queries | [Scientific API Reference](./SCIENTIFIC_API_REFERENCE.md) |
| **NexusLang** | Code compilation | [Backend README](./backend/README.md#nexuslang-programming) |
| **Voice** | Speech processing | [Backend README](./backend/README.md#voice-ai) |
| **Auth** | Authentication | [Backend README](./backend/README.md#authentication) |
| **Research** | Research tools | [Backend README](./backend/README.md#research-tools) |

### Authentication

All API requests require authentication:

```python
headers = {
    "Authorization": "Bearer YOUR_JWT_TOKEN",
    "Content-Type": "application/json"
}
```

Get token:
```python
response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    json={"email": "user@example.com", "password": "password"}
)
token = response.json()["access_token"]
```

---

## 🌐 Deployment Options

### 1. Local Development

**Best for**: Development, testing  
**Requirements**: Python 3.8+, Node.js 16+, PostgreSQL, Redis

```bash
# Backend
cd v2/backend && python main.py

# Frontend
cd v2/frontend && npm run dev
```

📖 **Guide**: [Backend README](./backend/README.md#quick-start) | [Frontend README](./frontend/README.md#quick-start)

---

### 2. Docker

**Best for**: Containerized deployment, consistency

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

📖 **Guide**: [Docker Compose Configuration](../docker-compose.yml)

---

### 3. RunPod (Recommended for AI)

**Best for**: GPU-accelerated AI workloads, production

```bash
# One-command deployment
cd /workspace && \
git clone https://github.com/galion-studio/nexuslang-v2.git project-nexus && \
cd project-nexus && \
chmod +x runpod-diagnose-and-fix.sh && \
./runpod-diagnose-and-fix.sh
```

📖 **Guides**:
- [RunPod Deployment README](../RUNPOD_DEPLOYMENT_README.md)
- [RunPod SSH Instructions](../RUNPOD_SSH_INSTRUCTIONS.md)
- [RunPod Quick Reference](../RUNPOD_QUICK_REFERENCE.md)
- [RunPod Troubleshooting](../RUNPOD_WEB_SERVER_FIX.md)

---

### 4. Kubernetes

**Best for**: Large-scale production, high availability

```bash
# Apply configurations
kubectl apply -f k8s/

# Check status
kubectl get pods -n nexus

# View logs
kubectl logs -f deployment/nexus-backend -n nexus
```

📖 **Guide**: [Kubernetes Configurations](../k8s/)

---

### 5. Cloud Providers

**AWS, GCP, Azure**

Use our Terraform configurations for automated setup:

```bash
cd terraform/aws  # or gcp, azure
terraform init
terraform plan
terraform apply
```

📖 **Guide**: [Terraform Configurations](../terraform/)

---

## 💻 Development Workflow

### Setting Up Development Environment

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/nexuslang-v2.git
   cd nexuslang-v2
   ```

2. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Set Up Backend**
   ```bash
   cd v2/backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Dev dependencies
   ```

4. **Set Up Frontend**
   ```bash
   cd v2/frontend
   npm install
   ```

5. **Make Changes**
   - Write code
   - Add tests
   - Update documentation

6. **Test Changes**
   ```bash
   # Backend tests
   cd v2/backend && pytest

   # Frontend tests
   cd v2/frontend && npm test

   # Linting
   cd v2/backend && flake8
   cd v2/frontend && npm run lint
   ```

7. **Commit and Push**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   git push origin feature/your-feature-name
   ```

8. **Create Pull Request**
   - Go to GitHub
   - Create PR from your branch
   - Fill in description
   - Request review

### Code Standards

- **Python**: PEP 8, type hints, docstrings
- **TypeScript**: ESLint rules, proper types
- **Git**: Conventional commits
- **Tests**: Write tests for new features
- **Documentation**: Update relevant docs

---

## 🔌 Integration Guide

### Using the Platform in Your Application

#### JavaScript/TypeScript

```typescript
import { NexusClient } from '@nexuslang/sdk';

const client = new NexusClient({
  apiUrl: 'https://galion.studio',
  apiKey: 'YOUR_API_KEY'
});

// Submit scientific query
const result = await client.grokopedia.query({
  query: 'Explain quantum computing',
  domain: 'computer_science'
});

console.log(result.analysis);
```

#### Python

```python
from nexuslang import NexusClient

client = NexusClient(
    api_url='https://galion.studio',
    api_key='YOUR_API_KEY'
)

# Submit scientific query
result = client.grokopedia.query(
    query='Explain quantum computing',
    domain='computer_science'
)

print(result.analysis)
```

#### REST API

```bash
curl -X POST https://galion.studio/api/v1/grokopedia/scientific-query \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Explain quantum computing",
    "domain": "computer_science"
  }'
```

📖 **Full guide**: [Integration Guide](./INTEGRATION_GUIDE.md)

---

## 🔧 Troubleshooting

### Common Issues

#### Backend Won't Start

```bash
# Check Python version
python --version  # Should be 3.8+

# Check dependencies
pip install -r requirements.txt

# Check database connection
psql -U postgres -c "SELECT 1;"

# Check environment variables
cat .env | grep DATABASE_URL

# Try simplified server
python main_simple.py
```

📖 **Guide**: [Backend README - Troubleshooting](./backend/README.md#troubleshooting)

---

#### Frontend Won't Start

```bash
# Check Node version
node --version  # Should be 16+

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Check environment
cat .env.local | grep NEXT_PUBLIC_API_URL

# Rebuild
npm run build
npm start
```

📖 **Guide**: [Frontend README - Troubleshooting](./frontend/README.md#troubleshooting)

---

#### API Connection Issues

```bash
# Test backend
curl http://localhost:8000/health

# Check CORS settings
# In backend/main.py, check allowed_origins

# Check API URL in frontend
# In frontend/.env.local, check NEXT_PUBLIC_API_URL
```

---

#### RunPod Deployment Issues

```bash
# Run diagnostic
cd /workspace/project-nexus
./runpod-diagnose-and-fix.sh

# Check logs
tail -50 /workspace/logs/galion-backend.log

# Try simplified server
./runpod-start-simple.sh
```

📖 **Guides**:
- [RunPod Troubleshooting](../RUNPOD_WEB_SERVER_FIX.md)
- [Quick Reference](../RUNPOD_QUICK_REFERENCE.md)

---

## 📚 Resources

### Documentation

- **Main README**: [../README.md](../README.md)
- **Backend Guide**: [backend/README.md](./backend/README.md)
- **Frontend Guide**: [frontend/README.md](./frontend/README.md)
- **RunPod Guide**: [../RUNPOD_DEPLOYMENT_README.md](../RUNPOD_DEPLOYMENT_README.md)
- **Scripts Guide**: [../scripts/README.md](../scripts/README.md)

### API Documentation

- **API Reference**: [../API_REFERENCE.md](../API_REFERENCE.md)
- **Scientific APIs**: [SCIENTIFIC_API_REFERENCE.md](./SCIENTIFIC_API_REFERENCE.md)
- **Integration Guide**: [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md)

### External Links

- **GitHub**: [galion-studio/nexuslang-v2](https://github.com/galion-studio/nexuslang-v2)
- **Website**: [galion.studio](https://galion.studio)
- **API Docs**: [docs.galion.studio](https://docs.galion.studio)

### Community

- **Issues**: [GitHub Issues](https://github.com/galion-studio/nexuslang-v2/issues)
- **Discussions**: [GitHub Discussions](https://github.com/galion-studio/nexuslang-v2/discussions)
- **Email**: support@galion.studio

---

## 🗺️ Next Steps

### For New Users

1. ✅ Read this document
2. ✅ Try the [Quick Start](#quick-start-guides)
3. ✅ Explore the [Web Interface](https://galion.studio)
4. ✅ Read [API Documentation](../API_REFERENCE.md)
5. ✅ Join our community

### For Developers

1. ✅ Set up [local environment](#for-developers)
2. ✅ Read [Backend README](./backend/README.md)
3. ✅ Read [Frontend README](./frontend/README.md)
4. ✅ Explore the codebase
5. ✅ Make your first contribution

### For DevOps

1. ✅ Review [deployment options](#deployment-options)
2. ✅ Choose deployment platform
3. ✅ Follow deployment guide
4. ✅ Set up monitoring
5. ✅ Configure backups

---

## 📄 License

MIT License - see [LICENSE](../LICENSE) file for details.

---

## 🙏 Acknowledgments

- OpenAI for GPT-4 API
- FastAPI team
- Next.js team
- RunPod for GPU hosting
- All our contributors

---

## 📞 Support

### Get Help

- 📖 **Documentation**: Start with relevant README
- 🐛 **Issues**: [GitHub Issues](https://github.com/galion-studio/nexuslang-v2/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/galion-studio/nexuslang-v2/discussions)
- 📧 **Email**: support@galion.studio

### Report Security Issues

**Email**: security@galion.studio  
**Do not** create public issues for security vulnerabilities.

---

## ✅ Documentation Checklist

When adding new features, update:

- [ ] This master README (if needed)
- [ ] Component-specific README
- [ ] API documentation
- [ ] Integration guide
- [ ] Deployment guides (if needed)
- [ ] Troubleshooting sections
- [ ] Code comments
- [ ] Tests

---

**Built with ❤️ by the Galion Studio team**

**Version**: 2.0.0  
**Last Updated**: November 14, 2025  

---

## 🔗 Quick Links

| What You Need | Where to Go |
|---------------|-------------|
| **Start developing** | [Backend README](./backend/README.md) \| [Frontend README](./frontend/README.md) |
| **Deploy to RunPod** | [RunPod SSH Instructions](../RUNPOD_SSH_INSTRUCTIONS.md) |
| **Use the API** | [API Reference](../API_REFERENCE.md) |
| **Scientific features** | [Scientific Knowledge README](./SCIENTIFIC_KNOWLEDGE_README.md) |
| **Troubleshooting** | [RunPod Troubleshooting](../RUNPOD_WEB_SERVER_FIX.md) |
| **Quick commands** | [Quick Reference](../RUNPOD_QUICK_REFERENCE.md) |
| **Integration** | [Integration Guide](./INTEGRATION_GUIDE.md) |
| **Scripts** | [Scripts README](../scripts/README.md) |

---

🎉 **Everything you need is documented. Choose your path and start building!**
