# 🚀 Automatic Git Push & Deploy to RunPod
# Run this on your Windows machine

Write-Host "🚀 Pushing to GitHub..." -ForegroundColor Green

# Navigate to project directory
Set-Location "C:\Users\Gigabyte\Documents\project-nexus"

# Add all files
git add .

# Commit with timestamp
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
git commit -m "Complete implementation - All platforms - $timestamp"

# Push to GitHub
git push origin main

Write-Host "✅ Pushed to GitHub!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Now run this on RunPod:" -ForegroundColor Cyan
Write-Host ""
Write-Host "cd /workspace/project-nexus" -ForegroundColor Yellow
Write-Host "git pull" -ForegroundColor Yellow
Write-Host "bash MASTER_DEPLOY_ALL_PLATFORMS.sh" -ForegroundColor Yellow
Write-Host ""
Write-Host "Or run the auto-deploy command:" -ForegroundColor Cyan
Write-Host "cd /workspace/project-nexus && git pull && bash MASTER_DEPLOY_ALL_PLATFORMS.sh" -ForegroundColor Yellow

