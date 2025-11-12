# BUDGET & SIZING

**Cost Estimates, Storage, GPU Requirements**

**Version:** 1.0  
**Date:** November 9, 2025  
**Status:** Alpha Phase

---

## EXECUTIVE SUMMARY

### Alpha (Months 1-2)
- **Monthly Cost:** ~$500-600
- **Storage:** 100 GB
- **GPU:** 1x g5.2xlarge (Spot)
- **Users:** 500 MAU, 100 DAU
- **Voice:** 5k minutes/month

### Beta (Months 3-6)
- **Monthly Cost:** ~$1,500-2,000
- **Storage:** 1 TB
- **GPU:** 2x g5.2xlarge (Spot)
- **Users:** 5k MAU, 500 DAU
- **Voice:** 50k minutes/month

### 1.0 (Months 7+)
- **Monthly Cost:** ~$4,500-6,000
- **Storage:** 5 TB
- **GPU:** 4x g5.2xlarge (Spot) + auto-scaling
- **Users:** 50k MAU, 5k DAU
- **Voice:** 500k minutes/month

---

## DETAILED BREAKDOWN

### ALPHA PHASE (Months 1-2)

#### Compute

**ECS on EC2:**

| Instance | Type | vCPU | RAM | GPU | Spot Price | Hours/Mo | Monthly Cost |
|----------|------|------|-----|-----|------------|----------|--------------|
| General | m7i.large | 2 | 8 GB | 0 | $0.03/hr | 1,460 | $44 |
| GPU | g5.2xlarge | 8 | 32 GB | 1x A10G | $0.40/hr | 730 | $292 |
| **Total** | | | | | | | **$336** |

**Spot Savings:** 60-62% vs On-Demand

**Services Running:**
- api-gateway (512 CPU, 1024 MB) × 2
- auth-service (512 CPU, 1024 MB) × 2
- user-service (512 CPU, 1024 MB) × 2
- voice-service (4096 CPU, 20480 MB, 1 GPU) × 1

#### Data

**RDS Postgres:**
- Instance: db.t4g.medium (2 vCPU, 4 GB RAM)
- Storage: 100 GB gp3 (3000 IOPS)
- Multi-AZ: No
- Cost: ~$60/month

**ElastiCache Redis:**
- Node: cache.t4g.small (2 vCPU, 1.37 GB RAM)
- Replicas: 0
- Cost: ~$30/month

**S3 Storage:**

| Bucket | Purpose | Size | Storage Class | Cost/GB | Monthly Cost |
|--------|---------|------|---------------|---------|--------------|
| galion-app-data-us | User data, voice | 50 GB | Standard | $0.023 | $1.15 |
| galion-app-data-eu | EU user data | 20 GB | Standard | $0.023 | $0.46 |
| galion-model-artifacts | ML models | 20 GB | Standard | $0.023 | $0.46 |
| galion-static | Static assets | 10 GB | Standard | $0.023 | $0.23 |
| **Total** | | **100 GB** | | | **$2.30** |

**Total Data:** ~$92/month

#### Networking

**NAT Gateway:**
- 1x NAT (us-east-1a)
- Cost: $0.045/hr × 730 = $33/month
- Data processing: $0.045/GB × 100 GB = $4.50/month
- **Total:** ~$38/month

**Data Transfer:**
- Out to internet: 100 GB/month × $0.09/GB = $9/month
- CloudFront (optional): $0.085/GB × 100 GB = $8.50/month

**ALB:**
- Cost: $0.0225/hr × 730 = $16/month
- LCU: ~$5/month
- **Total:** ~$21/month

**Total Networking:** ~$58/month

#### Observability

**CloudWatch:**
- Logs: 10 GB ingested × $0.50/GB = $5/month
- Metrics: 100 custom metrics × $0.30 = $30/month
- Alarms: 10 alarms × $0.10 = $1/month
- **Total:** ~$36/month

**GuardDuty:**
- VPC Flow Logs: 10 GB × $0.50/GB = $5/month

**Total Observability:** ~$41/month

#### Other

**ECR:**
- Storage: 50 GB × $0.10/GB = $5/month

**Secrets Manager:**
- 10 secrets × $0.40 = $4/month

**KMS:**
- 2 keys × $1 = $2/month

