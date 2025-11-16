#!/bin/bash
# ============================================
# GALION PRODUCTION DEPLOYMENT SCRIPT
# ============================================
# Complete deployment pipeline for Galion Voice API

set -e

echo "🚀 Deploying Galion Voice API to Production..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="/opt/galion"
BACKUP_DIR="/opt/galion/backups"
LOGS_DIR="/var/log/galion"

# Function to print status
print_status() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

# Function to print success
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Function to print error
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   print_error "This script must be run as root"
   exit 1
fi

# Create directories
print_status "Creating project directories..."
mkdir -p $PROJECT_DIR
mkdir -p $BACKUP_DIR
mkdir -p $LOGS_DIR
mkdir -p /var/www/galion-app
mkdir -p /var/www/developer-galion

# Install system dependencies
print_status "Installing system dependencies..."
apt update
apt install -y \
    python3.11 python3.11-venv python3-pip \
    nginx certbot python3-certbot-nginx \
    redis-server postgresql postgresql-contrib \
    supervisor git curl wget \
    build-essential python3-dev

# Install Node.js for frontend
if ! command -v node &> /dev/null; then
    print_status "Installing Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt install -y nodejs
fi

# Setup Python virtual environment
print_status "Setting up Python virtual environment..."
python3 -m venv $PROJECT_DIR/venv
source $PROJECT_DIR/venv/bin/activate

# Clone/update repository
if [[ -d "$PROJECT_DIR/repo" ]]; then
    print_status "Updating repository..."
    cd $PROJECT_DIR/repo
    git pull origin clean-nexuslang
else
    print_status "Cloning repository..."
    git clone -b clean-nexuslang https://github.com/galion-studio/nexuslang-v2.git $PROJECT_DIR/repo
    cd $PROJECT_DIR/repo
fi

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install --upgrade pip
pip install -r v2/backend/requirements.txt

# Setup environment file
print_status "Setting up environment configuration..."
if [[ ! -f "$PROJECT_DIR/.env" ]]; then
    cp v2/backend/.env.example $PROJECT_DIR/.env
    print_warning "Please edit $PROJECT_DIR/.env with your API keys and configuration"
fi

# Setup nginx
print_status "Configuring Nginx..."
cp nginx/nginx.conf /etc/nginx/nginx.conf
cp nginx/sites-available/* /etc/nginx/sites-available/
ln -sf /etc/nginx/sites-available/galion-voice-api /etc/nginx/sites-enabled/
ln -sf /etc/nginx/sites-available/api.galion.app /etc/nginx/sites-enabled/
ln -sf /etc/nginx/sites-available/developer.galion.app /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
if nginx -t; then
    print_success "Nginx configuration is valid"
    systemctl reload nginx
else
    print_error "Nginx configuration has errors"
    exit 1
fi

# Setup SSL certificates
print_status "Setting up SSL certificates..."
./scripts/setup-ssl.sh

# Build frontend
print_status "Building frontend..."
cd galion-app
npm install
npm run build
cp -r .next /var/www/galion-app/
cp -r public /var/www/galion-app/

# Setup supervisor for process management
print_status "Setting up process management..."
cat > /etc/supervisor/conf.d/galion.conf << EOF
[program:galion-backend]
command=$PROJECT_DIR/venv/bin/python $PROJECT_DIR/repo/v2/backend/main_simple.py
directory=$PROJECT_DIR/repo/v2/backend
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=$LOGS_DIR/backend.log
environment=PATH="$PROJECT_DIR/venv/bin"

[program:galion-frontend]
command=npm start
directory=$PROJECT_DIR/repo/galion-app
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=$LOGS_DIR/frontend.log
EOF

supervisorctl reread
supervisorctl update
supervisorctl start galion-backend
supervisorctl start galion-frontend

# Setup log rotation
print_status "Setting up log rotation..."
cat > /etc/logrotate.d/galion << EOF
$LOGS_DIR/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data adm
    postrotate
        supervisorctl restart galion-backend
        supervisorctl restart galion-frontend
    endscript
}
EOF

# Setup firewall
print_status "Configuring firewall..."
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw --force enable

# Create backup script
print_status "Creating backup script..."
cat > $PROJECT_DIR/backup.sh << 'EOF'
#!/bin/bash
BACKUP_NAME="galion-$(date +%Y%m%d-%H%M%S)"
BACKUP_DIR="/opt/galion/backups"

mkdir -p $BACKUP_DIR
pg_dump -U galion -h localhost galion_db > $BACKUP_DIR/$BACKUP_NAME.sql
tar -czf $BACKUP_DIR/$BACKUP_NAME.tar.gz -C /opt/galion repo .env

# Keep only last 7 backups
cd $BACKUP_DIR
ls -t *.tar.gz | tail -n +8 | xargs -r rm
ls -t *.sql | tail -n +8 | xargs -r rm

echo "Backup completed: $BACKUP_NAME"
EOF
chmod +x $PROJECT_DIR/backup.sh

# Add backup to cron
(crontab -l ; echo "0 2 * * * $PROJECT_DIR/backup.sh") | crontab -

# Setup monitoring (basic)
print_status "Setting up basic monitoring..."
cat > $PROJECT_DIR/health-check.sh << 'EOF'
#!/bin/bash
# Basic health check script

# Check backend
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend: OK"
else
    echo "❌ Backend: FAILED"
    exit 1
fi

# Check frontend
if curl -f http://localhost:3003 > /dev/null 2>&1; then
    echo "✅ Frontend: OK"
else
    echo "❌ Frontend: FAILED"
    exit 1
fi

# Check nginx
if systemctl is-active --quiet nginx; then
    echo "✅ Nginx: OK"
else
    echo "❌ Nginx: FAILED"
    exit 1
fi

echo "🎉 All services are healthy!"
EOF
chmod +x $PROJECT_DIR/health-check.sh

# Final verification
print_status "Running final verification..."
if $PROJECT_DIR/health-check.sh; then
    print_success "Deployment completed successfully!"
else
    print_error "Deployment verification failed"
    exit 1
fi

# Print summary
echo ""
echo "========================================"
echo "🎉 GALION VOICE API DEPLOYMENT COMPLETE"
echo "========================================"
echo ""
echo "📡 Services:"
echo "   - Frontend: https://galion.app"
echo "   - API: https://api.galion.app"
echo "   - Developer: https://developer.galion.app"
echo ""
echo "📊 Monitoring:"
echo "   - Health checks: $PROJECT_DIR/health-check.sh"
echo "   - Logs: $LOGS_DIR/"
echo "   - Backups: $BACKUP_DIR/"
echo ""
echo "🔧 Management:"
echo "   - Restart backend: supervisorctl restart galion-backend"
echo "   - Restart frontend: supervisorctl restart galion-frontend"
echo "   - View logs: tail -f $LOGS_DIR/backend.log"
echo ""
echo "📝 Next steps:"
echo "   1. Configure DNS for your domains"
echo "   2. Update $PROJECT_DIR/.env with production API keys"
echo "   3. Setup monitoring alerts"
echo "   4. Configure backup storage"
echo ""
echo -e "${GREEN}🚀 Your voice-first platform is live!${NC}"

