# GALION.APP AWS Deployment Plan ⭐ DEPLOY NOW
## Complete Production Deployment Guide

**Version:** 1.0  
**Last Updated:** November 2025  
**Timeline:** 4 weeks to production  
**Budget:** $1,480/month ($1,000 infrastructure + $480 APIs)  
**Target:** 500 MAU, 100 DAU, 5K voice minutes/month

---

## 🎯 Executive Summary

This document provides a complete, production-ready deployment plan for GALION.APP on AWS. It includes:

- Complete AWS architecture (VPC, ECS, RDS, ElastiCache, S3)
- Voice-to-voice implementation (Whisper API + ElevenLabs)
- 4-week deployment timeline with milestones
- Detailed cost breakdown
- Code examples (Go backend, Node.js voice service, React frontend)
- Security configuration (IAM, Security Groups, encryption)
- GDPR + CCPA compliance checklist
- 90-day scale plan

**You can start deploying TODAY and be live in 4 weeks.**

---

## 🏗️ AWS Architecture

### High-Level Overview

```
Internet
    ↓
CloudFront (CDN)
    ↓
Application Load Balancer (ALB)
    ↓
ECS Fargate Cluster
    ├─ API Gateway (Go)
    ├─ Auth Service (Python)
    ├─ User Service (Python)
    ├─ Voice Service (Node.js)
    └─ Analytics Service (Go)
    ↓
RDS PostgreSQL (Multi-AZ)
ElastiCache Redis (Cluster Mode)
S3 Buckets (Assets, Backups, Logs)
```

### Detailed Components

#### 1. Networking Layer (VPC)

**VPC Configuration:**
```yaml
CIDR Block: 10.0.0.0/16
Availability Zones: 3 (us-east-1a, us-east-1b, us-east-1c)

Public Subnets:
  - 10.0.1.0/24 (AZ-1)
  - 10.0.2.0/24 (AZ-2)
  - 10.0.3.0/24 (AZ-3)

Private Subnets:
  - 10.0.11.0/24 (AZ-1)
  - 10.0.12.0/24 (AZ-2)
  - 10.0.13.0/24 (AZ-3)

Database Subnets:
  - 10.0.21.0/24 (AZ-1)
  - 10.0.22.0/24 (AZ-2)
  - 10.0.23.0/24 (AZ-3)
```

**Terraform Configuration:**
```hcl
# infrastructure/terraform/vpc.tf

resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "galion-vpc"
    Environment = "production"
  }
}

resource "aws_subnet" "public" {
  count                   = 3
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.${count.index + 1}.0/24"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name = "galion-public-${count.index + 1}"
  }
}

resource "aws_subnet" "private" {
  count             = 3
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${count.index + 11}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = "galion-private-${count.index + 1}"
  }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "galion-igw"
  }
}

resource "aws_nat_gateway" "main" {
  count         = 3
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id

  tags = {
    Name = "galion-nat-${count.index + 1}"
  }
}

resource "aws_eip" "nat" {
  count  = 3
  domain = "vpc"

  tags = {
    Name = "galion-nat-eip-${count.index + 1}"
  }
}
```

#### 2. Compute Layer (ECS Fargate)

