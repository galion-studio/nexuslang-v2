# ⚡ Galion Studio RunPod - Quick Start (Fix 521 Error)

## 🎯 The Problem
Your website **galion.studio** shows **Cloudflare Error 521** because the backend server on RunPod isn't running.

## ✅ The Solution (3 Steps - 5 Minutes)

### Step 1: Access Your RunPod Pod

1. Go to [RunPod.io](https://www.runpod.io/)
2. Log in to your account
3. Find your pod and click **"Connect"**
4. Choose **"Start Web Terminal"** or **"Connect via SSH"**

### Step 2: Upload and Run Startup Script

**Option A: Copy-Paste Commands** (Easiest)

In your RunPod terminal, paste this:

```bash
cd /workspace/project-nexus
export PYTHONPATH=/workspace/project-nexus:/workspace/project-nexus/v2
export PORT=8080
pkill -f "uvicorn.*8080" || true
mkdir -p /workspace/logs
cd v2/backend
nohup python -m uvicorn main:app --host 0.0.0.0 --port 8080 --workers 2 > /workspace/logs/galion-backend.log 2>&1 &
sleep 3
curl http://localhost:8080/health
```

**Option B: Upload Script Files** (Better for production)

1. Download these files from your project:
   - `runpod-start-server.sh`
   - `runpod-stop-server.sh`

2. Upload to RunPod (using RunPod web interface or SCP)

3. Run in RunPod terminal:
```bash
cd /workspace/project-nexus
chmod +x runpod-start-server.sh
./runpod-start-server.sh
```

### Step 3: Configure Cloudflare

After the server starts, you'll see your **RunPod Public IP** (e.g., `123.45.67.89`)

1. Go to **Cloudflare Dashboard**
2. Select **galion.studio** domain
3. Go to **DNS** section
4. Add/Update these records:

```
Type: A
Name: @
Content: YOUR_RUNPOD_IP
Proxy: ✅ ON (orange cloud)
```

```
Type: A
Name: www
Content: YOUR_RUNPOD_IP
Proxy: ✅ ON (orange cloud)
```

5. Go to **SSL/TLS** → **Overview**
6. Set encryption mode to: **Flexible** or **Full**

7. **Wait 2-3 minutes** for DNS propagation

8. **Test your website**: https://galion.studio/health

---

## ✅ Verification

### Check if Server is Running

```bash
# On RunPod terminal:
curl http://localhost:8080/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-14T19:30:00Z",
  "services": {...},
  "version": "2.0.0"
}
```

### Check from Outside

```bash
# On your local machine:
curl http://YOUR_RUNPOD_IP:8080/health
```

### Check via Domain

```bash
# After Cloudflare setup:
curl https://galion.studio/health
```

---

## 🔧 Common Issues

### Issue: "Connection refused"

**Solution**: Server not running. Start it:
```bash
cd /workspace/project-nexus
./runpod-start-server.sh
```

### Issue: "Import errors"

**Solution**: Install dependencies:
```bash
cd /workspace/project-nexus
pip install -r requirements.txt
```

### Issue: "Port 8080 already in use"

**Solution**: Kill existing process:
```bash
pkill -f "uvicorn.*8080"
./runpod-start-server.sh
```

### Issue: Still getting 521 error

**Checklist**:
1. ✅ Server running on RunPod: `curl http://localhost:8080/health`
2. ✅ RunPod port 8080 exposed in pod settings
3. ✅ Cloudflare DNS points to correct IP
4. ✅ Cloudflare SSL set to "Flexible" or "Full"
5. ✅ Waited 2-3 minutes for DNS propagation

**Debug Steps**:
```bash
# 1. Check server process
ps aux | grep uvicorn

# 2. Check server logs
tail -f /workspace/logs/galion-backend.log

# 3. Test direct IP (replace with your IP)
curl http://YOUR_RUNPOD_IP:8080/health

# 4. Temporarily disable Cloudflare proxy
#    In Cloudflare DNS, click the orange cloud to turn it gray
#    Then test: http://galion.studio:8080/health
```

---

## 🚀 Production Setup (Optional)

For a more robust setup that survives pod restarts:

### 1. Create Startup Script in RunPod

```bash
cat > /workspace/start-on-boot.sh << 'EOF'
#!/bin/bash
cd /workspace/project-nexus
export PYTHONPATH=/workspace/project-nexus:/workspace/project-nexus/v2
cd v2/backend
python -m uvicorn main:app --host 0.0.0.0 --port 8080 --workers 2
EOF

chmod +x /workspace/start-on-boot.sh
```

### 2. Test the Script

```bash
/workspace/start-on-boot.sh
```

### 3. Set as RunPod Startup Command

In RunPod pod settings, add startup command:
```bash
/workspace/start-on-boot.sh
```

---

## 📊 Monitoring

### View Live Logs

```bash
tail -f /workspace/logs/galion-backend.log
```

### Check Server Status

```bash
curl http://localhost:8080/health | jq .
```

### Check System Resources

```bash
# CPU and Memory
htop

# Disk space
df -h
```

---

## 🎯 Next Steps

Once your server is running:

1. ✅ Test all API endpoints: https://galion.studio/docs
2. ✅ Set up monitoring (logs, uptime checks)
3. ✅ Configure environment variables
4. ✅ Set up automatic backups
5. ✅ Add health check monitoring service

---

## 🆘 Need Help?

### Get Your Current Status

Run this diagnostic script:

```bash
cat > /tmp/diagnose.sh << 'EOF'
#!/bin/bash
echo "🔍 Galion Studio Server Diagnostic"
echo "=================================="
echo ""
echo "1. Server Process:"
ps aux | grep uvicorn | grep -v grep
echo ""
echo "2. Port 8080 Status:"
netstat -tulpn | grep 8080 || echo "  Port not in use"
echo ""
echo "3. Health Check:"
curl -s http://localhost:8080/health | head -20 || echo "  Failed"
echo ""
echo "4. Public IP:"
curl -s ifconfig.me
echo ""
echo "5. Recent Logs:"
tail -20 /workspace/logs/galion-backend.log 2>/dev/null || echo "  No logs found"
EOF

chmod +x /tmp/diagnose.sh
/tmp/diagnose.sh
```

Share the output if you need help debugging!

---

## 📝 Summary

**Quick Fix Command** (run in RunPod terminal):

```bash
cd /workspace/project-nexus && \
export PYTHONPATH=/workspace/project-nexus:/workspace/project-nexus/v2 && \
pkill -f uvicorn || true && \
mkdir -p /workspace/logs && \
cd v2/backend && \
nohup python -m uvicorn main:app --host 0.0.0.0 --port 8080 --workers 2 > /workspace/logs/galion-backend.log 2>&1 & \
sleep 3 && \
curl http://localhost:8080/health && \
curl -s ifconfig.me && \
echo " <- Configure this IP in Cloudflare DNS"
```

This will:
1. ✅ Kill any old server processes
2. ✅ Start server on port 8080
3. ✅ Show your public IP
4. ✅ Test health endpoint

Then configure Cloudflare with the IP shown!

---

🎉 **Your galion.studio will be live in 5 minutes!**

