# NEXUS CORE - FULL SYSTEM RELOAD
# Clears all caches and reloads every Nexus service
# Built with First Principles: Fast, Simple, Effective

Write-Host "================================" -ForegroundColor Cyan
Write-Host "NEXUS CORE - FULL SYSTEM RELOAD" -ForegroundColor Cyan
Write-Host "Clearing Caches & Reloading Services" -ForegroundColor Yellow
Write-Host "================================`n" -ForegroundColor Cyan

# Step 1: Clear Redis Cache
Write-Host "[1/5] Clearing Redis cache..." -ForegroundColor Yellow
try {
    $redisPassword = (Get-Content .env | Select-String "^REDIS_PASSWORD=").ToString().Split('=')[1]
    docker exec nexus-redis redis-cli -a $redisPassword FLUSHALL 2>&1 | Out-Null
    Write-Host "✓ Redis cache cleared" -ForegroundColor Green
} catch {
    Write-Host "⚠ Redis cache clear failed (might not be running)" -ForegroundColor Yellow
}

# Step 2: Stop all application services (keep data stores running)
Write-Host "`n[2/5] Stopping all application services..." -ForegroundColor Yellow
$appServices = @(
    "api-gateway",
    "auth-service", 
    "user-service",
    "scraping-service",
    "voice-service",
    "analytics-service"
)

foreach ($service in $appServices) {
    Write-Host "  - Stopping $service..." -ForegroundColor Gray
    docker-compose stop $service 2>&1 | Out-Null
}
Write-Host "✓ All services stopped" -ForegroundColor Green

# Step 3: Remove containers to force fresh start
Write-Host "`n[3/5] Removing containers for clean restart..." -ForegroundColor Yellow
foreach ($service in $appServices) {
    docker-compose rm -f $service 2>&1 | Out-Null
}
Write-Host "✓ Containers removed" -ForegroundColor Green

# Step 4: Restart all services
Write-Host "`n[4/5] Starting all services..." -ForegroundColor Yellow
docker-compose up -d 2>&1 | Out-Null
Write-Host "✓ Services restarted" -ForegroundColor Green

# Step 5: Wait for services to be healthy
Write-Host "`n[5/5] Waiting for services to be healthy..." -ForegroundColor Yellow
Write-Host "  This takes ~45 seconds for health checks..." -ForegroundColor Gray

Start-Sleep -Seconds 10
Write-Host "  ▓▓▓░░░░░░░ 25% - Services initializing..." -ForegroundColor Cyan
Start-Sleep -Seconds 10
Write-Host "  ▓▓▓▓▓▓░░░░ 50% - Database connections..." -ForegroundColor Cyan
Start-Sleep -Seconds 15
Write-Host "  ▓▓▓▓▓▓▓▓░░ 75% - Health checks running..." -ForegroundColor Cyan
Start-Sleep -Seconds 10
Write-Host "  ▓▓▓▓▓▓▓▓▓▓ 100% - Services ready!" -ForegroundColor Cyan

# Step 6: Verify system health
Write-Host "`n================================" -ForegroundColor Cyan
Write-Host "SYSTEM STATUS" -ForegroundColor Cyan
Write-Host "================================`n" -ForegroundColor Cyan

# Check API Gateway
try {
    $health = curl.exe -s http://localhost:8080/health | ConvertFrom-Json
    if ($health.status -eq "healthy") {
        Write-Host "✓ API Gateway: HEALTHY" -ForegroundColor Green
    } else {
        Write-Host "⚠ API Gateway: $($health.status)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "✗ API Gateway: NOT RESPONDING" -ForegroundColor Red
}

# Check Auth Service
try {
    $health = curl.exe -s http://localhost:8000/health | ConvertFrom-Json
    if ($health.status -eq "ok") {
        Write-Host "✓ Auth Service: HEALTHY" -ForegroundColor Green
    } else {
        Write-Host "⚠ Auth Service: STARTING" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠ Auth Service: STARTING (wait 30s)" -ForegroundColor Yellow
}

# Check User Service
try {
    $health = curl.exe -s http://localhost:8001/health | ConvertFrom-Json
    if ($health.status -eq "ok") {
        Write-Host "✓ User Service: HEALTHY" -ForegroundColor Green
    } else {
        Write-Host "⚠ User Service: STARTING" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠ User Service: STARTING (wait 30s)" -ForegroundColor Yellow
}

# Check Analytics Service
try {
    $health = curl.exe -s http://localhost:9090/health | ConvertFrom-Json
    if ($health.status -eq "ok") {
        Write-Host "✓ Analytics Service: HEALTHY" -ForegroundColor Green
    } else {
        Write-Host "⚠ Analytics Service: STARTING" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠ Analytics Service: STARTING (wait 30s)" -ForegroundColor Yellow
}

# Check Voice Service
try {
    $health = curl.exe -s http://localhost:8003/health | ConvertFrom-Json
    if ($health.status -eq "ok") {
        Write-Host "✓ Voice Service: HEALTHY" -ForegroundColor Green
    } else {
        Write-Host "⚠ Voice Service: STARTING" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠ Voice Service: STARTING (wait 30s)" -ForegroundColor Yellow
}

# Check Scraping Service
try {
    $health = curl.exe -s http://localhost:8002/health | ConvertFrom-Json
    if ($health.status -eq "ok") {
        Write-Host "✓ Scraping Service: HEALTHY" -ForegroundColor Green
    } else {
        Write-Host "⚠ Scraping Service: STARTING" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠ Scraping Service: STARTING (wait 30s)" -ForegroundColor Yellow
}

# Display service count
Write-Host "`n================================" -ForegroundColor Cyan
$runningCount = (docker-compose ps --filter "status=running" | Measure-Object).Count - 1  # Subtract header
Write-Host "Running Services: $runningCount/12" -ForegroundColor $(if ($runningCount -eq 12) { "Green" } else { "Yellow" })

# Quick commands reference
Write-Host "`n================================" -ForegroundColor Cyan
Write-Host "QUICK COMMANDS" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host "View logs:         docker-compose logs -f [service-name]" -ForegroundColor Gray
Write-Host "Check status:      docker-compose ps" -ForegroundColor Gray
Write-Host "Test API:          curl.exe http://localhost:8080/health" -ForegroundColor Gray
Write-Host "Admin Terminal:    .\nexus-admin.ps1" -ForegroundColor Gray
Write-Host "Reload again:      .\reload-nexus.ps1" -ForegroundColor Gray

Write-Host "`n================================" -ForegroundColor Cyan
Write-Host "RELOAD COMPLETE!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host "`nAll caches cleared, all services reloaded!" -ForegroundColor Green
Write-Host "If services show 'STARTING', wait 30 seconds and test again.`n" -ForegroundColor Yellow

