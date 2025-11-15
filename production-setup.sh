#!/bin/bash
# Production-Ready Galion Platform Setup
# This script sets up everything correctly and makes it production-ready

set -e  # Exit on any error

echo "🚀 GALION PLATFORM - PRODUCTION SETUP"
echo "======================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================
# STEP 1: VERIFY ENVIRONMENT
# ============================================
echo -e "${BLUE}1️⃣  VERIFYING ENVIRONMENT${NC}"
echo "============================"

# Check if we're in the right directory
if [ ! -d "v2/backend" ]; then
    echo -e "${RED}❌ Error: Not in /nexuslang-v2 directory${NC}"
    echo "Please run: cd /nexuslang-v2 && bash production-setup.sh"
    exit 1
fi

# Verify main_simple.py exists
if [ ! -f "v2/backend/main_simple.py" ]; then
    echo -e "${RED}❌ Error: v2/backend/main_simple.py not found${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Environment verified${NC}"
echo "   Working directory: $(pwd)"
echo "   Backend file: v2/backend/main_simple.py"
echo ""

# ============================================
# STEP 2: CLEAN UP EXISTING SERVICES
# ============================================
echo -e "${BLUE}2️⃣  CLEANING UP EXISTING SERVICES${NC}"
echo "===================================="

# Stop PM2
pm2 kill 2>/dev/null || true

# Stop Nginx
pkill -9 nginx 2>/dev/null || true

# Clean up any hanging processes
pkill -f "main_simple.py" 2>/dev/null || true
pkill -f "next-server" 2>/dev/null || true

sleep 2
echo -e "${GREEN}✅ All services stopped${NC}"
echo ""

# ============================================
# STEP 3: INSTALL DEPENDENCIES
# ============================================
echo -e "${BLUE}3️⃣  INSTALLING DEPENDENCIES${NC}"
echo "============================="

echo "Installing Python dependencies..."
pip3 install -q fastapi uvicorn psutil pydantic starlette python-multipart 2>&1 | grep -v "Requirement already satisfied" || true
echo -e "${GREEN}✅ Python dependencies installed${NC}"

if [ -d "galion-studio" ]; then
    echo "Installing galion-studio dependencies..."
    cd galion-studio
    npm install --silent 2>&1 | tail -1
    npm install react-hot-toast lucide-react clsx tailwind-merge --silent 2>&1 | tail -1
    cd ..
    echo -e "${GREEN}✅ Galion Studio dependencies installed${NC}"
fi

echo ""

# ============================================
# STEP 4: CONFIGURE NGINX
# ============================================
echo -e "${BLUE}4️⃣  CONFIGURING NGINX${NC}"
echo "======================"

