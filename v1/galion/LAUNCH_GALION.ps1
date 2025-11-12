# GALION.APP Launch Script
# Following Elon Musk's First Principles

Write-Host "🚀 GALION.APP - LAUNCH SEQUENCE" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Backend
Write-Host "Step 1: Checking Backend Services..." -ForegroundColor Yellow
cd C:\Users\Gigabyte\Documents\project-nexus
$services = docker-compose ps --services
if ($services) {
    Write-Host "✅ Backend services running" -ForegroundColor Green
} else {
    Write-Host "⚠️  Starting backend services..." -ForegroundColor Yellow
    docker-compose up -d
    Start-Sleep -Seconds 10
}

# Step 2: Launch Frontend
Write-Host ""
Write-Host "Step 2: Starting Frontend..." -ForegroundColor Yellow
cd frontend

# Check if already running
$port3000 = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue
if ($port3000) {
    Write-Host "✅ Frontend already running on port 3000" -ForegroundColor Green
} else {
    Write-Host "🚀 Starting production server..." -ForegroundColor Cyan
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\Users\Gigabyte\Documents\project-nexus\frontend; npm start"
    Start-Sleep -Seconds 5
}

# Step 3: Display Access Info
Write-Host ""
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host "✅ GALION.APP IS LIVE!" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host ""
Write-Host "🌐 ACCESS:" -ForegroundColor Yellow
Write-Host "   http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "🔑 CEO ADMIN LOGIN:" -ForegroundColor Yellow
Write-Host "   Email:    info@galion.studio" -ForegroundColor White
Write-Host "   Password: Admin123!" -ForegroundColor White
Write-Host "   Role:     CEO / Full Control" -ForegroundColor White
Write-Host ""
Write-Host "📊 BACKEND SERVICES:" -ForegroundColor Yellow
Write-Host "   API Gateway:  http://localhost:8080" -ForegroundColor White
Write-Host "   Grafana:      http://localhost:9300" -ForegroundColor White
Write-Host "   Prometheus:   http://localhost:9301" -ForegroundColor White
Write-Host ""
Write-Host "🎯 NEXT STEPS:" -ForegroundColor Yellow
Write-Host "   1. Open http://localhost:3000 in your browser" -ForegroundColor White
Write-Host "   2. Login with CEO credentials above" -ForegroundColor White
Write-Host "   3. Explore all 19 pages and features" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Built with Elon Musk's First Principles" -ForegroundColor Cyan
Write-Host "   Question → Delete → Simplify → Accelerate → Ship" -ForegroundColor Cyan
Write-Host ""
Write-Host "=" * 50 -ForegroundColor Cyan

# Open browser
Write-Host "Opening browser..." -ForegroundColor Yellow
Start-Process "http://localhost:3000"

