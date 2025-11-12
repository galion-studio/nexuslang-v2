# Security Setup Script (PowerShell Version)
# Run this to set up your development environment with security tools

Write-Host "🔒 Setting up security tools for NexusLang v2..." -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
Write-Host "✓ Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python not found. Please install Python 3.11+." -ForegroundColor Red
    exit 1
}
Write-Host "  Found $pythonVersion" -ForegroundColor Green

# Install pre-commit
Write-Host ""
Write-Host "✓ Installing pre-commit hooks..." -ForegroundColor Yellow
pip install pre-commit | Out-Null
pre-commit install
pre-commit install --hook-type commit-msg
Write-Host "  ✅ Pre-commit hooks installed" -ForegroundColor Green

# Install security tools
Write-Host ""
Write-Host "✓ Installing security scanning tools..." -ForegroundColor Yellow
pip install safety pip-audit bandit detect-secrets | Out-Null
Write-Host "  ✅ Security tools installed" -ForegroundColor Green

# Generate secrets if not exist
Write-Host ""
Write-Host "✓ Generating secure secrets..." -ForegroundColor Yellow

if (-not (Test-Path ".env")) {
    Write-Host "  Creating .env file..." -ForegroundColor Yellow
    Copy-Item "env.template" ".env"
    
    # Generate JWT secret (PowerShell alternative to openssl)
    $jwt_secret = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 64 | % {[char]$_})
    (Get-Content ".env") -replace "JWT_SECRET_KEY=.*", "JWT_SECRET_KEY=$jwt_secret" | Set-Content ".env"
    
    Write-Host "  ✅ Secrets generated and saved to .env" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  .env already exists, skipping..." -ForegroundColor Yellow
}

# Create secrets baseline
Write-Host ""
Write-Host "✓ Creating secrets baseline..." -ForegroundColor Yellow
detect-secrets scan > .secrets.baseline
Write-Host "  ✅ Secrets baseline created" -ForegroundColor Green

# Run initial security scan
Write-Host ""
Write-Host "✓ Running initial security scan..." -ForegroundColor Yellow
Set-Location v2\backend

Write-Host "  Checking dependencies..." -ForegroundColor Yellow
safety check -r requirements.txt 2>&1 | Out-Null

Write-Host "  Scanning for secrets..." -ForegroundColor Yellow
detect-secrets scan . 2>&1 | Out-Null

Write-Host "  Running Bandit..." -ForegroundColor Yellow
bandit -r . 2>&1 | Out-Null

Set-Location ..\..

# Summary
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "✅ Security setup complete!" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "What was configured:" -ForegroundColor White
Write-Host "  ✅ Pre-commit hooks for secret detection" -ForegroundColor Green
Write-Host "  ✅ Security scanning tools (safety, bandit, etc.)" -ForegroundColor Green
Write-Host "  ✅ Secure secrets generated in .env" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "  1. Review .env and update API keys if needed" -ForegroundColor Yellow
Write-Host "  2. Run: cd v2\backend; pytest tests\test_security.py" -ForegroundColor Yellow
Write-Host "  3. Read: SECURITY_DEPLOYMENT_CHECKLIST.md" -ForegroundColor Yellow
Write-Host ""
Write-Host "🔒 Stay secure!" -ForegroundColor Cyan

