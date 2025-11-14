@echo off
echo 🚀 Starting Galion Ecosystem...
echo.

set STARTED_SERVICES=0

echo Starting Galion App (Port 3010)...
cd galion-app
if exist package.json (
    echo Installing dependencies...
    call npm install
    echo Starting service...
    start "Galion App" npm run dev
    timeout /t 5 /nobreak > nul
    echo Galion App started on port 3010
    set /a STARTED_SERVICES+=1
) else (
    echo ERROR: package.json not found in galion-app
)
cd ..
echo.

echo Starting Developer Platform (Port 3020)...
cd developer-platform
if exist package.json (
    echo Installing dependencies...
    call npm install
    echo Starting service...
    start "Developer Platform" npm run dev
    timeout /t 5 /nobreak > nul
    echo Developer Platform started on port 3020
    set /a STARTED_SERVICES+=1
) else (
    echo ERROR: package.json not found in developer-platform
)
cd ..
echo.

echo Starting Galion Studio (Port 3030)...
cd galion-studio
if exist package.json (
    echo Installing dependencies...
    call npm install
    echo Starting service...
    start "Galion Studio" npm run dev
    timeout /t 5 /nobreak > nul
    echo Galion Studio started on port 3030
    set /a STARTED_SERVICES+=1
) else (
    echo ERROR: package.json not found in galion-studio
)
cd ..
echo.

echo 🎯 DEPLOYMENT SUMMARY:
echo Services started: %STARTED_SERVICES% / 3
echo.

if %STARTED_SERVICES% gtr 0 (
    echo 🌐 ACCESS YOUR GALION ECOSYSTEM:
    echo Galion.app (Voice):     http://localhost:3010
    echo Developer Platform:     http://localhost:3020
    echo Galion Studio:         http://localhost:3030
    echo Backend API:           http://localhost:8010
    echo.
    echo 🎉 Galion Ecosystem is LIVE!
) else (
    echo ❌ No services were started successfully
)

echo.
pause
