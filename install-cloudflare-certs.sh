#!/bin/bash
# Quick Script to Install Cloudflare Origin Certificates
# Fixes: ERR_SSL_VERSION_OR_CIPHER_MISMATCH error

set -e  # Exit on any error

echo "============================================"
echo "Cloudflare Origin Certificate Installer"
echo "============================================"
echo ""
echo "This script will help you install Cloudflare Origin Certificates"
echo "to fix the SSL error on api.developer.galion.app"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ ERROR: Please run as root (use sudo)"
    exit 1
fi

echo "Step 1: Creating certificate directory..."
mkdir -p /etc/cloudflare/certs
echo "✅ Directory created: /etc/cloudflare/certs"
echo ""

echo "============================================"
echo "Step 2: Get Your Cloudflare Origin Certificate"
echo "============================================"
echo ""
echo "1. Open: https://dash.cloudflare.com/"
echo "2. Select your 'galion.app' domain"
echo "3. Go to: SSL/TLS → Origin Server"
echo "4. Click: 'Create Certificate'"
echo "5. Add hostnames:"
echo "   - developer.galion.app"
echo "   - api.developer.galion.app"
echo "   - *.developer.galion.app"
echo "6. Set validity: 15 years"
echo "7. Click 'Create'"
echo ""
echo "Press ENTER when you have the certificate and key ready..."
read -r

echo ""
echo "============================================"
echo "Step 3: Install Certificate"
echo "============================================"
echo ""
echo "Opening nano editor for CERTIFICATE..."
echo "Paste the CERTIFICATE (the long text starting with -----BEGIN CERTIFICATE-----)"
echo "Then press: Ctrl+X, then Y, then Enter"
echo ""
echo "Press ENTER to open editor..."
read -r

nano /etc/cloudflare/certs/developer.galion.app.pem

echo ""
echo "✅ Certificate saved!"
echo ""

echo "============================================"
echo "Step 4: Install Private Key"
echo "============================================"
echo ""
echo "Opening nano editor for PRIVATE KEY..."
echo "Paste the PRIVATE KEY (the long text starting with -----BEGIN PRIVATE KEY-----)"
echo "Then press: Ctrl+X, then Y, then Enter"
echo ""
echo "Press ENTER to open editor..."
read -r

nano /etc/cloudflare/certs/developer.galion.app.key

echo ""
echo "✅ Private key saved!"
echo ""

echo "Step 5: Setting file permissions..."
chmod 644 /etc/cloudflare/certs/developer.galion.app.pem
chmod 600 /etc/cloudflare/certs/developer.galion.app.key
chown root:root /etc/cloudflare/certs/*
echo "✅ Permissions set correctly"
echo ""

echo "Step 6: Verifying certificate files..."
if [ ! -s /etc/cloudflare/certs/developer.galion.app.pem ]; then
    echo "❌ ERROR: Certificate file is empty!"
    exit 1
fi

if [ ! -s /etc/cloudflare/certs/developer.galion.app.key ]; then
    echo "❌ ERROR: Private key file is empty!"
    exit 1
fi

echo "✅ Certificate files verified"
echo ""

echo "Step 7: Updating Nginx configuration..."
NGINX_CONF="/etc/nginx/sites-available/developer.galion.app"

if [ -f "$NGINX_CONF" ]; then
    # Create backup
    cp "$NGINX_CONF" "$NGINX_CONF.backup.$(date +%Y%m%d_%H%M%S)"
    echo "✅ Backup created: $NGINX_CONF.backup.*"
    
    # Update certificate paths
    sed -i 's|#.*ssl_certificate /etc/cloudflare/certs/developer.galion.app.pem;|ssl_certificate /etc/cloudflare/certs/developer.galion.app.pem;|g' "$NGINX_CONF"
    sed -i 's|#.*ssl_certificate_key /etc/cloudflare/certs/developer.galion.app.key;|ssl_certificate_key /etc/cloudflare/certs/developer.galion.app.key;|g' "$NGINX_CONF"
    
    # Comment out Let's Encrypt paths
    sed -i 's|^\s*ssl_certificate /etc/letsencrypt/|#ssl_certificate /etc/letsencrypt/|g' "$NGINX_CONF"
    sed -i 's|^\s*ssl_certificate_key /etc/letsencrypt/|#ssl_certificate_key /etc/letsencrypt/|g' "$NGINX_CONF"
    
    echo "✅ Nginx configuration updated"
else
    echo "⚠️  WARNING: Nginx config not found at $NGINX_CONF"
    echo "You'll need to manually update your nginx configuration"
    echo ""
    echo "Add these lines to your nginx config:"
    echo "    ssl_certificate /etc/cloudflare/certs/developer.galion.app.pem;"
    echo "    ssl_certificate_key /etc/cloudflare/certs/developer.galion.app.key;"
fi
echo ""

echo "Step 8: Testing Nginx configuration..."
if nginx -t; then
    echo "✅ Nginx configuration is valid!"
else
    echo "❌ ERROR: Nginx configuration test failed!"
    echo "Please check the error messages above"
    exit 1
fi
echo ""

echo "Step 9: Restarting Nginx..."
if systemctl restart nginx; then
    echo "✅ Nginx restarted successfully!"
else
    echo "❌ ERROR: Failed to restart Nginx"
    exit 1
fi
echo ""

echo "Step 10: Checking Nginx status..."
if systemctl is-active --quiet nginx; then
    echo "✅ Nginx is running!"
else
    echo "❌ WARNING: Nginx is not running!"
    systemctl status nginx
fi
echo ""

echo "============================================"
echo "✅ INSTALLATION COMPLETE!"
echo "============================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Test your site:"
echo "   curl -I https://developer.galion.app"
echo "   curl -I https://api.developer.galion.app"
echo ""
echo "2. Check SSL in browser:"
echo "   https://developer.galion.app"
echo "   https://api.developer.galion.app"
echo ""
echo "3. Test SSL certificate:"
echo "   openssl s_client -connect api.developer.galion.app:443 -servername api.developer.galion.app"
echo ""
echo "4. If still getting errors:"
echo "   - Clear browser cache"
echo "   - Wait 2-3 minutes for changes to propagate"
echo "   - Check Cloudflare SSL/TLS mode is 'Full (strict)'"
echo "   - Purge Cloudflare cache"
echo ""
echo "Certificate details:"
echo "  Certificate: /etc/cloudflare/certs/developer.galion.app.pem"
echo "  Private Key: /etc/cloudflare/certs/developer.galion.app.key"
echo ""
echo "For troubleshooting, see: FIX_SSL_ERROR.md"
echo ""
echo "Happy coding! 🚀"
echo ""