**ECS Cluster:**
```hcl
# infrastructure/terraform/ecs.tf

resource "aws_ecs_cluster" "main" {
  name = "galion-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Name        = "galion-cluster"
    Environment = "production"
  }
}

resource "aws_ecs_task_definition" "api_gateway" {
  family                   = "api-gateway"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([{
    name      = "api-gateway"
    image     = "${aws_ecr_repository.api_gateway.repository_url}:latest"
    essential = true

    portMappings = [{
      containerPort = 8080
      protocol      = "tcp"
    }]

    environment = [
      {
        name  = "ENVIRONMENT"
        value = "production"
      },
      {
        name  = "PORT"
        value = "8080"
      }
    ]

    secrets = [
      {
        name      = "DATABASE_URL"
        valueFrom = aws_secretsmanager_secret.db_url.arn
      },
      {
        name      = "REDIS_URL"
        valueFrom = aws_secretsmanager_secret.redis_url.arn
      }
    ]

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.api_gateway.name
        "awslogs-region"        = var.aws_region
        "awslogs-stream-prefix" = "ecs"
      }
    }

    healthCheck = {
      command     = ["CMD-SHELL", "curl -f http://localhost:8080/health || exit 1"]
      interval    = 30
      timeout     = 5
      retries     = 3
      startPeriod = 60
    }
  }])
}

resource "aws_ecs_service" "api_gateway" {
  name            = "api-gateway"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.api_gateway.arn
  desired_count   = 2
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.api_gateway.arn
    container_name   = "api-gateway"
    container_port   = 8080
  }

  deployment_configuration {
    maximum_percent         = 200
    minimum_healthy_percent = 100
  }

  depends_on = [aws_lb_listener.https]
}
```

**Service Specifications:**

| Service | CPU | Memory | Replicas | Cost/month |
|---------|-----|--------|----------|------------|
| API Gateway (Go) | 256 | 512 MB | 2 | $30 |
| Auth Service (Python) | 256 | 512 MB | 2 | $30 |
| User Service (Python) | 256 | 512 MB | 2 | $30 |
| Voice Service (Node.js) | 512 | 1024 MB | 2 | $60 |
| Analytics Service (Go) | 256 | 512 MB | 1 | $15 |
| **Total** | | | **9** | **$165** |

#### 3. Database Layer (RDS PostgreSQL)

**RDS Configuration:**
```hcl
# infrastructure/terraform/rds.tf

resource "aws_db_subnet_group" "main" {
  name       = "galion-db-subnet"
  subnet_ids = aws_subnet.private[*].id

  tags = {
    Name = "galion-db-subnet"
  }
}

resource "aws_db_instance" "postgres" {
  identifier     = "galion-postgres"
  engine         = "postgres"
  engine_version = "15.4"
  instance_class = "db.t4g.micro"

  allocated_storage     = 20
  max_allocated_storage = 100
  storage_type          = "gp3"
  storage_encrypted     = true

  db_name  = "galion"
  username = "galion_admin"
  password = random_password.db_password.result

  multi_az               = true
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]

  backup_retention_period = 7
  backup_window           = "03:00-04:00"
  maintenance_window      = "mon:04:00-mon:05:00"

  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]

  deletion_protection = true
  skip_final_snapshot = false
  final_snapshot_identifier = "galion-postgres-final-${formatdate("YYYYMMDD-hhmm", timestamp())}"

  tags = {
    Name        = "galion-postgres"
    Environment = "production"
  }
}

resource "random_password" "db_password" {
  length  = 32
  special = true
}

resource "aws_secretsmanager_secret" "db_password" {
  name = "galion/database/password"
}

resource "aws_secretsmanager_secret_version" "db_password" {
  secret_id     = aws_secretsmanager_secret.db_password.id
  secret_string = random_password.db_password.result
}
```

**Specs:**
- **Instance:** db.t4g.micro (2 vCPU, 1 GB RAM)
- **Storage:** 20 GB gp3 (auto-scales to 100 GB)
- **Multi-AZ:** Enabled (automatic failover)
- **Backups:** 7-day retention
- **Encryption:** AES-256 at rest
- **Cost:** $25/month

#### 4. Cache Layer (ElastiCache Redis)

```hcl
# infrastructure/terraform/elasticache.tf

resource "aws_elasticache_subnet_group" "main" {
  name       = "galion-cache-subnet"
  subnet_ids = aws_subnet.private[*].id
}

resource "aws_elasticache_replication_group" "redis" {
  replication_group_id       = "galion-redis"
  replication_group_description = "Redis cluster for session and cache"
  
  engine               = "redis"
  engine_version       = "7.0"
  node_type            = "cache.t4g.micro"
  num_cache_clusters   = 2
  port                 = 6379

  subnet_group_name    = aws_elasticache_subnet_group.main.name
  security_group_ids   = [aws_security_group.redis.id]

  automatic_failover_enabled = true
  multi_az_enabled           = true

  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  auth_token                 = random_password.redis_password.result

  snapshot_retention_limit = 5
  snapshot_window          = "03:00-05:00"

  tags = {
    Name        = "galion-redis"
    Environment = "production"
  }
}
```

