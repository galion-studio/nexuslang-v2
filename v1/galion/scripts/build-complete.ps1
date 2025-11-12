# Complete Build Script - Ready to Execute

# This script will build everything once WSL 2 is installed
# Run after WSL 2 installation and Docker Desktop is running

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Nexus Core - Complete Build" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check WSL
Write-Host "Checking WSL..." -ForegroundColor Yellow
$wslStatus = wsl --status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: WSL not installed. Run: wsl --install (as Administrator)" -ForegroundColor Red
    exit 1
}
Write-Host "OK: WSL found" -ForegroundColor Green

# Check Docker
Write-Host "`nChecking Docker..." -ForegroundColor Yellow
$dockerCheck = docker ps 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Docker Desktop not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}
Write-Host "OK: Docker is running" -ForegroundColor Green

# Build all images
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Building Docker Images" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "This may take 5-10 minutes on first build..." -ForegroundColor Yellow
Write-Host ""

docker-compose build

if ($LASTEXITCODE -ne 0) {
    Write-Host "`nERROR: Build failed" -ForegroundColor Red
    exit 1
}

Write-Host "`nOK: Build successful!" -ForegroundColor Green

# Start all services
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Starting Services" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

docker-compose up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to start services" -ForegroundColor Red
    exit 1
}

Write-Host "OK: Services started!" -ForegroundColor Green

# Wait for services
Write-Host "`nWaiting for services to be ready (30 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Check status
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Service Status" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
docker-compose ps

# Test system
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Testing System" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if (Test-Path "scripts\test-analytics.ps1") {
    .\scripts\test-analytics.ps1
} else {
    Write-Host "Test script not found, skipping test" -ForegroundColor Yellow
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "BUILD COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Services are running:" -ForegroundColor Green
Write-Host "  - API Gateway: http://localhost:8080" -ForegroundColor White
Write-Host "  - Auth Service: http://localhost:8000/docs" -ForegroundColor White
Write-Host "  - User Service: http://localhost:8001/docs" -ForegroundColor White
Write-Host "  - Analytics Metrics: http://localhost:9090/metrics" -ForegroundColor White
Write-Host "  - Kafka UI: http://localhost:8090" -ForegroundColor White
Write-Host "  - Grafana: http://localhost:3000 (admin/admin)" -ForegroundColor White
Write-Host ""

