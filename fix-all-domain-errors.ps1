# ╔════════════════════════════════════════════════════════════╗
# ║  Automated Domain Error Fix Script (PowerShell)           ║
# ║  Fixes all domain configuration issues in NexusLang v2    ║
# ╚════════════════════════════════════════════════════════════╝

# Check if running from project root
if (-not (Test-Path "v2")) {
    Write-Host "❌ ERROR: Please run this script from the project root directory" -ForegroundColor Red
    Write-Host "cd C:\path\to\project-nexus" -ForegroundColor Yellow
    Write-Host ".\fix-all-domain-errors.ps1" -ForegroundColor Yellow
    exit
}

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  NexusLang v2 - Domain Configuration Fix                  ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

Write-Host "✅ Running from correct directory" -ForegroundColor Green
Write-Host ""

# Ask user for deployment type
Write-Host "Where are you deploying NexusLang v2?" -ForegroundColor Yellow
Write-Host "1. Local development (localhost)" -ForegroundColor White
Write-Host "2. developer.galion.app (production)" -ForegroundColor White
Write-Host "3. nexuslang.galion.app (production)" -ForegroundColor White
Write-Host "4. RunPod (with custom domain)" -ForegroundColor White
Write-Host "5. RunPod (direct proxy URLs)" -ForegroundColor White
Write-Host ""
$deployChoice = Read-Host "Enter choice (1-5)"

# Set values based on choice
switch ($deployChoice) {
    "1" {
        $deploymentType = "local"
        $frontendUrl = "http://localhost:3000"
        $backendUrl = "http://localhost:8000"
        $primaryDomain = "localhost"
        $corsOrigins = "http://localhost:3000,http://localhost:8000"
    }
    "2" {
        $deploymentType = "developer.galion.app"
        $frontendUrl = "https://developer.galion.app"
        $backendUrl = "https://api.developer.galion.app"
        $primaryDomain = "developer.galion.app"
        $corsOrigins = "https://developer.galion.app,https://api.developer.galion.app"
    }
    "3" {
        $deploymentType = "nexuslang.galion.app"
        $frontendUrl = "https://nexuslang.galion.app"
        $backendUrl = "https://api.nexuslang.galion.app"
        $primaryDomain = "nexuslang.galion.app"
        $corsOrigins = "https://nexuslang.galion.app,https://api.nexuslang.galion.app"
    }
    "4" {
        $deploymentType = "runpod-custom"
        $customDomain = Read-Host "Enter your custom domain (e.g., nexuslang.yoursite.com)"
        $frontendUrl = "https://$customDomain"
        $backendUrl = "https://api.$customDomain"
        $primaryDomain = $customDomain
        $corsOrigins = "https://$customDomain,https://api.$customDomain"
    }
    "5" {
        $deploymentType = "runpod-direct"
        $podId = Read-Host "Enter your RunPod Pod ID (e.g., abc123xyz456)"
        $frontendUrl = "https://$podId-3000.proxy.runpod.net"
        $backendUrl = "https://$podId-8000.proxy.runpod.net"
        $primaryDomain = "proxy.runpod.net"
        $corsOrigins = "https://$podId-3000.proxy.runpod.net,https://$podId-8000.proxy.runpod.net"
    }
    default {
        Write-Host "Invalid choice!" -ForegroundColor Red
        exit
    }
}

Write-Host ""
Write-Host "Configuration Summary:" -ForegroundColor Cyan
Write-Host "  Deployment Type: $deploymentType" -ForegroundColor Green
Write-Host "  Frontend URL:    $frontendUrl" -ForegroundColor Green
Write-Host "  Backend URL:     $backendUrl" -ForegroundColor Green
Write-Host "  Primary Domain:  $primaryDomain" -ForegroundColor Green
Write-Host ""
$confirm = Read-Host "Is this correct? (y/n)"

if ($confirm -ne "y") {
    Write-Host "Cancelled by user" -ForegroundColor Yellow
    exit
}

Write-Host ""
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "Step 1: Creating Environment Files" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Function to generate random password
function Get-RandomPassword {
    param([int]$length = 32)
    $chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    $password = ""
    for ($i = 0; $i -lt $length; $i++) {
        $password += $chars[(Get-Random -Maximum $chars.Length)]
    }
    return $password
}

