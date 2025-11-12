# Production Deployment Script for Nexus Core
# Deploys to production with Cloudflare integration

param(
    [Parameter(Mandatory=$true)]
    [string]$ServerIP,
    
    [Parameter(Mandatory=$false)]
    [string]$SSHUser = "root",
    
    [Parameter(Mandatory=$false)]
    [switch]$SetupCloudflare = $true,
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipBuild = $false
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Nexus Core - Production Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Validate parameters
if (-not $ServerIP -or $ServerIP -notmatch '^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$') {
    Write-Host "[ERROR] Invalid server IP address!" -ForegroundColor Red
    exit 1
}

Write-Host "[INFO] Deployment Target: $SSHUser@$ServerIP" -ForegroundColor Yellow
Write-Host ""

# Step 1: Setup Cloudflare DNS
if ($SetupCloudflare) {
    Write-Host "[1/5] Setting up Cloudflare DNS..." -ForegroundColor Cyan
    
    .\scripts\cloudflare-setup.ps1 -SetupDNS -ServerIP $ServerIP
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Cloudflare DNS configured" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Cloudflare DNS setup failed!" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "[1/5] Configuring Cloudflare security..." -ForegroundColor Cyan
    .\scripts\cloudflare-setup.ps1 -SetupSecurity
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Cloudflare security configured" -ForegroundColor Green
    }
} else {
    Write-Host "[1/5] Skipping Cloudflare setup" -ForegroundColor Yellow
}

Write-Host ""

# Step 2: Build Docker images locally (optional)
if (-not $SkipBuild) {
    Write-Host "[2/5] Building Docker images..." -ForegroundColor Cyan
    
    docker-compose build --parallel
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Docker images built successfully" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Docker build failed!" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[2/5] Skipping local build" -ForegroundColor Yellow
}

Write-Host ""

# Step 3: Prepare deployment package
Write-Host "[3/5] Preparing deployment package..." -ForegroundColor Cyan

$deployFiles = @(
    "docker-compose.yml",
    "docker-compose.cloudflare.yml",
    ".env",
    "database/",
    "infrastructure/",
    "services/"
)

# Create deployment directory
$deployDir = "deploy-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
New-Item -ItemType Directory -Path $deployDir -Force | Out-Null

# Copy files
foreach ($file in $deployFiles) {
    if (Test-Path $file) {
        if ((Get-Item $file) -is [System.IO.DirectoryInfo]) {
            Copy-Item -Path $file -Destination $deployDir -Recurse -Force
        } else {
            Copy-Item -Path $file -Destination $deployDir -Force
        }
        Write-Host "  ✓ Copied: $file" -ForegroundColor Gray
    }
}

Write-Host "[OK] Deployment package prepared: $deployDir" -ForegroundColor Green
Write-Host ""

# Step 4: Transfer to server
Write-Host "[4/5] Transferring to server..." -ForegroundColor Cyan
Write-Host "[INFO] You need to manually transfer files to the server" -ForegroundColor Yellow
Write-Host ""
Write-Host "Option 1: Using SCP" -ForegroundColor Cyan
Write-Host "  scp -r $deployDir $SSHUser@${ServerIP}:/opt/nexus-core/" -ForegroundColor Gray
Write-Host ""
Write-Host "Option 2: Using Git" -ForegroundColor Cyan
Write-Host "  ssh $SSHUser@$ServerIP" -ForegroundColor Gray
Write-Host "  git clone https://github.com/yourusername/project-nexus.git /opt/nexus-core" -ForegroundColor Gray
Write-Host "  cd /opt/nexus-core" -ForegroundColor Gray
Write-Host ""

# Step 5: Deployment commands
Write-Host "[5/5] Server Deployment Commands" -ForegroundColor Cyan
Write-Host ""
Write-Host "Run these commands on your server:" -ForegroundColor Yellow
Write-Host ""

$serverCommands = @"
# 1. Install Docker (if not already installed)
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 2. Install Docker Compose
apt-get install docker-compose-plugin -y

# 3. Navigate to application directory
cd /opt/nexus-core

# 4. Generate production secrets
./generate-secrets.ps1

# 5. Update .env with production values
nano .env
# Set ENVIRONMENT=production
# Set DEBUG=false
# Update ALLOWED_ORIGINS with your domains

# 6. Build and start services
docker-compose build --parallel
docker-compose up -d

# 7. Verify deployment
docker-compose ps
docker-compose logs -f

# 8. Test health endpoints
curl http://localhost:8080/health
curl http://localhost:8000/health
curl http://localhost:8001/health

# 9. Test from Cloudflare
curl https://api.galion.app/health
curl https://api.galion.app/api/v1/auth/health
"@

Write-Host $serverCommands -ForegroundColor Gray
Write-Host ""

# Save commands to file
$serverCommands | Out-File -FilePath "$deployDir\DEPLOY_COMMANDS.txt" -Encoding UTF8

Write-Host "[OK] Deployment commands saved to: $deployDir\DEPLOY_COMMANDS.txt" -ForegroundColor Green
Write-Host ""

# DNS propagation check
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Post-Deployment Checklist" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[ ] 1. Transfer files to server" -ForegroundColor Yellow
Write-Host "[ ] 2. Install Docker on server" -ForegroundColor Yellow
Write-Host "[ ] 3. Generate production secrets" -ForegroundColor Yellow
Write-Host "[ ] 4. Update .env with production settings" -ForegroundColor Yellow
Write-Host "[ ] 5. Build and start Docker containers" -ForegroundColor Yellow
Write-Host "[ ] 6. Verify all services are healthy" -ForegroundColor Yellow
Write-Host "[ ] 7. Test local health endpoints" -ForegroundColor Yellow
Write-Host "[ ] 8. Wait for DNS propagation (up to 24 hours)" -ForegroundColor Yellow
Write-Host "[ ] 9. Test public endpoints via Cloudflare" -ForegroundColor Yellow
Write-Host "[ ] 10. Monitor Cloudflare Analytics" -ForegroundColor Yellow
Write-Host "[ ] 11. Set up automated backups" -ForegroundColor Yellow
Write-Host "[ ] 12. Configure monitoring alerts" -ForegroundColor Yellow
Write-Host ""

Write-Host "DNS Records Created:" -ForegroundColor Cyan
Write-Host "  https://galion.app           -> $ServerIP" -ForegroundColor Gray
Write-Host "  https://api.galion.app       -> $ServerIP" -ForegroundColor Gray
Write-Host "  https://app.galion.app       -> $ServerIP" -ForegroundColor Gray
Write-Host "  https://grafana.galion.app   -> $ServerIP" -ForegroundColor Gray
Write-Host ""

Write-Host "Check DNS Propagation:" -ForegroundColor Cyan
Write-Host "  nslookup api.galion.app 1.1.1.1" -ForegroundColor Gray
Write-Host "  https://dnschecker.org/#A/api.galion.app" -ForegroundColor Gray
Write-Host ""

Write-Host "Monitor Deployment:" -ForegroundColor Cyan
Write-Host "  Cloudflare Dashboard: https://dash.cloudflare.com/" -ForegroundColor Gray
Write-Host "  Grafana Dashboard:    https://grafana.galion.app" -ForegroundColor Gray
Write-Host ""

Write-Host "[DONE] Deployment preparation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next: Follow the server deployment commands above" -ForegroundColor Yellow

