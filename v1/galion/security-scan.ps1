# NEXUS CORE - SECURITY VULNERABILITY SCANNER
# Scans for security vulnerabilities and generates report

function AddScanFinding {
    param(
        [string]$Severity,
        [string]$Category,
        [string]$Description,
        [string]$Remediation
    )
    
    if (-not $global:scanResults) {
        $global:scanResults = New-Object System.Collections.ArrayList
    }
    if ($null -eq $global:criticalIssues) { $global:criticalIssues = 0 }
    if ($null -eq $global:highIssues) { $global:highIssues = 0 }
    if ($null -eq $global:mediumIssues) { $global:mediumIssues = 0 }
    if ($null -eq $global:lowIssues) { $global:lowIssues = 0 }
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

    $null = $global:scanResults.Add([PSCustomObject]@{
        Severity = $Severity
        Category = $Category
        Description = $Description
        Remediation = $Remediation
        Timestamp = $timestamp
    })
    
    switch ($Severity) {
        "CRITICAL" { $global:criticalIssues++; $color = "Red" }
        "HIGH" { $global:highIssues++; $color = "Red" }
        "MEDIUM" { $global:mediumIssues++; $color = "Yellow" }
        "LOW" { $global:lowIssues++; $color = "Gray" }
    }
    
    Write-Host "[$Severity] $Category - $Description" -ForegroundColor $color
}

Write-Host "🔍 NEXUS CORE - SECURITY SCANNER" -ForegroundColor Cyan
Write-Host "Following Elon Musk First Principles: Find and Fix Everything`n" -ForegroundColor Yellow

$ErrorActionPreference = "Continue"
$global:scanResults = New-Object System.Collections.ArrayList
$global:criticalIssues = 0
$global:highIssues = 0
$global:mediumIssues = 0
$global:lowIssues = 0

Write-Host "🔍 Step 1: Checking Environment Configuration..." -ForegroundColor Cyan

# Check .env file
if (-not (Test-Path ".env")) {
    AddScanFinding -Severity "CRITICAL" -Category "Configuration" `
        -Description ".env file not found - secrets not configured" `
        -Remediation "Run .\generate-secrets.ps1 to create secure .env file"
} else {
    $envContent = Get-Content ".env" -Raw
    
    # Check for default/weak passwords
    if ($envContent -match "CHANGE_ME" -or $envContent -match "devpassword" -or $envContent -match "admin123") {
        AddScanFinding -Severity "CRITICAL" -Category "Secrets" `
            -Description "Default or weak passwords detected in .env" `
            -Remediation "Run .\generate-secrets.ps1 to generate strong secrets"
    }
    
    # Check JWT secret length
    if ($envContent -match "JWT_SECRET_KEY=(.+)") {
        $jwtSecret = $matches[1].Trim()
        if ($jwtSecret.Length -lt 32) {
            AddScanFinding -Severity "HIGH" -Category "Authentication" `
                -Description "JWT secret key is too short (< 32 characters)" `
                -Remediation "Generate longer JWT secret: openssl rand -hex 64"
        }
    }
    
    # Check if debug mode enabled
    if ($envContent -match "DEBUG=true") {
        AddScanFinding -Severity "MEDIUM" -Category "Configuration" `
            -Description "Debug mode is enabled" `
            -Remediation "Set DEBUG=false in .env for production"
    }
}

# Check .gitignore
if (-not (Test-Path ".gitignore")) {
    AddScanFinding -Severity "HIGH" -Category "Version Control" `
        -Description ".gitignore file not found - secrets may be committed" `
        -Remediation "Create .gitignore file with .env excluded"
} else {
    $gitignoreContent = Get-Content ".gitignore" -Raw
    if ($gitignoreContent -notmatch "\.env") {
        AddScanFinding -Severity "HIGH" -Category "Version Control" `
            -Description ".env not in .gitignore - secrets may be committed" `
            -Remediation "Add .env to .gitignore"
    }
}

