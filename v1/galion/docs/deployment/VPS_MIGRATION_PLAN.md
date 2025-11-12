# VPS MIGRATION PLAN - GALION.APP & GALION.STUDIO
## Complete Migration from AWS to VPS Infrastructure

**Version:** 1.0  
**Date:** November 10, 2025  
**Status:** Ready to Execute  
**Estimated Timeline:** 2-3 weeks  
**Budget:** $80-$150/month (vs $1,480/month AWS)

---

## 🎯 EXECUTIVE SUMMARY

This document provides a complete migration plan to move both **GALION.APP** and **GALION.STUDIO** from AWS managed services to VPS infrastructure.

**Why Migrate to VPS?**
- ✅ **Cost Savings:** 90% reduction ($1,480/month → $80-150/month)
- ✅ **Simplicity:** Single server vs 15+ AWS services
- ✅ **Control:** Full root access, no vendor lock-in
- ✅ **Predictability:** Fixed monthly costs
- ✅ **Performance:** Dedicated resources (no noisy neighbors)
- ✅ **Easy Migration:** Can always move to AWS later if needed

**Trade-offs:**
- ⚠️ Manual scaling (no auto-scaling)
- ⚠️ Self-managed backups
- ⚠️ Single point of failure (until you add redundancy)
- ⚠️ You handle security updates

**Verdict:** For early-stage startup with <1,000 users, VPS is the smart choice.

---

## 📊 CURRENT AWS ARCHITECTURE → VPS MAPPING

### AWS Services → VPS Equivalents

| AWS Service | Current Use | VPS Equivalent | Implementation |
|------------|-------------|----------------|----------------|
| **ECS Fargate** | Container orchestration | Docker + Docker Compose | Same containers, simpler deployment |
| **RDS PostgreSQL** | Database | PostgreSQL 15 (self-hosted) | Direct install or Docker container |
| **ElastiCache Redis** | Cache & sessions | Redis 7 (self-hosted) | Docker container or direct install |
| **S3** | File storage | Local disk + backup to B2/Wasabi | Mounted volumes + cron backups |
| **CloudFront** | CDN | Nginx + Cloudflare | Cloudflare free CDN |
| **ALB** | Load balancer | Nginx reverse proxy | Single Nginx config |
| **Route 53** | DNS | Cloudflare DNS | Free, faster than Route 53 |
| **ACM** | SSL certificates | Let's Encrypt + Certbot | Free, auto-renewing |
| **CloudWatch** | Monitoring | Prometheus + Grafana | Self-hosted or Grafana Cloud (free tier) |
| **Secrets Manager** | Secrets | .env files + encryption | Docker secrets or encrypted files |
| **VPC/Security Groups** | Networking | iptables + UFW firewall | Built-in Linux firewall |

---

## 💰 COST COMPARISON

### Current AWS Plan (Monthly)

| Service | Cost |
|---------|------|
| ECS Fargate (9 tasks) | $165 |
| RDS PostgreSQL (Multi-AZ) | $25 |
| ElastiCache Redis | $25 |
| ALB + CloudFront | $30 |
| S3 Storage (50GB) | $5 |
| NAT Gateway (3×) | $110 |
| Other (Secrets, Logs, etc.) | $30 |
| OpenAI APIs (Whisper, GPT-4) | $55 |
| ElevenLabs TTS | $135 |
| **TOTAL** | **$1,480/month** |

### VPS Plan (Monthly)

| Provider | Plan | Specs | Cost | Recommendation |
|----------|------|-------|------|----------------|
| **Hetzner** | CPX51 | 16 vCPU, 32GB RAM, 360GB NVMe | €46 (~$50) | ✅ **BEST VALUE** |
| **DigitalOcean** | Professional | 16 vCPU, 32GB RAM, 400GB SSD | $168 | Good, but more expensive |
| **Linode** | Dedicated 32GB | 8 CPU, 32GB RAM, 640GB SSD | $145 | Good for CPU-heavy workloads |
| **Vultr** | High Performance | 8 vCPU, 32GB RAM, 256GB NVMe | $120 | Good compromise |
| **OVHcloud** | Advance-4 | 8 vCPU, 32GB RAM, 200GB SSD | $80 | Europe-focused |

**Recommended Setup:**
```yaml
Primary VPS:        Hetzner CPX51 (€46/$50)
  - Both GALION.APP and GALION.STUDIO
  - PostgreSQL, Redis, all services
  - 32GB RAM is enough for 500-1000 users

Backup Storage:     Backblaze B2 (100GB) ($0.50/month)
  - Daily database backups
  - Weekly full backups
  
CDN:                Cloudflare (Free)
  - DNS, SSL, DDoS protection
  - Caching, compression
  
Monitoring:         Grafana Cloud (Free tier)
  - Metrics, logs, alerts
  
APIs:               OpenAI + ElevenLabs ($190/month)
  - Same as AWS plan

TOTAL:              $240/month (84% savings)
```

