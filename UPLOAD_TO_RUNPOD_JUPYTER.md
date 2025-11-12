# 📤 Upload Project to RunPod via Jupyter

## Method 1: Direct Upload via Jupyter (Easiest)

### Step 1: Access Jupyter on RunPod

1. Go to your RunPod pod
2. Click "Connect" → "Jupyter Lab"
3. Opens: `https://YOUR_POD_ID.proxy.runpod.net/lab`

### Step 2: Upload Files

**Option A: Upload Zip (Recommended)**

1. On your PC, create deployment package:
   ```powershell
   .\create-deployment-package.ps1
   ```
   Creates: `nexuslang-v2-deploy.zip`

2. In Jupyter Lab:
   - Click Upload button (⬆️ icon)
   - Select `nexuslang-v2-deploy.zip`
   - Wait for upload (shows progress)

3. Extract in Jupyter terminal:
   ```bash
   cd /workspace
   unzip nexuslang-v2-deploy.zip
   cd nexuslang-v2
   ```

**Option B: Upload Individual Files**

1. In Jupyter Lab file browser:
   - Right-click → New Folder → `nexuslang-v2`
   - Drag & drop files from PC
   - Or use Upload button

### Step 3: Setup & Run

In Jupyter terminal:

```bash
cd /workspace/nexuslang-v2
chmod +x runpod-quick-deploy.sh
./runpod-quick-deploy.sh
```

---

## Method 2: GitHub (Fastest for Large Projects)

### Step 1: Push to GitHub

On your PC:
```powershell
git init
git add .
git commit -m "Initial commit"
git remote add origin YOUR_GITHUB_URL
git push -u origin main
```

### Step 2: Clone on RunPod

In Jupyter terminal:
```bash
cd /workspace
git clone YOUR_GITHUB_URL nexuslang-v2
cd nexuslang-v2
chmod +x runpod-quick-deploy.sh
./runpod-quick-deploy.sh
```

---

## Method 3: RunPod File Manager

1. In RunPod pod → "Files" tab
2. Navigate to `/workspace`
3. Click "Upload"
4. Select `nexuslang-v2-deploy.zip`
5. Extract via terminal

---

## Quick Commands for Jupyter Terminal

### After Upload:

```bash
# Navigate to workspace
cd /workspace

# Extract if uploaded zip
unzip nexuslang-v2-deploy.zip

# Go to project
cd nexuslang-v2

# Make scripts executable
chmod +x *.sh

# Deploy
./runpod-quick-deploy.sh
```

### Configure AI:

```bash
# Edit .env
nano .env

# Add your keys:
# OPENROUTER_API_KEY=sk-or-your-key

# Restart
docker-compose restart backend
```

### Check Status:

```bash
# View logs
docker-compose logs -f backend

# Check health
curl http://localhost:8000/health

# List containers
docker-compose ps
```

---

## File Size Considerations

**Essential Files Only (~50MB):**
- Python source code
- Configuration files
- Docker files
- Scripts

**Excluded (download on RunPod):**
- `node_modules/` - Will install on pod
- `.git/` - Clone from GitHub instead
- `__pycache__/` - Generated on pod
- Large AI models - Downloaded when needed

---

## Jupyter Notebook for Setup

Create this in Jupyter Lab:

```python
# Cell 1: Extract and setup
!cd /workspace && unzip -q nexuslang-v2-deploy.zip
!cd /workspace/nexuslang-v2 && chmod +x *.sh
print("✅ Extracted")

# Cell 2: Install Docker
!curl -fsSL https://get.docker.com | sh
!curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
!chmod +x /usr/local/bin/docker-compose
print("✅ Docker installed")

# Cell 3: Deploy
!cd /workspace/nexuslang-v2 && ./runpod-quick-deploy.sh
print("✅ Deployed")

# Cell 4: Check status
import requests
try:
    r = requests.get("http://localhost:8000/health")
    print(f"✅ Backend: {r.json()}")
except:
    print("⏳ Backend starting...")

# Cell 5: Show URLs
import os
hostname = os.getenv('HOSTNAME', 'YOUR_POD_ID')
print(f"""
🌐 Your URLs:
  API:  https://{hostname}-8000.proxy.runpod.net
  Docs: https://{hostname}-8000.proxy.runpod.net/docs
  UI:   https://{hostname}-3000.proxy.runpod.net
""")
```

---

## Tips for Jupyter Upload

### Faster Upload:
1. Compress files: `zip -r project.zip . -x "node_modules/*" ".git/*"`
2. Use GitHub for large projects
3. Upload during off-peak hours

### Monitor Upload:
- Jupyter shows progress bar
- Large files may take 5-10 minutes
- Don't close browser during upload

### Troubleshooting:

**Upload fails:**
- Try smaller zip file
- Use GitHub method instead
- Split into multiple zips

**Upload stuck:**
- Refresh Jupyter Lab
- Try different browser
- Check RunPod connection

**Disk full:**
- Clean old files: `rm -rf /workspace/old_projects`
- Check space: `df -h /workspace`

---

## What Gets Uploaded

**Include:**
- ✅ `v2/backend/` - Python code
- ✅ `v2/frontend/` - React code
- ✅ `*.yml` - Docker configs
- ✅ `*.sh` - Scripts
- ✅ `*.md` - Docs
- ✅ `.env` - After adding keys

**Exclude:**
- ❌ `node_modules/`
- ❌ `.git/`
- ❌ `__pycache__/`
- ❌ `*.pyc`
- ❌ `v1/` (old version)

---

## After Upload Checklist

- [ ] Files extracted to `/workspace/nexuslang-v2`
- [ ] Made scripts executable (`chmod +x *.sh`)
- [ ] Added API keys to `.env`
- [ ] Ran deployment script
- [ ] Exposed ports in RunPod (8000, 3000)
- [ ] Tested health endpoint
- [ ] Accessed /docs

---

## Quick Reference

| Action | Command |
|--------|---------|
| Upload | Drag & drop in Jupyter |
| Extract | `unzip file.zip` |
| Deploy | `./runpod-quick-deploy.sh` |
| Logs | `docker-compose logs -f` |
| Restart | `docker-compose restart` |
| Stop | `docker-compose down` |

---

**Ready to upload! Start with Jupyter Lab upload method! 🚀**

