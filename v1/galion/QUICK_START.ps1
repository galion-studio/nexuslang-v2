# NEXUS CORE - ONE-COMMAND QUICK START
# Following Elon Musk's principle: Make it simple, make it work

Write-Host "================================" -ForegroundColor Cyan
Write-Host "NEXUS CORE - QUICK START" -ForegroundColor Cyan
Write-Host "Building & Testing Complete System" -ForegroundColor Yellow
Write-Host "================================`n" -ForegroundColor Cyan

# Step 1: Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "[1/4] Generating secure secrets..." -ForegroundColor Yellow
    .\generate-secrets.ps1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to generate secrets" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[1/4] Secrets already exist" -ForegroundColor Green
}

# Step 2: Build services
Write-Host "`n[2/4] Building Docker services..." -ForegroundColor Yellow
docker-compose build --parallel
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to build services" -ForegroundColor Red
    exit 1
}
Write-Host "Build complete!" -ForegroundColor Green

# Step 3: Start services
Write-Host "`n[3/4] Starting all services..." -ForegroundColor Yellow
docker-compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to start services" -ForegroundColor Red
    exit 1
}

# Wait for services to be ready
Write-Host "Waiting for services to initialize..." -ForegroundColor Gray
Start-Sleep -Seconds 15

# Create Kafka topic if it doesn't exist
Write-Host "Ensuring Kafka topic exists..." -ForegroundColor Gray
docker exec nexus-kafka kafka-topics --bootstrap-server localhost:9092 --create --topic user-events --partitions 1 --replication-factor 1 --if-not-exists 2>&1 | Out-Null

# Restart auth service to ensure Kafka connection
docker-compose restart auth-service 2>&1 | Out-Null
Start-Sleep -Seconds 5

Write-Host "All services started!" -ForegroundColor Green

# Step 4: Run tests
Write-Host "`n[4/4] Running system tests..." -ForegroundColor Yellow
.\test-complete-system.ps1

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n================================" -ForegroundColor Cyan
    Write-Host "SUCCESS! NEXUS CORE IS READY" -ForegroundColor Green
    Write-Host "================================" -ForegroundColor Cyan
    
    Write-Host "`nAccess Points:" -ForegroundColor Yellow
    Write-Host "  API Gateway:  http://localhost:8080" -ForegroundColor White
    Write-Host "  Grafana:      http://localhost:3000" -ForegroundColor White
    Write-Host "  Kafka UI:     http://localhost:8090" -ForegroundColor White
    Write-Host "  Prometheus:   http://localhost:9091" -ForegroundColor White
    
    Write-Host "`nNext Steps:" -ForegroundColor Yellow
    Write-Host "  1. Open Grafana at http://localhost:3000" -ForegroundColor White
    Write-Host "  2. Try the API: curl http://localhost:8080/health" -ForegroundColor White
    Write-Host "  3. View logs: docker-compose logs -f" -ForegroundColor White
    
    Write-Host "`nDocumentation:" -ForegroundColor Yellow
    Write-Host "  - BUILD_COMPLETE.md - What was built" -ForegroundColor White
    Write-Host "  - README.md - Full documentation" -ForegroundColor White
    Write-Host "  - API_REFERENCE.md - API examples" -ForegroundColor White
    
    exit 0
} else {
    Write-Host "`nSome tests failed. Check the output above." -ForegroundColor Red
    Write-Host "View logs: docker-compose logs [service-name]" -ForegroundColor Yellow
    exit 1
}

