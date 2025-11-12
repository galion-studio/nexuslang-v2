# GALION.APP Terraform Infrastructure

**Infrastructure as Code for AWS Alpha Environment**

---

## Overview

This directory contains Terraform configurations to provision the complete GALION.APP infrastructure on AWS, including:

- VPC with public/private subnets across 2 AZs
- ECS cluster with general and GPU capacity providers
- RDS Postgres with pgvector extension
- ElastiCache Redis
- S3 buckets with lifecycle policies
- KMS encryption
- Secrets Manager
- GuardDuty and Security Hub
- Application Load Balancer
- CloudWatch logging and monitoring

---

## Prerequisites

### 1. Install Tools

```powershell
# Install Terraform
winget install HashiCorp.Terraform

# Install AWS CLI
winget install Amazon.AWSCLI

# Verify installations
terraform version  # Should be >= 1.6.0
aws --version
```

### 2. Configure AWS Credentials

```powershell
# Configure AWS CLI
aws configure

# Enter your credentials:
# AWS Access Key ID: YOUR_ACCESS_KEY
# AWS Secret Access Key: YOUR_SECRET_KEY
# Default region: us-east-1
# Default output format: json
```

### 3. Create S3 Backend (One-Time Setup)

```powershell
# Create S3 bucket for Terraform state
aws s3api create-bucket `
  --bucket galion-terraform-state `
  --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning `
  --bucket galion-terraform-state `
  --versioning-configuration Status=Enabled

# Enable encryption
aws s3api put-bucket-encryption `
  --bucket galion-terraform-state `
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'

# Create DynamoDB table for state locking
aws dynamodb create-table `
  --table-name galion-terraform-locks `
  --attribute-definitions AttributeName=LockID,AttributeType=S `
  --key-schema AttributeName=LockID,KeyType=HASH `
  --billing-mode PAY_PER_REQUEST `
  --region us-east-1
```

### 4. Create ACM Certificate (One-Time Setup)

```powershell
# Request certificate for *.galion.app
aws acm request-certificate `
  --domain-name "*.galion.app" `
  --subject-alternative-names "galion.app" `
  --validation-method DNS `
  --region us-east-1

# Note the CertificateArn from output
# Add DNS validation records in Cloudflare
# Wait for certificate to be issued (5-30 minutes)
```

---

## Directory Structure

```
infrastructure/terraform/
├── modules/
│   ├── networking/       # VPC, subnets, security groups
│   ├── compute/          # ECS, EC2, auto scaling
│   ├── data/             # RDS, Redis, S3
│   └── security/         # KMS, Secrets Manager, GuardDuty
├── environments/
│   └── alpha/
│       ├── main.tf                    # Main configuration
│       ├── variables.tf               # Variable definitions
│       ├── outputs.tf                 # Output definitions
│       ├── terraform.tfvars.example   # Example variables
│       └── terraform.tfvars           # Your variables (DO NOT COMMIT)
└── README.md (this file)
```

---

## Deployment Steps

### Step 1: Configure Variables

```powershell
cd infrastructure/terraform/environments/alpha

# Copy example variables
cp terraform.tfvars.example terraform.tfvars

# Edit terraform.tfvars with your values
notepad terraform.tfvars
```

**Important:** Generate strong secrets:

```powershell
# Generate database password
openssl rand -base64 32

# Generate Redis auth token
openssl rand -base64 32

# Generate JWT secret
openssl rand -base64 64
```

### Step 2: Initialize Terraform

```powershell
# Initialize Terraform (downloads providers, sets up backend)
terraform init
```

### Step 3: Plan Infrastructure

```powershell
# Preview changes
terraform plan

# Save plan to file
terraform plan -out=tfplan
```

### Step 4: Apply Infrastructure

```powershell
# Apply changes (will prompt for confirmation)
terraform apply

# Or apply saved plan
terraform apply tfplan
```

**Expected time:** 15-20 minutes

**Expected cost:** ~$590/month (with Spot instances)

### Step 5: Verify Deployment

```powershell
# Get outputs
terraform output

# Test ALB
$alb_dns = terraform output -raw alb_dns_name
curl "http://$alb_dns/health"
```

---

## Post-Deployment

### 1. Configure DNS (Cloudflare)

```powershell
# Get ALB DNS name
$alb_dns = terraform output -raw alb_dns_name
$alb_zone_id = terraform output -raw alb_zone_id

# Add CNAME record in Cloudflare:
# Type: CNAME
# Name: galion.app
# Target: $alb_dns
# Proxy: Yes (orange cloud)
```

### 2. Enable pgvector Extension

```powershell
# Get RDS endpoint
$rds_endpoint = terraform output -raw rds_endpoint

# Connect to database
psql -h $rds_endpoint -U galionadmin -d galionapp

# Enable pgvector
CREATE EXTENSION IF NOT EXISTS vector;

