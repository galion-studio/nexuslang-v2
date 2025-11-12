# Deploy GALION.APP Alpha Infrastructure to AWS
# This script automates the Terraform deployment process

param(
    [switch]$Init,
    [switch]$Plan,
    [switch]$Apply,
    [switch]$Destroy,
    [switch]$Output,
    [switch]$All
)

$ErrorActionPreference = "Stop"

# Colors
function Write-Success { Write-Host $args -ForegroundColor Green }
function Write-Info { Write-Host $args -ForegroundColor Cyan }
function Write-Warning { Write-Host $args -ForegroundColor Yellow }
function Write-Error { Write-Host $args -ForegroundColor Red }

# Banner
Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                                                            ║" -ForegroundColor Cyan
Write-Host "║            GALION.APP Alpha Deployment                     ║" -ForegroundColor Cyan
Write-Host "║            Infrastructure as Code (Terraform)              ║" -ForegroundColor Cyan
Write-Host "║                                                            ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Change to alpha environment directory
$alphaDir = Join-Path $PSScriptRoot "environments/alpha"
if (-not (Test-Path $alphaDir)) {
    Write-Error "Alpha environment directory not found: $alphaDir"
    exit 1
}

Set-Location $alphaDir
Write-Info "Working directory: $alphaDir"
Write-Host ""

# Check prerequisites
Write-Info "Checking prerequisites..."

# Check Terraform
try {
    $tfVersion = terraform version -json | ConvertFrom-Json
    Write-Success "✓ Terraform installed: $($tfVersion.terraform_version)"
} catch {
    Write-Error "✗ Terraform not found. Install with: winget install HashiCorp.Terraform"
    exit 1
}

# Check AWS CLI
try {
    $awsVersion = aws --version 2>&1
    Write-Success "✓ AWS CLI installed: $awsVersion"
} catch {
    Write-Error "✗ AWS CLI not found. Install with: winget install Amazon.AWSCLI"
    exit 1
}

# Check AWS credentials
try {
    $identity = aws sts get-caller-identity | ConvertFrom-Json
    Write-Success "✓ AWS credentials configured: $($identity.Arn)"
} catch {
    Write-Error "✗ AWS credentials not configured. Run: aws configure"
    exit 1
}

# Check terraform.tfvars exists
if (-not (Test-Path "terraform.tfvars")) {
    Write-Warning "⚠ terraform.tfvars not found"
    Write-Info "Creating from terraform.tfvars.example..."
    Copy-Item "terraform.tfvars.example" "terraform.tfvars"
    Write-Warning "⚠ Please edit terraform.tfvars with your values before proceeding"
    Write-Info "Required: db_password, redis_auth_token, jwt_secret, security_alert_email, acm_certificate_arn"
    exit 1
}

Write-Host ""

# Initialize
if ($Init -or $All) {
    Write-Info "═══ Step 1: Initialize Terraform ═══"
    Write-Info "Downloading providers and setting up backend..."
    terraform init
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Terraform init failed"
        exit 1
    }
    Write-Success "✓ Terraform initialized"
    Write-Host ""
}

# Plan
if ($Plan -or $All) {
    Write-Info "═══ Step 2: Plan Infrastructure ═══"
    Write-Info "Previewing changes..."
    terraform plan -out=tfplan
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Terraform plan failed"
        exit 1
    }
    Write-Success "✓ Plan saved to tfplan"
    Write-Host ""
    
    Write-Warning "Review the plan above carefully before applying!"
    Write-Info "Estimated cost: ~$590/month"
    Write-Info "Deployment time: ~15-20 minutes"
    Write-Host ""
}

# Apply
if ($Apply -or $All) {
    Write-Info "═══ Step 3: Apply Infrastructure ═══"
    
    if (-not $All) {
        $confirm = Read-Host "Apply infrastructure changes? This will incur AWS costs. (yes/no)"
        if ($confirm -ne "yes") {
            Write-Warning "Deployment cancelled"
            exit 0
        }
    }
    
    Write-Info "Deploying infrastructure..."
    terraform apply tfplan
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Terraform apply failed"
        exit 1
    }
    Write-Success "✓ Infrastructure deployed"
    Write-Host ""
    
    # Show outputs
    Write-Info "═══ Deployment Outputs ═══"
    terraform output
    Write-Host ""
    
    Write-Success "╔════════════════════════════════════════════════════════════╗"
    Write-Success "║                                                            ║"
    Write-Success "║            Deployment Complete!                            ║"
    Write-Success "║                                                            ║"
    Write-Success "╚════════════════════════════════════════════════════════════╝"
    Write-Host ""
    
    Write-Info "Next steps:"
    Write-Info "1. Configure DNS in Cloudflare (point to ALB)"
    Write-Info "2. Enable pgvector extension in RDS"
    Write-Info "3. Deploy ECS services"
    Write-Host ""
}

# Destroy
if ($Destroy) {
    Write-Warning "═══ DESTROY Infrastructure ═══"
    Write-Warning "This will DELETE ALL resources and data!"
    Write-Host ""
    
    $confirm = Read-Host "Type 'DESTROY' to confirm"
    if ($confirm -ne "DESTROY") {
        Write-Warning "Destruction cancelled"
        exit 0
    }
    
    Write-Info "Destroying infrastructure..."
    terraform destroy
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Terraform destroy failed"
        exit 1
    }
    Write-Success "✓ Infrastructure destroyed"
    Write-Host ""
}

# Output
if ($Output) {
    Write-Info "═══ Infrastructure Outputs ═══"
    terraform output
    Write-Host ""
}

# Show usage if no flags
if (-not ($Init -or $Plan -or $Apply -or $Destroy -or $Output -or $All)) {
    Write-Info "Usage:"
    Write-Info "  .\deploy-alpha.ps1 -All          # Initialize, plan, and apply"
    Write-Info "  .\deploy-alpha.ps1 -Init         # Initialize Terraform"
    Write-Info "  .\deploy-alpha.ps1 -Plan         # Preview changes"
    Write-Info "  .\deploy-alpha.ps1 -Apply        # Apply changes"
    Write-Info "  .\deploy-alpha.ps1 -Output       # Show outputs"
    Write-Info "  .\deploy-alpha.ps1 -Destroy      # Destroy infrastructure"
    Write-Host ""
}

