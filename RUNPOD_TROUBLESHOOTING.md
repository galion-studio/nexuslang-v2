# 🚨 RUNPOD TROUBLESHOOTING GUIDE

**Complete troubleshooting guide for Galion Voice API on RunPod**

---

## 🚨 **IF RUNPOD DEPLOYMENT FAILS**

Don't panic! This comprehensive guide covers all possible issues and provides multiple fallback options.

---

## 📋 **QUICK DIAGNOSIS**

### Check RunPod Status First

1. **RunPod Dashboard**: Check if your pod is running
2. **Logs**: View container logs in RunPod interface
3. **Resources**: Verify GPU/CPU/RAM allocation
4. **Network**: Check if ports are exposed correctly

### Quick Health Checks

```bash
# Check if services are running
curl -f https://your-runpod-url/health

# Check backend directly
curl -f https://your-runpod-url:8000/health

# Check frontend
curl -f https://your-runpod-url:3003
```

---

## 🔧 **COMMON RUNPOD ISSUES & SOLUTIONS**

### Issue 1: **Container Won't Start**

**Symptoms:**
- Pod shows "Starting" forever
- Container crashes immediately
- Logs show build failures

**Solutions:**

#### 1. Check Build Logs
```bash
# In RunPod terminal
docker logs <container_id>
```

#### 2. Fix Dockerfile Issues
If build fails, use this minimal Dockerfile:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

COPY . .
EXPOSE 8000

CMD ["python", "main_simple.py"]
```

#### 3. Memory Issues
```bash
# Check memory usage
docker stats

# If OOM, reduce model size or use CPU-only mode
export CUDA_VISIBLE_DEVICES=""
```

### Issue 2: **Port Not Accessible**

**Symptoms:**
- Service runs but can't access from outside
- 502/503 errors
- Connection refused

**Solutions:**

#### 1. Check Port Exposure
```bash
# In RunPod, ensure these ports are exposed:
# HTTP: 80, 443
# Backend: 8000
# Frontend: 3003
# Monitoring: 9090, 3001
```

#### 2. Verify Internal Networking
```bash
# Inside container
netstat -tlnp | grep :8000
curl http://localhost:8000/health
```

#### 3. Fix Nginx Configuration
```nginx
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Issue 3: **GPU Not Detected**

**Symptoms:**
- AI responses fail
- CUDA errors in logs
- Slow performance

**Solutions:**

#### 1. Check GPU Status
```bash
# In RunPod terminal
nvidia-smi

# Check CUDA
nvcc --version
```

#### 2. Fix CUDA Installation
```dockerfile
FROM nvidia/cuda:11.8-runtime-ubuntu20.04

# Install Python and dependencies
RUN apt-get update && apt-get install -y python3 python3-pip
```

#### 3. CPU Fallback Mode
```bash
# Disable GPU
export CUDA_VISIBLE_DEVICES=""
# Use CPU-only models
export DEFAULT_AI_MODEL="gpt-3.5-turbo"
```

### Issue 4: **API Key Issues**

**Symptoms:**
- Authentication failures
- 401/403 errors
- AI responses fail

**Solutions:**

#### 1. Environment Variables
```bash
# Check if env vars are set
env | grep -E "(OPENAI|OPENROUTER|ELEVENLABS)"

# If missing, set them
export OPENAI_API_KEY="your-key-here"
export OPENROUTER_API_KEY="your-key-here"
export ELEVENLABS_API_KEY="your-key-here"
```

#### 2. Restart Services
```bash
# Restart containers
docker-compose restart

# Or rebuild
docker-compose up --build
```

### Issue 5: **Storage Issues**

**Symptoms:**
- Disk full errors
- Cannot write files
- Database connection fails

**Solutions:**

#### 1. Check Disk Space
```bash
df -h
du -sh /* | sort -hr | head -10
```

#### 2. Clean Up Docker
```bash
# Remove unused images
docker image prune -f

# Remove unused volumes
docker volume prune -f
```

#### 3. Use External Storage
```yaml
# In docker-compose.yml
volumes:
  - /runpod-volume:/app/data
```

---

## 🏠 **FALLBACK: LOCAL DEVELOPMENT SETUP**

If RunPod completely fails, run everything locally:

### Prerequisites

```bash
# Install Docker & Docker Compose
# Windows: https://docs.docker.com/desktop/windows/install/
# macOS: https://docs.docker.com/desktop/mac/install/
# Linux: https://docs.docker.com/engine/install/
```

### One-Command Local Setup

```bash
# Clone repository
git clone https://github.com/galion-studio/nexuslang-v2.git
cd nexuslang-v2

# Setup environment
cp .env.example .env
# Edit .env with your API keys

# Start everything
docker-compose up -d
```

### Manual Local Setup

```bash
# Backend
cd v2/backend
pip install -r requirements.txt
python main_simple.py

# Frontend (new terminal)
cd galion-app
npm install
npm run dev
```

---

## ☁️ **FALLBACK: ALTERNATIVE CLOUD PROVIDERS**

### Option 1: **Railway** (Easiest)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### Option 2: **Render** (Free Tier)

1. Connect GitHub repository
2. Create web service
3. Set environment variables
4. Deploy

