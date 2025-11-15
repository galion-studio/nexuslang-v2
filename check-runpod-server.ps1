# ============================================
# RunPod Server Health Check Script
# ============================================
# PowerShell script to check Galion Platform server status

param(
    [string]$RunPodIP = "213.173.105.83",
    [string]$SSHKey = "$env:USERPROFILE\.ssh\id_ed25519"
)

Write-Host "🔍 Galion Platform - RunPod Server Health Check" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host ""

# Check if SSH key exists
if (-not (Test-Path $SSHKey)) {
    Write-Host "❌ SSH key not found at: $SSHKey" -ForegroundColor Red
    Write-Host "Please ensure your SSH key is set up for RunPod access." -ForegroundColor Yellow
    exit 1
}

Write-Host "📋 Manual commands to run on RunPod server:" -ForegroundColor Green
Write-Host "-" * 40 -ForegroundColor Green

Write-Host ""
Write-Host "1️⃣ SSH into RunPod server:" -ForegroundColor Yellow
Write-Host "   ssh -i $SSHKey root@$RunPodIP" -ForegroundColor White
Write-Host ""

Write-Host "2️⃣ Once connected, run these health checks:" -ForegroundColor Yellow
Write-Host ""

Write-Host "   # Check PM2 services" -ForegroundColor Gray
Write-Host "   pm2 status" -ForegroundColor White
Write-Host ""

Write-Host "   # Check system resources" -ForegroundColor Gray
Write-Host "   free -h && df -h" -ForegroundColor White
Write-Host ""

Write-Host "   # Check nginx" -ForegroundColor Gray
Write-Host "   systemctl status nginx" -ForegroundColor White
Write-Host ""

Write-Host "   # Test backend API" -ForegroundColor Gray
Write-Host "   curl -s http://localhost:8000/health | jq" -ForegroundColor White
Write-Host ""

Write-Host "   # Test all services" -ForegroundColor Gray
Write-Host "   curl -s http://localhost:3030 | head -5" -ForegroundColor White
Write-Host "   curl -s http://localhost:3000 | head -5" -ForegroundColor White
Write-Host "   curl -s http://localhost:3003 | head -5" -ForegroundColor White
Write-Host ""

Write-Host "   # Check for errors" -ForegroundColor Gray
Write-Host "   pm2 logs --lines 10 --err" -ForegroundColor White
Write-Host ""

Write-Host "3️⃣ Or run the comprehensive check script:" -ForegroundColor Yellow
Write-Host "   wget -O - https://raw.githubusercontent.com/galion-studio/nexuslang-v2/clean-nexuslang/test-all-services-v2.sh | bash" -ForegroundColor White
Write-Host ""

Write-Host "4️⃣ Alternative: Download and run manual check:" -ForegroundColor Yellow
Write-Host "   wget https://raw.githubusercontent.com/galion-studio/nexuslang-v2/clean-nexuslang/manual-server-check.sh" -ForegroundColor White
Write-Host "   chmod +x manual-server-check.sh" -ForegroundColor White
Write-Host "   ./manual-server-check.sh" -ForegroundColor White
Write-Host ""

Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host "💡 Pro tip: Copy these commands and paste them in your SSH session!" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Cyan
