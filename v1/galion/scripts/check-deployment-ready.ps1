# GALION Deployment Readiness Check
# Simple PowerShell script to verify files before VPS deployment

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  GALION Deployment Readiness Check" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green

$errors = 0
$warnings = 0

# Check critical files
Write-Host "Checking critical files..." -ForegroundColor Cyan

$criticalFiles = @(
    "docker-compose.yml",
    ".env.example",
    "scripts/generate-secrets.sh",
    "scripts/full-deployment.sh",
    "scripts/backup.sh",
    "scripts/health-check.sh",
    "configs/postgresql.conf",
    "nginx/nginx.conf"
)

foreach ($file in $criticalFiles) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $file MISSING" -ForegroundColor Red
        $errors++
    }
}

Write-Host "`nChecking documentation..." -ForegroundColor Cyan

$docs = @(
    "DEPLOYMENT_CHECKLIST.md",
    "START_DEPLOYMENT.md",
    "docs/RUNBOOK.md",
    "docs/TROUBLESHOOTING.md"
)

foreach ($doc in $docs) {
    if (Test-Path $doc) {
        Write-Host "  ✓ $doc" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ $doc missing" -ForegroundColor Yellow
        $warnings++
    }
}

Write-Host "`nChecking .env configuration..." -ForegroundColor Cyan

if (Test-Path ".env") {
    Write-Host "  ✓ .env file exists" -ForegroundColor Green
    $envContent = Get-Content ".env" -Raw
    
    if ($envContent -match "POSTGRES_PASSWORD=\S+") {
        Write-Host "  ✓ POSTGRES_PASSWORD configured" -ForegroundColor Green
    } else {
        Write-Host "  ✗ POSTGRES_PASSWORD not set" -ForegroundColor Red
        $errors++
    }
    
    if ($envContent -match "OPENAI_API_KEY=sk-") {
        Write-Host "  ✓ OPENAI_API_KEY configured" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ OPENAI_API_KEY not set or placeholder" -ForegroundColor Yellow
        $warnings++
    }
} else {
    Write-Host "  ⚠ .env file not found (will be created on server)" -ForegroundColor Yellow
    $warnings++
}

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  SUMMARY" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green

Write-Host "Errors: $errors" -ForegroundColor $(if ($errors -eq 0) { "Green" } else { "Red" })
Write-Host "Warnings: $warnings" -ForegroundColor $(if ($warnings -eq 0) { "Green" } else { "Yellow" })
Write-Host ""

if ($errors -eq 0) {
    Write-Host "✅ READY TO DEPLOY!" -ForegroundColor Green
    Write-Host "`nNext steps:" -ForegroundColor Cyan
    Write-Host "  1. SSH to server: ssh root@54.37.161.67" -ForegroundColor White
    Write-Host "  2. Follow: START_DEPLOYMENT.md" -ForegroundColor White
    Write-Host "  3. Upload files or clone from git" -ForegroundColor White
} else {
    Write-Host "✗ NOT READY - Fix errors above" -ForegroundColor Red
}

Write-Host ""

