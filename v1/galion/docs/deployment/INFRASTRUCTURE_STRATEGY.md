# Infrastructure & Deployment Strategy

**Status:** Draft  
**Version:** 1.0.0  
**Date:** November 9, 2025  
**Philosophy:** First Principles - Build, Simplify, Scale

---

## Executive Summary

This document outlines the complete infrastructure strategy for deploying the Nexus ecosystem, including Galion, JARVIS AI, Black Box Core, and all supporting services across development, staging, and production environments.

**Key Objectives:**
1. **Self-Hosted Infrastructure** - Own our servers, control our destiny
2. **Cloud-Hybrid Model** - Use cloud for GPU workloads, self-host for core services
3. **Cost Optimization** - <$5K/month for alpha, scale as needed
4. **High Availability** - 99.9% uptime with automatic failover
5. **Security First** - Zero-trust architecture, encrypted everything

---

## 1. First Principles Analysis

### 1.1 Question Every Requirement

**Q:** Do we need managed Kubernetes (EKS/GKE/AKS)?  
**A:** NO for alpha. Self-managed K3s on dedicated servers is 10x cheaper.

**Q:** Do we need multi-region deployment?  
**A:** NO for alpha. Single region with good backups is sufficient.

**Q:** Do we need expensive GPU instances 24/7?  
**A:** NO. Use spot instances for training, dedicated for inference.

**Q:** Do we need managed databases?  
**A:** MAYBE. PostgreSQL on dedicated server vs RDS - depends on scale.

**Q:** Do we need CDN?  
**A:** YES. Cloudflare is free and provides DDoS protection.

### 1.2 Delete Unnecessary Components

**DELETE:**
- ❌ Managed Kubernetes (use K3s, save $200/month)
- ❌ NAT Gateway (use single public IP, save $50/month)
- ❌ Load Balancer (use nginx/Traefik, save $20/month)
- ❌ Managed Redis (self-host, save $100/month)
- ❌ Multiple environments initially (dev/staging/prod → dev/prod only)

**KEEP:**
- ✅ Cloud GPU for AI workloads (necessary)
- ✅ CDN (Cloudflare free tier)
- ✅ Object storage (S3 or equivalent)
- ✅ Monitoring (self-hosted Prometheus)

### 1.3 Simplify Architecture

**Before (Complex):**
```
Managed K8s → NAT Gateway → Load Balancer → Service Mesh
  ↓
Managed Redis + Managed DB + Managed Cache
  ↓
Multi-AZ, Multi-Region, Auto-Scaling Everything
Monthly Cost: $5,000+
```

**After (Simplified):**
```
K3s on Dedicated Servers → Cloudflare → nginx
  ↓
Self-Hosted PostgreSQL + Redis (with backups)
  ↓
Single Region, Manual Scaling, Essential Services Only
Monthly Cost: $500-1,500
```

---

## 2. Infrastructure Tiers

### 2.1 Alpha Tier (Current → 6 months)

**Goal:** Prove concept, support 100-1000 users

**Infrastructure:**
```
┌─────────────────────────────────────────────┐
│           ALPHA INFRASTRUCTURE               │
├─────────────────────────────────────────────┤
│                                             │
│  Dedicated Servers (Hetzner/OVH)            │
│  ├── Server 1: AMD EPYC 16 cores, 64GB RAM │
│  │   • K3s Control Plane                    │
│  │   • PostgreSQL (primary)                 │
│  │   • Redis                                │
│  │   • Core services                        │
│  │                                           │
│  ├── Server 2: AMD EPYC 16 cores, 64GB RAM │
│  │   • K3s Worker                           │
│  │   • Application services                 │
│  │   • Monitoring stack                     │
│  │                                           │
│  └── Server 3: Storage Server               │
│      • 4TB NVMe RAID                        │
│      • Backup storage                       │
│      • MinIO (S3-compatible)                │
│                                             │
│  Cloud GPU (AWS/Vast.ai/RunPod)            │
│  ├── 1× A100 40GB for inference            │
│  └── Spot instances for training            │
│                                             │
│  Cloudflare (Free Tier)                     │
│  ├── DNS                                    │
│  ├── CDN                                    │
│  ├── DDoS protection                        │
│  └── SSL certificates                       │
│                                             │
└─────────────────────────────────────────────┘

Monthly Cost: $400-600 servers + $500-800 GPU = $900-1,400
```

