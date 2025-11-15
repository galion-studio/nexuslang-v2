# ============================================
# Setup SSH Connection from Local Machine to RunPod
# ============================================
# This script configures your local machine for seamless SSH access

param(
    [Parameter(Mandatory=$true)]
    [string]$RunPodIP,
    
    [Parameter(Mandatory=$false)]
    [string]$SSHKeyPath = "$env:USERPROFILE\.ssh\id_ed25519"
)

$ErrorActionPreference = "Stop"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  SSH PIPELINE SETUP FOR RUNPOD" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Helper functions
function Write-Success { 
    param($message)
    Write-Host "✓ $message" -ForegroundColor Green 
}

function Write-Error { 
    param($message)
    Write-Host "✗ $message" -ForegroundColor Red 
}

function Write-Info { 
    param($message)
    Write-Host "ℹ $message" -ForegroundColor Blue 
}

function Write-Warning { 
    param($message)
    Write-Host "⚠ $message" -ForegroundColor Yellow 
}

# Step 1: Check SSH directory
Write-Info "Step 1: Checking SSH directory..."
$sshDir = "$env:USERPROFILE\.ssh"
if (-not (Test-Path $sshDir)) {
    Write-Warning "Creating .ssh directory..."
    New-Item -ItemType Directory -Path $sshDir -Force | Out-Null
    Write-Success "Created $sshDir"
} else {
    Write-Success "SSH directory exists"
}

# Step 2: Check SSH key
Write-Info "Step 2: Checking SSH key..."
if (-not (Test-Path $SSHKeyPath)) {
    Write-Warning "SSH key not found at $SSHKeyPath"
    Write-Info "Generating new SSH key..."
    
    ssh-keygen -t ed25519 -f $SSHKeyPath -N '""' -C "galion-pipeline-$(hostname)"
    
    if (Test-Path $SSHKeyPath) {
        Write-Success "SSH key generated successfully"
    } else {
        Write-Error "Failed to generate SSH key"
        exit 1
    }
} else {
    Write-Success "SSH key found at $SSHKeyPath"
}

# Step 3: Create SSH config
Write-Info "Step 3: Configuring SSH..."
$sshConfigPath = "$sshDir\config"
$configContent = @"

# ============================================
# RunPod Configuration - Added by Galion Pipeline
# ============================================

Host runpod
    HostName $RunPodIP
    User root
    Port 22
    IdentityFile $($SSHKeyPath -replace '\\', '/')
    StrictHostKeyChecking no
    UserKnownHostsFile NUL
    ServerAliveInterval 60
    ServerAliveCountMax 3
    ForwardAgent yes

Host runpod-tunnel
    HostName $RunPodIP
    User root
    Port 22
    IdentityFile $($SSHKeyPath -replace '\\', '/')
    LocalForward 8000 localhost:8000
    LocalForward 3001 localhost:3001
    LocalForward 3002 localhost:3002
    LocalForward 3003 localhost:3003
    LocalForward 80 localhost:80
    StrictHostKeyChecking no
    UserKnownHostsFile NUL
    ServerAliveInterval 60
    ServerAliveCountMax 3

"@

# Check if config already has runpod entry
if (Test-Path $sshConfigPath) {
    $existingConfig = Get-Content $sshConfigPath -Raw
    if ($existingConfig -match "Host runpod") {
        Write-Warning "RunPod config already exists, backing up..."
        Copy-Item $sshConfigPath "$sshConfigPath.backup.$(Get-Date -Format 'yyyyMMdd-HHmmss')"
        Write-Success "Backup created"
    }
}

Add-Content -Path $sshConfigPath -Value $configContent
Write-Success "SSH config updated"

# Step 4: Copy public key
Write-Info "Step 4: Preparing public key..."
$publicKeyPath = "$SSHKeyPath.pub"
if (Test-Path $publicKeyPath) {
    $publicKey = Get-Content $publicKeyPath -Raw
    Write-Success "Public key ready"
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Yellow
    Write-Host "  PUBLIC KEY (copy this):" -ForegroundColor Yellow
    Write-Host "============================================" -ForegroundColor Yellow
    Write-Host $publicKey -ForegroundColor White
    Write-Host "============================================" -ForegroundColor Yellow
} else {
    Write-Error "Public key not found"
    exit 1
}

# Step 5: Instructions for RunPod
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  NEXT STEPS:" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Copy the public key above" -ForegroundColor White
Write-Host ""
Write-Host "2. In your RunPod terminal, run:" -ForegroundColor White
Write-Host ""
Write-Host "   mkdir -p ~/.ssh && echo '$publicKey' >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys" -ForegroundColor Green
Write-Host ""
Write-Host "3. Test connection from this machine:" -ForegroundColor White
Write-Host ""
Write-Host "   ssh runpod" -ForegroundColor Green
Write-Host ""
Write-Host "4. Start tunnel for all services:" -ForegroundColor White
Write-Host ""
Write-Host "   ssh runpod-tunnel -N" -ForegroundColor Green
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Save connection info
$connectionInfo = @{
    RunPodIP = $RunPodIP
    SSHKeyPath = $SSHKeyPath
    PublicKey = $publicKey
    ConfiguredAt = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
}

$connectionInfo | ConvertTo-Json | Out-File "$PSScriptRoot\connection-info.json"
Write-Success "Connection info saved to connection-info.json"

Write-Host ""
Write-Success "SSH pipeline setup complete!"
Write-Host ""

