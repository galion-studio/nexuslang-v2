# PowerShell Deployment Script for RunPod
# Deploy NexusLang v2 + Content Management System

param(
    [Parameter(Mandatory=$false)]
    [string]$RunPodHost = $env:RUNPOD_HOST,
    
    [Parameter(Mandatory=$false)]
    [string]$RunPodPort = $env:RUNPOD_PORT,
    
    [Parameter(Mandatory=$false)]
    [string]$SSHUser = "root"
)

Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  NexusLang v2 + Content Manager Deployment            ║" -ForegroundColor Cyan
Write-Host "║  Deploying to RunPod                                   ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check environment variables
if (-not $RunPodHost -or -not $RunPodPort) {
    Write-Host "❌ Error: RUNPOD_HOST and RUNPOD_PORT must be set" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please set environment variables:" -ForegroundColor Yellow
    Write-Host '  $env:RUNPOD_HOST = "your-runpod-ip"'
    Write-Host '  $env:RUNPOD_PORT = "your-ssh-port"'
    exit 1
}

$ProjectPath = "/root/project-nexus"

Write-Host "📋 Deployment Configuration:" -ForegroundColor Green
Write-Host "   Host: $RunPodHost"
Write-Host "   Port: $RunPodPort"
Write-Host "   User: $SSHUser"
Write-Host ""

# Function to run remote commands
function Invoke-RemoteCommand {
    param([string]$Command)
    ssh -p $RunPodPort "$SSHUser@$RunPodHost" $Command
}

Write-Host "🔍 Step 1: Testing SSH connection..." -ForegroundColor Yellow
try {
    $result = Invoke-RemoteCommand "echo 'Connection successful'"
    Write-Host "✅ SSH connection established" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to connect via SSH" -ForegroundColor Red
    Write-Host "Please check your RUNPOD_HOST, RUNPOD_PORT, and SSH keys" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "📦 Step 2: Checking if repository exists..." -ForegroundColor Yellow
$repoExists = Invoke-RemoteCommand "[ -d $ProjectPath ] && echo 'exists'"
if ($repoExists -eq "exists") {
    Write-Host "📂 Repository exists, updating..." -ForegroundColor Green
    Invoke-RemoteCommand "cd $ProjectPath && git pull origin main"
} else {
    Write-Host "📥 Cloning repository..." -ForegroundColor Yellow
    Write-Host "⚠️  Note: Update GITHUB_REPO variable if using private repo" -ForegroundColor Gray
    $repoUrl = $env:GITHUB_REPO
    if (-not $repoUrl) {
        $repoUrl = "https://github.com/yourusername/project-nexus.git"
    }
    Invoke-RemoteCommand "git clone $repoUrl $ProjectPath"
}

Write-Host ""
Write-Host "🔧 Step 3: Installing dependencies..." -ForegroundColor Yellow
Invoke-RemoteCommand @"
cd $ProjectPath/v2 && \
apt-get update -qq && \
apt-get install -y -qq docker.io docker-compose postgresql-client redis-tools curl wget git && \
systemctl start docker && \
systemctl enable docker && \
echo '✅ Dependencies installed'
"@

Write-Host ""
Write-Host "⚙️  Step 4: Setting up environment..." -ForegroundColor Yellow
Invoke-RemoteCommand @"
cd $ProjectPath/v2
if [ ! -f .env ]; then
    cat > .env << 'EOF'
DATABASE_URL=postgresql://nexuslang:`$(openssl rand -hex 16)@postgres:5432/nexuslang_v2
REDIS_URL=redis://redis:6379/0
SECRET_KEY=`$(openssl rand -hex 32)
JWT_SECRET=`$(openssl rand -hex 32)
ENCRYPTION_KEY=`$(openssl rand -hex 32)
CORS_ORIGINS=["http://localhost:3100","https://developer.galion.app"]
BACKEND_PORT=8100
FRONTEND_PORT=3100
STORAGE_TYPE=local
MEDIA_STORAGE_PATH=/app/media_storage
MEDIA_BASE_URL=http://localhost:8100/media
ENVIRONMENT=production
DEBUG=false
EOF
    echo '✅ Environment configured'
else
    echo '✅ Environment file exists'
fi
"@

Write-Host ""
Write-Host "🐳 Step 5: Building and starting Docker services..." -ForegroundColor Yellow
Invoke-RemoteCommand "cd $ProjectPath/v2 && docker-compose -f docker-compose.nexuslang.yml down"
Invoke-RemoteCommand "cd $ProjectPath/v2 && docker-compose -f docker-compose.nexuslang.yml pull"
Invoke-RemoteCommand "cd $ProjectPath/v2 && docker-compose -f docker-compose.nexuslang.yml build"
Invoke-RemoteCommand "cd $ProjectPath/v2 && docker-compose -f docker-compose.nexuslang.yml up -d"

Write-Host ""
Write-Host "⏳ Waiting for services to start (30 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

Write-Host ""
Write-Host "🗄️  Step 6: Running database migrations..." -ForegroundColor Yellow
Write-Host "   - Creating database schema..."
Invoke-RemoteCommand @"
cd $ProjectPath/v2 && docker-compose -f docker-compose.nexuslang.yml exec -T backend python -c '
from core.database import init_db
import asyncio
asyncio.run(init_db())
print(\"Database initialized\")
'
"@

Write-Host "   - Running content manager migration..."
Invoke-RemoteCommand "cd $ProjectPath/v2 && docker-compose -f docker-compose.nexuslang.yml exec -T postgres psql -U nexuslang nexuslang_v2 < database/migrations/003_content_manager.sql"

Write-Host ""
Write-Host "🔍 Step 7: Checking service health..." -ForegroundColor Yellow
$services = Invoke-RemoteCommand "cd $ProjectPath/v2 && docker-compose -f docker-compose.nexuslang.yml ps"
Write-Host $services
if ($services -match "Up") {
    Write-Host "✅ Services are running" -ForegroundColor Green
} else {
    Write-Host "⚠️  Some services may not be running" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🧪 Step 8: Testing API..." -ForegroundColor Yellow
Start-Sleep -Seconds 5
$healthCheck = Invoke-RemoteCommand "curl -s http://localhost:8100/health"
if ($healthCheck -match "healthy") {
    Write-Host "✅ Backend API is responding" -ForegroundColor Green
} else {
    Write-Host "⚠️  Backend API may not be ready yet" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  🎉 DEPLOYMENT COMPLETE!                               ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "🌐 Your services are running at:" -ForegroundColor Green
Write-Host "   Backend:  http://$RunPodHost`:8100"
Write-Host "   Frontend: http://$RunPodHost`:3100"
Write-Host "   API Docs: http://$RunPodHost`:8100/docs"
Write-Host ""
Write-Host "🔐 Admin Access:" -ForegroundColor Green
Write-Host "   ssh -p $RunPodPort $SSHUser@$RunPodHost"
Write-Host ""
Write-Host "📝 Next Steps:" -ForegroundColor Yellow
Write-Host "   1. Setup Cloudflare Tunnel for HTTPS"
Write-Host "   2. Connect social media accounts"
Write-Host "   3. Create your first post"
Write-Host ""
Write-Host "🛠️  Useful Commands:" -ForegroundColor Cyan
Write-Host "   View logs:  .\admin-control.ps1 -Action logs"
Write-Host "   Restart:    .\admin-control.ps1 -Action restart"
Write-Host "   Status:     .\admin-control.ps1 -Action status"
Write-Host ""

