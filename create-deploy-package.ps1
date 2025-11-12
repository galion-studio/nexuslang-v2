# Create deployment package for RunPod
# Simple - just creates a zip file you can upload via browser

Write-Host "📦 Creating RunPod Deployment Package" -ForegroundColor Cyan
Write-Host ""

cd C:\Users\Gigabyte\Documents\project-nexus

Write-Host "Packaging files..." -ForegroundColor Gray

# Create zip with only needed files
Compress-Archive -Path @(
    "v2",
    "docker-compose.runpod.yml", 
    "runpod-deploy.sh",
    "env.runpod.template"
) -DestinationPath nexus-runpod-deploy.zip -Force

$size = (Get-Item nexus-runpod-deploy.zip).Length / 1MB

Write-Host "✅ Package created!" -ForegroundColor Green
Write-Host ""
Write-Host "File: nexus-runpod-deploy.zip" -ForegroundColor Cyan
Write-Host "Size: $([math]::Round($size, 2)) MB" -ForegroundColor Gray
Write-Host "Location: C:\Users\Gigabyte\Documents\project-nexus\" -ForegroundColor Gray
Write-Host ""
Write-Host "📤 Next Steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Open RunPod dashboard in browser" -ForegroundColor White
Write-Host "2. Click your pod → 'Files' button" -ForegroundColor White
Write-Host "3. Navigate to: /workspace" -ForegroundColor White
Write-Host "4. Click 'Upload' and select: nexus-runpod-deploy.zip" -ForegroundColor White
Write-Host "5. Wait for upload to complete" -ForegroundColor White
Write-Host ""
Write-Host "Then in RunPod terminal:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  cd /workspace" -ForegroundColor Cyan
Write-Host "  unzip -o nexus-runpod-deploy.zip" -ForegroundColor Cyan
Write-Host "  chmod +x runpod-deploy.sh" -ForegroundColor Cyan
Write-Host "  ./runpod-deploy.sh" -ForegroundColor Cyan
Write-Host ""
Write-Host "🚀 That's it!" -ForegroundColor Green
Write-Host ""

# Open explorer to show the file
explorer.exe /select,"$PWD\nexus-runpod-deploy.zip"

