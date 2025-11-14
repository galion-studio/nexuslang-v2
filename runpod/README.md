# ☁️ RunPod Deployment Guide

**Complete guide for deploying Project Nexus on RunPod GPU cloud platform**

---

## 📋 Table of Contents

- [Overview](#overview)
- [Why RunPod](#why-runpod)
- [Prerequisites](#prerequisites)
- [Quick Deployment](#quick-deployment)
- [Detailed Setup](#detailed-setup)
- [Configuration](#configuration)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)
- [Cost Optimization](#cost-optimization)

---

## 🎯 Overview

This directory contains everything you need to deploy Project Nexus on RunPod, a GPU-accelerated cloud platform perfect for AI workloads.

### What's Included

- ✅ Automated deployment scripts
- ✅ Diagnostic tools
- ✅ Configuration templates
- ✅ Health monitoring
- ✅ Cloudflare integration guide

---

## 💡 Why RunPod

### Advantages

- **🚀 GPU Acceleration** - Perfect for AI/ML workloads
- **💰 Cost-Effective** - Pay per second, no commitment
- **⚡ Fast Deployment** - Spin up in minutes
- **🔧 Flexible** - Full root access
- **🌍 Global** - Multiple datacenter locations
- **📊 Simple** - Easy-to-use interface

### Use Cases

- AI model inference
- Real-time voice processing
- Large-scale research queries
- Development and testing
- Production workloads

---

## 📦 Prerequisites

### RunPod Account

1. Sign up at [RunPod.io](https://www.runpod.io/)
2. Add payment method
3. Create a pod (any template)

### Local Requirements

- Git installed
- SSH client
- Web browser for Cloudflare

---

## ⚡ Quick Deployment

### One-Command Deployment

Connect to your RunPod pod via SSH, then run:

```bash
cd /workspace && \
git clone https://github.com/galion-studio/nexuslang-v2.git project-nexus && \
cd project-nexus && \
git checkout clean-nexuslang && \
chmod +x runpod-diagnose-and-fix.sh && \
./runpod-diagnose-and-fix.sh
```

**That's it!** The script will:
1. ✅ Check your environment
2. ✅ Install dependencies
3. ✅ Configure the system
4. ✅ Start the server
5. ✅ Show your public IP

---

## 📖 Detailed Setup

### Step 1: Create RunPod Pod

1. **Log in** to [RunPod](https://www.runpod.io/)

2. **Click "Deploy"** → "GPU Instance"

3. **Select GPU**:
   - For AI workloads: RTX 3090, A4000, or better
   - For basic API: Any GPU or even CPU pod

4. **Select Template**:
   - RunPod PyTorch (recommended)
   - Or any Ubuntu-based template

5. **Configure**:
   - Disk Space: Minimum 50GB (recommended: 100GB)
   - Expose TCP Ports: **8080**
   - Volume: Optional (for persistent data)

6. **Deploy** and wait for pod to start

### Step 2: Access Pod

**Via Web Terminal**:
1. Click "Connect" → "Start Web Terminal"
2. Terminal opens in browser

**Via SSH** (recommended):
1. Click "Connect" → "TCP Port Mappings"
2. Find SSH port (usually 22)
3. Connect:
   ```bash
   ssh root@XXX.XXX.XXX.XXX -p PORT
   ```

### Step 3: Clone Repository

```bash
# Navigate to workspace
cd /workspace

# Clone repository
git clone https://github.com/galion-studio/nexuslang-v2.git project-nexus

# Navigate to project
cd project-nexus

# Switch to correct branch
git checkout clean-nexuslang

# Verify files
ls -la
```

### Step 4: Run Deployment

**Option A: Automated (Recommended)**

```bash
# Make script executable
chmod +x runpod-diagnose-and-fix.sh

# Run diagnostic and deployment
./runpod-diagnose-and-fix.sh
```

**Option B: Simplified Server**

```bash
chmod +x runpod-start-simple.sh
./runpod-start-simple.sh
```

**Option C: Full-Featured Server**

```bash
chmod +x runpod-start-server.sh
./runpod-start-server.sh
```

### Step 5: Note Public IP

The script will display your public IP at the end:

```
Public IP: 123.45.67.89
```

**Copy this IP!** You'll need it for Cloudflare.

### Step 6: Configure Cloudflare

1. **Go to Cloudflare Dashboard**
2. **Select your domain** (e.g., galion.studio)
3. **Navigate to DNS**
4. **Add A Records**:

   **Record 1** (Root domain):
   - Type: `A`
   - Name: `@`
   - IPv4 address: `123.45.67.89` (your RunPod IP)
   - Proxy status: **Proxied** (🟠 orange cloud)
   - TTL: Auto

   **Record 2** (WWW):
   - Type: `A`
   - Name: `www`
   - IPv4 address: `123.45.67.89` (your RunPod IP)
   - Proxy status: **Proxied** (🟠 orange cloud)
   - TTL: Auto

5. **Configure SSL/TLS**:
   - Go to SSL/TLS → Overview
   - Set encryption mode: **"Flexible"**

6. **Wait 1-3 minutes** for DNS propagation

### Step 7: Test Deployment

```bash
# Test locally
curl http://localhost:8080/health

# Test via public IP
curl http://123.45.67.89:8080/health

# Test via domain (after Cloudflare)
curl https://galion.studio/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-14T20:00:00Z",
  "version": "2.0.0"
}
```

---

## ⚙️ Configuration

### Environment Variables

Create `/workspace/project-nexus/.env`:

```bash
# Server
PORT=8080
HOST=0.0.0.0
WORKERS=2

# Database (if using)
DATABASE_URL=postgresql://user:pass@host:5432/db

# Redis (if using)
REDIS_URL=redis://localhost:6379/0

# AI APIs
OPENAI_API_KEY=your-key-here

# Security
SECRET_KEY=your-secret-key-change-this
```

### Port Configuration

**Expose port 8080** in RunPod pod settings:

1. Stop pod
2. Edit pod
3. Expose TCP Ports → Add `8080`
4. Save and restart pod

---

## 📊 Monitoring

### Check Server Status

```bash
# Health check
curl http://localhost:8080/health

# System info
curl http://localhost:8080/system-info

# View logs
tail -f /workspace/logs/galion-backend.log

# Check process
ps aux | grep uvicorn

# Check port
netstat -tulpn | grep 8080
```

### Resource Monitoring

```bash
# CPU and memory
htop

# Disk usage
df -h

# Network connections
netstat -tuln

# GPU usage (if using GPU)
nvidia-smi
```

### Log Files

```bash
# Application logs
tail -f /workspace/logs/galion-backend.log

# Simplified server logs
tail -f /workspace/logs/galion-simple.log

# All logs
tail -f /workspace/logs/*.log
```

---

## 🔧 Troubleshooting

### Server Won't Start

```bash
# Run diagnostic
cd /workspace/project-nexus
./runpod-diagnose-and-fix.sh

# Check logs
tail -50 /workspace/logs/galion-backend.log

# Try simplified server
./runpod-start-simple.sh
```

### Port Already in Use

```bash
# Kill existing processes
pkill -f uvicorn

# Or force kill port 8080
fuser -k 8080/tcp

# Restart
./runpod-start-simple.sh
```

### Import Errors

```bash
# Reinstall dependencies
cd /workspace/project-nexus
pip install -r requirements.txt

# Set PYTHONPATH
export PYTHONPATH=/workspace/project-nexus:/workspace/project-nexus/v2

# Use simplified server
./runpod-start-simple.sh
```

### Cloudflare Error 521

**Checklist**:

1. ✅ Server running on RunPod?
   ```bash
   curl http://localhost:8080/health
   ```

2. ✅ Port 8080 exposed in pod settings?

3. ✅ Correct IP in Cloudflare DNS?
   ```bash
   curl ifconfig.me
   ```

4. ✅ Cloudflare SSL set to "Flexible"?

5. ✅ Waited for DNS propagation? (2-3 minutes)

6. ✅ Orange cloud enabled in Cloudflare?

### Pod Stops Unexpectedly

```bash
# Check pod status in RunPod dashboard
# Possible causes:
# - Out of credits
# - Pod limit reached
# - Server crashed

# View error logs
tail -100 /workspace/logs/galion-backend.log
```

---

## 💰 Cost Optimization

### Tips to Save Money

1. **Choose Right GPU**:
   - CPU pod: $0.10-0.20/hour
   - RTX 3090: $0.30-0.50/hour
   - A4000: $0.40-0.60/hour

2. **Stop When Not Using**:
   ```bash
   # Stop server
   pkill -f uvicorn
   ```
   Then stop pod in RunPod dashboard

3. **Use Spot Instances**:
   - 50-70% cheaper
   - May be terminated with notice

4. **Optimize Resources**:
   - Use fewer workers
   - Reduce memory usage
   - Cache aggressively

5. **Monitor Usage**:
   - Check RunPod dashboard
   - Set up billing alerts
   - Review logs regularly

### Estimated Costs

**Development/Testing**:
- CPU Pod: ~$0.15/hour = $3.60/day
- Basic GPU: ~$0.40/hour = $9.60/day

**Production (24/7)**:
- CPU Pod: ~$110/month
- Basic GPU: ~$290/month
- High-end GPU: ~$500-800/month

---

## 🔄 Maintenance

### Updating Deployment

```bash
# Stop server
pkill -f uvicorn

# Pull latest changes
cd /workspace/project-nexus
git pull origin clean-nexuslang

# Restart server
./runpod-start-simple.sh
```

### Backup Data

```bash
# Backup application data
tar -czf backup-$(date +%Y%m%d).tar.gz \
  /workspace/project-nexus \
  /workspace/logs

# Download via SCP (from your computer)
scp -P PORT root@RUNPOD_IP:/workspace/backup-*.tar.gz ./
```

### Clean Up

```bash
# Remove old logs
rm /workspace/logs/*.log.old

# Clean Python cache
find /workspace/project-nexus -type d -name "__pycache__" -exec rm -r {} +

# Clean Docker (if using)
docker system prune -af
```

---

## 📚 Additional Resources

- [RunPod Documentation](https://docs.runpod.io/)
- [Main Project README](../README.md)
- [Backend README](../v2/backend/README.md)
- [RunPod SSH Instructions](../RUNPOD_SSH_INSTRUCTIONS.md)
- [Troubleshooting Guide](../RUNPOD_WEB_SERVER_FIX.md)
- [Quick Reference](../RUNPOD_QUICK_REFERENCE.md)

---

## 🆘 Support

### Get Help

1. **Run diagnostic**: `./runpod-diagnose-and-fix.sh`
2. **Check logs**: `tail -50 /workspace/logs/galion-backend.log`
3. **Read troubleshooting**: See above section
4. **GitHub Issues**: [Report an issue](https://github.com/galion-studio/nexuslang-v2/issues)

---

## ✅ Deployment Checklist

Before going live, ensure:

- [ ] Server starts successfully
- [ ] Health check returns "healthy"
- [ ] Port 8080 exposed in RunPod
- [ ] Public IP obtained
- [ ] Cloudflare DNS configured
- [ ] SSL/TLS set to "Flexible"
- [ ] Domain resolves correctly
- [ ] API endpoints working
- [ ] Logs show no errors
- [ ] Monitoring set up
- [ ] Backup plan in place
- [ ] Cost limits understood

---

**Built with ❤️ by the Galion Studio team**

**Last Updated**: November 14, 2025
