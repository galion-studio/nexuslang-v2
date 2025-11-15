#!/bin/bash

# Galion Ecosystem - Fix Nginx Configuration
# Downloads and applies the correct nginx config for API proxy

set -e

echo "🔧 GALION ECOSYSTEM - NGINX CONFIG FIX"
echo "======================================"
echo ""

# Backup current config
echo "📋 Backing up current nginx config..."
sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup.$(date +%s)

# Apply new configuration
echo "⚙️  Applying new nginx configuration..."
sudo tee /etc/nginx/nginx.conf > /dev/null << 'EOF'
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;

    # Gzip
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # Upstream servers
    upstream galion_backend {
        server localhost:8000;
    }

    upstream galion_studio {
        server localhost:3001;
    }

    upstream developer_platform {
        server localhost:3002;
    }

    upstream galion_app {
        server localhost:3003;
    }

    # Main server block
    server {
        listen 80;
        server_name _;

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header Referrer-Policy "no-referrer-when-downgrade" always;

        # API proxy - Backend services
        location /api/ {
            proxy_pass http://galion_backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_cache_bypass $http_upgrade;
            add_header 'Access-Control-Allow-Origin' '*' always;
            add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
            add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization' always;
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
        }

        # Health check
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }

        # Default response for root
        location / {
            return 200 "Galion Ecosystem API Gateway\nAvailable endpoints:\n- /api/* (Backend API)\n- /health (Health check)\n";
            add_header Content-Type text/plain;
        }
    }
}
EOF

# Test configuration
echo "🧪 Testing nginx configuration..."
if sudo nginx -t 2>/dev/null; then
    echo "✅ Configuration is valid"
else
    echo "❌ Configuration has errors"
    sudo nginx -t
    exit 1
fi

# Restart nginx
echo "🔄 Restarting nginx..."
sudo nginx -s stop 2>/dev/null || true
sleep 1
sudo nginx

# Verify
echo "🔍 Verifying nginx is listening on port 80..."
if ss -tlnp | grep -q :80; then
    echo "✅ Nginx is listening on port 80"
else
    echo "❌ Nginx is not listening on port 80"
    exit 1
fi

# Test endpoints
echo "🧪 Testing endpoints..."
echo ""

echo "Testing /health:"
curl -s http://localhost/health
echo ""

echo "Testing /api/health:"
curl -s http://localhost/api/health
echo ""

echo "Testing root (/):"
curl -s http://localhost/
echo ""

echo ""
echo "🎉 NGINX CONFIGURATION FIXED SUCCESSFULLY!"
echo "=========================================="
echo ""
echo "📋 Your Galion Ecosystem API is now accessible:"
echo "   Health Check: http://[your-runpod-ip]/health"
echo "   API Endpoints: http://[your-runpod-ip]/api/*"
echo ""
echo "🔧 Remember to expose port 80 in RunPod dashboard!"
echo ""
echo "Script completed at: $(date)"
