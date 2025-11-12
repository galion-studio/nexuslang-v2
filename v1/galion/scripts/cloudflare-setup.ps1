# Cloudflare Setup Script for Nexus Core
# This script configures Cloudflare for production deployment

param(
    [Parameter(Mandatory=$false)]
    [string]$ServerIP = "",
    
    [Parameter(Mandatory=$false)]
    [switch]$SetupDNS = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$SetupSecurity = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$PurgeCache = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$ShowInfo = $false
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Cloudflare Setup - Nexus Core" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Load environment variables
if (Test-Path ".env") {
    Write-Host "[INFO] Loading environment variables from .env..." -ForegroundColor Yellow
    Get-Content .env | ForEach-Object {
        if ($_ -match '^([^=]+)=(.*)$') {
            $name = $matches[1]
            $value = $matches[2]
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
        }
    }
} else {
    Write-Host "[ERROR] .env file not found! Run generate-secrets.ps1 first." -ForegroundColor Red
    exit 1
}

# Check if Python is installed
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "[ERROR] Python not found! Please install Python 3.11+." -ForegroundColor Red
    exit 1
}

# Check if cloudflare package is installed
Write-Host "[INFO] Checking Cloudflare SDK..." -ForegroundColor Yellow
$pipList = & python -m pip list 2>$null
if ($pipList -notmatch "cloudflare") {
    Write-Host "[INFO] Installing Cloudflare SDK..." -ForegroundColor Yellow
    & python -m pip install cloudflare python-dotenv --quiet
}

# Verify Cloudflare credentials
$zoneId = $env:CLOUDFLARE_ZONE_ID
$apiToken = $env:CLOUDFLARE_API_TOKEN

if (-not $zoneId -or -not $apiToken) {
    Write-Host "[ERROR] Cloudflare credentials not found in .env file!" -ForegroundColor Red
    Write-Host "Please add CLOUDFLARE_ZONE_ID and CLOUDFLARE_API_TOKEN to your .env file." -ForegroundColor Yellow
    exit 1
}

Write-Host "[OK] Cloudflare credentials found" -ForegroundColor Green
Write-Host "  Zone ID: $zoneId" -ForegroundColor Gray
Write-Host ""

# Python script path
$scriptPath = "services\cloudflare-service\cloudflare_client.py"

if (-not (Test-Path $scriptPath)) {
    Write-Host "[ERROR] Cloudflare client script not found at: $scriptPath" -ForegroundColor Red
    exit 1
}

# Execute actions based on parameters
if ($ShowInfo) {
    Write-Host "[INFO] Fetching Cloudflare zone information..." -ForegroundColor Yellow
    & python -c @"
import os
import sys
sys.path.insert(0, 'services/cloudflare-service')
from cloudflare_client import CloudflareClient, CloudflareConfig

config = CloudflareConfig(
    zone_id=os.getenv('CLOUDFLARE_ZONE_ID'),
    account_id=os.getenv('CLOUDFLARE_ACCOUNT_ID'),
    api_token=os.getenv('CLOUDFLARE_API_TOKEN')
)
client = CloudflareClient(config)

# Zone info
zone_info = client.get_zone_info()
print(f'\n=== Zone Information ===')
print(f'Name: {zone_info.get(\"name\", \"Unknown\")}')
print(f'Status: {zone_info.get(\"status\", \"Unknown\")}')
print(f'Name Servers: {zone_info.get(\"name_servers\", [])}')

# DNS Records
print(f'\n=== DNS Records ===')
records = client.list_dns_records()
for record in records:
    proxy = '🟠 Proxied' if record['proxied'] else '⚪ DNS Only'
    print(f'{record[\"type\"]:6} {record[\"name\"]:35} -> {record[\"content\"]:25} {proxy}')

# Settings
print(f'\n=== Security Settings ===')
settings = client.get_zone_settings()
print(f'SSL Mode: {settings.get(\"ssl\", \"Unknown\")}')
print(f'Always HTTPS: {settings.get(\"always_use_https\", \"Unknown\")}')
print(f'Security Level: {settings.get(\"security_level\", \"Unknown\")}')
"@
}

if ($SetupDNS) {
    if (-not $ServerIP) {
        Write-Host "[ERROR] Server IP required for DNS setup! Use -ServerIP parameter." -ForegroundColor Red
        exit 1
    }
    
    Write-Host "[INFO] Setting up DNS records for IP: $ServerIP" -ForegroundColor Yellow
    & python -c @"
import os
import sys
sys.path.insert(0, 'services/cloudflare-service')
from cloudflare_client import CloudflareClient, CloudflareConfig, setup_production_dns

config = CloudflareConfig(
    zone_id=os.getenv('CLOUDFLARE_ZONE_ID'),
    account_id=os.getenv('CLOUDFLARE_ACCOUNT_ID'),
    api_token=os.getenv('CLOUDFLARE_API_TOKEN')
)
client = CloudflareClient(config)
setup_production_dns(client, '$ServerIP')
"@
}

if ($SetupSecurity) {
    Write-Host "[INFO] Configuring security settings..." -ForegroundColor Yellow
    & python -c @"
import os
import sys
sys.path.insert(0, 'services/cloudflare-service')
from cloudflare_client import CloudflareClient, CloudflareConfig, setup_security, setup_page_rules

config = CloudflareConfig(
    zone_id=os.getenv('CLOUDFLARE_ZONE_ID'),
    account_id=os.getenv('CLOUDFLARE_ACCOUNT_ID'),
    api_token=os.getenv('CLOUDFLARE_API_TOKEN')
)
client = CloudflareClient(config)
setup_security(client)
setup_page_rules(client)
"@
}

if ($PurgeCache) {
    Write-Host "[INFO] Purging Cloudflare cache..." -ForegroundColor Yellow
    & python -c @"
import os
import sys
sys.path.insert(0, 'services/cloudflare-service')
from cloudflare_client import CloudflareClient, CloudflareConfig

config = CloudflareConfig(
    zone_id=os.getenv('CLOUDFLARE_ZONE_ID'),
    account_id=os.getenv('CLOUDFLARE_ACCOUNT_ID'),
    api_token=os.getenv('CLOUDFLARE_API_TOKEN')
)
client = CloudflareClient(config)
if client.purge_cache_all():
    print('✅ Cache purged successfully!')
"@
}

# Show help if no action specified
if (-not ($ShowInfo -or $SetupDNS -or $SetupSecurity -or $PurgeCache)) {
    Write-Host "Usage:" -ForegroundColor Cyan
    Write-Host "  .\scripts\cloudflare-setup.ps1 -ShowInfo                Show zone information" -ForegroundColor Gray
    Write-Host "  .\scripts\cloudflare-setup.ps1 -SetupDNS -ServerIP <IP> Setup DNS records" -ForegroundColor Gray
    Write-Host "  .\scripts\cloudflare-setup.ps1 -SetupSecurity           Configure security" -ForegroundColor Gray
    Write-Host "  .\scripts\cloudflare-setup.ps1 -PurgeCache              Purge all cache" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Cyan
    Write-Host "  .\scripts\cloudflare-setup.ps1 -ShowInfo" -ForegroundColor Gray
    Write-Host "  .\scripts\cloudflare-setup.ps1 -SetupDNS -ServerIP 203.0.113.1" -ForegroundColor Gray
    Write-Host "  .\scripts\cloudflare-setup.ps1 -SetupSecurity -PurgeCache" -ForegroundColor Gray
    Write-Host ""
}

Write-Host ""
Write-Host "[DONE] Cloudflare setup completed!" -ForegroundColor Green

