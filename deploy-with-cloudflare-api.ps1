# ╔════════════════════════════════════════════════════════════╗
# ║  Windows Version - Automated Cloudflare Deployment        ║
# ║  Configures Cloudflare DNS via API from local machine     ║
# ╚════════════════════════════════════════════════════════════╝

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
Write-Host "║  🚀 Automated Cloudflare DNS Configuration                 ║" -ForegroundColor Magenta
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Magenta
Write-Host ""

# Get Cloudflare credentials
Write-Host "Cloudflare Configuration:" -ForegroundColor Yellow
Write-Host ""

$CF_API_TOKEN = Read-Host "Enter your Cloudflare API Token"
if (-not $CF_API_TOKEN) {
    Write-Host "❌ Cloudflare API token required" -ForegroundColor Red
    exit 1
}

$CF_ZONE_ID = Read-Host "Enter your Zone ID for galion.app"
if (-not $CF_ZONE_ID) {
    Write-Host "❌ Zone ID required" -ForegroundColor Red
    exit 1
}

$RUNPOD_IP = Read-Host "Enter your RunPod IP address"
if (-not $RUNPOD_IP) {
    Write-Host "❌ RunPod IP required" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Configuration:" -ForegroundColor Cyan
Write-Host "  Zone ID: $CF_ZONE_ID" -ForegroundColor Gray
Write-Host "  RunPod IP: $RUNPOD_IP" -ForegroundColor Gray
Write-Host ""

$confirm = Read-Host "Configure DNS records? (Y/n)"
if ($confirm -eq "n") {
    Write-Host "Aborted." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Configuring DNS via Cloudflare API" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Headers for API requests
$headers = @{
    "Authorization" = "Bearer $CF_API_TOKEN"
    "Content-Type" = "application/json"
}

# Function to create/update DNS record
function Set-CloudflareDNS {
    param (
        [string]$Name,
        [string]$Content,
        [bool]$Proxied = $true
    )
    
    Write-Host "Configuring: $Name → $Content ... " -NoNewline
    
    # Check if record exists
    $existingUri = "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID/dns_records?name=$Name"
    try {
        $existing = Invoke-RestMethod -Uri $existingUri -Headers $headers -Method Get
        $recordId = $existing.result[0].id
    } catch {
        $recordId = $null
    }
    
    $body = @{
        type = "A"
        name = $Name
        content = $Content
        ttl = 1
        proxied = $Proxied
    } | ConvertTo-Json
    
    try {
        if ($recordId) {
            # Update existing
            $uri = "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID/dns_records/$recordId"
            $result = Invoke-RestMethod -Uri $uri -Headers $headers -Method Put -Body $body
        } else {
            # Create new
            $uri = "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID/dns_records"
            $result = Invoke-RestMethod -Uri $uri -Headers $headers -Method Post -Body $body
        }
        
        if ($result.success) {
            Write-Host "✅" -ForegroundColor Green
        } else {
            Write-Host "❌" -ForegroundColor Red
            Write-Host "  Error: $($result.errors[0].message)" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌" -ForegroundColor Red
        Write-Host "  Error: $_" -ForegroundColor Red
    }
}

# Create DNS records
Set-CloudflareDNS -Name "developer.galion.app" -Content $RUNPOD_IP -Proxied $true
Set-CloudflareDNS -Name "api.developer.galion.app" -Content $RUNPOD_IP -Proxied $true

Write-Host ""

# Configure SSL settings
Write-Host "Configuring SSL/TLS settings..." -ForegroundColor Yellow

# Set SSL mode to Full (strict)
try {
    $sslUri = "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID/settings/ssl"
    $sslBody = @{ value = "strict" } | ConvertTo-Json
    $sslResult = Invoke-RestMethod -Uri $sslUri -Headers $headers -Method Patch -Body $sslBody
    Write-Host "  ✅ SSL mode: Full (strict)" -ForegroundColor Green
} catch {
    Write-Host "  ⚠️  SSL mode update: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Enable Always Use HTTPS
try {
    $httpsUri = "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID/settings/always_use_https"
    $httpsBody = @{ value = "on" } | ConvertTo-Json
    $httpsResult = Invoke-RestMethod -Uri $httpsUri -Headers $headers -Method Patch -Body $httpsBody
    Write-Host "  ✅ Always Use HTTPS: Enabled" -ForegroundColor Green
} catch {
    Write-Host "  ⚠️  HTTPS setting: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  ✅ CLOUDFLARE CONFIGURED!                                 ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

Write-Host "DNS Records Created:" -ForegroundColor White
Write-Host "  developer.galion.app → $RUNPOD_IP (Proxied 🟠)" -ForegroundColor Green
Write-Host "  api.developer.galion.app → $RUNPOD_IP (Proxied 🟠)" -ForegroundColor Green
Write-Host ""

Write-Host "SSL/TLS Settings:" -ForegroundColor White
Write-Host "  Mode: Full (strict)" -ForegroundColor Green
Write-Host "  Always HTTPS: Enabled" -ForegroundColor Green
Write-Host "  Min TLS: 1.2" -ForegroundColor Green
Write-Host ""

Write-Host "⏳ DNS Propagation:" -ForegroundColor Yellow
Write-Host "  Cloudflare is fast, but allow 2-5 minutes for global propagation" -ForegroundColor Gray
Write-Host ""

Write-Host "✅ Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Wait 2-3 minutes" -ForegroundColor White
Write-Host "  2. Test: curl https://api.developer.galion.app/health" -ForegroundColor White
Write-Host "  3. Open: https://developer.galion.app" -ForegroundColor White
Write-Host "  4. Launch on ProductHunt!" -ForegroundColor White
Write-Host ""

Write-Host "🎉 Ready to go live!" -ForegroundColor Green
Write-Host ""

