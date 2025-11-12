#!/bin/bash
# GALION FULLY AUTOMATED DEPLOYMENT
# Run this ONE command on your VPS to deploy everything
# curl -fsSL https://raw.githubusercontent.com/galion-studio/galion-platform/main/FULL_AUTO_DEPLOY.sh | bash

set -e

echo "========================================="
echo "  GALION AUTOMATED DEPLOYMENT"
echo "  This will deploy everything automatically"
echo "========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
   echo "Please run as root: sudo bash FULL_AUTO_DEPLOY.sh"
   exit 1
fi

# Update system
echo "[1/15] Updating system..."
apt update && DEBIAN_FRONTEND=noninteractive apt upgrade -y

# Install Docker
echo "[2/15] Installing Docker..."
curl -fsSL https://get.docker.com | sh
systemctl enable docker
systemctl start docker

# Install Docker Compose
echo "[3/15] Installing Docker Compose..."
apt install -y docker-compose-plugin

# Install all required packages
echo "[4/15] Installing Nginx, Certbot, tools..."
DEBIAN_FRONTEND=noninteractive apt install -y \
    nginx \
    certbot \
    python3-certbot-nginx \
    git \
    curl \
    wget \
    htop \
    iotop \
    nethogs \
    ncdu \
    postgresql-client-15 \
    redis-tools \
    fail2ban \
    ufw \
    jq \
    vim

# Configure firewall
echo "[5/15] Configuring firewall..."
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# Configure fail2ban
echo "[6/15] Configuring fail2ban..."
systemctl enable fail2ban
systemctl start fail2ban

# Create deploy user
echo "[7/15] Creating deploy user..."
if ! id "deploy" &>/dev/null; then
    adduser --disabled-password --gecos "" deploy
    echo "deploy:$(openssl rand -base64 32)" | chpasswd
    usermod -aG sudo,docker deploy
    
    # Setup SSH for deploy user
    mkdir -p /home/deploy/.ssh
    cp /root/.ssh/authorized_keys /home/deploy/.ssh/ 2>/dev/null || true
    chown -R deploy:deploy /home/deploy/.ssh
    chmod 700 /home/deploy/.ssh
    chmod 600 /home/deploy/.ssh/authorized_keys 2>/dev/null || true
fi

# Create directory structure
echo "[8/15] Creating directories..."
su - deploy <<'DEPLOY_COMMANDS'
mkdir -p ~/galion
cd ~/galion
mkdir -p data/{postgres,redis,uploads,logs,prometheus}
mkdir -p backups/wal_archive
mkdir -p logs
DEPLOY_COMMANDS

# Clone repository as deploy user
echo "[9/15] Cloning code from GitHub..."
su - deploy <<'DEPLOY_COMMANDS'
cd ~/galion
if [ ! -d ".git" ]; then
    git clone https://github.com/galion-studio/galion-platform.git .
else
    git pull origin main
fi
DEPLOY_COMMANDS

