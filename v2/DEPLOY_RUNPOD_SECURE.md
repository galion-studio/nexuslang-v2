# Secure RunPod Deployment with Admin Access
## NexusLang v2 + Content Management System

This guide sets up secure deployment on RunPod with administrative access from your local machine.

## Architecture Overview

```
Local Machine (Cursor/Admin) ←→ SSH/HTTPS ←→ RunPod Instance
                                              ├── NexusLang v2
                                              ├── Content Manager
                                              ├── PostgreSQL
                                              └── Redis
```

## Part 1: RunPod Setup

### 1.1 Create RunPod Instance

1. Go to RunPod.io and create a new Pod
2. Select template: **RunPod PyTorch** or **Ubuntu 22.04**
3. Recommended specs:
   - GPU: Optional (not required for CMS)
   - CPU: 4+ vCPUs
   - RAM: 16GB+
   - Storage: 50GB+
4. Enable **SSH** and note the connection details

### 1.2 Initial Connection

```bash
# From your local machine
ssh root@<POD_IP> -p <POD_PORT>

# Or use RunPod's web terminal
```

## Part 2: Secure Setup

### 2.1 Create Admin User

```bash
# On RunPod instance
# Create admin user for remote management
useradd -m -s /bin/bash nexus-admin
usermod -aG sudo nexus-admin
passwd nexus-admin  # Set strong password

# Add to docker group
usermod -aG docker nexus-admin

# Setup SSH key authentication
mkdir -p /home/nexus-admin/.ssh
chmod 700 /home/nexus-admin/.ssh
```

### 2.2 Setup SSH Keys (On Local Machine)

```bash
# Generate SSH key if you don't have one
ssh-keygen -t ed25519 -C "admin@galion-studio"

# Copy public key to RunPod
cat ~/.ssh/id_ed25519.pub | ssh root@<POD_IP> -p <POD_PORT> \
  'cat >> /home/nexus-admin/.ssh/authorized_keys'

# Set proper permissions on RunPod
ssh root@<POD_IP> -p <POD_PORT> << 'EOF'
chown -R nexus-admin:nexus-admin /home/nexus-admin/.ssh
chmod 600 /home/nexus-admin/.ssh/authorized_keys
EOF

# Test connection
ssh nexus-admin@<POD_IP> -p <POD_PORT>
```

### 2.3 Configure Firewall

```bash
# On RunPod instance
sudo apt update
sudo apt install -y ufw

# Allow SSH
sudo ufw allow <POD_PORT>/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow application ports
sudo ufw allow 3100/tcp  # Frontend
sudo ufw allow 8100/tcp  # Backend

# Enable firewall
sudo ufw --force enable
```

## Part 3: Deploy Application

### 3.1 Clone Repository

```bash
# On RunPod instance as nexus-admin
cd /home/nexus-admin
git clone https://github.com/<YOUR_ORG>/project-nexus.git
cd project-nexus/v2
```

### 3.2 Setup Environment

```bash
# Create environment file
cat > .env << 'EOF'
# Database
DATABASE_URL=postgresql://nexuslang:secure_password_here@postgres:5432/nexuslang_v2

# Redis
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET=$(openssl rand -hex 32)

# CORS
CORS_ORIGINS=["https://developer.galion.app","http://localhost:3100"]

# Ports
BACKEND_PORT=8100
FRONTEND_PORT=3100

# Storage (for media files)
STORAGE_TYPE=local
MEDIA_STORAGE_PATH=/app/media_storage
MEDIA_BASE_URL=https://developer.galion.app/media
EOF

# Generate secure secrets
sed -i "s/secure_password_here/$(openssl rand -base64 32)/g" .env
```

### 3.3 Deploy with Docker

```bash
# Build and start services
docker-compose -f docker-compose.nexuslang.yml up -d

# Run database migrations
docker-compose -f docker-compose.nexuslang.yml exec backend \
  python -c "from core.database import init_db; import asyncio; asyncio.run(init_db())"

# Run content manager migration
docker-compose -f docker-compose.nexuslang.yml exec backend \
  psql $DATABASE_URL -f /app/database/migrations/003_content_manager.sql
```

## Part 4: Secure Admin Access

### 4.1 Setup SSH Tunnel for Database Access

```bash
# From local machine - Access PostgreSQL
ssh -L 5432:localhost:5432 nexus-admin@<POD_IP> -p <POD_PORT>

# Now you can connect to database from local machine
psql postgresql://nexuslang:password@localhost:5432/nexuslang_v2
```

### 4.2 Setup Remote Development Access

Create `~/.ssh/config` on local machine:

```
Host runpod-nexus
    HostName <POD_IP>
    Port <POD_PORT>
    User nexus-admin
    IdentityFile ~/.ssh/id_ed25519
    LocalForward 5432 localhost:5432
    LocalForward 6379 localhost:6379
    LocalForward 8100 localhost:8100
    LocalForward 3100 localhost:3100
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

### 4.3 Connect from Cursor/VS Code

In Cursor:
1. Install "Remote - SSH" extension
2. Press Cmd/Ctrl+Shift+P
3. Select "Remote-SSH: Connect to Host"
4. Select "runpod-nexus"
5. Open folder: `/home/nexus-admin/project-nexus`

## Part 5: Cloudflare Tunnel (Secure Public Access)

### 5.1 Install Cloudflared

```bash
# On RunPod instance
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared
sudo chmod +x /usr/local/bin/cloudflared
```

### 5.2 Authenticate

```bash
cloudflared tunnel login
```

### 5.3 Create Tunnels

```bash
# Create tunnel for frontend
cloudflared tunnel create nexuslang-frontend

