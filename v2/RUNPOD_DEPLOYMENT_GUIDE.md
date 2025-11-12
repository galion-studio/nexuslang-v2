# NexusLang v2 - RunPod Deployment Guide

**Last Updated:** November 11, 2025  
**Platform:** RunPod GPU Cloud  
**Best For:** AI/ML workloads with GPU acceleration

---

## Why RunPod?

RunPod is perfect for NexusLang v2 because:
- ✅ GPU acceleration for Whisper (STT) and TTS models
- ✅ Affordable GPU instances ($0.20-0.50/hour)
- ✅ Easy deployment with Docker
- ✅ Persistent storage for databases
- ✅ Port forwarding for web access
- ✅ SSH access for management

---

## Prerequisites

1. **RunPod Account**
   - Sign up at https://runpod.io
   - Add payment method
   - Minimum $10 credit recommended

2. **Local Tools**
   - SSH client
   - Git
   - Text editor

---

## Step-by-Step Deployment

### Step 1: Create RunPod Pod

1. **Go to RunPod Console**
   - Visit https://www.runpod.io/console/pods
   - Click "Deploy" or "Create Pod"

2. **Select GPU (Recommended)**
   - **For Development:** RTX 3070 ($0.29/hour)
   - **For Production:** RTX 4090 ($0.69/hour) or A40 ($0.79/hour)
   - **Budget Option:** No GPU ($0.20/hour) - STT/TTS will be slower

3. **Choose Template**
   - Select "RunPod PyTorch" or "Ubuntu + CUDA"
   - Or use custom Docker image

4. **Configure Pod**
   - **Container Disk:** 50 GB minimum
   - **Volume Disk:** 100 GB (for database and files)
   - **Exposed Ports:** 
     - 3000 (Frontend)
     - 8000 (Backend API)
     - 5432 (PostgreSQL - optional, for external access)

5. **Deploy Pod**
   - Click "Deploy On-Demand" or "Deploy Spot" (cheaper)
   - Wait for pod to start (~2-3 minutes)

---

### Step 2: Connect to Pod

1. **Get Connection Info**
   - In RunPod console, click on your pod
   - Note the SSH connection string
   - Example: `ssh root@ssh.runpod.io -p 12345 -i ~/.ssh/id_ed25519`

2. **Connect via SSH**
   ```bash
   ssh root@ssh.runpod.io -p YOUR_PORT
   ```

3. **Verify GPU (if using GPU pod)**
   ```bash
   nvidia-smi
   ```

---

### Step 3: Install Dependencies

```bash
# Update system
apt-get update && apt-get upgrade -y

# Install Docker Compose
apt-get install -y docker-compose

# Install Git (if not present)
apt-get install -y git curl

# Verify installations
docker --version
docker-compose --version
git --version
```

---

### Step 4: Clone Repository

```bash
# Clone your repository
cd /workspace
git clone https://github.com/your-org/project-nexus.git
cd project-nexus

# Or upload files via SCP
# scp -P YOUR_PORT -r ./project-nexus root@ssh.runpod.io:/workspace/
```

---

### Step 5: Configure Environment

```bash
# Copy RunPod-specific configuration
cp docker-compose.runpod.yml docker-compose.yml

# Create environment file
cat > .env << 'EOF'
# Database Configuration
POSTGRES_PASSWORD=runpod_secure_password_change_me
POSTGRES_USER=nexus
POSTGRES_DB=nexus_v2
DATABASE_URL=postgresql+asyncpg://nexus:runpod_secure_password_change_me@postgres:5432/nexus_v2

# Redis Configuration
REDIS_PASSWORD=redis_secure_password_change_me
REDIS_URL=redis://:redis_secure_password_change_me@redis:6379

# Security Keys (Generate unique values!)
SECRET_KEY=your_secret_key_min_32_characters_change_me
JWT_SECRET=your_jwt_secret_min_64_characters_change_me_for_production

# AI API Keys (Optional but recommended)
OPENAI_API_KEY=sk-your-openai-api-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here

# Whisper Configuration (GPU acceleration)
WHISPER_MODEL=base
WHISPER_DEVICE=cuda

# TTS Configuration (GPU acceleration)
TTS_MODEL=tts_models/en/ljspeech/tacotron2-DDC
TTS_DEVICE=cuda

# Application URLs (RunPod provides these)
FRONTEND_URL=https://YOUR_POD_ID-3000.proxy.runpod.net
BACKEND_URL=https://YOUR_POD_ID-8000.proxy.runpod.net
EOF

# Generate secure keys
echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env
echo "JWT_SECRET=$(openssl rand -hex 64)" >> .env
```

