# 🚀 RunPod Quick Start - Universal Manager

## One-Command Magic ✨

Get the entire Galion Platform running on RunPod with a single command!

---

## 📋 Prerequisites

- RunPod account with an active pod
- SSH access to your RunPod instance (or use web terminal)
- At least 10GB free disk space
- At least 2GB available memory

---

## ⚡ Quick Start

### Step 1: Connect to RunPod

**Option A: Web Terminal (Easiest)**
1. Go to your RunPod dashboard
2. Click on your pod
3. Click "Connect" → "Start Web Terminal"

**Option B: SSH**
```bash
ssh root@YOUR_RUNPOD_IP
```

### Step 2: Run Universal Manager

Copy and paste this single command:

```bash
cd /nexuslang-v2 && wget -O - https://raw.githubusercontent.com/galion-studio/nexuslang-v2/clean-nexuslang/universal-manager.sh | sudo bash
```

### Step 3: Relax ☕

The Universal Manager will:
- ✅ Validate your system
- ✅ Install all dependencies
- ✅ Fix any issues automatically
- ✅ Start all services
- ✅ Configure Nginx
- ✅ Launch backup daemon
- ✅ Run health checks
- ✅ Display beautiful status report

**Time:** ~2-3 minutes

---

## 📊 What You'll See

```
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║   ██████╗  █████╗ ██╗     ██╗ ██████╗ ███╗   ██╗       ║
║  ██╔════╝ ██╔══██╗██║     ██║██╔═══██╗████╗  ██║       ║
║  ██║  ███╗███████║██║     ██║██║   ██║██╔██╗ ██║       ║
║  ██║   ██║██╔══██║██║     ██║██║   ██║██║╚██╗██║       ║
║  ╚██████╔╝██║  ██║███████╗██║╚██████╔╝██║ ╚████║       ║
║   ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝       ║
║                                                          ║
║              UNIVERSAL STARTING MANAGER v2.0            ║
║         Intelligent • Autonomous • Self-Healing         ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
```

Then you'll see:
- ✅ System validation
- ✅ Dependency installation/updates
- ✅ Port conflict resolution
- ✅ Service recovery
- ✅ Service launch
- ✅ Health checks
- ✅ Backup daemon launch
- ✅ Final status report

---

## 🌐 Access Your Services

After completion, access your services:

### Internal Access (from RunPod)

```bash
# Backend API
curl http://localhost:8000/health

# API Documentation
curl http://localhost:8000/docs

# Galion Studio
curl http://localhost:3030

# Galion App
curl http://localhost:3000

# Developer Platform
curl http://localhost:3003
```

### External Access

1. **Find your RunPod public URL** in the RunPod dashboard
2. Access services:
   - Backend API: `http://YOUR_RUNPOD_URL:8000/health`
   - API Docs: `http://YOUR_RUNPOD_URL:8000/docs`
   - Galion Studio: `http://YOUR_RUNPOD_URL:3030`
   - Galion App: `http://YOUR_RUNPOD_URL:3000`
   - Developer Platform: `http://YOUR_RUNPOD_URL:3003`

---

## 🔧 Useful Commands

### View Service Status

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
pm2 logs galion-app
pm2 logs developer-platform

# Backup daemon
tail -f /var/log/galion-platform/backup-daemon.log
```

### Monitor Services

```bash
pm2 monit
```

### Restart Services

```bash
# All services
pm2 restart all

# Specific service
pm2 restart backend
```

### Check Backups

```bash
ls -lh /var/backups/galion-platform/
```

### Restore from Backup

```bash
cd /nexuslang-v2
./restore-backup.sh
```

---

## 🆘 Troubleshooting

### Problem: Service not starting

**Solution:**
```bash
# Re-run Universal Manager
cd /nexuslang-v2
sudo ./universal-manager.sh
```

### Problem: Port conflict

**Solution:**
```bash
# Auto-fix engine will handle it, or manually:
./auto-fix-engine.sh port_conflict 8000
```

### Problem: Missing dependency

**Solution:**
```bash
# Auto-fix engine will handle it, or manually:
./auto-fix-engine.sh missing_dependency python fastapi
```

### Problem: Service crashed

**Solution:**
```bash
# Auto-fix engine will handle it, or manually:
./auto-fix-engine.sh service_crashed backend
```

### Problem: Need to restore from backup

**Solution:**
```bash
cd /nexuslang-v2
./restore-backup.sh
```

---

## 📈 Performance Tips

### Optimize Memory

If running low on memory:

```bash
# Restart services to free memory
pm2 restart all

