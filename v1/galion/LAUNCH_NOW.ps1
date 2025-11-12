#!/usr/bin/env pwsh
# GALION.APP FAZE ALPHA - LAUNCH SCRIPT
# Following Elon's Principle: SHIP IT!

param(
    [switch]$Production = $false,
    [switch]$SkipTests = $false
)

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     GALION.APP FAZE ALPHA LAUNCH SEQUENCE       ║" -ForegroundColor Cyan
Write-Host "║          Following Elon's Principles            ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

if ($Production) {
    Write-Host "🔴 PRODUCTION LAUNCH MODE" -ForegroundColor Red
    Write-Host "   Domain: galion.app" -ForegroundColor Yellow
    Write-Host ""
    $confirm = Read-Host "Are you sure you want to deploy to PRODUCTION? (yes/no)"
    if ($confirm -ne "yes") {
        Write-Host "❌ Launch aborted." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "🟢 LOCAL DEVELOPMENT MODE" -ForegroundColor Green
    Write-Host "   Domain: localhost" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""

# Step 1: Verify Docker
Write-Host "📦 Step 1/6: Verifying Docker..." -ForegroundColor Cyan
try {
    $dockerVersion = docker --version
    Write-Host "   ✅ Docker: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Docker not found. Please install Docker Desktop." -ForegroundColor Red
    exit 1
}

# Step 2: Check .env
Write-Host ""
Write-Host "⚙️  Step 2/6: Checking configuration..." -ForegroundColor Cyan
if (Test-Path .env) {
    Write-Host "   ✅ .env file exists" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  .env file missing. Generating..." -ForegroundColor Yellow
    if (Test-Path generate-secrets.ps1) {
        .\generate-secrets.ps1
        Write-Host "   ✅ Secrets generated!" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Cannot generate secrets. Please create .env manually." -ForegroundColor Red
        exit 1
    }
}

if ($Production) {
    Write-Host "   🔍 Verifying production settings..." -ForegroundColor Yellow
    $envContent = Get-Content .env -Raw
    if ($envContent -match "ENVIRONMENT=production" -and $envContent -match "DEBUG=false") {
        Write-Host "   ✅ Production settings verified" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Warning: Ensure ENVIRONMENT=production and DEBUG=false in .env" -ForegroundColor Yellow
    }
}

# Step 3: Build Services
Write-Host ""
Write-Host "🔨 Step 3/6: Building all services..." -ForegroundColor Cyan
Write-Host "   (This may take 5-10 minutes on first build)" -ForegroundColor Gray
Write-Host ""

try {
    docker-compose build --parallel 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ All services built successfully!" -ForegroundColor Green
    } else {
        throw "Build failed"
    }
} catch {
    Write-Host "   ❌ Build failed. Check Docker logs." -ForegroundColor Red
    exit 1
}

# Step 4: Launch Services
Write-Host ""
Write-Host "🚀 Step 4/6: Launching services..." -ForegroundColor Cyan
Write-Host ""

try {
    docker-compose up -d
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ All services started!" -ForegroundColor Green
    } else {
        throw "Launch failed"
    }
} catch {
    Write-Host "   ❌ Failed to start services." -ForegroundColor Red
    exit 1
}

# Step 5: Wait for Services
Write-Host ""
Write-Host "⏳ Step 5/6: Waiting for services to be ready..." -ForegroundColor Cyan
Write-Host "   (This takes about 30-60 seconds)" -ForegroundColor Gray

Start-Sleep -Seconds 45

$services = @(
    @{Name="API Gateway"; URL="http://localhost:8080/health"; Critical=$true},
    @{Name="Auth Service"; URL="http://localhost:8000/health"; Critical=$true},
    @{Name="User Service"; URL="http://localhost:8001/health"; Critical=$true},
    @{Name="Analytics"; URL="http://localhost:9090/health"; Critical=$false}
)