**Specs:**
- **Instance:** cache.t4g.micro (2 vCPU, 0.5 GB RAM)
- **Replicas:** 2 (primary + read replica)
- **Multi-AZ:** Enabled
- **Encryption:** In-transit + at-rest
- **Cost:** $25/month

#### 5. Storage (S3)

```hcl
# infrastructure/terraform/s3.tf

resource "aws_s3_bucket" "assets" {
  bucket = "galion-assets-prod"

  tags = {
    Name        = "galion-assets"
    Environment = "production"
  }
}

resource "aws_s3_bucket_versioning" "assets" {
  bucket = aws_s3_bucket.assets.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_encryption" "assets" {
  bucket = aws_s3_bucket.assets.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "assets" {
  bucket = aws_s3_bucket.assets.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "assets" {
  bucket = aws_s3_bucket.assets.id

  rule {
    id     = "move-to-glacier"
    status = "Enabled"

    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    expiration {
      days = 365
    }
  }
}
```

**Buckets:**
- `galion-assets-prod`: User uploads, voice recordings
- `galion-backups-prod`: Database backups
- `galion-logs-prod`: Application logs
- **Cost:** $5/month (50 GB storage)

---

## 🎤 Voice-to-Voice Implementation

### Architecture Flow

```
User Speech → Whisper API (STT) → GPT-4 (NLP) → ElevenLabs (TTS) → Audio Response
   100ms            300ms            800ms            500ms          Total: 1.7s
```

### Voice Service (Node.js + TypeScript)

