# ============================================
# Remote Execution Script for RunPod
# ============================================
# Execute commands on RunPod from local machine

param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$Command,
    
    [Parameter(Mandatory=$false)]
    [string]$WorkDir = "/nexuslang-v2",
    
    [Parameter(Mandatory=$false)]
    [switch]$Silent,
    
    [Parameter(Mandatory=$false)]
    [switch]$Interactive
)

$ErrorActionPreference = "Continue"

# Check if SSH is configured
if (-not (Test-Path "$env:USERPROFILE\.ssh\config")) {
    Write-Host "✗ SSH not configured. Run setup-local-ssh.ps1 first" -ForegroundColor Red
    exit 1
}

# Build SSH command
$sshCmd = "ssh runpod"

if ($Interactive) {
    # Interactive mode - open shell in working directory
    $remoteCmd = "cd $WorkDir && bash"
} else {
    # Execute command
    $remoteCmd = "cd $WorkDir && $Command"
}

if (-not $Silent) {
    Write-Host "→ Executing on RunPod: " -NoNewline -ForegroundColor Blue
    Write-Host "$Command" -ForegroundColor White
    Write-Host ""
}

# Execute
& ssh runpod $remoteCmd

if ($LASTEXITCODE -eq 0 -and -not $Silent) {
    Write-Host ""
    Write-Host "✓ Command completed successfully" -ForegroundColor Green
} elseif ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "✗ Command failed with exit code $LASTEXITCODE" -ForegroundColor Red
    exit $LASTEXITCODE
}

