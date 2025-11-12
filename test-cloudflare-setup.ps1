# Test Script to Verify Cloudflare Tunnel Setup
# This checks if all required files and configurations are in place

Write-Host "===============================================================" -ForegroundColor Cyan
Write-Host "  Testing Cloudflare Tunnel Setup" -ForegroundColor Cyan
Write-Host "===============================================================" -ForegroundColor Cyan
Write-Host ""

$allGood = $true

# Check required files
Write-Host "Checking Required Files..." -ForegroundColor Yellow
$requiredFiles = @(
    "docker-compose.yml",
    "docker-compose.cloudflare.yml",
    "cloudflare-tunnel-galion-studio.yml",
    "cloudflare-tunnel-galion-app.yml",
    "start-with-cloudflare.ps1",
    "start-with-cloudflare.sh"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "  [OK] $file" -ForegroundColor Green
    } else {
        Write-Host "  [MISSING] $file" -ForegroundColor Red
        $allGood = $false
    }
}

# Check Docker
Write-Host "`nChecking Docker..." -ForegroundColor Yellow
try {
    docker info > $null 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] Docker is running" -ForegroundColor Green
    } else {
        Write-Host "  [ERROR] Docker is not running" -ForegroundColor Red
        $allGood = $false
    }
} catch {
    Write-Host "  [ERROR] Docker not found" -ForegroundColor Red
    $allGood = $false
}

# Check .env file
Write-Host "`nChecking Environment Configuration..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "  [OK] .env file exists" -ForegroundColor Green
    
    # Check for critical variables
    $envContent = Get-Content ".env" -Raw
    $criticalVars = @(
        "POSTGRES_PASSWORD",
        "REDIS_PASSWORD",
        "JWT_SECRET_KEY"
    )
    
    foreach ($var in $criticalVars) {
        if ($envContent -match "$var=.+") {
            Write-Host "  [OK] $var is set" -ForegroundColor Green
        } else {
            Write-Host "  [WARNING] $var might need to be configured" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "  [WARNING] .env file not found (will be created from template)" -ForegroundColor Yellow
}

# Check tunnel tokens in docker-compose
Write-Host "`nChecking Tunnel Tokens..." -ForegroundColor Yellow
if (Test-Path "docker-compose.cloudflare.yml") {
    $dockerContent = Get-Content "docker-compose.cloudflare.yml" -Raw
    if ($dockerContent -match "cloudflared-studio") {
        Write-Host "  [OK] galion.studio tunnel configured" -ForegroundColor Green
    }
    if ($dockerContent -match "cloudflared-app") {
        Write-Host "  [OK] galion.app tunnel configured" -ForegroundColor Green
    }
}

# Summary
Write-Host ""
Write-Host "===============================================================" -ForegroundColor Cyan
if ($allGood) {
    Write-Host "  Setup Complete - Ready to Start!" -ForegroundColor Green
} else {
    Write-Host "  Some Issues Found - Please Review Above" -ForegroundColor Yellow
}
Write-Host "===============================================================" -ForegroundColor Cyan

Write-Host "`nNext Steps:" -ForegroundColor Cyan
Write-Host "   1. Make sure .env file is configured" -ForegroundColor White
Write-Host "   2. Run: .\start-with-cloudflare.ps1" -ForegroundColor White
Write-Host "   3. Wait 30-60 seconds for services to start" -ForegroundColor White
Write-Host "   4. Visit: https://galion.studio or https://galion.app" -ForegroundColor White
Write-Host ""
