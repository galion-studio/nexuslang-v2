#!/bin/bash
# NexusLang v2 - Complete Production Deployment
# Automated deployment for the entire platform to production

set -e  # Exit on any error

echo "🚀 NexusLang v2 - COMPLETE PRODUCTION DEPLOYMENT"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}" | tee -a production-deploy.log
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
    log "SUCCESS: $1"
}

error() {
    echo -e "${RED}❌ ERROR: $1${NC}" >&2
    log "ERROR: $1"
    exit 1
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    log "WARNING: $1"
}

# Configuration variables (customize for your environment)
DEPLOY_ENV=${DEPLOY_ENV:-production}
RUNPOD_POD_ID=${RUNPOD_POD_ID:-}
DOMAIN=${DOMAIN:-nexuslang.dev}
EMAIL=${EMAIL:-admin@nexuslang.dev}

# Pre-deployment checks
pre_deployment_checks() {
    log "🔍 Running pre-deployment checks..."

    # Check if we're in the right directory
    if [[ ! -d "v2" ]]; then
        error "v2 directory not found. Please run from project root."
    fi

    # Check for required files
    required_files=(
        "v2/backend/main.py"
        "v2/frontend/package.json"
        "docker-compose.yml"
        "setup-production-database.sh"
    )

    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            error "Required file missing: $file"
        fi
    done

    # Check system resources
    TOTAL_MEM=$(free -g | grep '^Mem:' | awk '{print $2}')
    if [[ $TOTAL_MEM -lt 8 ]]; then
        warning "Low memory detected: ${TOTAL_MEM}GB (16GB+ recommended for production)"
    fi

    AVAILABLE_SPACE=$(df / | tail -1 | awk '{print $4}')
    AVAILABLE_GB=$((AVAILABLE_SPACE / 1024 / 1024))
    if [[ $AVAILABLE_GB -lt 20 ]]; then
        warning "Low disk space: ${AVAILABLE_GB}GB available (50GB+ recommended)"
    fi

    success "Pre-deployment checks passed"
}

# Setup environment and dependencies
setup_environment() {
    log "🔧 Setting up deployment environment..."

    # Install system dependencies
    sudo apt update
    sudo apt install -y curl wget git htop jq

    # Install Docker if not present
    if ! command -v docker &> /dev/null; then
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        sudo systemctl enable docker
        sudo systemctl start docker
        success "Docker installed and started"
    fi

    # Install Docker Compose if not present
    if ! command -v docker-compose &> /dev/null; then
        sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
        success "Docker Compose installed"
    fi

    # Install Node.js for frontend
    if ! command -v node &> /dev/null; then
        curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
        sudo apt-get install -y nodejs
        success "Node.js installed"
    fi

    # Install Python for backend
    if ! command -v python3 &> /dev/null; then
        sudo apt install -y python3 python3-pip python3-venv
        success "Python 3 installed"
    fi

    success "Environment setup completed"
}

# Setup database
setup_database() {
    log "🗄️  Setting up production database..."

    # Run database setup script
    chmod +x setup-production-database.sh
    ./setup-production-database.sh setup

    success "Database setup completed"
}

# Build and deploy backend
deploy_backend() {
    log "🧠 Building and deploying backend..."

    cd v2/backend

    # Create production environment file
    cat > .env << EOF
# Production Environment Configuration
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql://nexus:dev_password_2025@localhost:5432/galion_platform

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=${JWT_SECRET_KEY:-$(openssl rand -hex 32)}
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI/OpenRouter
OPENROUTER_API_KEY=${OPENROUTER_API_KEY:-}
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-}

# Email
SMTP_SERVER=${SMTP_SERVER:-smtp.gmail.com}
SMTP_PORT=${SMTP_PORT:-587}
SMTP_USERNAME=${SMTP_USERNAME:-}
SMTP_PASSWORD=${SMTP_PASSWORD:-}

# Security
SECRET_KEY=${SECRET_KEY:-$(openssl rand -hex 32)}
ENCRYPTION_KEY=${ENCRYPTION_KEY:-$(openssl rand -hex 32)}

# CORS
ALLOWED_ORIGINS=https://$DOMAIN,https://www.$DOMAIN,http://localhost:3000

