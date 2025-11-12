# 🔥 DEPLOY NEXUSLANG V2 NOW!

**Copy these commands to your RunPod terminal**

---

## 🚀 DEPLOYMENT COMMANDS

### **SSH into your RunPod server, then copy-paste this:**

```bash
# Navigate to your project
cd /workspace/project-nexus

# Make deployment script executable
chmod +x v2/deploy-nexuslang-to-runpod.sh

# Run deployment
./v2/deploy-nexuslang-to-runpod.sh
```

**Wait 5 minutes for services to start...**

---

## ✅ VERIFY DEPLOYMENT

```bash
# Check NexusLang is running
curl http://localhost:8100/health

# Check containers
docker ps | grep nexuslang

# View logs
cd v2 && docker-compose -f docker-compose.nexuslang.yml logs -f
```

**Press Ctrl+C to exit logs when you see services running**

---

## 🌐 EXPOSE PORTS IN RUNPOD

**In RunPod Dashboard:**
1. Find your pod
2. Click **"Edit"**
3. Scroll to **"Expose HTTP Ports"**
4. Add: **3100**
5. Add: **8100**
6. Click **"Save"**

**You'll get URLs like:**
```
https://xxxxx-3100.proxy.runpod.net
https://xxxxx-8100.proxy.runpod.net
```

**Open the 3100 URL in your browser → You're LIVE!** 🎉

---

## 📝 QUICK TEST

**Open in browser:**
```
https://your-runpod-3100-url/ide
```

**You should see:**
- NexusLang v2 IDE
- Can register account
- Can write and run code
- Everything works!

---

## 🎊 SHARE WITH USERS

**Send this:**
```
🚀 NexusLang v2 Alpha is LIVE!

Try it: https://your-runpod-3100-url/ide

Features:
⚡ Binary compilation (10x faster)
🧠 Personality system
📚 Knowledge queries
🎤 Voice commands

Free for alpha - start coding now!
```

---

**DEPLOY COMMAND:**
```bash
cd /workspace/project-nexus && ./v2/deploy-nexuslang-to-runpod.sh
```

**GO!** 🚀

