# GALION.APP - Master Launch Script
# Launches all services in the correct order

Write-Host "================================" -ForegroundColor Cyan
Write-Host "   GALION.APP - LAUNCH SYSTEM   " -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
Write-Host "[1/6] Checking Docker..." -ForegroundColor Yellow
try {
    docker version | Out-Null
    Write-Host "✓ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker is not running!" -ForegroundColor Red
    Write-Host "Please start Docker Desktop and try again." -ForegroundColor Yellow
    exit 1
}

# Check if ports are available
Write-Host ""
Write-Host "[2/6] Checking ports..." -ForegroundColor Yellow
$ports = @(3000, 8000, 8001, 8003, 8004, 8005, 8080, 9090)
$portsInUse = @()

foreach ($port in $ports) {
    $connection = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($connection) {
        $portsInUse += $port
    }
}

if ($portsInUse.Count -gt 0) {
    Write-Host "⚠ Warning: The following ports are already in use: $($portsInUse -join ', ')" -ForegroundColor Yellow
    Write-Host "Services using these ports may fail to start." -ForegroundColor Yellow
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne 'y') {
        exit 1
    }
} else {
    Write-Host "✓ All required ports are available" -ForegroundColor Green
}

# Start backend services
Write-Host ""
Write-Host "[3/6] Starting backend services..." -ForegroundColor Yellow
docker-compose up -d

Start-Sleep -Seconds 5

# Check backend health
Write-Host ""
Write-Host "[4/6] Checking backend health..." -ForegroundColor Yellow
$maxRetries = 30
$retryCount = 0
$backendHealthy = $false

while ($retryCount -lt $maxRetries -and -not $backendHealthy) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8080/health" -TimeoutSec 2 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            $backendHealthy = $true
            Write-Host "✓ Backend services are healthy" -ForegroundColor Green
        }
    } catch {
        $retryCount++
        Write-Host "Waiting for backend... ($retryCount/$maxRetries)" -ForegroundColor Yellow
        Start-Sleep -Seconds 2
    }
}

if (-not $backendHealthy) {
    Write-Host "✗ Backend services failed to start!" -ForegroundColor Red
    Write-Host "Check logs with: docker-compose logs" -ForegroundColor Yellow
    exit 1
}

# Install frontend dependencies if needed
Write-Host ""
Write-Host "[5/6] Preparing frontend..." -ForegroundColor Yellow
if (-not (Test-Path "frontend/node_modules")) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    Set-Location frontend
    npm install
    Set-Location ..
    Write-Host "✓ Frontend dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✓ Frontend dependencies already installed" -ForegroundColor Green
}

# Start frontend
Write-Host ""
Write-Host "[6/6] Starting frontend..." -ForegroundColor Yellow
Set-Location frontend

# Start frontend in background
Start-Process powershell -ArgumentList "-NoExit", "-Command", "npm run dev" -WindowStyle Normal

Set-Location ..

# Wait for frontend to start
Write-Host "Waiting for frontend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

$frontendHealthy = $false
$retryCount = 0

while ($retryCount -lt 30 -and -not $frontendHealthy) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 2 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            $frontendHealthy = $true
        }
    } catch {
        $retryCount++
        Start-Sleep -Seconds 2
    }
}

# Show status
Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "   LAUNCH COMPLETE!   " -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Services Status:" -ForegroundColor White
Write-Host ""

# Check each service
$services = @(
    @{Name="Frontend"; URL="http://localhost:3000"; Port=3000},
    @{Name="API Gateway"; URL="http://localhost:8080/health"; Port=8080},
    @{Name="Auth Service"; URL="http://localhost:8000/health"; Port=8000},
    @{Name="User Service"; URL="http://localhost:8001/health"; Port=8001},
    @{Name="Voice Service"; URL="http://localhost:8003/health"; Port=8003},
    @{Name="Document Service"; URL="http://localhost:8004/health"; Port=8004},
    @{Name="Permissions Service"; URL="http://localhost:8005/health"; Port=8005}
)

foreach ($service in $services) {
    try {
        $response = Invoke-WebRequest -Uri $service.URL -TimeoutSec 2 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "✓ $($service.Name) (port $($service.Port))" -ForegroundColor Green
        } else {
            Write-Host "⚠ $($service.Name) (port $($service.Port))" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "✗ $($service.Name) (port $($service.Port))" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Access Points:" -ForegroundColor White
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "  Frontend:      http://localhost:3000" -ForegroundColor Cyan
Write-Host "  API Gateway:   http://localhost:8080" -ForegroundColor Cyan
Write-Host "  API Docs:      http://localhost:3000/docs" -ForegroundColor Cyan
Write-Host "  Status Page:   http://localhost:3000/status" -ForegroundColor Cyan
Write-Host "  Analytics:     http://localhost:3000/analytics" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

Write-Host "Quick Actions:" -ForegroundColor White
Write-Host "  • Register:    http://localhost:3000/register" -ForegroundColor Gray
Write-Host "  • Login:       http://localhost:3000/login" -ForegroundColor Gray
Write-Host "  • Dashboard:   http://localhost:3000/dashboard" -ForegroundColor Gray
Write-Host ""

Write-Host "Useful Commands:" -ForegroundColor White
Write-Host "  View Logs:     docker-compose logs -f" -ForegroundColor Gray
Write-Host "  Stop All:      docker-compose down" -ForegroundColor Gray
Write-Host "  Restart:       docker-compose restart" -ForegroundColor Gray
Write-Host "  Status:        docker-compose ps" -ForegroundColor Gray
Write-Host ""

Write-Host "Opening browser..." -ForegroundColor Yellow
Start-Sleep -Seconds 2
Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "🚀 GALION.APP IS LIVE! 🚀" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop monitoring (services will continue running)" -ForegroundColor Gray
Write-Host ""

# Monitor services
try {
    while ($true) {
        Start-Sleep -Seconds 5
        
        # Quick health check
        $healthStatus = @()
        foreach ($service in $services) {
            try {
                $response = Invoke-WebRequest -Uri $service.URL -TimeoutSec 1 -UseBasicParsing
                if ($response.StatusCode -eq 200) {
                    $healthStatus += "✓"
                } else {
                    $healthStatus += "⚠"
                }
            } catch {
                $healthStatus += "✗"
            }
        }
        
        Write-Host "`r[$(Get-Date -Format 'HH:mm:ss')] Health: $($healthStatus -join ' ')" -NoNewline -ForegroundColor Gray
    }
} catch {
    Write-Host ""
    Write-Host "Monitoring stopped. Services are still running." -ForegroundColor Yellow
    Write-Host "To stop all services: docker-compose down" -ForegroundColor Yellow
}