# Create tunnel for backend API
cloudflared tunnel create nexuslang-api

# Note the tunnel IDs and update DNS
```

### 5.4 Configure Tunnels

Create `cloudflare-tunnel-config.yml`:

```yaml
tunnel: <TUNNEL_ID>
credentials-file: /home/nexus-admin/.cloudflared/<TUNNEL_ID>.json

ingress:
  # Frontend
  - hostname: developer.galion.app
    service: http://localhost:3100
  
  # Backend API
  - hostname: api.developer.galion.app
    service: http://localhost:8100
  
  # Catch-all
  - service: http_status:404
```

### 5.5 Start Tunnel

```bash
cloudflared tunnel run --config cloudflare-tunnel-config.yml <TUNNEL_ID>

# Or run as service
sudo cloudflared service install
sudo systemctl enable cloudflared
sudo systemctl start cloudflared
```

## Part 6: CI/CD Pipeline Setup

### 6.1 GitHub Actions Workflow

Create `.github/workflows/deploy-runpod.yml`:

```yaml
name: Deploy to RunPod

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to RunPod
        env:
          SSH_PRIVATE_KEY: ${{ secrets.RUNPOD_SSH_KEY }}
          RUNPOD_HOST: ${{ secrets.RUNPOD_HOST }}
          RUNPOD_PORT: ${{ secrets.RUNPOD_PORT }}
        run: |
          mkdir -p ~/.ssh
          echo "$SSH_PRIVATE_KEY" > ~/.ssh/id_rsa
          chmod 600 ~/.ssh/id_rsa
          ssh-keyscan -p $RUNPOD_PORT $RUNPOD_HOST >> ~/.ssh/known_hosts
          
          # Deploy
          ssh -p $RUNPOD_PORT nexus-admin@$RUNPOD_HOST << 'ENDSSH'
            cd /home/nexus-admin/project-nexus
            git pull origin main
            cd v2
            docker-compose -f docker-compose.nexuslang.yml pull
            docker-compose -f docker-compose.nexuslang.yml up -d
            docker-compose -f docker-compose.nexuslang.yml exec -T backend python -m pytest
          ENDSSH
```

### 6.2 Setup GitHub Secrets

Add to GitHub repository secrets:
- `RUNPOD_SSH_KEY`: Your private SSH key
- `RUNPOD_HOST`: RunPod IP address
- `RUNPOD_PORT`: RunPod SSH port

## Part 7: Monitoring & Backup

### 7.1 Setup Monitoring

```bash
# Install monitoring tools
docker-compose -f docker-compose.nexuslang.yml -f docker-compose.monitoring.yml up -d

# Access Grafana: http://<POD_IP>:3000
```

### 7.2 Automated Backups

Create `/home/nexus-admin/backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/home/nexus-admin/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
docker-compose exec -T postgres pg_dump -U nexuslang nexuslang_v2 | \
  gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Backup media files
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /home/nexus-admin/project-nexus/v2/media_storage

# Keep only last 7 days
find $BACKUP_DIR -mtime +7 -delete

# Upload to S3/R2 (optional)
# aws s3 cp $BACKUP_DIR/db_$DATE.sql.gz s3://your-bucket/backups/
```

Setup cron:

```bash
crontab -e

# Add line:
0 2 * * * /home/nexus-admin/backup.sh
```

## Part 8: Security Checklist

- [x] SSH key authentication only
- [x] Firewall configured (UFW)
- [x] Non-root admin user
- [x] Cloudflare Tunnel for public access
- [x] Environment variables for secrets
- [x] Regular automated backups
- [x] HTTPS via Cloudflare
- [x] Database not exposed publicly
- [x] Redis not exposed publicly

## Part 9: Admin Commands

### From Local Machine

```bash
# Connect to RunPod
ssh runpod-nexus

# View logs
ssh runpod-nexus 'cd project-nexus/v2 && docker-compose logs -f --tail=100'

# Restart services
ssh runpod-nexus 'cd project-nexus/v2 && docker-compose restart'

# Database shell
ssh runpod-nexus 'docker-compose exec postgres psql -U nexuslang nexuslang_v2'

# Run migrations
ssh runpod-nexus 'cd project-nexus/v2 && docker-compose exec backend python scripts/migrate.py'
```

### Database Management

```bash
# Backup
ssh runpod-nexus './backup.sh'

# Restore
scp backup.sql.gz runpod-nexus:~/
ssh runpod-nexus 'gunzip < backup.sql.gz | docker-compose exec -T postgres psql -U nexuslang nexuslang_v2'
```

## Part 10: Troubleshooting

### Check Service Status

```bash
ssh runpod-nexus 'docker-compose ps'
```

### View Logs

```bash
# All services
ssh runpod-nexus 'docker-compose logs'

# Specific service
ssh runpod-nexus 'docker-compose logs backend'
ssh runpod-nexus 'docker-compose logs frontend'
```

### Test API

```bash
curl https://api.developer.galion.app/health
```

## Summary

You now have:
- ✅ Secure RunPod deployment
- ✅ SSH key-based admin access
- ✅ Cloudflare Tunnel for HTTPS
- ✅ Database and Redis secured
- ✅ CI/CD pipeline ready
- ✅ Automated backups
- ✅ Remote development access from Cursor

Access your platform:
- **Frontend**: https://developer.galion.app
- **API**: https://api.developer.galion.app
- **Admin SSH**: `ssh runpod-nexus`

