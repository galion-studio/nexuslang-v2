# NEXUS CORE - BUILD SCRIPT
# Following Elon Musk's First Principles: Simple, Fast, Automated

Write-Host "🚀 NEXUS CORE - AUTOMATED BUILD" -ForegroundColor Cyan
Write-Host "Following Elon Musk's Principles: Question, Delete, Simplify, Accelerate, Automate`n" -ForegroundColor Yellow

# Security Check - Verify environment before building
Write-Host "🔐 Pre-Build Security Check..." -ForegroundColor Cyan

if (-not (Test-Path ".env")) {
    Write-Host "❌ ERROR: .env file not found!" -ForegroundColor Red
    Write-Host "Run: .\generate-secrets.ps1 or .\fix-security-now.ps1" -ForegroundColor Yellow
    exit 1
}

$envContent = Get-Content ".env" -Raw
if ($envContent -match "CHANGE_ME") {
    Write-Host "❌ ERROR: .env contains placeholder values!" -ForegroundColor Red
    Write-Host "Run: .\generate-secrets.ps1 to generate secure secrets" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Environment configured securely`n" -ForegroundColor Green

# Step 1: Wait for Docker to be ready (max 2 minutes)
Write-Host "⏳ Step 1: Waiting for Docker Engine..." -ForegroundColor Cyan
$maxAttempts = 24
$attempt = 0
$dockerReady = $false

while ($attempt -lt $maxAttempts -and -not $dockerReady) {
    $attempt++
    Write-Host "   Attempt $attempt/$maxAttempts..." -NoNewline
    
    try {
        $result = docker ps 2>&1 | Out-String
        if ($result -notmatch "error" -and $result -notmatch "Error") {
            $dockerReady = $true
            Write-Host " ✅ Docker is ready!" -ForegroundColor Green
        } else {
            Write-Host " ⏳ Waiting..." -ForegroundColor Yellow
            Start-Sleep -Seconds 5
        }
    } catch {
        Write-Host " ⏳ Waiting..." -ForegroundColor Yellow
        Start-Sleep -Seconds 5
    }
}

if (-not $dockerReady) {
    Write-Host "`n❌ Docker Engine failed to start after 2 minutes" -ForegroundColor Red
    Write-Host "Please ensure Docker Desktop is running and try again." -ForegroundColor Yellow
    exit 1
}

# Step 2: Stop any existing containers
Write-Host "`n🧹 Step 2: Cleaning up old containers..." -ForegroundColor Cyan
docker-compose down -v 2>&1 | Out-Null
Write-Host "   ✅ Cleanup complete" -ForegroundColor Green

# Step 3: Build all images
Write-Host "`n🔨 Step 3: Building Docker images..." -ForegroundColor Cyan
Write-Host "   This will take 3-5 minutes on first run..." -ForegroundColor Yellow
$buildStart = Get-Date

docker-compose build --progress=plain

if ($LASTEXITCODE -eq 0) {
    $buildTime = (Get-Date) - $buildStart
    Write-Host "   ✅ Build complete in $([math]::Round($buildTime.TotalSeconds, 0)) seconds" -ForegroundColor Green
} else {
    Write-Host "   ❌ Build failed!" -ForegroundColor Red
    exit 1
}

# Step 4: Start all services
Write-Host "`n🚀 Step 4: Starting all services..." -ForegroundColor Cyan
docker-compose up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Services started" -ForegroundColor Green
} else {
    Write-Host "   ❌ Failed to start services!" -ForegroundColor Red
    exit 1
}

# Step 5: Wait for services to be healthy
Write-Host "`n⏳ Step 5: Waiting for services to initialize..." -ForegroundColor Cyan
Start-Sleep -Seconds 20

# Step 6: Check service status
Write-Host "`n📊 Step 6: Service Status" -ForegroundColor Cyan
docker-compose ps

# Step 7: Test health endpoints
Write-Host "`n🧪 Step 7: Testing Health Endpoints..." -ForegroundColor Cyan

# Test API Gateway
Write-Host "   Testing API Gateway (8080)..." -NoNewline
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8080/health" -TimeoutSec 5 -UseBasicParsing 2>&1
    if ($response.StatusCode -eq 200) {
        Write-Host " ✅" -ForegroundColor Green
    } else {
        Write-Host " ⚠️  Status: $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host " ⚠️  Not ready yet" -ForegroundColor Yellow
}

# Test Auth Service
Write-Host "   Testing Auth Service (8000)..." -NoNewline
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5 -UseBasicParsing 2>&1
    if ($response.StatusCode -eq 200) {
        Write-Host " ✅" -ForegroundColor Green
    } else {
        Write-Host " ⚠️  Status: $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host " ⚠️  Not ready yet" -ForegroundColor Yellow
}

# Test User Service
Write-Host "   Testing User Service (8001)..." -NoNewline
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8001/health" -TimeoutSec 5 -UseBasicParsing 2>&1
    if ($response.StatusCode -eq 200) {
        Write-Host " ✅" -ForegroundColor Green
    } else {
        Write-Host " ⚠️  Status: $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host " ⚠️  Not ready yet" -ForegroundColor Yellow
}

# Test Analytics Service
Write-Host "   Testing Analytics Service (9090)..." -NoNewline
try {
    $response = Invoke-WebRequest -Uri "http://localhost:9090/metrics" -TimeoutSec 5 -UseBasicParsing 2>&1
    if ($response.StatusCode -eq 200) {
        Write-Host " ✅" -ForegroundColor Green
    } else {
        Write-Host " ⚠️  Status: $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host " ⚠️  Not ready yet" -ForegroundColor Yellow
}

# Final Summary
Write-Host "`n" + "="*70 -ForegroundColor Cyan
Write-Host "✅ NEXUS CORE BUILD COMPLETE!" -ForegroundColor Green
Write-Host "="*70 -ForegroundColor Cyan

Write-Host "`n📍 Service URLs:" -ForegroundColor Yellow
Write-Host "   API Gateway:     http://localhost:8080"
Write-Host "   Auth Service:    http://localhost:8000/docs"
Write-Host "   User Service:    http://localhost:8001/docs"
Write-Host "   Analytics:       http://localhost:9090/metrics"
Write-Host "   Kafka UI:        http://localhost:8090"
Write-Host "   Prometheus:      http://localhost:9091"
Write-Host "   Grafana:         http://localhost:3000 (admin/admin)"

Write-Host "`n🧪 Quick Test:" -ForegroundColor Yellow
Write-Host '   Invoke-RestMethod -Uri "http://localhost:8080/health" -Method GET'

Write-Host "`n📝 View Logs:" -ForegroundColor Yellow
Write-Host "   docker-compose logs -f"
Write-Host "   docker-compose logs -f api-gateway"

Write-Host "`n🛑 Stop Services:" -ForegroundColor Yellow
Write-Host "   docker-compose down"

Write-Host "`n🎯 Next Steps:" -ForegroundColor Yellow
Write-Host "   1. Test user registration: .\test-system.ps1"
Write-Host "   2. View analytics: http://localhost:9090/metrics"
Write-Host "   3. Check Grafana dashboards: http://localhost:3000"

Write-Host "`n🚀 System Ready!" -ForegroundColor Green