**Total Other:** ~$11/month

#### Alpha Total

| Category | Monthly Cost |
|----------|--------------|
| Compute | $336 |
| Data | $92 |
| Networking | $58 |
| Observability | $41 |
| Other | $11 |
| **Total** | **$538** |

**With 10% buffer:** ~$590/month

---

### BETA PHASE (Months 3-6)

#### Compute

| Instance | Quantity | Spot Price | Monthly Cost |
|----------|----------|------------|--------------|
| m7i.large | 4 | $0.03/hr | $88 |
| g5.2xlarge | 2 | $0.40/hr | $584 |
| **Total** | | | **$672** |

**Services Scaling:**
- api-gateway × 4 (load balanced)
- auth-service × 4
- user-service × 4
- voice-service × 2 (GPU)
- ml-service × 1 (GPU, shared with voice)

#### Data

**RDS Postgres:**
- Instance: db.t4g.large (2 vCPU, 8 GB RAM)
- Storage: 500 GB gp3
- Multi-AZ: Yes
- Cost: ~$240/month

**ElastiCache Redis:**
- Node: cache.r6g.large (2 vCPU, 13.07 GB RAM)
- Cluster: 3 shards, 1 replica each
- Cost: ~$440/month

**S3 Storage:**

| Bucket | Size | Lifecycle | Monthly Cost |
|--------|------|-----------|--------------|
| galion-app-data-us | 500 GB | 30d Standard → IA | $11.50 |
| galion-app-data-eu | 200 GB | 30d Standard → IA | $4.60 |
| galion-model-artifacts | 200 GB | Standard | $4.60 |
| galion-static | 100 GB | Standard | $2.30 |
| **Total** | **1 TB** | | **$23** |

**Total Data:** ~$703/month

#### Networking

**NAT Gateway:**
- 2x NAT (AZ-a, AZ-b)
- Cost: $66/month + $20/month (data) = $86/month

**Data Transfer:**
- Out: 500 GB × $0.09 = $45/month

**ALB:**
- Cost: $16/month + LCU $10/month = $26/month

**Total Networking:** ~$157/month

#### Security

**WAF:**
- Base: $5/month
- Rules: 5 × $1 = $5/month
- Requests: 10M × $0.60/1M = $6/month
- **Total:** ~$16/month

**Macie:**
- S3 scanning: 1 TB × $1/GB (first scan) = $1,000 (one-time)
- Ongoing: ~$10/month

**Total Security:** ~$26/month (+ $1,000 one-time)

#### Observability

**CloudWatch:**
- Logs: 50 GB × $0.50 = $25/month
- Metrics: 500 × $0.30 = $150/month
- **Total:** ~$175/month

**X-Ray (optional):**
- Traces: 10M × $0.50/1M = $5/month

**Total Observability:** ~$180/month

#### Other

**ECR:** $10/month  
**Secrets Manager:** $4/month  
**KMS:** $2/month  
**Total Other:** ~$16/month

#### Beta Total

| Category | Monthly Cost |
|----------|--------------|
| Compute | $672 |
| Data | $703 |
| Networking | $157 |
| Security | $26 |
| Observability | $180 |
| Other | $16 |
| **Total** | **$1,754** |

**With 10% buffer:** ~$1,930/month

---

### 1.0 PHASE (Months 7+)

#### Compute (EKS)

**EKS Control Plane:** $73/month

| Instance | Quantity | Spot Price | Monthly Cost |
|----------|----------|------------|--------------|
| m7i.large | 10 | $0.03/hr | $220 |
| g5.2xlarge | 4 | $0.40/hr | $1,168 |
| **Total** | | | **$1,461** |

**Auto-Scaling:**
- Peak: +4 m7i.large, +2 g5.2xlarge = +$700/month
- Average: ~$300/month

**Total Compute:** ~$1,761/month

#### Data

**RDS Postgres:**
- Instance: db.r6g.xlarge (4 vCPU, 32 GB RAM)
- Storage: 2 TB gp3
- Multi-AZ: Yes
- Read Replicas: 1
- Cost: ~$1,200/month

**ElastiCache Redis:**
- Node: cache.r6g.xlarge (4 vCPU, 26.32 GB RAM)
- Cluster: 6 shards, 1 replica each
- Cost: ~$1,760/month

