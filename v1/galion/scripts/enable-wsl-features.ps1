# Enable WSL 2 Features - Run as Administrator

# This script enables Windows features needed for WSL 2
# MUST be run as Administrator

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Enabling WSL 2 Windows Features" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell → Run as Administrator" -ForegroundColor Yellow
    exit 1
}

Write-Host "Enabling Windows Subsystem for Linux..." -ForegroundColor Yellow
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux -NoRestart

if ($LASTEXITCODE -eq 0) {
    Write-Host "OK: Windows Subsystem for Linux enabled" -ForegroundColor Green
} else {
    Write-Host "WARNING: May already be enabled" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Enabling Virtual Machine Platform..." -ForegroundColor Yellow
Enable-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform -NoRestart

if ($LASTEXITCODE -eq 0) {
    Write-Host "OK: Virtual Machine Platform enabled" -ForegroundColor Green
} else {
    Write-Host "WARNING: May already be enabled" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Features Enabled!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "IMPORTANT: You must restart your computer!" -ForegroundColor Yellow
Write-Host ""
Write-Host "After restart:" -ForegroundColor Cyan
Write-Host "  1. Run: wsl --set-default-version 2" -ForegroundColor White
Write-Host "  2. Start Docker Desktop" -ForegroundColor White
Write-Host "  3. Run: .\scripts\build-complete.ps1" -ForegroundColor White
Write-Host ""

# Ask if user wants to restart now
$restart = Read-Host "Restart computer now? (Y/N)"
if ($restart -eq "Y" -or $restart -eq "y") {
    Write-Host "Restarting in 10 seconds..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
    Restart-Computer
}

