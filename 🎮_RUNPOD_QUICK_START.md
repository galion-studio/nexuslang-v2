# 🎮 RunPod Quick Start - NexusLang v2

**Deploy in 10 Minutes with GPU Acceleration!**

---

## ⚡ Quick Deploy (5 Commands)

```bash
# 1. SSH into your RunPod pod
ssh root@ssh.runpod.io -p YOUR_PORT

# 2. Clone repository
cd /workspace
git clone https://github.com/your-org/project-nexus.git
cd project-nexus

# 3. Run deploy script
chmod +x runpod-deploy.sh
./runpod-deploy.sh

# 4. Get your URLs
cat /workspace/RUNPOD_URLS.txt

# 5. Open in browser!
# https://YOUR_POD_ID-3000.proxy.runpod.net
```

**That's it! Your platform is live! 🎉**

---

## 🖥️ Creating Your RunPod Pod

### Step 1: Sign Up
- Go to https://runpod.io
- Create account
- Add $10+ credit

### Step 2: Deploy Pod

**In RunPod Console:**
1. Click "Deploy" → "GPU Pod" or "CPU Pod"
2. Select GPU:
   - **Development:** RTX 3070 ($0.29/hr)
   - **Production:** RTX 4090 ($0.69/hr)
   - **Budget:** CPU only ($0.20/hr)
3. **Container Disk:** 50 GB
4. **Volume Disk:** 100 GB
5. **Ports to Expose:**
   - 3000 (Frontend)
   - 8000 (Backend)
   - 9090 (Prometheus - optional)
   - 3001 (Grafana - optional)
6. Click **"Deploy On-Demand"** or **"Deploy Spot"** (cheaper)

### Step 3: Connect

```bash
# From RunPod console, copy SSH command
ssh root@ssh.runpod.io -p YOUR_PORT
```

---

## 🚀 What You Get

### GPU-Accelerated Features
- ✅ **Whisper STT** - 10-30x faster speech recognition
- ✅ **TTS** - 5-10x faster speech synthesis
- ✅ **Real-time processing** - Voice responses in <1 second
- ✅ **Model caching** - First load slow, then instant

### Automatic Features
- ✅ **HTTPS** - RunPod proxy provides SSL automatically
- ✅ **Port Forwarding** - No complex networking needed
- ✅ **Persistent Storage** - Data saved in /workspace
- ✅ **GPU Drivers** - Pre-installed and configured

### Access URLs
```
Frontend: https://POD_ID-3000.proxy.runpod.net
Backend:  https://POD_ID-8000.proxy.runpod.net
API Docs: https://POD_ID-8000.proxy.runpod.net/docs
```

---

## 💰 Cost Breakdown

### Development (8 hrs/day)
| Item | Cost |
|------|------|
| RTX 3070 Pod | $0.29/hr × 240 hrs = $69.60 |
| Storage (100GB) | $3/month |
| **Total** | **~$73/month** |

### Production (24/7 Spot)
| Item | Cost |
|------|------|
| RTX 4090 Spot | $0.29/hr × 720 hrs = $208 |
| Storage (100GB) | $3/month |
| **Total** | **~$211/month** |

**vs VPS:** Traditional VPS with GPU costs $500-1000/month!

---

## 🎯 After Deployment

### Test Your Platform

```bash
# Get your pod ID
POD_ID=$(hostname | cut -d'-' -f1 | head -c 10)

# Test backend
curl https://${POD_ID}-8000.proxy.runpod.net/health

# Open frontend
echo "Frontend: https://${POD_ID}-3000.proxy.runpod.net"
```

### First User Setup

1. Open frontend URL
2. Click "Sign Up"
3. Create account
4. Go to IDE (`/ide`)
5. Write NexusLang code
6. Click "Run" - see results instantly!

### Test GPU Features

**Voice Recording:**
1. Go to IDE
2. Click microphone icon
3. Record your voice
4. Watch real-time transcription (powered by GPU!)

