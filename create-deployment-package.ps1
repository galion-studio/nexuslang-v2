# Create Deployment Package for RunPod
# Excludes unnecessary files to keep size small

Write-Host ""
Write-Host "📦 Creating RunPod Deployment Package" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

$packageName = "nexuslang-v2-deploy.zip"
$tempDir = ".\deploy-temp"

# Create temp directory
if (Test-Path $tempDir) {
    Remove-Item $tempDir -Recurse -Force
}
New-Item -ItemType Directory -Path $tempDir | Out-Null

Write-Host "📋 Copying essential files..." -ForegroundColor Yellow

# Copy essential directories and files
$itemsToCopy = @(
    "v2\backend",
    "v2\frontend",
    "docker-compose.yml",
    "docker-compose.runpod.yml",
    "runpod-quick-deploy.sh",
    "deploy-to-runpod.sh",
    ".env",
    "*.md",
    "*.sh"
)

# Copy v2 backend (excluding __pycache__)
Write-Host "  Copying v2/backend..." -ForegroundColor Gray
robocopy "v2\backend" "$tempDir\v2\backend" /E /XD __pycache__ .pytest_cache /XF *.pyc /NFL /NDL /NJH /NJS | Out-Null

# Copy v2 frontend (excluding node_modules)
Write-Host "  Copying v2/frontend..." -ForegroundColor Gray
robocopy "v2\frontend" "$tempDir\v2\frontend" /E /XD node_modules .next /NFL /NDL /NJH /NJS | Out-Null

# Copy docker compose files
Write-Host "  Copying Docker files..." -ForegroundColor Gray
Copy-Item "docker-compose.yml" $tempDir -ErrorAction SilentlyContinue
Copy-Item "docker-compose.runpod.yml" $tempDir -ErrorAction SilentlyContinue

# Copy scripts
Write-Host "  Copying scripts..." -ForegroundColor Gray
Copy-Item "runpod-quick-deploy.sh" $tempDir -ErrorAction SilentlyContinue
Copy-Item "deploy-to-runpod.sh" $tempDir -ErrorAction SilentlyContinue
Copy-Item "setup-env.ps1" $tempDir -ErrorAction SilentlyContinue

# Copy .env if exists
if (Test-Path ".env") {
    Write-Host "  Copying .env file..." -ForegroundColor Gray
    Copy-Item ".env" $tempDir
}

# Copy documentation
Write-Host "  Copying documentation..." -ForegroundColor Gray
Get-ChildItem "*.md" | Copy-Item -Destination $tempDir -ErrorAction SilentlyContinue

# Create README for RunPod
$runpodReadme = @"
# NexusLang v2 - RunPod Deployment

## Quick Start

1. Extract this zip to /workspace
2. cd /workspace/nexuslang-v2
3. chmod +x runpod-quick-deploy.sh
4. ./runpod-quick-deploy.sh

## After Deployment

1. Edit .env and add your OPENROUTER_API_KEY
2. docker-compose restart backend
3. Access: https://YOUR_POD_ID-8000.proxy.runpod.net/docs

## Documentation

- RUNPOD_QUICK_START.md - Quick setup
- AI_ROUTER_GUIDE.md - AI features
- 🎉_AI_IMPLEMENTATION_COMPLETE.md - Full details

Get OpenRouter key: https://openrouter.ai/keys
"@

$runpodReadme | Out-File "$tempDir\README_RUNPOD.md" -Encoding UTF8

Write-Host "🗜️  Creating zip file..." -ForegroundColor Yellow

# Remove old package
if (Test-Path $packageName) {
    Remove-Item $packageName -Force
}

# Create zip
Compress-Archive -Path "$tempDir\*" -DestinationPath $packageName -CompressionLevel Optimal

# Cleanup
Remove-Item $tempDir -Recurse -Force

# Get file size
$fileSize = (Get-Item $packageName).Length / 1MB

Write-Host ""
Write-Host "✅ Package created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📦 File: $packageName" -ForegroundColor Cyan
Write-Host "💾 Size: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Cyan
Write-Host ""
Write-Host "📤 Next Steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  1. Upload to RunPod Jupyter Lab:"
Write-Host "     - Open Jupyter Lab on your RunPod pod"
Write-Host "     - Click Upload button"
Write-Host "     - Select: $packageName"
Write-Host ""
Write-Host "  2. In Jupyter terminal:"
Write-Host "     cd /workspace"
Write-Host "     unzip $packageName"
Write-Host "     cd nexuslang-v2"
Write-Host "     chmod +x runpod-quick-deploy.sh"
Write-Host "     ./runpod-quick-deploy.sh"
Write-Host ""
Write-Host "  3. Add API keys to .env and restart"
Write-Host ""
Write-Host "📚 See: UPLOAD_TO_RUNPOD_JUPYTER.md for detailed guide"
Write-Host ""
