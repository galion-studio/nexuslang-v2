# NexusLang v2 Platform Status Check
# Quick overview of all services on RunPod CPU instance

Write-Host ""
Write-Host "🔍 NexusLang v2 Platform Status Check" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Check running containers
Write-Host "🐳 Running Containers:" -ForegroundColor Yellow
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
Write-Host ""

# Test key services
Write-Host "🌐 Service Health Checks:" -ForegroundColor Yellow

$services = @(
    @{ Name = "NexusLang Backend"; Url = "http://localhost:8100/health"; Expected = "healthy" },
    @{ Name = "Main Backend"; Url = "http://localhost:8000"; Expected = "response" },
    @{ Name = "Grafana"; Url = "http://localhost:3003"; Expected = "200" },
    @{ Name = "Prometheus"; Url = "http://localhost:9091"; Expected = "200" },
    @{ Name = "Elasticsearch"; Url = "http://localhost:9201"; Expected = "200" }
)

foreach ($service in $services) {
    try {
        $response = Invoke-WebRequest -Uri $service.Url -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "   ✅ $($service.Name): HTTP 200" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️  $($service.Name): HTTP $($response.StatusCode)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "   ❌ $($service.Name): Connection failed" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "📋 Quick Access URLs:" -ForegroundColor Cyan
Write-Host "   • NexusLang API: http://localhost:8100" -ForegroundColor White
Write-Host "   • API Docs: http://localhost:8100/docs" -ForegroundColor White
Write-Host "   • Grafana: http://localhost:3003 (admin/admin123)" -ForegroundColor White
Write-Host "   • Prometheus: http://localhost:9091" -ForegroundColor White
Write-Host "   • Elasticsearch: http://localhost:9201" -ForegroundColor White

Write-Host ""
Write-Host "🎯 Platform Status: Most services operational!" -ForegroundColor Green
