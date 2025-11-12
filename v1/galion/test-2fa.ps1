# Test 2FA Implementation
# Quick test script for Two-Factor Authentication

$baseUrl = "http://localhost:8001"
$email = "test2fa@example.com"
$password = "Test2FA123!"
$name = "2FA Test User"

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Testing 2FA Implementation" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Register user
Write-Host "1. Registering test user..." -ForegroundColor Yellow
$registerBody = @{
    email = $email
    password = $password
    name = $name
} | ConvertTo-Json

try {
    $registerResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/auth/register" `
        -Method Post `
        -Body $registerBody `
        -ContentType "application/json"
    Write-Host "✓ User registered successfully" -ForegroundColor Green
    Write-Host ""
} catch {
    if ($_.Exception.Response.StatusCode -eq 400) {
        Write-Host "! User already exists, continuing..." -ForegroundColor Yellow
    } else {
        Write-Host "✗ Registration failed: $_" -ForegroundColor Red
        exit 1
    }
}

# Step 2: Login to get token
Write-Host "2. Logging in..." -ForegroundColor Yellow
$loginBody = @{
    email = $email
    password = $password
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/auth/login" `
        -Method Post `
        -Body $loginBody `
        -ContentType "application/json"
    
    $token = $loginResponse.data.token
    Write-Host "✓ Login successful" -ForegroundColor Green
    Write-Host "  Token: $($token.Substring(0,20))..." -ForegroundColor Gray
    Write-Host ""
} catch {
    Write-Host "✗ Login failed: $_" -ForegroundColor Red
    exit 1
}

# Step 3: Check 2FA status
Write-Host "3. Checking 2FA status..." -ForegroundColor Yellow
$headers = @{
    "Authorization" = "Bearer $token"
}

