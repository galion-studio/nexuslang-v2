# Galion Platform - RunPod Quick Start (PowerShell)
# "Your imagination is the end."

$ErrorActionPreference = "Continue"

Write-Host "============================================" -ForegroundColor Blue
Write-Host "  GALION PLATFORM - RUNPOD" -ForegroundColor Blue
Write-Host "  Quick Start Script" -ForegroundColor Blue
Write-Host "============================================" -ForegroundColor Blue
Write-Host ""

# Step 1: Check backend
Write-Host "Step 1: Checking backend services..." -ForegroundColor Blue
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8010/health/fast" -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-Host "OK Backend is healthy" -ForegroundColor Green
    }
} catch {
    Write-Host "WARNING Backend not responding" -ForegroundColor Yellow
}
Write-Host ""

# Step 2: Start Galion.app
Write-Host "Step 2: Starting Galion.app..." -ForegroundColor Blue
Push-Location galion-app

if (-not (Test-Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    npm install
}

$galionJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    npm run dev 2>&1
}
Write-Host "OK Galion.app started - Job ID: $($galionJob.Id)" -ForegroundColor Green
Pop-Location
Write-Host ""

# Step 3: Start Developer Platform
Write-Host "Step 3: Starting Developer Platform..." -ForegroundColor Blue
Push-Location developer-platform

if (-not (Test-Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    npm install
}

$devJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    $env:PORT = "3020"
    npm run dev 2>&1
}
Write-Host "OK Developer Platform started - Job ID: $($devJob.Id)" -ForegroundColor Green
Pop-Location
Write-Host ""

# Step 4: Start Galion Studio
Write-Host "Step 4: Starting Galion Studio..." -ForegroundColor Blue
Push-Location galion-studio

if (-not (Test-Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    npm install
}

$studioJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    $env:PORT = "3030"
    npm run dev 2>&1
}
Write-Host "OK Galion Studio started - Job ID: $($studioJob.Id)" -ForegroundColor Green
Pop-Location
Write-Host ""

# Wait for initialization
Write-Host "Waiting for services to initialize..." -ForegroundColor Blue
Start-Sleep -Seconds 15
Write-Host ""

# Display info
Write-Host "============================================" -ForegroundColor Green
Write-Host "  GALION PLATFORM RUNNING!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Access your platforms:" -ForegroundColor Blue
Write-Host ""
Write-Host "Galion.app (Voice-First):"
Write-Host "   http://localhost:3000/voice"
Write-Host "   http://localhost:3000/onboarding"
Write-Host ""
Write-Host "Developer Platform (IDE):"
Write-Host "   http://localhost:3020/ide"
Write-Host ""
Write-Host "Galion Studio (Corporate):"
Write-Host "   http://localhost:3030"
Write-Host ""
Write-Host "Backend API:"
Write-Host "   http://localhost:8010/docs"
Write-Host "   http://localhost:8010/health/fast"
Write-Host ""
Write-Host "Job IDs saved to .galion-jobs.txt" -ForegroundColor Yellow
Write-Host ""
Write-Host "View logs:" -ForegroundColor Yellow
Write-Host "   Receive-Job -Id $($galionJob.Id) -Keep"
Write-Host ""
Write-Host "Stop all services:" -ForegroundColor Yellow
Write-Host "   Get-Content .galion-jobs.txt | ForEach-Object { Stop-Job -Id `$_ ; Remove-Job -Id `$_ }"
Write-Host ""

# Save job IDs
$galionJob.Id, $devJob.Id, $studioJob.Id | Out-File -FilePath ".galion-jobs.txt"
