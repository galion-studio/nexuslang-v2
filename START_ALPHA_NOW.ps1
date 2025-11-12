# Start NexusLang v2 Alpha - Windows PowerShell Version
# Simple script to get everything running quickly

$ErrorActionPreference = "Stop"

Write-Host "🚀 Starting NexusLang v2 Alpha..." -ForegroundColor Blue
Write-Host ""

# Check Docker
if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker not found. Please install Docker Desktop first." -ForegroundColor Red
    exit 1
}

Write-Host "✓ Docker found" -ForegroundColor Green
Write-Host ""

# Create .env if it doesn't exist
if (!(Test-Path .env)) {
    Write-Host "⚙️ Creating default environment file..." -ForegroundColor Yellow
    
    @"
# NexusLang v2 Alpha - Development Configuration

# Database
POSTGRES_USER=nexus
POSTGRES_PASSWORD=nexus_dev_pass_123
POSTGRES_DB=nexus_v2

# Redis
REDIS_PASSWORD=redis_dev_pass_123

# Security (development only - change for production!)
SECRET_KEY=dev_secret_key_for_alpha_testing_only_32chars
JWT_SECRET=dev_jwt_secret_for_alpha_testing_only_needs_64_characters_minimum

# AI Services (optional for alpha)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# Whisper/TTS (CPU for alpha - fast enough for testing)
WHISPER_MODEL=tiny
WHISPER_DEVICE=cpu
TTS_MODEL=tts_models/en/ljspeech/tacotron2-DDC
TTS_DEVICE=cpu

# Application
DEBUG=true
LOG_LEVEL=INFO
ENVIRONMENT=development
"@ | Out-File -FilePath .env -Encoding UTF8
    
    Write-Host "✓ Environment file created" -ForegroundColor Green
    Write-Host "   For AI features, add your OPENAI_API_KEY to .env" -ForegroundColor Yellow
    Write-Host ""
}

# Stop any existing containers
Write-Host "🛑 Stopping existing containers..." -ForegroundColor Blue
docker-compose down 2>$null
Write-Host ""

# Start services
Write-Host "🚀 Starting services..." -ForegroundColor Blue
Write-Host ""

# Start database and cache first
Write-Host "Starting PostgreSQL and Redis..."
docker-compose up -d postgres redis

# Wait for database
Write-Host -NoNewline "Waiting for PostgreSQL..."
for ($i=0; $i -lt 30; $i++) {
    $ready = docker-compose exec -T postgres pg_isready -U nexus 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host " ✓" -ForegroundColor Green
        break
    }
    Start-Sleep -Seconds 1
    Write-Host -NoNewline "."
}
Write-Host ""

# Start Elasticsearch
Write-Host "Starting Elasticsearch..."
docker-compose up -d elasticsearch
Start-Sleep -Seconds 5
Write-Host ""

# Start backend
Write-Host "Starting Backend API..."
docker-compose up -d backend

# Wait for backend
Write-Host -NoNewline "Waiting for Backend..."
for ($i=0; $i -lt 60; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 1 2>$null
        if ($response.StatusCode -eq 200) {
            Write-Host " ✓" -ForegroundColor Green
            break
        }
    } catch {}
    Start-Sleep -Seconds 2
    Write-Host -NoNewline "."
}
Write-Host ""

# Start frontend
Write-Host "Starting Frontend..."
docker-compose up -d frontend

# Wait for frontend
Write-Host -NoNewline "Waiting for Frontend..."
for ($i=0; $i -lt 60; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 1 2>$null
        if ($response.StatusCode -eq 200) {
            Write-Host " ✓" -ForegroundColor Green
            break
        }
    } catch {}
    Start-Sleep -Seconds 2
    Write-Host -NoNewline "."
}
Write-Host ""

# Check health
Write-Host "🏥 Checking service health..." -ForegroundColor Blue
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health"
    if ($health.status -eq "healthy") {
        Write-Host "✓ Backend is healthy!" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️ Backend may still be starting..." -ForegroundColor Yellow
}
Write-Host ""

# Show status
Write-Host "📊 Service Status:" -ForegroundColor Blue
docker-compose ps
Write-Host ""

# Success message
Write-Host "════════════════════════════════════════" -ForegroundColor Green
Write-Host "   ✅ NEXUSLANG V2 ALPHA IS RUNNING!" -ForegroundColor Green
Write-Host "════════════════════════════════════════" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Access URLs:" -ForegroundColor Blue
Write-Host ""
Write-Host "  Frontend:   " -NoNewline
Write-Host "http://localhost:3000" -ForegroundColor Green
Write-Host "  IDE:        " -NoNewline
Write-Host "http://localhost:3000/ide" -ForegroundColor Green
Write-Host "  Grokopedia: " -NoNewline
Write-Host "http://localhost:3000/grokopedia" -ForegroundColor Green
Write-Host "  Community:  " -NoNewline
Write-Host "http://localhost:3000/community" -ForegroundColor Green
Write-Host "  Billing:    " -NoNewline
Write-Host "http://localhost:3000/billing" -ForegroundColor Green
Write-Host ""
Write-Host "  Backend:    " -NoNewline
Write-Host "http://localhost:8000" -ForegroundColor Green
Write-Host "  API Docs:   " -NoNewline
Write-Host "http://localhost:8000/docs" -ForegroundColor Green
Write-Host "  Health:     " -NoNewline
Write-Host "http://localhost:8000/health" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Quick Test:" -ForegroundColor Blue
Write-Host ""
Write-Host "1. Open http://localhost:3000"
Write-Host "2. Click 'Sign Up Free'"
Write-Host "3. Create an account"
Write-Host "4. Go to IDE and write code"
Write-Host "5. Click 'Run' to execute!"
Write-Host ""
Write-Host "📚 Helpful Commands:" -ForegroundColor Blue
Write-Host ""
Write-Host "  View logs:    docker-compose logs -f"
Write-Host "  Stop:         docker-compose stop"
Write-Host "  Restart:      docker-compose restart"
Write-Host "  Clean start:  docker-compose down; .\START_ALPHA_NOW.ps1"
Write-Host ""
Write-Host "🎉 Enjoy your NexusLang v2 Alpha!" -ForegroundColor Green
Write-Host ""

# Open browser
Write-Host "Opening browser..." -ForegroundColor Blue
Start-Process "http://localhost:3000"