---

### Step 6: Deploy Services

```bash
# Pull images (if using pre-built)
docker-compose pull

# Start all services
docker-compose up -d

# Wait for services to start (30-60 seconds)
sleep 30

# Check status
docker-compose ps

# Expected output:
# NAME                STATUS              PORTS
# postgres            Up                  5432/tcp
# redis               Up                  6379/tcp
# backend             Up                  8000/tcp
# frontend            Up                  3000/tcp
```

---

### Step 7: Initialize Database

```bash
# Wait for PostgreSQL to be ready
until docker-compose exec postgres pg_isready; do
  echo "Waiting for PostgreSQL..."
  sleep 2
done

# Create database and tables
docker-compose exec postgres psql -U nexus -d nexus_v2 << 'EOF'
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create tables (simplified - full schema in v2/database/schemas/init.sql)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- More tables created automatically by backend on first run
EOF

echo "✅ Database initialized!"
```

---

### Step 8: Get Access URLs

**RunPod provides automatic port forwarding!**

1. **In RunPod Console:**
   - Click on your pod
   - Find "Connect" section
   - Look for "HTTP Services"

2. **Your URLs will be:**
   ```
   Frontend: https://YOUR_POD_ID-3000.proxy.runpod.net
   Backend:  https://YOUR_POD_ID-8000.proxy.runpod.net
   ```

3. **Test Access:**
   ```bash
   # Get your pod ID from RunPod console
   POD_ID="your-pod-id-here"
   
   # Test backend
   curl https://${POD_ID}-8000.proxy.runpod.net/health
   
   # Should return: {"status":"healthy","service":"nexuslang-v2-api","version":"2.0.0-beta"}
   ```

---

### Step 9: Configure Frontend

```bash
# Update frontend environment
docker-compose exec frontend sh -c "cat > .env.local << 'EOF'
NEXT_PUBLIC_API_URL=https://YOUR_POD_ID-8000.proxy.runpod.net
EOF"

# Restart frontend to apply changes
docker-compose restart frontend
```

---

### Step 10: Verify Everything Works

```bash
# Check all services
docker-compose ps

# Check logs
docker-compose logs --tail=50

# Test backend health
curl https://YOUR_POD_ID-8000.proxy.runpod.net/health

# Test API docs
echo "API Docs: https://YOUR_POD_ID-8000.proxy.runpod.net/docs"

# Test frontend
echo "Frontend: https://YOUR_POD_ID-3000.proxy.runpod.net"
```

**Open the frontend URL in your browser - you should see the landing page!**

---

## RunPod-Specific Optimizations

### GPU Acceleration

Your `.env` file already enables GPU for:
- **Whisper (STT):** `WHISPER_DEVICE=cuda`
- **TTS:** `TTS_DEVICE=cuda`

This gives you:
- **10-30x faster** speech recognition
- **5-10x faster** speech synthesis
- Real-time voice processing

### Persistent Storage

```bash
# Mount RunPod volume for persistence
# In docker-compose.runpod.yml:
volumes:
  postgres-data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /workspace/postgres-data

  redis-data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /workspace/redis-data
```

### Auto-Restart

```bash
# Keep services running even if pod restarts
docker-compose up -d --restart unless-stopped
```

---

## Managing Your RunPod Deployment

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend

# Last 100 lines
docker-compose logs --tail=100
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend

# Full rebuild
docker-compose down
docker-compose up -d --build
```

### Update Code

```bash
# Pull latest changes
cd /workspace/project-nexus
git pull

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

### Backup Data

```bash
# Backup PostgreSQL
docker-compose exec postgres pg_dump -U nexus nexus_v2 > /workspace/backup_$(date +%Y%m%d).sql

# Backup to your local machine
scp -P YOUR_PORT root@ssh.runpod.io:/workspace/backup_*.sql ./backups/
```

---

## Cost Optimization

### Use Spot Instances (Save 50-70%)

