# 🚀 RunPod Quick Start - NexusLang v2

**Deploy in 5 minutes!**

---

## ⚡ FASTEST WAY (Copy & Paste)

### Step 1: SSH into Your RunPod

```bash
# From RunPod dashboard, click "Connect" → copy SSH command
ssh root@your-pod-id.runpod.net -i ~/.ssh/runpod
```

### Step 2: Run This One Command

```bash
cd /workspace && \
git clone https://github.com/your-org/project-nexus.git && \
cd project-nexus && \
chmod +x v2/deploy-to-runpod.sh && \
./v2/deploy-to-runpod.sh && \
cd v2/backend && \
./start.sh
```

### Step 3: Access Your API

**Local:** http://localhost:8000/docs  
**Public:** https://your-pod-id-8000.proxy.runpod.net/docs

**Done!** 🎉

---

## 🐳 DOCKER METHOD (More Reliable)

```bash
# 1. Clone repo
cd /workspace
git clone https://github.com/your-org/project-nexus.git
cd project-nexus/v2/backend

# 2. Build & run
docker build -f Dockerfile.runpod -t nexuslang:latest .
docker run -d -p 8000:8000 --name nexuslang \
  -e JWT_SECRET_KEY="$(openssl rand -hex 64)" \
  --restart unless-stopped \
  nexuslang:latest

# 3. Check
docker logs -f nexuslang
```

---

## 📍 PORT CONFIGURATION

**In RunPod Dashboard:**
1. Go to your pod
2. Click "Ports"
3. Add: `8000` → `8000` (HTTP)
4. Note your URL: `https://xxx-8000.proxy.runpod.net`

---

## 🔧 ESSENTIAL ENVIRONMENT VARIABLES

Create `/workspace/project-nexus/v2/backend/.env`:

```bash
JWT_SECRET_KEY=your-64-char-secret-here
DATABASE_URL=sqlite+aiosqlite:////workspace/nexuslang.db
REDIS_URL=redis://localhost:6379/1
DEBUG=false
CORS_ORIGINS=https://your-pod-8000.proxy.runpod.net
```

Generate secret:
```bash
openssl rand -hex 64
```

---

## ✅ VERIFY IT'S WORKING

```bash
# Test 1: Health check
curl http://localhost:8000/health

# Expected: {"status":"healthy","service":"nexuslang-v2-api"}

# Test 2: Security headers
curl -I http://localhost:8000/health | grep X-

# Expected: X-RateLimit-*, X-Frame-Options, etc.

# Test 3: Register user
curl -X POST http://localhost:8000/api/v2/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","username":"test","password":"TestPass123!@#"}'

# Expected: JWT token returned
```

---

## 🔄 AUTO-START ON POD RESTART

Create `/workspace/autostart.sh`:

```bash
#!/bin/bash
cd /workspace/project-nexus/v2/backend
export $(cat .env | xargs)
./start.sh &
```

Make executable:
```bash
chmod +x /workspace/autostart.sh
```

**In RunPod → Docker Command:**
```bash
/workspace/autostart.sh && sleep infinity
```

---

## 📊 MONITORING

```bash
# View logs
tail -f /workspace/project-nexus/v2/backend/logs/*.log

# Check status
systemctl status nexuslang

# Resource usage
htop
```

---

## 🆘 COMMON ISSUES

### "Port 8000 already in use"
```bash
pkill -f uvicorn
./start.sh
```

### "Database is locked"
```bash
# Use /workspace for persistence
DATABASE_URL=sqlite+aiosqlite:////workspace/nexuslang.db
```

### "Can't access from outside"
- Check RunPod port forwarding (8000:8000)
- Update CORS_ORIGINS in .env
- Restart service

---

## 🎯 NEXT STEPS

1. ✅ Deploy (you just did!)
2. Test all endpoints at `/docs`
3. Set up monitoring
4. Configure backups
5. Update frontend URL
6. Go live! 🚀

---

**Full Guide:** See `RUNPOD_DEPLOYMENT.md`  
**Security:** See `SECURITY_DEPLOYMENT_CHECKLIST.md`

**🚀 You're live on RunPod!**

