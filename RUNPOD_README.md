# 🎮 RunPod Deployment - NexusLang v2

**Deploy your AI platform in 10 minutes with GPU acceleration!**

---

## 🚀 Quick Deploy (3 Steps)

### Step 1: Create RunPod Pod (3 minutes)

1. Go to https://runpod.io
2. Create account + add $10 credit
3. Click "Deploy" → Choose GPU:
   - **RTX 3070** - $0.29/hour (recommended for dev)
   - **RTX 4090** - $0.69/hour (recommended for production)
4. Set **Container Disk: 50GB**, **Volume: 100GB**
5. **Expose Ports:** 3000, 8000
6. Click "Deploy"

### Step 2: Connect & Deploy (5 minutes)

```bash
# SSH to pod (get command from RunPod console)
ssh root@ssh.runpod.io -p YOUR_PORT

# Clone and deploy
cd /workspace
git clone https://github.com/your-org/project-nexus.git
cd project-nexus

# Configure
cp env.runpod.template .env
nano .env  # Add your OpenAI API key

# Deploy!
chmod +x runpod-deploy.sh
./runpod-deploy.sh
```

### Step 3: Access & Test (2 minutes)

```bash
# Get your URLs
cat /workspace/RUNPOD_URLS.txt

# Open in browser
# https://YOUR_POD_ID-3000.proxy.runpod.net
```

**That's it! Your platform is live!** 🎉

---

## 💰 Costs

| Usage | GPU | Hours/Month | Cost/Month |
|-------|-----|-------------|------------|
| **Light Dev** | RTX 3070 | 120 (4hrs/day) | $35 |
| **Heavy Dev** | RTX 3070 | 240 (8hrs/day) | $70 |
| **Production 24/7** | RTX 4090 Spot | 720 | $208 |

**Stop pod when not using = $0**

---

## ✨ What You Get

### GPU-Accelerated
- ⚡ Whisper STT: 10-30x faster
- ⚡ TTS: 5-10x faster
- ⚡ Real-time voice processing
- ⚡ Instant model loading (after cache)

### Automatic
- 🔒 HTTPS (no configuration!)
- 🌐 Public URLs (share immediately!)
- 💾 Persistent storage (/workspace)
- 🔄 Auto-restart on failure

### Complete Platform
- ✅ Web IDE with code execution
- ✅ Knowledge base with AI search
- ✅ Voice recording/playback
- ✅ Billing system
- ✅ Community features

---

## 🎯 Quick Commands

```bash
# View logs
docker-compose -f docker-compose.runpod.yml logs -f

# Restart services
docker-compose -f docker-compose.runpod.yml restart

# Check health
curl http://localhost:8000/health

# Monitor GPU
nvidia-smi

# Stop (save money!)
docker-compose -f docker-compose.runpod.yml stop

# Start again
docker-compose -f docker-compose.runpod.yml start
```

---

## 📚 Full Guides

- **🎮_DEPLOY_TO_RUNPOD_NOW.md** - Ultra-quick start
- **🎮_RUNPOD_QUICK_START.md** - Detailed guide
- **v2/RUNPOD_DEPLOYMENT_GUIDE.md** - Complete reference

---

## 🆘 Issues?

### Can't connect to pod
Wait 2-3 minutes after creation

### GPU not found
```bash
nvidia-smi  # Should show your GPU
```

### Services won't start
```bash
docker-compose -f docker-compose.runpod.yml logs
```

### Need help
- RunPod Discord: https://discord.gg/runpod
- RunPod Docs: https://docs.runpod.io

---

## 🎊 Success!

Once deployed, share your URL:

```
https://YOUR_POD_ID-3000.proxy.runpod.net
```

**Features working:**
- ✅ Web IDE
- ✅ Code execution
- ✅ Knowledge search
- ✅ Voice features (GPU!)
- ✅ User accounts
- ✅ Billing system
- ✅ Community

**Ready for beta testing!** 🚀

---

**NexusLang v2 • RunPod Optimized • GPU Powered • Launch Ready**