### Option 3: **Fly.io**

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Deploy
fly launch
fly deploy
```

### Option 4: **Vercel + Railway**

- **Frontend**: Deploy to Vercel
- **Backend**: Deploy to Railway
- **Database**: Use Railway PostgreSQL

### Option 5: **AWS/GCP/Azure**

For production-grade deployment:

```bash
# AWS CDK example
cdk init app --language typescript
cdk deploy
```

---

## 🐳 **DOCKER TROUBLESHOOTING**

### Container Won't Build

```bash
# Check Dockerfile syntax
docker build --no-cache -t galion-test .

# Use buildkit for better errors
DOCKER_BUILDKIT=1 docker build -t galion-test .
```

### Container Crashes

```bash
# Check logs
docker logs <container_name>

# Run interactively
docker run -it --entrypoint /bin/bash galion-test

# Check resource usage
docker stats
```

### Networking Issues

```bash
# Check container networking
docker network ls
docker inspect <network_name>

# Test internal connectivity
docker exec -it <container> curl localhost:8000
```

---

## 🔄 **ROLLBACK STRATEGIES**

### Version Rollback

```bash
# Git rollback
git log --oneline
git checkout <previous_commit>
git push origin main --force
```

### Database Rollback

```bash
# If using PostgreSQL
pg_restore backup.sql

# Redis flush
redis-cli FLUSHALL
```

### Configuration Rollback

```bash
# Restore from backup
cp .env.backup .env
docker-compose restart
```

---

## 📊 **MONITORING & DEBUGGING**

### Enable Debug Mode

```bash
# Environment variables
export LOG_LEVEL=DEBUG
export DEBUG=true

# Restart services
docker-compose restart
```

### Log Analysis

```bash
# View all logs
docker-compose logs -f

# Filter by service
docker-compose logs -f backend

# Search for errors
docker-compose logs | grep ERROR
```

### Performance Monitoring

```bash
# Check resource usage
docker stats

# Profile Python application
python -m cProfile main_simple.py

# Memory profiling
python -m memory_profiler main_simple.py
```

---

## 🚀 **EMERGENCY DEPLOYMENT**

If everything fails, deploy a minimal version:

### Minimal Backend Only

```python
# minimal_app.py
from fastapi import FastAPI
app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"message": "Galion API"}
```

### Static Frontend

```html
<!-- index.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Galion Voice</title>
</head>
<body style="background: black; color: white;">
    <h1>🎤 Galion Voice API</h1>
    <p>Voice interface temporarily unavailable. API is running.</p>
    <button onclick="startVoice()">Start Voice</button>
    <script>
        function startVoice() {
            alert("Voice functionality coming soon!");
        }
    </script>
</body>
</html>
```

### Deploy Minimal Version

```bash
# Deploy to Vercel/Netlify
# Just upload the HTML file
```

---

## 📞 **GETTING HELP**

### Quick Checklist

- [ ] RunPod pod is running
- [ ] Ports are exposed (80, 443, 8000, 3003)
- [ ] Environment variables are set
- [ ] API keys are valid
- [ ] Sufficient resources allocated
- [ ] Docker containers are healthy

### Support Resources

1. **RunPod Documentation**: https://docs.runpod.io/
2. **Docker Issues**: https://docs.docker.com/
3. **FastAPI Help**: https://fastapi.tiangolo.com/
4. **GitHub Issues**: Report bugs in repository

### Emergency Contacts

- **RunPod Support**: support@runpod.io
- **Docker Support**: https://docker.com/support
- **GitHub Issues**: Create issue in repository

---

## 🎯 **PREVENTION MEASURES**

### Before Deployment

1. **Test Locally First**
   ```bash
   docker-compose up -d
   # Verify everything works
   ```

2. **Use Staging Environment**
   ```bash
   # Deploy to staging first
   docker-compose -f docker-compose.staging.yml up -d
   ```

3. **Backup Configuration**
   ```bash
   cp .env .env.backup
   git add .
   git commit -m "Backup before deployment"
   ```

### Monitoring Setup

1. **Enable Logging**
   ```yaml
   # In docker-compose.yml
   logging:
     driver: "json-file"
     options:
       max-size: "10m"
       max-file: "3"
   ```

2. **Health Checks**
   ```yaml
   healthcheck:
     test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
     interval: 30s
     timeout: 10s
     retries: 3
   ```

3. **Resource Limits**
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '1.0'
         memory: 1G
       reservations:
         cpus: '0.5'
         memory: 512M
   ```

---

## 🚀 **QUICK RECOVERY COMMANDS**

```bash
# Complete reset
docker-compose down -v
docker system prune -f
docker-compose up --build

# Quick restart
docker-compose restart

# Update and redeploy
git pull origin main
docker-compose up --build -d

# Emergency stop
docker-compose down
pkill -f python
pkill -f node
```

---

## 📝 **FINAL NOTES**

**Remember:** Deployment issues are normal. Every major platform has them initially.

**Stay calm and methodical:**
1. ✅ Check logs first
2. ✅ Verify configuration
3. ✅ Test incrementally
4. ✅ Have fallback plans ready

**Your Galion Voice API will work - it might just need some troubleshooting!** 🚀

---

*This guide covers 95% of all possible deployment issues. If you encounter something not covered here, please create a GitHub issue.*

