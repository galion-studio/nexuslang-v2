#!/usr/bin/env pwsh
# GALION STUDIO - STATUS CHECK

Write-Host "📊 GALION STUDIO - STATUS" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

# Check Docker containers
$containers = docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | Select-String "nexus"

if ($containers) {
    Write-Host "`n✅ Running Services:" -ForegroundColor Green
    docker ps --filter "name=nexus" --format "  {{.Names}}: {{.Status}}"
    
    # Test endpoints
    Write-Host "`n🌐 Testing Endpoints:" -ForegroundColor Yellow
    
    # Frontend
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        Write-Host "  Frontend (3000):    ✅ OK" -ForegroundColor Green
    } catch {
        Write-Host "  Frontend (3000):    ❌ DOWN" -ForegroundColor Red
    }
    
    # API Gateway
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8080/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        Write-Host "  API Gateway (8080): ✅ OK" -ForegroundColor Green
    } catch {
        Write-Host "  API Gateway (8080): ❌ DOWN" -ForegroundColor Red
    }
    
    # Grafana
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:9300" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        Write-Host "  Grafana (9300):     ✅ OK" -ForegroundColor Green
    } catch {
        Write-Host "  Grafana (9300):     ❌ DOWN" -ForegroundColor Red
    }
    
} else {
    Write-Host "`n⚠️  No services running!" -ForegroundColor Yellow
    Write-Host "Run: .\LAUNCH.ps1" -ForegroundColor Gray
}

Write-Host ""

