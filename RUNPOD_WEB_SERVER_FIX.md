# 🔧 RunPod Web Server Issue - Complete Fix Guide

## 📋 Problem Overview

Your web server on RunPod isn't working properly. This could be due to:

1. **Import errors** - Complex dependencies failing to load
2. **Port issues** - Server not binding to the correct port
3. **Process management** - Old processes blocking the port
4. **Missing dependencies** - Python packages not installed
5. **Cloudflare configuration** - DNS not pointing to correct IP

## ✅ Solution: Three Options

### 🚀 **Option 1: Use Diagnostic Script (Recommended)**

This script will automatically diagnose and fix most issues.

**Steps:**

1. **Upload to RunPod**: Upload `runpod-diagnose-and-fix.sh` to your RunPod pod
   
2. **Run in RunPod terminal**:
   ```bash
   cd /workspace/project-nexus
   chmod +x runpod-diagnose-and-fix.sh
   ./runpod-diagnose-and-fix.sh
   ```

3. **Review output**: The script will show you:
   - ✅ What's working
   - ❌ What's broken
   - 🔧 What it fixed
   - 📍 Your public IP for Cloudflare

4. **Configure Cloudflare** with the IP shown at the end

**What This Does:**
- ✅ Checks your environment
- ✅ Kills old server processes
- ✅ Installs missing dependencies
- ✅ Tests Python imports
- ✅ Starts the server
- ✅ Verifies it's working
- ✅ Shows you your public IP

---

### 🎯 **Option 2: Use Simplified Server (Most Reliable)**

If Option 1 doesn't work, use the simplified server that has fewer dependencies.

**Steps:**

1. **Run this command in RunPod**:
   ```bash
   cd /workspace/project-nexus
   chmod +x runpod-start-simple.sh
   ./runpod-start-simple.sh
   ```

2. **That's it!** The server will start using `main_simple.py` which is more reliable.

**What This Does:**
- ✅ Uses simplified server with minimal dependencies
- ✅ More reliable startup
- ✅ Still provides full API access
- ✅ Works even if some modules are missing

---

### ⚡ **Option 3: Quick One-Liner (Fastest)**

If you just want to start the server NOW with no diagnosis:

```bash
cd /workspace/project-nexus && \
export PYTHONPATH=/workspace/project-nexus:/workspace/project-nexus/v2 && \
export PORT=8080 && \
pkill -f uvicorn || true && \
mkdir -p /workspace/logs && \
pip install -q fastapi uvicorn psutil && \
cd v2/backend && \
nohup python -m uvicorn main_simple:app --host 0.0.0.0 --port 8080 --workers 2 > /workspace/logs/server.log 2>&1 & \
sleep 3 && \
curl http://localhost:8080/health && \
curl -s ifconfig.me && echo " <- Configure this IP in Cloudflare"
```

**What This Does:**
- Immediately starts the server
- Shows health check result
- Shows your public IP

---

## 🔍 Troubleshooting Common Issues

### Issue: "Connection refused" or "Cannot connect"

**Cause**: Server not running or not listening on correct port

**Fix**:
```bash
# Check if server is running
ps aux | grep uvicorn

# Check what's on port 8080
lsof -i :8080

# Start server
cd /workspace/project-nexus
./runpod-start-simple.sh
```

---

### Issue: "Import Error" or "Module not found"

**Cause**: Missing Python dependencies

**Fix**:
```bash
cd /workspace/project-nexus
pip install -r requirements.txt

# Or install just the essentials
pip install fastapi uvicorn psutil
```

---

### Issue: "Port 8080 already in use"

**Cause**: Old server process still running

**Fix**:
```bash
# Kill all uvicorn processes
pkill -f uvicorn

# Or kill specific port
fuser -k 8080/tcp

# Then restart server
./runpod-start-simple.sh
```

---

### Issue: "Cloudflare Error 521 - Web server is down"

**Cause**: Cloudflare can't reach your RunPod server

**Fix - Step by step**:

1. **Verify server is running on RunPod**:
   ```bash
   curl http://localhost:8080/health
   ```
   Should return: `{"status":"healthy",...}`

2. **Get your public IP**:
   ```bash
   curl ifconfig.me
   ```

3. **Test from outside**:
   ```bash
   curl http://YOUR_RUNPOD_IP:8080/health
   ```

4. **Configure Cloudflare**:
   - Go to Cloudflare Dashboard
   - Select `galion.studio` domain
   - DNS → Add/Update records:
     - Type: `A`, Name: `@`, Content: `YOUR_RUNPOD_IP`, Proxy: **ON** ✅
     - Type: `A`, Name: `www`, Content: `YOUR_RUNPOD_IP`, Proxy: **ON** ✅
   - SSL/TLS → Set to **"Flexible"**
   - Wait 2-3 minutes

