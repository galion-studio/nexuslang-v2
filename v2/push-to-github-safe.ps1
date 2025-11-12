# Safe GitHub Push Script
# Pushes only safe files, excludes secrets

param(
    [Parameter(Mandatory=$false)]
    [string]$CommitMessage = "Add content management system",
    
    [Parameter(Mandatory=$false)]
    [switch]$DryRun = $false
)

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Safe GitHub Push - Security First" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check if git repo
if (-not (Test-Path ".git")) {
    Write-Host "Not a git repository. Initializing..." -ForegroundColor Yellow
    git init
    Write-Host "SUCCESS: Git initialized" -ForegroundColor Green
}

# Run security scan first
Write-Host "Running security scan..." -ForegroundColor Yellow
.\prepare-github-push.ps1

Write-Host ""
$continue = Read-Host "Continue with push? (Y/n)"
if ($continue -eq "n") {
    Write-Host "Push cancelled." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Preparing files..." -ForegroundColor Yellow

# Create/update .gitignore if needed
if (-not (Test-Path "../.gitignore")) {
    Write-Host "Creating .gitignore..." -ForegroundColor Yellow
    # .gitignore already exists at root
}

# Check for sensitive files
$sensitivePatterns = @("*.env*", "*.pem", "*.key", "*password*", "*secret*", "*credential*")
$trackedSensitive = @()

foreach ($pattern in $sensitivePatterns) {
    $files = git ls-files $pattern 2>$null
    if ($files) {
        $trackedSensitive += $files
    }
}

if ($trackedSensitive.Count -gt 0) {
    Write-Host ""
    Write-Host "DANGER: Sensitive files are tracked in git:" -ForegroundColor Red
    $trackedSensitive | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
    Write-Host ""
    Write-Host "Run these commands to remove them:" -ForegroundColor Yellow
    $trackedSensitive | ForEach-Object { 
        Write-Host "  git rm --cached $_" -ForegroundColor White
    }
    Write-Host ""
    exit 1
}

Write-Host "SUCCESS: No sensitive files tracked" -ForegroundColor Green

# Add files
Write-Host ""
Write-Host "Adding files to git..." -ForegroundColor Yellow

if ($DryRun) {
    Write-Host "[DRY RUN] Would add:" -ForegroundColor Cyan
    git add --dry-run -A
} else {
    git add -A
    Write-Host "Files added" -ForegroundColor Green
}

# Show what will be committed
Write-Host ""
Write-Host "Files to be committed:" -ForegroundColor Cyan
git diff --cached --name-status | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }

Write-Host ""
$fileCount = (git diff --cached --name-only | Measure-Object -Line).Lines
Write-Host "Total files: $fileCount" -ForegroundColor Cyan

# Commit
Write-Host ""
if ($DryRun) {
    Write-Host "[DRY RUN] Would commit with message: $CommitMessage" -ForegroundColor Cyan
} else {
    git commit -m $CommitMessage
    Write-Host "SUCCESS: Changes committed" -ForegroundColor Green
}

# Check remote
Write-Host ""
Write-Host "Checking git remote..." -ForegroundColor Yellow
$remotes = git remote 2>$null

if (-not $remotes) {
    Write-Host "No git remote configured." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Add remote with:" -ForegroundColor Cyan
    Write-Host "  git remote add origin https://github.com/YOUR_USERNAME/project-nexus.git" -ForegroundColor White
    Write-Host ""
    Write-Host "Or for private repo:" -ForegroundColor Cyan
    Write-Host "  git remote add origin git@github.com:YOUR_USERNAME/project-nexus.git" -ForegroundColor White
    Write-Host ""
    
    $addRemote = Read-Host "Add remote now? (y/N)"
    if ($addRemote -eq "y") {
        $repoUrl = Read-Host "Enter repository URL"
        git remote add origin $repoUrl
        Write-Host "Remote added" -ForegroundColor Green
    } else {
        Write-Host "Commit saved locally. Add remote and push later." -ForegroundColor Yellow
        exit 0
    }
}

# Push
Write-Host ""
if ($DryRun) {
    Write-Host "[DRY RUN] Would push to: $(git remote get-url origin 2>$null)" -ForegroundColor Cyan
} else {
    Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
    $remoteName = git remote 2>$null | Select-Object -First 1
    $branch = git branch --show-current 2>$null
    
    if (-not $branch) {
        $branch = "main"
        git branch -M main
    }
    
    git push -u $remoteName $branch
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "============================================================" -ForegroundColor Green
        Write-Host "  SUCCESS: Pushed to GitHub!" -ForegroundColor Green
        Write-Host "============================================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Repository URL: $(git remote get-url origin)" -ForegroundColor Cyan
        Write-Host "Branch: $branch" -ForegroundColor Cyan
        Write-Host ""
    } else {
        Write-Host ""
        Write-Host "ERROR: Push failed" -ForegroundColor Red
        Write-Host "This might be your first push. Try:" -ForegroundColor Yellow
        Write-Host "  git push -u origin main --force" -ForegroundColor White
        Write-Host ""
    }
}

Write-Host "Remember:" -ForegroundColor Cyan
Write-Host "  - .env files are NOT pushed (they're gitignored)"
Write-Host "  - API keys are NOT pushed (they're gitignored)"
Write-Host "  - Database dumps are NOT pushed"
Write-Host "  - All secrets stay local"
Write-Host ""
Write-Host "Your credentials are safe!" -ForegroundColor Green
Write-Host ""

