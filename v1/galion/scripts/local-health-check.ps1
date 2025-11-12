# GALION Local Health Check & Debugger
# PowerShell version for Windows testing
# Usage: .\scripts\local-health-check.ps1

Write-Host "========================================" -ForegroundColor Green
Write-Host "  GALION Health Check & Debugger" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

$ErrorCount = 0
$WarningCount = 0

# Function to test a condition
function Test-Condition {
    param(
        [string]$Name,
        [scriptblock]$Test,
        [string]$ErrorMessage = "",
        [string]$Type = "Error"
    )
    
    Write-Host "Checking: $Name... " -NoNewline
    
    try {
        $result = & $Test
        if ($result) {
            Write-Host "✓ PASS" -ForegroundColor Green
            return $true
        } else {
            if ($Type -eq "Warning") {
                Write-Host "⚠ WARN" -ForegroundColor Yellow
                if ($ErrorMessage) { Write-Host "  $ErrorMessage" -ForegroundColor Yellow }
                $script:WarningCount++
            } else {
                Write-Host "✗ FAIL" -ForegroundColor Red
                if ($ErrorMessage) { Write-Host "  $ErrorMessage" -ForegroundColor Red }
                $script:ErrorCount++
            }
            return $false
        }
    } catch {
        Write-Host "✗ ERROR" -ForegroundColor Red
        Write-Host "  $_" -ForegroundColor Red
        $script:ErrorCount++
        return $false
    }
}

Write-Host "=== LOCAL ENVIRONMENT CHECKS ===" -ForegroundColor Cyan
Write-Host ""

# Check if files exist
Test-Condition "docker-compose.yml exists" { Test-Path "docker-compose.yml" } "Missing main orchestration file"
Test-Condition ".env.example exists" { Test-Path ".env.example" } "Missing configuration template"
Test-Condition "scripts directory exists" { Test-Path "scripts" } "Missing scripts directory"
Test-Condition "configs directory exists" { Test-Path "configs" } "Missing configs directory"
Test-Condition "nginx directory exists" { Test-Path "nginx" } "Missing nginx directory"

Write-Host ""
Write-Host "=== CONFIGURATION FILES ===" -ForegroundColor Cyan
Write-Host ""

Test-Condition "PostgreSQL config exists" { Test-Path "configs/postgresql.conf" }
Test-Condition "PgBouncer config exists" { Test-Path "configs/pgbouncer.ini" }
Test-Condition "Nginx main config exists" { Test-Path "nginx/nginx.conf" }
Test-Condition "Prometheus config exists" { Test-Path "monitoring/prometheus.yml" }
Test-Condition "Alert rules exist" { Test-Path "monitoring/alerts.yml" }

Write-Host ""
Write-Host "=== DEPLOYMENT SCRIPTS ===" -ForegroundColor Cyan
Write-Host ""

$requiredScripts = @(
    "vps-setup.sh",
    "generate-secrets.sh",
    "full-deployment.sh",
    "deploy.sh",
    "backup.sh",
    "restore.sh",
    "health-check.sh",
    "migrate.sh"
)

foreach ($script in $requiredScripts) {
    Test-Condition "$script exists" { Test-Path "scripts/$script" } -Type "Warning"
}

Write-Host ""
Write-Host "=== APPLICATION CODE ===" -ForegroundColor Cyan
Write-Host ""

Test-Condition "Health API exists" { Test-Path "app/api/health.py" } -Type "Warning"
Test-Condition "Cache module exists" { Test-Path "app/core/cache.py" } -Type "Warning"
Test-Condition "Circuit breaker exists" { Test-Path "app/core/circuit_breaker.py" } -Type "Warning"
Test-Condition "Rate limiting exists" { Test-Path "app/middleware/rate_limit.py" } -Type "Warning"

Write-Host ""
Write-Host "=== DOCUMENTATION ===" -ForegroundColor Cyan
Write-Host ""

Test-Condition "Deployment checklist" { Test-Path "DEPLOYMENT_CHECKLIST.md" }
Test-Condition "Runbook" { Test-Path "docs/RUNBOOK.md" }
Test-Condition "Troubleshooting guide" { Test-Path "docs/TROUBLESHOOTING.md" }
Test-Condition "Scaling guide" { Test-Path "docs/SCALING_GUIDE.md" }

Write-Host ""
Write-Host "=== DOCKER COMPOSE VALIDATION ===" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is installed
if (Get-Command docker -ErrorAction SilentlyContinue) {
    Write-Host "✓ Docker is installed" -ForegroundColor Green
    
    # Validate docker-compose.yml
    Write-Host "Validating docker-compose.yml... " -NoNewline
    $validateResult = docker compose config 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ VALID" -ForegroundColor Green
        
        # Count services
        $services = ($validateResult | Select-String "services:" -Context 0,100 | Out-String)
        Write-Host "  Services defined in compose file" -ForegroundColor Gray
    } else {
        Write-Host "✗ INVALID" -ForegroundColor Red
        Write-Host "  $validateResult" -ForegroundColor Red
        $ErrorCount++
    }
} else {
    Write-Host "⚠ Docker not installed (OK for Windows development)" -ForegroundColor Yellow
    $WarningCount++
}

Write-Host ""
Write-Host "=== ENVIRONMENT VARIABLES ===" -ForegroundColor Cyan
Write-Host ""

