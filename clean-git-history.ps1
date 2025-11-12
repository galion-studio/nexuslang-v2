# ╔════════════════════════════════════════════════════════════╗
# ║  Clean Git History - Remove Secrets Completely            ║
# ║  Use BFG Repo-Cleaner for safe history rewriting          ║
# ╚════════════════════════════════════════════════════════════╝

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Red
Write-Host "║  🔒 Git History Cleaning - Remove Leaked Secrets           ║" -ForegroundColor Red
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Red
Write-Host ""

Write-Host "⚠️  WARNING: This will rewrite git history!" -ForegroundColor Yellow
Write-Host "   Only do this if the secret was accidentally committed." -ForegroundColor Yellow
Write-Host ""

$confirm = Read-Host "Continue? (type 'YES' to confirm)"
if ($confirm -ne "YES") {
    Write-Host "Aborted." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Method 1: Amend Last Commit (Simplest)" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "If the secret is only in the most recent commit:" -ForegroundColor White
Write-Host ""
Write-Host "  git reset --soft HEAD~1" -ForegroundColor Gray
Write-Host "  # Edit files to remove secret" -ForegroundColor Gray
Write-Host "  git add -A" -ForegroundColor Gray
Write-Host "  git commit -m 'Your message (without secret)'" -ForegroundColor Gray
Write-Host "  git push --force-with-lease origin main" -ForegroundColor Gray
Write-Host ""

Write-Host "Method 2: Filter Entire History (Nuclear Option)" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "To remove the secret from ALL commits:" -ForegroundColor White
Write-Host ""
Write-Host "# Using git-filter-repo (recommended)" -ForegroundColor Yellow
Write-Host "pip install git-filter-repo" -ForegroundColor Gray
Write-Host "git filter-repo --invert-paths --path 'file-with-secret.md'" -ForegroundColor Gray
Write-Host ""
Write-Host "# Or use BFG Repo-Cleaner (faster)" -ForegroundColor Yellow
Write-Host "# Download from: https://rtyley.github.io/bfg-repo-cleaner/" -ForegroundColor Gray
Write-Host "java -jar bfg.jar --replace-text passwords.txt" -ForegroundColor Gray
Write-Host ""

Write-Host "Method 3: Start Fresh (Safest for Public Repo)" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "For nexuslang-v2 (public), start with clean history:" -ForegroundColor White
Write-Host ""
Write-Host "# 1. Create new clean branch without history" -ForegroundColor Yellow
Write-Host "git checkout --orphan clean-main" -ForegroundColor Gray
Write-Host "git add -A" -ForegroundColor Gray
Write-Host "git commit -m 'Initial public release - NexusLang v2 production ready'" -ForegroundColor Gray
Write-Host ""
Write-Host "# 2. Force push to main" -ForegroundColor Yellow
Write-Host "git branch -D main" -ForegroundColor Gray
Write-Host "git branch -m main" -ForegroundColor Gray
Write-Host "git push --force origin main" -ForegroundColor Gray
Write-Host ""

Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "  Recommended Action" -ForegroundColor Green
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""
Write-Host "For PRIVATE repo (project-nexus):" -ForegroundColor White
Write-Host "  → Use Method 3 (start fresh)" -ForegroundColor Yellow
Write-Host "  → This is your private repo, history doesn't matter as much" -ForegroundColor Gray
Write-Host ""
Write-Host "For PUBLIC repo (nexuslang-v2):" -ForegroundColor White
Write-Host "  → Use separate push script (push-to-public-repo.ps1)" -ForegroundColor Yellow
Write-Host "  → Only push v2/ directory, no secrets, clean history" -ForegroundColor Gray
Write-Host ""
Write-Host "Execute this now? Run:" -ForegroundColor Green
Write-Host "  .\start-fresh-clean-history.ps1" -ForegroundColor Cyan
Write-Host ""

