# ╔════════════════════════════════════════════════════════════╗
# ║  Automated GitHub Push - Private & Public Repos           ║
# ║  Separates proprietary code (private) from open source    ║
# ╚════════════════════════════════════════════════════════════╝

param(
    [string]$Message = "Production deployment ready - all features complete",
    [switch]$SkipSecurityCheck = $false
)

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  🚀 Automated GitHub Push                                  ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Security check first
if (-not $SkipSecurityCheck) {
    Write-Host "🔒 Running security scan..." -ForegroundColor Yellow
    
    # Check for .env files (should not be committed)
    $envFiles = Get-ChildItem -Recurse -Filter "*.env" -File -ErrorAction SilentlyContinue | 
                Where-Object { $_.Name -ne ".env.template" -and $_.Name -ne ".env.example" }
    
    if ($envFiles) {
        Write-Host "❌ SECURITY ALERT: Found .env files that would be committed!" -ForegroundColor Red
        Write-Host ""
        $envFiles | ForEach-Object { Write-Host "  - $($_.FullName)" -ForegroundColor Yellow }
        Write-Host ""
        Write-Host "These files contain secrets and MUST NOT be committed!" -ForegroundColor Red
        Write-Host ""
        $continue = Read-Host "Type 'SKIP' to continue anyway (NOT RECOMMENDED)"
        if ($continue -ne "SKIP") {
            Write-Host "Aborting to prevent secret leak." -ForegroundColor Red
            exit 1
        }
    }
    
    # Check for API keys in code
    Write-Host "Scanning for exposed API keys..." -ForegroundColor Yellow
    $suspiciousPatterns = @(
        "sk-proj-[a-zA-Z0-9]{20,}",
        "sk-or-v1-[a-zA-Z0-9]{20,}",
        "sk-ant-[a-zA-Z0-9]{20,}"
    )
    
    $foundKeys = $false
    foreach ($pattern in $suspiciousPatterns) {
        $matches = Select-String -Pattern $pattern -Path "v2\backend\*.py","v2\frontend\*.ts","v2\frontend\*.tsx" -Recurse -ErrorAction SilentlyContinue
        if ($matches) {
            Write-Host "⚠️  WARNING: Found potential API key pattern:" -ForegroundColor Yellow
            $matches | Select-Object -First 3 | ForEach-Object {
                Write-Host "  $($_.Filename):$($_.LineNumber)" -ForegroundColor Gray
            }
            $foundKeys = $true
        }
    }
    
    if ($foundKeys) {
        Write-Host ""
        $continue = Read-Host "Found potential API keys. Continue? (y/N)"
        if ($continue -ne "y") {
            Write-Host "Aborting for security review." -ForegroundColor Yellow
            exit 1
        }
    } else {
        Write-Host "✅ No exposed API keys found" -ForegroundColor Green
    }
    
    Write-Host ""
}

Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Repository Configuration" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

Write-Host "Your repository structure:" -ForegroundColor White
Write-Host "  📦 project-nexus (PRIVATE)" -ForegroundColor Yellow
Write-Host "     - Contains: Full codebase, including v1, configs, secrets" -ForegroundColor Gray
Write-Host "     - Visibility: Private" -ForegroundColor Gray
Write-Host ""
Write-Host "  📦 nexuslang-v2 (PUBLIC - Open Source)" -ForegroundColor Green
Write-Host "     - Contains: v2/ code only, documentation, examples" -ForegroundColor Gray
Write-Host "     - Visibility: Public" -ForegroundColor Gray
Write-Host ""

$choice = Read-Host "Which repository to update? (1=Private, 2=Public, 3=Both)"

Write-Host ""
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Git Operations" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Check git status
Write-Host "📊 Checking git status..." -ForegroundColor Yellow
$gitStatus = git status --porcelain

if (-not $gitStatus) {
    Write-Host "✅ No changes to commit" -ForegroundColor Green
    exit 0
}

Write-Host "📝 Changes detected:" -ForegroundColor Green
$gitStatus | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
Write-Host ""

# Show what will be committed
Write-Host "🔍 Files to commit:" -ForegroundColor Yellow
git diff --name-only --cached
git diff --name-only
Write-Host ""

$confirm = Read-Host "Proceed with commit? (y/N)"
if ($confirm -ne "y") {
    Write-Host "Aborted by user." -ForegroundColor Yellow
    exit 0
}

# Stage files
Write-Host ""
Write-Host "📦 Staging files..." -ForegroundColor Yellow
git add .

# Show final status
Write-Host "✅ Files staged" -ForegroundColor Green
Write-Host ""

# Commit
Write-Host "💾 Committing changes..." -ForegroundColor Yellow
Write-Host "Message: $Message" -ForegroundColor Gray

try {
    git commit -m "$Message"
    Write-Host "✅ Commit successful" -ForegroundColor Green
} catch {
    Write-Host "❌ Commit failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Push to appropriate remote(s)
if ($choice -eq "1" -or $choice -eq "3") {
    Write-Host "📤 Pushing to PRIVATE repo (project-nexus)..." -ForegroundColor Yellow
    
    try {
        git push origin main
        Write-Host "✅ Pushed to private repo" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Push failed (may need to set up remote): $_" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "To set up private remote:" -ForegroundColor White
        Write-Host "  git remote add origin https://github.com/YOUR-ORG/project-nexus.git" -ForegroundColor Gray
    }
}

if ($choice -eq "2" -or $choice -eq "3") {
    Write-Host ""
    Write-Host "📤 Preparing PUBLIC repo (nexuslang-v2)..." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "⚠️  IMPORTANT: Public repo should only include v2/ code!" -ForegroundColor Yellow
    Write-Host "   Excluding: v1/, private configs, internal docs" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Manual steps for public repo:" -ForegroundColor White
    Write-Host "  1. Copy v2/ to separate folder" -ForegroundColor Gray
    Write-Host "  2. Remove sensitive files" -ForegroundColor Gray
    Write-Host "  3. Push to public GitHub repo" -ForegroundColor Gray
    Write-Host ""
    Write-Host "See: v2/WHAT_IS_PUBLIC.md for details" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  ✅ GITHUB PUSH COMPLETE                                   ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "  1. Verify commit on GitHub" -ForegroundColor Gray
Write-Host "  2. Deploy to RunPod" -ForegroundColor Gray
Write-Host "  3. Configure DNS" -ForegroundColor Gray
Write-Host "  4. Launch!" -ForegroundColor Gray
Write-Host ""

