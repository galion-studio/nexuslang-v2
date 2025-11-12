# 📚 Nexus API Documentation

Welcome to the Nexus Core API Documentation! This directory contains comprehensive API references for all Nexus services.

## 📖 Quick Start

**View Documentation:**
- **Start Here:** [index.html](index.html) - Complete documentation hub
- **Status Page:** [../nexus-status.html](../nexus-status.html) - Real-time system status

## 📑 Available Services

### Core Services

#### [🌐 API Gateway](api-gateway.html)
Single entry point with authentication, rate limiting, and request routing.
- Port: 8080
- Tech: Go 1.21, Gorilla Mux
- Features: JWT validation, rate limiting, CORS, security headers

#### [🔐 Authentication Service](auth-service.html)
User registration, login, and JWT token management.
- Port: 8000
- Tech: FastAPI, Python 3.11
- Features: Registration, login, 2FA (TOTP), JWT tokens
- [Swagger UI](http://localhost:8000/docs)

#### [👤 User Service](user-service.html)
User profile management, search, and admin operations.
- Port: 8001
- Tech: FastAPI, Python 3.11
- Features: Profiles, search, pagination, admin controls
- [Swagger UI](http://localhost:8001/docs)

### Feature Services

#### [🎤 Voice Service](voice-service.html)
Speech-to-Text, Text-to-Speech, and AI-powered voice interactions.
- Port: 8003
- Tech: FastAPI, OpenAI Whisper, ElevenLabs
- Features: STT, TTS, WebSocket streaming, voice commands
- [Swagger UI](http://localhost:8003/docs)

#### [📊 Analytics Service](analytics-service.html)
Real-time event processing and metrics.
- Port: 9090
- Tech: Go 1.21, Kafka, PostgreSQL
- Features: Event processing, Prometheus metrics, Grafana dashboards
- [Metrics](http://localhost:9090/metrics)

## 🚀 How to Use This Documentation

### 1. Local Development
```bash
# Simply open the HTML files in your browser
open index.html
open auth-service.html
# etc.
```

### 2. Start Web Server
```bash
# From project root
python -m http.server 8888

# Then visit:
# http://localhost:8888/api-docs/index.html
```

### 3. Use Quick Start Script
```powershell
# Windows
..\start-docs-server.ps1

# macOS/Linux
../start-docs-server.sh
```

## 📂 Documentation Structure

```
api-docs/
├── index.html              # Main documentation hub ⭐ START HERE
├── auth-service.html       # Authentication API reference
├── user-service.html       # User management API reference
├── voice-service.html      # Voice service API reference
├── api-gateway.html        # Gateway documentation
├── analytics-service.html  # Analytics documentation
└── README.md              # This file
```

## 🔗 Related Documentation

- **Service Details:** [../docs/](../docs/) - Deep technical guides for each service
- **Status Page:** [../nexus-status.html](../nexus-status.html) - Real-time monitoring
- **Public Access:** [../PUBLIC_ACCESS_GUIDE.md](../PUBLIC_ACCESS_GUIDE.md) - Deployment options
- **Main README:** [../README.md](../README.md) - Project overview

## 🎯 What Each Page Contains

Every API documentation page includes:

✅ **Overview** - Service purpose and key features  
✅ **API Endpoints** - Complete endpoint reference  
✅ **Request/Response Examples** - Real code samples  
✅ **Authentication** - How to authenticate requests  
✅ **Configuration** - Environment variables and settings  
✅ **Error Handling** - Status codes and error responses  
✅ **Monitoring** - Health checks and metrics  

## 🔐 Authentication

Most endpoints require JWT tokens. Here's how to get started:

### 1. Register a User
```bash
POST http://localhost:8080/api/v1/auth/register
{
  "email": "user@example.com",
  "password": "SecurePassword123",
  "name": "John Doe"
}
```

### 2. Login
```bash
POST http://localhost:8080/api/v1/auth/login
{
  "email": "user@example.com",
  "password": "SecurePassword123"
}
```

Response includes JWT token:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "expires_in": 3600
}
```

### 3. Use Token
Include in Authorization header for authenticated requests:
```bash
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

## 📊 Interactive Documentation

All FastAPI services provide interactive Swagger UI:

- **Auth Service:** http://localhost:8000/docs
- **User Service:** http://localhost:8001/docs
- **Voice Service:** http://localhost:8003/docs

Features:
- Try endpoints directly
- Auto-generated from code
- Request/response schemas
- Authentication testing

## 🌍 Making Documentation Public

See [PUBLIC_ACCESS_GUIDE.md](../PUBLIC_ACCESS_GUIDE.md) for multiple deployment options:

**Quick Options:**
1. **Python Server** (1 min) - Local network access
2. **Cloudflare Tunnel** (15 min) - Internet access, free
3. **GitHub Pages** (10 min) - Permanent hosting, free
4. **Netlify** (5 min) - Drag & drop, free
5. **Ngrok** (5 min) - Quick demos

## 🛠️ For Developers

### Using the APIs

Each service documentation includes:
- cURL examples
- Python examples
- JavaScript examples
- Request/response formats

### Testing Endpoints

Use the Swagger UI for quick testing:
```bash
# Start services
docker-compose up -d

# Visit
http://localhost:8000/docs  # Auth Service
http://localhost:8001/docs  # User Service
http://localhost:8003/docs  # Voice Service
```

### Code Examples

Every endpoint includes copy-paste ready examples:
- cURL commands
- Python requests
- JavaScript fetch
- Full request/response bodies

## 🔍 Quick Reference

### Base URLs
```
API Gateway:   http://localhost:8080
Auth Service:  http://localhost:8000
User Service:  http://localhost:8001
Voice Service: http://localhost:8003
Analytics:     http://localhost:9090
```

### Common Headers
```
Content-Type: application/json
Authorization: Bearer {jwt_token}
```

### Response Format
```json
{
  "success": true,
  "data": { ... }
}
```

### Error Format
```json
{
  "detail": "Error message",
  "status_code": 400
}
```

## 🎉 Getting Started

1. **Start Here:** Open [index.html](index.html)
2. **Choose Service:** Select the service you need
3. **Read Docs:** Review endpoints and examples
4. **Test API:** Use Swagger UI or cURL
5. **Integrate:** Copy examples into your code

## 📞 Support

- **Status Dashboard:** [nexus-status.html](../nexus-status.html)
- **Service Guides:** [../docs/](../docs/)
- **Architecture:** [../ARCHITECTURE.md](../ARCHITECTURE.md)
- **Main README:** [../README.md](../README.md)

---

**Last Updated:** November 9, 2024  
**Version:** 1.0.0  
**Status:** ✅ Complete

**Next Step:** Open [index.html](index.html) to get started! 🚀

