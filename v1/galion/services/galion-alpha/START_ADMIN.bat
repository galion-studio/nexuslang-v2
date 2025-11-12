@echo off
echo ========================================
echo   GALION.STUDIO - Admin Panel
echo ========================================
echo.
echo Opening admin panel at http://localhost:9000
echo.
cd /d %~dp0
start http://localhost:9000
py admin.py
pause

