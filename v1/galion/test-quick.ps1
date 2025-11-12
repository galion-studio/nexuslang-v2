# Quick API Test - Register User and Login
Write-Host "Testing NEXUS API..." -ForegroundColor Cyan

# Generate random user
$randomId = Get-Random -Minimum 1000 -Maximum 9999
$email = "testuser$randomId@example.com"
$password = "SecurePass123!"
$name = "Test User $randomId"

Write-Host "`n1. Registering user: $email" -ForegroundColor Yellow
$registerBody = @{
    email = $email
    password = $password
    name = $name
} | ConvertTo-Json

try {
    $registerResponse = Invoke-RestMethod -Uri "http://localhost:8080/api/v1/auth/register" `
        -Method POST `
        -ContentType "application/json" `
        -Body $registerBody
    
    Write-Host "✓ User registered successfully!" -ForegroundColor Green
    Write-Host "  User ID: $($registerResponse.id)" -ForegroundColor Gray
} catch {
    Write-Host "✗ Registration failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host "`n2. Logging in..." -ForegroundColor Yellow
$loginBody = @{
    email = $email
    password = $password
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "http://localhost:8080/api/v1/auth/login" `
        -Method POST `
        -ContentType "application/json" `
        -Body $loginBody
    
    Write-Host "✓ Login successful!" -ForegroundColor Green
    Write-Host "  Token received" -ForegroundColor Gray
    $token = $loginResponse.access_token
} catch {
    Write-Host "✗ Login failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host "`n3. Getting user profile..." -ForegroundColor Yellow
try {
    $headers = @{
        "Authorization" = "Bearer $token"
    }
    $profileResponse = Invoke-RestMethod -Uri "http://localhost:8080/api/v1/auth/me" `
        -Method GET `
        -Headers $headers
    
    Write-Host "✓ Profile retrieved!" -ForegroundColor Green
    Write-Host "  Name: $($profileResponse.name)" -ForegroundColor Gray
    Write-Host "  Email: $($profileResponse.email)" -ForegroundColor Gray
}
catch {
    Write-Host "✗ Profile fetch failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host "`n================================" -ForegroundColor Cyan
Write-Host "✓ ALL TESTS PASSED!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host "`nNexus API is working perfectly!`n" -ForegroundColor Green

