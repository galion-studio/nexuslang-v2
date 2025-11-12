#!/bin/bash
# VPS Setup Script for GALION.APP & GALION.STUDIO
# Run this on a fresh Ubuntu 22.04 server
# Usage: curl -fsSL https://raw.githubusercontent.com/galion/infrastructure/main/scripts/vps-setup.sh | bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║      GALION VPS Setup Script                           ║${NC}"
echo -e "${GREEN}║      Version 1.0 - November 2025                       ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
   echo -e "${RED}Please run as root (use: sudo su)${NC}"
   exit 1
fi

echo -e "${YELLOW}This script will:${NC}"
echo "  1. Update system packages"
echo "  2. Install Docker & Docker Compose"
echo "  3. Install Nginx"
echo "  4. Install Certbot (SSL)"
echo "  5. Configure firewall (UFW)"
echo "  6. Install fail2ban"
echo "  7. Create deploy user"
echo "  8. Set up directory structure"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

# Update system
echo -e "\n${GREEN}[1/8] Updating system packages...${NC}"
apt update && apt upgrade -y

# Install Docker
echo -e "\n${GREEN}[2/8] Installing Docker...${NC}"
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    systemctl enable docker
    systemctl start docker
    echo -e "${GREEN}✓ Docker installed successfully${NC}"
else
    echo -e "${YELLOW}✓ Docker already installed${NC}"
fi

# Install Docker Compose
echo -e "\n${GREEN}Installing Docker Compose plugin...${NC}"
apt install docker-compose-plugin -y

# Install Nginx
echo -e "\n${GREEN}[3/8] Installing Nginx...${NC}"
if ! command -v nginx &> /dev/null; then
    apt install nginx -y
    systemctl enable nginx
    systemctl start nginx
    echo -e "${GREEN}✓ Nginx installed successfully${NC}"
else
    echo -e "${YELLOW}✓ Nginx already installed${NC}"
fi

# Install Certbot
echo -e "\n${GREEN}[4/8] Installing Certbot (Let's Encrypt)...${NC}"
if ! command -v certbot &> /dev/null; then
    apt install certbot python3-certbot-nginx -y
    echo -e "${GREEN}✓ Certbot installed successfully${NC}"
else
    echo -e "${YELLOW}✓ Certbot already installed${NC}"
fi

# Configure UFW firewall
echo -e "\n${GREEN}[5/8] Configuring firewall (UFW)...${NC}"
apt install ufw -y
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp comment "SSH"
ufw allow 80/tcp comment "HTTP"
ufw allow 443/tcp comment "HTTPS"
ufw --force enable
echo -e "${GREEN}✓ Firewall configured${NC}"
ufw status verbose

# Install fail2ban
echo -e "\n${GREEN}[6/8] Installing fail2ban...${NC}"
if ! command -v fail2ban-client &> /dev/null; then
    apt install fail2ban -y
    systemctl enable fail2ban
    systemctl start fail2ban
    
    # Configure fail2ban for SSH
    cat > /etc/fail2ban/jail.local <<EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = 22
logpath = /var/log/auth.log
EOF
    
    systemctl restart fail2ban
    echo -e "${GREEN}✓ fail2ban installed and configured${NC}"
else
    echo -e "${YELLOW}✓ fail2ban already installed${NC}"
fi

# Create deploy user
echo -e "\n${GREEN}[7/8] Creating deploy user...${NC}"
if id "deploy" &>/dev/null; then
    echo -e "${YELLOW}✓ deploy user already exists${NC}"
else
    adduser --disabled-password --gecos "" deploy
    usermod -aG sudo deploy
    usermod -aG docker deploy
    echo -e "${GREEN}✓ deploy user created${NC}"
    
    # Setup SSH keys for deploy user
    mkdir -p /home/deploy/.ssh
    cp /root/.ssh/authorized_keys /home/deploy/.ssh/ 2>/dev/null || true
    chown -R deploy:deploy /home/deploy/.ssh
    chmod 700 /home/deploy/.ssh
    chmod 600 /home/deploy/.ssh/authorized_keys 2>/dev/null || true
fi

# Set up directory structure
echo -e "\n${GREEN}[8/8] Setting up directory structure...${NC}"
su - deploy <<'DEPLOY_EOF'
mkdir -p ~/galion/{app,studio,data,backups,nginx,monitoring,scripts}
mkdir -p ~/galion/data/{postgres,redis,uploads,logs,prometheus}
mkdir -p ~/galion/nginx/{conf.d,ssl}
echo "✓ Directory structure created"
DEPLOY_EOF

