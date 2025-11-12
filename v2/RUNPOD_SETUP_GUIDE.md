# 🚀 RunPod Setup & Deployment Guide

## Step-by-Step: Get Your System Running in the Cloud

---

## Part 1: Get RunPod Credentials (5 minutes)

### 1.1 Create RunPod Account

1. **Go to RunPod**:
   - Visit: https://runpod.io
   - Click "Sign Up" (or "Login" if you have an account)
   - Complete registration

2. **Add Payment Method**:
   - Go to Settings → Billing
   - Add credit card or crypto wallet
   - RunPod charges only for what you use

### 1.2 Deploy a Pod

1. **Start Deployment**:
   - Click "Deploy" or "GPU Pods" in the top menu
   - Select "Deploy On-Demand" (or "Spot" for cheaper)

2. **Choose Template**:
   - Search for "Ubuntu 22.04" or "RunPod PyTorch"
   - **Don't need GPU** - uncheck GPU requirement
   
3. **Select Specifications**:
   ```
   CPU: 4+ vCPUs (recommended: 4-8)
   RAM: 16GB+ (recommended: 16-32 GB)
   Storage: 50GB+ (recommended: 100GB)
   ```

4. **Configuration**:
   - Region: Choose closest to you (EU-RO-1, US-OR-1, etc.)
   - Volume: Default is fine
   - Click "Deploy On-Demand"

5. **Wait for Pod to Start** (30-60 seconds):
   - Status will change from "Starting" to "Running"
   - Green indicator means ready

### 1.3 Get SSH Connection Details

Once your pod is running:

1. **Find Connect Button**:
   - Click on your pod name
   - Look for "Connect" section

2. **Copy SSH Command**:
   You'll see something like:
   ```bash
   ssh root@12.345.67.89 -p 12345 -i ~/.ssh/id_ed25519
   ```

3. **Extract Credentials**:
   - **RUNPOD_HOST**: `12.345.67.89` (the IP address after `root@`)
   - **RUNPOD_PORT**: `12345` (the number after `-p`)
   
4. **Save These Values**:
   ```
   IP: 12.345.67.89
   Port: 12345
   ```

---

## Part 2: Setup SSH Access (3 minutes)

### Option A: Using Existing SSH Keys (If you have them)

Check if you have SSH keys:
```powershell
Test-Path ~/.ssh/id_ed25519
# If True, you're good to go!
```

### Option B: Generate New SSH Keys (If needed)

```powershell
# Generate new key
ssh-keygen -t ed25519 -C "your-email@example.com"

# Press Enter for default location
# Press Enter for no passphrase (or add one for extra security)
```

### Option C: Use RunPod's Web Terminal (Easiest)

RunPod provides a web-based terminal:
1. In your pod details, click "Web Terminal"
2. This opens a browser-based SSH session
3. You can use this initially, then setup keys later

---

## Part 3: Test Connection (1 minute)

### Windows PowerShell:
```powershell
# Set variables (use your actual values)
$env:RUNPOD_HOST = "12.345.67.89"
$env:RUNPOD_PORT = "12345"

# Test connection
ssh root@$env:RUNPOD_HOST -p $env:RUNPOD_PORT

# You should see:
# root@runpod-pod-xxxxx:~#

# Type 'exit' to disconnect
```

### If Connection Fails:

**Problem 1: Permission denied (publickey)**
- RunPod doesn't have your SSH key
- Solution: Use RunPod Web Terminal instead, or add your key:
  ```powershell
  # Copy your public key
  Get-Content ~/.ssh/id_ed25519.pub | clip
  
  # Go to RunPod → Settings → SSH Keys
  # Click "Add SSH Key"
  # Paste and save
  # Restart your pod
  ```

**Problem 2: Connection timeout**
- Pod might not be fully started
- Wait 30 more seconds and try again

**Problem 3: SSH key not found**
- Generate one (see Part 2, Option B above)

---

## Part 4: Deploy Your System (2 minutes)

### 4.1 Set Environment Variables

**Windows PowerShell**:
```powershell
# Use your actual values from Part 1.3
$env:RUNPOD_HOST = "12.345.67.89"
$env:RUNPOD_PORT = "12345"

# Save permanently (optional)
[Environment]::SetEnvironmentVariable("RUNPOD_HOST", "12.345.67.89", "User")
[Environment]::SetEnvironmentVariable("RUNPOD_PORT", "12345", "User")
```

