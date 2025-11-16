#!/bin/bash
# ============================================
# GALION SSL SETUP SCRIPT
# ============================================
# Automated SSL certificate setup with Let's Encrypt

set -e

echo "🔒 Setting up SSL certificates for Galion domains..."

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

# Check if certbot is installed
if ! command -v certbot &> /dev/null; then
    echo "📦 Installing Certbot..."
    apt update
    apt install -y certbot python3-certbot-nginx
fi

# Function to get certificate for a domain
get_certificate() {
    local domain=$1
    local extra_args=$2

    echo "🔐 Getting SSL certificate for $domain..."

    if certbot certificates --domain $domain | grep -q "Certificate Name: $domain"; then
        echo -e "${YELLOW}⚠️  Certificate for $domain already exists. Renewing...${NC}"
        certbot renew --cert-name $domain
    else
        certbot --nginx -d $domain $extra_args --non-interactive --agree-tos --email admin@galion.app
    fi
}

# Get certificates for all domains
echo "🌐 Configuring SSL for Galion domains..."

# Main app
get_certificate "galion.app" "-d www.galion.app"

# API gateway
get_certificate "api.galion.app"

# Developer platform
get_certificate "developer.galion.app"

# Test certificates
echo "🧪 Testing SSL certificates..."
if openssl s_client -connect galion.app:443 -servername galion.app < /dev/null 2>/dev/null | openssl x509 -noout -dates >/dev/null 2>&1; then
    echo -e "${GREEN}✅ SSL certificates are valid${NC}"
else
    echo -e "${RED}❌ SSL certificate validation failed${NC}"
    exit 1
fi

# Set up auto-renewal
echo "🔄 Setting up automatic certificate renewal..."
(crontab -l ; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -

# Restart nginx to apply certificates
echo "🔄 Restarting nginx..."
systemctl restart nginx

# Verify HTTPS is working
echo "✅ Verifying HTTPS setup..."
if curl -s -I https://galion.app | grep -q "HTTP/2 200"; then
    echo -e "${GREEN}✅ HTTPS is working correctly${NC}"
else
    echo -e "${YELLOW}⚠️  HTTPS may not be fully configured yet${NC}"
fi

echo ""
echo -e "${GREEN}🎉 SSL setup complete!${NC}"
echo ""
echo "🔒 Your domains are now secured with Let's Encrypt SSL:"
echo "   - https://galion.app"
echo "   - https://www.galion.app"
echo "   - https://api.galion.app"
echo "   - https://developer.galion.app"
echo ""
echo "📅 Certificates will auto-renew monthly"
echo ""
echo "🧪 Test your setup:"
echo "   curl -I https://galion.app"
echo "   curl -I https://api.galion.app/health"