# Check memory usage
free -h
pm2 status
```

### Optimize Disk

If running low on disk space:

```bash
# Clean old backups (keeps last 10)
cd /var/backups/galion-platform/
ls -lt *.tar.gz | tail -n +11 | awk '{print $9}' | xargs rm -f

# Clean npm cache
npm cache clean --force

# Clean pip cache
pip3 cache purge
```

### Optimize Performance

```bash
# Use PM2 monitoring
pm2 monit

# Check logs for errors
pm2 logs --lines 100

# Restart services for clean state
pm2 restart all
```

---

## 🔄 Updates

### Update Platform Code

```bash
cd /nexuslang-v2
git pull origin clean-nexuslang
pm2 restart all
```

### Update Universal Manager

```bash
cd /nexuslang-v2
wget -O universal-manager.sh https://raw.githubusercontent.com/galion-studio/nexuslang-v2/clean-nexuslang/universal-manager.sh
chmod +x universal-manager.sh
sudo ./universal-manager.sh
```

---

## 💾 Backup & Restore

### Automatic Backups

Backups run automatically every 15 minutes. No action needed!

**Check backup status:**
```bash
cat /var/run/galion-last-backup
ls -lh /var/backups/galion-platform/
```

### Manual Backup

```bash
# Backups are automatic, but you can trigger one by restarting the daemon
pkill -f backup-daemon
cd /nexuslang-v2
nohup bash backup-daemon.sh > /var/log/galion-platform/backup-daemon.log 2>&1 &
```

### Restore from Backup

```bash
cd /nexuslang-v2
./restore-backup.sh

# Or restore specific timestamp
./restore-backup.sh 2025-11-15_23-30
```

---

## 🎯 Common Tasks

### Task: Deploy Code Changes

```bash
cd /nexuslang-v2
git pull origin clean-nexuslang
pm2 restart all
```

### Task: Check Service Health

```bash
pm2 status
curl http://localhost:8000/health
curl http://localhost:3000
curl http://localhost:3003
curl http://localhost:3030
```

### Task: View Recent Logs

```bash
pm2 logs --lines 100
```

### Task: Clean Restart

```bash
pm2 delete all
cd /nexuslang-v2
sudo ./universal-manager.sh
```

### Task: Check System Resources

```bash
# Memory
free -h

# Disk
df -h

# CPU
top

# PM2 monitoring
pm2 monit
```

---

## 📚 Documentation

- **Universal Manager:** `UNIVERSAL-MANAGER-README.md`
- **Implementation Summary:** `IMPLEMENTATION-SUMMARY.md`
- **API Reference:** `v2/backend/API_REFERENCE.md`
- **Main README:** `README.md`

---

## 🆘 Support

### Check Logs

```bash
# Universal Manager logs
ls -lh /var/log/galion-platform/universal-manager-*.log
tail -100 /var/log/galion-platform/universal-manager-*.log

# Backup daemon logs
tail -f /var/log/galion-platform/backup-daemon.log

# Service logs
pm2 logs
```

### Get Help

1. Check logs (see above)
2. Re-run Universal Manager: `sudo ./universal-manager.sh`
3. Restore from backup: `./restore-backup.sh`
4. Check GitHub issues: https://github.com/galion-studio/nexuslang-v2/issues

---

## ✅ Success Checklist

After running Universal Manager, verify:

- [ ] All services show "online" in `pm2 status`
- [ ] Backend API responds: `curl http://localhost:8000/health`
- [ ] Galion Studio responds: `curl http://localhost:3030`
- [ ] Galion App responds: `curl http://localhost:3000`
- [ ] Developer Platform responds: `curl http://localhost:3003`
- [ ] Nginx is running: `ps aux | grep nginx`
- [ ] Backup daemon is running: `ps aux | grep backup-daemon`
- [ ] Backups exist: `ls -lh /var/backups/galion-platform/`

---

## 🎉 You're All Set!

Your Galion Platform is now:
- ✅ Fully operational
- ✅ Self-healing
- ✅ Automatically backed up
- ✅ Production-ready

**Enjoy your autonomous platform!** 🚀

---

## 🔗 Quick Links

- **GitHub:** https://github.com/galion-studio/nexuslang-v2
- **Branch:** clean-nexuslang
- **Universal Manager:** https://raw.githubusercontent.com/galion-studio/nexuslang-v2/clean-nexuslang/universal-manager.sh

---

**Remember:** If anything goes wrong, just run:
```bash
cd /nexuslang-v2 && sudo ./universal-manager.sh
```

The Universal Manager will fix everything automatically! 🎯

