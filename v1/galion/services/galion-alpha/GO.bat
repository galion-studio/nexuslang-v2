@echo off
cd /d %~dp0
start "Backend" cmd /k py app.py
timeout /t 5 /nobreak >nul
curl -s -X POST http://localhost:5000/api/seed >nul
start "Frontend" cmd /k "cd frontend && set PORT=3001 && npm start"
timeout /t 30 /nobreak >nul
start http://localhost:3001

