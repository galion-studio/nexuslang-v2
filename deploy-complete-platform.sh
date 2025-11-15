#!/bin/bash
# 🚀 GALION PLATFORM - Complete Production Deployment for RunPod
# Master deployment script that handles all services and configurations

set -e

echo "🚀 GALION PLATFORM - COMPLETE PRODUCTION DEPLOYMENT"
echo "=================================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Logging functions
log() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

# Check if we're in the right environment
check_environment() {
    log "Checking deployment environment..."

    if [ ! -d "/workspace/project-nexus" ]; then
        error "Not in RunPod workspace. Please run from /workspace/project-nexus"
    fi

    cd /workspace/project-nexus
    success "In correct workspace directory"

    # Make scripts executable
    chmod +x *.sh 2>/dev/null || true
    chmod +x v2/backend/*.sh 2>/dev/null || true
}

# Start infrastructure services
start_infrastructure() {
    log "Starting infrastructure services..."

    # Stop any existing services
    docker-compose down --remove-orphans 2>/dev/null || true

    # Start core infrastructure
    docker-compose up -d postgres redis elasticsearch
    sleep 10

    # Verify infrastructure is running
    if docker-compose ps postgres | grep -q "Up"; then
        success "PostgreSQL running"
    else
        error "PostgreSQL failed to start"
    fi

    if docker-compose ps redis | grep -q "Up"; then
        success "Redis running"
    else
        error "Redis failed to start"
    fi

    if docker-compose ps elasticsearch | grep -q "Up"; then
        success "Elasticsearch running"
    else
        error "Elasticsearch failed to start"
    fi
}

# Start backend services
start_backend() {
    log "Starting backend services..."

    docker-compose up -d backend ai-models
    sleep 15

    # Verify backend is running
    if curl -f -s --max-time 10 http://localhost:8010/health/fast >/dev/null 2>&1; then
        success "Backend API running (8010)"
    else
        error "Backend API failed to start"
    fi

    # Verify AI models service
    if curl -f -s --max-time 15 http://localhost:8011/health >/dev/null 2>&1; then
        success "AI Models service running (8011)"
    else
        warning "AI Models service not yet ready (may be initializing)"
    fi
}

# Start monitoring stack
start_monitoring() {
    log "Starting monitoring stack..."

    docker-compose up -d prometheus grafana monitoring
    sleep 10

    # Verify monitoring services
    if curl -f -s http://localhost:9090/-/healthy >/dev/null 2>&1; then
        success "Prometheus running (9090)"
    else
        warning "Prometheus not ready"
    fi

    if curl -f -s http://localhost:3001/api/health >/dev/null 2>&1; then
        success "Grafana running (3001)"
    else
        warning "Grafana not ready"
    fi

    if curl -f -s http://localhost:8080/health >/dev/null 2>&1; then
        success "Platform monitoring running (8080)"
    else
        warning "Platform monitoring not ready"
    fi
}

# Start reverse proxy
start_nginx() {
    log "Starting Nginx reverse proxy..."

    docker-compose up -d nginx
    sleep 5

    # Verify nginx is running
    if curl -f -s http://localhost/nginx-health >/dev/null 2>&1; then
        success "Nginx reverse proxy running"
    else
        error "Nginx failed to start"
    fi
}

# Deploy frontend applications
deploy_frontends() {
    log "Deploying frontend applications..."

    # Build and start Galion.app
    if [ -d "galion-app" ]; then
        log "Building Galion.app..."
        docker-compose build galion-app
        docker-compose up -d galion-app
        sleep 10

        if curl -f -s http://localhost:3000 >/dev/null 2>&1; then
            success "Galion.app deployed (3000)"
        else
            warning "Galion.app container started but may still be initializing"
        fi
    else
        warning "galion-app directory not found - skipping"
    fi

    # Build and start Developer Platform
    if [ -d "developer-platform" ]; then
        log "Building Developer Platform..."
        docker-compose build developer-platform
        docker-compose up -d developer-platform
        sleep 10

        if curl -f -s http://localhost:3020 >/dev/null 2>&1; then
            success "Developer Platform deployed (3020)"
        else
            warning "Developer Platform container started but may still be initializing"
        fi
    else
        warning "developer-platform directory not found - skipping"
    fi

    # Build and start Galion Studio
    if [ -d "galion-studio" ]; then
        log "Building Galion Studio..."
        docker-compose build galion-studio
        docker-compose up -d galion-studio
        sleep 10

        if curl -f -s http://localhost:3030 >/dev/null 2>&1; then
            success "Galion Studio deployed (3030)"
        else
            warning "Galion Studio container started but may still be initializing"
        fi
    else
        warning "galion-studio directory not found - skipping"
    fi
}

# Run comprehensive health check
run_health_checks() {
    log "Running comprehensive health checks..."

    if [ -f "health-check.sh" ]; then
        chmod +x health-check.sh
        ./health-check.sh all
    else
        warning "health-check.sh not found - running basic checks"

        # Basic health checks
        echo ""
        echo "🔍 BASIC HEALTH CHECKS"
        echo "======================"

        # Backend
        if curl -f -s http://localhost:8010/health/fast >/dev/null 2>&1; then
            success "Backend API healthy"
        else
            error "Backend API unhealthy"
        fi

        # AI Models
        if curl -f -s http://localhost:8011/health >/dev/null 2>&1; then
            success "AI Models service healthy"
        else
            warning "AI Models service not ready"
        fi

        # Nginx
        if curl -f -s http://localhost/nginx-health >/dev/null 2>&1; then
            success "Nginx proxy healthy"
        else
            error "Nginx proxy unhealthy"
        fi
    fi
}

# Display deployment summary
show_deployment_summary() {
    echo ""
    echo "================================================"
    echo -e "${GREEN}🎉 GALION PLATFORM DEPLOYMENT COMPLETE!${NC}"
    echo "================================================"
    echo ""

    # Get RunPod IP
    RUNPOD_IP=$(curl -s ifconfig.me 2>/dev/null || echo "your-runpod-ip")

    echo "🌐 PLATFORM ACCESS URLs:"
    echo ""
    echo "🎤 Galion.app (Voice-First AI):"
    echo "   Direct:  http://localhost:3000"
    echo "   Proxy:   http://$RUNPOD_IP/galion/"
    echo "   Voice:   http://$RUNPOD_IP/galion/voice"
    echo ""

    echo "💻 Developer Platform (IDE):"
    echo "   Direct:  http://localhost:3020"
    echo "   Proxy:   http://$RUNPOD_IP/developer/"
    echo "   IDE:     http://$RUNPOD_IP/developer/ide"
    echo ""

    echo "🏢 Galion Studio (Corporate):"
    echo "   Direct:  http://localhost:3030"
    echo "   Proxy:   http://$RUNPOD_IP/studio/"
    echo ""

    echo "🔧 APIs & Services:"
    echo "   Backend API:     http://$RUNPOD_IP/api/"
    echo "   API Docs:        http://$RUNPOD_IP:8010/docs"
    echo "   AI Models API:   http://$RUNPOD_IP/api/models/"
    echo "   Voice API:       http://$RUNPOD_IP/api/voice/"
    echo "   NexusLang API:   http://$RUNPOD_IP/api/nexuslang/"
    echo ""

    echo "📊 Monitoring & Management:"
    echo "   Grafana:         http://$RUNPOD_IP:3001 (admin/admin)"
    echo "   Prometheus:      http://$RUNPOD_IP:9090"
    echo "   Platform Health: http://$RUNPOD_IP/monitoring/"
    echo "   Health Check:    http://$RUNPOD_IP/health"
    echo ""

    echo "🛠️  Management Commands:"
    echo ""
    echo "View all services:"
    echo "   docker-compose ps"
    echo ""
    echo "View logs:"
    echo "   docker-compose logs -f [service-name]"
    echo ""
    echo "Restart service:"
    echo "   docker-compose restart [service-name]"
    echo ""
    echo "Run health check:"
    echo "   ./health-check.sh"
    echo ""
    echo "Stop all services:"
    echo "   docker-compose down"
    echo ""

    echo "📈 SERVICE STATUS:"
    echo "=================="
    docker-compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
    echo ""

    echo -e "${GREEN}\"Your imagination is the end.\" - Successfully deployed on RunPod! 🚀${NC}"
    echo ""
    echo "🎯 Ready for production traffic and user testing!"
    echo ""
}

# Handle command line arguments
case "${1:-deploy}" in
    "infrastructure")
        log "Deploying only infrastructure..."
        check_environment
        start_infrastructure
        success "Infrastructure deployment complete"
        ;;
    "backend")
        log "Deploying only backend services..."
        check_environment
        start_infrastructure
        start_backend
        success "Backend deployment complete"
        ;;
    "monitoring")
        log "Deploying only monitoring..."
        check_environment
        start_monitoring
        success "Monitoring deployment complete"
        ;;
    "frontends")
        log "Deploying only frontends..."
        check_environment
        deploy_frontends
        success "Frontend deployment complete"
        ;;
    "health")
        check_environment
        run_health_checks
        ;;
    "stop")
        log "Stopping all services..."
        docker-compose down --remove-orphans
        success "All services stopped"
        ;;
    "restart")
        log "Restarting all services..."
        docker-compose down --remove-orphans
        sleep 5
        check_environment
        start_infrastructure
        start_backend
        start_monitoring
        start_nginx
        deploy_frontends
        run_health_checks
        show_deployment_summary
        ;;
    "deploy"|*)
        log "Starting complete platform deployment..."
        echo ""

        check_environment
        start_infrastructure
        start_backend
        start_monitoring
        start_nginx
        deploy_frontends
        run_health_checks
        show_deployment_summary
        ;;
esac
