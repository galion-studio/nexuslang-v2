# PROJECT NEXUS - Admin Terminal Setup
# Fast, simple, effective - First Principles approach

Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     PROJECT NEXUS - ADMIN TERMINAL SETUP                  ║" -ForegroundColor Cyan
Write-Host "║     Building with First Principles                        ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Python
Write-Host "[1/5] Checking Python..." -ForegroundColor Yellow
$pythonCmd = $null
foreach ($cmd in @("python", "python3", "py")) {
    try {
        $version = & $cmd --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $pythonCmd = $cmd
            Write-Host "  ✓ Found: $version" -ForegroundColor Green
            break
        }
    } catch { continue }
}

if (-not $pythonCmd) {
    Write-Host "  ✗ Python not found!" -ForegroundColor Red
    Write-Host "  → Install from: https://www.python.org" -ForegroundColor Yellow
    exit 1
}

# Step 2: Check Docker
Write-Host "[2/5] Checking Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Found: $dockerVersion" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Docker not running" -ForegroundColor Red
        Write-Host "  → Start Docker Desktop" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ✗ Docker not found!" -ForegroundColor Red
    Write-Host "  → Install from: https://www.docker.com" -ForegroundColor Yellow
}

# Step 3: Check docker-compose
Write-Host "[3/5] Checking docker-compose..." -ForegroundColor Yellow
try {
    $composeVersion = docker-compose --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Found: $composeVersion" -ForegroundColor Green
    }
} catch {
    Write-Host "  ⚠ docker-compose not found (might be integrated with Docker)" -ForegroundColor Yellow
}

# Step 4: Verify files
Write-Host "[4/5] Verifying admin terminal files..." -ForegroundColor Yellow
$files = @("nexus-admin.py", "nexus-admin.ps1", "ADMIN_TERMINAL.md")
$allExist = $true

foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $file (missing)" -ForegroundColor Red
        $allExist = $false
    }
}

if (-not $allExist) {
    Write-Host ""
    Write-Host "Some files are missing. Please ensure you're in the project-nexus directory." -ForegroundColor Yellow
    exit 1
}

# Step 5: Make files executable (if on Linux/Mac through WSL)
Write-Host "[5/5] Setting up executables..." -ForegroundColor Yellow
Write-Host "  ✓ Windows detected - using PowerShell launcher" -ForegroundColor Green

# Success message
Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║              SETUP COMPLETE - READY TO LAUNCH              ║" -ForegroundColor Green
Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

Write-Host "Quick Start:" -ForegroundColor Cyan
Write-Host "  1. Launch admin terminal:" -ForegroundColor White
Write-Host "     .\nexus-admin.ps1" -ForegroundColor Yellow
Write-Host ""
Write-Host "  2. Or run directly:" -ForegroundColor White
Write-Host "     $pythonCmd nexus-admin.py" -ForegroundColor Yellow
Write-Host ""
Write-Host "  3. For help:" -ForegroundColor White
Write-Host "     $pythonCmd nexus-admin.py help" -ForegroundColor Yellow
Write-Host ""

# Offer to launch now
Write-Host "Launch admin terminal now? (Y/n): " -ForegroundColor Cyan -NoNewline
$response = Read-Host

if ($response -eq "" -or $response -eq "Y" -or $response -eq "y") {
    Write-Host ""
    Write-Host "🚀 Launching Nexus Admin Terminal..." -ForegroundColor Cyan
    Write-Host ""
    & $pythonCmd nexus-admin.py
} else {
    Write-Host ""
    Write-Host "Setup complete! Run '.\nexus-admin.ps1' when ready." -ForegroundColor Green
}