**Capacity:**
- **Users:** 1,000 concurrent
- **Requests:** 10,000 req/min
- **Storage:** 4TB
- **Bandwidth:** 10TB/month

### 2.2 Beta Tier (6-12 months)

**Goal:** Scale to 10,000 users, production-ready

**Infrastructure:**
```
┌─────────────────────────────────────────────┐
│            BETA INFRASTRUCTURE               │
├─────────────────────────────────────────────┤
│                                             │
│  Dedicated Servers (5 total)                │
│  ├── 2× Control Plane (HA)                 │
│  ├── 3× Worker Nodes                        │
│  └── Storage: 10TB NVMe                     │
│                                             │
│  Cloud GPU (scaled up)                      │
│  ├── 2× A100 80GB (inference)              │
│  ├── 4× A100 40GB (training pool)          │
│  └── Auto-scaling based on queue           │
│                                             │
│  Managed Services (selective)               │
│  ├── RDS PostgreSQL (multi-AZ)             │
│  └── ElastiCache Redis (if needed)         │
│                                             │
│  Cloudflare (Pro Plan - $20/month)         │
│  ├── Enhanced DDoS                          │
│  ├── WAF rules                              │
│  └── Analytics                              │
│                                             │
└─────────────────────────────────────────────┘

Monthly Cost: $1,500 servers + $2,000 GPU + $500 managed = $4,000
```

**Capacity:**
- **Users:** 10,000 concurrent
- **Requests:** 100,000 req/min
- **Storage:** 10TB
- **Bandwidth:** 50TB/month

### 2.3 Production Tier (12+ months)

**Goal:** Scale to 100,000+ users, enterprise-grade

**Infrastructure:**
```
┌─────────────────────────────────────────────┐
│         PRODUCTION INFRASTRUCTURE            │
├─────────────────────────────────────────────┤
│                                             │
│  Self-Hosted Cluster (10+ servers)          │
│  ├── 3× Control Plane (HA)                 │
│  ├── 7× Worker Nodes                        │
│  ├── Storage: 50TB distributed             │
│  └── Private network (10 Gbps)             │
│                                             │
│  On-Premise GPU Cluster                     │
│  ├── 8× H100 80GB (owned)                  │
│  ├── 16× A100 40GB (owned)                 │
│  └── ROI break-even at 12 months           │
│                                             │
│  Hybrid Cloud (burst capacity)             │
│  ├── AWS for overflow traffic              │
│  ├── GCP for ML experiments                │
│  └── Cost optimization                      │
│                                             │
│  CDN & Security                             │
│  ├── Cloudflare Enterprise                 │
│  ├── Custom WAF rules                       │
│  └── Advanced bot management                │
│                                             │
└─────────────────────────────────────────────┘

Monthly Cost: $5,000 servers + $3,000 GPU amortization + $2,000 cloud = $10,000
(Plus $500K initial GPU investment amortized over 3 years)
```

---

## 3. Technology Stack

### 3.1 Compute Layer

**Kubernetes Distribution: K3s**
- **Why:** Lightweight (60MB binary), perfect for edge/dedicated servers
- **Features:** Built-in load balancer, minimal dependencies
- **Cost:** FREE (vs $150/month for EKS)

```yaml
# K3s installation
curl -sfL https://get.k3s.io | sh -s - server \
  --write-kubeconfig-mode 644 \
  --disable traefik \  # Use nginx instead
  --disable servicelb  # Use MetalLB
```

**Container Runtime:**
- **containerd** (default with K3s)
- **Alternative:** Docker (if needed for compatibility)

**Service Mesh:**
- **Alpha:** None (keep it simple)
- **Beta:** Linkerd (lighter than Istio)
- **Production:** Istio (full features)

