# GALION.APP DEPLOYMENT GUIDE

**Complete Step-by-Step Implementation Guide**

**Date:** November 9, 2025  
**Status:** Ready to Deploy

---

## 🎯 OVERVIEW

This guide walks you through deploying the complete GALION.APP infrastructure and services to AWS.

**What You'll Deploy:**
- AWS Infrastructure (VPC, ECS, RDS, Redis, S3)
- Voice Service (Faster-Whisper, XTTS, Llama 3.1 8B)
- RAG Service (pgvector, embeddings)
- Security (2FA, KMS, TLS 1.3)
- Data Lake (S3, Glue, Athena)
- ML Evaluation Harness

**Timeline:** 2-3 hours  
**Cost:** ~$590/month

---

## 📋 PREREQUISITES

### 1. Install Required Tools

```powershell
# Install Terraform
winget install HashiCorp.Terraform

# Install AWS CLI
winget install Amazon.AWSCLI

# Install Docker Desktop
winget install Docker.DockerDesktop

# Install Git
winget install Git.Git

# Verify installations
terraform version
aws --version
docker --version
git --version
```

### 2. Configure AWS

```powershell
# Configure AWS credentials
aws configure
# Enter: Access Key, Secret Key, Region (us-east-1), Output (json)

# Verify
aws sts get-caller-identity
```

### 3. Get API Keys (Optional for Alpha)

- OpenAI: https://platform.openai.com/api-keys
- ElevenLabs: https://elevenlabs.io/
- OpenRouter: https://openrouter.ai/

---

## 🚀 PHASE 1: INFRASTRUCTURE (30 minutes)

### Step 1: Create S3 Backend

```powershell
# Create S3 bucket for Terraform state
aws s3api create-bucket `
  --bucket galion-terraform-state `
  --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning `
  --bucket galion-terraform-state `
  --versioning-configuration Status=Enabled

# Create DynamoDB table for locking
aws dynamodb create-table `
  --table-name galion-terraform-locks `
  --attribute-definitions AttributeName=LockID,AttributeType=S `
  --key-schema AttributeName=LockID,KeyType=HASH `
  --billing-mode PAY_PER_REQUEST `
  --region us-east-1
```

### Step 2: Request ACM Certificate

```powershell
# Request certificate
aws acm request-certificate `
  --domain-name "*.galion.app" `
  --subject-alternative-names "galion.app" `
  --validation-method DNS `
  --region us-east-1

# Note the CertificateArn
# Add DNS validation records in Cloudflare
# Wait for certificate to be issued (5-30 minutes)
```

### Step 3: Configure Terraform

```powershell
cd infrastructure/terraform/environments/alpha

# Copy example variables
cp terraform.tfvars.example terraform.tfvars

# Generate secrets
$dbPassword = openssl rand -base64 32
$redisToken = openssl rand -base64 32
$jwtSecret = openssl rand -base64 64

# Edit terraform.tfvars
notepad terraform.tfvars
# Fill in: db_password, redis_auth_token, jwt_secret, security_alert_email, acm_certificate_arn
```

### Step 4: Deploy Infrastructure

```powershell
# Run deployment script
..\..\..\deploy-alpha.ps1 -All

# Or manually:
terraform init
terraform plan -out=tfplan
terraform apply tfplan
```

**Expected time:** 15-20 minutes  
**Result:** VPC, ECS, RDS, Redis, S3, KMS, GuardDuty all deployed

### Step 5: Configure DNS

```powershell
# Get ALB DNS name
$alb_dns = terraform output -raw alb_dns_name

# In Cloudflare:
# Add CNAME: galion.app → $alb_dns
# Enable proxy (orange cloud)
```

### Step 6: Enable pgvector

```powershell
# Get RDS endpoint
$rds_endpoint = terraform output -raw rds_endpoint

# Connect
psql -h $rds_endpoint -U galionadmin -d galionapp

# Enable extension
CREATE EXTENSION IF NOT EXISTS vector;
\dx
\q
```

---

## 🎤 PHASE 2: VOICE SERVICE (45 minutes)

### Step 1: Build Docker Image

```powershell
cd services/voice-service

# Build production image
docker build -f Dockerfile.production -t galion/voice-service:latest .

# Test locally (requires GPU)
docker run --gpus all -p 8003:8003 galion/voice-service:latest
```

### Step 2: Push to ECR

```powershell
# Get ECR login
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Create repository
aws ecr create-repository --repository-name galion/voice-service --region us-east-1

# Tag and push
docker tag galion/voice-service:latest ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/galion/voice-service:latest
docker push ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/galion/voice-service:latest
```

### Step 3: Create ECS Task Definition

See `infrastructure/ecs/voice-service-task-definition.json`

```powershell
# Register task definition
aws ecs register-task-definition --cli-input-json file://infrastructure/ecs/voice-service-task-definition.json
```

### Step 4: Create ECS Service

```powershell
# Create service
aws ecs create-service `
  --cluster galion-app-cluster `
  --service-name voice-service `
  --task-definition voice-service:1 `
  --desired-count 1 `
  --launch-type EC2 `
  --placement-constraints type=memberOf,expression="attribute:ecs.instance-type == g5.2xlarge"
```

### Step 5: Verify Deployment

```powershell
# Check service status
aws ecs describe-services --cluster galion-app-cluster --services voice-service

# Check task logs
aws logs tail /ecs/galion-app/voice-service --follow

# Test endpoint
curl https://galion.app/api/voice/health
```

---

## 📊 PHASE 3: RAG SERVICE (30 minutes)

### Step 1: Create ML Service

```powershell
cd services/ml-service

