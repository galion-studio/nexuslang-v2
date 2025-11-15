#!/bin/bash
# Galion Platform - Complete Automation Setup Script
# This script automates the entire setup process for RunPod deployment

set -e # Exit on any error

echo "🚀 GALION PLATFORM - COMPLETE AUTOMATION SETUP"
echo "=============================================="
echo "This script will:"
echo "  ✅ Deploy latest code from GitHub"
echo "  ✅ Install all dependencies"
echo "  ✅ Start all PM2 services"
echo "  ✅ Configure Nginx for multi-domain routing"
echo "  ✅ Test all services and domains"
echo ""
echo "RunPod IP: $(hostname -i)"
echo "Date: $(date)"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# ============================================
# STEP 1: DEPLOY LATEST CODE
# ============================================
log "Step 1: Deploying latest code from GitHub..."

cd /nexuslang-v2

# Fetch and reset to latest clean-nexuslang branch
log "Pulling latest code..."
git fetch origin
git reset --hard origin/clean-nexuslang

success "Code deployed successfully"

# ============================================
# STEP 2: INSTALL DEPENDENCIES
# ============================================
log "Step 2: Installing dependencies..."

# Python dependencies
log "Installing Python dependencies..."
pip3 install -q fastapi uvicorn psutil pydantic python-multipart

# Frontend dependencies
log "Installing frontend dependencies..."
cd galion-studio && npm install --silent && cd ..
cd galion-app && npm install --silent && npm install lucide-react --silent && cd ..
cd developer-platform && npm install --silent && cd ..

cd /nexuslang-v2
success "Dependencies installed"

# ============================================
# STEP 3: START PM2 SERVICES
# ============================================
log "Step 3: Starting PM2 services..."

# Delete existing services
pm2 delete all 2>/dev/null || true

# Start backend (FastAPI)
log "Starting backend service..."
cd v2/backend
pm2 start python3 --name backend -- main_simple.py --host 0.0.0.0 --port 8000
cd ../..

# Start galion-studio
log "Starting galion-studio..."
cd galion-studio
pm2 start npm --name galion-studio -- run dev -- -p 3030
cd ..

# Start galion-app
log "Starting galion-app..."
cd galion-app
pm2 start npm --name galion-app -- run dev -- -p 3000
cd ..

# Start developer-platform
log "Starting developer-platform..."
cd developer-platform
pm2 start npm --name developer-platform -- run dev -- -p 3003
cd ..

# Save PM2 configuration
pm2 save

success "PM2 services started"

# ============================================
# STEP 4: CONFIGURE NGINX
# ============================================
log "Step 4: Configuring Nginx for multi-domain routing..."

# Backup existing config
cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup.$(date +%Y%m%d_%H%M%S)

# Remove conflicting default config
rm -f /etc/nginx/sites-enabled/default

# Add our server blocks to nginx.conf
log "Adding server blocks to nginx.conf..."

# Create a backup
cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup.$(date +%Y%m%d_%H%M%S)

# Remove the conflicting default config
rm -f /etc/nginx/sites-enabled/default

# Remove the broken config file
rm -f /etc/nginx/sites-enabled/galion-platform

# Remove any include lines that were added previously
sed -i '/include \/etc\/nginx\/sites-enabled\/\*/d' /etc/nginx/nginx.conf

# Find the exact location of the closing brace for the http block
# and add our server blocks before it
HTTP_END_LINE=$(grep -n "^}$" /etc/nginx/nginx.conf | tail -1 | cut -d: -f1)

if [ -n "$HTTP_END_LINE" ]; then
    # Insert our server blocks before the last closing brace
    sed -i "${HTTP_END_LINE}i\\
    # ============================================\\
    # GALION.STUDIO DOMAIN\\
    # ============================================\\
\\
    # Main Domain - galion.studio (redirects to galion.app)\\
    server {\\
        listen 80;\\
        server_name galion.studio www.galion.studio;\\
        return 301 https://galion.app\$request_uri;\\
    }\\
\\
    # ============================================\\
    # GALION.APP DOMAIN\\
    # ============================================\\
\\
    # Main Domain - galion.app (points to main app)\\
    server {\\
        listen 80;\\
        server_name galion.app www.galion.app;\\
\\
        location / {\\
            proxy_pass http://localhost:3000;\\
            proxy_http_version 1.1;\\
            proxy_set_header Host \$host;\\
            proxy_set_header X-Real-IP \$remote_addr;\\
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;\\
            proxy_set_header X-Forwarded-Proto \$scheme;\\
            proxy_set_header Upgrade \$http_upgrade;\\
            proxy_set_header Connection \"upgrade\";\\
        }\\
\\
        location /_next/static {\\
            proxy_pass http://localhost:3000;\\
            proxy_cache_valid 200 60m;\\
            add_header Cache-Control \"public, immutable\";\\
        }\\
    }\\
