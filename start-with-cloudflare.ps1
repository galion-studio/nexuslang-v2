# PowerShell Script to Start NexusLang v2 with Cloudflare Tunnels
# This script starts all services including both Cloudflare tunnels

# Display banner
Write-Host "===============================================================" -ForegroundColor Cyan
Write-Host "  Starting NexusLang v2 with Cloudflare Tunnels" -ForegroundColor Cyan
Write-Host "  Domains: galion.studio & galion.app" -ForegroundColor Cyan
Write-Host "===============================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
Write-Host "[1/4] Checking Docker..." -ForegroundColor Yellow
try {
    docker info > $null 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Docker is not running! Please start Docker Desktop." -ForegroundColor Red
        exit 1
    }
    Write-Host "[OK] Docker is running" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Docker is not installed or not running!" -ForegroundColor Red
    exit 1
}

# Check if .env file exists
Write-Host "`n[2/4] Checking environment configuration..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Write-Host "[WARNING] .env file not found. Creating from template..." -ForegroundColor Yellow
    if (Test-Path "env.template") {
        Copy-Item "env.template" ".env"
        Write-Host "[INFO] Please edit .env file and set your environment variables" -ForegroundColor Cyan
        Write-Host "       Required: POSTGRES_PASSWORD, REDIS_PASSWORD, SECRET_KEY, JWT_SECRET" -ForegroundColor Cyan
        exit 0
    } else {
        Write-Host "[ERROR] env.template not found!" -ForegroundColor Red
        exit 1
    }
}
Write-Host "[OK] Environment configuration found" -ForegroundColor Green

# Stop existing containers if running
Write-Host "`n[3/4] Stopping existing containers..." -ForegroundColor Yellow
docker-compose down > $null 2>&1
Write-Host "[OK] Cleaned up existing containers" -ForegroundColor Green

# Start services with Cloudflare tunnels
Write-Host "`n[4/4] Starting all services..." -ForegroundColor Yellow
Write-Host "   - PostgreSQL (Database)" -ForegroundColor Gray
Write-Host "   - Redis (Cache)" -ForegroundColor Gray
Write-Host "   - Elasticsearch (Search)" -ForegroundColor Gray
Write-Host "   - Backend API" -ForegroundColor Gray
Write-Host "   - Frontend (Next.js)" -ForegroundColor Gray
Write-Host "   - Prometheus (Metrics)" -ForegroundColor Gray
Write-Host "   - Grafana (Monitoring)" -ForegroundColor Gray
Write-Host "   - Cloudflare Tunnel (galion.studio)" -ForegroundColor Gray
Write-Host "   - Cloudflare Tunnel (galion.app)" -ForegroundColor Gray
Write-Host ""

# Start all services
docker-compose -f docker-compose.yml -f docker-compose.cloudflare.yml up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n[SUCCESS] All services started successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "===============================================================" -ForegroundColor Green
    Write-Host "  Access Your Services" -ForegroundColor Green
    Write-Host "===============================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Local Access:" -ForegroundColor Cyan
    Write-Host "   Frontend:    http://localhost:3000" -ForegroundColor White
    Write-Host "   Backend API: http://localhost:8000" -ForegroundColor White
    Write-Host "   Grafana:     http://localhost:3001" -ForegroundColor White
    Write-Host "   Prometheus:  http://localhost:9090" -ForegroundColor White
    Write-Host ""
    Write-Host "Public Access via Cloudflare:" -ForegroundColor Cyan
    Write-Host "   galion.studio domains:" -ForegroundColor Magenta
    Write-Host "     https://galion.studio           (Frontend)" -ForegroundColor White
    Write-Host "     https://www.galion.studio       (Frontend)" -ForegroundColor White
    Write-Host "     https://api.galion.studio       (Backend API)" -ForegroundColor White
    Write-Host "     https://grafana.galion.studio   (Monitoring)" -ForegroundColor White
    Write-Host "     https://prometheus.galion.studio (Metrics)" -ForegroundColor White
    Write-Host ""
    Write-Host "   galion.app domains:" -ForegroundColor Magenta
    Write-Host "     https://galion.app              (Frontend)" -ForegroundColor White
    Write-Host "     https://www.galion.app          (Frontend)" -ForegroundColor White
    Write-Host "     https://api.galion.app          (Backend API)" -ForegroundColor White
    Write-Host "     https://grafana.galion.app      (Monitoring)" -ForegroundColor White
    Write-Host "     https://prometheus.galion.app   (Metrics)" -ForegroundColor White
    Write-Host ""
    Write-Host "Useful Commands:" -ForegroundColor Cyan
    Write-Host "   View logs:         docker-compose logs -f" -ForegroundColor White
    Write-Host "   Stop services:     docker-compose down" -ForegroundColor White
    Write-Host "   Restart services:  docker-compose restart" -ForegroundColor White
    Write-Host "   View status:       docker-compose ps" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "`n[ERROR] Failed to start services!" -ForegroundColor Red
    Write-Host "[INFO] Check logs with: docker-compose logs" -ForegroundColor Yellow
    exit 1
}
