# 🚀 V2 Deployment - Quick Start

**NO MORE SSH PROBLEMS! Use simple HTTP instead.**

---

## ⚡ Setup (5 Minutes)

### **Step 1: On RunPod Web Terminal**

```bash
# Pull latest code
cd /nexuslang-v2
git pull origin clean-nexuslang

# Install Flask
pip3 install flask

# Start webhook
cd v2-deployment
chmod +x start-webhook.sh
./start-webhook.sh
```

You should see: `✅ Webhook started on port 7000!`

---

### **Step 2: Expose Port in RunPod Dashboard**

1. Go to **RunPod.io** → Your Pod
2. Click **"Edit"** or **"Configure"**
3. Find **"Expose TCP Ports"** or **"Port Mappings"**
4. Add port: **7000**
5. **Save** and note the external port number

---

### **Step 3: On Your Windows Laptop**

```powershell
# Pull latest code
cd C:\Users\Gigabyte\Documents\project-nexus
git pull origin clean-nexuslang

# Test the webhook
cd v2-deployment
.\deploy-from-laptop.ps1 -Action health
```

If you see `Status: healthy` → **SUCCESS!** ✅

---

## 🚀 Deploy!

```powershell
.\deploy-from-laptop.ps1 -Action deploy
```

**That's it!** No SSH, no passwords, no problems! 🎉

---

## 📋 Other Commands

```powershell
# Check service status
.\deploy-from-laptop.ps1 -Action status

# View logs
.\deploy-from-laptop.ps1 -Action logs

# Health check
.\deploy-from-laptop.ps1 -Action health
```

---

## 🔧 If Port 7000 is Already Used

RunPod might map it to a different external port (like 7001, 7002, etc.)

Check your pod's **TCP Port Mappings** and use that port:

```powershell
.\deploy-from-laptop.ps1 -Port 7001 -Action health
```

---

## ✅ Benefits

- ✅ No SSH configuration
- ✅ No password issues
- ✅ Works in Docker containers
- ✅ Simple HTTP requests
- ✅ Always stable

---

**Ready? Start with Step 1 on RunPod!** 🚀