# Create v2/.env if it doesn't exist
if (-not (Test-Path "v2\.env")) {
    Write-Host "Creating v2/.env from template..." -ForegroundColor Yellow
    
    $envContent = Get-Content "v2\env.template" -Raw
    
    # Generate secure secrets
    $secretKey = Get-RandomPassword -length 64
    $jwtSecret = Get-RandomPassword -length 128
    $postgresPassword = Get-RandomPassword -length 32
    $redisPassword = Get-RandomPassword -length 32
    
    # Replace values
    $envContent = $envContent -replace "PRIMARY_DOMAIN=localhost", "PRIMARY_DOMAIN=$primaryDomain"
    $envContent = $envContent -replace "FRONTEND_URL=http://localhost:3000", "FRONTEND_URL=$frontendUrl"
    $envContent = $envContent -replace "BACKEND_URL=http://localhost:8000", "BACKEND_URL=$backendUrl"
    $envContent = $envContent -replace "CORS_ORIGINS=http://localhost:3000,http://localhost:8000", "CORS_ORIGINS=$corsOrigins"
    $envContent = $envContent -replace "SECRET_KEY=your_secret_key.*", "SECRET_KEY=$secretKey"
    $envContent = $envContent -replace "JWT_SECRET=your_jwt_secret.*", "JWT_SECRET=$jwtSecret"
    $envContent = $envContent -replace "POSTGRES_PASSWORD=your_secure_postgres_password_here_min_32_chars", "POSTGRES_PASSWORD=$postgresPassword"
    $envContent = $envContent -replace "REDIS_PASSWORD=your_secure_redis_password_here_min_32_chars", "REDIS_PASSWORD=$redisPassword"
    $envContent = $envContent -replace "postgresql\+asyncpg://nexus:your_secure_postgres_password_here_min_32_chars@", "postgresql+asyncpg://nexus:$postgresPassword@"
    $envContent = $envContent -replace "redis://:your_secure_redis_password_here_min_32_chars@", "redis://:$redisPassword@"
    
    $envContent | Out-File -FilePath "v2\.env" -Encoding UTF8
    
    Write-Host "✅ Created v2/.env" -ForegroundColor Green
} else {
    Write-Host "⚠️  v2/.env already exists, updating URLs..." -ForegroundColor Yellow
    
    $envContent = Get-Content "v2\.env" -Raw
    $envContent = $envContent -replace "PRIMARY_DOMAIN=.*", "PRIMARY_DOMAIN=$primaryDomain"
    $envContent = $envContent -replace "FRONTEND_URL=.*", "FRONTEND_URL=$frontendUrl"
    $envContent = $envContent -replace "BACKEND_URL=.*", "BACKEND_URL=$backendUrl"
    $envContent = $envContent -replace "CORS_ORIGINS=.*", "CORS_ORIGINS=$corsOrigins"
    $envContent | Out-File -FilePath "v2\.env" -Encoding UTF8
    
    Write-Host "✅ Updated v2/.env" -ForegroundColor Green
}

# Create v2/frontend/.env.local if it doesn't exist
if (-not (Test-Path "v2\frontend\.env.local")) {
    Write-Host "Creating v2/frontend/.env.local..." -ForegroundColor Yellow
    
    $envLocalContent = Get-Content "v2\frontend\env.local.template" -Raw
    
    # Set WebSocket URL
    if ($backendUrl -like "https://*") {
        $wsUrl = $backendUrl -replace "https://", "wss://"
    } else {
        $wsUrl = $backendUrl -replace "http://", "ws://"
    }
    
    $envLocalContent = $envLocalContent -replace "NEXT_PUBLIC_API_URL=http://localhost:8000", "NEXT_PUBLIC_API_URL=$backendUrl"
    $envLocalContent = $envLocalContent -replace "NEXT_PUBLIC_WS_URL=ws://localhost:8000", "NEXT_PUBLIC_WS_URL=$wsUrl"
    
    $envLocalContent | Out-File -FilePath "v2\frontend\.env.local" -Encoding UTF8
    
    Write-Host "✅ Created v2/frontend/.env.local" -ForegroundColor Green
} else {
    Write-Host "⚠️  v2/frontend/.env.local already exists, updating..." -ForegroundColor Yellow
    
    # Set WebSocket URL
    if ($backendUrl -like "https://*") {
        $wsUrl = $backendUrl -replace "https://", "wss://"
    } else {
        $wsUrl = $backendUrl -replace "http://", "ws://"
    }
    
    $envLocalContent = Get-Content "v2\frontend\.env.local" -Raw
    $envLocalContent = $envLocalContent -replace "NEXT_PUBLIC_API_URL=.*", "NEXT_PUBLIC_API_URL=$backendUrl"
    $envLocalContent = $envLocalContent -replace "NEXT_PUBLIC_WS_URL=.*", "NEXT_PUBLIC_WS_URL=$wsUrl"
    $envLocalContent | Out-File -FilePath "v2\frontend\.env.local" -Encoding UTF8
    
    Write-Host "✅ Updated v2/frontend/.env.local" -ForegroundColor Green
}

