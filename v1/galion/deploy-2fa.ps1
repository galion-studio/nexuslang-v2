# Deploy 2FA Implementation
# Applies database migrations and restarts services

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Deploying 2FA Implementation" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Apply database migration
Write-Host "1. Applying database migration..." -ForegroundColor Yellow
try {
    $env:PGPASSWORD = "postgres"
    docker exec nexus-postgres psql -U postgres -d nexus_db -f /docker-entrypoint-initdb.d/migrations/004_add_2fa_support.sql
    Write-Host "✓ Database migration applied" -ForegroundColor Green
} catch {
    Write-Host "! Migration may already be applied or container not running" -ForegroundColor Yellow
    Write-Host "  Try: docker exec nexus-postgres psql -U postgres -d nexus_db -f /docker-entrypoint-initdb.d/migrations/004_add_2fa_support.sql" -ForegroundColor Gray
}
Write-Host ""

# Step 2: Rebuild auth service with new dependencies
Write-Host "2. Rebuilding auth-service with 2FA dependencies..." -ForegroundColor Yellow
try {
    docker-compose build auth-service
    Write-Host "✓ Auth service rebuilt" -ForegroundColor Green
} catch {
    Write-Host "✗ Build failed: $_" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 3: Restart auth service
Write-Host "3. Restarting auth-service..." -ForegroundColor Yellow
try {
    docker-compose restart auth-service
    Start-Sleep -Seconds 3
    Write-Host "✓ Auth service restarted" -ForegroundColor Green
} catch {
    Write-Host "✗ Restart failed: $_" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 4: Check health
Write-Host "4. Checking service health..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8001/health" -TimeoutSec 5
    Write-Host "✓ Service is healthy" -ForegroundColor Green
    Write-Host "  Status: $($health.status)" -ForegroundColor Gray
} catch {
    Write-Host "! Service may still be starting..." -ForegroundColor Yellow
    Write-Host "  Wait a few seconds and check: http://localhost:8001/docs" -ForegroundColor Gray
}
Write-Host ""

# Step 5: Show API docs
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "2FA Endpoints available at:" -ForegroundColor Yellow
Write-Host "  • POST   /api/v1/2fa/setup" -ForegroundColor White
Write-Host "  • POST   /api/v1/2fa/verify" -ForegroundColor White
Write-Host "  • POST   /api/v1/2fa/disable" -ForegroundColor White
Write-Host "  • GET    /api/v1/2fa/status" -ForegroundColor White
Write-Host "  • POST   /api/v1/2fa/backup-codes/regenerate" -ForegroundColor White
Write-Host "  • POST   /api/v1/auth/login/2fa" -ForegroundColor White
Write-Host ""
Write-Host "API Documentation: http://localhost:8001/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Test the implementation:" -ForegroundColor Yellow
Write-Host "  .\test-2fa.ps1" -ForegroundColor White
Write-Host ""
Write-Host "Read the docs:" -ForegroundColor Yellow
Write-Host "  services\auth-service\2FA_IMPLEMENTATION.md" -ForegroundColor White
Write-Host ""