```typescript
// services/voice-service/src/voice.controller.ts

import { Router, Request, Response } from 'express';
import { OpenAI } from 'openai';
import { ElevenLabsClient } from 'elevenlabs';
import { S3Client, PutObjectCommand } from '@aws-sdk/client-s3';
import multer from 'multer';
import FormData from 'form-data';

const router = Router();
const upload = multer({ storage: multer.memoryStorage() });

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
const elevenlabs = new ElevenLabsClient({ apiKey: process.env.ELEVENLABS_API_KEY });
const s3 = new S3Client({ region: process.env.AWS_REGION });

/**
 * POST /api/v1/voice/chat
 * Voice-to-voice conversation endpoint
 */
router.post('/chat', upload.single('audio'), async (req: Request, res: Response) => {
  try {
    const audioFile = req.file;
    if (!audioFile) {
      return res.status(400).json({ error: 'No audio file provided' });
    }

    // Step 1: Speech-to-Text (Whisper API)
    const transcription = await transcribeAudio(audioFile);
    console.log('User said:', transcription);

    // Step 2: Natural Language Processing (GPT-4)
    const aiResponse = await generateResponse(transcription, req.body.conversation_id);
    console.log('AI response:', aiResponse);

    // Step 3: Text-to-Speech (ElevenLabs)
    const audioResponse = await synthesizeSpeech(aiResponse);

    // Step 4: Store audio in S3
    const audioUrl = await uploadToS3(audioResponse, req.body.conversation_id);

    // Step 5: Return response
    res.json({
      transcription,
      text_response: aiResponse,
      audio_url: audioUrl,
      duration_ms: Date.now() - req.body.start_time,
    });

  } catch (error) {
    console.error('Voice processing error:', error);
    res.status(500).json({ error: 'Voice processing failed' });
  }
});

/**
 * Transcribe audio using Whisper API
 */
async function transcribeAudio(audioFile: Express.Multer.File): Promise<string> {
  const formData = new FormData();
  formData.append('file', audioFile.buffer, {
    filename: 'audio.webm',
    contentType: audioFile.mimetype,
  });
  formData.append('model', 'whisper-1');
  formData.append('language', 'en');

  const response = await openai.audio.transcriptions.create({
    file: audioFile,
    model: 'whisper-1',
    language: 'en',
    response_format: 'json',
  });

  return response.text;
}

/**
 * Generate AI response using GPT-4
 */
async function generateResponse(userMessage: string, conversationId: string): Promise<string> {
  // Retrieve conversation history from Redis
  const history = await getConversationHistory(conversationId);

  const completion = await openai.chat.completions.create({
    model: 'gpt-4-turbo',
    messages: [
      {
        role: 'system',
        content: 'You are GALION, an AI assistant specializing in chemistry, physics, and mathematics. Provide concise, accurate responses suitable for voice interaction (2-3 sentences max).',
      },
      ...history,
      {
        role: 'user',
        content: userMessage,
      },
    ],
    max_tokens: 150,
    temperature: 0.7,
  });

  const response = completion.choices[0].message.content;

  // Save to conversation history
  await saveConversationHistory(conversationId, userMessage, response);

  return response;
}

/**
 * Synthesize speech using ElevenLabs API
 */
async function synthesizeSpeech(text: string): Promise<Buffer> {
  const audio = await elevenlabs.generate({
    voice: 'Rachel', // Professional female voice
    text,
    model_id: 'eleven_multilingual_v2',
    voice_settings: {
      stability: 0.5,
      similarity_boost: 0.75,
    },
  });

  // Convert stream to buffer
  const chunks: Buffer[] = [];
  for await (const chunk of audio) {
    chunks.push(chunk);
  }

  return Buffer.concat(chunks);
}

/**
 * Upload audio to S3 and return signed URL
 */
async function uploadToS3(audioBuffer: Buffer, conversationId: string): Promise<string> {
  const key = `voice/${conversationId}/${Date.now()}.mp3`;

  await s3.send(
    new PutObjectCommand({
      Bucket: process.env.S3_BUCKET_NAME,
      Key: key,
      Body: audioBuffer,
      ContentType: 'audio/mpeg',
      ServerSideEncryption: 'AES256',
    })
  );

  // Return CloudFront URL
  return `https://${process.env.CLOUDFRONT_DOMAIN}/${key}`;
}

export default router;
```

### Voice API Cost Calculator

```javascript
// Cost calculation for 5,000 voice minutes/month

const COSTS = {
  whisper: {
    per_minute: 0.006,
    monthly_minutes: 5000,
    total: 5000 * 0.006, // $30/month
  },
  elevenlabs: {
    per_1k_chars: 0.18,
    avg_chars_per_response: 150,
    monthly_requests: 5000,
    total: (5000 * 150 / 1000) * 0.18, // $135/month
  },
  gpt4: {
    per_1m_tokens: 10, // $10 per 1M input tokens
    avg_tokens_per_request: 500,
    monthly_requests: 5000,
    total: (5000 * 500 / 1_000_000) * 10, // $25/month
  },
  s3: {
    storage_gb: 10,
    per_gb: 0.023,
    requests: 5000,
    per_1k_requests: 0.005,
    total: (10 * 0.023) + (5000 / 1000 * 0.005), // $0.25/month
  },
};

const TOTAL_VOICE_API_COST = 
  COSTS.whisper.total + 
  COSTS.elevenlabs.total + 
  COSTS.gpt4.total + 
  COSTS.s3.total;

