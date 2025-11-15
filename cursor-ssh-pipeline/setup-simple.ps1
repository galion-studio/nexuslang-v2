# ============================================
# Simple SSH Setup for RunPod (No Dependencies)
# ============================================

param(
    [Parameter(Mandatory=$true)]
    [string]$RunPodIP,
    
    [Parameter(Mandatory=$false)]
    [string]$SSHKeyPath = "$env:USERPROFILE\.ssh\id_ed25519"
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  SSH PIPELINE SETUP FOR RUNPOD" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check SSH directory
Write-Host "Step 1: Checking SSH directory..." -ForegroundColor Blue
$sshDir = "$env:USERPROFILE\.ssh"
if (-not (Test-Path $sshDir)) {
    Write-Host "[!] Creating .ssh directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $sshDir -Force | Out-Null
    Write-Host "[+] Created $sshDir" -ForegroundColor Green
} else {
    Write-Host "[+] SSH directory exists" -ForegroundColor Green
}

# Step 2: Check SSH key
Write-Host ""
Write-Host "Step 2: Checking SSH key..." -ForegroundColor Blue
if (-not (Test-Path $SSHKeyPath)) {
    Write-Host "[!] SSH key not found at $SSHKeyPath" -ForegroundColor Yellow
    Write-Host "[i] Generating new SSH key..." -ForegroundColor Blue
    
    $hostname = $env:COMPUTERNAME
    & ssh-keygen -t ed25519 -f $SSHKeyPath -N '""' -C "galion-pipeline-$hostname"
    
    if (Test-Path $SSHKeyPath) {
        Write-Host "[+] SSH key generated successfully" -ForegroundColor Green
    } else {
        Write-Host "[-] Failed to generate SSH key" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[+] SSH key found at $SSHKeyPath" -ForegroundColor Green
}

# Step 3: Create SSH config
Write-Host ""
Write-Host "Step 3: Configuring SSH..." -ForegroundColor Blue
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

# Backup existing config if it has runpod entry
if (Test-Path $sshConfigPath) {
    $existingConfig = Get-Content $sshConfigPath -Raw
    if ($existingConfig -match 'Host runpod') {
        Write-Host "[!] RunPod config already exists, backing up..." -ForegroundColor Yellow
        $backupName = "$sshConfigPath.backup.$(Get-Date -Format 'yyyyMMdd-HHmmss')"
        Copy-Item $sshConfigPath $backupName
        Write-Host "[+] Backup created" -ForegroundColor Green
    }
}

Add-Content -Path $sshConfigPath -Value $configContent
Write-Host "[+] SSH config updated" -ForegroundColor Green

# Step 4: Display public key
Write-Host ""
Write-Host "Step 4: Your public key..." -ForegroundColor Blue
$publicKeyPath = "$SSHKeyPath.pub"
if (Test-Path $publicKeyPath) {
    $publicKey = Get-Content $publicKeyPath -Raw
    Write-Host "[+] Public key ready" -ForegroundColor Green
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Yellow
    Write-Host "  PUBLIC KEY (copy this):" -ForegroundColor Yellow
    Write-Host "============================================" -ForegroundColor Yellow
    Write-Host $publicKey -ForegroundColor White
    Write-Host "============================================" -ForegroundColor Yellow
} else {
    Write-Host "[-] Public key not found" -ForegroundColor Red
    exit 1
}

# Step 5: Instructions
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  NEXT STEPS:" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Copy the public key above" -ForegroundColor White
Write-Host ""
Write-Host "2. In your RunPod terminal, run:" -ForegroundColor White
Write-Host ""
$runpodCommand = "mkdir -p ~/.ssh && echo '$publicKey' >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
Write-Host "   $runpodCommand" -ForegroundColor Green
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

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$connectionInfo | ConvertTo-Json | Out-File "$scriptDir\connection-info.json"
Write-Host "[+] Connection info saved to connection-info.json" -ForegroundColor Green

Write-Host ""
Write-Host "[+] SSH pipeline setup complete!" -ForegroundColor Green
Write-Host ""

