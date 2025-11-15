# ⚡ Quick Reference - Cursor SSH Pipeline

**One-page command reference for daily use**

---

## 🚀 Quick Commands

### From Cursor IDE

Press `Ctrl+Shift+P` → "Tasks: Run Task" → Select:

- **Deploy All** - Full deployment
- **Quick Deploy** - Fast deploy (no build)
- **Check Status** - View services
- **View Logs** - Live logs
- **Restart Services** - Restart all
- **Health Check** - Check endpoints
- **Open Shell** - RunPod terminal
- **Start Tunnel** - Local access

---

## 💻 Command Line

### Windows PowerShell

```powershell
# Deploy
.\deploy.ps1                    # Full deploy
.\deploy.ps1 -SkipBuild        # Quick deploy

# Quick commands
.\quick-commands.ps1 status     # Service status
.\quick-commands.ps1 logs       # View logs
.\quick-commands.ps1 restart    # Restart all
.\quick-commands.ps1 health     # Health check
.\quick-commands.ps1 shell      # Open shell
.\quick-commands.ps1 tunnel     # Start tunnel

# Remote execution
.\remote-exec.ps1 "any command"
```

### Mac/Linux Bash

```bash
# Deploy
./deploy.sh                     # Full deploy
./deploy.sh all true            # Quick deploy

# Quick commands
./quick-commands.sh status      # Service status
./quick-commands.sh logs        # View logs
./quick-commands.sh restart     # Restart all
./quick-commands.sh health      # Health check
./quick-commands.sh shell       # Open shell
./quick-commands.sh tunnel      # Start tunnel

# Remote execution
ssh runpod "any command"
```

---

## 🔌 SSH Shortcuts

```bash
# Connect to RunPod
ssh runpod

# Start tunnel (all services)
ssh runpod-tunnel -N

# Execute command
ssh runpod "cd /nexuslang-v2 && pm2 status"
```

---

## 📊 Monitoring

```bash
# Service status
pm2 status

# View logs
pm2 logs
pm2 logs galion-backend
pm2 logs galion-studio --lines 100

# Health endpoints
curl http://localhost:8000/health
curl http://localhost/health

# Check ports
ss -tlnp | grep -E ":(80|8000|3001|3002|3003)"
```

---

## 🛠️ Service Management

```bash
# Restart
pm2 restart all
pm2 restart galion-backend

# Stop
pm2 stop all
pm2 stop galion-backend

# Start
pm2 start all
pm2 start galion-backend

# Delete
pm2 delete all
pm2 delete galion-backend

# Save config
pm2 save
```

---

## 🌐 Local Access (via Tunnel)

After running `.\quick-commands.ps1 tunnel`:

- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Galion Studio:** http://localhost:3001
- **Dev Platform:** http://localhost:3002
- **Galion App:** http://localhost:3003
- **Nginx:** http://localhost:80

---

## 🔍 Troubleshooting Commands

```bash
# Check SSH connection
ssh runpod echo "Connected!"

# View recent errors
ssh runpod "pm2 logs --err --lines 50"

# Check disk space
ssh runpod "df -h"

# Check memory
ssh runpod "free -h"

# Check processes
ssh runpod "ps aux | grep node"
ssh runpod "ps aux | grep python"

# Network check
ssh runpod "netstat -tlnp"
ssh runpod "ss -tlnp"

# Git status
ssh runpod "cd /nexuslang-v2 && git status"
ssh runpod "cd /nexuslang-v2 && git log -1"
```

---

## 🔧 Common Workflows

### Deploy Code Changes

```bash
# Local machine
git add .
git commit -m "Your changes"
git push origin clean-nexuslang

# Deploy
.\deploy.ps1
```

### Restart After Config Change

```bash
.\quick-commands.ps1 restart
.\quick-commands.ps1 health
```

### Debug Service Issues

```bash
# Check logs
.\quick-commands.ps1 logs

# Open shell for investigation
.\quick-commands.ps1 shell

# Inside shell:
cd /nexuslang-v2
pm2 logs galion-backend --lines 100
```

### Test Changes Locally

```bash
# Start tunnel
.\quick-commands.ps1 tunnel

# Test in browser
http://localhost:8000/docs
```

---

## 📁 Important Paths

```
Local:
  ~/Documents/project-nexus/cursor-ssh-pipeline/
  ~/.ssh/config
  ~/.ssh/id_ed25519

RunPod:
  /nexuslang-v2/                  # Main project
  /nexuslang-v2/v2/backend/       # Backend code
  /nexuslang-v2/galion-studio/    # Studio frontend
  /nexuslang-v2/galion-app/       # App frontend
  /nexuslang-v2/developer-platform/ # Dev platform
  ~/.ssh/authorized_keys          # SSH keys
```

---

## 🆘 Emergency Commands

```bash
# Kill all services
ssh runpod "pm2 delete all"

# Kill specific port
ssh runpod "kill -9 \$(lsof -ti:8000)"

# Force restart everything
ssh runpod "cd /nexuslang-v2 && pm2 delete all && pm2 flush"
.\deploy.ps1 -SkipBuild

# Reset git state
ssh runpod "cd /nexuslang-v2 && git reset --hard origin/clean-nexuslang"
```

---

## 📞 Quick Support Info

```bash
# Get all diagnostic info
ssh runpod "echo '=== PM2 ===' && pm2 status && \
            echo '=== Health ===' && curl -s localhost:8000/health && \
            echo '=== Ports ===' && ss -tlnp | grep -E ':(80|8000|3001)' && \
            echo '=== Disk ===' && df -h && \
            echo '=== Memory ===' && free -h"
```

---

## 🎯 Daily Workflow

**Morning:**
```bash
ssh runpod                      # Check connection
.\quick-commands.ps1 status    # Check services
.\quick-commands.ps1 tunnel &  # Start tunnel
```

**During Development:**
```bash
# Make changes locally
git commit -am "Changes"
git push
.\deploy.ps1 -SkipBuild        # Quick deploy
```

**Evening:**
```bash
.\quick-commands.ps1 health    # Final check
```

---

## 🔐 Security Notes

**Never commit:**
- `connection-info.json`
- `~/.ssh/id_ed25519` (private key)
- Any files with passwords or tokens

**Safe to commit:**
- `~/.ssh/id_ed25519.pub` (public key)
- All `.ps1` and `.sh` scripts
- Configuration templates

---

## 📚 More Help

- **Full README:** `cursor-ssh-pipeline/README.md`
- **Setup Guide:** `cursor-ssh-pipeline/SETUP_GUIDE.md`
- **RunPod Docs:** https://docs.runpod.io/

---

**Last Updated:** 2025-11-15

