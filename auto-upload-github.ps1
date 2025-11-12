# Automatic Upload via GitHub (Easiest Method)
# Push to GitHub, then clone on RunPod

Write-Host ""
Write-Host "📤 Auto Upload via GitHub" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check if git repo exists
if (-not (Test-Path ".git")) {
    Write-Host "📝 Initializing git repository..." -ForegroundColor Yellow
    git init
    Write-Host "✅ Git initialized" -ForegroundColor Green
}

# Step 2: Create .gitignore if needed
if (-not (Test-Path ".gitignore")) {
    Write-Host "📝 Creating .gitignore..." -ForegroundColor Yellow
    
    $gitignore = @"
# Environment
.env
.env.local
*.log

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/

# Node
node_modules/
.next/
dist/
build/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Data
*.db
*.sqlite
data/
logs/

# Docker
.docker/
"@
    
    $gitignore | Out-File -FilePath ".gitignore" -Encoding UTF8
    Write-Host "✅ .gitignore created" -ForegroundColor Green
}

# Step 3: Check git status
Write-Host ""
Write-Host "📊 Git status:" -ForegroundColor Yellow
git status --short

# Step 4: Add files
Write-Host ""
Write-Host "➕ Adding files..." -ForegroundColor Yellow
git add .
Write-Host "✅ Files staged" -ForegroundColor Green

# Step 5: Commit
Write-Host ""
Write-Host "💾 Creating commit..." -ForegroundColor Yellow
$commitMessage = "Deploy NexusLang v2 with AI Router - $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
git commit -m $commitMessage
Write-Host "✅ Committed" -ForegroundColor Green

# Step 6: Check for remote
Write-Host ""
$hasRemote = git remote -v
if (-not $hasRemote) {
    Write-Host "⚠️  No git remote configured" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please add your GitHub repository:" -ForegroundColor Cyan
    Write-Host "   1. Create repo at: https://github.com/new"
    Write-Host "   2. Run: git remote add origin YOUR_GITHUB_URL"
    Write-Host "   3. Run: git push -u origin main"
    Write-Host ""
    Write-Host "Then on RunPod, run:" -ForegroundColor Cyan
    Write-Host "   cd /workspace"
    Write-Host "   git clone YOUR_GITHUB_URL nexuslang-v2"
    Write-Host "   cd nexuslang-v2"
    Write-Host "   chmod +x runpod-quick-deploy.sh"
    Write-Host "   ./runpod-quick-deploy.sh"
} else {
    Write-Host "🚀 Pushing to GitHub..." -ForegroundColor Yellow
    git push
    
    Write-Host ""
    Write-Host "✅ Pushed to GitHub!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Next: Run on RunPod Jupyter terminal:" -ForegroundColor Cyan
    Write-Host ""
    
    $repoUrl = (git remote get-url origin)
    Write-Host "cd /workspace" -ForegroundColor Green
    Write-Host "git clone $repoUrl nexuslang-v2" -ForegroundColor Green
    Write-Host "cd nexuslang-v2" -ForegroundColor Green
    Write-Host "chmod +x runpod-quick-deploy.sh" -ForegroundColor Green
    Write-Host "./runpod-quick-deploy.sh" -ForegroundColor Green
    Write-Host ""
}

Write-Host "✨ Ready for RunPod deployment!" -ForegroundColor Green