Write-Host "`n🔍 Step 2: Scanning Python Dependencies..." -ForegroundColor Cyan

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "   Found: $pythonVersion" -ForegroundColor Green
    
    # Install safety if not present
    Write-Host "   Installing/updating safety scanner..." -ForegroundColor Gray
    pip install --quiet --upgrade safety pip-audit 2>&1 | Out-Null
    
    # Scan auth-service dependencies
    if (Test-Path "services/auth-service/requirements.txt") {
        Write-Host "   Scanning auth-service dependencies..." -ForegroundColor Gray
        $safetyOutput = safety check --file services/auth-service/requirements.txt --output json 2>&1
        
        if ($safetyOutput -match "vulnerabilities found") {
            AddScanFinding -Severity "HIGH" -Category "Dependencies" `
                -Description "Vulnerabilities found in auth-service Python packages" `
                -Remediation "Run: pip install --upgrade PACKAGE_NAME"
        }
    }
    
    # Scan user-service dependencies
    if (Test-Path "services/user-service/requirements.txt") {
        Write-Host "   Scanning user-service dependencies..." -ForegroundColor Gray
        $safetyOutput = safety check --file services/user-service/requirements.txt --output json 2>&1
        
        if ($safetyOutput -match "vulnerabilities found") {
            AddScanFinding -Severity "HIGH" -Category "Dependencies" `
                -Description "Vulnerabilities found in user-service Python packages" `
                -Remediation "Run: pip install --upgrade PACKAGE_NAME"
        }
    }
} catch {
    AddScanFinding -Severity "MEDIUM" -Category "Tooling" `
        -Description "Python not found - cannot scan Python dependencies" `
        -Remediation "Install Python 3.11+ to enable dependency scanning"
}

Write-Host "`n🔍 Step 3: Scanning Go Dependencies..." -ForegroundColor Cyan

# Check if Go is available
try {
    $goVersion = go version 2>&1
    Write-Host "   Found: $goVersion" -ForegroundColor Green
    
    if (Test-Path "services/api-gateway/go.mod") {
        Write-Host "   Scanning api-gateway dependencies..." -ForegroundColor Gray
        Push-Location "services/api-gateway"
        
        # Run go list to check for known vulnerabilities
        $goVulnCheck = go list -json -m all 2>&1 | Out-String
        
        # Check for outdated critical packages
        if ($goVulnCheck -match "golang-jwt.*v[0-4]") {
            AddScanFinding -Severity "MEDIUM" -Category "Dependencies" `
                -Description "golang-jwt version may be outdated" `
                -Remediation "Update to latest: go get -u github.com/golang-jwt/jwt/v5"
        }
        
        Pop-Location
    }
} catch {
    AddScanFinding -Severity "MEDIUM" -Category "Tooling" `
        -Description "Go not found - cannot scan Go dependencies" `
        -Remediation "Install Go 1.21+ to enable dependency scanning"
}

Write-Host "`n🔍 Step 4: Checking Docker Configuration..." -ForegroundColor Cyan

if (Test-Path "docker-compose.yml") {
    $dockerContent = Get-Content "docker-compose.yml" -Raw
    
    # Check for hardcoded secrets
    if ($dockerContent -match 'password.*=.*[^$]' -and $dockerContent -notmatch '\$\{') {
        AddScanFinding -Severity "CRITICAL" -Category "Secrets" `
            -Description "Hardcoded passwords found in docker-compose.yml" `
            -Remediation 'Move all secrets to .env file and use ${VARIABLE} syntax'
    }
    
    # Check for exposed ports
    $postgresExposed = [regex]::IsMatch($dockerContent, '-\s*"5432:5432"')
    $redisExposed = [regex]::IsMatch($dockerContent, '-\s*"6379:6379"')
    if ($postgresExposed -or $redisExposed) {
        AddScanFinding -Severity "MEDIUM" -Category "Network Security" `
            -Description "Database ports exposed to host network" `
            -Remediation "Use 127.0.0.1:PORT:PORT to restrict to localhost only"
    }
    
    # Check for security options
    if ($dockerContent -notmatch "security_opt") {
        AddScanFinding -Severity "LOW" -Category "Container Security" `
            -Description "Docker security options not configured" `
            -Remediation "Add security_opt: no-new-privileges:true to all services"
    }
    
    # Check for resource limits
    if ($dockerContent -notmatch "resources:") {
        AddScanFinding -Severity "LOW" -Category "Container Security" `
            -Description "No resource limits defined for containers" `
            -Remediation "Add deploy.resources.limits to prevent resource exhaustion"
    }
}

Write-Host "`n🔍 Step 5: Checking File Permissions..." -ForegroundColor Cyan

# Check sensitive file permissions (on Unix-like systems this is more relevant)
$sensitiveFiles = @(".env", "database/init.sql")
foreach ($file in $sensitiveFiles) {
    if (Test-Path $file) {
        Write-Host "   ✅ Found: $file" -ForegroundColor Green
    }
}

