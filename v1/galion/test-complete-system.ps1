# NEXUS CORE - COMPLETE SYSTEM TEST
# Tests the entire microservices platform end-to-end
# Following Elon Musk's First Principles: Test what matters, delete what doesn't

Write-Host "================================" -ForegroundColor Cyan
Write-Host "NEXUS CORE - SYSTEM TEST" -ForegroundColor Cyan
Write-Host "Testing Complete Microservices Platform" -ForegroundColor Yellow
Write-Host "================================`n" -ForegroundColor Cyan

$testsPassed = 0
$testsFailed = 0
$baseUrl = "http://localhost:8080"

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Url,
        [string]$Method = "GET",
        [string]$Body = $null,
        [int]$ExpectedStatus = 200
    )
    
    try {
        $params = @{
            Uri = $Url
            Method = $Method
            UseBasicParsing = $true
        }
        
        if ($Body) {
            $params.Body = $Body
            $params.ContentType = "application/json"
        }
        
        $response = Invoke-WebRequest @params -ErrorAction Stop
        
        if ($response.StatusCode -eq $ExpectedStatus) {
            Write-Host "[PASS] $Name" -ForegroundColor Green
            $script:testsPassed++
            return $response
        } else {
            Write-Host "[FAIL] $Name - Expected $ExpectedStatus, got $($response.StatusCode)" -ForegroundColor Red
            $script:testsFailed++
            return $null
        }
    } catch {
        Write-Host "[FAIL] $Name - $($_.Exception.Message)" -ForegroundColor Red
        $script:testsFailed++
        return $null
    }
}

# Test 1: Health Checks
Write-Host "`n1. HEALTH CHECKS" -ForegroundColor Cyan
Write-Host "=================" -ForegroundColor Cyan
Test-Endpoint "API Gateway Health" "$baseUrl/health"
Test-Endpoint "Auth Service Health" "http://localhost:8000/health"
Test-Endpoint "User Service Health" "http://localhost:8001/health"
Test-Endpoint "Analytics Service Health" "http://localhost:9090/health"

# Test 2: User Registration
Write-Host "`n2. USER REGISTRATION" -ForegroundColor Cyan
Write-Host "=====================" -ForegroundColor Cyan
$email = "testuser_$(Get-Random)@example.com"
$registerBody = @{
    email = $email
    password = "SecurePass123!"
    name = "Test User"
} | ConvertTo-Json

$registerResponse = Test-Endpoint "Register New User" "$baseUrl/api/v1/auth/register" "POST" $registerBody 201

# Test 3: User Login
Write-Host "`n3. USER LOGIN" -ForegroundColor Cyan
Write-Host "==============" -ForegroundColor Cyan
$loginBody = @{
    email = $email
    password = "SecurePass123!"
} | ConvertTo-Json

$loginResponse = Test-Endpoint "User Login" "$baseUrl/api/v1/auth/login" "POST" $loginBody

if ($loginResponse) {
    $token = ($loginResponse.Content | ConvertFrom-Json).data.token
    Write-Host "   Token received: $($token.Substring(0,20))..." -ForegroundColor Gray
}

# Test 4: Authenticated Requests
Write-Host "`n4. AUTHENTICATED REQUESTS" -ForegroundColor Cyan
Write-Host "==========================" -ForegroundColor Cyan

if ($token) {
    try {
        $headers = @{
            "Authorization" = "Bearer $token"
        }
        $meResponse = Invoke-WebRequest -Uri "$baseUrl/api/v1/auth/me" -Method GET -Headers $headers -UseBasicParsing
        Write-Host "[PASS] Get Current User (Protected Route)" -ForegroundColor Green
        $script:testsPassed++
        
        $userData = ($meResponse.Content | ConvertFrom-Json).data
        Write-Host "   User: $($userData.name) ($($userData.email))" -ForegroundColor Gray
    } catch {
        Write-Host "[FAIL] Get Current User - $($_.Exception.Message)" -ForegroundColor Red
        $script:testsFailed++
    }
} else {
    Write-Host "[FAIL] Skipped - No token available" -ForegroundColor Red
    $script:testsFailed++
}

# Test 5: Analytics Pipeline
Write-Host "`n5. ANALYTICS PIPELINE" -ForegroundColor Cyan
Write-Host "======================" -ForegroundColor Cyan

Start-Sleep -Seconds 3  # Wait for events to be processed

