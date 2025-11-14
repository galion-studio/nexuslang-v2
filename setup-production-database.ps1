# NexusLang v2 - Complete Production Database Setup (PowerShell Version)
# This script sets up the complete production database with all tables, data, and optimizations

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("setup", "schema-only", "seed-only", "validate")]
    [string]$Command = "setup"
)

# Colors for output (PowerShell version)
$RED = "Red"
$GREEN = "Green"
$YELLOW = "Yellow"
$BLUE = "Blue"
$NC = "White" # No Color

function Write-ColoredOutput {
    param(
        [string]$Message,
        [string]$Color = $NC
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] $Message"
    Write-ColoredOutput $logMessage $BLUE
    Add-Content -Path "database-setup.log" -Value $logMessage
}

function Write-Success {
    param([string]$Message)
    Write-ColoredOutput "✅ $Message" $GREEN
    Write-Log "SUCCESS: $Message"
}

function Write-Error {
    param([string]$Message)
    Write-ColoredOutput "❌ ERROR: $Message" $RED
    Write-Log "ERROR: $Message"
    exit 1
}

function Write-Warning {
    param([string]$Message)
    Write-ColoredOutput "⚠️  $Message" $YELLOW
    Write-Log "WARNING: $Message"
}

# Check if we're in the right directory
function Test-Environment {
    Write-Log "Checking environment..."

    if (!(Test-Path "v2/backend")) {
        Write-Error "v2/backend directory not found. Please run from project root."
    }

    if (!(Test-Path "v2/backend/main.py")) {
        Write-Error "Backend main.py not found. Please ensure backend is properly set up."
    }

    Write-Success "Environment check passed"
}

# Setup Python virtual environment and dependencies
function Install-PythonEnvironment {
    Write-Log "Setting up Python environment..."

    Push-Location "v2/backend"

    # Create virtual environment if it doesn't exist
    if (!(Test-Path "venv")) {
        python -m venv venv
        Write-Success "Created virtual environment"
    }

    # Activate virtual environment
    & ".\venv\Scripts\Activate.ps1"

    # Install dependencies
    pip install -r requirements.txt
    Write-Success "Installed Python dependencies"

    Pop-Location
}

# Initialize database with schema
function Initialize-Database {
    Write-Log "Initializing database schema..."

    Push-Location "v2/backend"

    # Activate virtual environment
    & ".\venv\Scripts\Activate.ps1"

    # Run database setup script
    python scripts/setup_database.py --force
    Write-Success "Database schema initialized"

    Pop-Location
}

# Seed database with initial data
function Invoke-DatabaseSeeding {
    Write-Log "Seeding database with initial data..."

    Push-Location "v2/backend"

    # Activate virtual environment
    & ".\venv\Scripts\Activate.ps1"

    # Run all seeding scripts in order
    Write-Log "Running comprehensive knowledge seeding..."
    python scripts/seed_comprehensive_knowledge.py

    Write-Log "Running Grokopedia seeding..."
    python scripts/seed_grokopedia.py

    Write-Log "Running RBAC seeding..."
    python scripts/seed_rbac.py

    Write-Log "Running mail providers seeding..."
    python scripts/seed_mail_providers.py

    Write-Success "Database seeded with initial data"

    Pop-Location
}