RunPod Spot instances are much cheaper:
- **On-Demand:** $0.69/hour (RTX 4090)
- **Spot:** $0.29/hour (RTX 4090)
- **Savings:** ~60% cheaper

**Note:** Spot instances can be interrupted, so:
- Keep backups
- Use persistent volumes
- Set up auto-restart

### Stop When Not Using

```bash
# Stop all services (keep data)
docker-compose stop

# Start again when needed
docker-compose start

# Or pause pod in RunPod console to save money
```

### Estimated Monthly Costs

**Development (8 hours/day):**
- GPU Pod (RTX 3070): $0.29/hour × 8 hours × 30 days = $69/month
- Storage (100GB): $3/month
- **Total:** ~$72/month

**Production (24/7):**
- GPU Pod (RTX 4090 Spot): $0.29/hour × 720 hours = $208/month
- Storage (100GB): $3/month
- **Total:** ~$211/month

---

## Troubleshooting

### Pod Won't Start

```bash
# Check Docker
docker ps -a

# Check disk space
df -h

# Restart Docker daemon
service docker restart

# Start services
docker-compose up -d
```

### Database Connection Failed

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres

# Wait 10 seconds
sleep 10
```

### Frontend Won't Load

```bash
# Check if backend is accessible
curl http://localhost:8000/health

# Check frontend logs
docker-compose logs frontend

# Verify environment variables
docker-compose exec frontend env | grep NEXT_PUBLIC

# Rebuild frontend
docker-compose up -d --build frontend
```

### GPU Not Detected

```bash
# Check NVIDIA drivers
nvidia-smi

# Check Docker GPU access
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi

# If issues, reinstall NVIDIA Docker runtime
# (RunPod usually has this pre-configured)
```

---

## Advanced Configuration

### Custom Domain

1. **Get RunPod Proxy URLs** (from console)
2. **Set up Cloudflare Tunnel** (recommended) or **Configure DNS CNAME**

**Option A: Cloudflare Tunnel (Best)**
```bash
# Install cloudflared on your pod
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
chmod +x cloudflared-linux-amd64
mv cloudflared-linux-amd64 /usr/local/bin/cloudflared

# Create tunnel
cloudflared tunnel create nexuslang-v2

# Configure tunnel
cat > /root/.cloudflared/config.yml << 'EOF'
tunnel: YOUR_TUNNEL_ID
credentials-file: /root/.cloudflared/YOUR_TUNNEL_ID.json

ingress:
  - hostname: nexuslang.dev
    service: http://localhost:3000
  - hostname: api.nexuslang.dev
    service: http://localhost:8000
  - service: http_status:404
EOF

# Run tunnel
cloudflared tunnel run nexuslang-v2
```

**Option B: Direct DNS (Simple but exposes IP)**
```
Type: CNAME
Name: nexuslang
Content: YOUR_POD_ID-3000.proxy.runpod.net
```

### SSL/HTTPS

RunPod proxy URLs already have SSL! ✅

If using custom domain with Cloudflare Tunnel, SSL is automatic! ✅

### Monitoring

```bash
# Install monitoring tools
apt-get install -y htop iotop

# Monitor resources
htop

# Monitor GPU
watch -n 1 nvidia-smi

# Monitor Docker
docker stats
```

---

## Scaling on RunPod

### Vertical Scaling (Upgrade GPU)

1. Stop your pod
2. Edit pod configuration
3. Select larger GPU (e.g., RTX 4090 → A100)
4. Restart pod
5. Your data persists on volume!

### Horizontal Scaling (Multiple Pods)

For high traffic, deploy multiple pods:

1. **Load Balancer Pod** (Nginx)
   - Routes traffic to backend pods
   - No GPU needed

2. **Backend Pods** (2-3 pods)
   - Each with GPU for AI features
   - Stateless (database is separate)

3. **Database Pod** (Separate)
   - PostgreSQL on persistent volume
   - No GPU needed
   - Shared by all backends

---

## Backup Strategy

### Automatic Backups

```bash
# Create backup script
cat > /workspace/backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/workspace/backups"

mkdir -p $BACKUP_DIR

# Backup PostgreSQL
docker-compose exec -T postgres pg_dump -U nexus nexus_v2 | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Backup uploaded files (if any)
tar -czf $BACKUP_DIR/files_$DATE.tar.gz /workspace/uploads 2>/dev/null || true