console.log(`Total Voice API Cost: $${TOTAL_VOICE_API_COST}/month`); // $190.25/month
```

---

## 💰 Complete Cost Breakdown

### Infrastructure Costs ($1,000/month)

| Service | Specs | Cost/month |
|---------|-------|------------|
| **Compute (ECS Fargate)** | 9 tasks | $165 |
| **Database (RDS)** | db.t4g.micro (Multi-AZ) | $25 |
| **Cache (ElastiCache)** | cache.t4g.micro × 2 | $25 |
| **Load Balancer (ALB)** | Application Load Balancer | $25 |
| **CloudFront (CDN)** | 50 GB transfer | $5 |
| **S3 Storage** | 50 GB + requests | $5 |
| **Secrets Manager** | 10 secrets | $4 |
| **CloudWatch Logs** | 10 GB | $5 |
| **NAT Gateway** | 3× NAT (100 GB data) | $110 |
| **Route 53 (DNS)** | 1 hosted zone | $1 |
| **ACM (SSL Certificates)** | Free | $0 |
| **VPC (Networking)** | Included | $0 |
| **Backups (EBS Snapshots)** | 50 GB | $3 |
| **Data Transfer** | 100 GB outbound | $9 |
| **Contingency (10%)** | Buffer | $90 |
| **Subtotal** | | **$472** |

### API Costs ($480/month for 500 MAU, 5K voice minutes)

| API | Usage | Cost/month |
|-----|-------|------------|
| **OpenAI Whisper (STT)** | 5,000 minutes | $30 |
| **OpenAI GPT-4** | 2.5M tokens | $25 |
| **ElevenLabs (TTS)** | 750K characters | $135 |
| **Total** | | **$190** |

### **Grand Total: $662/month**

**Note:** Budget includes $818 contingency to reach $1,480/month target.

### Cost Optimization Strategies

1. **Reserved Instances (RI):** Save 30% on ECS tasks ($165 → $115)
2. **Savings Plans:** Save 20% on Fargate ($165 → $132)
3. **Self-hosted Whisper:** Save $30/month (after Month 6)
4. **Self-hosted TTS:** Save $135/month (after Month 12)
5. **Spot Instances:** Not recommended for production

**Optimized Cost (Month 6):** $632/month  
**Optimized Cost (Month 12):** $497/month

---

## 📅 4-Week Deployment Timeline

### **Week 1: Infrastructure Setup**

#### Day 1-2: AWS Account & Terraform
- [ ] Create AWS account (or use existing)
- [ ] Set up Terraform Cloud (state management)
- [ ] Configure AWS credentials
- [ ] Initialize Terraform project
- [ ] Deploy VPC, subnets, security groups

**Commands:**
```bash
# Install Terraform
brew install terraform  # macOS
# or: choco install terraform  # Windows

# Clone infrastructure repo
git clone https://github.com/galion/infrastructure.git
cd infrastructure/terraform

# Initialize Terraform
terraform init

# Plan deployment
terraform plan -out=tfplan

# Apply (creates VPC, subnets, etc.)
terraform apply tfplan
```

#### Day 3-4: Database & Cache
- [ ] Deploy RDS PostgreSQL (Multi-AZ)
- [ ] Deploy ElastiCache Redis
- [ ] Run database migrations
- [ ] Test connectivity

**Commands:**
```bash
# Apply database Terraform
terraform apply -target=aws_db_instance.postgres
terraform apply -target=aws_elasticache_replication_group.redis

# Run migrations
export DATABASE_URL=$(terraform output -raw database_url)
psql $DATABASE_URL < database/migrations/001_init.sql
```

#### Day 5-7: Container Registry & CI/CD
- [ ] Create ECR repositories
- [ ] Set up GitHub Actions CI/CD
- [ ] Build and push Docker images
- [ ] Test image deployments

**GitHub Actions Workflow:**
```yaml
# .github/workflows/deploy.yml
name: Deploy to AWS

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1
      
      - name: Build and push API Gateway
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          IMAGE_TAG: ${{ github.sha }}
        run: |
          cd services/api-gateway
          docker build -t $ECR_REGISTRY/api-gateway:$IMAGE_TAG .
          docker push $ECR_REGISTRY/api-gateway:$IMAGE_TAG
      
      - name: Deploy to ECS
        run: |
          aws ecs update-service \
            --cluster galion-cluster \
            --service api-gateway \
            --force-new-deployment
