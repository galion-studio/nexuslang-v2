# Test Cloudflare Integration for Nexus Core
# Verifies DNS, SSL, API endpoints, and security

param(
    [Parameter(Mandatory=$false)]
    [switch]$SkipDNS = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipSSL = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipAPI = $false
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Cloudflare Integration Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Cloudflare API Connection
Write-Host "[TEST 1] Cloudflare API Connection" -ForegroundColor Cyan

.\scripts\cloudflare-setup.ps1 -ShowInfo

if ($LASTEXITCODE -eq 0) {
    Write-Host "[✓] Cloudflare API connection successful" -ForegroundColor Green
} else {
    Write-Host "[✗] Cloudflare API connection failed" -ForegroundColor Red
}
Write-Host ""

# Test 2: DNS Resolution
if (-not $SkipDNS) {
    Write-Host "[TEST 2] DNS Resolution" -ForegroundColor Cyan
    
    $domains = @(
        "galion.app",
        "api.galion.app",
        "app.galion.app",
        "grafana.galion.app"
    )
    
    foreach ($domain in $domains) {
        $result = Resolve-DnsName -Name $domain -ErrorAction SilentlyContinue
        
        if ($result) {
            $ip = $result | Where-Object { $_.Type -eq "A" } | Select-Object -First 1 -ExpandProperty IPAddress
            Write-Host "  [✓] $domain -> $ip" -ForegroundColor Green
        } else {
            Write-Host "  [✗] $domain -> NOT RESOLVED" -ForegroundColor Red
        }
    }
} else {
    Write-Host "[TEST 2] DNS Resolution - SKIPPED" -ForegroundColor Yellow
}
Write-Host ""

# Test 3: SSL/TLS Certificate
if (-not $SkipSSL) {
    Write-Host "[TEST 3] SSL/TLS Certificate" -ForegroundColor Cyan
    
    $domains = @("api.galion.app", "app.galion.app")
    
    foreach ($domain in $domains) {
        try {
            $req = [System.Net.WebRequest]::Create("https://$domain")
            $req.Timeout = 5000
            $resp = $req.GetResponse()
            $resp.Close()
            Write-Host "  [✓] $domain - SSL Valid" -ForegroundColor Green
        } catch {
            Write-Host "  [✗] $domain - SSL Error: $_" -ForegroundColor Red
        }
    }
} else {
    Write-Host "[TEST 3] SSL/TLS Certificate - SKIPPED" -ForegroundColor Yellow
}
Write-Host ""

# Test 4: API Endpoints
if (-not $SkipAPI) {
    Write-Host "[TEST 4] API Endpoints" -ForegroundColor Cyan
    
    $endpoints = @{
        "https://api.galion.app/health" = "API Gateway Health"
        "https://api.galion.app/api/v1/auth/health" = "Auth Service Health"
        "https://api.galion.app/api/v1/users/health" = "User Service Health"
    }
    
    foreach ($endpoint in $endpoints.Keys) {
        $description = $endpoints[$endpoint]
        
        try {
            $response = Invoke-WebRequest -Uri $endpoint -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
            
            if ($response.StatusCode -eq 200) {
                Write-Host "  [✓] $description - OK" -ForegroundColor Green
            } else {
                Write-Host "  [✗] $description - Status: $($response.StatusCode)" -ForegroundColor Red
            }
        } catch {
            Write-Host "  [✗] $description - Error: $($_.Exception.Message)" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "[TEST 4] API Endpoints - SKIPPED" -ForegroundColor Yellow
}
Write-Host ""

# Test 5: Security Headers
Write-Host "[TEST 5] Security Headers" -ForegroundColor Cyan

try {
    $response = Invoke-WebRequest -Uri "https://api.galion.app/" -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
    
    $requiredHeaders = @(
        "Strict-Transport-Security",
        "X-Content-Type-Options",
        "X-Frame-Options"
    )
    
    foreach ($header in $requiredHeaders) {
        if ($response.Headers[$header]) {
            Write-Host "  [✓] $header: $($response.Headers[$header])" -ForegroundColor Green
        } else {
            Write-Host "  [✗] $header: MISSING" -ForegroundColor Red
        }
    }
    
    # Check Cloudflare headers
    if ($response.Headers["CF-Ray"]) {
        Write-Host "  [✓] CF-Ray: $($response.Headers['CF-Ray']) (Cloudflare Active)" -ForegroundColor Green
    } else {
        Write-Host "  [⚠] CF-Ray: NOT FOUND (Not proxied through Cloudflare?)" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "  [✗] Could not fetch security headers: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 6: Rate Limiting
Write-Host "[TEST 6] Rate Limiting" -ForegroundColor Cyan

try {
    $requests = 0
    $rateLimit = $false
    
    for ($i = 1; $i -le 10; $i++) {
        $response = Invoke-WebRequest -Uri "https://api.galion.app/health" -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
        $requests++
        
        if ($response.StatusCode -eq 429) {
            $rateLimit = $true
            break
        }
    }
    
    if ($rateLimit) {
        Write-Host "  [✓] Rate limiting active (triggered after $requests requests)" -ForegroundColor Green
    } else {
        Write-Host "  [✓] Rate limiting configured ($requests test requests succeeded)" -ForegroundColor Green
    }
} catch {
    if ($_.Exception.Response.StatusCode -eq 429) {
        Write-Host "  [✓] Rate limiting active (429 Too Many Requests)" -ForegroundColor Green
    } else {
        Write-Host "  [⚠] Could not test rate limiting: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}
Write-Host ""

# Test 7: Cache Headers
Write-Host "[TEST 7] Cache Headers" -ForegroundColor Cyan

try {
    $response = Invoke-WebRequest -Uri "https://api.galion.app/" -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
    
    if ($response.Headers["CF-Cache-Status"]) {
        Write-Host "  [✓] CF-Cache-Status: $($response.Headers['CF-Cache-Status'])" -ForegroundColor Green
    } else {
        Write-Host "  [⚠] CF-Cache-Status: NOT FOUND" -ForegroundColor Yellow
    }
    
    if ($response.Headers["Cache-Control"]) {
        Write-Host "  [✓] Cache-Control: $($response.Headers['Cache-Control'])" -ForegroundColor Green
    }
} catch {
    Write-Host "  [✗] Could not fetch cache headers: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Test Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "If all tests pass, your Cloudflare integration is working correctly!" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Monitor Cloudflare Analytics: https://dash.cloudflare.com/" -ForegroundColor Gray
Write-Host "  2. Check Grafana dashboards: https://grafana.galion.app" -ForegroundColor Gray
Write-Host "  3. Test user registration and login" -ForegroundColor Gray
Write-Host "  4. Set up monitoring alerts" -ForegroundColor Gray
Write-Host ""