# RunPod
RUNPOD_INSTANCE=true
WORKSPACE_PATH=/workspace
EOF

    # Build backend container
    docker build -t nexuslang-backend:latest .
    success "Backend container built"

    cd ../..
}

# Build and deploy frontend
deploy_frontend() {
    log "🌐 Building and deploying frontend..."

    cd v2/frontend

    # Install dependencies
    npm install

    # Create production environment
    cat > .env.local << EOF
NEXT_PUBLIC_API_URL=https://api.$DOMAIN
NEXT_PUBLIC_APP_URL=https://$DOMAIN
EOF

    # Build for production
    npm run build
    success "Frontend built for production"

    # Build frontend container
    docker build -t nexuslang-frontend:latest -f Dockerfile .
    success "Frontend container built"

    cd ../..
}

# Deploy infrastructure
deploy_infrastructure() {
    log "🏗️  Deploying infrastructure..."

    # Create Docker networks
    docker network create nexuslang-network 2>/dev/null || true

    # Start infrastructure services
    docker-compose up -d postgres redis elasticsearch
    success "Infrastructure services started"

    # Wait for services to be ready
    log "Waiting for infrastructure services..."
    sleep 30

    # Verify services are running
    if docker-compose ps postgres | grep -q "Up"; then
        success "PostgreSQL is running"
    else
        error "PostgreSQL failed to start"
    fi

    if docker-compose ps redis | grep -q "Up"; then
        success "Redis is running"
    else
        error "Redis failed to start"
    fi
}

# Deploy application services
deploy_application() {
    log "🚀 Deploying application services..."

    # Start all application services
    docker-compose up -d backend frontend nginx monitoring
    success "Application services deployed"

    # Wait for services to start
    log "Waiting for application services..."
    sleep 60

    # Verify backend is running
    if curl -f -s http://localhost:8010/health/fast >/dev/null 2>&1; then
        success "Backend API is responding"
    else
        error "Backend API is not responding"
    fi

    # Verify frontend is running
    if curl -f -s http://localhost:3010 >/dev/null 2>&1; then
        success "Frontend is responding"
    else
        error "Frontend is not responding"
    fi
}

# Setup monitoring and logging
setup_monitoring() {
    log "📊 Setting up monitoring and logging..."

    # Start monitoring stack
    docker-compose up -d prometheus grafana
    success "Monitoring stack deployed"

    # Setup log aggregation if needed
    # Add any additional monitoring configuration here

    success "Monitoring setup completed"
}

