#!/bin/bash
# Quick VPS Setup and Deployment for GALION
# Run this on your VPS after SSHing in
# curl -fsSL https://raw.githubusercontent.com/your-org/galion/main/deploy-to-vps.sh | bash

set -e

echo "========================================"
echo "  GALION VPS Quick Setup & Deploy"
echo "========================================"
echo ""

# Update system
echo "[1/10] Updating system..."
apt update && apt upgrade -y

# Install Docker
echo "[2/10] Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
systemctl enable docker
systemctl start docker

# Install Docker Compose
echo "[3/10] Installing Docker Compose..."
apt install -y docker-compose-plugin

# Install Nginx & Certbot
echo "[4/10] Installing Nginx & Certbot..."
apt install -y nginx certbot python3-certbot-nginx

# Install utilities
echo "[5/10] Installing utilities..."
apt install -y git curl wget htop iotop nethogs postgresql-client-15 redis-tools fail2ban ufw

# Configure firewall
echo "[6/10] Configuring firewall..."
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# Setup fail2ban
echo "[7/10] Configuring fail2ban..."
systemctl enable fail2ban
systemctl start fail2ban

# Create deploy user
echo "[8/10] Creating deploy user..."
if ! id "deploy" &>/dev/null; then
    adduser --disabled-password --gecos "" deploy
    usermod -aG sudo,docker deploy
    
    # Copy SSH keys
    mkdir -p /home/deploy/.ssh
    cp /root/.ssh/authorized_keys /home/deploy/.ssh/ 2>/dev/null || true
    chown -R deploy:deploy /home/deploy/.ssh
    chmod 700 /home/deploy/.ssh
fi

# Create directory structure
echo "[9/10] Creating directories..."
su - deploy <<'EOF'
mkdir -p ~/galion/{data,backups,logs,configs,nginx,monitoring,scripts,app,tests}
mkdir -p ~/galion/data/{postgres,redis,uploads,logs,prometheus}
mkdir -p ~/galion/backups/wal_archive
cd ~/galion
EOF

# Harden SSH
echo "[10/10] Hardening SSH..."
sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config

echo ""
echo "========================================"
echo "  ✅ Setup Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "  1. Switch to deploy user: su - deploy"
echo "  2. Upload your files to ~/galion"
echo "  3. Configure .env file"
echo "  4. Run: cd ~/galion && docker compose up -d"
echo ""

