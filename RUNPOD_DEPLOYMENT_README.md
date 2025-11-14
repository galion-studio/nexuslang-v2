# 🚀 Project Nexus - RunPod Deployment Guide

Complete guide for deploying the Nexus Lang V2 Scientific Platform on RunPod with Cloudflare integration.

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Prerequisites](#prerequisites)
3. [Deployment Options](#deployment-options)
4. [Step-by-Step Instructions](#step-by-step-instructions)
5. [Troubleshooting](#troubleshooting)
6. [Monitoring & Maintenance](#monitoring--maintenance)
7. [Cloudflare Configuration](#cloudflare-configuration)

---

## 🎯 Quick Start

### Ultra-Fast Deployment (2 Minutes)

1. **Access your RunPod pod** via SSH or Web Terminal

2. **Clone the repository**:
   ```bash
   cd /workspace
   git clone https://github.com/YOUR_USERNAME/project-nexus.git
   cd project-nexus
   ```

3. **Run the auto-fix script**:
   ```bash
   chmod +x runpod-diagnose-and-fix.sh
   ./runpod-diagnose-and-fix.sh
   ```

4. **Get your public IP** (shown at the end of script output)

5. **Configure Cloudflare DNS** with the IP

✅ **Done!** Your server is live at `https://galion.studio`

---

## 📦 Prerequisites

### RunPod Requirements

- **Pod Type**: Any RunPod instance (CPU or GPU)
- **Disk Space**: Minimum 10GB
- **Network**: Port 8080 exposed
- **OS**: Linux (Ubuntu recommended)

### Software Requirements

The scripts will auto-install these, but for reference:

- Python 3.8 or higher
- pip (Python package manager)
- FastAPI
- Uvicorn
- psutil (optional, for system monitoring)

### External Services

- **Cloudflare Account** (for domain management)
- **Domain Name** (e.g., `galion.studio`)

---

## 🛠️ Deployment Options

We provide **THREE** deployment methods, from most automated to most manual:

### Option 1: Automated Diagnostic & Fix (Recommended) ⭐

**Best for**: First-time deployment, troubleshooting

**Script**: `runpod-diagnose-and-fix.sh`

**What it does**:
- ✅ Comprehensive system diagnostics
- ✅ Auto-installs dependencies
- ✅ Kills conflicting processes
- ✅ Tests Python imports
- ✅ Starts the server
- ✅ Verifies everything works
- ✅ Shows your public IP

**Usage**:
```bash
cd /workspace/project-nexus
chmod +x runpod-diagnose-and-fix.sh
./runpod-diagnose-and-fix.sh
```

---

### Option 2: Simplified Server (Most Reliable)

**Best for**: When imports fail, production stability

**Script**: `runpod-start-simple.sh`

**What it does**:
- ✅ Starts simplified server (`main_simple.py`)
- ✅ Minimal dependencies
- ✅ More reliable
- ✅ Full API functionality

**Usage**:
```bash
cd /workspace/project-nexus
chmod +x runpod-start-simple.sh
./runpod-start-simple.sh
```

---

### Option 3: Full-Featured Server

**Best for**: Production with all features enabled

**Script**: `runpod-start-server.sh`

**What it does**:
- ✅ Starts full server (`main.py`)
- ✅ All scientific modules
- ✅ Agent orchestration
- ✅ Advanced features

**Usage**:
```bash
cd /workspace/project-nexus
chmod +x runpod-start-server.sh
./runpod-start-server.sh
```

---

## 📝 Step-by-Step Instructions

### Step 1: Access RunPod

1. Go to [RunPod.io](https://www.runpod.io/)
2. Log in to your account
3. Find your pod
4. Click **"Connect"**
5. Choose **"Start Web Terminal"** or **"Connect via SSH"**

### Step 2: Clone Repository

```bash
cd /workspace
git clone https://github.com/YOUR_USERNAME/project-nexus.git
cd project-nexus
```

### Step 3: Make Scripts Executable

```bash
chmod +x runpod-diagnose-and-fix.sh
chmod +x runpod-start-simple.sh
chmod +x runpod-start-server.sh
```

### Step 4: Run Deployment Script

**Recommended: Use diagnostic script**
```bash
./runpod-diagnose-and-fix.sh
```

This will:
1. Check your environment ✅
2. Install dependencies ✅
3. Stop old processes ✅
4. Start the server ✅
5. Verify it's working ✅
6. Show your public IP ✅

### Step 5: Note Your Public IP

The script will display your public IP at the end:

```
Public IP: 123.45.67.89
```

**Write this down!** You'll need it for Cloudflare.

### Step 6: Configure Cloudflare

1. Go to **Cloudflare Dashboard**
2. Select your domain (`galion.studio`)
3. Go to **DNS** section
4. Add/Update these records:

   **Record 1 (Root domain):**
   - Type: `A`
   - Name: `@`
   - Content: `123.45.67.89` (your RunPod IP)
   - Proxy status: **Proxied** (orange cloud) ✅
   - TTL: Auto

   **Record 2 (WWW subdomain):**
   - Type: `A`
   - Name: `www`
   - Content: `123.45.67.89` (your RunPod IP)
   - Proxy status: **Proxied** (orange cloud) ✅
   - TTL: Auto

5. Go to **SSL/TLS** → **Overview**
6. Set encryption mode to: **"Flexible"**

7. **Wait 1-3 minutes** for DNS propagation

### Step 7: Test Your Deployment

```bash
# Test locally on RunPod
curl http://localhost:8080/health

# Test via public IP
curl http://YOUR_RUNPOD_IP:8080/health

# Test via domain (after Cloudflare setup)
curl https://galion.studio/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-14T19:30:00Z",
  "version": "2.0.0",
  "services": {...}
}
```

---

## 🔧 Troubleshooting

### Problem: Server won't start

**Symptoms**: Script fails, no process running

**Solution**:
```bash
# Check logs for errors
tail -50 /workspace/logs/galion-backend.log

# Try simplified server
./runpod-start-simple.sh

# Install dependencies manually
pip install fastapi uvicorn psutil
```

---

### Problem: Import errors

**Symptoms**: Python module errors in logs

**Solution**:
```bash
# Install all requirements
cd /workspace/project-nexus
pip install -r requirements.txt

# Use simplified server (fewer dependencies)
./runpod-start-simple.sh
```

---

### Problem: Port already in use

**Symptoms**: "Address already in use" error

**Solution**:
```bash
# Kill existing processes
pkill -f uvicorn

# Or kill specific port
fuser -k 8080/tcp

# Restart
./runpod-start-simple.sh
```

---

### Problem: Cloudflare Error 521

**Symptoms**: "Web server is down" error on domain

**Checklist**:

1. ✅ **Server running on RunPod?**
   ```bash
   curl http://localhost:8080/health
   ```

2. ✅ **Port 8080 exposed in RunPod?**
   - Check RunPod pod settings
   - Ensure port 8080 is exposed

3. ✅ **Correct IP in Cloudflare?**
   ```bash
   curl ifconfig.me  # Get current IP
   ```
   - Update DNS if IP changed

4. ✅ **Cloudflare SSL set correctly?**
   - Should be "Flexible" or "Full"

5. ✅ **Waited for DNS propagation?**
   - Wait 2-3 minutes after DNS changes

6. ✅ **Proxy enabled?** (Orange cloud)
   - Must be enabled in Cloudflare DNS

---

### Problem: Server crashes immediately

**Symptoms**: Starts but stops within seconds

**Solution**:
```bash
# View crash logs
tail -100 /workspace/logs/galion-backend.log

# Check for missing dependencies
python -c "import fastapi, uvicorn, psutil"

# Use simplified server
./runpod-start-simple.sh
```

---

## 📊 Monitoring & Maintenance

### View Live Logs

```bash
# Main server logs
tail -f /workspace/logs/galion-backend.log

# Simplified server logs
tail -f /workspace/logs/galion-simple.log

# All logs
tail -f /workspace/logs/*.log
```

### Check Server Status

```bash
# Health check
curl http://localhost:8080/health | python -m json.tool

# System info
curl http://localhost:8080/system-info | python -m json.tool

# Check process
ps aux | grep uvicorn

# Check port
netstat -tulpn | grep 8080
```

### Stop Server

```bash
# Graceful stop (if PID known)
kill $(cat /workspace/logs/server.pid)

# Force stop all uvicorn
pkill -f uvicorn

# Stop specific port
fuser -k 8080/tcp
```

### Restart Server

```bash
# Stop first
pkill -f uvicorn

# Wait a moment
sleep 2

# Start again
cd /workspace/project-nexus
./runpod-start-simple.sh
```

---

## ☁️ Cloudflare Configuration

### DNS Setup

**Required Records:**

| Type | Name | Content | Proxy | TTL |
|------|------|---------|-------|-----|
| A | @ | YOUR_RUNPOD_IP | ✅ Proxied | Auto |
| A | www | YOUR_RUNPOD_IP | ✅ Proxied | Auto |

### SSL/TLS Settings

1. Go to **SSL/TLS** → **Overview**
2. Select: **"Flexible"**
3. Enable: **Always Use HTTPS** (SSL/TLS → Edge Certificates)
4. Enable: **Automatic HTTPS Rewrites**

### Performance Optimization (Optional)

1. **Caching**:
   - Go to **Caching** → **Configuration**
   - Caching Level: **Standard**
   - Browser Cache TTL: **4 hours**

2. **Speed**:
   - Go to **Speed** → **Optimization**
   - Enable **Auto Minify** (JavaScript, CSS, HTML)
   - Enable **Brotli**

3. **Firewall** (Optional):
   - Go to **Security** → **WAF**
   - Enable **Managed Rules**
   - Set to **Medium** security level

---

## 🧪 Testing Your Deployment

### Local Tests (on RunPod)

```bash
# Health check
curl http://localhost:8080/health

# Root endpoint
curl http://localhost:8080/

# API docs
curl http://localhost:8080/docs

# Scientific capabilities
curl http://localhost:8080/api/v1/scientific-capabilities
```

### Public IP Tests

```bash
# Get your IP
MY_IP=$(curl -s ifconfig.me)

# Health check
curl http://$MY_IP:8080/health

# Root
curl http://$MY_IP:8080/
```

### Domain Tests (after Cloudflare)

```bash
# Health check
curl https://galion.studio/health

# Root
curl https://galion.studio/

# In browser
open https://galion.studio/docs
```

---

## 📚 API Endpoints

Once deployed, your API will have these endpoints:

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check |
| `/system-info` | GET | System information |
| `/docs` | GET | API documentation (Swagger UI) |
| `/redoc` | GET | API documentation (ReDoc) |

### API v1 Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/test` | GET | Test endpoint |
| `/api/v1/query` | POST | Submit a query |
| `/api/v1/scientific-capabilities` | GET | Get capabilities |

---

## 🔐 Security Considerations

### Production Checklist

- [ ] Change default ports if needed
- [ ] Set up firewall rules
- [ ] Enable HTTPS only
- [ ] Configure rate limiting
- [ ] Set up monitoring/alerts
- [ ] Regular backups
- [ ] Update dependencies regularly
- [ ] Use environment variables for secrets
- [ ] Enable Cloudflare security features
- [ ] Set up logging and monitoring

### Environment Variables

Create a `.env` file (NOT committed to git):

```bash
# Server Configuration
PORT=8080
HOST=0.0.0.0
WORKERS=2

# Security
SECRET_KEY=your-secret-key-here
DEBUG=false

# Database (if used)
DATABASE_URL=postgresql://user:pass@host:port/db

# API Keys (if needed)
OPENAI_API_KEY=your-key-here
```

---

## 🆘 Getting Help

### Run Full Diagnostic

```bash
cd /workspace/project-nexus
./runpod-diagnose-and-fix.sh
```

This will show you everything that's working or broken.

### Common Commands

```bash
# View logs
tail -f /workspace/logs/galion-backend.log

# Check process
ps aux | grep uvicorn

# Check port
lsof -i :8080

# Test health
curl http://localhost:8080/health

# Get IP
curl ifconfig.me

# Restart everything
pkill -f uvicorn && sleep 2 && ./runpod-start-simple.sh
```

---

## 📖 Additional Resources

- **Main Documentation**: See `RUNPOD_WEB_SERVER_FIX.md` for detailed troubleshooting
- **Quick Start**: See `RUNPOD_QUICK_START.md` for quick reference
- **API Reference**: Visit `/docs` on your deployed server

---

## 🎉 Success Checklist

Your deployment is successful when:

- [x] Server process is running: `ps aux | grep uvicorn`
- [x] Health check works: `curl http://localhost:8080/health`
- [x] Public IP works: `curl http://YOUR_IP:8080/health`
- [x] Domain resolves: `curl https://galion.studio/health`
- [x] API docs accessible: `https://galion.studio/docs`
- [x] No errors in logs: `tail /workspace/logs/galion-backend.log`

---

## 📞 Support

If you encounter issues:

1. Run the diagnostic script
2. Check the logs
3. Review troubleshooting section
4. Check GitHub issues

---

**Made with ❤️ by Project Nexus Team**

Last updated: November 14, 2025
