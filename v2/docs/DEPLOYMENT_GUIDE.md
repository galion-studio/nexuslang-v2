# NexusLang v2 - Deployment Guide

**Production deployment guide for NexusLang v2 Platform**

---

## Prerequisites

- Docker and Docker Compose
- Kubernetes cluster (for production)
- Domain names
- SSL certificates
- API keys (OpenAI, Shopify)

---

## Development Deployment

### 1. Setup Environment

```bash
# Clone repository
git clone https://github.com/your-org/project-nexus.git
cd project-nexus

# Copy environment file
cp .env.example .env

# Edit .env with your keys
nano .env
```

### 2. Start Services

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### 3. Initialize Database

```bash
# Run database migrations
docker-compose exec postgres psql -U nexus -d nexus_v2 < v2/database/schemas/init.sql
```

### 4. Access Applications

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001

---

## Production Deployment

### Option 1: Kubernetes (Recommended)

#### 1. Build Docker Images

```bash
# Build backend
cd v2/backend
docker build -t nexuslang/backend:latest .

# Build frontend
cd v2/frontend
docker build -t nexuslang/frontend:latest .

# Push to registry
docker push nexuslang/backend:latest
docker push nexuslang/frontend:latest
```

#### 2. Setup Kubernetes

```bash
# Create namespace
kubectl create namespace nexuslang-v2

# Create secrets
kubectl create secret generic nexuslang-secrets \
  --from-literal=database-url="postgresql://..." \
  --from-literal=redis-url="redis://..." \
  --from-literal=openai-api-key="sk-..." \
  --from-literal=shopify-api-key="..." \
  -n nexuslang-v2

# Deploy
kubectl apply -f v2/infrastructure/kubernetes/deployment.yaml

# Check status
kubectl get pods -n nexuslang-v2
kubectl get services -n nexuslang-v2
```

#### 3. Setup Ingress

```bash
# Install nginx ingress controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.9.0/deploy/static/provider/cloud/deploy.yaml

# Install cert-manager for SSL
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Apply ingress
kubectl apply -f v2/infrastructure/kubernetes/ingress.yaml
```

#### 4. Configure DNS

Point your domains to the load balancer:

```
nexuslang.dev          → Load Balancer IP
api.nexuslang.dev      → Load Balancer IP
```

### Option 2: VPS with Docker Compose

#### 1. Setup VPS

```bash
# SSH into VPS
ssh root@your-vps-ip

# Install Docker
curl -fsSL https://get.docker.com | sh

# Install Docker Compose
apt install docker-compose -y
```

#### 2. Deploy Application

```bash
# Clone repository
git clone https://github.com/your-org/project-nexus.git
cd project-nexus

# Setup environment
cp .env.example .env
nano .env

# Start services
docker-compose -f docker-compose.prod.yml up -d
```

#### 3. Setup Nginx

```bash
# Install nginx
apt install nginx -y

# Configure reverse proxy
nano /etc/nginx/sites-available/nexuslang

# Add configuration:
server {
    listen 80;
    server_name nexuslang.dev;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

server {
    listen 80;
    server_name api.nexuslang.dev;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Enable site
ln -s /etc/nginx/sites-available/nexuslang /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

#### 4. Setup SSL

```bash
# Install certbot
apt install certbot python3-certbot-nginx -y

# Get certificates
certbot --nginx -d nexuslang.dev -d api.nexuslang.dev
```

---

## Environment Variables

### Required

```env
# Security
SECRET_KEY=<random_secret>
JWT_SECRET=<random_secret>

# Database
POSTGRES_PASSWORD=<secure_password>
DATABASE_URL=postgresql://nexus:<password>@postgres:5432/nexus_v2

# Redis
REDIS_PASSWORD=<secure_password>

# OpenAI
OPENAI_API_KEY=sk-...

# Shopify
SHOPIFY_API_KEY=...
SHOPIFY_API_SECRET=...
SHOPIFY_ACCESS_TOKEN=...
```

### Optional

```env
# Email
SMTP_HOST=smtp.gmail.com
SMTP_USER=...
SMTP_PASSWORD=...

# Monitoring
SENTRY_DSN=...

