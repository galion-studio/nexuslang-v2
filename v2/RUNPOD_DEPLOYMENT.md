# 🚀 NexusLang v2 - RunPod Deployment Guide

**Deploy to RunPod for instant online testing and development**

---

## Why RunPod?

✅ **No local setup** - Everything runs in the cloud  
✅ **GPU access** - For future ML features  
✅ **Always accessible** - Test from anywhere  
✅ **Professional** - Production-ready environment  
✅ **Cost-effective** - Pay only when running

---

## Quick Deploy (5 Minutes)

### Step 1: Create RunPod Account
1. Go to https://www.runpod.io/
2. Sign up (free account available)
3. Add billing info (required for pods)

### Step 2: Deploy with Our Template

**Option A: Use Docker Image (Recommended)**

1. **Create Pod:**
   - Click "Deploy"
   - Select "GPU Pods" or "CPU Pods"
   - Choose: Ubuntu 22.04 + Docker
   - Storage: 20GB minimum
   - Expose ports: 8000, 3000

2. **After pod starts, connect via SSH:**
   ```bash
   # Get SSH command from RunPod dashboard
   ssh root@your-pod-ip -p your-port
   ```

3. **Clone and start:**
   ```bash
   # Inside the pod
   git clone https://github.com/your-org/project-nexus.git
   cd project-nexus
   docker-compose up -d
   ```

**Option B: Manual Setup**

See full guide below.

---

## Full RunPod Setup Guide

### Step 1: Create Pod

**In RunPod Dashboard:**
1. Click **"Deploy"**
2. Select **GPU Pods** (or CPU for cheaper testing)
3. Template: **Ubuntu 22.04 LTS**
4. Container Disk: **20 GB**
5. Volume: **50 GB** (persistent storage)
6. Expose HTTP Ports: **8000, 3000, 5432, 6379**

### Step 2: Connect to Pod

```bash
# Get connection details from RunPod dashboard
ssh root@<pod-ip> -p <ssh-port>
```

### Step 3: Install Docker (if not installed)

```bash
# Update system
apt-get update && apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Verify
docker --version
docker-compose --version
```

### Step 4: Deploy NexusLang v2

```bash
# Clone repository
git clone https://github.com/your-org/project-nexus.git
cd project-nexus

# Create environment file
cat > v2/backend/.env << EOF
DATABASE_URL=postgresql://nexus:nexuspass@postgres:5432/nexuslang_v2
REDIS_URL=redis://redis:6379/0
JWT_SECRET=$(openssl rand -hex 32)
SECRET_KEY=$(openssl rand -hex 32)
DEBUG=false
CORS_ORIGINS=["*"]
EOF

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Step 5: Access Your Deployment

**Get your pod's public URL from RunPod dashboard:**

- **Frontend:** `http://<pod-ip>:3000`
- **Backend API:** `http://<pod-ip>:8000`
- **API Docs:** `http://<pod-ip>:8000/docs`

**Test:**
```bash
# Check health
curl http://<pod-ip>:8000/health

# Should return:
# {"status":"healthy","service":"nexuslang-v2-api","version":"2.0.0-beta"}
```

---

## 🎯 Simplified One-Command Deploy

I've created a deployment script for you:

```bash
# Use the automated script
cd project-nexus
chmod +x v2/infrastructure/scripts/deploy-runpod.sh
./v2/infrastructure/scripts/deploy-runpod.sh
```

---

## 🐛 Troubleshooting

### Ports Not Accessible?
**In RunPod dashboard:**
1. Go to your pod settings
2. Click "Edit"
3. Add exposed HTTP ports: 3000, 8000
4. Save and restart pod

### Docker Compose Fails?
```bash
# Check Docker is running
systemctl status docker

# Check compose file
cd project-nexus
docker-compose config

# View detailed logs
docker-compose logs backend
docker-compose logs frontend
```

### Out of Memory?
- Upgrade to larger pod
- Or reduce container resources in docker-compose.yml

---

## 💰 RunPod Costs

**CPU Pods (Testing):**
- ~$0.10/hour
- ~$70/month if running 24/7
- Stop when not using to save money

**GPU Pods (ML Features):**
- ~$0.30-0.50/hour
- Use only when needed
- Stop after testing

**Recommendation:**
- Start with CPU pod for alpha
- Scale to GPU when adding ML training
- Use "Spot" instances for 50% savings

---

## 🎮 Using Your RunPod Deployment

### Access the IDE
```
http://<your-runpod-ip>:3000/ide
```

### Share with Users
```
# Your alpha testers can access:
http://<your-runpod-ip>:3000

# Or set up a custom domain:
nexuslang.your-domain.com → your-runpod-ip:3000
```

### Monitor
```bash
# SSH into pod
ssh root@<pod-ip> -p <ssh-port>

# Check logs
cd project-nexus
docker-compose logs -f backend

# Check resource usage
docker stats
```

---

## 🔒 Security for Production

### Add SSL (Cloudflare Tunnel)
```bash
# Install cloudflared
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /usr/local/bin/cloudflared
chmod +x /usr/local/bin/cloudflared

# Create tunnel
cloudflared tunnel login
cloudflared tunnel create nexuslang
cloudflared tunnel route dns nexuslang nexuslang.yourdomain.com

# Run tunnel
cloudflared tunnel --config config.yml run
```

**Result:** Secure HTTPS access to your deployment!

---

## 📊 Performance Monitoring

### Check if Everything is Running
```bash
# In RunPod SSH
cd project-nexus
docker-compose ps

# Should show:
# nexus_postgres    running
# nexus_redis       running  
# nexus_backend     running
# nexus_frontend    running
```

### Test Endpoints
```bash
# Health check
curl http://localhost:8000/health

# List examples
curl http://localhost:8000/api/v2/nexuslang/examples
```

---

## 🚀 GO LIVE CHECKLIST

- [ ] RunPod account created
- [ ] Pod deployed with Docker
- [ ] Services running (docker-compose ps)
- [ ] Health endpoint responding
- [ ] Frontend accessible
- [ ] Can register account
- [ ] Can run code
- [ ] Can save projects
- [ ] Share URL with users!

---

## 💡 Pro Tips

1. **Save Snapshot** - After setup, save pod snapshot to restore quickly
2. **Use Volume** - Persistent storage for database
3. **Stop When Idle** - Save money when not testing
4. **Monitor Logs** - Watch for errors during alpha
5. **Backup Database** - Export regularly

---

## 🎊 YOU'RE MINUTES AWAY FROM LIVE!

**Next command to run:**
```bash
# If you have RunPod SSH access:
git clone https://github.com/your-org/project-nexus.git
cd project-nexus
docker-compose up -d

# Wait 2 minutes for services to start
# Then access: http://<your-pod-ip>:3000
```

**That's it!** 🚀