# Keep only last 7 days
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete

echo "✅ Backup completed: $DATE"
EOF

chmod +x /workspace/backup.sh

# Run backup
/workspace/backup.sh

# Schedule daily backups (cron)
(crontab -l 2>/dev/null; echo "0 2 * * * /workspace/backup.sh") | crontab -
```

### Download Backups Locally

```bash
# From your local machine
scp -P YOUR_PORT root@ssh.runpod.io:/workspace/backups/*.gz ./local-backups/
```

---

## Performance Optimization for RunPod

### Optimize Docker Images

```dockerfile
# Use CUDA base images for GPU
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Multi-stage builds to reduce size
FROM python:3.11-slim AS builder
# Build dependencies
FROM python:3.11-slim
# Copy only what's needed
```

### Enable GPU in Docker Compose

Already configured in `docker-compose.runpod.yml`:
```yaml
services:
  backend:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

### Optimize Model Loading

```python
# In backend, lazy load models
# Don't load Whisper/TTS until first request
# This saves memory and startup time
```

---

## Monitoring and Maintenance

### Check Service Health

```bash
# Create health check script
cat > /workspace/health-check.sh << 'EOF'
#!/bin/bash
echo "=== NexusLang v2 Health Check ==="
echo ""

# Backend health
echo "Backend Health:"
curl -s http://localhost:8000/health | jq . || echo "❌ Backend unreachable"
echo ""

# Frontend health
echo "Frontend Health:"
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 && echo " ✅ Frontend OK" || echo "❌ Frontend unreachable"
echo ""

# Database health
echo "Database Health:"
docker-compose exec -T postgres pg_isready && echo "✅ Database OK" || echo "❌ Database down"
echo ""

# Redis health
echo "Redis Health:"
docker-compose exec -T redis redis-cli ping && echo "✅ Redis OK" || echo "❌ Redis down"
echo ""

# Docker containers
echo "Container Status:"
docker-compose ps
echo ""

# Resource usage
echo "GPU Usage:"
nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total --format=csv,noheader
EOF

chmod +x /workspace/health-check.sh

# Run health check
/workspace/health-check.sh
```

### Auto-Restart on Failure

```bash
# Create restart script
cat > /workspace/restart-on-failure.sh << 'EOF'
#!/bin/bash
while true; do
  if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "⚠️ Backend unhealthy, restarting..."
    docker-compose restart backend
    sleep 30
  fi
  sleep 60
done
EOF

chmod +x /workspace/restart-on-failure.sh

# Run in background
nohup /workspace/restart-on-failure.sh > /workspace/restart.log 2>&1 &
```

---

## RunPod-Specific Tips

### 1. Use Persistent Volumes

Mount RunPod volume to `/workspace`:
- All data in `/workspace` persists
- Data outside `/workspace` is lost on pod restart

```bash
# Ensure everything important is in /workspace
/workspace/
├── project-nexus/          # Your code
├── postgres-data/          # Database files
├── redis-data/             # Redis files
├── uploads/                # User uploads
└── backups/                # Backup files
```

### 2. Optimize Costs

- **Use Spot Instances** - 50-70% cheaper
- **Stop When Idle** - Stop pod when not developing
- **Use Smaller GPUs** - RTX 3070 is enough for development
- **Share GPU** - Run multiple light services on one GPU

### 3. Network Access

**RunPod Proxy (Included):**
- Automatic HTTPS
- No configuration needed
- Format: `https://POD_ID-PORT.proxy.runpod.net`

**Custom Ports:**
```bash
# Expose additional ports in RunPod console
# Settings → Edit → Expose Ports → Add Port
```

### 4. GPU Memory Management

```bash
# Monitor GPU memory
watch -n 1 nvidia-smi

# If running out of memory:
# 1. Use smaller models (whisper-tiny vs whisper-large)
# 2. Reduce batch sizes
# 3. Enable model offloading
```

---

## Quick Deploy Script

Save this as `runpod-deploy.sh`:

```bash
#!/bin/bash
# Quick deployment script for RunPod

set -e

echo "🚀 Deploying NexusLang v2 to RunPod..."

# Check if in workspace
if [[ ! "$PWD" == "/workspace"* ]]; then
    echo "⚠️ Not in /workspace, changing directory..."
    cd /workspace/project-nexus
fi

# Pull latest code
echo "📥 Pulling latest code..."
git pull

# Configure environment (if not exists)
if [ ! -f .env ]; then
    echo "⚙️ Creating environment file..."
    cp .env.runpod.template .env
    echo "⚠️ Please edit .env with your API keys!"
    exit 1
fi

# Stop existing services
echo "🛑 Stopping existing services..."
docker-compose down

# Start services
echo "🚀 Starting services..."
docker-compose up -d --build

# Wait for services
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check health
echo "🏥 Checking health..."
curl -s http://localhost:8000/health | jq .

# Get URLs
POD_ID=$(hostname | cut -d'-' -f1)
echo ""
echo "✅ Deployment complete!"
echo ""
echo "🌐 Frontend: https://${POD_ID}-3000.proxy.runpod.net"
echo "🔧 Backend: https://${POD_ID}-8000.proxy.runpod.net"
echo "📊 API Docs: https://${POD_ID}-8000.proxy.runpod.net/docs"
echo ""
echo "🎉 NexusLang v2 is LIVE on RunPod!"
```

Make it executable:
```bash
chmod +x runpod-deploy.sh
./runpod-deploy.sh
```

---

## Security on RunPod

### 1. Change Default Passwords

```bash
# Generate secure passwords
echo "POSTGRES_PASSWORD=$(openssl rand -base64 32)" >> .env
echo "REDIS_PASSWORD=$(openssl rand -base64 32)" >> .env
echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env
echo "JWT_SECRET=$(openssl rand -hex 64)" >> .env
```

### 2. Use Environment Variables

Never hardcode secrets! Always use `.env` file.

### 3. Enable Firewall (Optional)

```bash
# Install ufw
apt-get install -y ufw

# Allow only necessary ports
ufw allow ssh
ufw allow 3000
ufw allow 8000

# Enable firewall
ufw enable
```

### 4. Regular Updates

```bash
# Update system packages
apt-get update && apt-get upgrade -y

# Update Docker images
docker-compose pull
docker-compose up -d
```

---

## FAQ

**Q: Can I use RunPod for production?**  
A: Yes! Many AI companies use RunPod. Use On-Demand pods for reliability.

**Q: What if my pod gets terminated (Spot)?**  
A: Your data in `/workspace` is safe. Just start a new pod and deploy again.

**Q: How do I scale?**  
A: Deploy multiple backend pods behind a load balancer.

**Q: Can I use without GPU?**  
A: Yes! Set `WHISPER_DEVICE=cpu` and `TTS_DEVICE=cpu`. Will be slower but works.

**Q: How do I add custom domain?**  
A: Use Cloudflare Tunnel (see Advanced Configuration above).

---

## Next Steps

1. **Test Locally** ✅
   ```bash
   ./runpod-deploy.sh
   ```

2. **Configure Domain** (Optional)
   - Use Cloudflare Tunnel
   - Or use RunPod proxy URLs

3. **Add API Keys**
   - OpenAI for embeddings
   - Any other AI services

4. **Invite Beta Users**
   - Share your RunPod URL
   - Gather feedback
   - Iterate!

5. **Monitor and Optimize**
   - Watch GPU usage
   - Optimize costs
   - Scale as needed

---

## Support

**RunPod Issues:**
- Discord: https://discord.gg/runpod
- Docs: https://docs.runpod.io

**NexusLang Issues:**
- This is YOUR platform! 🎉
- Everything is documented
- All code is clean and modular

---

## 🎊 You're Ready!

**Your NexusLang v2 Platform is now deployed on RunPod with:**

- ✅ GPU-accelerated AI features
- ✅ Public HTTPS URLs
- ✅ Persistent storage
- ✅ Auto-restart capabilities
- ✅ Monitoring tools
- ✅ Backup strategy

**RunPod provides:**
- 💰 Affordable GPU compute
- ⚡ Fast deployment
- 🔒 Secure HTTPS proxies
- 💾 Persistent volumes
- 🌐 Global access

---

**Deployment URL:**
```
https://YOUR_POD_ID-3000.proxy.runpod.net
```

**Share this URL with testers and start gathering feedback!**

🚀 **NEXUSLANG V2 ON RUNPOD - LIVE!** 🚀

---

_Built with First Principles • Deployed on GPU Cloud • Ready for AI Workloads_

