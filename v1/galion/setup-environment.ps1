# Environment Setup Script for GALION.APP
# Creates .env.local for frontend with default values

Write-Host "================================" -ForegroundColor Cyan
Write-Host "  GALION.APP - Environment Setup " -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if frontend directory exists
if (-not (Test-Path "frontend")) {
    Write-Host "Error: frontend directory not found!" -ForegroundColor Red
    Write-Host "Please run this script from the project root." -ForegroundColor Yellow
    exit 1
}

# Create .env.local if it doesn't exist
$envFile = "frontend/.env.local"

if (Test-Path $envFile) {
    Write-Host "⚠ Warning: $envFile already exists!" -ForegroundColor Yellow
    $overwrite = Read-Host "Overwrite? (y/n)"
    if ($overwrite -ne 'y') {
        Write-Host "Skipping environment setup." -ForegroundColor Yellow
        exit 0
    }
}

# Create .env.local content
$envContent = @"
# GALION.APP Frontend Environment Variables
# Generated automatically by setup-environment.ps1

# Backend Service URLs (Local Development)
NEXT_PUBLIC_API_URL=http://localhost:8080
NEXT_PUBLIC_AUTH_SERVICE_URL=http://localhost:8000
NEXT_PUBLIC_USER_SERVICE_URL=http://localhost:8001
NEXT_PUBLIC_VOICE_SERVICE_URL=http://localhost:8003
NEXT_PUBLIC_DOCUMENT_SERVICE_URL=http://localhost:8004
NEXT_PUBLIC_PERMISSIONS_SERVICE_URL=http://localhost:8005
NEXT_PUBLIC_ANALYTICS_SERVICE_URL=http://localhost:9090

# Optional: AI API Keys (for AI chat feature)
# Uncomment and add your keys:
# NEXT_PUBLIC_OPENAI_API_KEY=sk-...
# NEXT_PUBLIC_ANTHROPIC_API_KEY=sk-ant-...

# Optional: Monitoring & Analytics
# NEXT_PUBLIC_SENTRY_DSN=
# NEXT_PUBLIC_GA_TRACKING_ID=

# Optional: Feature Flags
NEXT_PUBLIC_ENABLE_VOICE=true
NEXT_PUBLIC_ENABLE_AI_CHAT=true
NEXT_PUBLIC_ENABLE_ANALYTICS=true
"@

# Write the file
Write-Host "Creating $envFile..." -ForegroundColor Yellow
$envContent | Out-File -FilePath $envFile -Encoding utf8

Write-Host "✓ Environment file created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Configuration:" -ForegroundColor White
Write-Host "  API Gateway:        http://localhost:8080" -ForegroundColor Gray
Write-Host "  Auth Service:       http://localhost:8000" -ForegroundColor Gray
Write-Host "  User Service:       http://localhost:8001" -ForegroundColor Gray
Write-Host "  Voice Service:      http://localhost:8003" -ForegroundColor Gray
Write-Host "  Document Service:   http://localhost:8004" -ForegroundColor Gray
Write-Host "  Permissions Service: http://localhost:8005" -ForegroundColor Gray
Write-Host "  Analytics Service:  http://localhost:9090" -ForegroundColor Gray
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "  1. Review $envFile" -ForegroundColor Gray
Write-Host "  2. Add AI API keys if needed (optional)" -ForegroundColor Gray
Write-Host "  3. Run: .\launch-galion.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "✨ Ready to launch! ✨" -ForegroundColor Green