**S3 Storage:**

| Bucket | Size | Monthly Cost |
|--------|------|--------------|
| galion-app-data-us | 3 TB | $69 |
| galion-app-data-eu | 1 TB | $23 |
| galion-model-artifacts | 500 GB | $11.50 |
| galion-static | 500 GB | $11.50 |
| **Total** | **5 TB** | **$115** |

**Total Data:** ~$3,075/month

#### Networking

**NAT Gateway:** $66/month + $80/month (data) = $146/month  
**Data Transfer:** 2 TB × $0.09 = $180/month  
**ALB:** $16/month + LCU $20/month = $36/month  
**Total Networking:** ~$362/month

#### Security

**WAF:** $50/month (100M requests)  
**Shield Advanced (optional):** $3,000/month  
**Macie:** $50/month  
**GuardDuty:** $20/month  
**Total Security:** ~$120/month (without Shield)

#### Observability

**AMP (Prometheus):** $50/month  
**AMG (Grafana):** $50/month  
**CloudWatch:** Logs (200 GB) + Metrics (2k) = $100/month  
**X-Ray:** 50M traces × $0.50/1M = $25/month  
**Total Observability:** ~$225/month

#### Other

**ECR:** $50/month  
**Secrets Manager:** $10/month  
**KMS:** $4/month  
**Total Other:** ~$64/month

#### 1.0 Total

| Category | Monthly Cost |
|----------|--------------|
| Compute | $1,761 |
| Data | $3,075 |
| Networking | $362 |
| Security | $120 |
| Observability | $225 |
| Other | $64 |
| **Total** | **$5,607** |

**With 10% buffer:** ~$6,168/month

---

## STORAGE SIZING

### Voice Data

**Assumptions:**
- Alpha: 5k minutes/month
- Beta: 50k minutes/month
- 1.0: 500k minutes/month

**Storage Calculation:**
- Raw WAV: 1 min = ~10 MB
- FLAC compressed: 1 min = ~5 MB
- Retention: 90 days

**Alpha:**
- 5k min/mo × 5 MB = 25 GB/month
- 90 days = 25 GB × 3 = 75 GB total

**Beta:**
- 50k min/mo × 5 MB = 250 GB/month
- 90 days = 250 GB × 3 = 750 GB total

**1.0:**
- 500k min/mo × 5 MB = 2.5 TB/month
- 90 days = 2.5 TB × 3 = 7.5 TB total

### Text Data (Papers, Embeddings)

**Alpha:**
- Papers: 1k × 5 MB = 5 GB
- Embeddings: 1M chunks × 4 KB = 4 GB
- **Total:** ~10 GB

**Beta:**
- Papers: 10k × 5 MB = 50 GB
- Embeddings: 10M chunks × 4 KB = 40 GB
- **Total:** ~90 GB

**1.0:**
- Papers: 50k × 5 MB = 250 GB
- Embeddings: 50M chunks × 4 KB = 200 GB
- **Total:** ~450 GB

### 3D Models

**Alpha:**
- 100 models × 50 MB = 5 GB

**Beta:**
- 5k models × 50 MB = 250 GB

**1.0:**
- 20k models × 50 MB = 1 TB

---

## GPU REQUIREMENTS

### Model Sizes (VRAM)

| Model | Size | Precision | VRAM |
|-------|------|-----------|------|
| Faster-Whisper medium.en | 769M | int8 | 2 GB |
| XTTS v2 | 400M | fp16 | 4 GB |
| Llama 3.1 8B Instruct | 8B | int8 | 10 GB |
| bge-large embeddings | 335M | fp16 | 1 GB |
| **Total** | | | **17 GB** |

**Headroom:** 24 GB - 17 GB = 7 GB (for batch processing)

### GPU Options

| Instance | GPU | VRAM | vCPU | RAM | On-Demand | Spot | Spot Savings |
|----------|-----|------|------|-----|-----------|------|--------------|
| g5.xlarge | 1x A10G | 24 GB | 4 | 16 GB | $1.01/hr | $0.30/hr | 70% |
| g5.2xlarge | 1x A10G | 24 GB | 8 | 32 GB | $1.21/hr | $0.40/hr | 67% |
| g5.4xlarge | 1x A10G | 24 GB | 16 | 64 GB | $1.63/hr | $0.55/hr | 66% |
| g5.12xlarge | 4x A10G | 96 GB | 48 | 192 GB | $5.67/hr | $1.80/hr | 68% |

