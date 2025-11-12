# Interactive RunPod Setup Helper
# Guides you through getting RunPod credentials and deploying

Write-Host ""
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "  RunPod Setup & Deployment Helper" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "This script will guide you through:" -ForegroundColor Yellow
Write-Host "  1. Getting RunPod credentials"
Write-Host "  2. Configuring SSH access"
Write-Host "  3. Deploying your system"
Write-Host ""

# Step 1: Check if credentials are already set
Write-Host "[Step 1] Checking for existing RunPod credentials..." -ForegroundColor Yellow
Write-Host ""

if ($env:RUNPOD_HOST -and $env:RUNPOD_PORT) {
    Write-Host "Found existing credentials:" -ForegroundColor Green
    Write-Host "  Host: $env:RUNPOD_HOST"
    Write-Host "  Port: $env:RUNPOD_PORT"
    Write-Host ""
    $useExisting = Read-Host "Use these credentials? (Y/n)"
    
    if ($useExisting -eq "n" -or $useExisting -eq "N") {
        $env:RUNPOD_HOST = $null
        $env:RUNPOD_PORT = $null
    }
}

# Step 2: Get credentials if not set
if (-not $env:RUNPOD_HOST -or -not $env:RUNPOD_PORT) {
    Write-Host ""
    Write-Host "[Step 2] Let's get your RunPod credentials!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Do you have a RunPod account? (Y/n)" -ForegroundColor Cyan
    $hasAccount = Read-Host
    
    if ($hasAccount -eq "n" -or $hasAccount -eq "N") {
        Write-Host ""
        Write-Host "Let's create one:" -ForegroundColor Green
        Write-Host "  1. Open: https://runpod.io"
        Write-Host "  2. Click 'Sign Up'"
        Write-Host "  3. Complete registration"
        Write-Host "  4. Add payment method (Billing -> Add Payment)"
        Write-Host ""
        Write-Host "Press Enter when you've created your account..."
        Read-Host
    }
    
    Write-Host ""
    Write-Host "Do you have a running Pod? (Y/n)" -ForegroundColor Cyan
    $hasPod = Read-Host
    
    if ($hasPod -eq "n" -or $hasPod -eq "N") {
        Write-Host ""
        Write-Host "Let's deploy a Pod:" -ForegroundColor Green
        Write-Host "  1. Go to RunPod dashboard"
        Write-Host "  2. Click 'Deploy' or 'GPU Pods'"
        Write-Host "  3. Choose template: 'Ubuntu 22.04'"
        Write-Host "  4. Uncheck 'GPU' (not needed)"
        Write-Host "  5. Select specs:"
        Write-Host "     - CPU: 4+ vCPUs"
        Write-Host "     - RAM: 16GB+"
        Write-Host "     - Storage: 50GB+"
        Write-Host "  6. Click 'Deploy On-Demand'"
        Write-Host "  7. Wait 30-60 seconds for pod to start"
        Write-Host ""
        Write-Host "Press Enter when your pod is running (green status)..."
        Read-Host
    }
    
    Write-Host ""
    Write-Host "Now let's get your SSH credentials:" -ForegroundColor Yellow
    Write-Host "  1. Click on your pod in RunPod dashboard"
    Write-Host "  2. Find the 'Connect' section"
    Write-Host "  3. You'll see an SSH command like:"
    Write-Host "     ssh root@12.345.67.89 -p 12345 -i ~/.ssh/id_ed25519"
    Write-Host ""
    Write-Host "Enter your RunPod IP address:" -ForegroundColor Cyan
    Write-Host "(Example: 12.345.67.89)" -ForegroundColor Gray
    $runpodHost = Read-Host
    
    Write-Host ""
    Write-Host "Enter your RunPod SSH port:" -ForegroundColor Cyan
    Write-Host "(Example: 12345)" -ForegroundColor Gray
    $runpodPort = Read-Host
    
    # Save credentials
    $env:RUNPOD_HOST = $runpodHost
    $env:RUNPOD_PORT = $runpodPort
    
    Write-Host ""
    Write-Host "Save these credentials permanently? (Y/n)" -ForegroundColor Cyan
    $savePerm = Read-Host
    
    if ($savePerm -ne "n" -and $savePerm -ne "N") {
        [Environment]::SetEnvironmentVariable("RUNPOD_HOST", $runpodHost, "User")
        [Environment]::SetEnvironmentVariable("RUNPOD_PORT", $runpodPort, "User")
        Write-Host "Credentials saved!" -ForegroundColor Green
    }
}

# Step 3: Test SSH connection
Write-Host ""
Write-Host "[Step 3] Testing SSH connection..." -ForegroundColor Yellow
Write-Host ""

