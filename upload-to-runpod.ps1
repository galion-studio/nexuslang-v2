# Automatic Upload to RunPod via SSH
# This script will upload your project directly to RunPod

Write-Host ""
Write-Host "📤 Uploading to RunPod..." -ForegroundColor Cyan
Write-Host ""

# Configuration - UPDATE THESE
$RUNPOD_HOST = "YOUR_POD_ID.proxy.runpod.net"  # Get from RunPod dashboard
$RUNPOD_PORT = "22"  # SSH port (usually exposed)
$RUNPOD_USER = "root"

Write-Host "⚙️  Configuration:" -ForegroundColor Yellow
Write-Host "   Host: $RUNPOD_HOST"
Write-Host "   Port: $RUNPOD_PORT"
Write-Host ""

# Check if SSH key exists
$sshKeyPath = "$env:USERPROFILE\.ssh\id_rsa"
if (-not (Test-Path $sshKeyPath)) {
    Write-Host "❌ SSH key not found at: $sshKeyPath" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please add your SSH key or use password authentication"
    exit 1
}

# Create temp deployment folder
$deployFolder = ".\deploy-temp"
if (Test-Path $deployFolder) {
    Remove-Item $deployFolder -Recurse -Force
}
New-Item -ItemType Directory -Path $deployFolder | Out-Null

Write-Host "📦 Preparing files..." -ForegroundColor Yellow

# Copy essential files only
Write-Host "   Copying v2/backend..." -ForegroundColor Gray
robocopy "v2\backend" "$deployFolder\v2\backend" /E /XD __pycache__ .pytest_cache /XF *.pyc /NFL /NDL /NJH /NJS | Out-Null

Write-Host "   Copying v2/frontend..." -ForegroundColor Gray
robocopy "v2\frontend" "$deployFolder\v2\frontend" /E /XD node_modules .next /NFL /NDL /NJH /NJS | Out-Null

Write-Host "   Copying configs..." -ForegroundColor Gray
Copy-Item "docker-compose.yml" $deployFolder -ErrorAction SilentlyContinue
Copy-Item "docker-compose.runpod.yml" $deployFolder -ErrorAction SilentlyContinue
Copy-Item ".env" $deployFolder -ErrorAction SilentlyContinue
Copy-Item "runpod-quick-deploy.sh" $deployFolder -ErrorAction SilentlyContinue
Copy-Item "*.md" $deployFolder -ErrorAction SilentlyContinue

Write-Host "✅ Files prepared" -ForegroundColor Green
Write-Host ""
Write-Host "📤 Uploading to RunPod..." -ForegroundColor Yellow
Write-Host "   This may take a few minutes..." -ForegroundColor Gray
Write-Host ""

# Upload using SCP
$scpCommand = "scp -r -P $RUNPOD_PORT $deployFolder\* ${RUNPOD_USER}@${RUNPOD_HOST}:/workspace/nexuslang-v2/"

Write-Host "Running: $scpCommand" -ForegroundColor Gray
Write-Host ""

try {
    # Create directory on RunPod first
    ssh -p $RUNPOD_PORT ${RUNPOD_USER}@${RUNPOD_HOST} "mkdir -p /workspace/nexuslang-v2"
    
    # Upload files
    scp -r -P $RUNPOD_PORT "$deployFolder\*" "${RUNPOD_USER}@${RUNPOD_HOST}:/workspace/nexuslang-v2/"
    
    Write-Host ""
    Write-Host "✅ Upload complete!" -ForegroundColor Green
    
    # Run deployment script remotely
    Write-Host ""
    Write-Host "🚀 Running deployment on RunPod..." -ForegroundColor Cyan
    ssh -p $RUNPOD_PORT ${RUNPOD_USER}@${RUNPOD_HOST} "cd /workspace/nexuslang-v2 && chmod +x *.sh && ./runpod-quick-deploy.sh"
    
} catch {
    Write-Host "❌ Upload failed: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Try manual upload method instead (see UPLOAD_TO_RUNPOD_JUPYTER.md)"
}

# Cleanup
Remove-Item $deployFolder -Recurse -Force

Write-Host ""
Write-Host "✨ Done!" -ForegroundColor Green
