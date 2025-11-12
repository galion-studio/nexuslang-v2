# Test NexusLang v2 Alpha
# Verifies all services are working correctly

Write-Host "🧪 Testing NexusLang v2 Alpha..." -ForegroundColor Blue
Write-Host ""

$errors = 0
$warnings = 0

# Test 1: Check if Docker is running
Write-Host "Test 1: Docker Status..." -NoNewline
try {
    docker ps > $null 2>&1
    Write-Host " ✓" -ForegroundColor Green
} catch {
    Write-Host " ✗" -ForegroundColor Red
    Write-Host "   Docker is not running. Please start Docker Desktop." -ForegroundColor Yellow
    $errors++
}

# Test 2: Check if services are running
Write-Host "Test 2: Services Running..." -NoNewline
$services = docker-compose ps --services --filter "status=running" 2>$null
if ($services -and ($services.Count -ge 3)) {
    Write-Host " ✓" -ForegroundColor Green
} else {
    Write-Host " ✗" -ForegroundColor Red
    Write-Host "   Services not running. Run: .\START_ALPHA_NOW.ps1" -ForegroundColor Yellow
    $errors++
}

# Test 3: Backend health
Write-Host "Test 3: Backend Health..." -NoNewline
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 5
    if ($health.status -eq "healthy") {
        Write-Host " ✓" -ForegroundColor Green
    } else {
        Write-Host " ?" -ForegroundColor Yellow
        $warnings++
    }
} catch {
    Write-Host " ✗" -ForegroundColor Red
    Write-Host "   Backend not responding at http://localhost:8000" -ForegroundColor Yellow
    $errors++
}

# Test 4: Frontend accessible
Write-Host "Test 4: Frontend Loading..." -NoNewline
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host " ✓" -ForegroundColor Green
    } else {
        Write-Host " ?" -ForegroundColor Yellow
        $warnings++
    }
} catch {
    Write-Host " ✗" -ForegroundColor Red
    Write-Host "   Frontend not responding at http://localhost:3000" -ForegroundColor Yellow
    $errors++
}

# Test 5: Database connection
Write-Host "Test 5: Database Connection..." -NoNewline
try {
    $dbTest = docker-compose exec -T postgres pg_isready -U nexus 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host " ✓" -ForegroundColor Green
    } else {
        Write-Host " ✗" -ForegroundColor Red
        $errors++
    }
} catch {
    Write-Host " ✗" -ForegroundColor Red
    $errors++
}

# Test 6: Redis connection
Write-Host "Test 6: Redis Connection..." -NoNewline
try {
    $redisTest = docker-compose exec -T redis redis-cli -a redis_dev_pass_123 ping 2>$null
    if ($redisTest -match "PONG") {
        Write-Host " ✓" -ForegroundColor Green
    } else {
        Write-Host " ✗" -ForegroundColor Red
        $errors++
    }
} catch {
    Write-Host " ✗" -ForegroundColor Red
    $errors++
}

# Test 7: API Documentation
Write-Host "Test 7: API Documentation..." -NoNewline
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/docs" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host " ✓" -ForegroundColor Green
    } else {
        Write-Host " ?" -ForegroundColor Yellow
        $warnings++
    }
} catch {
    Write-Host " ✗" -ForegroundColor Red
    $errors++
}

# Test 8: OpenAI API Key (optional)
Write-Host "Test 8: OpenAI API Key..." -NoNewline
$envContent = Get-Content .env -ErrorAction SilentlyContinue
if ($envContent -match "OPENAI_API_KEY=sk-") {
    Write-Host " ✓" -ForegroundColor Green
} else {
    Write-Host " ⚠" -ForegroundColor Yellow
    Write-Host "   OpenAI key not set (AI features limited)" -ForegroundColor Yellow
    $warnings++
}

Write-Host ""
Write-Host "════════════════════════════════════════" -ForegroundColor Blue

# Summary
if ($errors -eq 0 -and $warnings -eq 0) {
    Write-Host "   ✅ ALL TESTS PASSED!" -ForegroundColor Green
    Write-Host "════════════════════════════════════════" -ForegroundColor Blue
    Write-Host ""
    Write-Host "🎉 Your alpha is working perfectly!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 Access your platform:" -ForegroundColor Blue
    Write-Host "   http://localhost:3000" -ForegroundColor Green
    Write-Host ""
    Write-Host "📚 Quick actions:" -ForegroundColor Blue
    Write-Host "   1. Create account at /auth/register"
    Write-Host "   2. Try IDE at /ide"
    Write-Host "   3. Search Grokopedia at /grokopedia"
    Write-Host ""
} elseif ($errors -eq 0) {
    Write-Host "   ✅ TESTS PASSED (with warnings)" -ForegroundColor Yellow
    Write-Host "════════════════════════════════════════" -ForegroundColor Blue
    Write-Host ""
    Write-Host "⚠️ $warnings warnings found (non-critical)" -ForegroundColor Yellow
    Write-Host "Platform should work, but some features may be limited." -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host "   ❌ TESTS FAILED" -ForegroundColor Red
    Write-Host "════════════════════════════════════════" -ForegroundColor Blue
    Write-Host ""
    Write-Host "❌ $errors errors found" -ForegroundColor Red
    Write-Host "⚠️ $warnings warnings found" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please run: .\START_ALPHA_NOW.ps1" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "📊 Detailed status: docker-compose ps" -ForegroundColor Blue
Write-Host "📋 View logs: docker-compose logs -f" -ForegroundColor Blue
Write-Host ""

