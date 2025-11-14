@echo off
REM NexusLang v2 Coding Agent Launcher for Windows
REM Launches the deployment interface with progress bars

echo 🚀 NexusLang v2 Coding Agent Launcher
echo =====================================
echo.

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: Node.js is not installed
    echo Please download and install Node.js from https://nodejs.org/
    echo.
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "galion-studio" (
    echo ❌ Error: galion-studio directory not found
    echo Please run this script from the project-nexus root directory
    echo.
    pause
    exit /b 1
)

echo ✅ Node.js found
echo ✅ Project structure verified
echo.

REM Launch the deployment interface
echo 🌐 Starting NexusLang v2 Coding Agent...
echo 📱 Interface will open at: http://localhost:3001/nexuslang-agent
echo.
echo Features available:
echo   • Enhanced deployment with progress bars
echo   • GitHub integration
echo   • RunPod deployment automation
echo   • Real-time monitoring
echo   • Live platform access
echo.
echo Press Ctrl+C to stop the deployment interface
echo.

node cursor-nexus-deploy.js

pause