try {
    $metricsResponse = Invoke-WebRequest -Uri "http://localhost:9090/metrics" -Method GET -UseBasicParsing
    $metrics = $metricsResponse.Content
    
    if ($metrics -match 'analytics_events_processed_total\{event_type="user\.registered"') {
        Write-Host "[PASS] User Registration Events Processed" -ForegroundColor Green
        $script:testsPassed++
    } else {
        Write-Host "[FAIL] No registration events found in metrics" -ForegroundColor Red
        $script:testsFailed++
    }
    
    if ($metrics -match 'analytics_events_processed_total\{event_type="user\.login"') {
        Write-Host "[PASS] User Login Events Processed" -ForegroundColor Green
        $script:testsPassed++
    } else {
        Write-Host "[FAIL] No login events found in metrics" -ForegroundColor Red
        $script:testsFailed++
    }
    
    if ($metrics -match 'analytics_events_stored_total (\d+)') {
        $eventsStored = $matches[1]
        Write-Host "[PASS] Events Stored in Database: $eventsStored" -ForegroundColor Green
        $script:testsPassed++
    } else {
        Write-Host "[FAIL] Could not determine events stored" -ForegroundColor Red
        $script:testsFailed++
    }
} catch {
    Write-Host "[FAIL] Failed to fetch metrics - $($_.Exception.Message)" -ForegroundColor Red
    $script:testsFailed += 3
}

# Test 6: Database Connectivity
Write-Host "`n6. DATABASE CONNECTIVITY" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan

try {
    $pgCheck = docker exec nexus-postgres pg_isready -U nexuscore 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[PASS] PostgreSQL Database Ready" -ForegroundColor Green
        $script:testsPassed++
    } else {
        Write-Host "[FAIL] PostgreSQL Not Ready" -ForegroundColor Red
        $script:testsFailed++
    }
} catch {
    Write-Host "[FAIL] PostgreSQL Check Failed" -ForegroundColor Red
    $script:testsFailed++
}

try {
    # Try Redis ping (password is configured in docker-compose)
    $redisCheck = docker exec nexus-redis redis-cli ping 2>&1 | Out-String
    if ($redisCheck -match "PONG" -or $redisCheck -match "NOAUTH") {
        Write-Host "[PASS] Redis Cache Ready" -ForegroundColor Green
        $script:testsPassed++
    } else {
        Write-Host "[FAIL] Redis Not Ready - $redisCheck" -ForegroundColor Red
        $script:testsFailed++
    }
} catch {
    Write-Host "[FAIL] Redis Check Failed - $($_.Exception.Message)" -ForegroundColor Red
    $script:testsFailed++
}

# Test 7: Kafka Topics
Write-Host "`n7. KAFKA MESSAGING" -ForegroundColor Cyan
Write-Host "===================" -ForegroundColor Cyan

try {
    $topics = docker exec nexus-kafka kafka-topics --bootstrap-server localhost:9092 --list 2>&1
    if ($topics -match "user-events") {
        Write-Host "[PASS] Kafka Topic 'user-events' Exists" -ForegroundColor Green
        $script:testsPassed++
    } else {
        Write-Host "[FAIL] Kafka Topic 'user-events' Not Found" -ForegroundColor Red
        $script:testsFailed++
    }
} catch {
    Write-Host "[FAIL] Kafka Check Failed" -ForegroundColor Red
    $script:testsFailed++
}

# Test 8: Monitoring Stack
Write-Host "`n8. MONITORING STACK" -ForegroundColor Cyan
Write-Host "====================" -ForegroundColor Cyan

Test-Endpoint "Prometheus Metrics" "http://localhost:9091/-/healthy"
Test-Endpoint "Grafana Dashboard" "http://localhost:3000/api/health"

# Summary
Write-Host "`n================================" -ForegroundColor Cyan
Write-Host "TEST SUMMARY" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Tests Passed: $testsPassed" -ForegroundColor Green
Write-Host "Tests Failed: $testsFailed" -ForegroundColor $(if ($testsFailed -eq 0) { "Green" } else { "Red" })
Write-Host "Total Tests:  $($testsPassed + $testsFailed)" -ForegroundColor White

if ($testsFailed -eq 0) {
    Write-Host "`nALL TESTS PASSED!" -ForegroundColor Green
    Write-Host "Your Nexus Core platform is fully operational." -ForegroundColor Green
    exit 0
} else {
    Write-Host "`nSOME TESTS FAILED" -ForegroundColor Red
    Write-Host "Review the errors above and check service logs." -ForegroundColor Yellow
    exit 1
}

