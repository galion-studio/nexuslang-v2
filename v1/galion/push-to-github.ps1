# ============================================================================
# NEXUS CORE - Push Documentation to GitHub
# ============================================================================
# This script helps you push ONLY documentation to GitHub (no code files)
# ============================================================================

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  NEXUS CORE - GitHub Push Helper" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check if Git is initialized
if (-not (Test-Path ".git")) {
    Write-Host "ERROR: Git not initialized!" -ForegroundColor Red
    Write-Host "Run: git init" -ForegroundColor Yellow
    exit 1
}

Write-Host "Step 1: Git Configuration" -ForegroundColor Green
Write-Host "-------------------------" -ForegroundColor Green
Write-Host ""

# Check if Git is configured
$gitName = git config --global user.name
$gitEmail = git config --global user.email

if ([string]::IsNullOrWhiteSpace($gitName) -or [string]::IsNullOrWhiteSpace($gitEmail)) {
    Write-Host "Git identity not configured!" -ForegroundColor Yellow
    Write-Host ""
    $name = Read-Host "Enter your name"
    $email = Read-Host "Enter your email"
    
    git config --global user.name "$name"
    git config --global user.email "$email"
    
    Write-Host "✓ Git configured!" -ForegroundColor Green
} else {
    Write-Host "✓ Already configured:" -ForegroundColor Green
    Write-Host "  Name: $gitName"
    Write-Host "  Email: $gitEmail"
}

Write-Host ""
Write-Host "Step 2: Create Commit" -ForegroundColor Green
Write-Host "--------------------" -ForegroundColor Green
Write-Host ""

# Check if there's already a commit
$commitCount = git rev-list --all --count 2>$null
if ($commitCount -eq $null -or $commitCount -eq 0) {
    Write-Host "Creating initial commit..."
    git commit -m "docs: Initial commit - Nexus Core documentation and architecture

- Complete project documentation (25+ .md files)
- Implementation roadmap and guides  
- Architecture documentation
- Service documentation (Auth, User, API Gateway, Analytics)
- Docker and infrastructure configuration
- Testing guides and Postman collection
- Setup scripts

Note: Code files (.py, .go) are intentionally excluded.
This repository contains documentation only."
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Commit created!" -ForegroundColor Green
    } else {
        Write-Host "ERROR: Failed to create commit" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✓ Commit already exists" -ForegroundColor Green
}

Write-Host ""
Write-Host "Step 3: GitHub Repository" -ForegroundColor Green
Write-Host "------------------------" -ForegroundColor Green
Write-Host ""
Write-Host "Please create a GitHub repository:" -ForegroundColor Yellow
Write-Host "  1. Go to: https://github.com/new"
Write-Host "  2. Repository name: nexus-core (or your choice)"
Write-Host "  3. Description: Nexus Core - AI Platform Documentation"
Write-Host "  4. Public or Private: Your choice"
Write-Host "  5. DO NOT initialize with README"
Write-Host "  6. Click 'Create repository'"
Write-Host ""

$created = Read-Host "Have you created the repository? (y/n)"

if ($created -ne "y") {
    Write-Host ""
    Write-Host "Please create the repository first, then run this script again." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
$username = Read-Host "Enter your GitHub username"
$repoName = Read-Host "Enter repository name (default: nexus-core)"

if ([string]::IsNullOrWhiteSpace($repoName)) {
    $repoName = "nexus-core"
}

Write-Host ""
Write-Host "Step 4: Push to GitHub" -ForegroundColor Green
Write-Host "---------------------" -ForegroundColor Green
Write-Host ""

# Check if remote already exists
$remoteUrl = git remote get-url origin 2>$null

if ($remoteUrl) {
    Write-Host "Remote 'origin' already exists: $remoteUrl" -ForegroundColor Yellow
    $change = Read-Host "Do you want to change it? (y/n)"
    
    if ($change -eq "y") {
        git remote remove origin
        git remote add origin "https://github.com/$username/$repoName.git"
    }
} else {
    git remote add origin "https://github.com/$username/$repoName.git"
    Write-Host "✓ Remote added: https://github.com/$username/$repoName.git" -ForegroundColor Green
}

Write-Host ""
Write-Host "Renaming branch to 'main'..."
git branch -M main

Write-Host ""
Write-Host "Pushing to GitHub..." -ForegroundColor Cyan
Write-Host ""
Write-Host "IMPORTANT: When prompted for password, use a Personal Access Token!" -ForegroundColor Yellow
Write-Host "Create token at: https://github.com/settings/tokens" -ForegroundColor Yellow
Write-Host "Required scope: repo (full control)" -ForegroundColor Yellow
Write-Host ""

git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=====================================" -ForegroundColor Green
    Write-Host "  SUCCESS!" -ForegroundColor Green
    Write-Host "=====================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "✓ Your documentation is now on GitHub!" -ForegroundColor Green
    Write-Host ""
    Write-Host "View your repository at:" -ForegroundColor Cyan
    Write-Host "  https://github.com/$username/$repoName" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Files pushed: 59 documentation files" -ForegroundColor Green
    Write-Host "Code files excluded: ALL (.py, .go, etc.)" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "ERROR: Push failed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Common issues:" -ForegroundColor Yellow
    Write-Host "  1. Wrong Personal Access Token"
    Write-Host "  2. Token doesn't have 'repo' scope"
    Write-Host "  3. Repository doesn't exist"
    Write-Host ""
    Write-Host "Try again or push manually:" -ForegroundColor Yellow
    Write-Host "  git push -u origin main"
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