**Linux/Mac Bash**:
```bash
# Use your actual values
export RUNPOD_HOST="12.345.67.89"
export RUNPOD_PORT="12345"

# Save permanently (add to ~/.bashrc)
echo 'export RUNPOD_HOST="12.345.67.89"' >> ~/.bashrc
echo 'export RUNPOD_PORT="12345"' >> ~/.bashrc
source ~/.bashrc
```

### 4.2 Run Deployment Script

```powershell
# Navigate to project
cd C:\Users\Gigabyte\Documents\project-nexus\v2

# Run deployment
.\deploy-to-runpod.ps1
```

The script will:
1. ✅ Test SSH connection
2. ✅ Clone/update repository
3. ✅ Install dependencies (Docker, PostgreSQL, etc.)
4. ✅ Generate secure environment configuration
5. ✅ Build and start Docker containers
6. ✅ Run database migrations
7. ✅ Initialize with 4 brands
8. ✅ Verify services are running
9. ✅ Test API health

**Time**: ~10 minutes total

---

## Part 5: Access Your System

### 5.1 Get Access URLs

After deployment completes, you'll see:

```
🌐 Your services are running at:
   Backend:  http://12.345.67.89:8100
   Frontend: http://12.345.67.89:3100
   API Docs: http://12.345.67.89:8100/docs
```

### 5.2 Open in Browser

```powershell
# Open frontend
Start-Process "http://12.345.67.89:3100"

# Open API documentation
Start-Process "http://12.345.67.89:8100/docs"
```

**Replace `12.345.67.89` with your actual RunPod IP**

---

## Part 6: Create First User

### Via API (Recommended):

```powershell
# Create admin user
$body = @{
    username = "admin"
    email = "admin@galion.studio"
    password = "YourSecurePassword123!"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://12.345.67.89:8100/api/v2/auth/register" `
    -Method POST `
    -Body $body `
    -ContentType "application/json"
```

### Via Browser:
1. Open API docs: `http://12.345.67.89:8100/docs`
2. Find `/api/v2/auth/register`
3. Click "Try it out"
4. Fill in details and execute

---

## Part 7: Verify Everything Works

### 7.1 Check Services

```powershell
ssh root@$env:RUNPOD_HOST -p $env:RUNPOD_PORT "cd /root/project-nexus/v2 && docker-compose ps"
```

Should show:
- ✅ backend (Up)
- ✅ frontend (Up)
- ✅ postgres (Up)
- ✅ redis (Up)

### 7.2 Check Brands

```powershell
# Use admin control script
.\admin-control.ps1 -Action db

# In database shell, run:
# SELECT id, name, slug FROM brands;

# Should show 4 brands:
# - Galion Studio
# - Galion App
# - Slavic Nomad
# - Marilyn Element
```

### 7.3 Test Frontend

1. Open `http://YOUR_RUNPOD_IP:3100`
2. You should see the dashboard
3. Navigate to `/content-manager/compose`
4. Try creating a draft post

---

## Part 8: Secure Your Deployment (Optional but Recommended)

### 8.1 Setup Cloudflare Tunnel (Free HTTPS)

See `DEPLOY_RUNPOD_SECURE.md` for full guide.

Quick steps:
1. Install cloudflared on RunPod
2. Create tunnel
3. Point domain to tunnel
4. Access via HTTPS (e.g., `https://developer.galion.app`)

### 8.2 Configure Firewall

```bash
# SSH into RunPod
ssh root@$env:RUNPOD_HOST -p $env:RUNPOD_PORT

# Setup firewall
apt install -y ufw
ufw allow $RUNPOD_PORT/tcp  # Your SSH port
ufw allow 8100/tcp          # Backend
ufw allow 3100/tcp          # Frontend
ufw --force enable
```

---

## Part 9: Manage Your Deployment

### Using Admin Control Script

