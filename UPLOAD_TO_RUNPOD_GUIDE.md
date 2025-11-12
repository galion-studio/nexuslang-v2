# Upload Code to RunPod - Quick Guide

## Connection Details

**Host:** 213.173.105.83  
**Port:** 56137  
**User:** root  
**SSH Key:** `~/.ssh/id_ed25519`

## Method 1: Using WinSCP (Easiest)

1. Open WinSCP
2. **File protocol:** SFTP
3. **Host name:** 213.173.105.83
4. **Port:** 56137
5. **User:** root
6. **Private key:** Browse to `C:\Users\Gigabyte\.ssh\id_ed25519`
7. Click "Login"
8. Upload `C:\Users\Gigabyte\Documents\project-nexus\` to `/workspace/galion-platform/`

## Method 2: Using SCP Command (PowerShell)

```powershell
# From Windows PowerShell
scp -P 56137 -i C:\Users\Gigabyte\.ssh\id_ed25519 -r C:\Users\Gigabyte\Documents\project-nexus\* root@213.173.105.83:/workspace/galion-platform/
```

## Method 3: Using rsync (if available)

```bash
rsync -avz -e "ssh -p 56137 -i ~/.ssh/id_ed25519" \
  /c/Users/Gigabyte/Documents/project-nexus/ \
  root@213.173.105.83:/workspace/galion-platform/
```

## What to Upload

From `C:\Users\Gigabyte\Documents\project-nexus\`:
- ✅ `/v2/` folder (NexusLang v2 - developer.galion.app)
- ✅ `/v1/galion/` folder (Galion.app code)
- ✅ `docker-compose*.yml` files
- ✅ `cloudflare-tunnel*.yml` files
- ✅ `.env.template` files

## After Upload

Run on RunPod:
```bash
# Verify upload
ls -la /workspace/galion-platform/

# Check structure
tree /workspace/galion-platform -L 2
```

## Estimated Time

- Upload size: ~500MB
- Time: 5-10 minutes depending on connection