# Remove old configs
rm -f /etc/nginx/sites-enabled/* 2>/dev/null || true

# Create clean nginx.conf
cat > /etc/nginx/nginx.conf << 'NGINXCONF'
user www-data;
worker_processes auto;
pid /run/nginx.pid;
error_log /var/log/nginx/error.log warn;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    
    access_log /var/log/nginx/access.log main;
    
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 100M;
    
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss application/rss+xml font/truetype font/opentype application/vnd.ms-fontobject image/svg+xml;
    
    include /etc/nginx/sites-enabled/*;
}
NGINXCONF

# Create production site config
cat > /etc/nginx/sites-available/galion << 'SITECONF'
# Galion Platform - Production Configuration

upstream backend_api {
    server 127.0.0.1:8000 max_fails=3 fail_timeout=30s;
    keepalive 32;
}

upstream galion_studio {
    server 127.0.0.1:3030 max_fails=3 fail_timeout=30s;
    keepalive 32;
}

server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # Main application
    location / {
        proxy_pass http://galion_studio;
        proxy_http_version 1.1;
        
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
        proxy_send_timeout 300s;
    }
    
    # API endpoints
    location /api/ {
        proxy_pass http://backend_api/;
        proxy_http_version 1.1;
        
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
    
    # Health check endpoint
    location /health {
        proxy_pass http://backend_api/health;
        access_log off;
        proxy_read_timeout 10s;
    }
    
    # API documentation
    location /docs {
        proxy_pass http://backend_api/docs;
        proxy_set_header Host $host;
    }
}
SITECONF

ln -sf /etc/nginx/sites-available/galion /etc/nginx/sites-enabled/

# Test nginx config
if nginx -t 2>&1 | grep -q "successful"; then
    echo -e "${GREEN}✅ Nginx configured successfully${NC}"
else
    echo -e "${RED}❌ Nginx configuration failed${NC}"
    nginx -t
    exit 1
fi

echo ""

# ============================================
# STEP 5: CREATE PM2 ECOSYSTEM FILE
# ============================================
echo -e "${BLUE}5️⃣  CREATING PM2 ECOSYSTEM${NC}"
echo "==========================="

cat > ecosystem.config.js << 'ECOCONF'
module.exports = {
  apps: [
    {
      name: 'backend',
      script: 'python3',
      args: 'main_simple.py --host 0.0.0.0 --port 8000',
      cwd: '/nexuslang-v2/v2/backend',
      interpreter: 'none',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      env: {
        NODE_ENV: 'production',
        PYTHONUNBUFFERED: '1'
      },
      error_file: '/root/.pm2/logs/backend-error.log',
      out_file: '/root/.pm2/logs/backend-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true
    },
    {
      name: 'galion-studio',
      script: 'npm',
      args: 'run dev -- -p 3030 -H 0.0.0.0',
      cwd: '/nexuslang-v2/galion-studio',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        NODE_ENV: 'production',
        PORT: '3030'
      },
      error_file: '/root/.pm2/logs/galion-studio-error.log',
      out_file: '/root/.pm2/logs/galion-studio-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true
    }
  ]
};
ECOCONF

echo -e "${GREEN}✅ PM2 ecosystem file created${NC}"
echo ""

# ============================================
# STEP 6: START SERVICES WITH PM2
# ============================================
echo -e "${BLUE}6️⃣  STARTING SERVICES${NC}"
echo "======================"

# Start services using ecosystem file
pm2 start ecosystem.config.js

sleep 5

echo -e "${GREEN}✅ Services started${NC}"
echo ""

# ============================================
# STEP 7: START NGINX
# ============================================
echo -e "${BLUE}7️⃣  STARTING NGINX${NC}"
echo "==================="

nginx

if pgrep nginx > /dev/null; then
    echo -e "${GREEN}✅ Nginx started successfully${NC}"
else
    echo -e "${RED}❌ Nginx failed to start${NC}"
    exit 1
fi

echo ""

# ============================================
# STEP 8: SAVE PM2 CONFIGURATION
# ============================================
echo -e "${BLUE}8️⃣  SAVING PM2 CONFIGURATION${NC}"
echo "=============================="

pm2 save
pm2 startup 2>/dev/null || true

echo -e "${GREEN}✅ PM2 configuration saved${NC}"
echo ""

# ============================================
# STEP 9: WAIT FOR SERVICES TO START
# ============================================
echo -e "${BLUE}9️⃣  WAITING FOR SERVICES${NC}"
echo "========================="

echo "Waiting 15 seconds for services to fully initialize..."
sleep 15

echo ""

# ============================================
# STEP 10: HEALTH CHECKS
# ============================================
echo -e "${BLUE}🔟 RUNNING HEALTH CHECKS${NC}"
echo "========================="

HEALTH_PASS=0
HEALTH_FAIL=0

# Test backend
echo -n "Backend API (port 8000): "
if curl -sf --max-time 10 http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ HEALTHY${NC}"
    HEALTH_PASS=$((HEALTH_PASS + 1))
else
    echo -e "${RED}❌ UNHEALTHY${NC}"
    HEALTH_FAIL=$((HEALTH_FAIL + 1))
fi

# Test galion studio
echo -n "Galion Studio (port 3030): "
if curl -sf --max-time 10 http://localhost:3030 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ HEALTHY${NC}"
    HEALTH_PASS=$((HEALTH_PASS + 1))
else
    echo -e "${RED}❌ UNHEALTHY${NC}"
    HEALTH_FAIL=$((HEALTH_FAIL + 1))
fi

# Test nginx
echo -n "Nginx (port 80): "
if curl -sf --max-time 10 http://localhost > /dev/null 2>&1; then
    echo -e "${GREEN}✅ HEALTHY${NC}"
    HEALTH_PASS=$((HEALTH_PASS + 1))
else
    echo -e "${RED}❌ UNHEALTHY${NC}"
    HEALTH_FAIL=$((HEALTH_FAIL + 1))
fi

echo ""

# ============================================
# STEP 11: DISPLAY STATUS
# ============================================
echo -e "${BLUE}📊 SERVICE STATUS${NC}"
echo "=================="
echo ""

pm2 list

echo ""
echo "Nginx processes:"
ps aux | grep nginx | grep -v grep | head -5

echo ""

# ============================================
# FINAL SUMMARY
# ============================================
echo ""
echo "=========================================="
if [ $HEALTH_FAIL -eq 0 ]; then
    echo -e "${GREEN}🎉 PRODUCTION SETUP COMPLETE!${NC}"
    echo "=========================================="
    echo ""
    echo -e "${GREEN}✅ All services are healthy and running!${NC}"
    echo ""
    echo "📊 Health Check Results:"
    echo "   ✅ $HEALTH_PASS services healthy"
    echo "   ❌ $HEALTH_FAIL services unhealthy"
    echo ""
    echo "🌐 Access Your Platform:"
    echo "   • Local: http://localhost"
    echo "   • Backend API: http://localhost:8000/health"
    echo "   • API Docs: http://localhost:8000/docs"
    echo ""
    echo "🔍 Find Your RunPod Public URL:"
    echo "   1. Go to RunPod Dashboard"
    echo "   2. Click on your pod"
    echo "   3. Look for 'HTTP Ports' or 'Connect' section"
    echo "   4. Copy your public URL"
    echo ""
    echo "📝 Useful Commands:"
    echo "   pm2 list          - Check service status"
    echo "   pm2 logs          - View all logs"
    echo "   pm2 logs backend  - View backend logs"
    echo "   pm2 restart all   - Restart all services"
    echo "   pm2 monit         - Real-time monitoring"
    echo ""
    echo -e "${GREEN}🚀 Your Galion Platform is production-ready!${NC}"
else
    echo -e "${YELLOW}⚠️  SETUP COMPLETE WITH WARNINGS${NC}"
    echo "=========================================="
    echo ""
    echo -e "${YELLOW}Some services may need attention:${NC}"
    echo "   ✅ $HEALTH_PASS services healthy"
    echo "   ❌ $HEALTH_FAIL services unhealthy"
    echo ""
    echo "🔍 Troubleshooting:"
    echo "   pm2 logs          - View all logs"
    echo "   pm2 logs backend  - View backend logs specifically"
    echo "   pm2 restart all   - Restart services"
    echo ""
    echo "Wait a few more seconds and test again:"
    echo "   curl http://localhost:8000/health"
    echo "   curl http://localhost:3030"
fi

echo ""

