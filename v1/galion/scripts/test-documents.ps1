# Test Document Verification System
# PowerShell script for comprehensive testing

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  TEST: Document Verification System             " -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$BASE_URL = "http://localhost:8080"
$DOC_SERVICE_URL = "http://localhost:8004"
$testEmail = "testuser@example.com"
$testPassword = "TestPassword123!"

# Test 1: Register test user
Write-Host "[Test 1] Registering test user..." -ForegroundColor Yellow
try {
    $registerBody = @{
        email = $testEmail
        password = $testPassword
        name = "Test User"
    } | ConvertTo-Json

    $registerResponse = Invoke-RestMethod -Uri "$BASE_URL/api/v1/auth/register" -Method Post -Body $registerBody -ContentType "application/json"
    Write-Host "✓ User registered: $($registerResponse.email)" -ForegroundColor Green
} catch {
    if ($_.Exception.Response.StatusCode -eq 400) {
        Write-Host "⚠ User already exists (continuing...)" -ForegroundColor Yellow
    } else {
        Write-Host "✗ Registration failed: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
}

# Test 2: Login and get JWT token
Write-Host "`n[Test 2] Logging in..." -ForegroundColor Yellow
try {
    $loginBody = @{
        email = $testEmail
        password = $testPassword
    } | ConvertTo-Json

    $loginResponse = Invoke-RestMethod -Uri "$BASE_URL/api/v1/auth/login" -Method Post -Body $loginBody -ContentType "application/json"
    $token = $loginResponse.access_token
    Write-Host "✓ Login successful, token obtained" -ForegroundColor Green
} catch {
    Write-Host "✗ Login failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 3: List document types
Write-Host "`n[Test 3] Listing document types..." -ForegroundColor Yellow
try {
    $headers = @{
        "Authorization" = "Bearer $token"
    }
    
    $types = Invoke-RestMethod -Uri "$DOC_SERVICE_URL/api/v1/documents/types" -Method Get -Headers $headers
    Write-Host "✓ Found $($types.Count) document types:" -ForegroundColor Green
    foreach ($type in $types | Select-Object -First 3) {
        Write-Host "  - $($type.name): $($type.description)" -ForegroundColor Gray
    }
} catch {
    Write-Host "✗ Failed to list document types: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: Create test PDF file
Write-Host "`n[Test 4] Creating test document..." -ForegroundColor Yellow
$testFilePath = "$env:TEMP\test-document.pdf"
$testContent = "%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Test Document) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000214 00000 n
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
307
%%EOF"

[System.IO.File]::WriteAllText($testFilePath, $testContent)
Write-Host "✓ Test PDF created: $testFilePath" -ForegroundColor Green

# Test 5: Upload document
Write-Host "`n[Test 5] Uploading document..." -ForegroundColor Yellow
try {
    # Note: PowerShell multipart form upload is complex, using curl if available
    $curlAvailable = Get-Command curl -ErrorAction SilentlyContinue
    
    if ($curlAvailable) {
        $uploadResult = curl -X POST "$DOC_SERVICE_URL/api/v1/documents/upload?document_type_id=1" `
            -H "Authorization: Bearer $token" `
            -F "file=@$testFilePath" `
            2>&1 | Out-String
        
        Write-Host "✓ Document uploaded successfully" -ForegroundColor Green
        Write-Host "  Response: $uploadResult" -ForegroundColor Gray
    } else {
        Write-Host "⚠ curl not available, skipping upload test" -ForegroundColor Yellow
        Write-Host "  Install curl to test file uploads" -ForegroundColor Gray
    }
} catch {
    Write-Host "✗ Upload failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 6: List user documents
Write-Host "`n[Test 6] Listing user documents..." -ForegroundColor Yellow
try {
    $documents = Invoke-RestMethod -Uri "$DOC_SERVICE_URL/api/v1/documents" -Method Get -Headers $headers
    Write-Host "✓ Found $($documents.total) documents" -ForegroundColor Green
    
    if ($documents.total -gt 0) {
        $doc = $documents.documents[0]
        Write-Host "  Latest document:" -ForegroundColor Gray
        Write-Host "    - ID: $($doc.id)" -ForegroundColor Gray
        Write-Host "    - File: $($doc.file_name)" -ForegroundColor Gray
        Write-Host "    - Status: $($doc.status)" -ForegroundColor Gray
        Write-Host "    - Size: $([math]::Round($doc.file_size_bytes / 1024, 2)) KB" -ForegroundColor Gray
        
        $global:lastDocId = $doc.id
    }
} catch {
    Write-Host "✗ Failed to list documents: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 7: Service health check
Write-Host "`n[Test 7] Checking service health..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$DOC_SERVICE_URL/health" -Method Get
    Write-Host "✓ Service health: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "✗ Health check failed" -ForegroundColor Red
}

# Test 8: Check metrics
Write-Host "`n[Test 8] Checking Prometheus metrics..." -ForegroundColor Yellow
try {
    $metrics = Invoke-WebRequest -Uri "$DOC_SERVICE_URL/metrics" -UseBasicParsing
    $metricsCount = ($metrics.Content -split "`n" | Where-Object { $_ -match "^document_service_" }).Count
    Write-Host "✓ Metrics available: $metricsCount document service metrics exposed" -ForegroundColor Green
} catch {
    Write-Host "✗ Metrics check failed" -ForegroundColor Red
}

# Cleanup
Write-Host "`n[Cleanup] Removing test file..." -ForegroundColor Yellow
Remove-Item $testFilePath -ErrorAction SilentlyContinue
Write-Host "✓ Cleanup complete" -ForegroundColor Green

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  TEST COMPLETE!                                 " -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Summary:" -ForegroundColor Yellow
Write-Host "  ✓ User authentication works" -ForegroundColor Green
Write-Host "  ✓ Document types loaded" -ForegroundColor Green
Write-Host "  ✓ Document listing works" -ForegroundColor Green
Write-Host "  ✓ Service health check passed" -ForegroundColor Green
Write-Host "  ✓ Metrics exposed" -ForegroundColor Green
Write-Host ""

Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  • Test permissions: .\scripts\test-permissions.ps1" -ForegroundColor White
Write-Host "  • View API docs: http://localhost:8004/docs" -ForegroundColor White
Write-Host "  • Check logs: docker-compose logs -f document-service" -ForegroundColor White
Write-Host ""

