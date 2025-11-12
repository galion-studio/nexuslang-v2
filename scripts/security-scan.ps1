# Quick Security Scan Script (PowerShell Version)
# Run this anytime to check your codebase security

Write-Host "🔒 Running comprehensive security scan..." -ForegroundColor Cyan
Write-Host ""

# Track issues found
$ISSUES_FOUND = 0

# Change to backend directory
Set-Location v2\backend

# 1. Dependency vulnerabilities
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "1️⃣  Checking dependency vulnerabilities..." -ForegroundColor White
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
try {
    pip-audit -r requirements.txt 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ No known vulnerabilities in dependencies" -ForegroundColor Green
    } else {
        Write-Host "❌ Vulnerabilities found in dependencies!" -ForegroundColor Red
        $ISSUES_FOUND++
    }
} catch {
    Write-Host "⚠️  pip-audit not available" -ForegroundColor Yellow
}
Write-Host ""

# 2. Secret scanning
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "2️⃣  Scanning for exposed secrets..." -ForegroundColor White
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
try {
    detect-secrets scan --baseline ..\..\..secrets.baseline . 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ No secrets detected" -ForegroundColor Green
    } else {
        Write-Host "❌ Potential secrets found!" -ForegroundColor Red
        detect-secrets scan .
        $ISSUES_FOUND++
    }
} catch {
    Write-Host "⚠️  detect-secrets not available" -ForegroundColor Yellow
}
Write-Host ""

# 3. Static security analysis
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "3️⃣  Running static security analysis (Bandit)..." -ForegroundColor White
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
try {
    bandit -r . -ll 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ No high/medium severity issues found" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Security issues found (see above)" -ForegroundColor Yellow
        $ISSUES_FOUND++
    }
} catch {
    Write-Host "⚠️  Bandit not available" -ForegroundColor Yellow
}
Write-Host ""

# 4. Security tests
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "4️⃣  Running security test suite..." -ForegroundColor White
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
$env:JWT_SECRET_KEY = "test-secret-for-ci-only-min-32-chars-long"
$env:DATABASE_URL = "sqlite+aiosqlite:///./test.db"

try {
    pytest tests\test_security.py -v --tb=short 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ All security tests passed" -ForegroundColor Green
    } else {
        Write-Host "❌ Security tests failed!" -ForegroundColor Red
        $ISSUES_FOUND++
    }
} catch {
    Write-Host "⚠️  pytest not available or tests failed" -ForegroundColor Yellow
    $ISSUES_FOUND++
}
Write-Host ""

# 5. Check for hardcoded credentials
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "5️⃣  Checking for hardcoded credentials..." -ForegroundColor White
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
$creds = Select-String -Path "*.py" -Pattern 'password.*=.*[''"]' -Exclude "*test*","*__pycache__*" -Recurse | Where-Object { $_.Line -notmatch "password_hash" }
if ($creds.Count -eq 0) {
    Write-Host "✅ No hardcoded credentials found" -ForegroundColor Green
} else {
    Write-Host "❌ Possible hardcoded credentials:" -ForegroundColor Red
    $creds
    $ISSUES_FOUND++
}
Write-Host ""

# 6. Check security middleware
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "6️⃣  Checking security middleware configuration..." -ForegroundColor White
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
if (Select-String -Path "main.py" -Pattern "SecurityHeadersMiddleware" -Quiet) {
    Write-Host "✅ Security headers middleware configured" -ForegroundColor Green
} else {
    Write-Host "❌ Security headers middleware not configured!" -ForegroundColor Red
    $ISSUES_FOUND++
}

if (Select-String -Path "main.py" -Pattern "RateLimitMiddleware" -Quiet) {
    Write-Host "✅ Rate limiting middleware configured" -ForegroundColor Green
} else {
    Write-Host "❌ Rate limiting middleware not configured!" -ForegroundColor Red
    $ISSUES_FOUND++
}
Write-Host ""

# Summary
Set-Location ..\..
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "📊 SECURITY SCAN SUMMARY" -ForegroundColor White
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

if ($ISSUES_FOUND -eq 0) {
    Write-Host "✅ All security checks passed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your codebase looks secure. Deploy with confidence! 🚀" -ForegroundColor Cyan
    exit 0
} else {
    Write-Host "❌ Found $ISSUES_FOUND issue(s) that need attention" -ForegroundColor Red
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor White
    Write-Host "  1. Review the issues above" -ForegroundColor Yellow
    Write-Host "  2. Fix critical/high priority issues" -ForegroundColor Yellow
    Write-Host "  3. Run this script again to verify fixes" -ForegroundColor Yellow
    Write-Host "  4. Check: SECURITY_AUDIT_REPORT.md for details" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