Write-Host "Checking if SSH keys exist..." -ForegroundColor Gray
if (-not (Test-Path "~/.ssh/id_ed25519") -and -not (Test-Path "~/.ssh/id_rsa")) {
    Write-Host ""
    Write-Host "No SSH keys found. Let's create one:" -ForegroundColor Yellow
    Write-Host ""
    $email = Read-Host "Enter your email for SSH key"
    
    ssh-keygen -t ed25519 -C $email
    
    Write-Host ""
    Write-Host "Key generated! Now add it to RunPod:" -ForegroundColor Green
    Write-Host "  1. Copy your public key (it's now in clipboard)"
    Get-Content ~/.ssh/id_ed25519.pub | Set-Clipboard
    Write-Host "  2. Go to RunPod -> Settings -> SSH Keys"
    Write-Host "  3. Click 'Add SSH Key'"
    Write-Host "  4. Paste and save"
    Write-Host "  5. Restart your pod"
    Write-Host ""
    Write-Host "Press Enter when you've added the key and restarted..."
    Read-Host
}

Write-Host "Testing connection to $env:RUNPOD_HOST`:$env:RUNPOD_PORT..." -ForegroundColor Gray
$testResult = ssh -p $env:RUNPOD_PORT -o ConnectTimeout=10 -o StrictHostKeyChecking=no "root@$env:RUNPOD_HOST" "echo 'Connection successful'" 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "SUCCESS: SSH connection working!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "WARNING: SSH connection failed" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Try using RunPod's Web Terminal instead:" -ForegroundColor Cyan
    Write-Host "  1. Go to your pod in RunPod dashboard"
    Write-Host "  2. Click 'Web Terminal' or 'Terminal'"
    Write-Host "  3. This opens a browser-based terminal"
    Write-Host ""
    Write-Host "Would you like to continue with Web Terminal? (Y/n)" -ForegroundColor Cyan
    $useWebTerminal = Read-Host
    
    if ($useWebTerminal -eq "n" -or $useWebTerminal -eq "N") {
        Write-Host "Setup paused. Fix SSH and run this script again." -ForegroundColor Yellow
        exit 1
    }
    
    Write-Host ""
    Write-Host "Using Web Terminal:" -ForegroundColor Green
    Write-Host "  1. Open Web Terminal in RunPod"
    Write-Host "  2. Run these commands:"
    Write-Host ""
    Write-Host "cd ~" -ForegroundColor White
    Write-Host "git clone https://github.com/yourusername/project-nexus.git" -ForegroundColor White
    Write-Host "cd project-nexus/v2" -ForegroundColor White
    Write-Host "bash deploy-to-runpod.sh" -ForegroundColor White
    Write-Host ""
    Write-Host "Press Enter when deployment completes in Web Terminal..."
    Read-Host
    
    Write-Host ""
    Write-Host "Deployment should be complete!" -ForegroundColor Green
    Write-Host "Access your system at: http://$env:RUNPOD_HOST`:3100"
    exit 0
}

# Step 4: Deploy
Write-Host ""
Write-Host "[Step 4] Ready to deploy!" -ForegroundColor Yellow
Write-Host ""
Write-Host "This will:" -ForegroundColor Cyan
Write-Host "  - Clone/update code on RunPod"
Write-Host "  - Install Docker and dependencies"
Write-Host "  - Start all services"
Write-Host "  - Initialize database with 4 brands"
Write-Host "  - Verify everything is working"
Write-Host ""
Write-Host "Estimated time: 10 minutes" -ForegroundColor Gray
Write-Host ""

$deploy = Read-Host "Start deployment now? (Y/n)"

if ($deploy -eq "n" -or $deploy -eq "N") {
    Write-Host ""
    Write-Host "Setup paused. Run this command to deploy:" -ForegroundColor Yellow
    Write-Host "  .\deploy-to-runpod.ps1"
    exit 0
}

Write-Host ""
Write-Host "======================================================" -ForegroundColor Green
Write-Host "  Starting Deployment..." -ForegroundColor Green
Write-Host "======================================================" -ForegroundColor Green
Write-Host ""

# Run deployment script
.\deploy-to-runpod.ps1

Write-Host ""
Write-Host "======================================================" -ForegroundColor Green
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "======================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Your system is now running in the cloud!" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access URLs:" -ForegroundColor Yellow
Write-Host "  Frontend: http://$env:RUNPOD_HOST`:3100"
Write-Host "  Backend:  http://$env:RUNPOD_HOST`:8100"
Write-Host "  API Docs: http://$env:RUNPOD_HOST`:8100/docs"
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Open frontend in browser"
Write-Host "  2. Register your first user"
Write-Host "  3. Go to /content-manager/compose"
Write-Host "  4. Create your first post!"
Write-Host ""

$openNow = Read-Host "Open frontend now? (Y/n)"
if ($openNow -ne "n" -and $openNow -ne "N") {
    Start-Process "http://$env:RUNPOD_HOST`:3100"
}