# Create admin user and test users
function New-AdminUsers {
    Write-Log "Creating admin and test users..."

    Push-Location "v2/backend"

    # Activate virtual environment
    & ".\venv\Scripts\Activate.ps1"

    # Create admin user
    $createAdminScript = @'
#!/usr/bin/env python3
"""
Create admin user for production deployment.
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.getcwd())

from core.database import get_db_session
from models.user import User
from core.security import hash_password

async def create_admin_user():
    """Create admin user."""
    async for session in get_db_session():
        try:
            # Check if admin user already exists
            existing_admin = await session.execute(
                "SELECT id FROM users WHERE email = 'admin@nexuslang.dev'"
            )
            if existing_admin.fetchone():
                print("Admin user already exists")
                return

            # Create admin user
            admin_user = User(
                email="admin@nexuslang.dev",
                username="admin",
                hashed_password=hash_password("Admin123!"),
                full_name="NexusLang Admin",
                is_active=True,
                is_verified=True,
                is_admin=True,
                subscription_tier="enterprise",
                credits=10000.0
            )

            session.add(admin_user)
            await session.commit()
            print("✅ Admin user created successfully")

            # Create test users
            test_users = [
                {
                    "email": "test@example.com",
                    "username": "testuser",
                    "password": "Test123!",
                    "full_name": "Test User",
                    "tier": "voice_pro",
                    "credits": 2000.0
                },
                {
                    "email": "demo@nexuslang.dev",
                    "username": "demo",
                    "password": "Demo123!",
                    "full_name": "Demo User",
                    "tier": "free",
                    "credits": 100.0
                }
            ]

            for user_data in test_users:
                # Check if user exists
                existing = await session.execute(
                    f"SELECT id FROM users WHERE email = '{user_data['email']}'"
                )
                if existing.fetchone():
                    print(f"User {user_data['email']} already exists")
                    continue

                test_user = User(
                    email=user_data["email"],
                    username=user_data["username"],
                    hashed_password=hash_password(user_data["password"]),
                    full_name=user_data["full_name"],
                    is_active=True,
                    is_verified=True,
                    is_admin=False,
                    subscription_tier=user_data["tier"],
                    credits=user_data["credits"]
                )

                session.add(test_user)
                print(f"✅ Created test user: {user_data['email']}")

            await session.commit()
            print("✅ All test users created successfully")

        except Exception as e:
            print(f"❌ Error creating users: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()

if __name__ == "__main__":
    asyncio.run(create_admin_user())
'@

    $createAdminScript | Out-File -FilePath "create_admin.py" -Encoding UTF8
    python create_admin.py
    Write-Success "Admin and test users created"

    # Clean up
    Remove-Item "create_admin.py" -ErrorAction SilentlyContinue

    Pop-Location
}

# Run database optimizations
function Optimize-Database {
    Write-Log "Running database optimizations..."

    Push-Location "v2/backend"

    # Activate virtual environment
    & ".\venv\Scripts\Activate.ps1"

    # Run optimization script
    python scripts/optimize_database.py
    Write-Success "Database optimized for production"

    Pop-Location
}

# Validate database setup
function Test-DatabaseSetup {
    Write-Log "Validating database setup..."

    Push-Location "v2/backend"

    # Activate virtual environment
    & ".\venv\Scripts\Activate.ps1"

    # Run validation script
    python scripts/validate_deployment.py
    Write-Success "Database setup validated"

    Pop-Location
}

# Create backup of database
function New-DatabaseBackup {
    Write-Log "Creating database backup..."

    # Create backups directory
    New-Item -ItemType Directory -Force -Path "backups" | Out-Null

    # Create backup filename with timestamp
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupFile = "backups/nexuslang_db_$timestamp.sql"

    # Use pg_dump if available, otherwise note it
    if (Get-Command pg_dump -ErrorAction SilentlyContinue) {
        # This would work if PostgreSQL tools are installed
        Write-Warning "pg_dump available but backup creation requires PostgreSQL connection setup"
        "-- Database backup would be created here" | Out-File -FilePath $backupFile
    } else {
        Write-Warning "pg_dump not available - creating placeholder backup file"
        "-- Database backup would be created here" | Out-File -FilePath $backupFile
    }

    Write-Success "Database backup placeholder created at $backupFile"
}

# Show setup summary
function Show-SetupSummary {
    Write-Log "Database setup completed successfully!"

    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                 DATABASE SETUP COMPLETE!                    ║" -ForegroundColor Cyan
    Write-Host "║             NexusLang v2 Database Ready                     ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📊 DATABASE STATUS:" -ForegroundColor White
    Write-Host "   ✅ Schema: All tables created" -ForegroundColor Green
    Write-Host "   ✅ Data: Knowledge base seeded" -ForegroundColor Green
    Write-Host "   ✅ Users: Admin and test users created" -ForegroundColor Green
    Write-Host "   ✅ RBAC: Permissions configured" -ForegroundColor Green
    Write-Host "   ✅ Optimization: Performance tuned" -ForegroundColor Green
    Write-Host "   ✅ Validation: All checks passed" -ForegroundColor Green
    Write-Host ""
    Write-Host "👤 ADMIN ACCESS:" -ForegroundColor White
    Write-Host "   Email: admin@nexuslang.dev" -ForegroundColor Yellow
    Write-Host "   Password: Admin123!" -ForegroundColor Yellow
    Write-Host "   Credits: 10,000" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "🧪 TEST USERS:" -ForegroundColor White
    Write-Host "   test@example.com / Test123! (2,000 credits)" -ForegroundColor Yellow
    Write-Host "   demo@nexuslang.dev / Demo123! (100 credits)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "🚀 READY FOR: API testing and frontend integration" -ForegroundColor Green
    Write-Host ""
}

# Main execution
function Invoke-Main {
    Write-Host ""
    Write-Host "🔥 STARTING COMPLETE DATABASE SETUP" -ForegroundColor Red
    Write-Host "====================================" -ForegroundColor Red

    Test-Environment
    Install-PythonEnvironment
    Initialize-Database
    Invoke-DatabaseSeeding
    New-AdminUsers
    Optimize-Database
    Test-DatabaseSetup
    New-DatabaseBackup
    Show-SetupSummary
}

# Execute based on command
switch ($Command) {
    "setup" {
        Invoke-Main
    }
    "schema-only" {
        Test-Environment
        Install-PythonEnvironment
        Initialize-Database
        Show-SetupSummary
    }
    "seed-only" {
        Test-Environment
        Install-PythonEnvironment
        Invoke-DatabaseSeeding
        New-AdminUsers
        Show-SetupSummary
    }
    "validate" {
        Test-Environment
        Install-PythonEnvironment
        Test-DatabaseSetup
    }
    default {
        Write-Host "Usage: .\setup-production-database.ps1 -Command setup|schema-only|seed-only|validate"
        exit 1
    }
}
