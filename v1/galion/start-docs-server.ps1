# ===============================================
# Nexus Documentation Server
# Quick start script for serving status page and API docs
# ===============================================

Write-Host ""
Write-Host "╔══════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   🚀 Nexus Documentation Server             ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python detected: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found! Please install Python 3.7+" -ForegroundColor Red
    Write-Host "  Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    pause
    exit 1
}

# Get local IP address
Write-Host ""
Write-Host "🔍 Detecting network configuration..." -ForegroundColor Cyan
$localIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notlike "*Loopback*" -and $_.IPAddress -notlike "169.254.*"} | Select-Object -First 1).IPAddress

if (-not $localIP) {
    $localIP = "localhost"
}

Write-Host "   Local IP: $localIP" -ForegroundColor White

# Choose port
$port = 8888
Write-Host "   Port: $port" -ForegroundColor White

# Check if port is available
$portInUse = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
if ($portInUse) {
    Write-Host ""
    Write-Host "⚠️  Port $port is already in use!" -ForegroundColor Yellow
    Write-Host "   Attempting to use port 9999 instead..." -ForegroundColor Yellow
    $port = 9999
}

Write-Host ""
Write-Host "╔══════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║   📡 Server Starting...                      ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

Write-Host "Access your documentation at:" -ForegroundColor White
Write-Host ""
Write-Host "  📊 Status Page:" -ForegroundColor Cyan
Write-Host "     http://localhost:$port/nexus-status.html" -ForegroundColor White
Write-Host "     http://${localIP}:$port/nexus-status.html" -ForegroundColor Yellow
Write-Host ""
Write-Host "  📚 API Documentation:" -ForegroundColor Cyan
Write-Host "     http://localhost:$port/api-docs/index.html" -ForegroundColor White
Write-Host "     http://${localIP}:$port/api-docs/index.html" -ForegroundColor Yellow
Write-Host ""
Write-Host "  📖 Service Details:" -ForegroundColor Cyan
Write-Host "     http://localhost:$port/docs/" -ForegroundColor White
Write-Host ""
Write-Host "╔══════════════════════════════════════════════╗" -ForegroundColor Magenta
Write-Host "║   Share with others on your network:         ║" -ForegroundColor Magenta
Write-Host "║   http://${localIP}:$port/nexus-status.html" -ForegroundColor White
Write-Host "╚══════════════════════════════════════════════╝" -ForegroundColor Magenta
Write-Host ""
Write-Host "💡 Tip: For public internet access, see:" -ForegroundColor Yellow
Write-Host "   PUBLIC_ACCESS_GUIDE.md" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""
Write-Host "═══════════════════════════════════════════════" -ForegroundColor DarkGray

# Start Python HTTP server
try {
    # Try to open status page in browser after 2 seconds
    Start-Sleep -Seconds 2
    Start-Process "http://localhost:$port/nexus-status.html"
    
    # Start server
    python -m http.server $port
} catch {
    Write-Host ""
    Write-Host "✗ Server failed to start!" -ForegroundColor Red
    Write-Host "  Error: $_" -ForegroundColor Red
    pause
    exit 1
}