**Recommendation:** g5.2xlarge (best balance of cost, performance, availability)

### Scaling Strategy

**Alpha:**
- 1x g5.2xlarge (Spot)
- All models on single GPU
- Cost: ~$292/month

**Beta:**
- 2x g5.2xlarge (Spot)
- GPU 1: STT + TTS
- GPU 2: LLM + Embeddings
- Cost: ~$584/month

**1.0:**
- 4x g5.2xlarge (Spot) + auto-scaling
- Load balanced across GPUs
- Cost: ~$1,168/month + $300 (auto-scaling)

---

## OPTIMIZATION STRATEGIES

### Cost Reduction

**1. Spot Instances:**
- Savings: 60-70%
- Risk: Interruption (mitigate with Spot Fleet, multiple AZs)

**2. Reserved Instances (Future):**
- Savings: 30-50% (1-year commitment)
- Use for predictable baseline (RDS, Redis)

**3. Savings Plans (Future):**
- Savings: 30-50% (1-year commitment)
- Flexible across instance types

**4. S3 Lifecycle:**
- Standard (30 days) → IA (60 days) → Glacier (90+ days)
- Savings: 50-90% on older data

**5. Model Quantization:**
- int8 quantization: 2x throughput, <1% accuracy loss
- Savings: 50% GPU costs (fewer instances needed)

**6. Caching:**
- Redis caching: 90% latency reduction for repeated queries
- Savings: Reduced compute (fewer LLM calls)

**7. Auto-Scaling:**
- Scale to zero at night (if no traffic)
- Savings: 50% compute costs (12 hours/day)

### Performance Optimization

**1. Model Optimization:**
- Flash Attention 2: 2x faster LLM inference
- CTranslate2: 4x faster STT
- TorchScript: 2x faster TTS

**2. Batching:**
- Batch size 4-8: 2-3x throughput
- Trade latency for cost (only at scale)

**3. Streaming:**
- Stream STT, LLM, TTS
- User sees response in 1s (vs 3s)

**4. CDN:**
- CloudFront for static assets
- 50% latency reduction (global users)

---

## TIMELINE & MILESTONES

### Month 1-2 (Alpha)
- **Budget:** $590/month
- **Milestone:** 500 MAU, 5k voice min/mo
- **Burn Rate:** $1,180 total

### Month 3-6 (Beta)
- **Budget:** $1,930/month
- **Milestone:** 5k MAU, 50k voice min/mo
- **Burn Rate:** $7,720 total

### Month 7-12 (1.0)
- **Budget:** $6,168/month
- **Milestone:** 50k MAU, 500k voice min/mo
- **Burn Rate:** $37,008 total

### Year 1 Total
- **Total Burn:** $46,908
- **Revenue (if $10/user/mo, 10% conversion):** $30,000
- **Net:** -$16,908 (seed funding needed)

---

## FUNDING REQUIREMENTS

### Seed Round ($100k)

**Allocation:**
- Infrastructure (Year 1): $50k
- Salaries (2 engineers × $60k/year): $120k (need additional $70k)
- Marketing: $10k
- Legal/Accounting: $5k
- Buffer: $15k

**Runway:** 12 months (break-even at 5k paying users)

### Series A ($1M)

**Allocation:**
- Infrastructure (Year 2-3): $300k
- Salaries (10 engineers): $1.2M
- Marketing: $200k
- Sales: $200k
- Legal/Accounting: $50k
- Buffer: $50k

**Runway:** 24 months (break-even at 50k paying users)

---

## NEXT STEPS

1. **This Week:**
   - Provision Alpha infrastructure ($590/mo)
   - Monitor costs daily (CloudWatch Billing)

2. **This Month:**
   - Optimize Spot usage (save 60%)
   - Implement S3 lifecycle (save 50% on storage)

3. **Next Quarter:**
   - Evaluate Reserved Instances (save 30-50%)
   - Implement auto-scaling (save 50% compute)

---

**Built with First Principles**  
**Status:** Budget Ready  
**Let's spend wisely.** 💰

