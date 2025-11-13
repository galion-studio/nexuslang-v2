#!/bin/bash
# Complete Nginx Setup for RunPod
# Reverse proxy for all Galion services

echo "🔧 Setting up Nginx on RunPod..."

# Install Nginx
apt-get update -qq
apt-get install -y nginx

# Stop default nginx
systemctl stop nginx 2>/dev/null || /etc/init.d/nginx stop

# Create Nginx config for galion.studio
cat > /etc/nginx/sites-available/galion.studio << 'EOF'
server {
    listen 80;
    listen [::]:80;
    server_name galion.studio www.galion.studio;

    # Redirect to HTTPS (Cloudflare handles SSL)
    # Cloudflare sends requests as HTTP to origin
    
    location / {
        proxy_pass http://localhost:3002;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
EOF

# Create config for api.studio.galion.app
cat > /etc/nginx/sites-available/api.studio.galion.app << 'EOF'
server {
    listen 80;
    listen [::]:80;
    server_name api.studio.galion.app;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
EOF

# Create config for studio.galion.app (if you want subdomain too)
cat > /etc/nginx/sites-available/studio.galion.app << 'EOF'
server {
    listen 80;
    listen [::]:80;
    server_name studio.galion.app;

    location / {
        proxy_pass http://localhost:3002;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
EOF

# Enable sites
ln -sf /etc/nginx/sites-available/galion.studio /etc/nginx/sites-enabled/
ln -sf /etc/nginx/sites-available/api.studio.galion.app /etc/nginx/sites-enabled/
ln -sf /etc/nginx/sites-available/studio.galion.app /etc/nginx/sites-enabled/

# Remove default site
rm -f /etc/nginx/sites-enabled/default

# Test configuration
nginx -t

# Start Nginx
systemctl start nginx 2>/dev/null || /etc/init.d/nginx start

echo "✅ Nginx configured and started!"
echo ""
echo "Configured domains:"
echo "  - galion.studio → localhost:3002"
echo "  - www.galion.studio → localhost:3002"
echo "  - studio.galion.app → localhost:3002"
echo "  - api.studio.galion.app → localhost:8000"
echo ""
echo "Services must be running on:"
echo "  - Port 8000: Backend API"
echo "  - Port 3002: Galion Studio"