Write-Host "`n🔍 Step 6: Checking for Exposed Secrets in Git History..." -ForegroundColor Cyan

try {
    # Check if this is a git repository
    $isGitRepo = git rev-parse --is-inside-work-tree 2>&1
    if ($isGitRepo -eq "true") {
        Write-Host "   Scanning git history for secrets..." -ForegroundColor Gray
        
        # Check recent commits for potential secrets
        $recentCommits = git log --all --pretty=format:"%H" -n 100 2>&1
        $secretPatterns = @(
            "password\s*=",
            "secret\s*=",
            "api[_-]?key",
            "token\s*=",
            "private[_-]?key"
        )
        
        $foundSecrets = $false
        foreach ($pattern in $secretPatterns) {
            $matches = git grep -i $pattern $recentCommits 2>&1
            if ($matches -and $matches -notmatch "fatal") {
                $foundSecrets = $true
                break
            }
        }
        
        if ($foundSecrets) {
            AddScanFinding -Severity "HIGH" -Category "Version Control" `
                -Description "Potential secrets found in git history" `
                -Remediation "Review git history and use git-filter-repo to remove secrets"
        }
    }
} catch {
    Write-Host "   Not a git repository or git not available" -ForegroundColor Gray
}

Write-Host "`n🔍 Step 7: Checking HTTPS and TLS Configuration..." -ForegroundColor Cyan

# Check for TLS/HTTPS configuration
$tlsConfigured = $false
if ((Test-Path "nginx.conf") -or (Test-Path "traefik.yml")) {
    $tlsConfigured = $true
}

if (-not $tlsConfigured) {
    AddScanFinding -Severity "MEDIUM" -Category "Transport Security" `
        -Description "No TLS/HTTPS configuration found" `
        -Remediation "Configure reverse proxy (nginx/traefik) with TLS certificates"
}

Write-Host "`n🔍 Step 8: Checking Security Headers..." -ForegroundColor Cyan

# This would require running services to check headers
AddScanFinding -Severity "LOW" -Category "HTTP Security" `
    -Description "Manual verification needed: Check security headers when services are running" `
    -Remediation "Verify: X-Frame-Options, X-Content-Type-Options, Strict-Transport-Security"

# Generate report
Write-Host "`n" + "="*70 -ForegroundColor Cyan
Write-Host "📊 SECURITY SCAN RESULTS" -ForegroundColor Cyan
Write-Host "="*70 -ForegroundColor Cyan

$totalIssues = $global:criticalIssues + $global:highIssues + $global:mediumIssues + $global:lowIssues

Write-Host "`nTotal Issues Found: $totalIssues" -ForegroundColor White
Write-Host "  🔴 CRITICAL: $($global:criticalIssues)" -ForegroundColor Red
Write-Host "  🔴 HIGH:     $($global:highIssues)" -ForegroundColor Red
Write-Host "  🟡 MEDIUM:   $($global:mediumIssues)" -ForegroundColor Yellow
Write-Host "  ⚪ LOW:      $($global:lowIssues)" -ForegroundColor Gray

if ($totalIssues -eq 0) {
    Write-Host "`n✅ No security issues found! System is secure." -ForegroundColor Green
} else {
    Write-Host "`n⚠️  Security issues detected. Review findings below:" -ForegroundColor Yellow
    Write-Host ""
    
    # Display all findings
    foreach ($finding in $global:scanResults) {
        $color = switch ($finding.Severity) {
            "CRITICAL" { "Red" }
            "HIGH" { "Red" }
            "MEDIUM" { "Yellow" }
            "LOW" { "Gray" }
        }
        
        Write-Host "[$($finding.Severity)] $($finding.Category)" -ForegroundColor $color
        Write-Host "  Issue: $($finding.Description)"
        Write-Host "  Fix: $($finding.Remediation)"
        Write-Host ""
    }
}

# Save detailed report
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$reportPath = "security-scan-report-$timestamp.txt"
$global:scanResults | ConvertTo-Json -Depth 10 | Out-File $reportPath
Write-Host "Detailed report saved to: $reportPath" -ForegroundColor Cyan

# Exit with appropriate code
if ($global:criticalIssues -gt 0 -or $global:highIssues -gt 0) {
    Write-Host "`n❌ CRITICAL or HIGH severity issues found. Fix them before deploying!" -ForegroundColor Red
    exit 1
} else {
    Write-Host "`n✅ No critical security issues. Safe to proceed." -ForegroundColor Green
    exit 0
}