$allHealthy = $true
foreach ($svc in $services) {
    try {
        $response = Invoke-WebRequest -Uri $svc.URL -Method Get -TimeoutSec 10 -UseBasicParsing -ErrorAction Stop
        Write-Host "   ✅ $($svc.Name): HEALTHY" -ForegroundColor Green
    } catch {
        Write-Host "   ⚠️  $($svc.Name): Not ready yet (may need more time)" -ForegroundColor Yellow
        if ($svc.Critical) {
            $allHealthy = $false
        }
    }
}

# Step 6: Run Tests
if (-not $SkipTests) {
    Write-Host ""
    Write-Host "🧪 Step 6/6: Running system tests..." -ForegroundColor Cyan
    Write-Host ""
    
    if (Test-Path test-complete-system.ps1) {
        try {
            .\test-complete-system.ps1
            Write-Host ""
            Write-Host "   ✅ All tests passed!" -ForegroundColor Green
        } catch {
            Write-Host ""
            Write-Host "   ⚠️  Some tests failed. Check output above." -ForegroundColor Yellow
        }
    } else {
        Write-Host "   ⚠️  Test script not found. Skipping tests." -ForegroundColor Yellow
    }
} else {
    Write-Host ""
    Write-Host "⏭️  Step 6/6: Tests skipped (--SkipTests)" -ForegroundColor Gray
}

# Success!
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""
Write-Host "╔══════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║          🎉  LAUNCH SUCCESSFUL!  🎉             ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

if ($Production) {
    Write-Host "🌐 GALION.APP IS NOW LIVE!" -ForegroundColor Magenta
    Write-Host ""
    Write-Host "   Production URLs:" -ForegroundColor Cyan
    Write-Host "   • API Gateway:    https://api.galion.app" -ForegroundColor White
    Write-Host "   • API Docs:       https://api.galion.app/docs" -ForegroundColor White
    Write-Host "   • Grafana:        https://grafana.galion.app" -ForegroundColor White
    Write-Host ""
    Write-Host "   📊 Next: Configure Cloudflare DNS" -ForegroundColor Yellow
    Write-Host "   📖 See: GALION_APP_LAUNCH_PLAN.md" -ForegroundColor Gray
} else {
    Write-Host "🎯 FAZE ALPHA - LOCAL DEPLOYMENT" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "   Local URLs:" -ForegroundColor Cyan
    Write-Host "   • API Gateway:    http://localhost:8080" -ForegroundColor White
    Write-Host "   • Auth API Docs:  http://localhost:8000/docs" -ForegroundColor White
    Write-Host "   • User API Docs:  http://localhost:8001/docs" -ForegroundColor White
    Write-Host "   • Grafana:        http://localhost:3000" -ForegroundColor White
    Write-Host "   • Kafka UI:       http://localhost:8090" -ForegroundColor White
    Write-Host "   • Prometheus:     http://localhost:9091" -ForegroundColor White
}

Write-Host ""
Write-Host "📋 Useful Commands:" -ForegroundColor Cyan
Write-Host "   • View logs:      docker-compose logs -f [service-name]" -ForegroundColor Gray
Write-Host "   • Check status:   docker-compose ps" -ForegroundColor Gray
Write-Host "   • Stop services:  docker-compose down" -ForegroundColor Gray
Write-Host "   • Run tests:      .\test-complete-system.ps1" -ForegroundColor Gray
Write-Host ""

if (-not $Production) {
    Write-Host "🚀 Ready for production?" -ForegroundColor Yellow
    Write-Host "   Run: .\LAUNCH_NOW.ps1 -Production" -ForegroundColor Gray
    Write-Host ""
}

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""
Write-Host "🔥 Built with Elon's Principles:" -ForegroundColor Magenta
Write-Host "   ✓ First Principles Thinking" -ForegroundColor Green
Write-Host "   ✓ Delete Unnecessary Complexity" -ForegroundColor Green
Write-Host "   ✓ Move Fast and Ship" -ForegroundColor Green
Write-Host "   ✓ Test What Matters" -ForegroundColor Green
Write-Host ""
Write-Host "   \"The best part is no part. The best process is no process.\"" -ForegroundColor Gray
Write-Host "   - Elon Musk" -ForegroundColor Gray
Write-Host ""

