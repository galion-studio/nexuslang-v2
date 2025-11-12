# Fix Permissions Policy - Restart Services with Updated Security Headers
# This fixes the "Age Verification Required" and geolocation blocking issues

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  FIXING PERMISSIONS POLICY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/4] Rebuilding Auth Service..." -ForegroundColor Yellow
docker-compose build auth-service

Write-Host ""
Write-Host "[2/4] Rebuilding User Service..." -ForegroundColor Yellow
docker-compose build user-service

Write-Host ""
Write-Host "[3/4] Restarting Services..." -ForegroundColor Yellow
docker-compose restart auth-service user-service

Write-Host ""
Write-Host "[4/4] Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  PERMISSIONS POLICY FIXED!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "Changes Applied:" -ForegroundColor Cyan
Write-Host "  - Geolocation: BLOCKED -> ALLOWED (self origin)" -ForegroundColor White
Write-Host "  - Microphone:  BLOCKED -> ALLOWED (self origin)" -ForegroundColor White
Write-Host "  - Camera:      BLOCKED -> ALLOWED (self origin)" -ForegroundColor White
Write-Host ""

Write-Host "Test the fix:" -ForegroundColor Cyan
Write-Host "  1. Open voice-ui.html in Chrome" -ForegroundColor White
Write-Host "  2. Click the microphone button" -ForegroundColor White
Write-Host "  3. You should see permission prompt (not blocked!)" -ForegroundColor White
Write-Host ""

Write-Host "Service URLs:" -ForegroundColor Cyan
Write-Host "  Auth:  http://localhost:8000/health" -ForegroundColor White
Write-Host "  User:  http://localhost:8001/health" -ForegroundColor White
Write-Host ""
