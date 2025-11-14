# 🚀 RunPod Quick Reference Card

**One-page reference for deploying and managing your server on RunPod**

---

## ⚡ Quick Deploy (Copy-Paste)

```bash
# 1. Clone repo
cd /workspace && \
git clone https://github.com/YOUR_USERNAME/project-nexus.git && \
cd project-nexus

# 2. Run auto-deploy
chmod +x runpod-diagnose-and-fix.sh && \
./runpod-diagnose-and-fix.sh
```

**Note your public IP from output!**

---

## 🔄 Alternative: Simple Server

```bash
cd /workspace/project-nexus && \
chmod +x runpod-start-simple.sh && \
./runpod-start-simple.sh
```

---

## 🔍 Check Status

```bash
# Health check
curl http://localhost:8080/health

# View logs
tail -f /workspace/logs/galion-backend.log

# Check process
ps aux | grep uvicorn

# Get public IP
curl ifconfig.me
```

---

## 🛑 Stop Server

```bash
# Stop all uvicorn processes
pkill -f uvicorn

# Or kill by PID
kill $(cat /workspace/logs/server.pid)
```

---

## ▶️ Start Server

```bash
cd /workspace/project-nexus
./runpod-start-simple.sh
```

---

## 🔄 Restart Server

```bash
pkill -f uvicorn && sleep 2 && \
cd /workspace/project-nexus && \
./runpod-start-simple.sh
```

---

## ☁️ Cloudflare DNS Setup

1. Get RunPod IP: `curl ifconfig.me`
2. Go to Cloudflare Dashboard
3. Select domain → DNS
4. Add records:
   - Type: `A`, Name: `@`, Content: `YOUR_IP`, Proxy: **ON**
   - Type: `A`, Name: `www`, Content: `YOUR_IP`, Proxy: **ON**
5. SSL/TLS → Set to **"Flexible"**
6. Wait 2 minutes

---

## 🧪 Test Endpoints

```bash
# Local
curl http://localhost:8080/health

# Public IP
curl http://YOUR_IP:8080/health

# Domain (after Cloudflare)
curl https://galion.studio/health

# API docs
open https://galion.studio/docs
```

---

## 🚨 Common Problems & Fixes

### Port in use
```bash
pkill -f uvicorn
./runpod-start-simple.sh
```

### Import errors
```bash
pip install fastapi uvicorn psutil
./runpod-start-simple.sh
```

### Server crashed
```bash
tail -50 /workspace/logs/galion-backend.log
./runpod-start-simple.sh
```

### Cloudflare 521
```bash
# Check server is running
curl http://localhost:8080/health

# Verify IP in Cloudflare matches
curl ifconfig.me
```

---

## 📊 Monitoring

```bash
# Live logs
tail -f /workspace/logs/galion-backend.log

# Health check (JSON formatted)
curl http://localhost:8080/health | python -m json.tool

# System resources
top
htop
df -h
```

---

## 🔧 Troubleshooting

```bash
# Full diagnostic
cd /workspace/project-nexus
./runpod-diagnose-and-fix.sh

# Manual check
cd /workspace/project-nexus/v2/backend
export PYTHONPATH=/workspace/project-nexus:/workspace/project-nexus/v2
python -c "from main_simple import app; print('OK')"
```

---

## 📁 Important Files

| File | Purpose |
|------|---------|
| `runpod-diagnose-and-fix.sh` | Auto-diagnose & fix |
| `runpod-start-simple.sh` | Start simplified server |
| `runpod-start-server.sh` | Start full server |
| `v2/backend/main_simple.py` | Simplified server |
| `v2/backend/main.py` | Full-featured server |
| `/workspace/logs/galion-backend.log` | Server logs |

---

## 🎯 Success Indicators

✅ Health check returns `{"status":"healthy"}`  
✅ Process visible in `ps aux | grep uvicorn`  
✅ Port 8080 listening: `netstat -tulpn | grep 8080`  
✅ Public IP accessible  
✅ Domain works after Cloudflare setup  
✅ No errors in logs  

---

## 📞 Need Help?

1. Run diagnostic: `./runpod-diagnose-and-fix.sh`
2. Check logs: `tail -50 /workspace/logs/galion-backend.log`
3. See full guide: `RUNPOD_DEPLOYMENT_README.md`
4. See troubleshooting: `RUNPOD_WEB_SERVER_FIX.md`

---

**Last Updated**: November 14, 2025

