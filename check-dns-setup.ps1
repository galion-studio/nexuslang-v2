# DNS Verification Script for Galion Domains
# Run this to check if DNS is properly configured

Write-Host "🔍 DNS Verification for Galion Platform" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host ""

$domains = @("galion.studio", "api.galion.studio", "studio.galion.studio", "app.galion.studio", "dev.galion.studio")
$expectedIP = "213.173.105.83"

Write-Host "Expected IP: $expectedIP" -ForegroundColor Yellow
Write-Host ""

foreach ($domain in $domains) {
    Write-Host "Checking $domain..." -ForegroundColor Green

    try {
        $result = Resolve-DnsName -Name $domain -Type A -ErrorAction Stop
        $resolvedIP = $result.IPAddress

        Write-Host "  Resolved IP: $resolvedIP" -ForegroundColor White

        if ($resolvedIP -eq $expectedIP) {
            Write-Host "  ✅ Direct IP match - DNS working!" -ForegroundColor Green
        } elseif ($resolvedIP -match "^(104\.|172\.6[4-7]\.|172\.7[0-1]\.)") {
            Write-Host "  ✅ Cloudflare IP - DNS proxied correctly!" -ForegroundColor Green
        } else {
            Write-Host "  ⚠️  Unexpected IP - Check DNS settings" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  ❌ DNS resolution failed" -ForegroundColor Red
    }

    Write-Host ""
}

Write-Host "Additional Tests:" -ForegroundColor Cyan
Write-Host "=================" -ForegroundColor Cyan

# Test connectivity
Write-Host "Testing connectivity to $expectedIP..." -ForegroundColor Yellow
$ping = Test-Connection -ComputerName $expectedIP -Count 2 -Quiet
if ($ping) {
    Write-Host "✅ Server is reachable" -ForegroundColor Green
} else {
    Write-Host "❌ Server not reachable" -ForegroundColor Red
}

Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "===========" -ForegroundColor Cyan
Write-Host "1. If DNS shows Cloudflare IPs (104.x.x.x), DNS is working!"
Write-Host "2. Wait 2-10 minutes for DNS propagation"
Write-Host "3. Test with: curl -I https://api.galion.studio/health"
Write-Host "4. If still not working, check Cloudflare proxy status"
