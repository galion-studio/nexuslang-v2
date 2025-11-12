# 🚀 RunPod Setup Guide

## How to Get RunPod Credentials

### Step 1: Create RunPod Account
1. Go to https://runpod.io
2. Sign up or log in
3. Add payment method

### Step 2: Deploy a Pod
1. Click "Deploy" or "GPU Pods"
2. Select a template:
   - **Recommended**: "RunPod PyTorch" or "Ubuntu 22.04"
   - **GPU**: Not required (optional)
   - **CPU**: 4+ vCPUs
   - **RAM**: 16GB+
   - **Storage**: 50GB+

3. Click "Deploy On-Demand" or "Deploy Spot"

### Step 3: Get SSH Credentials
Once your pod is running:

1. Click on your pod
2. Find "Connect" section
3. Copy the SSH command, it looks like:
   ```
   ssh root@12.345.67.89 -p 12345 -i ~/.ssh/id_ed25519
   ```

4. Extract:
   - **RUNPOD_HOST**: `12.345.67.89` (the IP address)
   - **RUNPOD_PORT**: `12345` (the port number)

### Step 4: Configure SSH Keys (If Needed)

If you don't have SSH keys:

```powershell
# Generate SSH key
ssh-keygen -t ed25519 -C "your-email@example.com"

# Add to RunPod
# Copy your public key
Get-Content ~/.ssh/id_ed25519.pub | clip

# Go to RunPod → Settings → SSH Keys
# Paste and save
```

### Step 5: Set Environment Variables

```powershell
# Windows PowerShell
$env:RUNPOD_HOST = "12.345.67.89"
$env:RUNPOD_PORT = "12345"

# Save permanently (optional)
[Environment]::SetEnvironmentVariable("RUNPOD_HOST", "12.345.67.89", "User")
[Environment]::SetEnvironmentVariable("RUNPOD_PORT", "12345", "User")
```

```bash
# Linux/Mac
export RUNPOD_HOST="12.345.67.89"
export RUNPOD_PORT="12345"

# Save permanently (add to ~/.bashrc or ~/.zshrc)
echo 'export RUNPOD_HOST="12.345.67.89"' >> ~/.bashrc
echo 'export RUNPOD_PORT="12345"' >> ~/.bashrc
```

### Step 6: Test Connection

```powershell
# Test SSH
ssh root@$env:RUNPOD_HOST -p $env:RUNPOD_PORT
```

If successful, you can now deploy!

---

## Deploy to RunPod

Once credentials are set:

```powershell
cd v2
.\deploy-to-runpod.ps1
```

---

## Cost Estimate

**On-Demand Pod** (4 vCPU, 16GB RAM):
- ~$0.20 - $0.40 per hour
- ~$5 - $10 per day
- ~$150 - $300 per month

**Spot Instance** (same specs):
- ~$0.10 - $0.20 per hour
- ~$2.50 - $5 per day
- ~$75 - $150 per month

💡 **Tip**: Use Spot instances for development, On-Demand for production

---

## Alternatives to RunPod

If you don't want to use RunPod, you can deploy to:

### Option 1: Deploy Locally (Free)
```powershell
cd v2
.\deploy-local.ps1
```

### Option 2: Other VPS Providers
- **DigitalOcean**: $12-24/month droplets
- **Linode**: $12-24/month instances
- **Hetzner**: €5-10/month VPS
- **AWS EC2**: Various pricing
- **Google Cloud**: Various pricing

Use the same deploy script with any SSH-accessible server!

---

## Quick Start: No RunPod Required

Test locally first:

```powershell
# 1. Install Docker Desktop
# Download from: https://www.docker.com/products/docker-desktop

# 2. Deploy locally
cd v2
.\deploy-local.ps1

# 3. Open in browser
Start-Process http://localhost:3100
```

---

## Troubleshooting

### Can't connect to RunPod
- Check pod is running in RunPod dashboard
- Verify SSH port is correct
- Check firewall settings
- Try web-based SSH from RunPod dashboard

### SSH key issues
- Make sure key is in `~/.ssh/`
- Check key permissions: `chmod 600 ~/.ssh/id_ed25519`
- Add key to ssh-agent: `ssh-add ~/.ssh/id_ed25519`

### Pod is expensive
- Use Spot instances instead of On-Demand
- Choose lower specs (2 vCPU, 8GB RAM works too)
- Stop pod when not in use
- Consider alternatives like Hetzner or DigitalOcean

---

## Summary

**With RunPod**:
1. Create account → Deploy pod → Get IP/Port
2. Set environment variables
3. Run: `.\deploy-to-runpod.ps1`

**Without RunPod**:
1. Install Docker Desktop
2. Run: `.\deploy-local.ps1`
3. Access at `http://localhost:3100`

Both options give you the full content management system!

