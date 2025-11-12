# 🚀 Deploy NexusLang v2 to RunPod RIGHT NOW

**5-minute checklist to get your platform live**

---

## ✅ STEP-BY-STEP (Copy & Paste Commands)

### Step 1: Create RunPod Pod (2 minutes)

**Go to:** https://www.runpod.io/

1. Click **"Deploy"**
2. Choose **"GPU Pods"** or **"CPU Pods"**
3. Select template: **"RunPod Pytorch"** (has Docker pre-installed)
4. Set disk: **30 GB**
5. **IMPORTANT:** Expose HTTP Ports: **3000, 8000**
6. Click **"Deploy On-Demand"**

**Cost:** ~$0.30/hour (stop when not using)

---

### Step 2: Connect via SSH (30 seconds)

**In RunPod dashboard:**
1. Find your pod
2. Click **"Connect"** → **"Start Web Terminal"** (easiest)
   - OR copy SSH command and paste in your terminal

**You're now in your cloud server!** ☁️

---

### Step 3: Deploy NexusLang v2 (2 minutes)

**Copy-paste this ENTIRE block into your RunPod terminal:**

```bash
# Install requirements
apt-get update && apt-get install -y git curl

# Clone your project
cd /workspace
git clone https://github.com/your-org/project-nexus.git
cd project-nexus

# Run automated deployment
chmod +x v2/infrastructure/scripts/deploy-runpod.sh
./v2/infrastructure/scripts/deploy-runpod.sh
```

**The script will:**
- ✅ Install Docker & Compose (if needed)
- ✅ Generate secure secrets
- ✅ Set up environment
- ✅ Build all services
- ✅ Start the platform

**Wait 3 minutes...** ⏳

---

### Step 4: Get Your Public URL (30 seconds)

**In RunPod dashboard:**
1. Find your pod
2. Look for **"TCP Port Mappings"**
3. Find port **3000** → Copy the external address
4. Find port **8000** → Copy the external address

**Example:**
- Port 3000 → `https://abc123-3000.proxy.runpod.net`
- Port 8000 → `https://abc123-8000.proxy.runpod.net`

---

### Step 5: Open and Test! (1 minute)

**Open in browser:**
```
https://your-pod-3000.proxy.runpod.net
```

**You should see:** NexusLang v2 landing page! 🎉

**Click:** "Start Coding Now" or go to `/ide`

**Register account → Start coding!**

---

## 🎊 YOU'RE LIVE!

**Share with users:**
```
🚀 NexusLang v2 Alpha is live!

Try it now: https://your-pod-3000.proxy.runpod.net/ide

Features:
✨ Binary compilation (10x faster)
🧠 Personality system
📚 Knowledge integration
🎤 Voice commands

Free to use - register and start coding!
```

---

## 🔧 If Something Goes Wrong

### Ports not accessible?
**Fix:** Edit pod → Expose HTTP Ports → Add 3000, 8000

### Services not starting?
```bash
# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Restart
docker-compose restart
```

### Need to update code?
```bash
cd /workspace/project-nexus
git pull
docker-compose up -d --build
```

---

## 💰 Cost Control

**While testing:**
- Keep pod running: ~$7/day
- Stop when not using: $0

**To stop:**
- RunPod dashboard → Your pod → **Stop**
- To restart: Click **Start**

**To save state:**
- Use **"Persistent Volume"** when creating pod
- Your data survives stops/starts

---

## 🎯 ALTERNATIVE: GitHub Codespaces

**If RunPod seems complex:**

1. Push your code to GitHub
2. Open in Codespaces
3. Run: `docker-compose up -d`
4. Forward ports 3000, 8000
5. Access via Codespaces URL

**Cost:** Free for 60 hours/month!

---

## 📞 Quick Commands Reference

```bash
# Check what's running
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Restart everything
docker-compose restart

# Stop everything
docker-compose down

# Start again
docker-compose up -d

# Check backend health
curl http://localhost:8000/health
```

---

## 🚀 YOU'RE READY!

**What to do NOW:**

1. ✅ **Deploy to RunPod** (follow steps above)
2. ✅ **Test yourself** (register, create project, run code)
3. ✅ **Share URL** with 5-10 waiting users
4. ✅ **Collect feedback** (what works, what doesn't)
5. ✅ **Iterate** (fix bugs, add features)

---

## 📋 RunPod Deployment Checklist

- [ ] RunPod account created
- [ ] Pod deployed (CPU or GPU)
- [ ] Ports exposed (3000, 8000)
- [ ] SSH connected
- [ ] Deployment script executed
- [ ] Services running (`docker-compose ps`)
- [ ] Frontend accessible (http://pod-ip:3000)
- [ ] Backend responding (http://pod-ip:8000/health)
- [ ] Can register account
- [ ] Can run code in IDE
- [ ] Shared with users!

---

**⏱️ TOTAL TIME: 5-10 MINUTES**

**🎊 RESULT: LIVE PLATFORM FOR USERS!**

---

**GO TO RUNPOD.IO AND START!** 🚀

_See `RUNPOD_DEPLOYMENT.md` for detailed guide_  
_See `RUNPOD_QUICK_START.md` for quick reference_

