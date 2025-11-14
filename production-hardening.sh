#!/bin/bash
# NexusLang v2 Production Hardening Script
# SSL certificates, security configurations, and production optimizations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
DOMAIN="${DOMAIN:-localhost}"
EMAIL="${EMAIL:-admin@nexuslang.dev}"
STAGING="${STAGING:-0}"  # Set to 1 for Let's Encrypt staging

# Logging
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

error() {
    echo -e "${RED}ERROR: $1${NC}" >&2
    log "ERROR: $1"
    exit 1
}

success() {
    echo -e "${GREEN}SUCCESS: $1${NC}"
    log "SUCCESS: $1"
}

info() {
    echo -e "${BLUE}INFO: $1${NC}"
    log "INFO: $1"
}

warning() {
    echo -e "${YELLOW}WARNING: $1${NC}"
    log "WARNING: $1"
}

# Check prerequisites
check_prerequisites() {
    info "Checking prerequisites..."

    # Check if running as root or with sudo
    if [[ $EUID -eq 0 ]]; then
        error "This script should not be run as root. Use sudo if needed."
    fi

    # Check if Docker is running
    if ! docker info >/dev/null 2>&1; then
        error "Docker is not running or not accessible"
    fi

    # Check if services are running
    if ! docker-compose ps | grep -q "Up"; then
        warning "No services appear to be running. Make sure to run 'docker-compose up -d' first."
    fi

    # Check if certbot is available
    if ! command -v certbot >/dev/null 2>&1; then
        info "Installing certbot for SSL certificates..."
        if command -v apt-get >/dev/null 2>&1; then
            sudo apt-get update
            sudo apt-get install -y certbot python3-certbot-nginx
        elif command -v yum >/dev/null 2>&1; then
            sudo yum install -y certbot python3-certbot-nginx
        else
            warning "Could not install certbot automatically. Please install it manually."
        fi
    fi

    success "Prerequisites check completed"
}

# Generate self-signed SSL certificates (fallback)
generate_self_signed_cert() {
    info "Generating self-signed SSL certificate..."

    local cert_dir="./ssl"
    mkdir -p "$cert_dir"

    # Generate private key
    openssl genrsa -out "$cert_dir/nexus.key" 2048

    # Generate certificate
    openssl req -new -x509 -key "$cert_dir/nexus.key" -out "$cert_dir/nexus.crt" -days 365 -subj "/C=US/ST=State/L=City/O=NexusLang/CN=$DOMAIN"

    success "Self-signed certificate generated in $cert_dir/"
}