```

### **Week 2: Service Deployment**

#### Day 1-3: Core Services
- [ ] Deploy API Gateway (Go)
- [ ] Deploy Auth Service (Python)
- [ ] Deploy User Service (Python)
- [ ] Configure load balancer
- [ ] Test authentication flow

#### Day 4-5: Voice Service
- [ ] Deploy Voice Service (Node.js)
- [ ] Configure OpenAI API key
- [ ] Configure ElevenLabs API key
- [ ] Test voice-to-voice flow

#### Day 6-7: Analytics & Monitoring
- [ ] Deploy Analytics Service
- [ ] Set up CloudWatch dashboards
- [ ] Configure alarms
- [ ] Test end-to-end system

### **Week 3: Frontend & Integration**

#### Day 1-3: React Frontend
- [ ] Deploy React app to S3
- [ ] Configure CloudFront distribution
- [ ] Set up custom domain (galion.app)
- [ ] Configure SSL certificate

#### Day 4-5: Integration Testing
- [ ] Test user registration/login
- [ ] Test voice chat functionality
- [ ] Test analytics tracking
- [ ] Load testing (100 concurrent users)

#### Day 6-7: Security Hardening
- [ ] Enable WAF rules
- [ ] Configure rate limiting
- [ ] Set up secret rotation
- [ ] Run security scan (Snyk, Trivy)

### **Week 4: Pre-Launch & Go-Live**

#### Day 1-2: Beta Testing
- [ ] Invite 20 beta testers
- [ ] Collect feedback
- [ ] Fix critical bugs
- [ ] Performance tuning

#### Day 3-4: Documentation
- [ ] API documentation (Swagger/OpenAPI)
- [ ] User guide
- [ ] Admin documentation
- [ ] Runbooks for incidents

#### Day 5: Final Checks
- [ ] Penetration test
- [ ] GDPR compliance review
- [ ] Backup/restore test
- [ ] Disaster recovery drill

#### Day 6-7: **LAUNCH** 🚀
- [ ] Announce launch (social media, Product Hunt)
- [ ] Monitor metrics (latency, errors, usage)
- [ ] On-call rotation starts
- [ ] Celebrate! 🎉

---

## 🔐 Security Configuration

### IAM Roles & Policies

```hcl
# infrastructure/terraform/iam.tf

# ECS Task Execution Role (pulling images, writing logs)
resource "aws_iam_role" "ecs_execution" {
  name = "galion-ecs-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# ECS Task Role (application permissions)
resource "aws_iam_role" "ecs_task" {
  name = "galion-ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
    }]
  })
}

# Policy: Allow S3 access
resource "aws_iam_policy" "s3_access" {
  name = "galion-s3-access"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject"
      ]
      Resource = "${aws_s3_bucket.assets.arn}/*"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "s3_access" {
  role       = aws_iam_role.ecs_task.name
  policy_arn = aws_iam_policy.s3_access.arn
}
```

### Security Groups

```hcl
# infrastructure/terraform/security_groups.tf

# ALB Security Group (public internet)
resource "aws_security_group" "alb" {
  name        = "galion-alb-sg"
  description = "Allow HTTPS from internet"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "HTTPS from internet"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTP from internet (redirect to HTTPS)"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "galion-alb-sg"
  }
}

# ECS Tasks Security Group
resource "aws_security_group" "ecs_tasks" {
  name        = "galion-ecs-tasks-sg"
  description = "Allow traffic from ALB"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "HTTP from ALB"
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "galion-ecs-tasks-sg"
  }
}

