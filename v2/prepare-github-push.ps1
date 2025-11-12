# Prepare for GitHub Push - Security Scanner
# Checks for secrets and prepares safe push

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  GitHub Security Scanner - Pre-Push Check" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$foundIssues = $false

Write-Host "[1/5] Checking for .env files..." -ForegroundColor Yellow
$envFiles = Get-ChildItem -Recurse -Filter "*.env*" -File 2>$null | Where-Object { $_.Name -match "\.env" }
if ($envFiles) {
    Write-Host "WARNING: Found .env files:" -ForegroundColor Red
    $envFiles | ForEach-Object { Write-Host "  - $($_.FullName)" -ForegroundColor Yellow }
    Write-Host "These will be excluded by .gitignore" -ForegroundColor Green
} else {
    Write-Host "SUCCESS: No .env files found" -ForegroundColor Green
}

Write-Host ""
Write-Host "[2/5] Scanning for API keys in code..." -ForegroundColor Yellow
$patterns = @(
    "sk-[a-zA-Z0-9]{20,}",  # OpenAI keys
    "Bearer [a-zA-Z0-9_-]{20,}",  # Bearer tokens
    "['\`"]password['\`"]\s*[:=]\s*['\`"][^'\`"]+['\`"]",  # Passwords
    "api[_-]?key['\`"]\s*[:=]\s*['\`"][^'\`"]+['\`"]"  # API keys
)

$suspiciousFiles = @()
foreach ($pattern in $patterns) {
    $matches = Select-String -Path "backend\*.py","frontend\*.ts","frontend\*.tsx" -Pattern $pattern -Recurse 2>$null
    if ($matches) {
        $suspiciousFiles += $matches
    }
}

if ($suspiciousFiles.Count -gt 0) {
    Write-Host "WARNING: Found potential secrets in code:" -ForegroundColor Red
    $suspiciousFiles | Select-Object -First 5 | ForEach-Object { 
        Write-Host "  - $($_.Filename):$($_.LineNumber)" -ForegroundColor Yellow 
    }
    $foundIssues = $true
} else {
    Write-Host "SUCCESS: No API keys found in code" -ForegroundColor Green
}

Write-Host ""
Write-Host "[3/5] Checking for IP addresses..." -ForegroundColor Yellow
$ipPattern = "\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"
$ipMatches = Select-String -Path "*.md","*.ps1","*.sh" -Pattern $ipPattern -Recurse 2>$null | Where-Object { 
    $_.Line -notmatch "0\.0\.0\.0|127\.0\.0\.1|localhost|example|your.*ip|192\.168|10\.\d+|172\.(1[6-9]|2[0-9]|3[01])"
}

if ($ipMatches) {
    Write-Host "WARNING: Found real IP addresses in docs:" -ForegroundColor Yellow
    $ipMatches | Select-Object -First 5 | ForEach-Object { 
        Write-Host "  - $($_.Filename):$($_.LineNumber) - $($_.Line.Trim())" -ForegroundColor Gray
    }
    Write-Host "Review these and replace with placeholders like 'YOUR_IP'" -ForegroundColor Yellow
} else {
    Write-Host "SUCCESS: No production IPs found" -ForegroundColor Green
}

Write-Host ""
Write-Host "[4/5] Checking .gitignore..." -ForegroundColor Yellow
if (Test-Path ".gitignore") {
    $gitignoreContent = Get-Content ".gitignore"
    $requiredPatterns = @(".env", "*.pem", "*.db", "api-keys")
    $missing = @()
    foreach ($pattern in $requiredPatterns) {
        if ($gitignoreContent -notmatch [regex]::Escape($pattern)) {
            $missing += $pattern
        }
    }
    
    if ($missing.Count -gt 0) {
        Write-Host "WARNING: .gitignore missing patterns:" -ForegroundColor Yellow
        $missing | ForEach-Object { Write-Host "  - $_" -ForegroundColor Gray }
    } else {
        Write-Host "SUCCESS: .gitignore looks good" -ForegroundColor Green
    }
} else {
    Write-Host "WARNING: No .gitignore found!" -ForegroundColor Red
    $foundIssues = $true
}

Write-Host ""
Write-Host "[5/5] Checking git status..." -ForegroundColor Yellow
$gitStatus = git status --short 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "Git repository found" -ForegroundColor Green
    $untrackedEnv = git ls-files --others --exclude-standard | Where-Object { $_ -match "\.env" }
    if ($untrackedEnv) {
        Write-Host "Found untracked .env files (GOOD - they're ignored):" -ForegroundColor Green
        $untrackedEnv | ForEach-Object { Write-Host "  - $_" -ForegroundColor Gray }
    }
} else {
    Write-Host "Not a git repository (run 'git init' first)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Security Scan Complete" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

if ($foundIssues) {
    Write-Host "⚠️  ISSUES FOUND - Fix before pushing!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Recommended actions:" -ForegroundColor Yellow
    Write-Host "  1. Review warnings above"
    Write-Host "  2. Remove any hardcoded secrets"
    Write-Host "  3. Replace real IPs with placeholders"
    Write-Host "  4. Run this script again"
    Write-Host ""
} else {
    Write-Host "✅ SAFE TO PUSH - No issues found!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Review what will be pushed: git status"
    Write-Host "  2. Add files: git add ."
    Write-Host "  3. Commit: git commit -m 'Add content manager'"
    Write-Host "  4. Push: git push origin main"
    Write-Host ""
    Write-Host "Or use the automated push script:" -ForegroundColor Yellow
    Write-Host "  .\push-to-github-safe.ps1"
    Write-Host ""
}

Write-Host "Remember:" -ForegroundColor Cyan
Write-Host "  - NEVER commit .env files"
Write-Host "  - NEVER commit API keys"
Write-Host "  - NEVER commit passwords"
Write-Host "  - NEVER commit SSH keys"
Write-Host "  - NEVER commit database dumps"
Write-Host ""

