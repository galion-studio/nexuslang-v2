#!/usr/bin/env pwsh
# GALION.STUDIO - ONE-COMMAND LAUNCH
# Following Elon Musk's First Principles: Simple, Fast, Effective

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "   GALION.STUDIO - LAUNCHING" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Start Backend
Write-Host "[1/3] Starting Backend..." -ForegroundColor Yellow
$backend = Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$PSScriptRoot'; py app.py"
) -PassThru -WindowStyle Normal

Write-Host "      Backend PID: $($backend.Id)" -ForegroundColor Green
Start-Sleep -Seconds 5

# Step 2: Start Frontend
Write-Host "[2/3] Starting Frontend..." -ForegroundColor Yellow
$frontend = Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$PSScriptRoot\frontend'; `$env:PORT=3001; npm start"
) -PassThru -WindowStyle Normal

Write-Host "      Frontend PID: $($frontend.Id)" -ForegroundColor Green
Start-Sleep -Seconds 20

# Step 3: Open Browser
Write-Host "[3/3] Opening Browser..." -ForegroundColor Yellow
Start-Process "http://localhost:3001"

Write-Host ""
Write-Host "================================" -ForegroundColor Green
Write-Host "   ✅ GALION.STUDIO IS LIVE!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Frontend: http://localhost:3001" -ForegroundColor Cyan
Write-Host "🔧 Backend:  http://localhost:5000" -ForegroundColor Cyan
Write-Host "📊 API Docs: http://localhost:5000/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "Test Users:" -ForegroundColor Yellow
Write-Host "  - john@acme.com   ($120/hr) - Owner" -ForegroundColor Gray
Write-Host "  - sarah@acme.com  ($150/hr) - Contributor" -ForegroundColor Gray
Write-Host "  - mike@acme.com   ($100/hr) - Contributor" -ForegroundColor Gray
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor White
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

