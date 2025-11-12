# Start All Services for Production Deployment
# Run this script to make galion.app fully accessible

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  STARTING GALION.APP PRODUCTION" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Start Docker services
Write-Host "[1/3] Starting Docker services..." -ForegroundColor Yellow
docker-compose up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Docker services failed to start" -ForegroundColor Red
    Write-Host "Make sure Docker Desktop is running!" -ForegroundColor Yellow
    exit 1
}

Write-Host "Waiting for services to be healthy (30 seconds)..." -ForegroundColor Gray
Start-Sleep -Seconds 30

# Step 2: Start Frontend (in background)
Write-Host ""
Write-Host "[2/3] Starting Frontend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"
Start-Sleep -Seconds 5

# Step 3: Start Cloudflare Tunnel (in background)
Write-Host ""
Write-Host "[3/3] Starting Cloudflare Tunnel..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cloudflared tunnel --config cloudflare-tunnel.yml run galion-app"
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  ALL SERVICES STARTED!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "Your site is now accessible at:" -ForegroundColor Yellow
Write-Host "  https://galion.app" -ForegroundColor Cyan
Write-Host "  https://www.galion.app" -ForegroundColor Cyan
Write-Host "  https://api.galion.app" -ForegroundColor Cyan
Write-Host "  https://grafana.galion.app" -ForegroundColor Cyan
Write-Host ""

Write-Host "Monitoring:" -ForegroundColor Yellow
Write-Host "  Frontend window - showing Next.js dev server" -ForegroundColor Gray
Write-Host "  Tunnel window - showing Cloudflare tunnel logs" -ForegroundColor Gray
Write-Host ""

Write-Host "To stop everything:" -ForegroundColor Yellow
Write-Host "  1. Close the Frontend and Tunnel windows" -ForegroundColor Gray
Write-Host "  2. Run: docker-compose down" -ForegroundColor Gray
Write-Host ""

Write-Host "Testing deployment in 30 seconds..." -ForegroundColor Gray
Start-Sleep -Seconds 30

Write-Host ""
Write-Host "Testing URLs..." -ForegroundColor Yellow
$urls = @("https://api.galion.app/health", "https://galion.app")
foreach ($url in $urls) {
    try {
        $response = Invoke-WebRequest -Uri $url -Method Get -TimeoutSec 10 -UseBasicParsing -ErrorAction Stop
        Write-Host "  $url - LIVE! (HTTP $($response.StatusCode))" -ForegroundColor Green
    } catch {
        Write-Host "  $url - Still starting..." -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Deployment complete! Check the windows for logs." -ForegroundColor Green
Write-Host ""

