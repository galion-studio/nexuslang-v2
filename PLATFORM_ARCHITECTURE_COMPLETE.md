# 🏗️ Complete Platform Architecture - Galion Ecosystem

**Date**: November 12, 2025  
**Status**: Complete Multi-Platform System  
**Deployment**: RunPod + Cloudflare

---

## 🎯 Platform Overview

### Two Frontend Platforms:

**1. developer.galion.app** (NexusLang IDE)
- Target: Developers, coders, technical users
- Focus: Programming, code execution, API access
- Features: IDE, NexusLang, AI chat, Grokopedia

**2. galion.studio** (Content Creation)
- Target: Creators, marketers, businesses
- Focus: AI content generation (images, videos, text, voice)
- Features: Generation tools, project library, collaboration

### One Shared Backend:

**api.developer.galion.app**
- Serves both platforms
- Unified authentication
- Shared credit system
- 54 API endpoints

---

## 🔗 Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                     User Layer                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  developer.galion.app          galion.studio           │
│  (Port 3000)                   (Port 3001)              │
│  - IDE                         - Image Gen              │
│  - Code Execution              - Video Gen              │
│  - AI Chat                     - Text Gen               │
│  - Grokopedia                  - Voice Gen              │
│  - API Docs                    - Project Library        │
│                                                         │
└──────────────┬──────────────────────────┬───────────────┘
               │                          │
               └──────────┬───────────────┘
                          │
                          ▼
          ┌───────────────────────────────────┐
          │   API Gateway (Cloudflare)        │
          │   api.developer.galion.app        │
          └───────────────┬───────────────────┘
                          │
                          ▼
          ┌───────────────────────────────────┐
          │   Shared Backend (FastAPI)        │
          │   Port 8000                       │
          ├───────────────────────────────────┤
          │  54 API Endpoints:                │
          │  - /api/v2/auth                   │
          │  - /api/v2/ai                     │
          │  - /api/v2/nexuslang              │
          │  - /api/v2/voice                  │
          │  - /api/v2/grokopedia             │
          │  - /api/v2/billing                │
          │  - /api/v2/content-manager        │
          └───────────────┬───────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
    ┌──────┐        ┌──────┐         ┌─────────┐
    │PostDB│        │Redis │         │OpenRouter│
    │5432  │        │6379  │         │30+ Models│
    └──────┘        └──────┘         └─────────┘
