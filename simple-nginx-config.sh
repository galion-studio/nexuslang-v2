#!/bin/bash
# Simple nginx configuration for Galion Platform

echo "🔧 SIMPLE NGINX CONFIG FOR GALION"
echo "================================="

# Stop nginx
pkill nginx 2>/dev/null || true

# Create simple config (just the essentials)
cat > /etc/nginx/sites-available/galion-simple << 'EOF'
# Simple Galion Platform Configuration

upstream backend_api { server localhost:8000; }
upstream galion_app { server localhost:3000; }
upstream developer_platform { server localhost:3003; }
upstream galion_studio { server localhost:3030; }

# Main server on port 8080
server {
    listen 8080;
    server_name galion.app www.galion.app;

    # Galion App
    location / {
        proxy_pass http://galion_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# API server
server {
    listen 8080;
    server_name api.galion.app;

    location / {
        proxy_pass http://backend_api;
        proxy_set_header Host $host;
    }

    location /health {
        proxy_pass http://backend_api/health;
        access_log off;
    }
}

# Developer server
server {
    listen 8080;
    server_name developer.galion.app;

    location / {
        proxy_pass http://developer_platform;
        proxy_set_header Host $host;
    }
}

# Studio server
server {
    listen 8080;
    server_name galion.studio www.galion.studio;

    location / {
        proxy_pass http://galion_studio;
        proxy_set_header Host $host;
    }
}
EOF

# Enable the config
ln -sf /etc/nginx/sites-available/galion-simple /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
rm -f /etc/nginx/sites-enabled/galion-platform

# Test and start
if nginx -t; then
    echo "✅ Nginx config is valid"
    nginx
    echo "✅ Nginx started on port 8080"

    # Test nginx
    sleep 2
    if curl -s -I http://localhost:8080 | head -1 | grep -q "301\|404\|200"; then
        echo "✅ Nginx responding"
    else
        echo "❌ Nginx not responding"
    fi
else
    echo "❌ Nginx config error:"
    nginx -t
fi
