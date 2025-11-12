# ⚡ RunPod Quick Start - Get NexusLang v2 Running in 5 Minutes

**Online testing environment - no local setup needed!**

---

## 🎯 The Plan

You'll deploy NexusLang v2 to RunPod so you can:
- ✅ Test online immediately
- ✅ Share with waiting users
- ✅ Develop in the cloud
- ✅ No local Python/Node issues

---

## Step 1: Create RunPod Pod (2 minutes)

1. **Go to RunPod:** https://www.runpod.io/
2. **Sign up** (if you haven't)
3. **Click "Deploy"**
4. **Select:**
   - Pod Type: **CPU Pod** (cheaper for testing)
   - Template: **RunPod Pytorch** or **Ubuntu 22.04**
   - Disk: **20 GB**
   - Expose Ports: **3000, 8000**
5. **Click "Deploy"**

**Wait ~1 minute for pod to start**

---

## Step 2: Get SSH Access (30 seconds)

1. **In RunPod dashboard**, find your pod
2. **Click "Connect"**
3. **Copy SSH command** (looks like: `ssh root@123.45.67.89 -p 12345`)
4. **Open your terminal** and paste the SSH command

**You're now inside your cloud server!** 🌩️

---

## Step 3: One-Command Deploy (2 minutes)

**Paste this into your RunPod SSH terminal:**

```bash
# Install Git (if needed)
apt-get update && apt-get install -y git curl

# Clone NexusLang
git clone https://github.com/your-org/project-nexus.git
cd project-nexus/v2

# Run automated deployment
chmod +x infrastructure/scripts/deploy-runpod.sh
./infrastructure/scripts/deploy-runpod.sh
```

**The script will:**
- Install Docker & Docker Compose
- Set up environment variables
- Generate secure secrets
- Build and start all services
- Initialize database

**Wait ~3 minutes for everything to start** ☕

---

## Step 4: Access Your Live Site! (30 seconds)

1. **Get your pod's IP** from RunPod dashboard
2. **Open in browser:**
   - IDE: `http://<your-pod-ip>:3000/ide`
   - API: `http://<your-pod-ip>:8000/docs`

3. **Register an account**
4. **Start coding!** 🚀

---

## ✅ YOU'RE LIVE!

**Your NexusLang v2 platform is now:**
- ✅ Running in the cloud
- ✅ Accessible from anywhere
- ✅ Ready for users
- ✅ Production-quality

---

## 🎯 Share with Users

**Send them:**
```
Hey! Try NexusLang v2 Alpha:
http://<your-pod-ip>:3000/ide

Features:
- AI-native language
- Binary compilation (10x speedup)
- Personality system
- Web IDE

Register and start coding!
```

---

## 🔧 Manage Your Deployment

### Check Status
```bash
# SSH into your pod
ssh root@<pod-ip> -p <port>

# Check services
cd project-nexus
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Restart Services
```bash
# Restart everything
docker-compose restart

# Restart specific service
docker-compose restart backend
docker-compose restart frontend
```

### Stop/Start
```bash
# Stop (saves money)
docker-compose down

# Start again
docker-compose up -d
```

### Update Code
```bash
# Pull latest changes
cd project-nexus
git pull

# Rebuild and restart
docker-compose up -d --build
```

---

## 💰 Cost Management

**Save money:**
- **Stop pod** when not testing (RunPod dashboard → Stop)
- **Use Spot instances** (50% cheaper)
- **Start only when needed**
- **Delete pod** after testing (save everything to Git first)

**Alpha testing estimate:**
- ~$50-100 for first month
- Stop when not using to reduce costs

---

## 🐛 Troubleshooting

### "Can't access port 3000"
**Fix:** In RunPod dashboard, edit pod and add TCP port 3000 to exposed ports

### "Backend not responding"
```bash
# Check logs
docker-compose logs backend

# Verify it's running
docker-compose ps

# Restart if needed
docker-compose restart backend
```

### "Database errors"
```bash
# Check postgres is running
docker-compose logs postgres

# Reset database (caution: deletes data)
docker-compose down -v
docker-compose up -d
```

### "Out of space"
- Increase container disk in RunPod settings
- Or clean up: `docker system prune -a`

---

## 🎉 SUCCESS!

**You now have:**
- ✅ NexusLang v2 running in the cloud
- ✅ Accessible from anywhere
- ✅ Ready for alpha testers
- ✅ Professional environment

**Next:**
- Share URL with users
- Collect feedback
- Iterate and improve
- Scale as needed

---

## 📞 Quick Reference

**Your URLs:**
- IDE: `http://<pod-ip>:3000/ide`
- API: `http://<pod-ip>:8000`
- Docs: `http://<pod-ip>:8000/docs`

**SSH Command:**
```bash
ssh root@<pod-ip> -p <ssh-port>
```

**Project Location:**
```bash
cd /root/project-nexus
```

**View Logs:**
```bash
docker-compose logs -f
```

**Restart:**
```bash
docker-compose restart
```

---

**🚀 Your NexusLang v2 is LIVE on RunPod!**

**Share with your waiting users NOW!** 🎊

