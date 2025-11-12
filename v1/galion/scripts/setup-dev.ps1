# PowerShell setup script for Windows

Write-Host "🚀 Setting up Nexus Core Development Environment" -ForegroundColor Green
Write-Host ""

# Check if Docker is installed
$dockerInstalled = Get-Command docker -ErrorAction SilentlyContinue
if (-not $dockerInstalled) {
    Write-Host "❌ Docker is not installed. Please install Docker Desktop first." -ForegroundColor Red
    Write-Host "   Download from: https://www.docker.com/products/docker-desktop"
    exit 1
}

Write-Host "✅ Docker is installed" -ForegroundColor Green

# Check if Docker is running
try {
    docker info | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

Write-Host ""

# Start infrastructure
Write-Host "📦 Starting PostgreSQL and Redis..." -ForegroundColor Cyan
docker compose up -d postgres redis

# Wait for services to be healthy
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check if postgres is ready
try {
    docker exec nexus-postgres pg_isready -U nexuscore | Out-Null
    Write-Host "✅ PostgreSQL is ready" -ForegroundColor Green
} catch {
    Write-Host "❌ PostgreSQL is not ready. Check logs with: docker logs nexus-postgres" -ForegroundColor Red
    exit 1
}

# Check if redis is ready
try {
    docker exec nexus-redis redis-cli ping | Out-Null
    Write-Host "✅ Redis is ready" -ForegroundColor Green
} catch {
    Write-Host "❌ Redis is not ready. Check logs with: docker logs nexus-redis" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✨ Infrastructure is ready!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Next steps:" -ForegroundColor Cyan
Write-Host "   1. Set up auth service:"
Write-Host "      cd services/auth-service"
Write-Host "      python -m venv venv"
Write-Host "      venv\Scripts\activate"
Write-Host "      pip install -r requirements.txt"
Write-Host "      uvicorn app.main:app --reload"
Write-Host ""
Write-Host "   2. Access the API documentation:"
Write-Host "      http://localhost:8000/docs"
Write-Host ""
Write-Host "   3. Test the database connection:"
Write-Host "      docker exec -it nexus-postgres psql -U nexuscore -d nexuscore"
Write-Host ""

