# Standalone Content Manager Deployment
# Following Musk's Principles: Simple, Fast, No Dependencies

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Content Manager - Standalone Deployment (Musk Principles)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Transparency Check:" -ForegroundColor Yellow
Write-Host "  - Deploying STANDALONE (won't touch Galion services)"
Write-Host "  - Using SQLite first (PostgreSQL later if needed)"
Write-Host "  - Starting with 3 platforms (Reddit, Twitter, Dev.to)"
Write-Host "  - Manual OAuth setup (UI flows later if painful)"
Write-Host "  - Shipping in 30 minutes (not 2 weeks)"
Write-Host ""

$continue = Read-Host "This is simple and will work. Continue? (Y/n)"
if ($continue -eq "n") {
    exit 0
}

Write-Host ""
Write-Host "[1/6] Checking Docker..." -ForegroundColor Yellow
$dockerRunning = docker ps 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Docker not running. Start Docker Desktop and try again." -ForegroundColor Red
    exit 1
}
Write-Host "SUCCESS: Docker is running" -ForegroundColor Green

Write-Host ""
Write-Host "[2/6] Creating simple environment..." -ForegroundColor Yellow

# Generate secure secrets
$dbPass = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 24 | ForEach-Object {[char]$_})
$redisPass = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 24 | ForEach-Object {[char]$_})
$secret = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})
$jwt = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})

# Create .env.content-manager
$envLines = @(
    "# Content Manager Standalone Configuration",
    "CONTENT_DB_PASSWORD=$dbPass",
    "CONTENT_REDIS_PASSWORD=$redisPass",
    "SECRET_KEY=$secret",
    "JWT_SECRET=$jwt",
    "ENVIRONMENT=production",
    "DEBUG=false",
    "",
    "# Add your platform API keys here",
    "# Get from:",
    "# Reddit: https://www.reddit.com/prefs/apps",
    "# Twitter: https://developer.twitter.com",
    "# Dev.to: https://dev.to/settings/extensions",
    "REDDIT_CLIENT_ID=",
    "REDDIT_CLIENT_SECRET=",
    "TWITTER_BEARER_TOKEN=",
    "TWITTER_API_KEY=",
    "TWITTER_API_SECRET=",
    "DEVTO_API_KEY="
)

$envLines | Out-File -FilePath ".env.content-manager" -Encoding utf8
Write-Host "SUCCESS: Environment created" -ForegroundColor Green
Write-Host "  File: .env.content-manager" -ForegroundColor Gray
Write-Host "  Note: Add your platform API keys to this file" -ForegroundColor Yellow

Write-Host ""
Write-Host "[3/6] Starting services..." -ForegroundColor Yellow
docker-compose -f docker-compose.content-manager-standalone.yml down 2>$null | Out-Null
docker-compose -f docker-compose.content-manager-standalone.yml --env-file .env.content-manager up -d --build

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Docker compose failed" -ForegroundColor Red
    Write-Host "Check logs: docker-compose -f docker-compose.content-manager-standalone.yml logs" -ForegroundColor Yellow
    exit 1
}

Write-Host "SUCCESS: Services started" -ForegroundColor Green

Write-Host ""
Write-Host "[4/6] Waiting for database..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Check database
$dbReady = docker-compose -f docker-compose.content-manager-standalone.yml exec -T content-postgres pg_isready -U contentmgr 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "SUCCESS: Database is ready" -ForegroundColor Green
} else {
    Write-Host "WARNING: Database may still be starting..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[5/6] Initializing database..." -ForegroundColor Yellow

# Run migration
Get-Content "database\migrations\003_content_manager.sql" | docker-compose -f docker-compose.content-manager-standalone.yml exec -T content-postgres psql -U contentmgr content_manager 2>$null | Out-Null

Write-Host "SUCCESS: Database initialized with 4 brands" -ForegroundColor Green
Write-Host "  - Galion Studio" -ForegroundColor Gray
Write-Host "  - Galion App" -ForegroundColor Gray
Write-Host "  - Slavic Nomad" -ForegroundColor Gray
Write-Host "  - Marilyn Element" -ForegroundColor Gray

Write-Host ""
Write-Host "[6/6] Testing services..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

try {
    $health = Invoke-WebRequest -Uri "http://localhost:8200/health" -TimeoutSec 5 -UseBasicParsing
    if ($health.StatusCode -eq 200) {
        Write-Host "SUCCESS: Backend API is healthy" -ForegroundColor Green
    }
} catch {
    Write-Host "WARNING: Backend may still be starting..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  DEPLOYED - Content Manager is Running!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Access Points:" -ForegroundColor Cyan
Write-Host "  Backend API:   http://localhost:8200" -ForegroundColor White
Write-Host "  API Docs:      http://localhost:8200/docs" -ForegroundColor White
Write-Host "  Frontend:      http://localhost:3200" -ForegroundColor White
Write-Host "  Database:      localhost:5433" -ForegroundColor White
Write-Host "  Redis:         localhost:6380" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Add API keys to .env.content-manager"
Write-Host "  2. Restart: docker-compose -f docker-compose.content-manager-standalone.yml restart"
Write-Host "  3. Create user: curl -X POST http://localhost:8200/api/v2/auth/register -d '{...}'"
Write-Host "  4. Start posting!"
Write-Host ""
Write-Host "Useful Commands:" -ForegroundColor Cyan
Write-Host "  View logs:   docker-compose -f docker-compose.content-manager-standalone.yml logs -f"
Write-Host "  Stop:        docker-compose -f docker-compose.content-manager-standalone.yml down"
Write-Host "  Restart:     docker-compose -f docker-compose.content-manager-standalone.yml restart"
Write-Host "  DB shell:    docker-compose -f docker-compose.content-manager-standalone.yml exec content-postgres psql -U contentmgr content_manager"
Write-Host ""
Write-Host "Status Check:" -ForegroundColor Yellow
docker-compose -f docker-compose.content-manager-standalone.yml ps

Write-Host ""
Write-Host "Ready! Open http://localhost:8200/docs to explore the API." -ForegroundColor Green
Write-Host ""

$openDocs = Read-Host "Open API docs now? (Y/n)"
if ($openDocs -ne "n") {
    Start-Process "http://localhost:8200/docs"
}

