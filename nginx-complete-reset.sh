#!/bin/bash
# Complete nginx configuration reset

echo "🔄 COMPLETE NGINX RESET"
echo "======================="

# Stop nginx completely
echo "1. Stopping nginx..."
pkill -9 nginx 2>/dev/null || true
sleep 2

# Backup current config
cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.corrupted.$(date +%s)

# Restore clean default nginx config
echo "2. Restoring clean nginx configuration..."
cat > /etc/nginx/nginx.conf << 'EOF'
user www-data;
worker_processes auto;
pid /run/nginx.pid;
include /etc/nginx/modules-enabled/*.conf;

events {
    worker_connections 768;
}

http {
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    ssl_protocols TLSv1 TLSv1.1 TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;

    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;

    gzip on;

    # Include server configurations
    include /etc/nginx/conf.d/*.conf;
    include /etc/nginx/sites-enabled/*;
}
EOF

# Remove any broken site configurations
echo "3. Removing broken configurations..."
rm -f /etc/nginx/sites-enabled/galion-platform
rm -f /etc/nginx/sites-available/galion-platform

# Test the clean config
echo "4. Testing clean nginx configuration..."
if nginx -t; then
    echo "✅ Clean nginx config is valid"
else
    echo "❌ Even clean config has issues"
    exit 1
fi

# Start nginx with clean config
echo "5. Starting nginx with clean configuration..."
nginx

# Wait a moment
sleep 3

# Check if nginx is running
if pgrep nginx > /dev/null; then
    echo "✅ Nginx started successfully"

    # Test basic functionality
    if curl -s -I http://localhost | head -1 | grep -q "200\|404"; then
        echo "✅ Nginx responding on port 80"
    else
        echo "⚠️  Nginx running but not responding on port 80"
    fi
else
    echo "❌ Nginx failed to start"
    exit 1
fi

echo ""
echo "======================="
echo "Nginx reset complete!"
echo ""
echo "Next: Run your Galion Platform setup script to configure nginx properly"
echo "======================="
