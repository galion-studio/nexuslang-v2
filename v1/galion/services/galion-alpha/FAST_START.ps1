# GALION.STUDIO - ULTRA FAST START
Write-Host "Starting GALION.STUDIO..." -ForegroundColor Cyan

# Backend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; Write-Host 'BACKEND' -ForegroundColor Green; py app.py"
Start-Sleep -Seconds 5

# Seed
try { Invoke-RestMethod "http://localhost:5000/api/seed" -Method Post | Out-Null; Write-Host "Database seeded" -ForegroundColor Green } catch {}

# Frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\frontend'; `$env:PORT=3001; Write-Host 'FRONTEND' -ForegroundColor Green; npm start"

Write-Host "`nStarted!" -ForegroundColor Green
Write-Host "Backend:  http://localhost:5000" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:3001" -ForegroundColor Cyan
Write-Host "`nOpening browser in 30 seconds..." -ForegroundColor Yellow

Start-Sleep -Seconds 30
Start-Process "http://localhost:3001"