# Build image
docker build -t galion/ml-service:latest .

# Push to ECR
aws ecr create-repository --repository-name galion/ml-service
docker tag galion/ml-service:latest ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/galion/ml-service:latest
docker push ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/galion/ml-service:latest
```

### Step 2: Deploy RAG Service

```powershell
# Register task definition
aws ecs register-task-definition --cli-input-json file://infrastructure/ecs/ml-service-task-definition.json

# Create service
aws ecs create-service `
  --cluster galion-app-cluster `
  --service-name ml-service `
  --task-definition ml-service:1 `
  --desired-count 1 `
  --launch-type EC2
```

### Step 3: Ingest First Papers

```powershell
# Run ingestion script
python scripts/ingest-papers.py --source arxiv --domain physics --count 100
```

---

## 🔒 PHASE 4: SECURITY (15 minutes)

### Step 1: Implement 2FA

Already implemented in auth-service. Verify:

```powershell
# Test 2FA flow
curl -X POST https://galion.app/api/auth/register `
  -H "Content-Type: application/json" `
  -d '{"email":"test@example.com","password":"Test123!@#"}'

# Should return: "2FA setup required"
```

### Step 2: Verify TLS 1.3

```powershell
# Check TLS version
openssl s_client -connect galion.app:443 -tls1_3
```

### Step 3: Configure GuardDuty Alerts

Already configured via Terraform. Verify:

```powershell
# Check GuardDuty
aws guardduty list-detectors

# Check SNS topic
aws sns list-subscriptions
```

---

## 📈 PHASE 5: MONITORING (15 minutes)

### Step 1: Access Grafana

```powershell
# Get Grafana URL (if deployed)
# Or use CloudWatch dashboards

# Open CloudWatch
start https://console.aws.amazon.com/cloudwatch/
```

### Step 2: Set Up Alarms

```powershell
# Create high latency alarm
aws cloudwatch put-metric-alarm `
  --alarm-name voice-high-latency `
  --alarm-description "Voice P95 latency > 3s" `
  --metric-name P95Latency `
  --namespace GALION/Voice `
  --statistic Average `
  --period 300 `
  --threshold 3000 `
  --comparison-operator GreaterThanThreshold `
  --evaluation-periods 2
```

---

## ✅ PHASE 6: VERIFICATION (15 minutes)

### Step 1: Run Health Checks

```powershell
# Check all services
curl https://galion.app/health
curl https://galion.app/api/auth/health
curl https://galion.app/api/users/health
curl https://galion.app/api/voice/health
```

### Step 2: Test Voice Pipeline

```powershell
# Test STT
curl -X POST https://galion.app/api/voice/stt `
  -F "audio=@test.wav"

# Test TTS
curl -X POST https://galion.app/api/voice/tts `
  -H "Content-Type: application/json" `
  -d '{"text":"Hello from Nexus Core"}'
```

### Step 3: Test RAG

```powershell
# Test query
curl -X POST https://galion.app/api/ml/query `
  -H "Content-Type: application/json" `
  -d '{"query":"What is the speed of light?"}'
```

---

## 📊 COST MONITORING

### Daily Checks

```powershell
# Check current costs
aws ce get-cost-and-usage `
  --time-period Start=2025-11-01,End=2025-11-30 `
  --granularity DAILY `
  --metrics BlendedCost

# Check Spot instance savings
aws ec2 describe-spot-instance-requests
```

### Monthly Budget

```powershell
# Create budget alert
aws budgets create-budget `
  --account-id ACCOUNT_ID `
  --budget file://budget.json
```

---

## 🔧 TROUBLESHOOTING

### Issue: ECS Task Won't Start

```powershell
# Check task status
aws ecs describe-tasks --cluster galion-app-cluster --tasks TASK_ID

# Check logs
aws logs tail /ecs/galion-app/voice-service --follow

# Common fixes:
# 1. Check IAM permissions
# 2. Verify GPU availability
# 3. Check image exists in ECR
```

### Issue: High Costs

```powershell
# Scale down GPU instances
aws ecs update-service `
  --cluster galion-app-cluster `
  --service voice-service `
  --desired-count 0

# Or use Terraform
terraform apply -var="gpu_desired_capacity=0"
```

### Issue: Voice Latency > 3s

```powershell
# Check GPU utilization
nvidia-smi

# Check model quantization
# Ensure using int8 for Whisper and Llama

# Scale up GPU instances
terraform apply -var="gpu_desired_capacity=2"
```

---

## 📝 POST-DEPLOYMENT CHECKLIST

- [ ] Infrastructure deployed (VPC, ECS, RDS, Redis, S3)
- [ ] DNS configured (Cloudflare → ALB)
- [ ] SSL certificate issued and attached
- [ ] pgvector extension enabled
- [ ] Voice service deployed and healthy
- [ ] ML service deployed and healthy
- [ ] 2FA enabled and tested
- [ ] GuardDuty alerts configured
- [ ] CloudWatch alarms set up
- [ ] Cost monitoring enabled
- [ ] Backup strategy verified
- [ ] Documentation updated

---

## 🎉 SUCCESS!

Your GALION.APP infrastructure is now deployed and running!

**Next Steps:**
1. Invite beta testers
2. Monitor costs and performance
3. Collect user feedback
4. Iterate and improve

**Support:**
- Documentation: `docs/`
- Issues: GitHub Issues
- Email: devops@galion.app

---

**Built with First Principles**  
**Status:** Deployed  
**Let's ship it!** 🚀