# Storage
S3_ENDPOINT=...
S3_ACCESS_KEY=...
S3_SECRET_KEY=...
```

---

## Monitoring

### Prometheus Metrics

Available at: http://prometheus:9090

**Key metrics:**
- API response times
- Database query performance
- Redis cache hit rate
- Error rates
- Request counts

### Grafana Dashboards

Available at: http://grafana:3001

**Default dashboards:**
- System overview
- API performance
- Database metrics
- User activity

### Logs

```bash
# Backend logs
docker-compose logs -f backend

# Frontend logs
docker-compose logs -f frontend

# All logs
docker-compose logs -f
```

---

## Backups

### Database Backups

```bash
# Manual backup
docker-compose exec postgres pg_dump -U nexus nexus_v2 | gzip > backup_$(date +%Y%m%d).sql.gz

# Automated backups (cron)
0 2 * * * cd /path/to/project && docker-compose exec postgres pg_dump -U nexus nexus_v2 | gzip > backups/backup_$(date +\%Y\%m\%d).sql.gz
```

### Restore

```bash
# Restore from backup
gunzip -c backup_20251111.sql.gz | docker-compose exec -T postgres psql -U nexus -d nexus_v2
```

---

## Scaling

### Horizontal Scaling (Kubernetes)

```yaml
# Increase replicas
replicas: 5  # Scale to 5 pods

# Auto-scaling already configured
# HorizontalPodAutoscaler will scale based on CPU
```

### Vertical Scaling (VPS)

```bash
# Upgrade VPS plan
# - Current: 2 CPU, 4GB RAM
# - Recommended: 4 CPU, 8GB RAM

# Update docker-compose.yml resource limits
```

---

## Security

### Firewall

```bash
# Allow only necessary ports
ufw allow 22    # SSH
ufw allow 80    # HTTP
ufw allow 443   # HTTPS
ufw enable
```

### SSL/TLS

```bash
# Auto-renew certificates
certbot renew --dry-run

# Setup auto-renewal cron
0 0 * * * certbot renew --quiet
```

### Updates

```bash
# Update application
git pull
docker-compose build
docker-compose up -d

# Update system
apt update && apt upgrade -y
```

---

## Health Checks

### Application Health

```bash
# Check backend
curl http://localhost:8000/health

# Check frontend
curl http://localhost:3000

# Check all services
docker-compose ps
```

### Database Health

```bash
# Check PostgreSQL
docker-compose exec postgres pg_isready -U nexus

# Check Redis
docker-compose exec redis redis-cli ping
```

---

## Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose logs service-name

# Restart service
docker-compose restart service-name

# Rebuild service
docker-compose up -d --build service-name
```

### Database Issues

```bash
# Connect to database
docker-compose exec postgres psql -U nexus -d nexus_v2

# Check tables
\dt

# Check connections
SELECT * FROM pg_stat_activity;
```

### Out of Memory

```bash
# Check memory usage
docker stats

# Increase memory limits in docker-compose.yml
# Or upgrade VPS/server
```

---

## CI/CD Pipeline

### GitHub Actions

Automatically triggers on:
- Push to `main` branch
- Pull requests

**Pipeline steps:**
1. Run tests (backend, frontend, NexusLang)
2. Build Docker images
3. Push to registry
4. Deploy to Kubernetes

### Manual Deployment

```bash
# Deploy specific version
kubectl set image deployment/nexuslang-backend \
  backend=nexuslang/backend:v2.0.1 \
  -n nexuslang-v2

# Rollback if needed
kubectl rollout undo deployment/nexuslang-backend -n nexuslang-v2
```

---

## Performance Optimization

### Database

```sql
-- Add indexes for common queries
CREATE INDEX idx_custom ON table_name(column_name);

-- Analyze tables
ANALYZE;

-- Vacuum database
VACUUM ANALYZE;
```

### Redis Caching

```python
# Cache expensive operations
# Already implemented in services
```

### CDN

```bash
# Use Cloudflare for static assets
# Configure in cloudflare dashboard
```

---

## Cost Optimization

### Infrastructure

- **Development:** ~$50/month (single VPS)
- **Production:** ~$300-500/month (Kubernetes cluster)
- **High Traffic:** ~$1000+/month (multi-region)

### API Costs

- **OpenAI:** ~$50-500/month (based on usage)
- **Shopify:** 2.9% + 30¢ per transaction

---

**For questions or issues, check the documentation or create a GitHub issue.**

_Last Updated: November 11, 2025_

