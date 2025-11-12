# Test Authentication Flow
Write-Host "`n🔥 TESTING AUTHENTICATION FLOW" -ForegroundColor Yellow
Write-Host "================================`n" -ForegroundColor Yellow

$baseUrl = "http://localhost:8080"

# Test 1: Register
Write-Host "1. REGISTERING USER..." -ForegroundColor Cyan
$registerData = @{
    email = "demo@galion.app"
    password = "DemoPass123!"
    name = "Demo User"
} | ConvertTo-Json

try {
    $regResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/auth/register" -Method Post -Body $registerData -ContentType "application/json"
    Write-Host "   ✅ Registration Success!" -ForegroundColor Green
    Write-Host "   User ID: $($regResponse.data.id)" -ForegroundColor White
} catch {
    Write-Host "   ⚠️  User exists, proceeding to login..." -ForegroundColor Yellow
}

# Test 2: Login
Write-Host "`n2. LOGGING IN..." -ForegroundColor Cyan
$loginData = @{
    email = "demo@galion.app"
    password = "DemoPass123!"
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/auth/login" -Method Post -Body $loginData -ContentType "application/json"
    Write-Host "   ✅ Login Success!" -ForegroundColor Green
    $token = $loginResponse.data.access_token
    Write-Host "   Token: $($token.Substring(0,50))..." -ForegroundColor White
    
    # Test 3: Authenticated Request
    Write-Host "`n3. GETTING USER INFO (Authenticated)..." -ForegroundColor Cyan
    $headers = @{
        Authorization = "Bearer $token"
    }
    $meResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/auth/me" -Method Get -Headers $headers
    Write-Host "   ✅ Authenticated Request Success!" -ForegroundColor Green
    Write-Host "   Email: $($meResponse.data.email)" -ForegroundColor White
    Write-Host "   Name: $($meResponse.data.name)" -ForegroundColor White
    Write-Host "   Role: $($meResponse.data.role)" -ForegroundColor White
    
    Write-Host "`n🎉 AUTHENTICATION FLOW WORKS PERFECTLY!" -ForegroundColor Green
    Write-Host "================================`n" -ForegroundColor Green
    
} catch {
    Write-Host "   ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Checking service logs..." -ForegroundColor Yellow
    docker logs nexus-auth-service --tail 10
}

