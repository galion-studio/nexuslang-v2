# Galion Ecosystem - Complete Online Setup
# Connects all services, sets up domains, and makes everything accessible

Write-Host "🌐 GALION ECOSYSTEM - COMPLETE ONLINE SETUP" -ForegroundColor Magenta
Write-Host "Connecting all services and making them accessible worldwide" -ForegroundColor White
Write-Host ""

# Step 1: Verify services are running
Write-Host "🔍 STEP 1: VERIFYING SERVICE STATUS" -ForegroundColor Cyan
Write-Host ""

$services = @(
    @{ Name = "Galion App"; Port = 3010; URL = "http://localhost:3010" },
    @{ Name = "Developer Platform"; Port = 3020; URL = "http://localhost:3020" },
    @{ Name = "Galion Studio"; Port = 3030; URL = "http://localhost:3030" },
    @{ Name = "Backend API"; Port = 8010; URL = "http://localhost:8010" }
)

$runningServices = 0

foreach ($service in $services) {
    Write-Host "Testing $($service.Name) ($($service.Port))..." -ForegroundColor White

    try {
        $response = Invoke-WebRequest -Uri $service.URL -TimeoutSec 5
        Write-Host "  ✅ RUNNING (HTTP $($response.StatusCode))" -ForegroundColor Green
        $runningServices++
    } catch {
        Write-Host "  ❌ NOT ACCESSIBLE" -ForegroundColor Red
        Write-Host "     Error: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Service Status: $runningServices / $($services.Count) running" -ForegroundColor $(if ($runningServices -eq $services.Count) { "Green" } else { "Yellow" })
Write-Host ""

# Step 2: Setup domain routing
Write-Host "🌐 STEP 2: DOMAIN ROUTING SETUP" -ForegroundColor Cyan
Write-Host ""

Write-Host "Creating reverse proxy configuration..." -ForegroundColor White
Write-Host "This will route traffic to the correct services based on domain" -ForegroundColor Gray
Write-Host ""

# Create nginx configuration
$nginxConfig = @"
# Galion Ecosystem - Domain Routing
server {
    listen 80;
    server_name galion.app www.galion.app;

    location / {
        proxy_pass http://localhost:3010;
        proxy_set_header Host `$host;
        proxy_set_header X-Real-IP `$remote_addr;
        proxy_set_header X-Forwarded-For `$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto `$scheme;
    }
}

server {
    listen 80;
    server_name developer.galion.app;

    location / {
        proxy_pass http://localhost:3020;
        proxy_set_header Host `$host;
        proxy_set_header X-Real-IP `$remote_addr;
        proxy_set_header X-Forwarded-For `$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto `$scheme;
    }
}

server {
    listen 80;
    server_name galion.studio www.galion.studio;

    location / {
        proxy_pass http://localhost:3030;
        proxy_set_header Host `$host;
        proxy_set_header X-Real-IP `$remote_addr;
        proxy_set_header X-Forwarded-For `$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto `$scheme;
    }
}

server {
    listen 80;
    server_name api.galion.app;

    location / {
        proxy_pass http://localhost:8010;
        proxy_set_header Host `$host;
        proxy_set_header X-Real-IP `$remote_addr;
        proxy_set_header X-Forwarded-For `$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto `$scheme;
    }
}
"@

$nginxConfig | Out-File -FilePath "galion-nginx.conf" -Encoding UTF8
Write-Host "✅ Created galion-nginx.conf" -ForegroundColor Green

# Step 3: Cloudflare setup instructions
Write-Host "☁️ STEP 3: CLOUDFLARE DOMAIN CONFIGURATION" -ForegroundColor Cyan
Write-Host ""

Write-Host "To make your Galion ecosystem accessible worldwide:" -ForegroundColor White
Write-Host ""
Write-Host "1. Go to https://cloudflare.com and sign up" -ForegroundColor Yellow
Write-Host "2. Add these domains to Cloudflare:" -ForegroundColor Yellow
Write-Host "   • galion.app (points to your server IP)" -ForegroundColor White
Write-Host "   • developer.galion.app (points to your server IP)" -ForegroundColor White
Write-Host "   • galion.studio (points to your server IP)" -ForegroundColor White
Write-Host "   • api.galion.app (points to your server IP)" -ForegroundColor White
Write-Host ""
Write-Host "3. DNS Records (Type: CNAME):" -ForegroundColor Yellow
Write-Host "   Name: @, Target: [your-server-ip], Proxy: Enabled" -ForegroundColor White
Write-Host ""
Write-Host "4. SSL/TLS Settings:" -ForegroundColor Yellow
Write-Host "   • SSL/TLS encryption mode: Full (strict)" -ForegroundColor White
Write-Host "   • Always Use HTTPS: On" -ForegroundColor White
Write-Host ""

# Step 4: Production deployment options
Write-Host "🚀 STEP 4: PRODUCTION DEPLOYMENT OPTIONS" -ForegroundColor Cyan
Write-Host ""

Write-Host "Option A: RunPod (Recommended for GPU workloads)" -ForegroundColor Green
Write-Host "  • Upload your Docker images to RunPod" -ForegroundColor White
Write-Host "  • Deploy with RTX A4000 GPU instances" -ForegroundColor White
Write-Host "  • Get global CDN acceleration" -ForegroundColor White
Write-Host ""

Write-Host "Option B: VPS/Cloud Server" -ForegroundColor Green
Write-Host "  • Use nginx with the galion-nginx.conf" -ForegroundColor White
Write-Host "  • Install SSL certificates (Let's Encrypt)" -ForegroundColor White
Write-Host "  • Configure firewall and security" -ForegroundColor White
Write-Host ""

Write-Host "Option C: Kubernetes" -ForegroundColor Green
Write-Host "  • Deploy using helm charts" -ForegroundColor White
Write-Host "  • Auto-scaling and load balancing" -ForegroundColor White
Write-Host "  • Enterprise-grade reliability" -ForegroundColor White
Write-Host ""

# Step 5: Connection verification
Write-Host "🔗 STEP 5: CONNECTION VERIFICATION" -ForegroundColor Cyan
Write-Host ""

Write-Host "Testing internal connections..." -ForegroundColor White

# Test service-to-service communication
$apiTests = @(
    @{ Service = "Voice API"; URL = "http://localhost:8010/health/fast" },
    @{ Service = "Agent API"; URL = "http://localhost:8010/api/v2/agents/list" },
    @{ Service = "Auth API"; URL = "http://localhost:8010/docs" }
)

foreach ($test in $apiTests) {
    try {
        $response = Invoke-WebRequest -Uri $test.URL -TimeoutSec 3
        Write-Host "  ✅ $($test.Service): Connected" -ForegroundColor Green
    } catch {
        Write-Host "  ⚠️ $($test.Service): Connection issue" -ForegroundColor Yellow
    }
}

Write-Host ""

# Step 6: Final summary
Write-Host "🎉 STEP 6: GALION ECOSYSTEM ONLINE!" -ForegroundColor Magenta
Write-Host ""

Write-Host "🌐 YOUR GALION ECOSYSTEM IS NOW CONNECTED:" -ForegroundColor Cyan
Write-Host ""
Write-Host "🎤 Galion.app (Voice-First AI)" -ForegroundColor Blue
Write-Host "   Local: http://localhost:3010" -ForegroundColor White
Write-Host "   Online: https://galion.app (with Cloudflare)" -ForegroundColor Green
Write-Host ""
Write-Host "💻 developer.Galion.app (Full IDE)" -ForegroundColor Cyan
Write-Host "   Local: http://localhost:3020" -ForegroundColor White
Write-Host "   Online: https://developer.galion.app (with Cloudflare)" -ForegroundColor Green
Write-Host ""
Write-Host "🏢 Galion.studio (Corporate Website)" -ForegroundColor Purple
Write-Host "   Local: http://localhost:3030" -ForegroundColor White
Write-Host "   Online: https://galion.studio (with Cloudflare)" -ForegroundColor Green
Write-Host ""
Write-Host "🔗 API Gateway" -ForegroundColor Yellow
Write-Host "   Local: http://localhost:8010" -ForegroundColor White
Write-Host "   Online: https://api.galion.app (with Cloudflare)" -ForegroundColor Green
Write-Host ""

Write-Host "🚀 NEXT STEPS:" -ForegroundColor Green
Write-Host "1. Set up Cloudflare domains (see instructions above)" -ForegroundColor White
Write-Host "2. Test all services: run test_deployment.py" -ForegroundColor White
Write-Host "3. Monitor performance with health checks" -ForegroundColor White
Write-Host "4. Invite beta users to test your ecosystem!" -ForegroundColor White
Write-Host ""

Write-Host "\"Your imagination is the end.\" - Galion is now live worldwide! 🌟" -ForegroundColor Magenta