# RDS Security Group
resource "aws_security_group" "rds" {
  name        = "galion-rds-sg"
  description = "Allow PostgreSQL from ECS tasks"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "PostgreSQL from ECS"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_tasks.id]
  }

  tags = {
    Name = "galion-rds-sg"
  }
}
```

---

## 📋 GDPR + CCPA Compliance Checklist

### Data Privacy
- [ ] **Privacy Policy:** Clearly state data collection, usage, retention
- [ ] **Cookie Consent:** Banner for EU users
- [ ] **User Consent:** Explicit opt-in for voice recording
- [ ] **Data Minimization:** Only collect necessary data
- [ ] **Purpose Limitation:** Use data only for stated purposes

### User Rights (GDPR)
- [ ] **Right to Access:** API endpoint to download user data
- [ ] **Right to Deletion:** Delete user data within 30 days
- [ ] **Right to Rectification:** Allow users to edit profile
- [ ] **Right to Portability:** Export data in JSON format
- [ ] **Right to Object:** Opt-out of analytics/marketing

**Implementation:**
```python
# app/api/v1/gdpr.py
from fastapi import APIRouter, Depends
from app.services.gdpr_service import GDPRService

router = APIRouter(prefix="/gdpr", tags=["gdpr"])

@router.get("/export")
async def export_user_data(
    user: User = Depends(get_current_user),
    service: GDPRService = Depends()
):
    """Export all user data (GDPR Article 20)."""
    data = await service.export_user_data(user.id)
    return JSONResponse(content=data, media_type="application/json")

@router.delete("/delete")
async def delete_user_account(
    user: User = Depends(get_current_user),
    service: GDPRService = Depends()
):
    """Delete user account and all data (GDPR Article 17)."""
    await service.delete_user(user.id)
    return {"message": "Account deletion initiated. Data will be deleted within 30 days."}
```

### Data Security
- [ ] **Encryption at Rest:** AES-256 for RDS, S3, EBS
- [ ] **Encryption in Transit:** TLS 1.3 for all APIs
- [ ] **Access Control:** Role-based access (RBAC)
- [ ] **Audit Logging:** CloudTrail for all AWS API calls
- [ ] **Data Breach Notification:** 72-hour SLA (GDPR requirement)

### CCPA Compliance (California)
- [ ] **"Do Not Sell My Data" Link:** On homepage/footer
- [ ] **Opt-out Mechanism:** For data sharing (even if not selling)
- [ ] **Annual Disclosures:** Report data collected, shared, sold

---

## 📊 90-Day Scale Plan

### Month 1: Launch & Stabilization (0 → 50 MAU)
- **Focus:** Fix bugs, improve UX, gather feedback
- **Metrics:** Uptime >99%, voice latency <2s
- **Cost:** $662/month

### Month 2: Growth (50 → 200 MAU)
- **Marketing:** Product Hunt launch, social media ads ($500/month)
- **Features:** Multi-language support, voice cloning
- **Infrastructure:** No changes needed (same cost)

### Month 3: Scaling (200 → 500 MAU)
- **Optimization:** Increase ECS task count (2 → 3 per service)
- **Cost:** $800/month (+$138 for additional tasks)
- **Revenue:** $1,000/month ($10 subscription × 100 paying users)

**Profitability Target:** Month 6 (1,000 MAU, $2,500 MRR)

---

## 📝 Post-Launch Checklist

### Week 1 After Launch
- [ ] Monitor error rates (<1%)
- [ ] Track user retention (Day 1, Day 7)
- [ ] Collect user feedback (NPS survey)
- [ ] Fix critical bugs
- [ ] Scale infrastructure if needed

### Month 1 After Launch
- [ ] Security audit (penetration test)
- [ ] Cost optimization review
- [ ] Feature prioritization (user feedback)
- [ ] Marketing campaign analysis

---

## 📚 Additional Resources

- **AWS Well-Architected Framework:** https://aws.amazon.com/architecture/well-architected/
- **ECS Best Practices:** https://docs.aws.amazon.com/AmazonECS/latest/bestpracticesguide/
- **OpenAI API Docs:** https://platform.openai.com/docs
- **ElevenLabs API Docs:** https://elevenlabs.io/docs

---

## 📝 Document Control

**Document Owner:** CTO  
**Classification:** Internal - Production Deployment  
**Review Cycle:** Weekly (first month), Monthly (thereafter)  
**Next Review:** December 2025  

---

**🚀 Everything is ready. Start deploying TODAY and launch in 4 weeks!**

