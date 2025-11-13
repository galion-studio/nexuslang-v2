# 🎯 Launch ALL THREE Galion Apps - Complete Guide

**Three Complete Platforms - One Command!**

---

## 🚀 Your Three Apps

### 1. **developer.galion.app** (Developer Platform)
- **Backend**: Port 8000
- **Frontend**: Port 3000
- **Features**: IDE, AI Chat, Code Execution, NexusLang, Grokopedia
- **Target**: Developers & programmers

### 2. **galion.studio** (Content Creation)
- **App**: Port 3001
- **Features**: Image, Video, Text, Voice generation, Project library
- **Target**: Creators & businesses

### 3. **galion.app** (Voice AI Assistant)
- **Backend**: Port 8100
- **Frontend**: Port 3100
- **Features**: Voice-first AI for science
- **Target**: Researchers & scientists

---

## ⚡ ONE-COMMAND LAUNCH

Run this on your RunPod terminal:

```bash
cd /workspace/project-nexus
bash LAUNCH_ALL_THREE_APPS.sh
```

This will:
- ✅ Start all backends
- ✅ Start all frontends
- ✅ Setup LocalTunnel for public URLs
- ✅ Run health checks
- ✅ Display all access URLs

**Time**: ~2 minutes (services already configured)

---

## 🌐 Access URLs

After running the launch script, you'll get:

### developer.galion.app:
- Backend API: `https://galion-developer-api-TIMESTAMP.loca.lt/docs`
- Frontend: `https://galion-developer-app-TIMESTAMP.loca.lt`

### galion.studio:
- App: `https://galion-studio-TIMESTAMP.loca.lt`

### galion.app:
- Backend API: `https://galion-voice-api-TIMESTAMP.loca.lt`
- Frontend: `https://galion-voice-app-TIMESTAMP.loca.lt`

**Password for all**: Your public IP (shown after launch)

---

## 📊 Port Assignments

| App | Backend | Frontend | Description |
|-----|---------|----------|-------------|
| developer.galion.app | 8000 | 3000 | Developer IDE |
| galion.studio | - | 3001 | Content Creation |
| galion.app | 8100 | 3100 | Voice AI |
| PostgreSQL | 5432 | - | Database |
| Redis | 6379 | - | Cache |

---

## 🎛️ Quick Management

### View All Services:
```bash
ps aux | grep -E 'uvicorn|next' | grep -v grep
```

### Check Health:
```bash
curl http://localhost:8000/health  # developer.galion.app
curl http://localhost:3001         # galion.studio
curl http://localhost:8100/health  # galion.app
```

### View Logs:
```bash
tail -f /workspace/logs/*.log
```

### Restart All:
```bash
pkill -f "uvicorn"
pkill -f "next dev"
bash LAUNCH_ALL_THREE_APPS.sh
```

---

## 🎨 Features by Platform

### developer.galion.app:
- ✅ Web IDE with code editor
- ✅ NexusLang execution
- ✅ AI chat (30+ models)
- ✅ Code generation
- ✅ Grokopedia search
- ✅ API documentation
- ✅ Project management

### galion.studio:
- ✅ Image generation (DALL-E, Stable Diffusion)
- ✅ Video generation (RunwayML, Stability AI)
- ✅ Text generation (7 templates)
- ✅ Voice synthesis (TTS/STT)
- ✅ Project library
- ✅ Team collaboration
- ✅ Analytics dashboard

### galion.app:
- ✅ Voice-first interface
- ✅ AI assistant for science
- ✅ Knowledge base integration
- ✅ Research tools

---

## 💾 After Launch

The script creates:
- `/workspace/ALL_APPS_DEPLOYED.txt` - All URLs and info
- `/workspace/logs/` - All application logs
- Unique LocalTunnel URLs for each service

---

## 🎉 Success Checklist

After launch, verify:

- [ ] developer.galion.app backend returns `{"status":"healthy"}`
- [ ] developer.galion.app frontend shows landing page
- [ ] galion.studio loads successfully
- [ ] LocalTunnel URLs are displayed
- [ ] Can access all URLs with your IP as password

---

## 🔥 LAUNCH NOW!

```bash
cd /workspace/project-nexus
bash LAUNCH_ALL_THREE_APPS.sh
```

**Your entire ecosystem will be live in 2 minutes!** 🚀