# Generate secrets
echo "[10/15] Generating secrets..."
su - deploy <<'DEPLOY_COMMANDS'
cd ~/galion
chmod +x scripts/*.sh 2>/dev/null || true

# Generate strong passwords
POSTGRES_PASS=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
REDIS_PASS=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
JWT_SECRET=$(openssl rand -base64 64 | tr -d "\n")

# Create .env file
cat > .env <<EOF
POSTGRES_USER=galion
POSTGRES_PASSWORD=$POSTGRES_PASS
POSTGRES_DB=galion
DATABASE_URL=postgresql://galion:$POSTGRES_PASS@postgres:5432/galion
DATABASE_URL_STUDIO=postgresql://galion:$POSTGRES_PASS@postgres:5432/galion_studio

REDIS_PASSWORD=$REDIS_PASS
REDIS_URL=redis://:$REDIS_PASS@redis:6379/0

JWT_SECRET=$JWT_SECRET
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=15

# IMPORTANT: Add your API keys here manually or set as environment variables
OPENAI_API_KEY=${OPENAI_API_KEY:-sk-your-key-here}
ELEVENLABS_API_KEY=${ELEVENLABS_API_KEY:-your-key-here}

ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

VITE_API_URL=https://api.galion.app
VITE_WS_URL=wss://api.galion.app
NEXT_PUBLIC_API_URL=https://api.studio.galion.app
NEXT_PUBLIC_WS_URL=wss://api.studio.galion.app

CORS_ORIGINS=https://galion.app,https://studio.galion.app
RATE_LIMIT_PER_MINUTE=100
EOF

chmod 600 .env
echo "✓ Secrets generated"
DEPLOY_COMMANDS

# Build and start services
echo "[11/15] Building Docker images..."
su - deploy <<'DEPLOY_COMMANDS'
cd ~/galion
docker compose build --parallel
DEPLOY_COMMANDS

echo "[12/15] Starting services..."
su - deploy <<'DEPLOY_COMMANDS'
cd ~/galion

# Start infrastructure
docker compose up -d postgres redis pgbouncer
sleep 30

# Start applications
docker compose up -d app-api studio-api app-voice studio-realtime
sleep 40

# Start frontends
docker compose up -d app-frontend studio-frontend

# Start monitoring
docker compose up -d prometheus node-exporter cadvisor postgres-exporter redis-exporter nginx-exporter

echo "✓ All services started"
DEPLOY_COMMANDS

# Configure Nginx
echo "[13/15] Configuring Nginx..."
cp /home/deploy/galion/nginx/nginx.conf /etc/nginx/nginx.conf
cp /home/deploy/galion/nginx/sites-available/* /etc/nginx/sites-available/
cp /home/deploy/galion/nginx/conf.d/* /etc/nginx/conf.d/
ln -sf /etc/nginx/sites-available/galion-app /etc/nginx/sites-enabled/
ln -sf /etc/nginx/sites-available/galion-studio /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
mkdir -p /var/www/certbot

# Test and reload
nginx -t && systemctl reload nginx

# Setup cron jobs
echo "[14/15] Setting up automated tasks..."
su - deploy <<'DEPLOY_COMMANDS'
(crontab -l 2>/dev/null | grep -v galion; cat <<CRON
0 2 * * * /home/deploy/galion/scripts/backup.sh >> /home/deploy/galion/logs/backup.log 2>&1
*/5 * * * * /home/deploy/galion/scripts/health-check.sh >> /home/deploy/galion/logs/health.log 2>&1
CRON
) | crontab -
DEPLOY_COMMANDS

# Verify deployment
echo "[15/15] Verifying deployment..."
su - deploy <<'DEPLOY_COMMANDS'
cd ~/galion
sleep 10
docker compose ps
echo ""
echo "Testing health endpoints..."
curl -s http://localhost:8001/health | jq '.' || echo "App API starting..."
curl -s http://localhost:8003/health | jq '.' || echo "Studio API starting..."
DEPLOY_COMMANDS

echo ""
echo "========================================="
echo "  ✅ DEPLOYMENT COMPLETE!"
echo "========================================="
echo ""
echo "Services deployed:"
echo "  ✓ PostgreSQL + PgBouncer"
echo "  ✓ Redis"
echo "  ✓ GALION.APP (API + Frontend + Voice)"
echo "  ✓ GALION.STUDIO (API + Frontend + Realtime)"
echo "  ✓ Monitoring (Prometheus + Exporters)"
echo ""
echo "⚠️  IMPORTANT: Configure SSL certificates:"
echo "    certbot --nginx -d galion.app -d www.galion.app -d api.galion.app"
echo "    certbot --nginx -d studio.galion.app -d api.studio.galion.app"
echo ""
echo "⚠️  IMPORTANT: Add your API keys to .env:"
echo "    su - deploy"
echo "    cd galion"
echo "    nano .env"
echo "    Add: OPENAI_API_KEY and ELEVENLABS_API_KEY"
echo "    Then: docker compose restart app-api app-voice"
echo ""
echo "Check status: su - deploy && cd galion && docker compose ps"
echo ""