**Budget Breakdown:**
- VPS: $50/month
- APIs: $190/month
- **Total: $240/month** (vs $1,480 AWS)

---

## 🏗️ VPS ARCHITECTURE

### Single Server Setup (Alpha/Beta - 0-1000 users)

```
┌─────────────────────────────────────────────────────────────┐
│                    VPS Server (Hetzner CPX51)               │
│                   32GB RAM, 16 vCPU, 360GB SSD              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ Nginx Reverse Proxy (Port 80/443)                    │ │
│  │ - galion.app → Frontend (React) + API                │ │
│  │ - studio.galion.app → Studio Frontend + API         │ │
│  │ - SSL/TLS termination (Let's Encrypt)               │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ Docker Compose Stack                                  │ │
│  ├──────────────────────────────────────────────────────┤ │
│  │ • galion-app-api        (Port 8001)  - FastAPI      │ │
│  │ • galion-app-frontend   (Port 3001)  - React        │ │
│  │ • galion-app-voice      (Port 8002)  - Node.js      │ │
│  │                                                       │ │
│  │ • galion-studio-api     (Port 8003)  - FastAPI      │ │
│  │ • galion-studio-frontend (Port 3003) - Next.js      │ │
│  │ • galion-studio-realtime (Port 8004) - Socket.IO    │ │
│  │                                                       │ │
│  │ • postgres              (Port 5432)  - PostgreSQL 15│ │
│  │ • redis                 (Port 6379)  - Redis 7      │ │
│  │ • prometheus            (Port 9090)  - Monitoring   │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ Storage Volumes                                       │ │
│  │ • /data/postgres      (20GB)  - Database files      │ │
│  │ • /data/redis         (2GB)   - Cache data          │ │
│  │ • /data/uploads       (50GB)  - User files          │ │
│  │ • /data/backups       (100GB) - Daily backups       │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
           │
           ├─────────────> Cloudflare CDN (Free)
           │                 - DNS, SSL, caching
           │
           ├─────────────> Backblaze B2 (Backups)
           │                 - Daily DB dumps
           │
           └─────────────> OpenAI + ElevenLabs APIs
                             - Voice services
```

### Scaling Path (1000+ users)

**Option 1: Vertical Scaling (Easier)**
```
Hetzner CPX51 ($50) → CPX61 ($100)
16 vCPU, 32GB RAM → 24 vCPU, 64GB RAM
Handles up to 5,000 users
```

**Option 2: Horizontal Scaling (More resilient)**
```
VPS 1: App Servers (GALION.APP + GALION.STUDIO)
VPS 2: Database (PostgreSQL + Redis) 
VPS 3: Database Replica (Read-only)
Load Balancer: Hetzner Load Balancer ($6/month)
```

**Option 3: Hybrid (Best of both)**
```
VPS: Web servers + Redis
Managed DB: Hetzner Managed PostgreSQL ($20/month)
CDN: Cloudflare (Free)
Cost: $70/month, 99.9% uptime SLA
```

---

## 🚀 MIGRATION STEPS

### Phase 1: VPS Setup (Week 1)

#### Day 1: Provision VPS

**1.1 Create Hetzner Account**
```bash
# Go to: https://www.hetzner.com/cloud
# Choose: CPX51 (32GB RAM)
# Region: Choose closest to your users (US: Ashburn, EU: Helsinki)
# OS: Ubuntu 22.04 LTS
```

**1.2 Initial Server Setup**
```bash
# SSH into your VPS
ssh root@YOUR_VPS_IP

# Update system
apt update && apt upgrade -y

# Set timezone
timedatectl set-timezone America/New_York  # or your timezone

# Create non-root user
adduser deploy
usermod -aG sudo deploy
usermod -aG docker deploy

# Copy SSH keys to deploy user
rsync --archive --chown=deploy:deploy ~/.ssh /home/deploy

# Configure SSH (disable root login)
nano /etc/ssh/sshd_config
# Set: PermitRootLogin no
# Set: PasswordAuthentication no
systemctl restart sshd
```

**1.3 Install Required Software**
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose-plugin -y

# Install Nginx
apt install nginx -y

# Install Certbot (SSL certificates)
apt install certbot python3-certbot-nginx -y

# Install monitoring tools
apt install htop iotop nethogs ncdu -y

# Install PostgreSQL client (for management)
apt install postgresql-client-15 -y

# Install fail2ban (security)
apt install fail2ban -y
```

**1.4 Configure Firewall**
```bash
# Install UFW (Uncomplicated Firewall)
apt install ufw -y

# Allow SSH (IMPORTANT: Do this first!)
ufw allow 22/tcp

# Allow HTTP and HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Enable firewall
ufw enable