\\
    # API Subdomain - api.galion.app\\
    server {\\
        listen 80;\\
        server_name api.galion.app;\\
\\
        client_max_body_size 100M;\\
        proxy_buffer_size 128k;\\
        proxy_buffers 4 256k;\\
        proxy_busy_buffers_size 256k;\\
\\
        location / {\\
            proxy_pass http://localhost:8000;\\
            proxy_http_version 1.1;\\
            proxy_set_header Host \$host;\\
            proxy_set_header X-Real-IP \$remote_addr;\\
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;\\
            proxy_set_header X-Forwarded-Proto \$scheme;\\
            proxy_set_header X-Forwarded-Host \$host;\\
            proxy_set_header CF-Connecting-IP \$http_cf_connecting_ip;\\
            proxy_set_header CF-RAY \$http_cf_ray;\\
            proxy_set_header Upgrade \$http_upgrade;\\
            proxy_set_header Connection \"upgrade\";\\
            proxy_connect_timeout 60s;\\
            proxy_send_timeout 60s;\\
            proxy_read_timeout 60s;\\
        }\\
\\
        location /docs {\\
            proxy_pass http://localhost:8000/docs;\\
            proxy_http_version 1.1;\\
            proxy_set_header Host \$host;\\
        }\\
\\
        location /health {\\
            proxy_pass http://localhost:8000/health;\\
            access_log off;\\
        }\\
    }\\
\\
    # Developer Subdomain - developer.galion.app\\
    server {\\
        listen 80;\\
        server_name developer.galion.app;\\
\\
        location / {\\
            proxy_pass http://localhost:3003;\\
            proxy_http_version 1.1;\\
            proxy_set_header Host \$host;\\
            proxy_set_header X-Real-IP \$remote_addr;\\
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;\\
            proxy_set_header X-Forwarded-Proto \$scheme;\\
            proxy_set_header Upgrade \$http_upgrade;\\
            proxy_set_header Connection \"upgrade\";\\
        }\\
\\
        location /_next/static {\\
            proxy_pass http://localhost:3003;\\
            proxy_cache_valid 200 60m;\\
            add_header Cache-Control \"public, immutable\";\\
        }\\
    }\\
" /etc/nginx/nginx.conf
else
    error "Could not find http block end in nginx.conf"
    exit 1
fi

# Test nginx configuration
log "Testing nginx configuration..."
if nginx -t; then
    success "Nginx configuration is valid"
else
    error "Nginx configuration test failed"
    exit 1
fi

# Restart nginx
log "Starting nginx..."
pkill -9 nginx 2>/dev/null || true
nginx

success "Nginx configured and started"

# ============================================
# STEP 5: TEST ALL SERVICES
# ============================================
log "Step 5: Testing all services..."

echo ""
echo "🔍 TESTING SERVICES"
echo "==================="

# Test PM2 services
echo "Testing PM2 services..."
pm2 status

# Test local service access
echo ""
echo "Testing local service access..."
echo -n "Backend API (port 8000): "
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health | grep -q "200\|404"; then
    success "Backend responding"
else
    warning "Backend not responding"
fi

echo -n "Galion App (port 3000): "
if curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 | grep -q "200\|404"; then
    success "Galion App responding"
else
    warning "Galion App not responding"
fi

echo -n "Developer Platform (port 3003): "
if curl -s -o /dev/null -w "%{http_code}" http://localhost:3003 | grep -q "200\|404"; then
    success "Developer Platform responding"
else
    warning "Developer Platform not responding"
fi

# Test nginx port 80
echo ""
echo "Testing nginx port 80..."
if ss -tlnp | grep -q ":80 "; then
    success "Nginx listening on port 80"
else
    error "Nginx not listening on port 80"
fi

# Test nginx proxy
echo -n "Nginx proxy (localhost): "
if curl -s -o /dev/null -w "%{http_code}" http://localhost | grep -q "200\|404\|301"; then
    success "Nginx proxy working"
else
    warning "Nginx proxy not working"
fi

# ============================================
# STEP 6: DISPLAY RESULTS AND NEXT STEPS
# ============================================
echo ""
echo "🎉 SETUP COMPLETE!"
echo "=================="

echo ""
echo "📊 SERVICE STATUS:"
pm2 status --no-interactive

echo ""
echo "🌐 NGINX CONFIGURATION:"
echo "Port 80 listening: $(ss -tlnp | grep -c ":80 " || echo "No")"
echo "Configuration file: /etc/nginx/nginx.conf"

echo ""
echo "🔗 EXTERNAL ACCESS:"
echo "RunPod IP: $(hostname -i)"
echo ""
echo "📋 DOMAINS TO CONFIGURE IN CLOUDFLARE:"
echo "• galion.studio → $(hostname -i) (redirects to galion.app)"
echo "• galion.app → $(hostname -i) (main app)"
echo "• api.galion.app → $(hostname -i) (backend API)"
echo "• developer.galion.app → $(hostname -i) (developer platform)"
echo ""
echo "📄 CLOUDFLARE DNS RECORDS:"
echo "See: cloudflare-dns-galion-studio.txt"
echo "See: cloudflare-dns-galion-app.txt"

echo ""
echo "🧪 TEST COMMANDS:"
echo "curl -I https://galion.app"
echo "curl -I https://api.galion.app/health"
echo "curl -I https://developer.galion.app"
echo "curl -I https://galion.studio"

echo ""
echo "📝 LOGS:"
echo "pm2 logs"
echo "tail -f /var/log/nginx/access.log"
echo "tail -f /var/log/nginx/error.log"

echo ""
success "Galion Platform setup completed successfully!"
echo "Configure Cloudflare DNS records to enable external access."

# Create a summary log
echo "
=== GALION PLATFORM SETUP SUMMARY ===
Date: $(date)
RunPod IP: $(hostname -i)
Services: $(pm2 list | grep -c online || echo "Check PM2")
Nginx Port 80: $(ss -tlnp | grep -c ":80 " || echo "Check nginx")
Git Commit: $(git rev-parse --short HEAD)
=====================================
" > /nexuslang-v2/setup-summary.log

echo "Summary saved to: /nexuslang-v2/setup-summary.log"
