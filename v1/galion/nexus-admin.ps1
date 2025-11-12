# PROJECT NEXUS - Admin Terminal Launcher (PowerShell)
# Built with First Principles: Simple, Fast, Effective

param(
    [string]$Command = ""
)

# Banner
Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║      PROJECT NEXUS - ADMIN TERMINAL LAUNCHER      ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
$pythonCmd = $null
foreach ($cmd in @("python", "python3", "py")) {
    try {
        $version = & $cmd --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $pythonCmd = $cmd
            Write-Host "✓ Python found: $version" -ForegroundColor Green
            break
        }
    } catch {
        continue
    }
}

if (-not $pythonCmd) {
    Write-Host "✗ Python not found!" -ForegroundColor Red
    Write-Host "→ Install Python from https://www.python.org" -ForegroundColor Yellow
    exit 1
}

# Check if nexus-admin.py exists
if (-not (Test-Path "nexus-admin.py")) {
    Write-Host "✗ nexus-admin.py not found in current directory" -ForegroundColor Red
    Write-Host "→ Make sure you're in the project-nexus directory" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Admin terminal script found" -ForegroundColor Green

# Launch admin terminal
Write-Host ""
Write-Host "🚀 Launching Nexus Admin Terminal..." -ForegroundColor Cyan
Write-Host ""

if ($Command) {
    # Execute single command
    & $pythonCmd nexus-admin.py $Command
} else {
    # Interactive mode
    & $pythonCmd nexus-admin.py
}

