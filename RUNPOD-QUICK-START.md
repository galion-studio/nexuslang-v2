# 🚀 Galion Platform - RunPod Quick Start Guide

## 📋 One-Command Solutions

### 🎯 **Smart Startup (RECOMMENDED)**
Checks all dependencies, installs missing ones, and starts everything:

```bash
cd /nexuslang-v2
wget -O start.sh https://raw.githubusercontent.com/galion-studio/nexuslang-v2/clean-nexuslang/start-galion-platform.sh && chmod +x start.sh && ./start.sh
```

**What it does:**
- ✅ Checks ALL dependencies (Python, Node.js, system packages)
- ✅ Auto-installs missing dependencies
- ✅ Starts backend, frontend services
- ✅ Configures Nginx
- ✅ Tests everything
- ✅ Shows you access URLs

---

### 🚨 **Emergency Fix**
If services are broken or errored:

```bash
cd /nexuslang-v2
wget -O fix.sh https://raw.githubusercontent.com/galion-studio/nexuslang-v2/clean-nexuslang/emergency-fix-all.sh && chmod +x fix.sh && ./fix.sh
```

**What it does:**
- ✅ Checks and installs all dependencies
- ✅ Completely resets Nginx (fixes corrupted configs)
- ✅ Cleans up errored PM2 processes
- ✅ Starts services fresh
- ✅ Tests and verifies everything

---

### 🔍 **Just Check Dependencies**
Only check and install missing dependencies:

```bash
cd /nexuslang-v2
wget -O check-deps.sh https://raw.githubusercontent.com/galion-studio/nexuslang-v2/clean-nexuslang/check-and-install-deps.sh && chmod +x check-deps.sh && ./check-deps.sh
```

**What it checks:**
- ✅ System packages (Python, Node.js, Nginx, PM2)
- ✅ Python backend packages (FastAPI, Uvicorn, etc.)
- ✅ Galion Studio dependencies (Next.js, React, react-hot-toast)
- ✅ Galion App dependencies
- ✅ Developer Platform dependencies
- ✅ Backend import verification

---

## 🔧 Common Issues & Solutions

### ❌ **Backend "errored" in PM2**
**Cause:** Missing Python dependencies

**Solution:**
```bash
cd /nexuslang-v2
./check-deps.sh
pm2 restart backend
```

---

### ❌ **Galion Studio 500 Error**
**Cause:** Missing `react-hot-toast` dependency

**Solution:**
```bash
cd /nexuslang-v2/galion-studio
npm install react-hot-toast
pm2 restart galion-studio
```

---

### ❌ **Nginx "invalid port 808080" Error**
**Cause:** Corrupted nginx.conf from previous `sed` commands

**Solution:**
```bash
cd /nexuslang-v2
./fix.sh
```

---

### ❌ **Services won't start after restart**
**Cause:** Dependencies not persisted in container

**Solution:** Always run the smart startup script after container restart:
```bash
cd /nexuslang-v2
./start.sh
```

---

## 📊 Monitoring & Management

### Check Service Status
```bash
pm2 status
```

### View Logs
```bash
# All services
pm2 logs

# Specific service
pm2 logs backend
pm2 logs galion-studio
```

### Restart Services
```bash
# All services
pm2 restart all

# Specific service
pm2 restart backend
```

### Test Services
```bash
# Backend
curl http://localhost:8000/health

# Galion Studio
curl http://localhost:3030

# Nginx
curl http://localhost
```

---

## 🌐 Finding Your RunPod Public URL

Your Galion Platform needs to be accessed via RunPod's public domain.

### **Method 1: RunPod Dashboard**
1. Go to [RunPod.io](https://runpod.io) → **My Pods**
2. Click on your running pod
3. Look for **"Connect"** or **"HTTP Ports"** section
4. Copy your public URL (usually looks like `https://xxxxx.runpod.io`)

### **Method 2: Check Exposed Ports**
1. In RunPod dashboard, go to your pod
2. Click **"Edit"** or **"Settings"**
3. Check **"HTTP Ports"** or **"TCP Ports"**
4. Ensure port **80** is exposed
5. The public URL will be shown there

### **Common RunPod URL Formats:**
- `https://[random-id].runpod.io`
- `https://[pod-id]-[port].proxy.runpod.net`
- Custom subdomain if configured

---

## 🎯 Complete Setup Flow

### **First Time Setup:**
```bash
# 1. Clone repository (if not already done)
cd /
git clone https://github.com/galion-studio/nexuslang-v2.git
cd nexuslang-v2
git checkout clean-nexuslang

# 2. Run smart startup
wget -O start.sh https://raw.githubusercontent.com/galion-studio/nexuslang-v2/clean-nexuslang/start-galion-platform.sh && chmod +x start.sh && ./start.sh

# 3. Find your public URL in RunPod dashboard

# 4. Access your platform!
```

### **After Container Restart:**
```bash
cd /nexuslang-v2
./start.sh
```

### **Quick Deploy (Update Code):**
```bash
cd /nexuslang-v2
git pull origin clean-nexuslang
pm2 restart all
```

---

## 📦 What Gets Installed Automatically

### **System Packages:**
- Python 3
- pip3
- Node.js
- npm
- PM2 (globally)
- Nginx
- curl
- git

### **Python Packages:**
- fastapi
- uvicorn
- psutil
- pydantic
- starlette
- typing_extensions
- python-multipart

### **Node.js Packages (per project):**
- next
- react
- react-dom
- react-hot-toast (galion-studio)
- lucide-react
- clsx
- tailwind-merge

---

## 🆘 Need Help?

### **Check Logs:**
```bash
pm2 logs
```

### **Check Nginx:**
```bash
nginx -t
ps aux | grep nginx
```

### **Check Ports:**
```bash
ss -tlnp | grep -E ':(80|8000|3000|3003|3030)'
```

### **Full Reset:**
```bash
cd /nexuslang-v2
./fix.sh
```

---

## 🎉 Success Checklist

After running the startup script, verify:

- [ ] Backend shows "online" in PM2
- [ ] Galion Studio shows "online" in PM2
- [ ] `curl http://localhost:8000/health` returns 200
- [ ] `curl http://localhost:3030` returns HTML
- [ ] `curl http://localhost` returns HTML (via Nginx)
- [ ] Found your RunPod public URL in dashboard
- [ ] Can access platform via public URL

---

## 📞 Support

If you encounter issues:

1. **Run the emergency fix:** `./fix.sh`
2. **Check logs:** `pm2 logs`
3. **Verify dependencies:** `./check-deps.sh`
4. **Check Nginx:** `nginx -t`

---

**🚀 Your Galion Platform is now production-ready on RunPod!**

