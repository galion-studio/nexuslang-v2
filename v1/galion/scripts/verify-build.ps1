# Build Verification - Simple Check

Write-Host "Build Verification" -ForegroundColor Cyan
Write-Host "==================" -ForegroundColor Cyan

$allGood = $true

# Check critical files
$checks = @(
    @{Path="docker-compose.yml"; Name="Docker Compose"},
    @{Path="database\init.sql"; Name="Database Init"},
    @{Path="services\auth-service\Dockerfile"; Name="Auth Dockerfile"},
    @{Path="services\user-service\Dockerfile"; Name="User Dockerfile"},
    @{Path="services\api-gateway\Dockerfile"; Name="Gateway Dockerfile"},
    @{Path="services\analytics-service\Dockerfile"; Name="Analytics Dockerfile"},
    @{Path="services\auth-service\requirements.txt"; Name="Auth Requirements"},
    @{Path="services\user-service\requirements.txt"; Name="User Requirements"},
    @{Path="services\api-gateway\go.mod"; Name="Gateway Go Module"},
    @{Path="services\analytics-service\go.mod"; Name="Analytics Go Module"}
)

foreach ($check in $checks) {
    if (Test-Path $check.Path) {
        Write-Host "OK: $($check.Name)" -ForegroundColor Green
    } else {
        Write-Host "MISSING: $($check.Name)" -ForegroundColor Red
        $allGood = $false
    }
}

Write-Host ""
if ($allGood) {
    Write-Host "READY TO BUILD!" -ForegroundColor Green
    Write-Host "Run: docker-compose build" -ForegroundColor Cyan
} else {
    Write-Host "FIX ERRORS FIRST" -ForegroundColor Red
}