### 3.2 Storage Layer

**Block Storage:**
```yaml
# Longhorn - Cloud-native distributed storage
# Replicates data across nodes
apiVersion: v1
kind: StorageClass
metadata:
  name: longhorn
provisioner: driver.longhorn.io
parameters:
  numberOfReplicas: "3"
  staleReplicaTimeout: "30"
```

**Object Storage:**
- **Alpha:** Self-hosted MinIO (S3-compatible)
- **Beta:** Hybrid (MinIO + S3 for backups)
- **Production:** S3 with Glacier for cold storage

**Database Storage:**
- **PostgreSQL:** Dedicated NVMe SSD (10K IOPS+)
- **Redis:** Memory + persistent AOF backups
- **Kafka:** Dedicated SSD (high throughput)

### 3.3 Networking

**Ingress Controller:**
```yaml
# nginx Ingress Controller
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nexus-ingress
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/rate-limit: "100"
spec:
  tls:
  - hosts:
    - galion.app
    - api.galion.app
    secretName: galion-tls
  rules:
  - host: galion.app
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend
            port:
              number: 80
```

**Load Balancing:**
- **Alpha:** nginx (single instance)
- **Beta:** MetalLB (K8s load balancer)
- **Production:** Multi-layer (Cloudflare → nginx → services)

**DNS & CDN:**
```
User Request
  ↓
Cloudflare (DNS, CDN, DDoS protection)
  ↓
Origin Server (nginx ingress)
  ↓
Kubernetes Services
  ↓
Pods
```

---

## 4. Deployment Strategy

### 4.1 GitOps Workflow

**Tool:** FluxCD

```yaml
# FluxCD setup
# Automatically sync Git → Cluster

# Repository structure
nexus-infra/
├── clusters/
│   ├── alpha/
│   │   ├── flux-system/
│   │   └── apps/
│   ├── beta/
│   └── production/
├── infrastructure/
│   ├── postgres/
│   ├── redis/
│   ├── kafka/
│   └── monitoring/
└── apps/
    ├── api-gateway/
    ├── auth-service/
    └── user-service/
```

**Deployment Flow:**
```
1. Developer commits to main branch
   ↓
2. CI builds and tests
   ↓
3. CI pushes image to registry
   ↓
4. CI updates Kubernetes manifests in Git
   ↓
5. FluxCD detects change
   ↓
6. FluxCD applies to cluster
   ↓
7. Kubernetes performs rolling update
   ↓
8. Health checks pass → deployment complete
```

### 4.2 CI/CD Pipeline

**Tool:** GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Build and Deploy

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker image
        run: docker build -t nexus/api-gateway:${{ github.sha }} .
      
      - name: Run tests
        run: docker run nexus/api-gateway:${{ github.sha }} pytest
      
      - name: Push to registry
        run: docker push nexus/api-gateway:${{ github.sha }}
      
      - name: Update K8s manifests
        run: |
          sed -i 's|image: nexus/api-gateway:.*|image: nexus/api-gateway:${{ github.sha }}|' k8s/deployment.yaml
          git commit -am "Deploy ${{ github.sha }}"
          git push
```

### 4.3 Blue-Green Deployment

```yaml
# Blue-green deployment strategy
apiVersion: v1
kind: Service
metadata:
  name: api-gateway
spec:
  selector:
    app: api-gateway
    version: blue  # Switch to 'green' for new version

---
# Blue deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway-blue
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api-gateway
      version: blue
  template:
    metadata:
      labels:
        app: api-gateway
        version: blue
    spec:
      containers:
      - name: api-gateway
        image: nexus/api-gateway:v1.0

---
# Green deployment (new version)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway-green
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api-gateway
      version: green
  template:
    metadata:
      labels:
        app: api-gateway
        version: green
    spec:
      containers:
      - name: api-gateway
        image: nexus/api-gateway:v1.1