```powershell
# Interactive menu
.\admin-control.ps1

# Or direct commands:
.\admin-control.ps1 -Action logs      # View logs
.\admin-control.ps1 -Action status    # Check status
.\admin-control.ps1 -Action restart   # Restart all
.\admin-control.ps1 -Action backup    # Backup database
.\admin-control.ps1 -Action sync      # Sync analytics
.\admin-control.ps1 -Action tunnel    # Open SSH tunnel
```

### Common Tasks

**View Logs**:
```powershell
.\admin-control.ps1 -Action logs
```

**Restart Services**:
```powershell
.\admin-control.ps1 -Action restart
```

**Backup Database**:
```powershell
.\admin-control.ps1 -Action backup
# Downloads to ./backups/ folder
```

**Update Code**:
```powershell
.\admin-control.ps1 -Action deploy
```

---

## Part 10: Cost Management

### Monitor Costs

**Check current charges**:
1. Go to RunPod dashboard
2. Click "Billing" → "Usage"
3. See hourly/daily breakdown

### Typical Costs

**On-Demand Pod** (4 vCPU, 16GB):
- Per hour: $0.20 - $0.40
- Per day (24h): $5 - $10
- Per month: $150 - $300

**Spot Instance** (same specs):
- Per hour: $0.10 - $0.20
- Per day (24h): $2.50 - $5
- Per month: $75 - $150

### Save Money

1. **Use Spot Instances**:
   - 50% cheaper
   - Can be interrupted (rare)
   - Good for development

2. **Stop When Not Using**:
   - Stop pod when not needed
   - Pay only when running
   - Restart anytime

3. **Choose Smaller Specs**:
   - 2 vCPU + 8GB RAM works too
   - Half the cost
   - Sufficient for moderate use

4. **Alternative: Hetzner**:
   - €5-10/month flat rate
   - Better for 24/7 production
   - See deployment guide

---

## 🎉 You're Done!

Your content management system is now running in the cloud!

### What You Can Do Now:

1. **Create Posts**:
   - Go to `/content-manager/compose`
   - Write content for multiple platforms
   - Schedule or publish immediately

2. **Connect Social Accounts**:
   - Go to `/content-manager/settings`
   - Connect Reddit, Twitter, LinkedIn, etc.
   - See `CONTENT_MANAGER_IMPLEMENTATION_COMPLETE.md` for OAuth setup

3. **View Analytics**:
   - Go to `/content-manager/analytics`
   - Track engagement across platforms

4. **Manage Remotely**:
   - Use `admin-control.ps1` from your local machine
   - No need to SSH manually

---

## 🆘 Troubleshooting

### Can't Connect to RunPod

**Check pod status**:
- Go to RunPod dashboard
- Ensure pod shows "Running" (green)
- If "Stopped", click "Start"

**Wrong credentials**:
- Double-check IP and port
- Try web terminal instead

### Services Won't Start

```powershell
# Check logs
.\admin-control.ps1 -Action logs

# Restart
.\admin-control.ps1 -Action restart
```

### Can't Access Frontend

**Check firewall**:
```bash
ssh root@$env:RUNPOD_HOST -p $env:RUNPOD_PORT
ufw status
# If inactive, run:
# ufw allow 3100/tcp
```

**Check service**:
```powershell
.\admin-control.ps1 -Action status
```

### Database Issues

```powershell
# Open database shell
.\admin-control.ps1 -Action db

# Check brands exist
# SELECT * FROM brands;
```

### Need Help?

- Check documentation: `v2/README_ADMIN.md`
- Review logs: `.\admin-control.ps1 -Action logs`
- Test locally first: `.\deploy-local.ps1`

---

## 📊 Quick Reference

| Task | Command |
|------|---------|
| Deploy | `.\deploy-to-runpod.ps1` |
| View logs | `.\admin-control.ps1 -Action logs` |
| Check status | `.\admin-control.ps1 -Action status` |
| Restart | `.\admin-control.ps1 -Action restart` |
| Backup | `.\admin-control.ps1 -Action backup` |
| Database shell | `.\admin-control.ps1 -Action db` |
| Open tunnel | `.\admin-control.ps1 -Action tunnel` |

**Your URLs**:
- Frontend: `http://YOUR_IP:3100`
- Backend: `http://YOUR_IP:8100`
- API Docs: `http://YOUR_IP:8100/docs`

---

**Deployment complete! Time to start posting! 🚀**

