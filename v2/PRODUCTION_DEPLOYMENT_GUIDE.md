# NexusLang v2 - Production Deployment Guide

**Last Updated:** November 11, 2025  
**Target:** Production Launch

---

## Overview

This guide covers deploying NexusLang v2 Platform to production using Kubernetes or Docker Compose.

---

## Prerequisites

### Required
- Docker 24+
- Kubernetes cluster (or Docker Compose for simpler deployment)
- Domain name configured
- SSL certificates (Let's Encrypt via cert-manager)
- PostgreSQL 15+ with pgvector extension
- Redis 7+

### Recommended
- Load balancer (Nginx/Cloudflare)
- Monitoring (Prometheus + Grafana)
- Backup solution
- CDN for static assets

---

## Option 1: Kubernetes Deployment (Recommended for Scale)

### 1. Prepare Cluster

```bash
# Create namespace
kubectl apply -f v2/infrastructure/kubernetes/namespace.yaml

# Verify namespace
kubectl get namespaces | grep nexuslang
```

### 2. Configure Secrets

```bash
# Create secrets for sensitive data
kubectl create secret generic nexuslang-secrets \
  --from-literal=database-url="postgresql+asyncpg://user:pass@postgres:5432/nexus_v2" \
  --from-literal=redis-url="redis://redis:6379" \
  --from-literal=openai-api-key="sk-your-key-here" \
  --from-literal=secret-key="your-secret-key-32-chars" \
  --from-literal=jwt-secret="your-jwt-secret-64-chars" \
  -n nexuslang-v2
```

### 3. Deploy Services

```bash
# Deploy in order
kubectl apply -f v2/infrastructure/kubernetes/postgres.yaml
kubectl apply -f v2/infrastructure/kubernetes/redis.yaml
kubectl apply -f v2/infrastructure/kubernetes/backend-deployment.yaml
kubectl apply -f v2/infrastructure/kubernetes/frontend-deployment.yaml
kubectl apply -f v2/infrastructure/kubernetes/ingress.yaml

# Or use the script
chmod +x v2/infrastructure/scripts/deploy.sh
./v2/infrastructure/scripts/deploy.sh
```

### 4. Verify Deployment

```bash
# Check pods
kubectl get pods -n nexuslang-v2

# Check services
kubectl get services -n nexuslang-v2

# Check logs
kubectl logs -f deployment/nexuslang-backend -n nexuslang-v2
kubectl logs -f deployment/nexuslang-frontend -n nexuslang-v2
```

---

## Option 2: Docker Compose Deployment (Simpler)

### 1. Prepare Server

```bash
# SSH to server
ssh user@your-server.com

# Install Docker and Docker Compose
curl -fsSL https://get.docker.com | sh
sudo apt install docker-compose-plugin

# Clone repository
git clone https://github.com/your-org/project-nexus.git
cd project-nexus
```

### 2. Configure Environment

```bash
# Copy environment template
cp env.production.template .env

# Edit with your values
nano .env
```

Required values in `.env`:
```env
# Database
POSTGRES_PASSWORD=your_secure_password
POSTGRES_USER=nexus
POSTGRES_DB=nexus_v2

# Redis
REDIS_PASSWORD=your_redis_password

# Security
SECRET_KEY=your_secret_key_at_least_32_characters
JWT_SECRET=your_jwt_secret_at_least_64_characters

# AI Services (optional but recommended)
OPENAI_API_KEY=sk-your-openai-key

# Domains
DOMAIN=nexuslang.dev
API_DOMAIN=api.nexuslang.dev
```

### 3. Deploy

```bash
# Pull images
docker-compose -f docker-compose.prod.yml pull

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### 4. Initialize Database

```bash
# Run migrations
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

# Or manually
docker-compose -f docker-compose.prod.yml exec postgres \
  psql -U nexus -d nexus_v2 -f /app/database/schemas/init.sql
```

---

## DNS Configuration

### Cloudflare Setup (Recommended)

1. **Add Domain to Cloudflare**
   - Go to Cloudflare dashboard
   - Add your domain
   - Update nameservers at registrar

2. **Create DNS Records**
   ```
   Type: A
   Name: @
   Content: YOUR_SERVER_IP
   Proxy: Enabled (orange cloud)
   
   Type: A
   Name: api
   Content: YOUR_SERVER_IP
   Proxy: Enabled
   
   Type: CNAME
   Name: www
   Content: nexuslang.dev
   Proxy: Enabled
   ```

3. **Enable Features**
   - SSL/TLS: Full (strict)
   - Always Use HTTPS: On
   - Automatic HTTPS Rewrites: On
   - Brotli compression: On
   - WAF: On
   - DDoS Protection: On

---

## SSL Certificates

### Option A: Cloudflare (Automatic)
If using Cloudflare with proxy enabled, SSL is automatic!

### Option B: Let's Encrypt with Cert-Manager

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create ClusterIssuer
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@nexuslang.dev
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

---

## Monitoring Setup

### 1. Deploy Prometheus

```bash
kubectl apply -f v2/infrastructure/prometheus/prometheus-deployment.yaml
```

### 2. Deploy Grafana

```bash
kubectl apply -f v2/infrastructure/grafana/grafana-deployment.yaml
```

### 3. Access Monitoring

```
Prometheus: https://prometheus.nexuslang.dev
Grafana: https://grafana.nexuslang.dev
```

---

## Post-Deployment Checklist

### Verify Services

- [ ] Frontend loads: https://nexuslang.dev
- [ ] Backend health: https://api.nexuslang.dev/health
- [ ] API docs: https://api.nexuslang.dev/docs
- [ ] Database connected
- [ ] Redis connected
- [ ] OpenAI API working

### Security

- [ ] SSL certificates valid
- [ ] HTTPS redirect working
- [ ] CORS configured correctly
- [ ] Rate limiting enabled
- [ ] Authentication working
- [ ] API keys secured

### Performance

- [ ] Page load < 1s
- [ ] API response < 100ms
- [ ] CDN caching working
- [ ] Asset compression enabled

### Monitoring

- [ ] Prometheus collecting metrics
- [ ] Grafana dashboards configured
- [ ] Alerts configured
- [ ] Log aggregation working

---

## Scaling

### Horizontal Scaling

```bash
# Scale backend
kubectl scale deployment nexuslang-backend --replicas=5 -n nexuslang-v2

# Scale frontend
kubectl scale deployment nexuslang-frontend --replicas=3 -n nexuslang-v2
```

### Auto-scaling

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: nexuslang-backend-hpa
  namespace: nexuslang-v2
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: nexuslang-backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

---

## Backup Strategy

### Database Backups

```bash
# Daily automated backup
0 2 * * * docker-compose exec postgres pg_dump -U nexus nexus_v2 | gzip > /backups/nexus_$(date +\%Y\%m\%d).sql.gz

# Or with Kubernetes CronJob
kubectl apply -f v2/infrastructure/kubernetes/backup-cronjob.yaml
```

### Restore from Backup

```bash
# Restore database
gunzip < /backups/nexus_20251111.sql.gz | \
  docker-compose exec -T postgres psql -U nexus -d nexus_v2
```

---

## Monitoring and Alerts

### Key Metrics to Monitor

1. **Application Health**
   - HTTP response time (target: <100ms)
   - Error rate (target: <0.1%)
   - Request throughput

2. **Resource Usage**
   - CPU usage (alert at >80%)
   - Memory usage (alert at >85%)
   - Disk space (alert at >80%)

3. **Database**
   - Connection pool usage
   - Query performance
   - Replication lag

4. **Business Metrics**
   - Active users
   - Code executions
   - API calls
   - Subscription signups

---

## Troubleshooting

### Backend Won't Start

```bash
# Check logs
kubectl logs deployment/nexuslang-backend -n nexuslang-v2

# Common issues:
# 1. Database not ready - wait 30s and retry
# 2. Missing secrets - verify kubectl get secrets
# 3. Port conflicts - check service ports
```

### Frontend Won't Load

```bash
# Check logs
kubectl logs deployment/nexuslang-frontend -n nexuslang-v2

# Common issues:
# 1. API URL misconfigured - check NEXT_PUBLIC_API_URL
# 2. Build failed - rebuild image
# 3. Memory limit - increase resources
```

### SSL Issues

```bash
# Check certificate
kubectl describe certificate nexuslang-tls -n nexuslang-v2

# Check cert-manager logs
kubectl logs -n cert-manager deployment/cert-manager
```

---

## Rollback Procedure

### Kubernetes

```bash
# Rollback backend
kubectl rollout undo deployment/nexuslang-backend -n nexuslang-v2

# Rollback frontend
kubectl rollout undo deployment/nexuslang-frontend -n nexuslang-v2

# Check rollout history
kubectl rollout history deployment/nexuslang-backend -n nexuslang-v2
```

### Docker Compose

```bash
# Stop current version
docker-compose -f docker-compose.prod.yml down

# Checkout previous version
git checkout previous-tag

# Start previous version
docker-compose -f docker-compose.prod.yml up -d
```

---

## Performance Optimization

### Database Optimization

```sql
-- Create indexes for common queries
CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_files_project_id ON files(project_id);
CREATE INDEX idx_knowledge_embeddings ON knowledge_entries USING ivfflat (embeddings vector_cosine_ops);

-- Analyze tables
ANALYZE projects;
ANALYZE files;
ANALYZE knowledge_entries;
```

### Caching Strategy

```python
# Redis caching for common queries
CACHE_TTL = {
    'knowledge_search': 3600,  # 1 hour
    'public_projects': 300,     # 5 minutes
    'user_profile': 600,        # 10 minutes
}
```

---

## Cost Estimation

### Monthly Costs (Approximate)

**Infrastructure:**
- Kubernetes cluster (3 nodes): $150-300
- PostgreSQL (managed): $50-100
- Redis (managed): $20-50
- CDN (Cloudflare): $0-20
- **Subtotal:** $220-470/month

**API Costs:**
- OpenAI API (embeddings + TTS): $100-500
- Whisper STT: Included (self-hosted)
- **Subtotal:** $100-500/month

**Total:** $320-970/month (scales with usage)

---

## Success Criteria

### Technical Metrics
- ✅ Uptime > 99.9%
- ✅ API response time < 100ms (p95)
- ✅ Page load time < 1s
- ✅ Error rate < 0.1%

### Business Metrics
- ✅ First 100 users onboarded
- ✅ 10+ paying subscribers
- ✅ 50+ public projects shared
- ✅ Active community participation

---

## Support and Maintenance

### Daily Tasks
- Monitor error rates
- Check system health
- Review user feedback

### Weekly Tasks
- Review analytics
- Update dependencies
- Database maintenance
- Backup verification

### Monthly Tasks
- Security audit
- Performance optimization
- Cost review
- Feature planning

---

## Launch Checklist

### Pre-Launch
- [x] All code deployed
- [x] Database migrated
- [x] Secrets configured
- [ ] DNS configured
- [ ] SSL verified
- [ ] Monitoring active
- [ ] Backups scheduled

### Launch Day
- [ ] Final smoke tests
- [ ] Enable public access
- [ ] Announce on social media
- [ ] Monitor closely
- [ ] Have rollback plan ready

### Post-Launch
- [ ] Gather user feedback
- [ ] Monitor performance
- [ ] Fix critical bugs
- [ ] Iterate quickly

---

## Contact

**Questions or Issues?**
- Email: devops@nexuslang.dev
- Discord: https://discord.gg/nexuslang
- GitHub Issues: https://github.com/your-org/project-nexus/issues

---

**Built with First Principles**  
**Designed for the 22nd Century**  
**Ready for Production**

🚀 **LET'S LAUNCH!** 🚀