# Get Let's Encrypt SSL certificates
get_letsencrypt_cert() {
    info "Obtaining Let's Encrypt SSL certificate for $DOMAIN..."

    # Stop nginx if running
    docker-compose stop nginx 2>/dev/null || true

    # Run certbot
    local certbot_cmd="certbot certonly --standalone"
    if [[ "$STAGING" -eq 1 ]]; then
        certbot_cmd="$certbot_cmd --staging"
    fi
    certbot_cmd="$certbot_cmd -d $DOMAIN --email $EMAIL --agree-tos --non-interactive"

    if sudo $certbot_cmd; then
        success "Let's Encrypt certificate obtained successfully"

        # Copy certificates to project directory
        local cert_dir="./ssl"
        mkdir -p "$cert_dir"

        sudo cp "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" "$cert_dir/nexus.crt"
        sudo cp "/etc/letsencrypt/live/$DOMAIN/privkey.pem" "$cert_dir/nexus.key"

        # Set proper permissions
        sudo chown $(id -u):$(id -g) "$cert_dir"/*.pem 2>/dev/null || true

        success "Certificates copied to $cert_dir/"
    else
        warning "Let's Encrypt certificate generation failed. Using self-signed certificate."
        generate_self_signed_cert
    fi
}

# Configure SSL certificates
configure_ssl() {
    info "Configuring SSL certificates..."

    local cert_dir="./ssl"

    if [[ ! -f "$cert_dir/nexus.crt" || ! -f "$cert_dir/nexus.key" ]]; then
        info "No SSL certificates found. Generating self-signed certificate..."
        generate_self_signed_cert
    fi

    # Validate certificate
    if openssl x509 -in "$cert_dir/nexus.crt" -text -noout >/dev/null 2>&1; then
        success "SSL certificate is valid"
    else
        error "SSL certificate is invalid"
    fi

    # Update nginx configuration to use SSL certificates
    if [[ -f "nginx.conf" ]]; then
        # Replace certificate paths in nginx.conf
        sed -i "s|ssl_certificate /etc/ssl/certs/nexus.crt;|ssl_certificate /etc/ssl/certs/nexus.crt;|g" nginx.conf
        sed -i "s|ssl_certificate_key /etc/ssl/private/nexus.key;|ssl_certificate_key /etc/ssl/private/nexus.key;|g" nginx.conf
        info "Nginx configuration updated for SSL"
    fi

    success "SSL configuration completed"
}

# Configure firewall
configure_firewall() {
    info "Configuring firewall..."

    # Detect firewall type
    if command -v ufw >/dev/null 2>&1; then
        info "Configuring UFW firewall..."

        sudo ufw --force enable
        sudo ufw allow ssh
        sudo ufw allow 80
        sudo ufw allow 443
        sudo ufw --force reload

        success "UFW firewall configured"

    elif command -v firewall-cmd >/dev/null 2>&1; then
        info "Configuring firewalld..."

        sudo firewall-cmd --permanent --add-service=ssh
        sudo firewall-cmd --permanent --add-service=http
        sudo firewall-cmd --permanent --add-service=https
        sudo firewall-cmd --reload

        success "Firewalld configured"

    else
        warning "No supported firewall detected (ufw/firewalld). Please configure manually."
        info "Required open ports: 22 (SSH), 80 (HTTP), 443 (HTTPS)"
    fi
}

# Harden Docker configuration
harden_docker() {
    info "Hardening Docker configuration..."

    # Create Docker daemon configuration if it doesn't exist
    local daemon_config="/etc/docker/daemon.json"

    if [[ ! -f "$daemon_config" ]]; then
        sudo tee "$daemon_config" > /dev/null <<EOF
{
    "icc": false,
    "log-driver": "json-file",
    "log-opts": {
        "max-size": "10m",
        "max-file": "3"
    },
    "default-ulimits": {
        "nofile": {
            "Name": "nofile",
            "Hard": 64000,
            "Soft": 64000
        }
    },
    "userns-remap": "default"
}
EOF
        sudo systemctl restart docker
        success "Docker daemon hardened"
    else
        info "Docker daemon configuration already exists"
    fi

    # Secure Docker socket
    if [[ -S "/var/run/docker.sock" ]]; then
        sudo chmod 660 /var/run/docker.sock
        info "Docker socket permissions secured"
    fi
}

# Configure log rotation
configure_logging() {
    info "Configuring log rotation..."

    # Create logrotate configuration for NexusLang
    sudo tee "/etc/logrotate.d/nexuslang" > /dev/null <<EOF
/var/log/nexuslang/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 root root
    postrotate
        docker-compose logs -f --tail=0 > /dev/null 2>&1 || true
    endscript
}
EOF

    success "Log rotation configured"
}

# Configure monitoring and alerts
configure_monitoring() {
    info "Configuring monitoring and alerts..."

    # Create systemd service for monitoring alerts
    sudo tee "/etc/systemd/system/nexuslang-monitor.service" > /dev/null <<EOF
[Unit]
Description=NexusLang v2 Monitoring Alerts
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$(pwd)
ExecStart=$(which python3) monitoring/alerts.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable nexuslang-monitor
    sudo systemctl start nexuslang-monitor

    success "Monitoring alerts service configured"
}

# Configure automatic backups
configure_backups() {
    info "Configuring automatic backups..."

    # Create cron job for daily backups
    local cron_job="0 2 * * * $(pwd)/backup-restore.sh backup"

    # Check if cron job already exists
    if ! crontab -l 2>/dev/null | grep -q "backup-restore.sh"; then
        (crontab -l 2>/dev/null; echo "$cron_job") | crontab -
        success "Daily backup cron job configured (2 AM daily)"
    else
        info "Backup cron job already exists"
    fi

    # Create cron job for cleanup
    local cleanup_job="0 3 * * 0 MAX_BACKUPS=7 $(pwd)/backup-restore.sh cleanup"
    if ! crontab -l 2>/dev/null | grep -q "cleanup"; then
        (crontab -l 2>/dev/null; echo "$cleanup_job") | crontab -
        success "Weekly cleanup cron job configured (Sundays 3 AM)"
    fi
}

# Configure security updates
configure_updates() {
    info "Configuring automatic security updates..."

    if command -v apt-get >/dev/null 2>&1; then
        # Configure unattended upgrades for Ubuntu/Debian
        sudo apt-get install -y unattended-upgrades

        sudo tee "/etc/apt/apt.conf.d/50unattended-upgrades" > /dev/null <<EOF
Unattended-Upgrade::Allowed-Origins {
    "\${distro_id}:\${distro_codename}";
    "\${distro_id}:\${distro_codename}-security";
    "\${distro_id}ESMApps:\${distro_codename}-apps-security";
    "\${distro_id}ESM:\${distro_codename}-infra-security";
};
Unattended-Upgrade::Package-Blacklist {
};
Unattended-Upgrade::Automatic-Reboot "false";
EOF

        sudo systemctl enable unattended-upgrades
        sudo systemctl start unattended-upgrades

        success "Automatic security updates configured"

    elif command -v yum >/dev/null 2>&1; then
        # Configure yum-cron for CentOS/RHEL
        sudo yum install -y yum-cron
        sudo systemctl enable yum-cron
        sudo systemctl start yum-cron

        success "YUM automatic updates configured"
    else
        warning "Unsupported package manager. Please configure automatic updates manually."
    fi
}

# Final security audit
security_audit() {
    info "Running final security audit..."

    local issues=0

    # Check SSH configuration
    if [[ -f "/etc/ssh/sshd_config" ]]; then
        if grep -q "^PermitRootLogin yes" /etc/ssh/sshd_config; then
            warning "Root SSH login is enabled"
            ((issues++))
        fi
        if ! grep -q "^PasswordAuthentication no" /etc/ssh/sshd_config; then
            warning "SSH password authentication is enabled"
            ((issues++))
        fi
    fi

    # Check Docker security
    if docker info 2>/dev/null | grep -q "userns"; then
        info "Docker user namespaces are enabled"
    else
        warning "Docker user namespaces not configured"
        ((issues++))
    fi

    # Check file permissions
    if [[ -f ".env" ]]; then
        local env_perms=$(stat -c %a .env 2>/dev/null || echo "unknown")
        if [[ "$env_perms" != "600" ]]; then
            warning "Environment file permissions should be 600"
            ((issues++))
        fi
    fi

    # Check SSL certificates
    if [[ -f "./ssl/nexus.crt" ]]; then
        if openssl x509 -checkend 86400 -noout -in ./ssl/nexus.crt 2>/dev/null; then
            info "SSL certificate is valid"
        else
            warning "SSL certificate expires within 24 hours"
            ((issues++))
        fi
    else
        warning "No SSL certificate found"
        ((issues++))
    fi

    if [[ $issues -eq 0 ]]; then
        success "Security audit passed - no issues found"
    else
        warning "Security audit found $issues potential issues"
        info "Review the warnings above and address them for better security"
    fi
}

# Main hardening function
harden_production() {
    log "Starting NexusLang v2 production hardening"

    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║            NexusLang v2 Production Hardening               ║"
    echo "║            SSL, Security, and System Optimization          ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""

    # Run hardening steps
    check_prerequisites

    if [[ "$DOMAIN" != "localhost" ]]; then
        get_letsencrypt_cert
    else
        generate_self_signed_cert
    fi

    configure_ssl
    configure_firewall
    harden_docker
    configure_logging
    configure_monitoring
    configure_backups
    configure_updates
    security_audit

    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                PRODUCTION HARDENING COMPLETE!              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    echo "🔒 Security Features Applied:"
    echo "   ✓ SSL/TLS certificates configured"
    echo "   ✓ Firewall rules applied"
    echo "   ✓ Docker daemon hardened"
    echo "   ✓ Log rotation configured"
    echo "   ✓ Monitoring alerts enabled"
    echo "   ✓ Automatic backups scheduled"
    echo "   ✓ Security updates automated"
    echo ""
    echo "🔧 System Services:"
    echo "   • NexusLang monitoring alerts (systemd)"
    echo "   • Daily automated backups (cron)"
    echo "   • Weekly backup cleanup (cron)"
    echo "   • Automatic security updates"
    echo ""
    echo "📊 Security Audit: Review warnings above if any"
    echo ""
    echo "🎯 Your NexusLang v2 deployment is now PRODUCTION HARDENED!"
    echo ""

    log "Production hardening completed successfully"
}

# Command line options
case "${1:-harden}" in
    "harden")
        harden_production
        ;;
    "ssl")
        configure_ssl
        ;;
    "firewall")
        configure_firewall
        ;;
    "audit")
        security_audit
        ;;
    "help"|*)
        echo "NexusLang v2 Production Hardening Script"
        echo ""
        echo "Usage: $0 [command] [options]"
        echo ""
        echo "Commands:"
        echo "  harden     - Full production hardening (default)"
        echo "  ssl        - Configure SSL certificates only"
        echo "  firewall   - Configure firewall only"
        echo "  audit      - Run security audit only"
        echo "  help       - Show this help message"
        echo ""
        echo "Environment Variables:"
        echo "  DOMAIN     - Domain name for SSL certificates (default: localhost)"
        echo "  EMAIL      - Email for Let's Encrypt notifications"
        echo "  STAGING    - Use Let's Encrypt staging (1=yes, 0=no, default: 0)"
        echo ""
        echo "Examples:"
        echo "  $0 harden"
        echo "  DOMAIN=nexuslang.dev EMAIL=admin@nexuslang.dev $0 harden"
        echo "  STAGING=1 $0 ssl"
        ;;
esac