try {
    $statusResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/2fa/status" `
        -Method Get `
        -Headers $headers
    
    Write-Host "✓ 2FA Status:" -ForegroundColor Green
    Write-Host "  Enabled: $($statusResponse.data.enabled)" -ForegroundColor Gray
    Write-Host "  Backup Codes: $($statusResponse.data.backup_codes_count)" -ForegroundColor Gray
    Write-Host ""
} catch {
    Write-Host "✗ Failed to get status: $_" -ForegroundColor Red
}

# Step 4: Setup 2FA
Write-Host "4. Setting up 2FA..." -ForegroundColor Yellow
try {
    $setupResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/2fa/setup" `
        -Method Post `
        -Headers $headers
    
    Write-Host "✓ 2FA Setup initiated" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Secret: $($setupResponse.data.secret)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Backup Codes (SAVE THESE!):" -ForegroundColor Yellow
    foreach ($code in $setupResponse.data.backup_codes) {
        Write-Host "    $code" -ForegroundColor White
    }
    Write-Host ""
    Write-Host "  QR Code generated (base64 image)" -ForegroundColor Gray
    Write-Host ""
    
    $secret = $setupResponse.data.secret
    $backupCodes = $setupResponse.data.backup_codes
    
    # Save QR code to file
    $qrData = $setupResponse.data.qr_code -replace '^data:image/png;base64,', ''
    $qrBytes = [Convert]::FromBase64String($qrData)
    [IO.File]::WriteAllBytes("2fa-qr-code.png", $qrBytes)
    Write-Host "  QR Code saved to: 2fa-qr-code.png" -ForegroundColor Cyan
    Write-Host "  Scan with Google Authenticator, Authy, or similar app" -ForegroundColor Cyan
    Write-Host ""
    
} catch {
    if ($_.Exception.Response.StatusCode -eq 400) {
        Write-Host "! 2FA already enabled. To test, disable it first." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "To disable 2FA, use:" -ForegroundColor Gray
        Write-Host "  curl -X POST http://localhost:8001/api/v1/2fa/disable \" -ForegroundColor Gray
        Write-Host "    -H 'Authorization: Bearer YOUR_TOKEN' \" -ForegroundColor Gray
        Write-Host "    -H 'Content-Type: application/json' \" -ForegroundColor Gray
        Write-Host "    -d '{""password"":""$password"",""code"":""123456""}'" -ForegroundColor Gray
        Write-Host ""
    } else {
        Write-Host "✗ Setup failed: $_" -ForegroundColor Red
    }
    exit 1
}

# Step 5: Instructions for verification
Write-Host "5. Next Steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "   a) Open 2fa-qr-code.png and scan with your authenticator app" -ForegroundColor White
Write-Host "   OR" -ForegroundColor Gray
Write-Host "   b) Manually enter secret: $secret" -ForegroundColor White
Write-Host ""
Write-Host "   c) Get the 6-digit code from your app" -ForegroundColor White
Write-Host ""
Write-Host "   d) Verify and enable 2FA:" -ForegroundColor White
Write-Host "      curl -X POST http://localhost:8001/api/v1/2fa/verify \" -ForegroundColor Gray
Write-Host "        -H 'Authorization: Bearer $token' \" -ForegroundColor Gray
Write-Host "        -H 'Content-Type: application/json' \" -ForegroundColor Gray
Write-Host "        -d '{""code"":""YOUR_6_DIGIT_CODE""}'" -ForegroundColor Gray
Write-Host ""
Write-Host "   e) Test login with 2FA:" -ForegroundColor White
Write-Host "      # Step 1: Login with password" -ForegroundColor Gray
Write-Host "      curl -X POST http://localhost:8001/api/v1/auth/login \" -ForegroundColor Gray
Write-Host "        -H 'Content-Type: application/json' \" -ForegroundColor Gray
Write-Host "        -d '{""email"":""$email"",""password"":""$password""}'" -ForegroundColor Gray
Write-Host ""
Write-Host "      # Step 2: Complete with 2FA code" -ForegroundColor Gray
Write-Host "      curl -X POST 'http://localhost:8001/api/v1/auth/login/2fa?user_id=USER_ID&code=123456'" -ForegroundColor Gray
Write-Host ""

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "2FA Setup Complete!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Test Credentials:" -ForegroundColor Yellow
Write-Host "  Email: $email" -ForegroundColor White
Write-Host "  Password: $password" -ForegroundColor White
Write-Host "  Token: $token" -ForegroundColor White
Write-Host ""
Write-Host "QR Code: 2fa-qr-code.png" -ForegroundColor Cyan
Write-Host ""

# Optional: Test with pyotp if available
Write-Host "Want to test verification automatically? (Y/N): " -ForegroundColor Yellow -NoNewline
$response = Read-Host
if ($response -eq "Y" -or $response -eq "y") {
    Write-Host ""
    Write-Host "Installing pyotp for testing..." -ForegroundColor Gray
    pip install pyotp --quiet
    
    Write-Host "Generating current TOTP code..." -ForegroundColor Gray
    $pythonCode = @"
import pyotp
totp = pyotp.TOTP('$secret')
print(totp.now())
"@
    
    $currentCode = python -c $pythonCode
    Write-Host "Current Code: $currentCode" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "Verifying 2FA..." -ForegroundColor Yellow
    $verifyBody = @{
        code = $currentCode
    } | ConvertTo-Json
    
    try {
        $verifyResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/2fa/verify" `
            -Method Post `
            -Headers $headers `
            -Body $verifyBody `
            -ContentType "application/json"
        
        Write-Host "✓ 2FA ENABLED SUCCESSFULLY!" -ForegroundColor Green
        Write-Host ""
        
        # Test login with 2FA
        Write-Host "Testing login flow with 2FA..." -ForegroundColor Yellow
        $loginResponse2 = Invoke-RestMethod -Uri "$baseUrl/api/v1/auth/login" `
            -Method Post `
            -Body $loginBody `
            -ContentType "application/json"
        
        if ($loginResponse2.data.requires_2fa) {
            Write-Host "✓ Login correctly requires 2FA" -ForegroundColor Green
            $userId = $loginResponse2.data.user_id
            
            # Generate new code
            $newCode = python -c $pythonCode
            Write-Host "  Using code: $newCode" -ForegroundColor Gray
            
            # Complete login
            $twoFAResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/auth/login/2fa?user_id=$userId&code=$newCode" `
                -Method Post
            
            Write-Host "✓ 2FA login successful!" -ForegroundColor Green
            Write-Host "  New token: $($twoFAResponse.data.token.Substring(0,20))..." -ForegroundColor Gray
            Write-Host ""
            Write-Host "==================================" -ForegroundColor Cyan
            Write-Host "ALL TESTS PASSED! ✓" -ForegroundColor Green
            Write-Host "==================================" -ForegroundColor Cyan
        }
        
    } catch {
        Write-Host "✗ Verification failed: $_" -ForegroundColor Red
    }
}

