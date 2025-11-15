@echo off
REM ============================================
REM Quick SSH Setup for RunPod
REM ============================================
REM Run this on your Windows laptop

echo.
echo ============================================
echo   CURSOR SSH PIPELINE SETUP
echo ============================================
echo.

echo [1/3] Pulling latest code from GitHub...
git pull origin clean-nexuslang

echo.
echo [2/3] Navigating to SSH pipeline...
cd cursor-ssh-pipeline

echo.
echo [3/3] Running setup script...
echo.
powershell -ExecutionPolicy Bypass -File setup-local-ssh.ps1 -RunPodIP "213.173.105.83"

echo.
echo ============================================
echo   SETUP COMPLETE!
echo ============================================
echo.
echo NEXT STEP: Copy the public key shown above
echo Then run these commands in your RunPod terminal:
echo.
echo mkdir -p ~/.ssh
echo echo 'YOUR_PUBLIC_KEY' ^>^> ~/.ssh/authorized_keys
echo chmod 600 ~/.ssh/authorized_keys
echo.
pause