```

---

## 5. Monitoring & Observability

### 5.1 Monitoring Stack

```
┌─────────────────────────────────────────────┐
│         MONITORING ARCHITECTURE              │
├─────────────────────────────────────────────┤
│                                             │
│  Metrics Collection (Prometheus)            │
│  ├── Application metrics                    │
│  ├── System metrics (node-exporter)         │
│  ├── Kubernetes metrics (kube-state)        │
│  └── Custom business metrics                │
│                                             │
│  Visualization (Grafana)                    │
│  ├── System dashboard                       │
│  ├── Application dashboard                  │
│  ├── Business metrics                       │
│  └── AI performance                         │
│                                             │
│  Logging (ELK Stack)                        │
│  ├── Filebeat (log collection)             │
│  ├── Elasticsearch (storage & search)       │
│  ├── Kibana (visualization)                 │
│  └── 7-day retention                        │
│                                             │
│  Tracing (Jaeger)                           │
│  ├── Distributed tracing                    │
│  ├── Request flow analysis                  │
│  └── Performance bottleneck detection       │
│                                             │
│  Alerting (Alertmanager)                    │
│  ├── Slack notifications                    │
│  ├── Email alerts                           │
│  ├── PagerDuty (production)                 │
│  └── Custom webhooks                        │
│                                             │
└─────────────────────────────────────────────┘
```

### 5.2 Key Metrics

**System Metrics:**
```yaml
# Prometheus rules
groups:
  - name: system_alerts
    rules:
      - alert: HighCPUUsage
        expr: node_cpu_seconds_total > 80
        for: 5m
        annotations:
          summary: "High CPU usage detected"
      
      - alert: HighMemoryUsage
        expr: node_memory_usage_percent > 85
        for: 5m
        annotations:
          summary: "High memory usage detected"
      
      - alert: DiskSpaceLow
        expr: node_filesystem_free_percent < 10
        for: 10m
        annotations:
          summary: "Disk space running low"
```

**Application Metrics:**
```yaml
# Custom application metrics
- name: application_alerts
  rules:
    - alert: HighErrorRate
      expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
      annotations:
        summary: "Error rate above 5%"
    
    - alert: SlowResponseTime
      expr: http_request_duration_seconds_p99 > 1.0
      annotations:
        summary: "P99 latency above 1 second"
    
    - alert: LowThroughput
      expr: rate(http_requests_total[5m]) < 10
      annotations:
        summary: "Request rate unexpectedly low"
```

---

## 6. Backup & Disaster Recovery

### 6.1 Backup Strategy (3-2-1 Rule)

**3 copies of data:**
1. Primary (production database)
2. Local backup (on backup server)
3. Remote backup (S3 Glacier)

**2 different media types:**
1. NVMe SSD (fast recovery)
2. HDD (cost-effective long-term)

**1 off-site copy:**
- S3 Glacier (encrypted, versioned)

### 6.2 Backup Schedule

```yaml
# PostgreSQL automated backups
apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgres-backup
spec:
  schedule: "0 */6 * * *"  # Every 6 hours
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:15
            command:
            - /bin/bash
            - -c
            - |
              pg_dump -h postgres -U admin nexus_db | gzip > /backup/nexus_$(date +%Y%m%d_%H%M%S).sql.gz
              # Upload to S3
              aws s3 cp /backup/nexus_*.sql.gz s3://nexus-backups/postgres/
```

**Retention Policy:**
- **Hourly backups:** Keep 24 hours
- **Daily backups:** Keep 7 days
- **Weekly backups:** Keep 4 weeks
- **Monthly backups:** Keep 12 months
- **Yearly backups:** Keep forever

### 6.3 Disaster Recovery Plan

**RTO (Recovery Time Objective):** 4 hours  
**RPO (Recovery Point Objective):** 1 hour

**Recovery Procedure:**
```bash
# 1. Provision new infrastructure (if needed)
terraform apply -var="disaster_recovery=true"

# 2. Restore PostgreSQL from backup
kubectl exec -it postgres-0 -- bash
psql -U admin nexus_db < /backup/latest.sql

