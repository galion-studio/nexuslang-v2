@echo off
echo ========================================
echo   GALION.STUDIO - ULTRA FAST START
echo ========================================
echo.

REM Start Backend
echo Starting Backend...
start "GALION Backend" cmd /k "cd /d %~dp0 && py app.py"
timeout /t 5 /nobreak >nul

REM Seed Database
echo Seeding Database...
curl -X POST http://localhost:5000/api/seed
echo.

REM Start Frontend on port 3001
echo Starting Frontend...
start "GALION Frontend" cmd /k "cd /d %~dp0frontend && set PORT=3001 && npm start"

REM Wait and open browser
echo.
echo ========================================
echo   GALION.STUDIO is starting!
echo ========================================
echo.
echo Backend:  http://localhost:5000
echo Frontend: http://localhost:3001
echo.
echo Wait 30 seconds for frontend to compile...
timeout /t 30 /nobreak >nul
start http://localhost:3001

echo.
echo Done! Browser opening...
pause

