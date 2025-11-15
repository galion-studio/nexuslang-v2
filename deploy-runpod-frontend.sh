#!/bin/bash
# 🚀 GALION PLATFORM - Complete Frontend Deployment for RunPod
# Deploys all frontend services: Galion.app, Developer Platform, Galion Studio

set -e

echo "🚀 GALION PLATFORM - RUNPOD FRONTEND DEPLOYMENT"
echo "================================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

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
}

# Check if we're in the right directory
check_environment() {
    log "Checking deployment environment..."

    if [ ! -d "/workspace/project-nexus" ]; then
        error "Not in RunPod workspace. Please run from /workspace/project-nexus"
        exit 1
    fi

    cd /workspace/project-nexus
    success "In correct workspace directory"

    # Check if backend is running
    if curl -f -s http://localhost:8010/health/fast > /dev/null 2>&1; then
        success "Backend API is healthy"
    else
        warning "Backend API not responding. Starting core services..."
        docker-compose up -d postgres redis elasticsearch backend
        sleep 30

        if curl -f -s http://localhost:8010/health/fast > /dev/null 2>&1; then
            success "Backend API started successfully"
        else
            error "Failed to start backend API"
            exit 1
        fi
    fi
}

# Deploy Galion.app (Voice-First Platform)
deploy_galion_app() {
    log "Deploying Galion.app (Voice-First Platform)..."

    if [ ! -d "galion-app" ]; then
        error "galion-app directory not found"
        exit 1
    fi

    cd galion-app

    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        log "Installing dependencies..."
        npm install --legacy-peer-deps
    fi

    # Create environment file
    if [ ! -f ".env.local" ]; then
        cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8010
NEXT_PUBLIC_WS_URL=ws://localhost:8010
NEXT_PUBLIC_APP_URL=http://localhost:3000
EOF
    fi

    # Start the service
    log "Starting Galion.app on port 3000..."
    npm run dev > ../logs/galion-app.log 2>&1 &
    GALION_PID=$!

    # Wait for startup
    sleep 10

    # Check if running
    if curl -f -s http://localhost:3000 > /dev/null 2>&1; then
        success "Galion.app deployed successfully (PID: $GALION_PID)"
        echo "🌐 Access: http://localhost:3000"
        echo "🎤 Voice Interface: http://localhost:3000/voice"
        echo "📚 Onboarding: http://localhost:3000/onboarding"
    else
        warning "Galion.app may still be starting up..."
    fi

    cd ..
}

# Deploy Developer Platform (IDE)
deploy_developer_platform() {
    log "Deploying Developer Platform (IDE)..."

    if [ ! -d "developer-platform" ]; then
        error "developer-platform directory not found"
        exit 1
    fi

    cd developer-platform

    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        log "Installing dependencies..."
        npm install --legacy-peer-deps
    fi

    # Create environment file
    if [ ! -f ".env.local" ]; then
        cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8010
NEXT_PUBLIC_APP_URL=http://localhost:3020
EOF
    fi

    # Start the service on port 3020
    log "Starting Developer Platform on port 3020..."
    PORT=3020 npm run dev > ../logs/developer-platform.log 2>&1 &
    DEV_PID=$!

    # Wait for startup
    sleep 10

    # Check if running
    if curl -f -s http://localhost:3020 > /dev/null 2>&1; then
        success "Developer Platform deployed successfully (PID: $DEV_PID)"
        echo "🌐 Access: http://localhost:3020"
        echo "💻 IDE: http://localhost:3020/ide"
    else
        warning "Developer Platform may still be starting up..."
    fi

    cd ..
}

# Deploy Galion Studio (Corporate Website)
deploy_galion_studio() {
    log "Deploying Galion Studio (Corporate Website)..."

    if [ ! -d "galion-studio" ]; then
        error "galion-studio directory not found"
        exit 1
    fi

    cd galion-studio

    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        log "Installing dependencies..."
        npm install --legacy-peer-deps
    fi

    # Create environment file
    if [ ! -f ".env.local" ]; then
        cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8010
NEXT_PUBLIC_APP_URL=http://localhost:3030
EOF
    fi

    # Start the service on port 3030
    log "Starting Galion Studio on port 3030..."
    PORT=3030 npm run dev > ../logs/galion-studio.log 2>&1 &
    STUDIO_PID=$!

    # Wait for startup
    sleep 10

    # Check if running
    if curl -f -s http://localhost:3030 > /dev/null 2>&1; then
        success "Galion Studio deployed successfully (PID: $STUDIO_PID)"
        echo "🌐 Access: http://localhost:3030"
    else
        warning "Galion Studio may still be starting up..."
    fi

    cd ..
}

# Deploy monitoring services
deploy_monitoring() {
    log "Ensuring monitoring services are running..."

    # Start Prometheus and Grafana if not running
    docker-compose up -d prometheus grafana monitoring 2>/dev/null || true

    sleep 5

    if curl -f -s http://localhost:9090 > /dev/null 2>&1; then
        success "Prometheus monitoring active"
    fi

    if curl -f -s http://localhost:3001 > /dev/null 2>&1; then
        success "Grafana dashboard active (admin/admin)"
    fi

    if curl -f -s http://localhost:8080 > /dev/null 2>&1; then
        success "Monitoring dashboard active"
    fi
}

