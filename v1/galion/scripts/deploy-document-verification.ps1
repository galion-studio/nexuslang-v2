# Deploy Document Verification and Permissions System
# PowerShell script for Windows

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  DEPLOY: Document Verification + Permissions    " -ForegroundColor Cyan
Write-Host "  Following Elon Musk's First Principles         " -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Run database migrations
Write-Host "[1/5] Running database migrations..." -ForegroundColor Yellow
Write-Host "  - Document verification tables" -ForegroundColor Gray
Write-Host "  - Custom permissions (RBAC) tables" -ForegroundColor Gray
Write-Host ""

# Check if postgres is running
$postgresRunning = docker ps --filter "name=nexus-postgres" --format "{{.Names}}"
if (-not $postgresRunning) {
    Write-Host "ERROR: PostgreSQL is not running!" -ForegroundColor Red
    Write-Host "Run: docker-compose up -d postgres" -ForegroundColor Yellow
    exit 1
}

# Run migrations
Write-Host "Executing migration 005_document_verification.sql..." -ForegroundColor Cyan
Get-Content database/migrations/005_document_verification.sql | docker exec -i nexus-postgres psql -U $env:POSTGRES_USER -d $env:POSTGRES_DB

Write-Host "Executing migration 006_custom_permissions.sql..." -ForegroundColor Cyan
Get-Content database/migrations/006_custom_permissions.sql | docker exec -i nexus-postgres psql -U $env:POSTGRES_USER -d $env:POSTGRES_DB

Write-Host "✓ Migrations complete!" -ForegroundColor Green
Write-Host ""

# Step 2: Build new services
Write-Host "[2/5] Building new services..." -ForegroundColor Yellow
Write-Host "  - Document Service (Python/FastAPI)" -ForegroundColor Gray
Write-Host "  - Permissions Service (Python/FastAPI)" -ForegroundColor Gray
Write-Host ""

docker-compose build document-service permissions-service

Write-Host "✓ Services built!" -ForegroundColor Green
Write-Host ""

# Step 3: Start new services
Write-Host "[3/5] Starting new services..." -ForegroundColor Yellow
Write-Host ""

docker-compose up -d document-service permissions-service

Write-Host "✓ Services started!" -ForegroundColor Green
Write-Host ""

# Step 4: Wait for health checks
Write-Host "[4/5] Waiting for services to be healthy..." -ForegroundColor Yellow
Write-Host ""

$maxWait = 60
$waited = 0
$interval = 5

while ($waited -lt $maxWait) {
    Write-Host "Checking service health... ($waited/$maxWait seconds)" -ForegroundColor Gray
    
    # Check document service
    try {
        $docHealth = Invoke-WebRequest -Uri "http://localhost:8004/health" -UseBasicParsing -TimeoutSec 2
        $docHealthy = $docHealth.StatusCode -eq 200
    } catch {
        $docHealthy = $false
    }
    
    # Check permissions service
    try {
        $permHealth = Invoke-WebRequest -Uri "http://localhost:8005/health" -UseBasicParsing -TimeoutSec 2
        $permHealthy = $permHealth.StatusCode -eq 200
    } catch {
        $permHealthy = $false
    }
    
    if ($docHealthy -and $permHealthy) {
        Write-Host "✓ All services healthy!" -ForegroundColor Green
        break
    }
    
    if (-not $docHealthy) {
        Write-Host "  ⏳ Document Service not ready yet..." -ForegroundColor Gray
    }
    if (-not $permHealthy) {
        Write-Host "  ⏳ Permissions Service not ready yet..." -ForegroundColor Gray
    }
    
    Start-Sleep -Seconds $interval
    $waited += $interval
}

if ($waited -ge $maxWait) {
    Write-Host "WARNING: Services taking longer than expected to start" -ForegroundColor Yellow
    Write-Host "Check logs: docker-compose logs document-service permissions-service" -ForegroundColor Yellow
}

Write-Host ""

# Step 5: Verify deployment
Write-Host "[5/5] Verifying deployment..." -ForegroundColor Yellow
Write-Host ""

# Test document service
Write-Host "Testing Document Service..." -ForegroundColor Cyan
try {
    $docResponse = Invoke-RestMethod -Uri "http://localhost:8004/" -Method Get
    Write-Host "  ✓ Document Service: $($docResponse.service) - $($docResponse.status)" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Document Service: Failed" -ForegroundColor Red
}

# Test permissions service
Write-Host "Testing Permissions Service..." -ForegroundColor Cyan
try {
    $permResponse = Invoke-RestMethod -Uri "http://localhost:8005/" -Method Get
    Write-Host "  ✓ Permissions Service: $($permResponse.service) - $($permResponse.status)" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Permissions Service: Failed" -ForegroundColor Red
}

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  DEPLOYMENT COMPLETE!                           " -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Services Running:" -ForegroundColor Yellow
Write-Host "  • Document Service:    http://localhost:8004" -ForegroundColor White
Write-Host "  • Permissions Service: http://localhost:8005" -ForegroundColor White
Write-Host ""

Write-Host "API Documentation:" -ForegroundColor Yellow
Write-Host "  • Document API Docs:    http://localhost:8004/docs" -ForegroundColor White
Write-Host "  • Permissions API Docs: http://localhost:8005/docs" -ForegroundColor White
Write-Host ""

Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Run test scripts: .\scripts\test-documents.ps1" -ForegroundColor White
Write-Host "  2. Check logs: docker-compose logs -f document-service" -ForegroundColor White
Write-Host "  3. View metrics: http://localhost:9091 (Prometheus)" -ForegroundColor White
Write-Host ""

Write-Host "Built with First Principles: Question → Delete → Simplify → Ship 🚀" -ForegroundColor Cyan