# Check status
ufw status verbose
```

#### Day 2: Set Up Docker Environment

**2.1 Create Directory Structure**
```bash
# Switch to deploy user
su - deploy

# Create project directories
mkdir -p /home/deploy/galion
cd /home/deploy/galion

mkdir -p {app,studio,data,backups,nginx}
mkdir -p data/{postgres,redis,uploads,logs}
mkdir -p nginx/{conf.d,ssl}

# Set permissions
sudo chown -R deploy:deploy /home/deploy/galion
chmod -R 755 /home/deploy/galion
```

**2.2 Create Docker Compose Configuration**

Create `/home/deploy/galion/docker-compose.yml`:

```yaml
version: '3.8'

services:
  # ==================== SHARED SERVICES ====================
  
  postgres:
    image: postgres:15-alpine
    container_name: galion-postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: galion
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: galion
    volumes:
      - ./data/postgres:/var/lib/postgresql/data
      - ./backups:/backups
    ports:
      - "127.0.0.1:5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U galion"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: galion-redis
    restart: unless-stopped
    command: redis-server --requirepass ${REDIS_PASSWORD} --maxmemory 2gb --maxmemory-policy allkeys-lru
    volumes:
      - ./data/redis:/data
    ports:
      - "127.0.0.1:6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  # ==================== GALION.APP ====================
  
  app-api:
    build:
      context: ./app/backend
      dockerfile: Dockerfile
    container_name: galion-app-api
    restart: unless-stopped
    environment:
      DATABASE_URL: postgresql://galion:${POSTGRES_PASSWORD}@postgres:5432/galion
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379/0
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      ELEVENLABS_API_KEY: ${ELEVENLABS_API_KEY}
      JWT_SECRET: ${JWT_SECRET}
      ENVIRONMENT: production
    volumes:
      - ./data/uploads:/app/uploads
      - ./data/logs:/app/logs
    ports:
      - "127.0.0.1:8001:8000"
    depends_on:
      - postgres
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  app-frontend:
    build:
      context: ./app/frontend
      dockerfile: Dockerfile
    container_name: galion-app-frontend
    restart: unless-stopped
    environment:
      VITE_API_URL: https://api.galion.app
      VITE_WS_URL: wss://api.galion.app
    ports:
      - "127.0.0.1:3001:3000"
    depends_on:
      - app-api

  app-voice:
    build:
      context: ./app/voice-service
      dockerfile: Dockerfile
    container_name: galion-app-voice
    restart: unless-stopped
    environment:
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      ELEVENLABS_API_KEY: ${ELEVENLABS_API_KEY}
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379/1
    volumes:
      - ./data/uploads:/app/audio
    ports:
      - "127.0.0.1:8002:8000"
    depends_on:
      - redis

  # ==================== GALION.STUDIO ====================
  
  studio-api:
    build:
      context: ./studio/backend
      dockerfile: Dockerfile
    container_name: galion-studio-api
    restart: unless-stopped
    environment:
      DATABASE_URL: postgresql://galion:${POSTGRES_PASSWORD}@postgres:5432/galion_studio
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379/2
      JWT_SECRET: ${JWT_SECRET}
      ENVIRONMENT: production
    volumes:
      - ./data/uploads:/app/uploads
      - ./data/logs:/app/logs
    ports:
      - "127.0.0.1:8003:8000"
    depends_on:
      - postgres
      - redis

  studio-frontend:
    build:
      context: ./studio/frontend
      dockerfile: Dockerfile
    container_name: galion-studio-frontend
    restart: unless-stopped
    environment:
      NEXT_PUBLIC_API_URL: https://api.studio.galion.app
      NEXT_PUBLIC_WS_URL: wss://api.studio.galion.app
    ports:
      - "127.0.0.1:3003:3000"
    depends_on:
      - studio-api

  studio-realtime:
    build:
      context: ./studio/realtime-service
      dockerfile: Dockerfile
    container_name: galion-studio-realtime
    restart: unless-stopped
    environment:
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379/3
      DATABASE_URL: postgresql://galion:${POSTGRES_PASSWORD}@postgres:5432/galion_studio
    ports:
      - "127.0.0.1:8004:8000"
    depends_on:
      - redis
      - postgres

  # ==================== MONITORING ====================
  
  prometheus:
    image: prom/prometheus:latest
    container_name: galion-prometheus
    restart: unless-stopped
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - ./data/prometheus:/prometheus
    ports:
      - "127.0.0.1:9090:9090"
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'

volumes:
  postgres_data:
  redis_data:
  uploads:
  logs:
  prometheus_data:

networks:
  default:
    name: galion-network
```

**2.3 Create Environment Variables**

Create `/home/deploy/galion/.env`:

```bash
# Database
POSTGRES_PASSWORD=GENERATE_STRONG_PASSWORD_HERE
POSTGRES_USER=galion

