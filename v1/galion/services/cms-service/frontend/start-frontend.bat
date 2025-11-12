@echo off
REM Startup script for CMS Frontend (Windows)

echo ========================================
echo   Starting CMS Frontend
echo ========================================
echo.

REM Check if node_modules exists
if not exist "node_modules" (
    echo Installing dependencies...
    npm install
)

REM Start the React development server
echo.
echo ========================================
echo   CMS Frontend is starting...
echo   URL: http://localhost:3000
echo ========================================
echo.

npm start