5. **Test**:
   ```bash
   curl https://galion.studio/health
   ```

---

### Issue: Server starts but immediately crashes

**Cause**: Import errors or missing dependencies

**Fix**:
```bash
# View logs to see the error
tail -50 /workspace/logs/galion-backend.log

# Or for simple server:
tail -50 /workspace/logs/galion-simple.log

# Usually fixed by:
pip install fastapi uvicorn psutil pydantic
```

---

## 📊 Monitoring Your Server

### View Live Logs
```bash
tail -f /workspace/logs/galion-backend.log

# Or for simple server:
tail -f /workspace/logs/galion-simple.log
```

### Check Server Health
```bash
curl http://localhost:8080/health | python -m json.tool
```

### Check Server Process
```bash
# See if server is running
ps aux | grep uvicorn

# See what's on port 8080
netstat -tulpn | grep 8080
```

### Stop Server
```bash
# Find process ID
ps aux | grep uvicorn

# Kill by PID (replace 12345 with actual PID)
kill 12345

# Or kill all uvicorn
pkill -f uvicorn
```

---

## 🎯 Testing Checklist

After starting your server, verify these:

- [ ] Server process is running: `ps aux | grep uvicorn`
- [ ] Health check works locally: `curl http://localhost:8080/health`
- [ ] Root endpoint works: `curl http://localhost:8080/`
- [ ] API docs accessible: `curl http://localhost:8080/docs`
- [ ] Health check works from public IP: `curl http://YOUR_IP:8080/health`
- [ ] Cloudflare DNS configured with correct IP
- [ ] Website works: `curl https://galion.studio/health`

---

## 🆘 Still Having Issues?

Run this diagnostic command and share the output:

```bash
cat > /tmp/full-diagnostic.sh << 'EOF'
#!/bin/bash
echo "=== FULL DIAGNOSTIC REPORT ==="
echo ""
echo "1. Environment:"
pwd
whoami
python --version
pip --version
echo ""
echo "2. Processes:"
ps aux | grep uvicorn | grep -v grep
echo ""
echo "3. Port Status:"
lsof -i :8080 || echo "Port 8080 not in use"
netstat -tulpn | grep 8080 || echo "Port 8080 not listening"
echo ""
echo "4. Health Check:"
curl -s http://localhost:8080/health || echo "Health check failed"
echo ""
echo "5. Public IP:"
curl -s ifconfig.me
echo ""
echo "6. Recent Logs:"
tail -30 /workspace/logs/galion-backend.log 2>/dev/null || \
tail -30 /workspace/logs/galion-simple.log 2>/dev/null || \
echo "No logs found"
echo ""
echo "7. Python Packages:"
pip list | grep -E "fastapi|uvicorn|psutil"
echo ""
echo "8. Directory Structure:"
ls -la /workspace/project-nexus/v2/backend/ | head -20
EOF

chmod +x /tmp/full-diagnostic.sh
/tmp/full-diagnostic.sh
```

---

## 📝 Quick Reference

| Command | Purpose |
|---------|---------|
| `./runpod-diagnose-and-fix.sh` | Full diagnostic and auto-fix |
| `./runpod-start-simple.sh` | Start simplified server |
| `./runpod-start-server.sh` | Start full-featured server |
| `tail -f /workspace/logs/*.log` | View live logs |
| `curl localhost:8080/health` | Test server health |
| `pkill -f uvicorn` | Stop server |
| `curl ifconfig.me` | Get public IP |

---

## 🎉 Success Indicators

You'll know everything is working when:

1. ✅ `curl http://localhost:8080/health` returns `{"status":"healthy"}`
2. ✅ Server logs show no errors
3. ✅ Public IP health check works
4. ✅ https://galion.studio/health returns data (after Cloudflare setup)
5. ✅ https://galion.studio/docs shows API documentation

---

## 📚 File Reference

**Diagnostic & Startup Scripts:**
- `runpod-diagnose-and-fix.sh` - Full diagnostic and auto-fix
- `runpod-start-simple.sh` - Simple server startup
- `runpod-start-server.sh` - Full server startup

**Server Files:**
- `v2/backend/main.py` - Full-featured server
- `v2/backend/main_simple.py` - Simplified, reliable server
- `v2/backend/api/grokopedia.py` - Scientific API router

**Configuration:**
- `requirements.txt` - Python dependencies
- `config/production.env.template` - Environment variables template

---

**Need help?** Share the output from the diagnostic command above!

