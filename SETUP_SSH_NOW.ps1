# ============================================
# Quick SSH Setup for RunPod
# ============================================
# Run this on your Windows laptop

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  CURSOR SSH PIPELINE SETUP" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/3] Pulling latest code from GitHub..." -ForegroundColor Yellow
git pull origin clean-nexuslang

Write-Host ""
Write-Host "[2/3] Navigating to SSH pipeline..." -ForegroundColor Yellow
Set-Location cursor-ssh-pipeline

Write-Host ""
Write-Host "[3/3] Running setup script..." -ForegroundColor Yellow
Write-Host ""

# Run the setup
.\setup-local-ssh.ps1 -RunPodIP "213.173.105.83"

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  READY TO TEST!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "After adding your public key to RunPod, test the connection:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  ssh runpod" -ForegroundColor White
Write-Host ""
Write-Host "Then deploy:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  .\deploy.ps1" -ForegroundColor White
Write-Host ""

