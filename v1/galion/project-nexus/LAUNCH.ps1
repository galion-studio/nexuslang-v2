#!/usr/bin/env pwsh
# GALION STUDIO - ONE COMMAND LAUNCH
# Following Elon Musk's Building Principles

Write-Host "🚀 GALION STUDIO - LAUNCH SEQUENCE" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

# Check Docker
Write-Host "`n📦 Checking Docker..." -NoNewline
if (Get-Command docker -ErrorAction SilentlyContinue) {
    Write-Host " ✅" -ForegroundColor Green
} else {
    Write-Host " ❌ Docker not found!" -ForegroundColor Red
    exit 1
}

# Check if already running
$running = docker ps --format "{{.Names}}" | Select-String "nexus"
if ($running) {
    Write-Host "✅ Services already running!" -ForegroundColor Green
} else {
    Write-Host "`n🚀 Starting backend services..." -ForegroundColor Yellow
    docker-compose up -d
    Write-Host "⏳ Waiting for services..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
}

# Start frontend in background if not running
$frontendRunning = Get-Process -Name node -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*frontend*"}
if (-not $frontendRunning) {
    Write-Host "`n🌐 Starting frontend..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev" -WindowStyle Minimized
    Start-Sleep -Seconds 5
}

Write-Host "`n✅ GALION STUDIO IS LIVE!" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Cyan

Write-Host "`n📍 Access Points:" -ForegroundColor White
Write-Host "  Frontend:   http://localhost:3000" -ForegroundColor Cyan
Write-Host "  API:        http://localhost:8080" -ForegroundColor Cyan
Write-Host "  Grafana:    http://localhost:9300" -ForegroundColor Cyan
Write-Host "  Prometheus: http://localhost:9301" -ForegroundColor Cyan
Write-Host "  Kafka UI:   http://localhost:9303" -ForegroundColor Cyan

Write-Host "`n🔐 Default Admin:" -ForegroundColor White
Write-Host "  Email:    admin@galion.app" -ForegroundColor Gray
Write-Host "  Password: Admin123!" -ForegroundColor Gray

Write-Host "`n🎯 Quick Commands:" -ForegroundColor White
Write-Host "  Stop All:     docker-compose down" -ForegroundColor Gray
Write-Host "  View Logs:    docker-compose logs -f" -ForegroundColor Gray
Write-Host "  Restart:      docker-compose restart" -ForegroundColor Gray

Write-Host "`n🚀 Ready to build the future!" -ForegroundColor Green

