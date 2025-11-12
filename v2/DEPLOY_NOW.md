# 🚀 DEPLOY NOW - Quick Commands

## Step 1: Set RunPod Details

### Windows (PowerShell):
```powershell
$env:RUNPOD_HOST = "your-runpod-ip-here"
$env:RUNPOD_PORT = "your-ssh-port-here"
```

### Linux/Mac (Bash):
```bash
export RUNPOD_HOST="your-runpod-ip-here"
export RUNPOD_PORT="your-ssh-port-here"
```

---

## Step 2: Deploy

### Windows:
```powershell
cd v2
.\deploy-to-runpod.ps1
```

### Linux/Mac:
```bash
cd v2
chmod +x deploy-to-runpod.sh
./deploy-to-runpod.sh
```

---

## ⏱️ Deploy Time: ~10 minutes

The script will automatically:
- ✅ Test SSH connection
- ✅ Clone/update code
- ✅ Install dependencies
- ✅ Setup environment
- ✅ Start Docker services
- ✅ Run migrations
- ✅ Verify deployment

---

## 🌐 After Deployment

Your system will be available at:
- **Backend**: `http://YOUR_RUNPOD_IP:8100`
- **Frontend**: `http://YOUR_RUNPOD_IP:3100`
- **API Docs**: `http://YOUR_RUNPOD_IP:8100/docs`

---

## 🔧 Manage System

Use the admin control script:

### Windows:
```powershell
.\admin-control.ps1
```

### Linux/Mac:
```bash
./admin-control.sh  # (use admin-control.ps1 syntax)
```

---

## 📚 Documentation

- **Quick Deploy Guide**: `QUICKSTART_DEPLOY.md`
- **Full Security Setup**: `DEPLOY_RUNPOD_SECURE.md`
- **Admin Manual**: `README_ADMIN.md`
- **Getting Started**: `START_HERE_CONTENT_MANAGER.md`

---

## 🆘 Need Help?

### Can't connect to RunPod?
```bash
# Test SSH
ssh root@YOUR_RUNPOD_IP -p YOUR_PORT
```

### Don't have RunPod credentials?
1. Go to https://runpod.io
2. Create/start a pod
3. Get SSH connection details
4. Copy IP and port

### Want to deploy locally first?
```bash
# Just run docker-compose
cd v2
docker-compose -f docker-compose.nexuslang.yml up -d
```

---

**Status**: Ready to deploy! 🚀

