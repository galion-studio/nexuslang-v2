@echo off
REM Startup script for CMS Backend (Windows)

echo ========================================
echo   Starting CMS Backend API
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Start the FastAPI server
echo.
echo ========================================
echo   CMS API is starting...
echo   API URL: http://localhost:8000
echo   Documentation: http://localhost:8000/docs
echo ========================================
echo.

REM Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