if (Test-Path ".env") {
    Write-Host "✓ .env file exists" -ForegroundColor Green
    
    # Check for placeholder values
    $envContent = Get-Content ".env" -Raw
    
    if ($envContent -match "GENERATE_STRONG_PASSWORD|your-key-here|your-password-here") {
        Write-Host "  ⚠ Contains placeholder values - run generate-secrets.sh" -ForegroundColor Yellow
        $WarningCount++
    } else {
        Write-Host "  ✓ Appears configured" -ForegroundColor Green
    }
    
    # Check for required variables
    $requiredVars = @("POSTGRES_PASSWORD", "REDIS_PASSWORD", "JWT_SECRET", "OPENAI_API_KEY", "ELEVENLABS_API_KEY")
    foreach ($var in $requiredVars) {
        if ($envContent -match "$var=\S+") {
            Write-Host "  ✓ $var is set" -ForegroundColor Green
        } else {
            Write-Host "  ✗ $var is missing or empty" -ForegroundColor Red
            $ErrorCount++
        }
    }
} else {
    Write-Host "⚠ .env file not found" -ForegroundColor Yellow
    Write-Host "  Run: ./scripts/generate-secrets.sh (on Linux)" -ForegroundColor Yellow
    Write-Host "  Or copy: .env.example to .env and configure" -ForegroundColor Yellow
    $WarningCount++
}

Write-Host ""
Write-Host "=== MEMORY ALLOCATION CHECK ===" -ForegroundColor Cyan
Write-Host ""

if (Test-Path "docker-compose.yml") {
    $composeContent = Get-Content "docker-compose.yml" -Raw
    
    # Extract memory limits
    $memoryLimits = [regex]::Matches($composeContent, 'memory:\s*(\d+)M')
    $totalMemoryMB = 0
    
    foreach ($match in $memoryLimits) {
        $totalMemoryMB += [int]$match.Groups[1].Value
    }
    
    $totalMemoryGB = [math]::Round($totalMemoryMB / 1024, 2)
    
    Write-Host "Total allocated memory: $totalMemoryGB GB" -ForegroundColor Cyan
    
    if ($totalMemoryGB -le 11) {
        Write-Host "✓ Memory allocation OK for 16GB server" -ForegroundColor Green
        Write-Host "  Buffer: $([math]::Round(16 - $totalMemoryGB, 2)) GB available for system" -ForegroundColor Gray
    } elseif ($totalMemoryGB -le 13) {
        Write-Host "⚠ Memory allocation tight" -ForegroundColor Yellow
        Write-Host "  Only $([math]::Round(16 - $totalMemoryGB, 2)) GB buffer" -ForegroundColor Yellow
        $WarningCount++
    } else {
        Write-Host "✗ Memory over-allocated!" -ForegroundColor Red
        Write-Host "  Exceeds 16GB by $([math]::Round($totalMemoryGB - 16, 2)) GB" -ForegroundColor Red
        $ErrorCount++
    }
}

Write-Host ""
Write-Host "=== FILE INTEGRITY CHECK ===" -ForegroundColor Cyan
Write-Host ""

# Check for common file issues
$issues = @()

# Check for CRLF in shell scripts
Get-ChildItem "scripts/*.sh" -ErrorAction SilentlyContinue | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    if ($content -match "`r`n") {
        $issues += "  ⚠ $($_.Name) has Windows line endings (CRLF)"
    }
}

if ($issues.Count -gt 0) {
    Write-Host "⚠ Line ending issues detected:" -ForegroundColor Yellow
    $issues | ForEach-Object { Write-Host $_ -ForegroundColor Yellow }
    Write-Host "  These will be fixed when uploaded to Linux server" -ForegroundColor Gray
    $WarningCount++
} else {
    Write-Host "✓ No file integrity issues" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  HEALTH CHECK SUMMARY" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

if ($ErrorCount -eq 0 -and $WarningCount -eq 0) {
    Write-Host "✅ ALL CHECKS PASSED!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your deployment is ready to execute!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. SSH to server: ssh root@54.37.161.67" -ForegroundColor White
    Write-Host "  2. Follow: START_DEPLOYMENT.md" -ForegroundColor White
    Write-Host "  3. Execute deployment" -ForegroundColor White
    
} elseif ($ErrorCount -eq 0) {
    Write-Host "⚠ CHECKS PASSED WITH WARNINGS" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Errors: $ErrorCount" -ForegroundColor Green
    Write-Host "Warnings: $WarningCount" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "You can proceed with deployment." -ForegroundColor Yellow
    Write-Host "Warnings are typically OK and will be resolved on server." -ForegroundColor Gray
    
} else {
    Write-Host "✗ CHECKS FAILED" -ForegroundColor Red
    Write-Host ""
    Write-Host "Errors: $ErrorCount" -ForegroundColor Red
    Write-Host "Warnings: $WarningCount" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please fix the errors above before deploying." -ForegroundColor Red
}

Write-Host ""
Write-Host "Detailed reports available in:" -ForegroundColor Cyan
Write-Host "  - DEPLOYMENT_CHECKLIST.md" -ForegroundColor White
Write-Host "  - docs/TROUBLESHOOTING.md" -ForegroundColor White
Write-Host ""

# Create detailed report file
$reportPath = "health-check-report.txt"
@"
GALION Health Check Report
Generated: $(Get-Date)
========================================

Errors: $ErrorCount
Warnings: $WarningCount

Status: $(if ($ErrorCount -eq 0) { "READY TO DEPLOY" } else { "NEEDS FIXES" })

========================================
Next Steps:
1. Review any errors above
2. Fix configuration issues
3. Run health check again
4. Proceed with deployment

For deployment guide, see:
- START_DEPLOYMENT.md
- DEPLOYMENT_CHECKLIST.md
"@ | Out-File $reportPath

Write-Host "Report saved to: $reportPath" -ForegroundColor Gray
Write-Host ""

