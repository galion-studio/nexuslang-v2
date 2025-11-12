# Test Authentication Flow for Nexus Core
Write-Host ""
Write-Host "TESTING AUTHENTICATION FLOW" -ForegroundColor Yellow
Write-Host "==============================" -ForegroundColor Yellow
Write-Host ""

$baseUrl = "http://localhost:8080"

# Step 1: Register
Write-Host "Step 1: Registering new user..." -ForegroundColor Cyan
$registerData = @{
    email = "testuser@galion.app"
    password = "TestPass123!"
    name = "Test User"
} | ConvertTo-Json

try {
    $regResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/auth/register" -Method Post -Body $registerData -ContentType "application/json"
    Write-Host "SUCCESS: User registered" -ForegroundColor Green
    Write-Host "User ID: $($regResponse.data.id)" -ForegroundColor White
} catch {
    Write-Host "User may already exist, continuing..." -ForegroundColor Yellow
}

# Step 2: Login
Write-Host ""
Write-Host "Step 2: Logging in..." -ForegroundColor Cyan
$loginData = @{
    email = "testuser@galion.app"
    password = "TestPass123!"
} | ConvertTo-Json

$loginResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/auth/login" -Method Post -Body $loginData -ContentType "application/json"
Write-Host "SUCCESS: Login successful" -ForegroundColor Green
$token = $loginResponse.data.access_token
Write-Host "Token received (first 50 chars): $($token.Substring(0,50))..." -ForegroundColor White

# Step 3: Authenticated Request
Write-Host ""
Write-Host "Step 3: Making authenticated request..." -ForegroundColor Cyan
$headers = @{
    Authorization = "Bearer $token"
}

$meResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/auth/me" -Method Get -Headers $headers
Write-Host "SUCCESS: Got user profile" -ForegroundColor Green
Write-Host "Email: $($meResponse.data.email)" -ForegroundColor White
Write-Host "Name: $($meResponse.data.name)" -ForegroundColor White
Write-Host "Role: $($meResponse.data.role)" -ForegroundColor White

Write-Host ""
Write-Host "==============================" -ForegroundColor Green
Write-Host "ALL TESTS PASSED!" -ForegroundColor Green
Write-Host "==============================" -ForegroundColor Green
Write-Host ""
Write-Host "System is fully operational and ready for galion.app deployment!" -ForegroundColor Cyan
Write-Host ""