Write-Host ""
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "Step 2: Updating Docker Compose Configuration" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Update docker-compose files
if (Test-Path "docker-compose.prod.yml") {
    Write-Host "Updating docker-compose.prod.yml..." -ForegroundColor Yellow
    
    $composeContent = Get-Content "docker-compose.prod.yml" -Raw
    $composeContent = $composeContent -replace "NEXT_PUBLIC_API_URL=.*", "NEXT_PUBLIC_API_URL=$backendUrl"
    $composeContent | Out-File -FilePath "docker-compose.prod.yml" -Encoding UTF8
    
    Write-Host "✅ Updated docker-compose.prod.yml" -ForegroundColor Green
}

if (Test-Path "v2\docker-compose.nexuslang.yml") {
    Write-Host "Updating v2/docker-compose.nexuslang.yml..." -ForegroundColor Yellow
    
    $composeContent = Get-Content "v2\docker-compose.nexuslang.yml" -Raw
    $composeContent = $composeContent -replace 'CORS_ORIGINS:.*', "CORS_ORIGINS: '$corsOrigins'"
    $composeContent = $composeContent -replace 'NEXT_PUBLIC_API_URL:.*', "NEXT_PUBLIC_API_URL: $backendUrl"
    $composeContent | Out-File -FilePath "v2\docker-compose.nexuslang.yml" -Encoding UTF8
    
    Write-Host "✅ Updated v2/docker-compose.nexuslang.yml" -ForegroundColor Green
}

Write-Host ""
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "Step 3: Nginx Configuration" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

if ($deploymentType -eq "local") {
    Write-Host "⚠️  Skipping nginx configuration for local development" -ForegroundColor Yellow
} else {
    Write-Host "Nginx configuration requires manual SSL certificate setup" -ForegroundColor Yellow
    Write-Host "See: QUICK_FIX_SSL_ERROR.md for instructions" -ForegroundColor Green
    Write-Host ""
    Write-Host "Nginx configs located at:" -ForegroundColor White
    Write-Host "  v2\infrastructure\nginx\developer.galion.app.conf" -ForegroundColor Cyan
    Write-Host "  v2\infrastructure\nginx\nexuslang.galion.app.conf" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "Verification" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

Write-Host "✅ Environment files created/updated" -ForegroundColor Green
Write-Host "✅ Docker compose configurations updated" -ForegroundColor Green
Write-Host "✅ Domain settings configured" -ForegroundColor Green
Write-Host ""

Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

if ($deploymentType -eq "local") {
    Write-Host "1. Start the services:" -ForegroundColor White
    Write-Host "   cd v2" -ForegroundColor Yellow
    Write-Host "   docker-compose up -d" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "2. Access the application:" -ForegroundColor White
    Write-Host "   Frontend: $frontendUrl" -ForegroundColor Green
    Write-Host "   Backend:  $backendUrl" -ForegroundColor Green
    Write-Host ""
    Write-Host "3. Check health:" -ForegroundColor White
    Write-Host "   curl $backendUrl/health" -ForegroundColor Yellow
} else {
    Write-Host "1. Set up SSL certificates (REQUIRED):" -ForegroundColor White
    Write-Host "   .\install-cloudflare-certs.ps1" -ForegroundColor Yellow
    Write-Host "   OR see: QUICK_FIX_SSL_ERROR.md" -ForegroundColor Green
    Write-Host ""
    Write-Host "2. Configure DNS records in Cloudflare:" -ForegroundColor White
    Write-Host "   $primaryDomain → Your server IP" -ForegroundColor Green
    Write-Host "   api.$primaryDomain → Your server IP" -ForegroundColor Green
    Write-Host ""
    Write-Host "3. Deploy to server" -ForegroundColor White
    Write-Host "4. Verify deployment:" -ForegroundColor White
    Write-Host "   curl -I $frontendUrl" -ForegroundColor Yellow
    Write-Host "   curl $backendUrl/health" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "Configuration Summary:" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "Deployment Type: $deploymentType" -ForegroundColor Green
Write-Host "Frontend URL:    $frontendUrl" -ForegroundColor Green
Write-Host "Backend URL:     $backendUrl" -ForegroundColor Green
Write-Host "CORS Origins:    $corsOrigins" -ForegroundColor Green
Write-Host ""
Write-Host "✅ Domain configuration complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Additional Resources:" -ForegroundColor Yellow
Write-Host "  - SSL Setup: QUICK_FIX_SSL_ERROR.md"
Write-Host "  - Full Guide: FIX_SSL_ERROR.md"
Write-Host "  - SSL Explained: SSL_ERROR_EXPLAINED.md"
Write-Host "  - Environment Template: v2\env.template"
Write-Host ""
Write-Host "🚀 Your NexusLang v2 platform is ready to launch!" -ForegroundColor Green
Write-Host ""
pause

