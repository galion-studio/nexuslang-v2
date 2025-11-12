# Test script for Analytics Service integration (PowerShell)
# Tests complete event flow: register user → check Kafka → verify analytics processes → check database

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Testing Analytics Service Integration" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
try {
    docker ps | Out-Null
} catch {
    Write-Host "Error: Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

Write-Host "Step 1: Checking if services are running..." -ForegroundColor Yellow
$servicesRunning = docker ps --format "{{.Names}}" | Select-String -Pattern "nexus-postgres|nexus-kafka|nexus-analytics-service"
if (-not $servicesRunning) {
    Write-Host "Services not running. Starting services..." -ForegroundColor Yellow
    docker-compose up -d postgres redis zookeeper kafka analytics-service
    Write-Host "Waiting for services to be ready..." -ForegroundColor Yellow
    Start-Sleep -Seconds 15
} else {
    Write-Host "Services are running" -ForegroundColor Green
}

Write-Host ""
Write-Host "Step 2: Registering a test user..." -ForegroundColor Yellow
$registerBody = @{
    email = "analytics-test@example.com"
    password = "TestPassword123!"
    name = "Analytics Test User"
} | ConvertTo-Json

try {
    $registerResponse = Invoke-RestMethod -Uri "http://localhost:8080/api/v1/auth/register" `
        -Method Post `
        -ContentType "application/json" `
        -Body $registerBody
    
    Write-Host "User registered successfully" -ForegroundColor Green
    $userId = $registerResponse.data.user.id
    Write-Host "User ID: $userId" -ForegroundColor Cyan
} catch {
    Write-Host "Failed to register user" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 3: Waiting for event to be processed (5 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "Step 4: Checking analytics service logs for processed events..." -ForegroundColor Yellow
$analyticsLogs = docker logs nexus-analytics-service --tail 50 2>&1
if ($analyticsLogs -match "user\.registered") {
    Write-Host "✓ Event found in analytics service logs" -ForegroundColor Green
    $analyticsLogs | Select-String "user\.registered" | Select-Object -Last 1
} else {
    Write-Host "✗ Event not found in analytics service logs" -ForegroundColor Red
    Write-Host "Recent logs:" -ForegroundColor Yellow
    $analyticsLogs | Select-Object -Last 10
}

Write-Host ""
Write-Host "Step 5: Checking database for stored events..." -ForegroundColor Yellow
try {
    $dbQuery = "SELECT COUNT(*) FROM analytics.events WHERE event_type = 'user.registered';"
    $dbResult = docker exec -i nexus-postgres psql -U nexuscore -d nexuscore -t -c $dbQuery 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        $eventCount = ($dbResult -replace '\s', '').Trim()
        if ([int]$eventCount -gt 0) {
            Write-Host "✓ Found $eventCount event(s) in database" -ForegroundColor Green
            
            Write-Host ""
            Write-Host "Recent events:" -ForegroundColor Cyan
            docker exec -i nexus-postgres psql -U nexuscore -d nexuscore -c `
                "SELECT event_type, user_id, service, timestamp FROM analytics.events ORDER BY timestamp DESC LIMIT 5;"
        } else {
            Write-Host "✗ No events found in database" -ForegroundColor Red
        }
    } else {
        Write-Host "✗ Failed to query database" -ForegroundColor Red
        Write-Host "Error: $dbResult" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ Database query failed: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "Step 6: Checking Prometheus metrics..." -ForegroundColor Yellow
try {
    $metrics = Invoke-RestMethod -Uri "http://localhost:9090/metrics" -Method Get
    if ($metrics -match "analytics_events_processed_total") {
        Write-Host "✓ Prometheus metrics are available" -ForegroundColor Green
        ($metrics -split "`n" | Select-String "analytics_events_processed_total") | Select-Object -First 5
    } else {
        Write-Host "✗ Prometheus metrics not found" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ Failed to fetch metrics: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "Step 7: Testing login event..." -ForegroundColor Yellow
try {
    $loginResponse = Invoke-RestMethod -Uri "http://localhost:8080/api/v1/auth/login?email=analytics-test@example.com&password=TestPassword123!" `
        -Method Post
    
    Write-Host "Login successful" -ForegroundColor Green
    Start-Sleep -Seconds 3
    
    # Check for login event
    $loginQuery = "SELECT COUNT(*) FROM analytics.events WHERE event_type = 'user.login';"
    $loginEvents = docker exec -i nexus-postgres psql -U nexuscore -d nexuscore -t -c $loginQuery 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        $loginCount = ($loginEvents -replace '\s', '').Trim()
        if ([int]$loginCount -gt 0) {
            Write-Host "✓ Login event found in database" -ForegroundColor Green
        } else {
            Write-Host "⚠ Login event not yet in database (may take a few seconds)" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "Login failed: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Test Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Summary:" -ForegroundColor Cyan
Write-Host "- User registration: ✓" -ForegroundColor Green
Write-Host "- Event publishing: Check logs above" -ForegroundColor Yellow
Write-Host "- Analytics processing: Check logs above" -ForegroundColor Yellow
Write-Host "- Database storage: Check database query above" -ForegroundColor Yellow
Write-Host "- Prometheus metrics: Check metrics above" -ForegroundColor Yellow
Write-Host ""
Write-Host "To view analytics service logs:" -ForegroundColor Cyan
Write-Host "  docker logs nexus-analytics-service -f" -ForegroundColor White
Write-Host ""
Write-Host "To query events in database:" -ForegroundColor Cyan
Write-Host "  docker exec -it nexus-postgres psql -U nexuscore -d nexuscore" -ForegroundColor White
Write-Host "  SELECT * FROM analytics.events ORDER BY timestamp DESC LIMIT 10;" -ForegroundColor White