**Knowledge Search:**
1. Go to Grokopedia (`/grokopedia`)
2. Search "machine learning"
3. See AI-powered semantic results

---

## 🛠️ Management

### View Logs
```bash
docker-compose -f docker-compose.runpod.yml logs -f
```

### Restart Services
```bash
docker-compose -f docker-compose.runpod.yml restart
```

### Update Code
```bash
cd /workspace/project-nexus
git pull
docker-compose -f docker-compose.runpod.yml up -d --build
```

### Backup Database
```bash
docker-compose -f docker-compose.runpod.yml exec postgres \
  pg_dump -U nexus nexus_v2 > /workspace/backup_$(date +%Y%m%d).sql
```

### Monitor GPU
```bash
# Real-time GPU usage
watch -n 1 nvidia-smi

# Check which processes use GPU
nvidia-smi pmon
```

---

## 🎮 RunPod-Specific Tips

### 1. Keep Everything in /workspace
```
/workspace/
├── project-nexus/      # Your code
├── postgres-data/      # Database (persists)
├── redis-data/         # Cache (persists)
├── models/             # AI models (cached)
├── backups/            # Database backups
└── RUNPOD_URLS.txt     # Your access URLs
```

### 2. Use Spot Instances
- Save 50-70% on costs
- Auto-restart on interruption
- Perfect for development

### 3. Stop When Not Using
```bash
# In RunPod console: Click "Stop Pod"
# Data in /workspace is preserved
# No charges while stopped!
```

### 4. Share with Team
```
Just share the RunPod proxy URL:
https://YOUR_POD_ID-3000.proxy.runpod.net

Anyone can access (no VPN needed)!
```

---

## ⚠️ Important Notes

### Data Persistence
- ✅ `/workspace` → **Persists** between restarts
- ❌ Other directories → **Lost** on restart
- Always use `/workspace` for important data

### GPU Memory
- Monitor with `nvidia-smi`
- Whisper base model: ~1GB GPU RAM
- TTS model: ~500MB GPU RAM
- Total: <2GB for both (plenty of room)

### Network
- RunPod proxy provides automatic HTTPS
- No port forwarding configuration needed
- URLs work immediately after deployment

### Spot vs On-Demand
- **Spot:** Cheaper, can be interrupted
- **On-Demand:** More expensive, guaranteed availability
- **Recommendation:** Spot for development, On-Demand for production

---

## 🆘 Troubleshooting

### "GPU not found"
```bash
# Check NVIDIA drivers
nvidia-smi

# Should show your GPU
# If not, contact RunPod support
```

### "Port not accessible"
```bash
# In RunPod console:
# 1. Click your pod
# 2. Go to "Edit"
# 3. Add ports 3000 and 8000 to "Expose Ports"
# 4. Save and restart pod
```

### "Services won't start"
```bash
# Check Docker
docker ps -a

# Check logs
docker-compose -f docker-compose.runpod.yml logs

# Restart everything
docker-compose -f docker-compose.runpod.yml down
docker-compose -f docker-compose.runpod.yml up -d
```

### "Out of disk space"
```bash
# Check space
df -h

# Clean Docker
docker system prune -af

# Increase volume size in RunPod console
```

---

## 🎉 Success!

Once deployed, you'll have:

- ✅ **Full NexusLang v2 Platform** running
- ✅ **GPU acceleration** for AI features
- ✅ **Public HTTPS URLs** for sharing
- ✅ **Persistent storage** for data
- ✅ **Automatic SSL** via RunPod
- ✅ **Easy management** via Docker Compose

**Share your RunPod URL and start building the future!** 🚀

---

## 📚 Full Documentation

For detailed information, see:
- **v2/RUNPOD_DEPLOYMENT_GUIDE.md** - Complete guide
- **README.md** - Platform overview
- **v2/PRODUCTION_DEPLOYMENT_GUIDE.md** - Alternative deployment options

---

**Your NexusLang v2 Platform is now live on RunPod!**

🎮 **Powered by GPU** • 🚀 **Ready to Scale** • 💰 **Cost Effective**