# Setup reverse proxy
setup_nginx() {
    log "Setting up Nginx reverse proxy..."

    # Start nginx if not running
    docker-compose up -d nginx 2>/dev/null || true

    sleep 5

    if curl -f -s http://localhost/nginx-health > /dev/null 2>&1; then
        success "Nginx reverse proxy active"
    else
        warning "Nginx may still be starting..."
    fi
}

# Create logs directory
create_logs_directory() {
    mkdir -p logs
}

# Save process IDs for management
save_process_ids() {
    # Save PIDs to file for later management
    echo "$GALION_PID $DEV_PID $STUDIO_PID" > .frontend-pids.txt
}

# Display access information
display_access_info() {
    echo ""
    echo "================================================"
    echo -e "${GREEN}🎉 GALION PLATFORM DEPLOYMENT COMPLETE!${NC}"
    echo "================================================"
    echo ""

    # Get RunPod IP
    RUNPOD_IP=$(curl -s ifconfig.me 2>/dev/null || echo "your-runpod-ip")

    echo "🌐 ACCESS YOUR GALION PLATFORM:"
    echo ""
    echo "🎤 Galion.app (Voice-First):"
    echo "   Local:  http://localhost:3000"
    echo "   External: http://$RUNPOD_IP:3000"
    echo "   Voice:   http://$RUNPOD_IP:3000/voice"
    echo "   Onboarding: http://$RUNPOD_IP:3000/onboarding"
    echo ""

    echo "💻 Developer Platform (IDE):"
    echo "   Local:  http://localhost:3020"
    echo "   External: http://$RUNPOD_IP:3020"
    echo "   IDE:    http://$RUNPOD_IP:3020/ide"
    echo ""

    echo "🏢 Galion Studio (Corporate):"
    echo "   Local:  http://localhost:3030"
    echo "   External: http://$RUNPOD_IP:3030"
    echo ""

    echo "🔧 Backend & Monitoring:"
    echo "   API:    http://$RUNPOD_IP:8010/docs"
    echo "   Health: http://$RUNPOD_IP:8010/health/fast"
    echo "   Grafana: http://$RUNPOD_IP:3001 (admin/admin)"
    echo "   Prometheus: http://$RUNPOD_IP:9090"
    echo ""

    echo "📊 Useful Commands:"
    echo ""
    echo "View logs:"
    echo "   tail -f logs/galion-app.log"
    echo "   tail -f logs/developer-platform.log"
    echo "   tail -f logs/galion-studio.log"
    echo ""
    echo "Check processes:"
    echo "   ps aux | grep 'next dev'"
    echo ""
    echo "Stop frontends:"
    echo "   kill \$(cat .frontend-pids.txt)"
    echo ""
    echo "Restart all:"
    echo "   ./deploy-runpod-frontend.sh"
}

# Health check all services
final_health_check() {
    log "Running final health checks..."

    echo ""
    echo "🔍 SERVICE HEALTH STATUS:"
    echo ""

    # Backend
    if curl -f -s http://localhost:8010/health/fast > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend API${NC} - http://localhost:8010"
    else
        echo -e "${RED}❌ Backend API${NC} - Not responding"
    fi

    # Galion.app
    if curl -f -s http://localhost:3000 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Galion.app${NC} - http://localhost:3000"
    else
        echo -e "${YELLOW}⚠️  Galion.app${NC} - Starting up..."
    fi

    # Developer Platform
    if curl -f -s http://localhost:3020 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Developer Platform${NC} - http://localhost:3020"
    else
        echo -e "${YELLOW}⚠️  Developer Platform${NC} - Starting up..."
    fi

    # Galion Studio
    if curl -f -s http://localhost:3030 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Galion Studio${NC} - http://localhost:3030"
    else
        echo -e "${YELLOW}⚠️  Galion Studio${NC} - Starting up..."
    fi

    # Nginx
    if curl -f -s http://localhost/nginx-health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Nginx Proxy${NC} - Active"
    else
        echo -e "${YELLOW}⚠️  Nginx Proxy${NC} - Not ready"
    fi

    echo ""
}

# Main deployment function
main() {
    echo "Starting complete frontend deployment..."
    echo ""

    create_logs_directory
    check_environment
    deploy_monitoring
    setup_nginx
    deploy_galion_app
    deploy_developer_platform
    deploy_galion_studio
    save_process_ids
    final_health_check
    display_access_info

    echo ""
    echo -e "${GREEN}\"Your imagination is the end.\" - Successfully deployed on RunPod! 🚀${NC}"
    echo ""
}

# Handle command line arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "galion-app")
        check_environment
        deploy_galion_app
        ;;
    "developer-platform")
        check_environment
        deploy_developer_platform
        ;;
    "galion-studio")
        check_environment
        deploy_galion_studio
        ;;
    "health")
        final_health_check
        ;;
    "stop")
        if [ -f ".frontend-pids.txt" ]; then
            kill $(cat .frontend-pids.txt) 2>/dev/null || true
            rm .frontend-pids.txt
            success "Frontend services stopped"
        else
            warning "No frontend PIDs file found"
        fi
        ;;
    *)
        echo "Usage: $0 [command]"
        echo "Commands:"
        echo "  deploy              - Deploy all frontend services (default)"
        echo "  galion-app          - Deploy only Galion.app"
        echo "  developer-platform  - Deploy only Developer Platform"
        echo "  galion-studio       - Deploy only Galion Studio"
        echo "  health              - Check service health"
        echo "  stop                - Stop all frontend services"
        exit 1
        ;;
esac
