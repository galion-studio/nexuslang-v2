#!/bin/bash
# ============================================
# GALION NGINX SETUP SCRIPT
# ============================================
# Automated nginx configuration for production deployment

set -e

echo "🚀 Setting up Nginx for Galion Voice API..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}This script must be run as root${NC}"
   exit 1
fi

# Install nginx if not present
if ! command -v nginx &> /dev/null; then
    echo "📦 Installing Nginx..."
    apt update
    apt install -y nginx
fi

# Create directories
echo "📁 Creating directories..."
mkdir -p /etc/nginx/sites-available
mkdir -p /etc/nginx/sites-enabled
mkdir -p /var/www/galion-app
mkdir -p /var/www/developer-galion
mkdir -p /var/www/letsencrypt
mkdir -p /var/log/nginx/galion

# Copy configuration files
echo "📋 Copying nginx configurations..."

# Main nginx.conf
cp nginx/nginx.conf /etc/nginx/nginx.conf

# Site configurations
cp nginx/sites-available/galion-voice-api /etc/nginx/sites-available/
cp nginx/sites-available/api.galion.app /etc/nginx/sites-available/
cp nginx/sites-available/developer.galion.app /etc/nginx/sites-available/

# Enable sites
ln -sf /etc/nginx/sites-available/galion-voice-api /etc/nginx/sites-enabled/
ln -sf /etc/nginx/sites-available/api.galion.app /etc/nginx/sites-enabled/
ln -sf /etc/nginx/sites-available/developer.galion.app /etc/nginx/sites-enabled/

# Remove default nginx site if it exists
rm -f /etc/nginx/sites-enabled/default

# Set proper permissions
chown -R www-data:www-data /var/www/
chmod -R 755 /var/www/

# Create log rotation
cat > /etc/logrotate.d/galion-nginx << EOF
/var/log/nginx/galion/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data adm
    postrotate
        systemctl reload nginx
    endscript
}
EOF

# Test nginx configuration
echo "🧪 Testing nginx configuration..."
if nginx -t; then
    echo -e "${GREEN}✅ Nginx configuration is valid${NC}"
else
    echo -e "${RED}❌ Nginx configuration has errors${NC}"
    exit 1
fi

# Create systemd service override for better performance
mkdir -p /etc/systemd/system/nginx.service.d
cat > /etc/systemd/system/nginx.service.d/override.conf << EOF
[Service]
LimitNOFILE=65536
EOF

# Reload systemd and restart nginx
systemctl daemon-reload
systemctl enable nginx
systemctl restart nginx

# Check if nginx is running
if systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✅ Nginx started successfully${NC}"
else
    echo -e "${RED}❌ Nginx failed to start${NC}"
    systemctl status nginx
    exit 1
fi

echo ""
echo -e "${GREEN}🎉 Nginx setup complete!${NC}"
echo ""
echo "📋 Next steps:"
echo "1. Configure DNS for your domains:"
echo "   - galion.app → your-server-ip"
echo "   - api.galion.app → your-server-ip"
echo "   - developer.galion.app → your-server-ip"
echo ""
echo "2. Get SSL certificates:"
echo "   certbot --nginx -d galion.app -d www.galion.app"
echo "   certbot --nginx -d api.galion.app"
echo "   certbot --nginx -d developer.galion.app"
echo ""
echo "3. Deploy your applications:"
echo "   - Frontend: Build and copy to /var/www/galion-app/"
echo "   - Backend: Run on port 8000"
echo ""
echo "4. Test the setup:"
echo "   curl -I https://galion.app"
echo "   curl -I https://api.galion.app/health"
echo ""
echo -e "${YELLOW}⚠️  Remember to update firewall rules for ports 80, 443${NC}"

