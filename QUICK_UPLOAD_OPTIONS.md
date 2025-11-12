# 🚀 Quick Upload Options to RunPod

Choose the method that works best for you:

---

## ⭐ **Option 1: GitHub (RECOMMENDED - Easiest)**

### On Your PC:

```powershell
# Run this script
.\auto-upload-github.ps1
```

This will:
1. Initialize git (if needed)
2. Commit your files
3. Push to GitHub

### On RunPod Jupyter Terminal:

```bash
cd /workspace
git clone YOUR_GITHUB_URL nexuslang-v2
cd nexuslang-v2
chmod +x runpod-quick-deploy.sh
./runpod-quick-deploy.sh
```

**Advantages:**
- ✅ Fastest for large projects
- ✅ Version control included
- ✅ Easy updates (just `git pull`)
- ✅ No file size limits

---

## 📦 **Option 2: Manual Zip Upload**

### On Your PC:

```powershell
# Create deployment package
.\create-deployment-package.ps1
```

Creates `nexuslang-v2-deploy.zip` (~50MB)

### On RunPod:

1. Open Jupyter Lab
2. Click Upload button (⬆️)
3. Select `nexuslang-v2-deploy.zip`
4. Wait for upload

### In Jupyter Terminal:

```bash
cd /workspace
unzip nexuslang-v2-deploy.zip
cd nexuslang-v2
chmod +x runpod-quick-deploy.sh
./runpod-quick-deploy.sh
```

**Advantages:**
- ✅ No GitHub needed
- ✅ All files in one package
- ✅ Works offline

---

## 🔗 **Option 3: Direct SSH Upload (Advanced)**

### Prerequisites:
- SSH access to RunPod
- SSH client installed

### On Your PC:

```powershell
# Configure and run
.\upload-to-runpod.ps1
```

Edit the script first to add your RunPod details!

**Advantages:**
- ✅ Fully automated
- ✅ No manual steps
- ✅ Direct transfer

**Disadvantages:**
- ⚠️ Requires SSH setup
- ⚠️ May be slower

---

## 📋 **Comparison**

| Method | Speed | Ease | Best For |
|--------|-------|------|----------|
| **GitHub** | ⚡⚡⚡ | ⭐⭐⭐ | Large projects, teams |
| **Zip Upload** | ⚡⚡ | ⭐⭐ | Quick one-time deploy |
| **SSH** | ⚡ | ⭐ | Advanced users |

---

## 🎯 **Recommended Flow**

### First Time:

1. **Use GitHub method** (auto-upload-github.ps1)
2. Clone on RunPod
3. Deploy

### Updates:

```bash
# On RunPod
cd /workspace/nexuslang-v2
git pull
docker-compose restart backend
```

---

## ⚡ **Super Quick Start**

**Absolute fastest way:**

```powershell
# On PC - one command
.\auto-upload-github.ps1
```

```bash
# On RunPod - one command (copy from script output)
cd /workspace && git clone YOUR_URL nexuslang-v2 && cd nexuslang-v2 && chmod +x *.sh && ./runpod-quick-deploy.sh
```

**Done in 2 minutes!** 🎉

---

## 🆘 **Troubleshooting**

### GitHub push fails
- Check you're logged in: `git config user.email`
- Create GitHub token: Settings → Developer settings → Personal access tokens
- Use token as password when pushing

### Upload too slow
- Use GitHub method instead
- Or compress better: Only include v2/ folder

### SSH not working
- Use Jupyter Lab upload instead
- It's more reliable for RunPod

---

## 📝 **After Upload**

Regardless of method, once files are on RunPod:

1. **Add API keys** to `.env`
2. **Expose ports** in RunPod Dashboard (8000, 3000, 3001)
3. **Access your platform** at the proxy URLs

---

**Choose GitHub method for easiest experience!** 🚀

