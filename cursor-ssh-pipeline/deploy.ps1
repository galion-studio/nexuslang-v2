# ============================================
# Automated Deployment to RunPod
# ============================================
# One-command deployment from Cursor

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("all", "backend", "frontend", "services")]
    [string]$Target = "all",
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipBuild,
    
    [Parameter(Mandatory=$false)]
    [switch]$Restart
)

$ErrorActionPreference = "Stop"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  DEPLOYING TO RUNPOD" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Functions
function Write-Step { 
    param($step, $message)
    Write-Host "[$step] " -NoNewline -ForegroundColor Blue
    Write-Host "$message" -ForegroundColor White
}

function Write-Success { Write-Host "✓ $args" -ForegroundColor Green }
function Write-Error { Write-Host "✗ $args" -ForegroundColor Red }
function Write-Info { Write-Host "ℹ $args" -ForegroundColor Cyan }

# Check SSH connection
Write-Step "1/6" "Testing SSH connection..."
$testResult = & ssh -o ConnectTimeout=5 runpod "echo 'connected'" 2>&1
if ($testResult -match "connected") {
    Write-Success "SSH connection verified"
} else {
    Write-Error "Cannot connect to RunPod. Run setup-local-ssh.ps1 first"
    exit 1
}

# Pull latest code
Write-Step "2/6" "Pulling latest code from GitHub..."
$pullCommand = @"
cd /nexuslang-v2 && \
git fetch origin && \
git checkout clean-nexuslang && \
git pull origin clean-nexuslang
"@

& ssh runpod "$pullCommand"
if ($LASTEXITCODE -eq 0) {
    Write-Success "Code updated"
} else {
    Write-Error "Failed to pull code"
    exit 1
}

# Install dependencies
Write-Step "3/6" "Installing dependencies..."
$depsCommand = @"
cd /nexuslang-v2 && \
pip3 install -q fastapi uvicorn psutil pydantic python-multipart && \
echo 'Backend dependencies installed' && \
for app in galion-studio galion-app developer-platform; do
    if [ -d "\$app" ]; then
        echo "Installing \$app dependencies..."
        cd "\$app" && npm install --silent && cd ..
    fi
done
"@

& ssh runpod "$depsCommand"
if ($LASTEXITCODE -eq 0) {
    Write-Success "Dependencies installed"
} else {
    Write-Error "Failed to install dependencies"
}

# Build frontend (if not skipped)
if (-not $SkipBuild -and ($Target -eq "all" -or $Target -eq "frontend")) {
    Write-Step "4/6" "Building frontend applications..."
    $buildCommand = @"
cd /nexuslang-v2 && \
for app in galion-studio galion-app developer-platform; do
    if [ -d "\$app" ]; then
        echo "Building \$app..."
        cd "\$app" && npm run build && cd ..
    fi
done
"@
    
    & ssh runpod "$buildCommand"
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Frontend built"
    } else {
        Write-Error "Frontend build failed (continuing anyway...)"
    }
} else {
    Write-Info "Skipping frontend build"
}

# Stop services
Write-Step "5/6" "Restarting services..."
$stopCommand = @"
pm2 delete all 2>/dev/null || true
"@

& ssh runpod "$stopCommand" | Out-Null

# Start services
$startCommand = @"
cd /nexuslang-v2 && \
echo 'Starting backend...' && \
cd v2/backend && pm2 start python3 --name galion-backend -- main_simple.py --host 0.0.0.0 --port 8000 && cd ../.. && \
echo 'Starting frontends...' && \
cd galion-studio && pm2 start npm --name galion-studio -- run dev -- -p 3001 && cd .. && \
cd galion-app && pm2 start npm --name galion-app -- run dev -- -p 3003 && cd .. && \
if [ -d 'developer-platform' ]; then cd developer-platform && pm2 start npm --name developer-platform -- run dev -- -p 3002 && cd ..; fi && \
pm2 save && \
echo 'Services started'
"@

& ssh runpod "$startCommand"
if ($LASTEXITCODE -eq 0) {
    Write-Success "Services started"
} else {
    Write-Error "Failed to start services"
    exit 1
}

# Verify deployment
Write-Step "6/6" "Verifying deployment..."
Start-Sleep -Seconds 5

$statusCommand = @"
pm2 status && \
echo '' && \
echo 'Testing backend...' && \
curl -s http://localhost:8000/health | head -c 100
"@

& ssh runpod "$statusCommand"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Success "Deployment complete!"
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Info "To view logs: .\remote-exec.ps1 'pm2 logs'"
Write-Info "To check status: .\remote-exec.ps1 'pm2 status'"
Write-Host ""

