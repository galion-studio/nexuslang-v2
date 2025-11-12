# Diagnose Cloudflare Error 1016 for galion.app
# This script checks DNS configuration and identifies the problem

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Error 1016 Diagnostic Tool" -ForegroundColor Cyan
Write-Host "   Domain: galion.app" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$domain = "galion.app"
$subdomains = @("api", "app", "www", "grafana")
$issues = @()
$recommendations = @()

# Test 1: Check if .env exists
Write-Host "[TEST 1] Checking .env file..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "  OK .env file exists" -ForegroundColor Green
    
    # Load environment variables
    Get-Content .env | ForEach-Object {
        if ($_ -match '^([^=]+)=(.*)$') {
            $name = $matches[1]
            $value = $matches[2]
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
        }
    }
} else {
    Write-Host "  ERROR .env file NOT found!" -ForegroundColor Red
    $issues += ".env file missing"
    $recommendations += "Run: .\generate-secrets.ps1"
}
Write-Host ""

# Test 2: Check Cloudflare credentials
Write-Host "[TEST 2] Checking Cloudflare credentials..." -ForegroundColor Yellow
$zoneId = $env:CLOUDFLARE_ZONE_ID
$apiToken = $env:CLOUDFLARE_API_TOKEN

if ($zoneId -and $apiToken) {
    Write-Host "  OK Cloudflare credentials found" -ForegroundColor Green
    Write-Host "     Zone ID: $zoneId" -ForegroundColor Gray
} else {
    Write-Host "  ERROR Cloudflare credentials NOT found!" -ForegroundColor Red
    $issues += "Missing Cloudflare API credentials"
    $recommendations += "Add CLOUDFLARE_ZONE_ID and CLOUDFLARE_API_TOKEN to .env"
}
Write-Host ""

# Test 3: Check Python installation
Write-Host "[TEST 3] Checking Python installation..." -ForegroundColor Yellow
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if ($pythonCmd) {
    $pythonVersion = & python --version 2>&1
    Write-Host "  OK Python installed: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "  ERROR Python NOT installed!" -ForegroundColor Red
    $issues += "Python not installed"
    $recommendations += "Install Python: winget install Python.Python.3.11"
}
Write-Host ""

# Test 4: Check Cloudflare SDK
Write-Host "[TEST 4] Checking Cloudflare SDK..." -ForegroundColor Yellow
if ($pythonCmd) {
    $pipList = & python -m pip list 2>$null
    if ($pipList -match "cloudflare") {
        Write-Host "  OK Cloudflare SDK installed" -ForegroundColor Green
    } else {
        Write-Host "  ERROR Cloudflare SDK NOT installed!" -ForegroundColor Red
        $issues += "Cloudflare SDK missing"
        $recommendations += "Install: pip install cloudflare python-dotenv requests"
    }
}
Write-Host ""

# Test 5: DNS Resolution Check
Write-Host "[TEST 5] Checking DNS resolution..." -ForegroundColor Yellow
$dnsWorking = $false

# Check main domain
try {
    $result = Resolve-DnsName -Name $domain -Server 1.1.1.1 -ErrorAction Stop
    if ($result) {
        Write-Host "  OK $domain resolves to: $($result[0].IPAddress)" -ForegroundColor Green
        $dnsWorking = $true
    }
} catch {
    Write-Host "  ERROR $domain does NOT resolve!" -ForegroundColor Red
    $issues += "DNS records not configured for $domain"
}

# Check subdomains
foreach ($sub in $subdomains) {
    $fullDomain = "$sub.$domain"
    try {
        $result = Resolve-DnsName -Name $fullDomain -Server 1.1.1.1 -ErrorAction Stop
        if ($result) {
            Write-Host "  OK $fullDomain resolves" -ForegroundColor Green
            $dnsWorking = $true
        }
    } catch {
        Write-Host "  WARNING $fullDomain does NOT resolve" -ForegroundColor Yellow
    }
}

if (-not $dnsWorking) {
    $recommendations += "Setup DNS: .\scripts\cloudflare-setup.ps1 -SetupDNS -ServerIP YOUR_IP"
    $recommendations += "OR use Cloudflare Tunnel: cloudflared tunnel create nexus-core"
}
Write-Host ""

# Test 6: Check Docker
Write-Host "[TEST 6] Checking Docker..." -ForegroundColor Yellow
$dockerCmd = Get-Command docker -ErrorAction SilentlyContinue
if ($dockerCmd) {
    try {
        $dockerVersion = & docker --version 2>&1
        Write-Host "  OK Docker installed: $dockerVersion" -ForegroundColor Green
        
        $dockerRunning = & docker ps 2>&1
        if ($dockerRunning -notmatch "error") {
            Write-Host "  OK Docker is running" -ForegroundColor Green
        } else {
            Write-Host "  WARNING Docker installed but not running" -ForegroundColor Yellow
            $recommendations += "Start Docker Desktop"
        }
    } catch {
        Write-Host "  WARNING Docker installed but not accessible" -ForegroundColor Yellow
    }
} else {
    Write-Host "  WARNING Docker NOT installed (optional)" -ForegroundColor Yellow
}
Write-Host ""

