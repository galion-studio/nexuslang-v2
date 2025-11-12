# PowerShell Encryption Setup Script for Project Nexus
# Generates encryption keys and sets up secure environment

Write-Host "Project Nexus - Encryption Setup" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Function to generate a secure random key
function Generate-Key {
    param([int]$Length)
    $bytes = New-Object byte[] $Length
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    $rng.GetBytes($bytes)
    return [System.BitConverter]::ToString($bytes).Replace("-", "").ToLower()
}

# Check if .env file exists
$envFile = "..\..\..\.env"
if (-not (Test-Path $envFile)) {
    Write-Host "WARNING: .env file not found. Creating from template..." -ForegroundColor Yellow
    if (Test-Path "..\..\..\env.template") {
        Copy-Item "..\..\..\env.template" $envFile
        Write-Host "SUCCESS: Created .env from template" -ForegroundColor Green
    } else {
        Write-Host "ERROR: env.template not found" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "Step 1: Generating encryption keys..." -ForegroundColor Cyan
Write-Host ""

# Generate keys
$ENCRYPTION_MASTER_KEY = Generate-Key 64
Write-Host "  Generated ENCRYPTION_MASTER_KEY (128 chars)" -ForegroundColor Green

$JWT_SECRET_KEY = Generate-Key 64
Write-Host "  Generated JWT_SECRET_KEY (128 chars)" -ForegroundColor Green

$POSTGRES_PASSWORD = Generate-Key 32
Write-Host "  Generated POSTGRES_PASSWORD (64 chars)" -ForegroundColor Green

$REDIS_PASSWORD = Generate-Key 32
Write-Host "  Generated REDIS_PASSWORD (64 chars)" -ForegroundColor Green

$SESSION_SECRET = Generate-Key 32
Write-Host "  Generated SESSION_SECRET (64 chars)" -ForegroundColor Green

Write-Host ""
Write-Host "Step 2: Updating .env file..." -ForegroundColor Cyan
Write-Host ""

# Backup existing .env
if (Test-Path $envFile) {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    Copy-Item $envFile "$envFile.backup.$timestamp"
    Write-Host "  Backed up existing .env" -ForegroundColor Green
}

# Read current .env content
$envContent = Get-Content $envFile -Raw -ErrorAction SilentlyContinue
if (-not $envContent) {
    $envContent = ""
}

# Function to update or add environment variable
function Update-EnvVar {
    param($Content, $Key, $Value)
    if ($Content -match "(?m)^$Key=.*$") {
        return $Content -replace "(?m)^$Key=.*$", "$Key=$Value"
    } else {
        if ($Content) {
            return $Content + "`n$Key=$Value"
        } else {
            return "$Key=$Value"
        }
    }
}

# Update all secrets
$envContent = Update-EnvVar $envContent "ENCRYPTION_MASTER_KEY" $ENCRYPTION_MASTER_KEY
$envContent = Update-EnvVar $envContent "JWT_SECRET_KEY" $JWT_SECRET_KEY
$envContent = Update-EnvVar $envContent "POSTGRES_PASSWORD" $POSTGRES_PASSWORD
$envContent = Update-EnvVar $envContent "REDIS_PASSWORD" $REDIS_PASSWORD
$envContent = Update-EnvVar $envContent "SESSION_SECRET" $SESSION_SECRET
$envContent = Update-EnvVar $envContent "ENCRYPTION_KEY_VERSION" "v1"

# Write updated content
$envContent | Set-Content $envFile -NoNewline

Write-Host "  Updated .env file with new secrets" -ForegroundColor Green
Write-Host ""

# Create secrets backup
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFile = "secrets.$timestamp.txt"

$backupContent = @"
Project Nexus - Secrets Backup
Generated: $(Get-Date)
================================

ENCRYPTION_MASTER_KEY=$ENCRYPTION_MASTER_KEY
JWT_SECRET_KEY=$JWT_SECRET_KEY
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
REDIS_PASSWORD=$REDIS_PASSWORD
SESSION_SECRET=$SESSION_SECRET

WARNING: KEEP THIS FILE SECURE!
Store in a password manager or encrypted location.
DO NOT commit to version control.
"@

$backupContent | Set-Content $backupFile

Write-Host "Step 3: Creating secrets backup..." -ForegroundColor Cyan
Write-Host "  Created backup: $backupFile" -ForegroundColor Green
Write-Host ""

# Display summary
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "SUCCESS: Encryption Setup Complete!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Generated secrets:"
Write-Host "  - ENCRYPTION_MASTER_KEY (128 chars)"
Write-Host "  - JWT_SECRET_KEY (128 chars)"
Write-Host "  - POSTGRES_PASSWORD (64 chars)"
Write-Host "  - REDIS_PASSWORD (64 chars)"
Write-Host "  - SESSION_SECRET (64 chars)"
Write-Host ""
Write-Host "Files updated:"
Write-Host "  - .env (with new secrets)"
Write-Host "  - $backupFile (backup copy)"
Write-Host ""
Write-Host "IMPORTANT SECURITY NOTES:" -ForegroundColor Yellow
Write-Host "  1. Keep $backupFile in a secure location"
Write-Host "  2. Add it to your password manager"
Write-Host "  3. DO NOT commit secrets to Git"
Write-Host "  4. Rotate keys every 90 days"
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Green
Write-Host "  1. Store backup file securely"
Write-Host "  2. Delete backup: Remove-Item $backupFile"
Write-Host "  3. Test encryption: cd ..\..\backend; python -m core.encryption"
Write-Host "  4. Start services: docker-compose up -d"
Write-Host ""
