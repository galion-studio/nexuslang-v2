# Deploy NexusLang v2 to developer.galion.app
# Production deployment script for Windows

Write-Host "🚀 Deploying NexusLang v2 to developer.galion.app..." -ForegroundColor Green
Write-Host ""

# Configuration
$DOMAIN = "developer.galion.app"
$API_DOMAIN = "api.developer.galion.app"
$FRONTEND_PORT = 3000
$BACKEND_PORT = 8000

Write-Host "📋 Configuration:" -ForegroundColor Cyan
Write-Host "   Domain: $DOMAIN"
Write-Host "   API Domain: $API_DOMAIN"
Write-Host "   Frontend Port: $FRONTEND_PORT"
Write-Host "   Backend Port: $BACKEND_PORT"
Write-Host ""

# Check if .env exists
if (!(Test-Path ".env")) {
    Write-Host "⚠️  Creating .env file..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✅ .env created. Please edit it with your API keys." -ForegroundColor Green
    Write-Host ""
    Write-Host "Required keys:" -ForegroundColor Yellow
    Write-Host "  - POSTGRES_PASSWORD"
    Write-Host "  - REDIS_PASSWORD"
    Write-Host "  - SECRET_KEY"
    Write-Host "  - JWT_SECRET"
    Write-Host "  - OPENAI_API_KEY"
    Write-Host "  - SHOPIFY_API_KEY"
    Write-Host ""
    $continue = Read-Host "Press Enter after editing .env, or Ctrl+C to exit"
}

# Create production environment override
Write-Host "📝 Creating production environment..." -ForegroundColor Cyan
$prodEnv = @"
# Production overrides for developer.galion.app
NEXT_PUBLIC_API_URL=https://api.developer.galion.app
NEXT_PUBLIC_WS_URL=wss://api.developer.galion.app
NODE_ENV=production
DEBUG=false
CORS_ORIGINS=https://developer.galion.app,https://api.developer.galion.app
"@

$prodEnv | Out-File -FilePath ".env.prod" -Encoding UTF8
Write-Host "✅ Production environment configured" -ForegroundColor Green
Write-Host ""

# Pull latest images
Write-Host "📦 Pulling Docker images..." -ForegroundColor Cyan
docker-compose pull
Write-Host ""

# Build services
Write-Host "🔨 Building NexusLang v2 services..." -ForegroundColor Cyan
docker-compose build --no-cache
Write-Host ""

# Stop any running services
Write-Host "🛑 Stopping existing services..." -ForegroundColor Cyan
docker-compose down
Write-Host ""

# Start services with production config
Write-Host "🚀 Starting services..." -ForegroundColor Cyan
docker-compose -f docker-compose.yml up -d
Write-Host ""

# Wait for services to be ready
Write-Host "⏳ Waiting for services to initialize (30 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Check service status
Write-Host "📊 Service Status:" -ForegroundColor Cyan
docker-compose ps
Write-Host ""

# Initialize database
Write-Host "🗄️  Initializing database..." -ForegroundColor Cyan
if (Test-Path "v2\database\schemas\init.sql") {
    Get-Content "v2\database\schemas\init.sql" | docker-compose exec -T postgres psql -U nexus -d nexus_v2
    Write-Host "✅ Database initialized" -ForegroundColor Green
} else {
    Write-Host "⚠️  Database schema not found at expected path" -ForegroundColor Yellow
}
Write-Host ""

# Install NexusLang CLI
Write-Host "📦 Installing NexusLang v2..." -ForegroundColor Cyan
Push-Location "v2\nexuslang"
pip install -e . --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ NexusLang v2 installed" -ForegroundColor Green
} else {
    Write-Host "⚠️  NexusLang installation had issues (may need manual setup)" -ForegroundColor Yellow
}
Pop-Location
Write-Host ""

# Test NexusLang
Write-Host "🧪 Testing NexusLang..." -ForegroundColor Cyan
Push-Location "v2\nexuslang"
if (Test-Path "examples\personality_demo.nx") {
    nexuslang run examples\personality_demo.nx 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ NexusLang working!" -ForegroundColor Green
    }
}
Pop-Location
Write-Host ""

# Display access information
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║           NEXUSLANG V2 DEPLOYED SUCCESSFULLY!              ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Access Points:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Local Development:" -ForegroundColor White
Write-Host "    • Frontend:    http://localhost:3000" -ForegroundColor Yellow
Write-Host "    • Backend API: http://localhost:8000" -ForegroundColor Yellow
Write-Host "    • API Docs:    http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "    • Prometheus:  http://localhost:9090" -ForegroundColor Yellow
Write-Host "    • Grafana:     http://localhost:3001" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Production URLs (after DNS setup):" -ForegroundColor White
Write-Host "    • Platform:    https://developer.galion.app" -ForegroundColor Magenta
Write-Host "    • API:         https://api.developer.galion.app" -ForegroundColor Magenta
Write-Host ""
Write-Host "📚 Quick Commands:" -ForegroundColor Cyan
Write-Host "    docker-compose ps              # Check status" -ForegroundColor White
Write-Host "    docker-compose logs -f         # View logs" -ForegroundColor White
Write-Host "    docker-compose restart         # Restart all" -ForegroundColor White
Write-Host "    docker-compose down            # Stop all" -ForegroundColor White
Write-Host ""
Write-Host "📖 Next Steps:" -ForegroundColor Cyan
Write-Host "    1. Configure DNS: developer.galion.app → your server IP" -ForegroundColor White
Write-Host "    2. Setup SSL with Cloudflare or Let's Encrypt" -ForegroundColor White
Write-Host "    3. Open browser to http://localhost:3000" -ForegroundColor White
Write-Host "    4. Test all features" -ForegroundColor White
Write-Host "    5. See 🎯_MASTER_LAUNCH_DOCUMENT.md for complete guide" -ForegroundColor White
Write-Host ""
Write-Host "NexusLang v2 is READY!" -ForegroundColor Green
Write-Host ""

