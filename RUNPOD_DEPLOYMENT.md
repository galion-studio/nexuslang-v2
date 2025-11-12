# 🚀 NexusLang v2 - RunPod Deployment Guide

Complete guide for deploying NexusLang v2 to RunPod with full security features.

---

## ⚡ QUICK START (5 Minutes)

### Method 1: Automated Script (Easiest)

```bash
# 1. SSH into your RunPod instance
# 2. Clone your repository to /workspace
cd /workspace
git clone https://github.com/your-org/project-nexus.git
cd project-nexus

# 3. Run deployment script
chmod +x v2/deploy-to-runpod.sh
./v2/deploy-to-runpod.sh

# 4. Start the server
cd v2/backend
./start.sh
```

**Done!** Your API is running on `http://localhost:8000`

---

### Method 2: Docker (Recommended for Production)

```bash
# 1. Clone repository
cd /workspace
git clone https://github.com/your-org/project-nexus.git
cd project-nexus/v2/backend

# 2. Build Docker image
docker build -f Dockerfile.runpod -t nexuslang-v2:latest .

# 3. Run container
docker run -d \
  --name nexuslang-v2 \
  -p 8000:8000 \
  -v /workspace/nexuslang-data:/app/data \
  -e JWT_SECRET_KEY="$(openssl rand -hex 64)" \
  -e DATABASE_URL="sqlite+aiosqlite:///./data/nexuslang.db" \
  --restart unless-stopped \
  nexuslang-v2:latest

# 4. Check logs
docker logs -f nexuslang-v2
```

---

## 📋 RUNPOD-SPECIFIC CONFIGURATION

### 1. Port Mapping

RunPod requires specific port configuration:

**In RunPod Dashboard:**
1. Go to your Pod settings
2. Add TCP port: `8000` → `8000`
3. Enable HTTP service
4. Get your public URL: `https://your-pod-id-8000.proxy.runpod.net`

**Update CORS in `.env`:**
```bash
CORS_ORIGINS=https://your-pod-id-8000.proxy.runpod.net,https://your-frontend.com
```

### 2. Persistent Storage

Use RunPod's `/workspace` for persistence:

```bash
# Store database in /workspace (persists across pod restarts)
DATABASE_URL=sqlite+aiosqlite:////workspace/nexuslang/nexuslang.db

# Or use PostgreSQL (recommended for production)
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/nexuslang
```

### 3. Redis Configuration

**Option A: Use RunPod's Redis Template**
1. Deploy Redis from RunPod templates
2. Get Redis connection URL
3. Update `.env`:
```bash
REDIS_URL=redis://your-redis-pod:6379/1
REDIS_PASSWORD=your-redis-password
```

**Option B: Install Redis Locally**
```bash
# Install Redis on your pod
apt-get update && apt-get install -y redis-server
redis-server --daemonize yes
```

---

## 🐳 DOCKER COMPOSE FOR RUNPOD

Create `docker-compose.runpod.yml`:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.runpod
    ports:
      - "8000:8000"
    environment:
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - DATABASE_URL=postgresql://nexus:${DB_PASSWORD}@postgres:5432/nexuslang_v2
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/1
    volumes:
      - /workspace/nexuslang/logs:/app/logs
      - /workspace/nexuslang/data:/app/data
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=nexus
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=nexuslang_v2
    volumes:
      - /workspace/nexuslang/postgres:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - /workspace/nexuslang/redis:/data
    restart: unless-stopped
```

**Deploy:**
```bash
# Set passwords
export JWT_SECRET_KEY=$(openssl rand -hex 64)
export DB_PASSWORD=$(openssl rand -base64 32)
export REDIS_PASSWORD=$(openssl rand -base64 32)

# Save to .env
echo "JWT_SECRET_KEY=$JWT_SECRET_KEY" > .env
echo "DB_PASSWORD=$DB_PASSWORD" >> .env
echo "REDIS_PASSWORD=$REDIS_PASSWORD" >> .env

# Start services
docker-compose -f docker-compose.runpod.yml up -d
```

---

## 🔧 RUNPOD STARTUP SCRIPT

Create `/workspace/start-nexuslang.sh` (runs on pod start):

```bash
#!/bin/bash
# Auto-start script for RunPod

cd /workspace/project-nexus/v2/backend

# Load environment
export $(cat .env | grep -v '^#' | xargs)

# Start Redis if needed
if ! pgrep redis-server > /dev/null; then
    redis-server --daemonize yes
fi

# Start NexusLang
./start.sh &

# Keep container running
tail -f logs/nexuslang.log
```

**Set as startup command in RunPod:**
```bash
/workspace/start-nexuslang.sh
```

---

## 🔒 SECURITY ON RUNPOD

### 1. Environment Variables

**In RunPod Dashboard → Environment Variables:**
```
JWT_SECRET_KEY=your-64-char-secret
DATABASE_URL=your-database-url
REDIS_URL=your-redis-url
OPENAI_API_KEY=your-openai-key (if using)
```

### 2. Network Security

```bash
# Allow only necessary ports
# In RunPod: Expose only 8000 for API

