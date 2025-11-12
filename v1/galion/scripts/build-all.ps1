# Auto-Build Script - Waits for Docker then Builds

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Nexus Core - Auto Build" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Wait for Docker to be ready
Write-Host "Waiting for Docker Desktop to be ready..." -ForegroundColor Yellow
$maxAttempts = 30
$attempt = 0

while ($attempt -lt $maxAttempts) {
    $result = docker ps 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "OK: Docker is ready!" -ForegroundColor Green
        break
    }
    
    $attempt++
    Write-Host "  Attempt $attempt/$maxAttempts..." -ForegroundColor Gray
    Start-Sleep -Seconds 2
}

if ($attempt -ge $maxAttempts) {
    Write-Host "ERROR: Docker Desktop is not ready. Please start Docker Desktop and try again." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Building all Docker images..." -ForegroundColor Cyan
Write-Host "This may take 5-10 minutes on first build..." -ForegroundColor Yellow
Write-Host ""

# Build all images
docker-compose build

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "OK: Build successful!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Starting all services..." -ForegroundColor Cyan
    docker-compose up -d
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "OK: All services started!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Waiting for services to be ready..." -ForegroundColor Yellow
        Start-Sleep -Seconds 15
        
        Write-Host ""
        Write-Host "Checking service status..." -ForegroundColor Cyan
        docker-compose ps
        
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "BUILD COMPLETE!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Next: Run .\scripts\test-analytics.ps1 to test the system" -ForegroundColor Yellow
    } else {
        Write-Host "ERROR: Failed to start services" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "ERROR: Build failed" -ForegroundColor Red
    exit 1
}
