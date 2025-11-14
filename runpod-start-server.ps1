# ============================================================================
# Galion Studio - RunPod Server Startup Script (PowerShell)
# ============================================================================
# Run this on your LOCAL Windows machine to connect to RunPod and start server

param(
    [string]$RunPodIP = "",
    [string]$Port = "8080"
)

Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "🚀 Galion Studio Backend - RunPod Remote Startup" -ForegroundColor Cyan
Write-Host "============================================================================`n" -ForegroundColor Cyan

if ([string]::IsNullOrEmpty($RunPodIP)) {
    Write-Host "❌ ERROR: RunPod IP address required" -ForegroundColor Red
    Write-Host "`nUsage:" -ForegroundColor Yellow
    Write-Host "  .\runpod-start-server.ps1 -RunPodIP YOUR_RUNPOD_IP" -ForegroundColor Yellow
    Write-Host "`nExample:" -ForegroundColor Yellow
    Write-Host "  .\runpod-start-server.ps1 -RunPodIP 123.45.67.89" -ForegroundColor Yellow
    exit 1
}

Write-Host "📍 Connecting to RunPod: $RunPodIP" -ForegroundColor Green

# Commands to run on RunPod
$commands = @"
# Navigate to project
cd /workspace/project-nexus

# Set environment
export PYTHONPATH=/workspace/project-nexus:/workspace/project-nexus/v2
export PORT=$Port
export HOST=0.0.0.0

# Kill existing server
pkill -f 'uvicorn.*$Port' || true

# Create log directory
mkdir -p /workspace/logs

# Start server
cd v2/backend
nohup python -m uvicorn main:app --host 0.0.0.0 --port $Port --workers 2 > /workspace/logs/galion-backend.log 2>&1 &

# Wait for startup
sleep 3

# Test health
curl -s http://localhost:$Port/health

echo ""
echo "✅ Server started on port $Port"
echo "📍 Access at: http://$RunPodIP:$Port"
echo "🔍 Health: http://$RunPodIP:$Port/health"
"@

Write-Host "`n📤 Sending startup commands to RunPod..." -ForegroundColor Yellow

# Note: This requires SSH access to RunPod
# Users should run these commands manually in their RunPod terminal

Write-Host "`n⚠️  Please run these commands in your RunPod terminal:" -ForegroundColor Yellow
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host $commands -ForegroundColor White
Write-Host "============================================================================" -ForegroundColor Cyan

Write-Host "`n💡 OR upload and run the bash script:" -ForegroundColor Yellow
Write-Host "   1. Upload runpod-start-server.sh to your RunPod pod" -ForegroundColor White
Write-Host "   2. Run: chmod +x runpod-start-server.sh" -ForegroundColor White
Write-Host "   3. Run: ./runpod-start-server.sh" -ForegroundColor White

Write-Host "`n🌐 After server starts, configure Cloudflare:" -ForegroundColor Green
Write-Host "   1. Go to Cloudflare Dashboard → galion.studio → DNS" -ForegroundColor White
Write-Host "   2. Add A record: @ → $RunPodIP (Proxy ON)" -ForegroundColor White
Write-Host "   3. SSL/TLS → Set to 'Flexible' or 'Full'" -ForegroundColor White
Write-Host "   4. Test: https://galion.studio/health" -ForegroundColor White