# Use RunPod's built-in firewall
# Block all except:
# - 8000 (API)
# - 22 (SSH)
```

### 3. SSL/TLS

RunPod provides automatic HTTPS via proxy:
```
http://localhost:8000 → https://your-pod-id-8000.proxy.runpod.net
```

**Update your CORS origins:**
```bash
CORS_ORIGINS=https://your-pod-id-8000.proxy.runpod.net
```

---

## 📊 MONITORING ON RUNPOD

### 1. Check Service Status

```bash
# Check if running
curl http://localhost:8000/health

# View logs
tail -f /workspace/project-nexus/v2/backend/logs/nexuslang.log

# Monitor resources
htop
```

### 2. Set Up Logging

```bash
# Create log directory
mkdir -p /workspace/nexuslang/logs

# Update logging in main.py
import logging
logging.basicConfig(
    filename='/workspace/nexuslang/logs/api.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### 3. Health Monitoring Script

Create `/workspace/monitor.sh`:

```bash
#!/bin/bash
# Monitor NexusLang health

while true; do
    STATUS=$(curl -s http://localhost:8000/health | jq -r '.status')
    if [ "$STATUS" != "healthy" ]; then
        echo "❌ Service unhealthy! Restarting..."
        systemctl restart nexuslang
    else
        echo "✅ Service healthy"
    fi
    sleep 60
done
```

---

## 🚀 PRODUCTION CHECKLIST FOR RUNPOD

### Before Going Live

- [ ] JWT_SECRET_KEY generated and set (64+ chars)
- [ ] Database configured (PostgreSQL recommended)
- [ ] Redis configured and connected
- [ ] CORS origins set to production URLs
- [ ] DEBUG=false in .env
- [ ] All tests passing (`pytest tests/test_security.py -v`)
- [ ] Security scan passing (`./scripts/security-scan.sh`)
- [ ] Logs directory created and writable
- [ ] Backup strategy configured
- [ ] Monitoring set up
- [ ] RunPod pod set to "Always On" (not spot instance)

### After Deployment

- [ ] Test all API endpoints via `/docs`
- [ ] Verify security headers present
- [ ] Test account lockout (5 failed logins)
- [ ] Test password reset flow
- [ ] Monitor logs for errors
- [ ] Set up alerts for downtime
- [ ] Document your RunPod URL for team

---

## 🔥 PERFORMANCE OPTIMIZATION

### 1. Use RunPod GPU (Optional)

If using AI features:

```python
# In main.py, detect GPU
import torch

if torch.cuda.is_available():
    print(f"✅ GPU Available: {torch.cuda.get_device_name(0)}")
    device = "cuda"
else:
    print("⚠️  Using CPU")
    device = "cpu"
```

### 2. Worker Configuration

```bash
# For RunPod A4000 (16GB RAM):
uvicorn main:app --workers 4 --host 0.0.0.0 --port 8000

# For RunPod A6000 (48GB RAM):
uvicorn main:app --workers 8 --host 0.0.0.0 --port 8000
```

### 3. Database Connection Pooling

In `config.py`:
```python
# Optimize for RunPod's network
POOL_SIZE = 20
MAX_OVERFLOW = 10
POOL_TIMEOUT = 30
```

---

## 🆘 TROUBLESHOOTING

### Issue: Port 8000 not accessible

**Solution:**
```bash
# Check if service is running
netstat -tlnp | grep 8000

# Check RunPod port forwarding
# In RunPod Dashboard → Ports → Add 8000:8000
```

### Issue: Database locked

**Solution:**
```bash
# If using SQLite, ensure it's in /workspace
DATABASE_URL=sqlite+aiosqlite:////workspace/nexuslang/nexuslang.db

# Or switch to PostgreSQL
```

### Issue: Out of memory

**Solution:**
```bash
# Reduce workers
uvicorn main:app --workers 1 --host 0.0.0.0 --port 8000

# Or upgrade RunPod instance
```

### Issue: Logs not persisting

**Solution:**
```bash
# Store logs in /workspace
mkdir -p /workspace/nexuslang/logs
# Update logging path in code
```

---

## 📞 SUPPORT

### RunPod-Specific Help
- **RunPod Docs:** https://docs.runpod.io
- **RunPod Discord:** https://discord.gg/runpod
- **RunPod Support:** support@runpod.io

### NexusLang Security
- **Security Issues:** security@nexuslang.dev
- **Documentation:** See `SECURITY_DEPLOYMENT_CHECKLIST.md`

---

## 🎯 NEXT STEPS

1. **Deploy to RunPod** using automated script
2. **Test all endpoints** via `/docs`
3. **Set up monitoring** and alerts
4. **Configure backups** for `/workspace`
5. **Update frontend** to use RunPod URL
6. **Go live!** 🚀

---

## 📋 RUNPOD TEMPLATE (Save This)

For quick deployments, save this as a RunPod template:

**Container Image:** `python:3.11-slim`
**Docker Command:**
```bash
cd /workspace/project-nexus/v2/backend && ./start.sh
```

**Environment Variables:**
```
JWT_SECRET_KEY=<generated-secret>
DATABASE_URL=sqlite+aiosqlite:////workspace/nexuslang.db
REDIS_URL=redis://localhost:6379/1
DEBUG=false
```

**Exposed Ports:** `8000`
**Volume Mounts:** `/workspace` (persistent)

---

**🚀 Your NexusLang v2 is now ready for RunPod deployment!**

*Optimized for RunPod's infrastructure with full security features enabled.*