# 3. Restore Redis (if backed up)
redis-cli --rdb /backup/dump.rdb

# 4. Restore application secrets
kubectl apply -f backup/secrets.yaml

# 5. Deploy applications
flux reconcile kustomization apps --with-source

# 6. Verify system health
kubectl get pods --all-namespaces
curl https://galion.app/health

# 7. Update DNS (if IP changed)
# 8. Notify team
```

---

## 7. Security Infrastructure

### 7.1 Network Security

```
┌─────────────────────────────────────────────┐
│          NETWORK SECURITY LAYERS             │
├─────────────────────────────────────────────┤
│                                             │
│  Layer 1: Cloudflare                        │
│  ├── DDoS protection (unlimited)            │
│  ├── WAF rules                              │
│  ├── Bot management                         │
│  └── Rate limiting                          │
│                                             │
│  Layer 2: Firewall (iptables/nftables)     │
│  ├── Allow ports: 80, 443 (public)         │
│  ├── Allow port: 6443 (K8s API, VPN only)  │
│  ├── Block all other incoming              │
│  └── Internal network unrestricted          │
│                                             │
│  Layer 3: Network Policies (Kubernetes)     │
│  ├── Deny all by default                    │
│  ├── Explicit allow rules                   │
│  ├── Namespace isolation                    │
│  └── Service-to-service restrictions        │
│                                             │
│  Layer 4: mTLS (Service Mesh)              │
│  ├── Mutual TLS between services           │
│  ├── Certificate rotation                   │
│  ├── Identity verification                  │
│  └── Encrypted communication                │
│                                             │
└─────────────────────────────────────────────┘
```

### 7.2 Access Control

**VPN Access:**
```bash
# WireGuard VPN for admin access
# /etc/wireguard/wg0.conf
[Interface]
Address = 10.0.0.1/24
PrivateKey = <server_private_key>
ListenPort = 51820

[Peer]  # Admin 1
PublicKey = <admin1_public_key>
AllowedIPs = 10.0.0.2/32

