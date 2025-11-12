@echo off
REM Quick Start Script - Launches both backend and frontend (Windows)

echo ========================================
echo   Starting Complete CMS System
echo ========================================
echo.
echo This will start:
echo  1. Backend API (http://localhost:8000)
echo  2. Frontend UI (http://localhost:3000)
echo.
echo Press Ctrl+C to stop the system
echo.

REM Start backend in new window
start "CMS Backend" cmd /k "start-backend.bat"

REM Wait a few seconds for backend to start
timeout /t 5 /nobreak > nul

REM Start frontend in new window
start "CMS Frontend" cmd /k "cd frontend && start-frontend.bat"

echo.
echo ========================================
echo   CMS System Starting...
echo.
echo   Backend API: http://localhost:8000/docs
echo   Frontend UI: http://localhost:3000
echo.
echo   Two windows will open for backend and frontend.
echo   Close those windows to stop the services.
echo ========================================
echo.

pause