# Redis
REDIS_PASSWORD=GENERATE_STRONG_PASSWORD_HERE

# JWT
JWT_SECRET=GENERATE_STRONG_SECRET_HERE

# OpenAI
OPENAI_API_KEY=sk-your-openai-key-here

# ElevenLabs
ELEVENLABS_API_KEY=your-elevenlabs-key-here

# Environment
ENVIRONMENT=production
```

**Generate strong passwords:**
```bash
# Generate passwords
openssl rand -base64 32  # For POSTGRES_PASSWORD
openssl rand -base64 32  # For REDIS_PASSWORD
openssl rand -base64 64  # For JWT_SECRET

# Save to .env file
nano /home/deploy/galion/.env
```

#### Day 3: Configure Nginx

**3.1 Main Nginx Configuration**

Create `/etc/nginx/nginx.conf`:

```nginx
user www-data;
worker_processes auto;
pid /run/nginx.pid;
include /etc/nginx/modules-enabled/*.conf;

events {
    worker_connections 4096;
    use epoll;
    multi_accept on;
}

http {
    # Basic Settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    server_tokens off;
    
    # Buffer Sizes (prevent buffer overflow attacks)
    client_body_buffer_size 128k;
    client_max_body_size 100M;  # For file uploads
    client_header_buffer_size 1k;
    large_client_header_buffers 4 32k;
    
    # Timeouts
    client_body_timeout 12;
    client_header_timeout 12;
    send_timeout 10;
    
    # MIME types
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    # Logging
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log warn;
    
    # Gzip Compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript 
               application/json application/javascript application/xml+rss 
               application/rss+xml font/truetype font/opentype 
               application/vnd.ms-fontobject image/svg+xml;
    gzip_disable "msie6";
    
    # Rate Limiting (DDoS protection)
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/m;
    limit_req_zone $binary_remote_addr zone=general_limit:10m rate=200r/m;
    
    # Connection Limiting
    limit_conn_zone $binary_remote_addr zone=addr:10m;
    limit_conn addr 10;
    
    # Include site configurations
    include /etc/nginx/conf.d/*.conf;
    include /etc/nginx/sites-enabled/*;
}
```

**3.2 GALION.APP Configuration**

Create `/etc/nginx/sites-available/galion-app`:

```nginx
# Redirect HTTP to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name galion.app www.galion.app;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS - Frontend
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name galion.app www.galion.app;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/galion.app/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/galion.app/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Logging
    access_log /var/log/nginx/galion-app-access.log;
    error_log /var/log/nginx/galion-app-error.log;
    
    # Frontend (React)
    location / {
        proxy_pass http://127.0.0.1:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}

# HTTPS - API
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name api.galion.app;
    
    # SSL Configuration (same as above)
    ssl_certificate /etc/letsencrypt/live/galion.app/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/galion.app/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    
    # Rate Limiting
    limit_req zone=api_limit burst=20 nodelay;
    
    # API (FastAPI)
    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # CORS (if needed)
        add_header 'Access-Control-Allow-Origin' 'https://galion.app' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type' always;
    }
    
    # WebSocket for voice
    location /ws {
        proxy_pass http://127.0.0.1:8002;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }
}
```

**3.3 GALION.STUDIO Configuration**

Create `/etc/nginx/sites-available/galion-studio`:

```nginx
# Redirect HTTP to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name studio.galion.app;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS - Frontend
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name studio.galion.app;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/studio.galion.app/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/studio.galion.app/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    
    # Frontend (Next.js)
    location / {
        proxy_pass http://127.0.0.1:3003;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# HTTPS - API
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name api.studio.galion.app;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/studio.galion.app/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/studio.galion.app/privkey.pem;
    
    # Rate Limiting
    limit_req zone=api_limit burst=20 nodelay;
    
    # API
    location / {
        proxy_pass http://127.0.0.1:8003;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    # WebSocket for real-time collaboration
    location /socket.io {
        proxy_pass http://127.0.0.1:8004;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }
}
```

**3.4 Enable Sites**
```bash
# Enable configurations
sudo ln -s /etc/nginx/sites-available/galion-app /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/galion-studio /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

#### Day 4: SSL Certificates

**4.1 Get SSL Certificates**
```bash
# For galion.app and api.galion.app
sudo certbot --nginx -d galion.app -d www.galion.app -d api.galion.app

# For studio.galion.app and api.studio.galion.app
sudo certbot --nginx -d studio.galion.app -d api.studio.galion.app

# Auto-renewal (cron job)
sudo certbot renew --dry-run

# Set up auto-renewal
sudo crontab -e
# Add: 0 0 * * * certbot renew --quiet --nginx
```

#### Day 5: DNS Configuration

**5.1 Configure Cloudflare**

Go to Cloudflare Dashboard → DNS:

```
# GALION.APP
A       galion.app              →  YOUR_VPS_IP  (Proxied: ON)
A       www.galion.app          →  YOUR_VPS_IP  (Proxied: ON)
A       api.galion.app          →  YOUR_VPS_IP  (Proxied: ON)

# GALION.STUDIO
A       studio.galion.app       →  YOUR_VPS_IP  (Proxied: ON)
A       api.studio.galion.app   →  YOUR_VPS_IP  (Proxied: ON)
```

**5.2 Cloudflare Settings**
- SSL/TLS Mode: **Full (strict)**
- Always Use HTTPS: **ON**
- Auto Minify: JS, CSS, HTML → **ON**
- Brotli Compression: **ON**
- HTTP/2 to Origin: **ON**
- WebSockets: **ON**
- Caching Level: **Standard**

---

### Phase 2: Deploy Applications (Week 2)

#### Day 6: Deploy Database

**6.1 Create Databases**
```bash
cd /home/deploy/galion

# Start PostgreSQL
docker compose up -d postgres

# Wait for it to be ready
docker compose logs -f postgres

# Create databases
docker compose exec postgres psql -U galion -c "CREATE DATABASE galion;"
docker compose exec postgres psql -U galion -c "CREATE DATABASE galion_studio;"

# Verify
docker compose exec postgres psql -U galion -l
```

**6.2 Run Migrations**
```bash
# GALION.APP migrations
docker compose run --rm app-api alembic upgrade head

# GALION.STUDIO migrations
docker compose run --rm studio-api alembic upgrade head
```

#### Day 7-8: Deploy Backend Services

**7.1 Build and Deploy**
```bash
cd /home/deploy/galion

# Build all services
docker compose build

# Start services one by one
docker compose up -d redis
docker compose up -d postgres
docker compose up -d app-api
docker compose up -d app-voice
docker compose up -d studio-api
docker compose up -d studio-realtime

# Check logs
docker compose logs -f app-api
```

**7.2 Health Checks**
```bash
# Check API health
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
curl http://localhost:8004/health

# Check database connection
docker compose exec app-api python -c "from app.db import engine; print(engine.execute('SELECT 1').scalar())"
```

#### Day 9-10: Deploy Frontend

**9.1 Build Frontends**
```bash
# Build and start frontends
docker compose up -d app-frontend
docker compose up -d studio-frontend

# Check logs
docker compose logs -f app-frontend
docker compose logs -f studio-frontend
```

**9.2 Test Full Stack**
```bash
# Test GALION.APP
curl https://galion.app
curl https://api.galion.app/health

# Test GALION.STUDIO
curl https://studio.galion.app
curl https://api.studio.galion.app/health
```

---

### Phase 3: Backups & Monitoring (Week 3)

#### Day 11: Set Up Backups

**11.1 Database Backup Script**

Create `/home/deploy/galion/scripts/backup.sh`:

```bash
#!/bin/bash
# Daily backup script for GALION databases

set -e

# Configuration
BACKUP_DIR="/home/deploy/galion/backups"
DATE=$(date +%Y%m%d_%H%M%S)
POSTGRES_CONTAINER="galion-postgres"
RETENTION_DAYS=30

# Create backup directory
mkdir -p "$BACKUP_DIR"

echo "Starting backup: $DATE"

# Backup GALION.APP database
echo "Backing up galion database..."
docker exec $POSTGRES_CONTAINER pg_dump -U galion -Fc galion > "$BACKUP_DIR/galion_${DATE}.dump"

# Backup GALION.STUDIO database
echo "Backing up galion_studio database..."
docker exec $POSTGRES_CONTAINER pg_dump -U galion -Fc galion_studio > "$BACKUP_DIR/galion_studio_${DATE}.dump"

# Compress backups
echo "Compressing backups..."
gzip "$BACKUP_DIR/galion_${DATE}.dump"
gzip "$BACKUP_DIR/galion_studio_${DATE}.dump"

# Upload to Backblaze B2 (optional)
if [ -n "$B2_BUCKET" ]; then
    echo "Uploading to Backblaze B2..."
    b2 upload-file $B2_BUCKET "$BACKUP_DIR/galion_${DATE}.dump.gz" "backups/galion_${DATE}.dump.gz"
    b2 upload-file $B2_BUCKET "$BACKUP_DIR/galion_studio_${DATE}.dump.gz" "backups/galion_studio_${DATE}.dump.gz"
fi

# Clean up old backups (keep last 30 days)
echo "Cleaning up old backups..."
find "$BACKUP_DIR" -name "*.dump.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completed: $DATE"
```

Make it executable:
```bash
chmod +x /home/deploy/galion/scripts/backup.sh
```

**11.2 Set Up Cron Job**
```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /home/deploy/galion/scripts/backup.sh >> /home/deploy/galion/logs/backup.log 2>&1
```

**11.3 Test Backup & Restore**
```bash
# Run backup
./scripts/backup.sh

# Test restore (to test database)
docker exec -i galion-postgres psql -U galion -c "CREATE DATABASE test_restore;"
gunzip -c backups/galion_20251110_020000.dump.gz | docker exec -i galion-postgres pg_restore -U galion -d test_restore
```

#### Day 12: Monitoring Setup

**12.1 Prometheus Configuration**

Create `/home/deploy/galion/monitoring/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  # Prometheus itself
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # Node Exporter (system metrics)
  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']

  # Docker metrics
  - job_name: 'docker'
    static_configs:
      - targets: ['docker-exporter:9323']

  # GALION.APP API
  - job_name: 'app-api'
    static_configs:
      - targets: ['app-api:8000']
    metrics_path: '/metrics'

  # GALION.STUDIO API
  - job_name: 'studio-api'
    static_configs:
      - targets: ['studio-api:8000']
    metrics_path: '/metrics'

  # PostgreSQL
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  # Redis
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
```

**12.2 Add Monitoring Containers**

Add to `docker-compose.yml`:

```yaml
  # Node Exporter (system metrics)
  node-exporter:
    image: prom/node-exporter:latest
    container_name: node-exporter
    restart: unless-stopped
    ports:
      - "127.0.0.1:9100:9100"
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro

  # Postgres Exporter
  postgres-exporter:
    image: prometheuscommunity/postgres-exporter:latest
    container_name: postgres-exporter
    restart: unless-stopped
    environment:
      DATA_SOURCE_NAME: "postgresql://galion:${POSTGRES_PASSWORD}@postgres:5432/galion?sslmode=disable"
    ports:
      - "127.0.0.1:9187:9187"
    depends_on:
      - postgres

  # Redis Exporter
  redis-exporter:
    image: oliver006/redis_exporter:latest
    container_name: redis-exporter
    restart: unless-stopped
    environment:
      REDIS_ADDR: "redis:6379"
      REDIS_PASSWORD: ${REDIS_PASSWORD}
    ports:
      - "127.0.0.1:9121:9121"
    depends_on:
      - redis
```

**12.3 Grafana Cloud Setup (Free Tier)**

```bash
# Sign up at: https://grafana.com/auth/sign-up/create-user
# Create free account (10k series, 50GB logs, 50GB traces)

# Get Prometheus Remote Write URL and credentials
# Add to prometheus.yml:

remote_write:
  - url: https://prometheus-prod-XX-prod-us-central-0.grafana.net/api/prom/push
    basic_auth:
      username: YOUR_USERNAME
      password: YOUR_PASSWORD
```

#### Day 13: Alerts & Notifications

**13.1 Create Alert Rules**

Create `/home/deploy/galion/monitoring/alerts.yml`:

```yaml
groups:
  - name: galion_alerts
    interval: 30s
    rules:
      # High CPU usage
      - alert: HighCPUUsage
        expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage detected"
          description: "CPU usage is above 80% for more than 5 minutes"

      # High memory usage
      - alert: HighMemoryUsage
        expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100 > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage detected"
          description: "Memory usage is above 85%"

      # Disk space low
      - alert: DiskSpaceLow
        expr: (node_filesystem_avail_bytes / node_filesystem_size_bytes) * 100 < 15
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Disk space running low"
          description: "Less than 15% disk space available"

      # API down
      - alert: APIDown
        expr: up{job=~"app-api|studio-api"} == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "API is down"
          description: "{{ $labels.job }} has been down for more than 2 minutes"

      # Database down
      - alert: DatabaseDown
        expr: up{job="postgres"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "PostgreSQL is down"
          description: "Database has been unreachable for more than 1 minute"

      # High error rate
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
          description: "More than 5% of requests are returning 5xx errors"
```

**13.2 Set Up Email/Slack Notifications**

Using Grafana Cloud for alerts is easiest. Alternatively, use Alertmanager:

Add to `docker-compose.yml`:

```yaml
  alertmanager:
    image: prom/alertmanager:latest
    container_name: alertmanager
    restart: unless-stopped
    volumes:
      - ./monitoring/alertmanager.yml:/etc/alertmanager/alertmanager.yml
    ports:
      - "127.0.0.1:9093:9093"
```

Create `/home/deploy/galion/monitoring/alertmanager.yml`:

```yaml
global:
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'alerts@galion.app'
  smtp_auth_username: 'your-email@gmail.com'
  smtp_auth_password: 'your-app-password'

route:
  receiver: 'email-notifications'
  group_by: ['alertname', 'severity']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h

receivers:
  - name: 'email-notifications'
    email_configs:
      - to: 'admin@galion.app'
        headers:
          Subject: '[ALERT] {{ .GroupLabels.alertname }}'

  - name: 'slack-notifications'
    slack_configs:
      - api_url: 'YOUR_SLACK_WEBHOOK_URL'
        channel: '#alerts'
        title: '[{{ .Status }}] {{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
```

#### Day 14: Log Management

**14.1 Centralized Logging**

Add Loki + Promtail for log aggregation:

```yaml
  loki:
    image: grafana/loki:latest
    container_name: loki
    restart: unless-stopped
    ports:
      - "127.0.0.1:3100:3100"
    volumes:
      - ./monitoring/loki-config.yml:/etc/loki/local-config.yaml
      - ./data/loki:/loki

  promtail:
    image: grafana/promtail:latest
    container_name: promtail
    restart: unless-stopped
    volumes:
      - /var/log:/var/log:ro
      - ./data/logs:/app/logs:ro
      - ./monitoring/promtail-config.yml:/etc/promtail/config.yml
    command: -config.file=/etc/promtail/config.yml
    depends_on:
      - loki
```

---

## 🔒 SECURITY HARDENING

### 1. SSH Security

```bash
# Disable password authentication
sudo nano /etc/ssh/sshd_config
# Set: PasswordAuthentication no
# Set: PermitRootLogin no
# Set: PubkeyAuthentication yes

# Restart SSH
sudo systemctl restart sshd

# Install fail2ban (auto-ban brute force attempts)
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 2. Firewall Configuration

```bash
# Configure UFW
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# Check status
sudo ufw status verbose
```

### 3. Docker Security

```bash
# Run containers as non-root user
# Add to Dockerfile:
USER node  # or USER 1000:1000

# Limit container resources
# Add to docker-compose.yml:
services:
  app-api:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

### 4. Database Security

```bash
# Strong password (already done via .env)
# Limited network access (127.0.0.1 only)
# Regular backups (automated via cron)

# PostgreSQL hardening
docker compose exec postgres psql -U galion -c "ALTER SYSTEM SET log_connections = 'on';"
docker compose exec postgres psql -U galion -c "ALTER SYSTEM SET log_disconnections = 'on';"
docker compose exec postgres psql -U galion -c "ALTER SYSTEM SET log_statement = 'all';"
```

### 5. Application Security

**Add Rate Limiting to FastAPI:**

```python
# app/middleware/rate_limit.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

# In main.py
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Use in routes
@app.get("/api/endpoint")
@limiter.limit("100/minute")
async def endpoint(request: Request):
    return {"message": "OK"}
```

---

## 📊 PERFORMANCE OPTIMIZATION

### 1. PostgreSQL Tuning

Create `/home/deploy/galion/postgres/postgresql.conf`:

```conf
# Memory (for 32GB RAM server)
shared_buffers = 8GB
effective_cache_size = 24GB
maintenance_work_mem = 2GB
work_mem = 64MB

# Checkpoints
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100

# Connections
max_connections = 200

# Logging
log_min_duration_statement = 1000  # Log queries > 1 second
```

Mount in docker-compose.yml:

```yaml
  postgres:
    volumes:
      - ./postgres/postgresql.conf:/etc/postgresql/postgresql.conf:ro
    command: postgres -c config_file=/etc/postgresql/postgresql.conf
```

### 2. Redis Tuning

```yaml
  redis:
    command: >
      redis-server
      --requirepass ${REDIS_PASSWORD}
      --maxmemory 4gb
      --maxmemory-policy allkeys-lru
      --appendonly yes
      --save 900 1
      --save 300 10
      --save 60 10000
```

### 3. Nginx Caching

Add to Nginx configuration:

```nginx
# Cache configuration
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m max_size=1g inactive=60m use_temp_path=off;

server {
    # ... existing config ...
    
    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Cache API responses (cautiously)
    location /api/public/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_cache api_cache;
        proxy_cache_valid 200 10m;
        proxy_cache_key "$request_uri";
        add_header X-Cache-Status $upstream_cache_status;
    }
}
```

---

## 🚦 CI/CD FOR VPS

### GitHub Actions Workflow

Create `.github/workflows/deploy-vps.yml`:

```yaml
name: Deploy to VPS

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Set up SSH
        uses: webfactory/ssh-agent@v0.8.0
        with:
          ssh-private-key: ${{ secrets.VPS_SSH_KEY }}
      
      - name: Deploy to VPS
        run: |
          ssh -o StrictHostKeyChecking=no deploy@${{ secrets.VPS_IP }} << 'EOF'
            set -e
            
            # Navigate to project directory
            cd /home/deploy/galion
            
            # Pull latest code
            git pull origin main
            
            # Rebuild containers
            docker compose build
            
            # Restart services with zero downtime
            docker compose up -d --no-deps --build app-api
            docker compose up -d --no-deps --build app-frontend
            docker compose up -d --no-deps --build studio-api
            docker compose up -d --no-deps --build studio-frontend
            
            # Wait for health checks
            sleep 10
            
            # Verify deployment
            curl -f http://localhost:8001/health || exit 1
            curl -f http://localhost:8003/health || exit 1
            
            echo "Deployment successful!"
          EOF
      
      - name: Notify Slack
        if: always()
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

---

## 📋 MIGRATION CHECKLIST

### Pre-Migration
```yaml
□ Purchase VPS (Hetzner CPX51 recommended)
□ Set up Cloudflare account
□ Generate strong passwords for database, Redis, JWT
□ Back up existing AWS data (if applicable)
□ Test deployment locally with Docker Compose
□ Document all API keys (OpenAI, ElevenLabs)
```

### Week 1: Infrastructure
```yaml
□ Day 1: Provision VPS, initial setup, firewall
□ Day 2: Install Docker, Nginx, Certbot
□ Day 3: Configure Nginx reverse proxy
□ Day 4: Get SSL certificates from Let's Encrypt
□ Day 5: Configure Cloudflare DNS
```

### Week 2: Deployment
```yaml
□ Day 6: Deploy PostgreSQL, create databases
□ Day 7-8: Deploy backend services (APIs, voice)
□ Day 9-10: Deploy frontends (React, Next.js)
```

### Week 3: Operations
```yaml
□ Day 11: Set up automated backups
□ Day 12: Configure monitoring (Prometheus)
□ Day 13: Set up alerts (email, Slack)
□ Day 14: Test disaster recovery
```

### Post-Migration
```yaml
□ Test all features end-to-end
□ Load test with 100 concurrent users
□ Monitor for 7 days
□ Document runbooks
□ Shut down AWS resources (save money!)
```

---

## 🆘 TROUBLESHOOTING

### Common Issues

**1. "Connection refused" errors**
```bash
# Check if services are running
docker compose ps

# Check logs
docker compose logs app-api

# Verify ports
sudo netstat -tulpn | grep -E '(8001|8002|8003|8004|3001|3003)'
```

**2. "502 Bad Gateway" from Nginx**
```bash
# Check upstream services
curl http://localhost:8001/health

# Check Nginx error log
sudo tail -f /var/log/nginx/error.log

# Restart Nginx
sudo systemctl restart nginx
```

**3. Database connection errors**
```bash
# Check PostgreSQL status
docker compose logs postgres

# Test connection
docker compose exec postgres psql -U galion -c "SELECT 1;"

# Check password in .env
cat .env | grep POSTGRES_PASSWORD
```

**4. Out of memory**
```bash
# Check memory usage
free -h
docker stats

# Restart memory-hungry services
docker compose restart app-api
```

**5. Disk space full**
```bash
# Check disk usage
df -h

# Clean up Docker
docker system prune -a --volumes -f

# Clean up logs
sudo journalctl --vacuum-time=7d
```

---

## 📞 SUPPORT & RESOURCES

### Documentation
- Docker: https://docs.docker.com/
- Nginx: https://nginx.org/en/docs/
- Let's Encrypt: https://letsencrypt.org/docs/
- Hetzner: https://docs.hetzner.com/
- Cloudflare: https://developers.cloudflare.com/

### Monitoring Dashboards
- Server: `http://YOUR_VPS_IP:9090` (Prometheus)
- Grafana: https://grafana.com (Grafana Cloud)

### Backup Locations
- Local: `/home/deploy/galion/backups`
- Remote: Backblaze B2 bucket (if configured)

---

## ✅ SUCCESS METRICS

### After Migration
- **Uptime:** >99.5% (measure with UptimeRobot)
- **Response Time:** <200ms API, <1s page load
- **Cost:** <$250/month (vs $1,480 AWS)
- **Deployment Time:** <5 minutes (CI/CD)
- **Backup Success Rate:** 100% (daily backups)

---

## 🎉 CONCLUSION

You now have a complete VPS migration plan that will:
- ✅ Save 84% on infrastructure costs ($1,480 → $240/month)
- ✅ Simplify your stack (1 server vs 15+ AWS services)
- ✅ Give you full control (root access, no vendor lock-in)
- ✅ Maintain performance (dedicated resources)
- ✅ Ensure reliability (automated backups, monitoring, alerts)

**Next Steps:**
1. Purchase Hetzner CPX51 VPS today
2. Follow Day 1-14 migration steps
3. Launch both GALION.APP and GALION.STUDIO
4. Monitor, iterate, scale

**Questions? Issues?**
- Open GitHub issue
- Email: support@galion.app
- Discord: https://discord.gg/galion

---

**Built with ⚡ Elon Musk's First Principles ⚡**

**Simplify → Control → Ship → Scale**

**Document Version:** 1.0  
**Last Updated:** November 10, 2025  
**Status:** READY TO EXECUTE

**LET'S MIGRATE!** 🚀🔥