[Peer]  # Admin 2
PublicKey = <admin2_public_key>
AllowedIPs = 10.0.0.3/32
```

**SSH Hardening:**
```bash
# /etc/ssh/sshd_config
Port 22
Protocol 2
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
AllowUsers admin1 admin2
MaxAuthTries 3
```

**Kubernetes RBAC:**
```yaml
# Role-based access control
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: developer
rules:
- apiGroups: ["", "apps"]
  resources: ["pods", "deployments"]
  verbs: ["get", "list", "watch"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: developer-binding
subjects:
- kind: User
  name: john@galion.app
roleRef:
  kind: Role
  name: developer
```

---

## 8. Cost Optimization

### 8.1 Current Costs (Alpha)

| Category | Item | Monthly Cost |
|----------|------|--------------|
| **Compute** | 2× Dedicated Servers (Hetzner AX101) | $180 × 2 = $360 |
| | 1× Storage Server (Hetzner SX133) | $80 |
| **GPU** | 1× A100 40GB (RunPod) | $600 |
| **Networking** | Bandwidth (10TB included) | $0 |
| | Cloudflare (Free) | $0 |
| **Storage** | MinIO (self-hosted) | $0 |
| | S3 backups (100GB) | $3 |
| **Monitoring** | Self-hosted (Prometheus/Grafana) | $0 |
| **DNS** | Cloudflare | $0 |
| **Total** | | **$1,043/month** |

### 8.2 Cost Projections

**6 Months (Beta):**
- Servers: $1,200/month (5 servers)
- GPU: $1,500/month (2× A100 + spot instances)
- Managed Services: $300/month (RDS if needed)
- **Total: $3,000/month**

**12 Months (Production):**
- Servers: $2,500/month (10 servers)
- GPU: $2,500/month (amortized ownership)
- Cloud: $1,000/month (burst capacity)
- CDN/Security: $500/month (Cloudflare Enterprise)
- **Total: $6,500/month**

### 8.3 Cost Optimization Strategies

**1. Spot Instances for Training:**
```python
# Use spot instances for batch training
# Save 70% on GPU costs
spot_config = {
    "instance_type": "g5.2xlarge",
    "max_price": "0.50",  # vs $1.21 on-demand
    "interruption_behavior": "terminate",
    "checkpoint_interval": "5min"  # Save progress frequently
}
```

**2. Auto-Scaling:**
```yaml
# Scale down during off-hours
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-gateway
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-gateway
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

**3. Compression & Caching:**
- Enable gzip compression (reduce bandwidth)
- Use CDN caching (reduce origin load)
- Redis caching (reduce database queries)

---

## 9. Migration Plan

### 9.1 Phase 1: Setup Infrastructure (Week 1-2)

```bash
# Day 1-3: Server provisioning
- Order dedicated servers
- Configure network
- Install OS (Ubuntu 22.04 LTS)
- Harden security

# Day 4-7: Kubernetes setup
- Install K3s
- Configure storage (Longhorn)
- Setup ingress controller
- Deploy monitoring stack

# Day 8-10: Deploy services
- Migrate databases
- Deploy applications
- Configure DNS
- Test end-to-end

# Day 11-14: Migration
- Run in parallel with old system
- Gradual traffic migration
- Monitor for issues
- Full cutover
```

### 9.2 Migration Checklist

**Pre-Migration:**
- [ ] Infrastructure provisioned
- [ ] Backups verified
- [ ] DNS TTL lowered (1 hour)
- [ ] Team notified
- [ ] Rollback plan ready

**During Migration:**
- [ ] Database migration (pg_dump → restore)
- [ ] File migration (rsync)
- [ ] DNS update
- [ ] Verify health checks
- [ ] Monitor error rates

**Post-Migration:**
- [ ] All services healthy
- [ ] Performance acceptable
- [ ] Backups working
- [ ] Monitoring active
- [ ] Old infrastructure decommissioned (after 7 days)

---

## 10. Performance Optimization

### 10.1 Database Optimization

```sql
-- PostgreSQL tuning
ALTER SYSTEM SET shared_buffers = '16GB';
ALTER SYSTEM SET effective_cache_size = '48GB';
ALTER SYSTEM SET work_mem = '256MB';
ALTER SYSTEM SET maintenance_work_mem = '2GB';
ALTER SYSTEM SET max_connections = '200';

-- Connection pooling (PgBouncer)
[databases]
nexus_db = host=localhost port=5432 dbname=nexus_db

[pgbouncer]
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 25
```

### 10.2 Caching Strategy

```python
# Multi-layer caching
class CacheManager:
    def __init__(self):
        self.l1_cache = {}  # In-memory (fast, volatile)
        self.l2_cache = RedisClient()  # Redis (fast, persistent)
        self.l3_cache = CDN()  # CDN (distributed)
    
    def get(self, key):
        # Check L1 cache (in-memory)
        if key in self.l1_cache:
            return self.l1_cache[key]
        
        # Check L2 cache (Redis)
        value = self.l2_cache.get(key)
        if value:
            self.l1_cache[key] = value  # Populate L1
            return value
        
        # Check L3 cache (CDN)
        value = self.l3_cache.get(key)
        if value:
            self.l2_cache.set(key, value)  # Populate L2
            self.l1_cache[key] = value  # Populate L1
            return value
        
        # Cache miss - fetch from database
        return None
```

---

## Conclusion

This infrastructure strategy provides a clear path from alpha to production, balancing cost, performance, and reliability. By following first principles and making smart technology choices, we achieve enterprise-grade infrastructure at a fraction of typical cloud costs.

**Key Achievements:**
- ✅ <$1,500/month for alpha (vs $5,000+ on AWS/GCP)
- ✅ Full control over infrastructure
- ✅ 99.9% uptime target
- ✅ Scalable architecture
- ✅ Security-first design

**Status:** Strategy Complete - Ready for Implementation

---

**Document Version:** 1.0  
**Last Updated:** November 9, 2025  
**Authors:** Project Nexus Team  
**License:** Proprietary