# Test 7: Check cloudflared
Write-Host "[TEST 7] Checking Cloudflare Tunnel (cloudflared)..." -ForegroundColor Yellow
$cloudflaredCmd = Get-Command cloudflared -ErrorAction SilentlyContinue
if ($cloudflaredCmd) {
    $cloudflaredVersion = & cloudflared --version 2>&1
    Write-Host "  OK cloudflared installed: $cloudflaredVersion" -ForegroundColor Green
} else {
    Write-Host "  INFO cloudflared NOT installed (optional)" -ForegroundColor Cyan
    Write-Host "  INFO Install for tunnel: winget install --id Cloudflare.cloudflared" -ForegroundColor Cyan
}
Write-Host ""

# ============================================
# SUMMARY AND RECOMMENDATIONS
# ============================================
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   DIAGNOSTIC SUMMARY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($issues.Count -eq 0) {
    Write-Host "OK No critical issues found!" -ForegroundColor Green
    Write-Host ""
    Write-Host "If you are still seeing Error 1016:" -ForegroundColor Yellow
    Write-Host "  1. DNS records exist but point to wrong IP" -ForegroundColor Yellow
    Write-Host "  2. Origin server is not responding" -ForegroundColor Yellow
    Write-Host "  3. DNS has not propagated yet (wait 5-10 min)" -ForegroundColor Yellow
} else {
    Write-Host "ERROR Found $($issues.Count) issue(s):" -ForegroundColor Red
    Write-Host ""
    foreach ($issue in $issues) {
        Write-Host "  - $issue" -ForegroundColor Red
    }
}

if ($recommendations.Count -gt 0) {
    Write-Host ""
    Write-Host "Recommendations:" -ForegroundColor Cyan
    Write-Host ""
    $recNum = 1
    foreach ($rec in $recommendations) {
        Write-Host "  $recNum. $rec" -ForegroundColor Yellow
        $recNum++
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   QUICK FIX GUIDE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Choose your deployment method:" -ForegroundColor Cyan
Write-Host ""
Write-Host "Option A: Traditional Server" -ForegroundColor Yellow
Write-Host "  1. Get your server IP address" -ForegroundColor White
Write-Host "  2. .\scripts\cloudflare-setup.ps1 -SetupDNS -ServerIP YOUR_IP" -ForegroundColor White
Write-Host "  3. Deploy: docker-compose up -d" -ForegroundColor White
Write-Host "  4. Test: curl https://api.galion.app/health" -ForegroundColor White
Write-Host ""
Write-Host "Option B: Cloudflare Tunnel" -ForegroundColor Yellow
Write-Host "  1. winget install --id Cloudflare.cloudflared" -ForegroundColor White
Write-Host "  2. cloudflared tunnel login" -ForegroundColor White
Write-Host "  3. cloudflared tunnel create nexus-core" -ForegroundColor White
Write-Host "  4. cloudflared tunnel route dns nexus-core galion.app" -ForegroundColor White
Write-Host "  5. docker-compose -f docker-compose.yml -f docker-compose.cloudflare.yml up -d" -ForegroundColor White
Write-Host ""
Write-Host "Full guide: FIX_ERROR_1016_NOW.md" -ForegroundColor Cyan
Write-Host ""

# Test live site
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   TESTING LIVE SITE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$testUrls = @(
    "https://galion.app",
    "https://api.galion.app",
    "https://app.galion.app"
)

foreach ($url in $testUrls) {
    Write-Host "Testing $url..." -ForegroundColor Yellow
    try {
        $response = Invoke-WebRequest -Uri $url -Method Get -TimeoutSec 10 -ErrorAction Stop
        Write-Host "  OK Status: $($response.StatusCode) - Site is UP!" -ForegroundColor Green
    } catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        if ($statusCode -eq 1016 -or $_.Exception.Message -match "1016") {
            Write-Host "  ERROR 1016 - DNS not configured" -ForegroundColor Red
        } elseif ($statusCode) {
            Write-Host "  WARNING Status: $statusCode" -ForegroundColor Yellow
        } else {
            Write-Host "  ERROR Cannot connect" -ForegroundColor Red
        }
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   DONE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Need help? Check:" -ForegroundColor Cyan
Write-Host "  - FIX_ERROR_1016_NOW.md" -ForegroundColor White
Write-Host "  - ERROR_1016_QUICK_REFERENCE.md" -ForegroundColor White
Write-Host "  - https://dash.cloudflare.com/" -ForegroundColor White
Write-Host ""
