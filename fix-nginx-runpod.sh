#!/bin/bash
# Fix nginx configuration for RunPod

echo "🔧 Fixing Nginx Configuration for RunPod"
echo "========================================"

# Remove the conflicting default config
echo "1. Removing conflicting default config..."
rm -f /etc/nginx/sites-enabled/default

# Add our custom server blocks to the main nginx.conf
echo "2. Adding our server blocks to nginx.conf..."

# Create a backup first
cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.before_fix

# Add our server blocks before the closing brace of the http block
cat >> /etc/nginx/nginx.conf << 'EOF'

    # ============================================
    # GALION.STUDIO DOMAIN
    # ============================================

    # Main Domain - galion.studio (redirects to galion.app)
    server {
        listen 80;
        server_name galion.studio www.galion.studio;
        return 301 https://galion.app$request_uri;
    }

    # ============================================
    # GALION.APP DOMAIN
    # ============================================

    # Main Domain - galion.app (points to main app)
    server {
        listen 80;
        server_name galion.app www.galion.app;

        location / {
            proxy_pass http://localhost:3000;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }

        location /_next/static {
            proxy_pass http://localhost:3000;
            proxy_cache_valid 200 60m;
            add_header Cache-Control "public, immutable";
        }
    }

    # API Subdomain - api.galion.app
    server {
        listen 80;
        server_name api.galion.app;

        client_max_body_size 100M;
        proxy_buffer_size 128k;
        proxy_buffers 4 256k;
        proxy_busy_buffers_size 256k;

        location / {
            proxy_pass http://localhost:8000;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header X-Forwarded-Host $host;
            proxy_set_header CF-Connecting-IP $http_cf_connecting_ip;
            proxy_set_header CF-RAY $http_cf_ray;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        location /docs {
            proxy_pass http://localhost:8000/docs;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
        }

        location /health {
            proxy_pass http://localhost:8000/health;
            access_log off;
        }
    }

    # Developer Subdomain - developer.galion.app
    server {
        listen 80;
        server_name developer.galion.app;

        location / {
            proxy_pass http://localhost:3003;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }

        location /_next/static {
            proxy_pass http://localhost:3003;
            proxy_cache_valid 200 60m;
            add_header Cache-Control "public, immutable";
        }
    }

}

EOF

# Remove the include line we added earlier that caused issues
sed -i '/include \/etc\/nginx\/sites-enabled\/\*/d' /etc/nginx/nginx.conf

# Remove the broken config file
rm -f /etc/nginx/sites-enabled/galion-platform

echo "3. Testing nginx configuration..."
nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Configuration test passed!"
    echo "4. Starting nginx..."
    pkill -9 nginx 2>/dev/null
    nginx

    echo "5. Checking if port 80 is listening..."
    sleep 2
    ss -tlnp | grep :80

    echo "6. Testing local nginx..."
    curl -I http://localhost 2>/dev/null | head -3

    echo ""
    echo "🎉 Nginx fixed! Test your domains:"
    echo "   curl -I https://galion.app"
    echo "   curl -I https://api.galion.app/health"
    echo "   curl -I https://developer.galion.app"
    echo "   curl -I https://galion.studio"

else
    echo "❌ Configuration test failed. Restoring backup..."
    cp /etc/nginx/nginx.conf.before_fix /etc/nginx/nginx.conf
fi

echo "========================================"
echo "Fix complete"
echo "========================================"