```

---

## 🔐 Admin Configuration

### Primary Admin: Maciej Grajczyk

**Email Accounts**:
- Primary: maci.grajczyk@gmail.com
- Secondary: polskitygrys111@gmail.com
- Secondary: frxdel@gmail.com  
- Secondary: legalizacija420@gmail.com
- Business: info@galion.studio

**Permissions**: Full access (owner role)

### Business Email Setup (Zoho Mail):

**Configured**:
- info@galion.studio (active)

**Future**:
- marketing@galion.studio
- developer@galion.studio
- shop@galion.studio
- support@galion.studio

**Email Forwarding**: All forward to maci.grajczyk@gmail.com

---

## 💰 Pricing Structure

### Galion Studio (Content Creation):

| Tier | Price | Features |
|------|-------|----------|
| Free Trial | $0 | 14 days, 20 images, watermarked |
| Creator | $20/mo | 200 images, commercial license |
| Professional | $50/mo | 1,000 images, team features |
| Business | $200/mo | 10,000 images, white-label |
| Enterprise | $2,500+/mo | Unlimited, custom |

### Developer Platform (API Access):

| Tier | Price | Features |
|------|-------|----------|
| Free | $0 | Pay-per-use, 100 free credits |
| Pro Dev | $49/mo | $50 credits included |
| Business API | $199/mo | $250 credits included |
| Enterprise | Custom | Unlimited, SLA |

---

## 🔧 Technical Stack

### Frontend Technologies:
- **Framework**: Next.js 14
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State**: React hooks
- **Auth**: JWT tokens (shared)

### Backend Technologies:
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15 with pgvector
- **Cache**: Redis 7
- **Search**: Elasticsearch (optional)
- **AI**: OpenRouter (primary, 99%) + OpenAI (fallback, 1%)

### Infrastructure:
- **Hosting**: RunPod GPU pod
- **DNS/CDN**: Cloudflare
- **SSL**: Cloudflare Full (strict)
- **Containers**: Docker + Docker Compose

---

## 🔗 API Integration

### Both Platforms Use Same APIs:

**Authentication**: `/api/v2/auth`
- Register, login, logout
- Same account works on both platforms

**AI Generation**: `/api/v2/ai`
- Text (Claude, GPT-4, etc.)
- Images (Stable Diffusion, DALL-E)
- Videos (Runway, Pika)
- All via OpenRouter

**Voice**: `/api/v2/voice`
- TTS (text-to-speech)
- STT (speech-to-text)
- Voice calls (WebSocket)

**Credits**: `/api/v2/billing`
- Shared credit pool
- Usage tracking
- Subscription management

---

## 🚀 Deployment Configuration

### Current RunPod Setup:

**IP**: 213.173.105.83  
**Services Running**:
- Backend: Port 8000
- Developer Frontend: Port 3000
- Studio Frontend: Port 3001 (when deployed)

### DNS Configuration (Cloudflare):

```
developer.galion.app → 213.173.105.83 (Proxied)
api.developer.galion.app → 213.173.105.83 (Proxied)
galion.studio → 213.173.105.83 (Proxied) [FUTURE]
```

### SSL: Full (strict) mode

---

## 📊 Feature Matrix

| Feature | Developer Platform | Galion Studio |
|---------|-------------------|---------------|
| Code Execution | ✅ | ❌ |
| AI Chat | ✅ | ✅ |
| Image Generation | Via API | ✅ Dashboard |
| Video Generation | Via API | ✅ Dashboard |
| Text Generation | Via API | ✅ Dashboard |
| Voice Synthesis | ✅ | ✅ |
| Voice Calls | ✅ | ✅ |
| Grokopedia | ✅ | ❌ |
| Content Manager | ✅ | ❌ |
| API Documentation | ✅ | ❌ |
| Project Library | ✅ IDE Projects | ✅ Content Projects |

---

## 🎯 User Flows

### Flow 1: Developer Using Both Platforms

1. Register at developer.galion.app
2. Get API key
3. Use IDE for coding
4. Switch to galion.studio for content
5. Same login, shared credits

### Flow 2: Creator Using Studio

1. Register at galion.studio  
2. Start with free tier (100 credits)
3. Generate images/videos
4. Upgrade when needed
5. Optional: Use API later

---

## 🔄 Credit System (Unified)

**Shared Credits**: Work on both platforms

**Costs**:
- NexusLang execution: 1 credit
- Image generation: 5 credits
- Video generation: 20 credits
- Text generation: 2 credits/1K tokens
- Voice synthesis: 3 credits

**User has ONE credit balance** used across all platforms

---

## 📁 Project Structure

```
project-nexus/
├── v2/                          # Developer Platform
│   ├── backend/                 # Shared backend (serves both)
│   │   ├── api/                 # 54 endpoints
│   │   ├── services/            # AI, voice, etc.
│   │   └── core/                # Auth, admin, email
│   └── frontend/                # developer.galion.app
│       └── app/                 # IDE, docs, etc.
│
├── galion-studio/               # Studio Platform (NEW)
│   ├── app/                     # Landing, dashboards
│   ├── components/              # UI components
│   └── lib/                     # API client
│
└── docker-compose.prod.yml      # Deploys everything
```

---

## 🚀 Deployment Status

**Ready**:
- ✅ developer.galion.app (code complete)
- ✅ Shared backend (running on RunPod)
- ✅ galion.studio (code complete, needs deployment)

**Next Steps**:
1. Deploy developer.galion.app (IN PROGRESS on RunPod)
2. Add galion.studio to docker-compose
3. Configure DNS for galion.studio
4. Both platforms live!

---

**Architecture**: Complete  
**Code**: Ready  
**Deployment**: In progress

🚀 **Unified ecosystem ready to launch!**

