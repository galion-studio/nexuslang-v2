# Run Database Migrations for Document Verification and Permissions
# PowerShell script to apply database migrations

param(
    [switch]$Force
)

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  DATABASE MIGRATIONS                            " -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Load environment variables
if (Test-Path ".env") {
    Get-Content .env | ForEach-Object {
        if ($_ -match '^([^#][^=]+)=(.*)$') {
            [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2])
        }
    }
}

$POSTGRES_USER = $env:POSTGRES_USER
$POSTGRES_DB = $env:POSTGRES_DB

if (-not $POSTGRES_USER -or -not $POSTGRES_DB) {
    Write-Host "ERROR: Environment variables not set!" -ForegroundColor Red
    Write-Host "Please ensure .env file exists and contains POSTGRES_USER and POSTGRES_DB" -ForegroundColor Yellow
    exit 1
}

# Check if PostgreSQL is running
Write-Host "Checking PostgreSQL status..." -ForegroundColor Yellow
$postgresRunning = docker ps --filter "name=nexus-postgres" --filter "status=running" --format "{{.Names}}"

if (-not $postgresRunning) {
    Write-Host "ERROR: PostgreSQL container is not running!" -ForegroundColor Red
    Write-Host "Start it with: docker-compose up -d postgres" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ PostgreSQL is running" -ForegroundColor Green
Write-Host ""

# List available migrations
Write-Host "Available migrations:" -ForegroundColor Yellow
$migrations = Get-ChildItem -Path "database/migrations" -Filter "*.sql" | Sort-Object Name
foreach ($migration in $migrations) {
    Write-Host "  - $($migration.Name)" -ForegroundColor Gray
}
Write-Host ""

# Confirm before running
if (-not $Force) {
    Write-Host "This will run the following migrations:" -ForegroundColor Yellow
    Write-Host "  1. 005_document_verification.sql - Document verification tables" -ForegroundColor White
    Write-Host "  2. 006_custom_permissions.sql - RBAC permissions system" -ForegroundColor White
    Write-Host ""
    
    $confirm = Read-Host "Continue? (y/n)"
    if ($confirm -ne 'y') {
        Write-Host "Migration cancelled." -ForegroundColor Yellow
        exit 0
    }
}

Write-Host ""
Write-Host "Running migrations..." -ForegroundColor Yellow
Write-Host ""

# Run migration 005
Write-Host "[1/2] Applying 005_document_verification.sql..." -ForegroundColor Cyan
try {
    Get-Content "database/migrations/005_document_verification.sql" | docker exec -i nexus-postgres psql -U $POSTGRES_USER -d $POSTGRES_DB
    Write-Host "✓ Document verification migration applied" -ForegroundColor Green
} catch {
    Write-Host "✗ Migration failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Run migration 006
Write-Host "[2/2] Applying 006_custom_permissions.sql..." -ForegroundColor Cyan
try {
    Get-Content "database/migrations/006_custom_permissions.sql" | docker exec -i nexus-postgres psql -U $POSTGRES_USER -d $POSTGRES_DB
    Write-Host "✓ Permissions system migration applied" -ForegroundColor Green
} catch {
    Write-Host "✗ Migration failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  MIGRATIONS COMPLETE!                           " -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Verify tables created
Write-Host "Verifying tables..." -ForegroundColor Yellow
$verifyQuery = @"
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_name IN ('documents', 'document_types', 'roles', 'permissions', 'role_permissions', 'user_roles')
ORDER BY table_name;
"@

Write-Host "Tables created:" -ForegroundColor Green
echo $verifyQuery | docker exec -i nexus-postgres psql -U $POSTGRES_USER -d $POSTGRES_DB -t

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Deploy services: .\scripts\deploy-document-verification.ps1" -ForegroundColor White
Write-Host "  2. Run tests: .\scripts\test-documents.ps1" -ForegroundColor White
Write-Host ""