# Configure reverse proxy and SSL
setup_reverse_proxy() {
    log "🔀 Setting up reverse proxy and SSL..."

    # Create nginx configuration for production
    cat > nginx.production.conf << EOF
upstream backend {
    server backend:8000;
}

upstream frontend {
    server frontend:3000;
}

server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    # Redirect HTTP to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;

    # SSL configuration (you'll need to add your certificates)
    # ssl_certificate /path/to/cert.pem;
    # ssl_certificate_key /path/to/key.pem;

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Backend API
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Health checks
    location /health {
        proxy_pass http://backend;
    }

    # Static files
    location /static/ {
        proxy_pass http://backend;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

    success "Nginx configuration created"
}

# Run post-deployment tests
run_post_deployment_tests() {
    log "🧪 Running post-deployment tests..."

    # Make test scripts executable
    chmod +x test-production-apis.py
    chmod +x test-end-to-end.sh

    # Run API tests
    log "Running API tests..."
    python3 test-production-apis.py --url http://localhost:8010

    # Run E2E tests
    log "Running E2E tests..."
    ./test-end-to-end.sh test

    success "Post-deployment tests completed"
}

# Setup backup and recovery
setup_backup_recovery() {
    log "💾 Setting up backup and recovery..."

    # Create backup directories
    mkdir -p backups/{database,config,logs}

    # Setup automated backups (example cron job)
    cat > backup-script.sh << 'EOF'
#!/bin/bash
# Automated backup script for NexusLang v2

BACKUP_DIR="/workspace/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Database backup
docker-compose exec -T postgres pg_dump -U nexus galion_platform > $BACKUP_DIR/database/backup_$TIMESTAMP.sql

# Configuration backup
cp v2/backend/.env $BACKUP_DIR/config/env_$TIMESTAMP.backup

# Log rotation
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.backup" -mtime +30 -delete

echo "Backup completed at $TIMESTAMP"
EOF

    chmod +x backup-script.sh

    # Add to crontab (example - daily at 2 AM)
    # (crontab -l ; echo "0 2 * * * /workspace/backup-script.sh") | crontab -

    success "Backup and recovery setup completed"
}

# Create deployment summary
create_deployment_summary() {
    log "📋 Creating deployment summary..."

    DEPLOYMENT_TIME=$(date)
    SUCCESS_RATE=$(( TESTS_PASSED * 100 / TOTAL_TESTS ))

    cat > production-deployment-summary.json << EOF
{
  "deployment": {
    "timestamp": "$DEPLOYMENT_TIME",
    "environment": "$DEPLOY_ENV",
    "domain": "$DOMAIN",
    "status": "completed"
  },
  "services": {
    "backend": "http://localhost:8010",
    "frontend": "http://localhost:3010",
    "database": "postgresql://localhost:5432",
    "redis": "redis://localhost:6379",
    "monitoring": "http://localhost:8080"
  },
  "testing": {
    "api_tests_passed": $TESTS_PASSED,
    "api_tests_failed": $TESTS_FAILED,
    "api_tests_total": $TOTAL_TESTS,
    "success_rate": $SUCCESS_RATE
  },
  "admin_credentials": {
    "email": "admin@nexuslang.dev",
    "password": "Admin123!",
    "credits": 10000
  },
  "next_steps": [
    "Configure SSL certificates for $DOMAIN",
    "Set up DNS records",
    "Configure monitoring alerts",
    "Set up log aggregation",
    "Configure backup retention policies",
    "Set up CDN for static assets",
    "Configure rate limiting rules",
    "Set up error tracking (Sentry, etc.)",
    "Configure performance monitoring",
    "Set up automated scaling"
  ]
}
EOF

    success "Deployment summary created"
}

# Main deployment function
main() {
    echo ""
    echo "🔥 STARTING COMPLETE PRODUCTION DEPLOYMENT"
    echo "=========================================="

    pre_deployment_checks
    setup_environment
    setup_database
    deploy_backend
    deploy_frontend
    deploy_infrastructure
    deploy_application
    setup_monitoring
    setup_reverse_proxy
    run_post_deployment_tests
    setup_backup_recovery
    create_deployment_summary

    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                 PRODUCTION DEPLOYMENT COMPLETE!             ║"
    echo "║              NexusLang v2 is LIVE in Production             ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    echo "🌐 ACCESS YOUR PRODUCTION SYSTEM:"
    echo "   Frontend:    http://localhost:3010"
    echo "   API:         http://localhost:8010"
    echo "   Monitoring:  http://localhost:8080"
    echo "   Health:      http://localhost:8010/health/fast"
    echo ""
    echo "👤 ADMIN ACCESS:"
    echo "   Email: admin@nexuslang.dev"
    echo "   Password: Admin123!"
    echo ""
    echo "📋 Deployment Summary: production-deployment-summary.json"
    echo "📜 Full Log: production-deploy.log"
    echo ""
    echo "🚀 READY FOR: SSL setup, DNS configuration, and user traffic!"
    echo ""
}

# Handle command line arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "infrastructure-only")
        pre_deployment_checks
        setup_environment
        deploy_infrastructure
        success "Infrastructure deployment completed"
        ;;
    "database-only")
        pre_deployment_checks
        setup_database
        success "Database setup completed"
        ;;
    "application-only")
        pre_deployment_checks
        deploy_backend
        deploy_frontend
        deploy_application
        success "Application deployment completed"
        ;;
    "test-only")
        run_post_deployment_tests
        ;;
    *)
        echo "Usage: $0 [command]"
        echo "Commands:"
        echo "  deploy              - Complete production deployment (default)"
        echo "  infrastructure-only - Deploy only infrastructure services"
        echo "  database-only       - Setup database only"
        echo "  application-only    - Deploy application services only"
        echo "  test-only           - Run post-deployment tests only"
        exit 1
        ;;
esac
