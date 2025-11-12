# NEXUS CORE - SECURE SECRETS GENERATOR
# Generates cryptographically secure secrets for .env file

Write-Host "================================" -ForegroundColor Cyan
Write-Host "NEXUS CORE - SECURE SECRETS GENERATOR" -ForegroundColor Cyan
Write-Host "Following Security Best Practices" -ForegroundColor Yellow
Write-Host "================================`n" -ForegroundColor Cyan

function Generate-SecurePassword {
    param (
        [int]$Length = 32
    )
    
    # Use alphanumeric characters only (URL-safe)
    $chars = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz23456789'
    $password = -join (1..$Length | ForEach-Object {
        $bytes = New-Object byte[] 1
        $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
        $rng.GetBytes($bytes)
        $chars[$bytes[0] % $chars.Length]
    })
    return $password
}

function Generate-HexSecret {
    param (
        [int]$Length = 64
    )
    
    $bytes = New-Object byte[] ($Length / 2)
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    $rng.GetBytes($bytes)
    $hex = ($bytes | ForEach-Object { $_.ToString("x2") }) -join ''
    return $hex
}

# Check if .env already exists
if (Test-Path ".env") {
    Write-Host "WARNING: .env file already exists!" -ForegroundColor Yellow
    $response = Read-Host "Do you want to overwrite it? Type 'yes' to continue"
    if ($response -ne "yes") {
        Write-Host "Aborted. Keeping existing .env file." -ForegroundColor Red
        exit 0
    }
}

Write-Host "Generating cryptographically secure secrets...`n" -ForegroundColor Cyan

# Generate secrets
$POSTGRES_PASSWORD = Generate-SecurePassword -Length 32
$REDIS_PASSWORD = Generate-SecurePassword -Length 32
$JWT_SECRET = Generate-HexSecret -Length 64
$GRAFANA_PASSWORD = Generate-SecurePassword -Length 16

Write-Host "Generated POSTGRES_PASSWORD (32 chars)" -ForegroundColor Green
Write-Host "Generated REDIS_PASSWORD (32 chars)" -ForegroundColor Green
Write-Host "Generated JWT_SECRET (64 hex chars)" -ForegroundColor Green
Write-Host "Generated GRAFANA_PASSWORD (16 chars)" -ForegroundColor Green

# Create .env file
$envContent = @"
# NEXUS CORE - ENVIRONMENT VARIABLES
# Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
# WARNING: NEVER commit this file to version control
# WARNING: Keep these secrets secure

# ============================================
# DATABASE CONFIGURATION
# ============================================
POSTGRES_USER=nexuscore
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
POSTGRES_DB=nexuscore
DATABASE_URL=postgresql://nexuscore:$POSTGRES_PASSWORD@postgres:5432/nexuscore

# ============================================
# REDIS CONFIGURATION
# ============================================
REDIS_PASSWORD=$REDIS_PASSWORD
REDIS_URL=redis://:$REDIS_PASSWORD@redis:6379/0

# ============================================
# JWT AUTHENTICATION
# ============================================
JWT_SECRET_KEY=$JWT_SECRET
JWT_ALGORITHM=HS256
JWT_EXPIRATION_SECONDS=3600

# ============================================
# GRAFANA CONFIGURATION
# ============================================
GF_SECURITY_ADMIN_USER=admin
GF_SECURITY_ADMIN_PASSWORD=$GRAFANA_PASSWORD

# ============================================
# API GATEWAY CONFIGURATION
# ============================================
ENVIRONMENT=development
DEBUG=false
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS_PER_MINUTE=60
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080

# ============================================
# KAFKA CONFIGURATION
# ============================================
KAFKA_BOOTSTRAP_SERVERS=kafka:9092

# ============================================
# SECURITY SETTINGS
# ============================================
ENABLE_SECURITY_HEADERS=true
ENABLE_RATE_LIMITING=true
ENABLE_REQUEST_LOGGING=true
SESSION_TIMEOUT_MINUTES=60
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=30
"@

# Write .env file
$envContent | Out-File -FilePath ".env" -Encoding UTF8 -NoNewline

Write-Host "`nCreated .env file with secure secrets" -ForegroundColor Green

# Display summary
Write-Host "`n======================================================================" -ForegroundColor Cyan
Write-Host "SECURITY SECRETS GENERATED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Cyan

Write-Host "`nImportant Credentials (Save these securely!):`n" -ForegroundColor Yellow

Write-Host "Grafana Dashboard:" -ForegroundColor Cyan
Write-Host "  URL:      http://localhost:3000"
Write-Host "  Username: admin"
Write-Host "  Password: $GRAFANA_PASSWORD" -ForegroundColor Green

Write-Host "`nPostgreSQL Database:" -ForegroundColor Cyan
Write-Host "  Username: nexuscore"
Write-Host "  Password: $POSTGRES_PASSWORD" -ForegroundColor Green

Write-Host "`nSECURITY REMINDERS:" -ForegroundColor Yellow
Write-Host "  1. .env file created with secure secrets"
Write-Host "  2. Never commit .env to git (already in .gitignore)"
Write-Host "  3. Save Grafana password - you'll need it to login"
Write-Host "  4. Change ALLOWED_ORIGINS for production"
Write-Host "  5. Set ENVIRONMENT=production for production"

Write-Host "`nNext Steps:" -ForegroundColor Green
Write-Host "  1. Review .env file and adjust ALLOWED_ORIGINS if needed"
Write-Host "  2. Run: .\build-now.ps1"
Write-Host "  3. Access Grafana at http://localhost:3000 with credentials above"

Write-Host "`nReady to build!" -ForegroundColor Green