# Verify
\dx
```

### 3. Deploy ECS Services

See `services/*/README.md` for service-specific deployment instructions.

---

## Cost Breakdown

### Alpha Environment (~$590/month)

| Resource | Type | Quantity | Monthly Cost |
|----------|------|----------|--------------|
| EC2 (General) | m7i.large (Spot) | 2 | $44 |
| EC2 (GPU) | g5.2xlarge (Spot) | 1 | $292 |
| RDS | db.t4g.medium | 1 | $60 |
| ElastiCache | cache.t4g.small | 1 | $30 |
| S3 | 100 GB | - | $2 |
| NAT Gateway | - | 1 | $33 |
| ALB | - | 1 | $16 |
| Data Transfer | 100 GB/month | - | $9 |
| CloudWatch | Logs + Metrics | - | $36 |
| GuardDuty | - | - | $5 |
| KMS | 2 keys | - | $2 |
| Secrets Manager | 10 secrets | - | $4 |
| **Total** | | | **~$533** |

**With 10% buffer:** ~$590/month

---

## Scaling

### Scale Up (More Capacity)

```powershell
# Edit terraform.tfvars
# Increase desired_capacity values

# Apply changes
terraform apply
```

### Scale Down (Reduce Costs)

```powershell
# Edit terraform.tfvars
# Decrease desired_capacity values

# Apply changes
terraform apply
```

### Auto-Scaling

ECS Capacity Providers automatically scale instances based on task demand.

**Targets:**
- General: 80% capacity utilization
- GPU: 90% capacity utilization

---

## Maintenance

### Update Infrastructure

```powershell
# Pull latest changes
git pull

# Review changes
terraform plan

# Apply updates
terraform apply
```

### Rotate Secrets

```powershell
# Generate new password
$new_password = openssl rand -base64 32

# Update in Secrets Manager
aws secretsmanager update-secret `
  --secret-id galion-app/alpha/db-password `
  --secret-string $new_password

# Update RDS password
aws rds modify-db-instance `
  --db-instance-identifier galion-app-postgres `
  --master-user-password $new_password `
  --apply-immediately
```

### Backup & Restore

**RDS Backups:**
- Automated daily snapshots (7-day retention)
- Manual snapshots: `aws rds create-db-snapshot`

**S3 Backups:**
- Versioning enabled (90-day retention)
- Lifecycle policies move old data to Glacier

**Terraform State:**
- Stored in S3 with versioning
- Locked with DynamoDB

---

## Troubleshooting

### Issue: Terraform Init Fails

**Solution:**
```powershell
# Check AWS credentials
aws sts get-caller-identity

# Check S3 backend bucket exists
aws s3 ls s3://galion-terraform-state

# Check DynamoDB table exists
aws dynamodb describe-table --table-name galion-terraform-locks
```

### Issue: Apply Fails with "Insufficient Capacity"

**Solution:**
```powershell
# GPU instances may not be available in all AZs
# Edit terraform.tfvars to use different AZ
# Or use On-Demand instead of Spot
```

### Issue: RDS Connection Timeout

**Solution:**
```powershell
# Check security group allows connection from ECS
# Verify RDS is in private subnet
# Check VPC routing tables
```

### Issue: High Costs

**Solution:**
```powershell
# Check Spot instance usage
aws ec2 describe-instances --filters "Name=instance-lifecycle,Values=spot"

# Review CloudWatch costs
aws ce get-cost-and-usage --time-period Start=2025-11-01,End=2025-11-30 --granularity MONTHLY --metrics BlendedCost

# Scale down if needed
terraform apply -var="gpu_desired_capacity=0"
```

---

## Destroy Infrastructure

**WARNING:** This will delete ALL resources and data!

```powershell
# Destroy infrastructure
terraform destroy

# Confirm by typing: yes

# Manually delete S3 buckets (if needed)
aws s3 rb s3://galion-app-data-us --force
aws s3 rb s3://galion-app-model-artifacts --force
aws s3 rb s3://galion-app-static --force
aws s3 rb s3://galion-app-logs --force
```

---

## Security Best Practices

1. **Never commit terraform.tfvars** - Add to .gitignore
2. **Use strong secrets** - Generate with `openssl rand -base64 32`
3. **Rotate secrets regularly** - Every 90 days
4. **Enable MFA** - On AWS root account
5. **Use IAM roles** - Not access keys for EC2
6. **Enable CloudTrail** - Audit all API calls
7. **Review Security Hub** - Weekly
8. **Monitor GuardDuty** - Daily
9. **Backup regularly** - Test restores monthly
10. **Least privilege** - Grant minimum permissions

---

## Support

**Issues:**
- GitHub: https://github.com/galion-app/infrastructure/issues
- Email: devops@galion.app

**Documentation:**
- AWS: https://docs.aws.amazon.com/
- Terraform: https://www.terraform.io/docs

---

**Built with First Principles**  
**Status:** Ready to Deploy  
**Let's provision AWS.** ☁️

