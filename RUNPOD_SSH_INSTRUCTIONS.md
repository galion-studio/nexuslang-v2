# 🚀 RunPod SSH Deployment Instructions

**How to deploy your server on RunPod using the scripts from GitHub**

---

## ✅ What Was Just Pushed to GitHub

The following files are now available in your GitHub repository:

1. **`runpod-diagnose-and-fix.sh`** - Automated diagnostic and deployment script
2. **`runpod-start-simple.sh`** - Simplified server startup
3. **`v2/backend/main_simple.py`** - Lightweight, reliable server
4. **`RUNPOD_DEPLOYMENT_README.md`** - Complete deployment guide
5. **`RUNPOD_WEB_SERVER_FIX.md`** - Troubleshooting guide
6. **`RUNPOD_QUICK_REFERENCE.md`** - Quick reference card
7. **`.gitignore`** - Protects secrets and temp files

---

## 📍 Your GitHub Repository

**Repository**: `https://github.com/galion-studio/nexuslang-v2.git`  
**Branch**: `clean-nexuslang`

---

## 🎯 Step-by-Step: Deploy via RunPod SSH

### Step 1: Access RunPod

1. Go to **[RunPod.io](https://www.runpod.io/)**
2. Log in to your account
3. Find your pod (or create a new one)
4. Click **"Connect"**
5. Choose **"Start Web Terminal"** or **"Connect via SSH"**

---

### Step 2: Clone Repository from GitHub

In your RunPod terminal, run:

```bash
# Navigate to workspace
cd /workspace

# Clone the repository
git clone https://github.com/galion-studio/nexuslang-v2.git project-nexus

# Navigate into the project
cd project-nexus

# Switch to the correct branch
git checkout clean-nexuslang
```

**Output should show**:
```
Cloning into 'project-nexus'...
remote: Enumerating objects...
Receiving objects: 100% done
```

---

### Step 3: Run the Automated Deployment Script

This is the **EASIEST** method - the script does everything automatically:

```bash
# Make the script executable
chmod +x runpod-diagnose-and-fix.sh

# Run the diagnostic and deployment script
./runpod-diagnose-and-fix.sh
```

**What this does**:
- ✅ Checks your environment
- ✅ Installs all dependencies
- ✅ Kills any old server processes
- ✅ Tests Python imports
- ✅ Starts the web server
- ✅ Verifies it's working
- ✅ Shows your public IP

**Expected Output** (last few lines):
```
============================================================================
✅ Galion Studio Backend Server Started Successfully!
============================================================================

📍 Server Access Points:
  - Local:     http://localhost:8080
  - Public IP: http://123.45.67.89:8080
  - Domain:    https://galion.studio (after Cloudflare config)

☁️  Cloudflare Configuration:
  1. Go to Cloudflare Dashboard → galion.studio → DNS
  2. Add A record: @ → 123.45.67.89 (Proxy ON)
  3. SSL/TLS → Set to 'Flexible' or 'Full'
  4. Wait 1-2 minutes for DNS propagation
  5. Test: https://galion.studio/health
```

**✨ NOTE YOUR PUBLIC IP!** You'll need it for Cloudflare.

---

### Step 4: Verify Server is Running

Test locally on RunPod:

```bash
curl http://localhost:8080/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-14T20:00:00Z",
  "version": "2.0.0",
  "services": {
    "core_api": "available",
    "psutil": "available"
  }
}
```

---

### Step 5: Configure Cloudflare

1. **Open Cloudflare Dashboard**: https://dash.cloudflare.com
2. **Select your domain**: `galion.studio`
3. **Go to DNS section**
4. **Add/Update DNS Records**:

   **Root Domain Record**:
   - Type: `A`
   - Name: `@`
   - IPv4 address: `123.45.67.89` ← (your RunPod IP)
   - Proxy status: **Proxied** (🟠 orange cloud)
   - TTL: Auto

   **WWW Subdomain Record**:
   - Type: `A`
   - Name: `www`
   - IPv4 address: `123.45.67.89` ← (your RunPod IP)
   - Proxy status: **Proxied** (🟠 orange cloud)
   - TTL: Auto

5. **Configure SSL**:
   - Go to **SSL/TLS** → **Overview**
   - Set encryption mode to: **"Flexible"**

6. **Wait 1-3 minutes** for DNS to propagate

---

### Step 6: Test Your Website

```bash
# Test via domain
curl https://galion.studio/health

# Open in browser (if you have one)
# Visit: https://galion.studio
```

**Expected**: You should see your website live!

---

## 🔄 Alternative Deployment Methods

### Method 1: Quick One-Liner (Ultra Fast)

If you just want to start immediately without diagnostics:

```bash
cd /workspace && \
git clone https://github.com/galion-studio/nexuslang-v2.git project-nexus && \
cd project-nexus && \
git checkout clean-nexuslang && \
chmod +x runpod-start-simple.sh && \
./runpod-start-simple.sh
```

This will:
- Clone the repo
- Start the simplified server
- Show you the public IP

---

### Method 2: Manual Clone + Simple Server

For more control:

```bash
# 1. Clone
cd /workspace
git clone https://github.com/galion-studio/nexuslang-v2.git project-nexus
cd project-nexus
git checkout clean-nexuslang

# 2. Make scripts executable
chmod +x runpod-start-simple.sh

# 3. Start simple server
./runpod-start-simple.sh
```

---

### Method 3: Full-Featured Server

For all advanced features:

```bash
cd /workspace/project-nexus
chmod +x runpod-start-server.sh
./runpod-start-server.sh
```

---

## 🔍 Verification Checklist

After deployment, verify:

- [ ] Repository cloned successfully
- [ ] Scripts are executable (`chmod +x` worked)
- [ ] Server started (see process with `ps aux | grep uvicorn`)
- [ ] Health check works locally (`curl http://localhost:8080/health`)
- [ ] Public IP obtained (`curl ifconfig.me`)
- [ ] Cloudflare DNS configured with correct IP
- [ ] Domain works (`curl https://galion.studio/health`)

---

## 🛑 Common Issues & Solutions

### Issue: "Permission denied" when running script

**Solution**:
```bash
chmod +x runpod-diagnose-and-fix.sh
./runpod-diagnose-and-fix.sh
```

---

### Issue: "fatal: destination path 'project-nexus' already exists"

**Solution** (Repository already cloned):
```bash
cd /workspace/project-nexus
git pull origin clean-nexuslang
chmod +x runpod-diagnose-and-fix.sh
./runpod-diagnose-and-fix.sh
```

---

### Issue: "Port 8080 already in use"

**Solution**:
```bash
pkill -f uvicorn
sleep 2
./runpod-start-simple.sh
```

---

### Issue: Import errors or missing modules

**Solution**:
```bash
cd /workspace/project-nexus
pip install -r requirements.txt
./runpod-start-simple.sh
```

---

### Issue: Script runs but server doesn't start

**Check logs**:
```bash
tail -50 /workspace/logs/galion-backend.log
```

**Try simplified server**:
```bash
./runpod-start-simple.sh
```

---

## 📊 Monitoring Your Server

### View Live Logs

```bash
tail -f /workspace/logs/galion-backend.log
```

Press `Ctrl+C` to stop viewing.

### Check Server Status

```bash
# Health check
curl http://localhost:8080/health

# System info
curl http://localhost:8080/system-info

# Check process
ps aux | grep uvicorn
```

### Get Public IP

```bash
curl ifconfig.me
```

---

## 🔄 Updating Your Deployment

When you push new changes to GitHub:

```bash
cd /workspace/project-nexus

# Stop current server
pkill -f uvicorn

# Pull latest changes
git pull origin clean-nexuslang

# Restart server
./runpod-start-simple.sh
```

---

## 🛑 Stopping the Server

```bash
# Kill all uvicorn processes
pkill -f uvicorn

# Or kill by PID
kill $(cat /workspace/logs/server.pid)
```

---

## 📚 Documentation Available

Once deployed, these files are available in your repository:

1. **RUNPOD_DEPLOYMENT_README.md** - Full deployment guide
2. **RUNPOD_WEB_SERVER_FIX.md** - Comprehensive troubleshooting
3. **RUNPOD_QUICK_REFERENCE.md** - Quick command reference

View them on GitHub or read them on RunPod:

```bash
cd /workspace/project-nexus
cat RUNPOD_QUICK_REFERENCE.md
```

---

## 🆘 Need Help?

### Run Full Diagnostic

```bash
cd /workspace/project-nexus
./runpod-diagnose-and-fix.sh
```

This will show you:
- ✅ What's working
- ❌ What's broken
- 🔧 Automatic fixes applied

### Get Support Information

```bash
cat > /tmp/support-info.sh << 'EOF'
#!/bin/bash
echo "=== SUPPORT INFORMATION ==="
echo "Git Status:"
cd /workspace/project-nexus && git status
echo ""
echo "Server Process:"
ps aux | grep uvicorn | grep -v grep
echo ""
echo "Health Check:"
curl -s http://localhost:8080/health
echo ""
echo "Public IP:"
curl -s ifconfig.me
echo ""
echo "Recent Logs:"
tail -30 /workspace/logs/galion-backend.log
EOF

chmod +x /tmp/support-info.sh
/tmp/support-info.sh
```

Share this output if you need help!

---

## ✅ Success!

Your server is successfully deployed when:

1. ✅ `curl http://localhost:8080/health` returns `{"status":"healthy"}`
2. ✅ Server process visible: `ps aux | grep uvicorn`
3. ✅ Public IP accessible: `curl http://YOUR_IP:8080/health`
4. ✅ Domain works: `https://galion.studio/health`
5. ✅ API docs accessible: `https://galion.studio/docs`

---

## 🎉 You're Live!

**Your server is now running on RunPod and accessible via your domain!**

**Next Steps**:
- Test all API endpoints
- Set up monitoring
- Configure backups
- Review security settings

**API Documentation**: https://galion.studio/docs

---

**Last Updated**: November 14, 2025  
**Repository**: https://github.com/galion-studio/nexuslang-v2  
**Branch**: clean-nexuslang

