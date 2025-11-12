# Quick System Test
Write-Host "`n🔍 NEXUS CORE - SYSTEM TEST" -ForegroundColor Cyan
Write-Host "================================`n" -ForegroundColor Cyan

# Test 1: Services Status
Write-Host "Test 1: Checking Service Status..." -ForegroundColor Yellow
$services = docker-compose ps --format json | ConvertFrom-Json
$healthy = 0
$total = 0
foreach ($svc in $services) {
    $total++
    if ($svc.State -match "Up|running") {
        $healthy++
        Write-Host "  ✅ $($svc.Name): $($svc.State)" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $($svc.Name): $($svc.State)" -ForegroundColor Red
    }
}
Write-Host "`n  Result: $healthy/$total services running" -ForegroundColor Cyan

# Test 2: Health Endpoints
Write-Host "`nTest 2: Testing Health Endpoints..." -ForegroundColor Yellow
$endpoints = @(
    @{Name="Auth Service"; URL="http://localhost:8000/health"},
    @{Name="User Service"; URL="http://localhost:8001/health"},
    @{Name="Analytics"; URL="http://localhost:9090/health"},
    @{Name="API Gateway"; URL="http://localhost:8080/health"}
)

$healthyEndpoints = 0
foreach ($ep in $endpoints) {
    try {
        $response = Invoke-WebRequest -Uri $ep.URL -Method Get -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "  ✅ $($ep.Name): Healthy" -ForegroundColor Green
            $healthyEndpoints++
        }
    } catch {
        Write-Host "  ❌ $($ep.Name): Unhealthy" -ForegroundColor Red
    }
}
Write-Host "`n  Result: $healthyEndpoints/$($endpoints.Count) endpoints healthy" -ForegroundColor Cyan

# Test 3: Database Connection
Write-Host "`nTest 3: Testing Database Connection..." -ForegroundColor Yellow
try {
    $dbTest = docker exec nexus-postgres psql -U nexuscore -d nexuscore -c 'SELECT 1;' 2>&1
    if ($dbTest -match '1 row') {
        Write-Host "  [OK] PostgreSQL: Connected" -ForegroundColor Green
    }
} catch {
    Write-Host "  [FAIL] PostgreSQL: Connection failed" -ForegroundColor Red
}

# Test 4: Redis Connection
Write-Host "`nTest 4: Testing Redis Connection..." -ForegroundColor Yellow
try {
    $redisPass = (Get-Content .env | Select-String 'REDIS_PASSWORD=').ToString().Split('=')[1]
    $redisTest = docker exec nexus-redis redis-cli -a $redisPass ping 2>&1
    if ($redisTest -match 'PONG') {
        Write-Host "  [OK] Redis: Connected" -ForegroundColor Green
    }
} catch {
    Write-Host "  [FAIL] Redis: Connection failed" -ForegroundColor Red
}

# Test 5: Kafka Status
Write-Host "`nTest 5: Testing Kafka..." -ForegroundColor Yellow
try {
    $kafkaTest = docker exec nexus-kafka kafka-topics --bootstrap-server localhost:9092 --list 2>&1
    if ($kafkaTest) {
        Write-Host "  ✅ Kafka: Running" -ForegroundColor Green
        Write-Host "    Topics: $($kafkaTest -join ', ')" -ForegroundColor Gray
    }
} catch {
    Write-Host "  ❌ Kafka: Not accessible" -ForegroundColor Red
}

# Summary
Write-Host "`n================================" -ForegroundColor Cyan
Write-Host "SYSTEM TEST COMPLETE" -ForegroundColor Green
Write-Host "================================`n" -ForegroundColor Cyan

Write-Host "Access Points:" -ForegroundColor Yellow
Write-Host "  - API Gateway:  http://localhost:8080"
Write-Host "  - Auth API:     http://localhost:8000/docs"
Write-Host "  - User API:     http://localhost:8001/docs"
Write-Host "  - Grafana:      http://localhost:3000"
Write-Host "  - Prometheus:   http://localhost:9091"
Write-Host "  - Kafka UI:     http://localhost:8090"
Write-Host ""