# Install useful tools
echo -e "\n${GREEN}Installing additional tools...${NC}"
apt install -y \
    htop \
    iotop \
    nethogs \
    ncdu \
    postgresql-client-15 \
    redis-tools \
    git \
    curl \
    wget \
    jq \
    vim \
    nano

# Configure SSH security
echo -e "\n${GREEN}Hardening SSH configuration...${NC}"
sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sed -i 's/PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
systemctl restart sshd

# Set up automatic security updates
echo -e "\n${GREEN}Enabling automatic security updates...${NC}"
apt install unattended-upgrades -y
dpkg-reconfigure -plow unattended-upgrades

# Create helpful aliases for deploy user
echo -e "\n${GREEN}Setting up helpful aliases...${NC}"
cat >> /home/deploy/.bashrc <<'EOF'

# GALION aliases
alias dc='docker compose'
alias dcup='docker compose up -d'
alias dcdown='docker compose down'
alias dclogs='docker compose logs -f'
alias dcps='docker compose ps'
alias dstats='docker stats'
alias nginx-reload='sudo systemctl reload nginx'
alias nginx-test='sudo nginx -t'
alias galion='cd ~/galion'

# Git aliases
alias gs='git status'
alias gp='git pull'
alias gc='git commit'
alias glog='git log --oneline --graph --decorate'

EOF

chown deploy:deploy /home/deploy/.bashrc

# Set system limits
echo -e "\n${GREEN}Optimizing system limits...${NC}"
cat >> /etc/security/limits.conf <<EOF
* soft nofile 65536
* hard nofile 65536
* soft nproc 65536
* hard nproc 65536
EOF

# Configure sysctl for better performance
cat >> /etc/sysctl.conf <<EOF

# GALION optimizations
vm.swappiness=10
net.core.somaxconn=4096
net.ipv4.tcp_max_syn_backlog=4096
net.ipv4.tcp_tw_reuse=1
net.ipv4.ip_local_port_range=10000 65000
net.ipv4.tcp_slow_start_after_idle=0
EOF

sysctl -p

# Create welcome message
cat > /etc/motd <<'EOF'
╔════════════════════════════════════════════════════════╗
║           GALION VPS - Production Server               ║
║                                                        ║
║  🚀 Applications:                                      ║
║     - GALION.APP    (galion.app)                      ║
║     - GALION.STUDIO (studio.galion.app)               ║
║                                                        ║
║  📚 Quick Commands:                                    ║
║     dc ps          - List containers                  ║
║     dclogs         - View logs                        ║
║     dcup           - Start all services               ║
║     dcdown         - Stop all services                ║
║     galion         - Go to project directory          ║
║                                                        ║
║  📖 Documentation: /home/deploy/galion/README.md      ║
╚════════════════════════════════════════════════════════╝
EOF

# Print summary
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║          Setup Complete! ✓                             ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}What was installed:${NC}"
echo "  ✓ Docker & Docker Compose"
echo "  ✓ Nginx web server"
echo "  ✓ Certbot (SSL certificates)"
echo "  ✓ UFW firewall (ports 22, 80, 443 open)"
echo "  ✓ fail2ban (brute force protection)"
echo "  ✓ deploy user with sudo access"
echo "  ✓ Directory structure at /home/deploy/galion"
echo ""
echo -e "${YELLOW}Security improvements:${NC}"
echo "  ✓ Root SSH login disabled"
echo "  ✓ Password authentication disabled"
echo "  ✓ Automatic security updates enabled"
echo "  ✓ fail2ban monitoring SSH"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Switch to deploy user:"
echo "     ${GREEN}su - deploy${NC}"
echo ""
echo "  2. Clone your repository:"
echo "     ${GREEN}cd ~/galion${NC}"
echo "     ${GREEN}git clone https://github.com/your-org/galion-platform.git .${NC}"
echo ""
echo "  3. Configure environment variables:"
echo "     ${GREEN}nano .env${NC}"
echo ""
echo "  4. Deploy services:"
echo "     ${GREEN}docker compose up -d${NC}"
echo ""
echo "  5. Get SSL certificates:"
echo "     ${GREEN}sudo certbot --nginx -d galion.app -d api.galion.app${NC}"
echo ""
echo -e "${YELLOW}Server Information:${NC}"
echo "  IP Address: $(hostname -I | awk '{print $1}')"
echo "  Hostname: $(hostname)"
echo "  Deploy User: deploy"
echo "  Project Dir: /home/deploy/galion"
echo ""
echo -e "${GREEN}Documentation: https://github.com/galion/docs/deployment${NC}"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT: Save your SSH keys before logging out!${NC}"
echo ""

# Log completion
echo "$(date): VPS setup completed successfully" >> /var/log/galion-setup.log

exit 0

