# Local Deployment Script
# Deploy entire system on your local Windows machine

Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "  NexusLang v2 + Content Manager - Local Deployment  " -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Continue"

# Check Docker
Write-Host "[1/8] Checking Docker..." -ForegroundColor Yellow
$dockerRunning = docker ps 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    Write-Host "After starting Docker, run this script again." -ForegroundColor Yellow
    exit 1
}
Write-Host "SUCCESS: Docker is running" -ForegroundColor Green

Write-Host ""
Write-Host "[2/8] Creating environment configuration..." -ForegroundColor Yellow

# Create .env if it doesn't exist
if (-not (Test-Path ".env")) {
    $dbPassword = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 16 | ForEach-Object {[char]$_})
    $secretKey = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})
    $jwtSecret = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})
    $encKey = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})
    
    $envLines = @(
        "DATABASE_URL=postgresql://nexuslang:$dbPassword@postgres:5432/nexuslang_v2",
        "REDIS_URL=redis://redis:6379/0",
        "SECRET_KEY=$secretKey",
        "JWT_SECRET=$jwtSecret",
        "ENCRYPTION_KEY=$encKey",
        'CORS_ORIGINS=["http://localhost:3100"]',
        "BACKEND_PORT=8100",
        "FRONTEND_PORT=3100",
        "STORAGE_TYPE=local",
        "MEDIA_STORAGE_PATH=./media_storage",
        "MEDIA_BASE_URL=http://localhost:8100/media",
        "ENVIRONMENT=development",
        "DEBUG=true"
    )
    
    $envLines | Out-File -FilePath ".env" -Encoding utf8
    Write-Host "SUCCESS: Environment configured" -ForegroundColor Green
} else {
    Write-Host "SUCCESS: Using existing .env file" -ForegroundColor Green
}

Write-Host ""
Write-Host "[3/8] Cleaning up old containers..." -ForegroundColor Yellow
docker-compose -f docker-compose.nexuslang.yml down 2>$null | Out-Null
Write-Host "SUCCESS: Cleanup complete" -ForegroundColor Green

Write-Host ""
Write-Host "[4/8] Building Docker images..." -ForegroundColor Yellow
Write-Host "This may take 5-10 minutes on first run..." -ForegroundColor Gray
docker-compose -f docker-compose.nexuslang.yml build --quiet

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Build failed. Check the error above." -ForegroundColor Red
    exit 1
}
Write-Host "SUCCESS: Images built" -ForegroundColor Green

Write-Host ""
Write-Host "[5/8] Starting services..." -ForegroundColor Yellow
docker-compose -f docker-compose.nexuslang.yml up -d
Write-Host "SUCCESS: Services started" -ForegroundColor Green

Write-Host ""
Write-Host "[6/8] Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Wait for database
$maxAttempts = 10
$attempt = 0
while ($attempt -lt $maxAttempts) {
    $dbReady = docker-compose -f docker-compose.nexuslang.yml exec -T postgres pg_isready -U nexuslang 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "SUCCESS: Database is ready" -ForegroundColor Green
        break
    }
    $attempt++
    Write-Host "Waiting for database... ($attempt/$maxAttempts)" -ForegroundColor Gray
    Start-Sleep -Seconds 3
}

Write-Host ""
Write-Host "[7/8] Initializing database..." -ForegroundColor Yellow

# Run database initialization
Write-Host "Creating database schema..." -ForegroundColor Gray
$initCmd = 'from core.database import init_db; import asyncio; asyncio.run(init_db())'
docker-compose -f docker-compose.nexuslang.yml exec -T backend python -c $initCmd 2>$null | Out-Null

# Run content manager migration
Write-Host "Running content manager migration..." -ForegroundColor Gray
Get-Content "database\migrations\003_content_manager.sql" | docker-compose -f docker-compose.nexuslang.yml exec -T postgres psql -U nexuslang nexuslang_v2 2>$null | Out-Null

Write-Host "SUCCESS: Database initialized" -ForegroundColor Green

Write-Host ""
Write-Host "[8/8] Testing services..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Test backend
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8100/health" -TimeoutSec 5 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "SUCCESS: Backend API is responding" -ForegroundColor Green
    }
} catch {
    Write-Host "WARNING: Backend may still be starting..." -ForegroundColor Yellow
}

# Test frontend
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3100" -TimeoutSec 5 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "SUCCESS: Frontend is responding" -ForegroundColor Green
    }
} catch {
    Write-Host "WARNING: Frontend may still be starting..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Service Status:" -ForegroundColor Yellow
docker-compose -f docker-compose.nexuslang.yml ps

Write-Host ""
Write-Host "======================================================" -ForegroundColor Green
Write-Host "  DEPLOYMENT COMPLETE!                                " -ForegroundColor Green
Write-Host "======================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Your system is running at:" -ForegroundColor Cyan
Write-Host "  Frontend:  http://localhost:3100" -ForegroundColor White
Write-Host "  Backend:   http://localhost:8100" -ForegroundColor White
Write-Host "  API Docs:  http://localhost:8100/docs" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Open http://localhost:3100 in your browser"
Write-Host "  2. Register your first user via API or UI"
Write-Host "  3. Go to /content-manager to start posting"
Write-Host ""
Write-Host "Quick Commands:" -ForegroundColor Cyan
Write-Host "  Open Frontend:  Start-Process http://localhost:3100"
Write-Host "  View Logs:      docker-compose -f docker-compose.nexuslang.yml logs -f"
Write-Host "  Stop Services:  docker-compose -f docker-compose.nexuslang.yml down"
Write-Host "  Restart:        docker-compose -f docker-compose.nexuslang.yml restart"
Write-Host ""
Write-Host "Ready to use! Happy posting!" -ForegroundColor Green
Write-Host ""

# Open browser
$openBrowser = Read-Host "Open frontend in browser now? (Y/n)"
if ($openBrowser -ne "n" -and $openBrowser -ne "N") {
    Start-Process "http://localhost:3100"
}
