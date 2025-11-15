# ============================================
# Quick Commands for RunPod Management
# ============================================
# Common operations made simple

param(
    [Parameter(Mandatory=$true, Position=0)]
    [ValidateSet(
        "status",      # Check service status
        "logs",        # View logs
        "restart",     # Restart all services
        "stop",        # Stop all services
        "start",       # Start all services
        "health",      # Health check
        "shell",       # Open interactive shell
        "pull",        # Pull latest code
        "deploy",      # Quick deploy
        "tunnel",      # Start SSH tunnel
        "ip"           # Get RunPod IP
    )]
    [string]$Action,
    
    [Parameter(Mandatory=$false, Position=1)]
    [string]$Service = "all"
)

$ErrorActionPreference = "Continue"

Write-Host "→ $Action" -ForegroundColor Cyan
Write-Host ""

switch ($Action) {
    "status" {
        & ssh runpod "cd /nexuslang-v2 && pm2 status"
    }
    
    "logs" {
        if ($Service -eq "all") {
            & ssh runpod "cd /nexuslang-v2 && pm2 logs --lines 50"
        } else {
            & ssh runpod "cd /nexuslang-v2 && pm2 logs $Service --lines 50"
        }
    }
    
    "restart" {
        & ssh runpod "cd /nexuslang-v2 && pm2 restart $Service && pm2 status"
    }
    
    "stop" {
        & ssh runpod "cd /nexuslang-v2 && pm2 stop $Service && pm2 status"
    }
    
    "start" {
        & ssh runpod "cd /nexuslang-v2 && pm2 start $Service && pm2 status"
    }
    
    "health" {
        Write-Host "Backend Health:" -ForegroundColor Yellow
        & ssh runpod "curl -s http://localhost:8000/health | jq ."
        Write-Host ""
        Write-Host "Nginx Health:" -ForegroundColor Yellow
        & ssh runpod "curl -s http://localhost/health | jq ."
        Write-Host ""
        Write-Host "Ports:" -ForegroundColor Yellow
        & ssh runpod "ss -tlnp | grep -E ':(80|8000|3001|3002|3003) '"
    }
    
    "shell" {
        Write-Host "Opening shell in /nexuslang-v2..." -ForegroundColor Green
        Write-Host "Type 'exit' to return" -ForegroundColor Yellow
        Write-Host ""
        & ssh runpod -t "cd /nexuslang-v2 && exec bash"
    }
    
    "pull" {
        & ssh runpod "cd /nexuslang-v2 && git pull origin clean-nexuslang && git status"
    }
    
    "deploy" {
        Write-Host "Running quick deployment..." -ForegroundColor Green
        & "$PSScriptRoot\deploy.ps1" -SkipBuild
    }
    
    "tunnel" {
        Write-Host "Starting SSH tunnel..." -ForegroundColor Green
        Write-Host "Services will be available at:" -ForegroundColor Yellow
        Write-Host "  Backend:  http://localhost:8000" -ForegroundColor White
        Write-Host "  Studio:   http://localhost:3001" -ForegroundColor White
        Write-Host "  DevPlatform: http://localhost:3002" -ForegroundColor White
        Write-Host "  App:      http://localhost:3003" -ForegroundColor White
        Write-Host ""
        Write-Host "Press Ctrl+C to stop tunnel" -ForegroundColor Yellow
        Write-Host ""
        & ssh runpod-tunnel -N
    }
    
    "ip" {
        Write-Host "RunPod IP Address:" -ForegroundColor Yellow
        & ssh runpod "curl -s ifconfig.me"
        Write-Host ""
    }
}

Write-Host ""

