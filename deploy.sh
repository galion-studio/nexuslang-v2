#!/bin/bash
# NexusLang v2 Production Deployment Script
# Automated deployment with health checks and rollback capability

set -e  # Exit on any error

# Configuration
COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"
BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
LOG_FILE="./deploy_$(date +%Y%m%d_%H%M%S).log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Error handling
error_exit() {
    echo -e "${RED}ERROR: $1${NC}" >&2
    log "DEPLOYMENT FAILED: $1"
    rollback_deployment
    exit 1
}

# Success message
success() {
    echo -e "${GREEN}SUCCESS: $1${NC}"
    log "SUCCESS: $1"
}

# Info message
info() {
    echo -e "${BLUE}INFO: $1${NC}"
    log "INFO: $1"
}

# Warning message
warning() {
    echo -e "${YELLOW}WARNING: $1${NC}"
    log "WARNING: $1"
}

# Pre-deployment checks
pre_deployment_checks() {
    info "Running pre-deployment checks..."

    # Check if Docker is running
    if ! docker info >/dev/null 2>&1; then
        error_exit "Docker is not running or not accessible"
    fi

    # Check if Docker Compose is available
    if ! command -v docker-compose >/dev/null 2>&1; then
        error_exit "Docker Compose is not installed"
    fi

    # Check if compose file exists
    if [ ! -f "$COMPOSE_FILE" ]; then
        error_exit "Docker Compose file '$COMPOSE_FILE' not found"
    fi

    # Check if environment file exists
    if [ ! -f "$ENV_FILE" ]; then
        warning "Environment file '$ENV_FILE' not found. Using defaults."
    fi

    # Check available disk space (need at least 5GB)
    AVAILABLE_SPACE=$(df / | tail -1 | awk '{print $4}')
    if [ "$AVAILABLE_SPACE" -lt 5242880 ]; then  # 5GB in KB
        warning "Low disk space detected: $(($AVAILABLE_SPACE/1024))MB available"
    fi

    # Check available memory (need at least 4GB)
    AVAILABLE_MEM=$(free -m | grep '^Mem:' | awk '{print $2}')
    if [ "$AVAILABLE_MEM" -lt 4096 ]; then
        warning "Low memory detected: ${AVAILABLE_MEM}MB available"
    fi

    success "Pre-deployment checks completed"
}

# Backup current deployment
backup_deployment() {
    info "Creating deployment backup..."

    mkdir -p "$BACKUP_DIR"

    # Backup environment file
    if [ -f "$ENV_FILE" ]; then
        cp "$ENV_FILE" "$BACKUP_DIR/"
    fi

    # Backup database if running
    if docker-compose ps postgres | grep -q "Up"; then
        info "Backing up PostgreSQL database..."
        docker-compose exec -T postgres pg_dump -U nexus galion_platform > "$BACKUP_DIR/database_backup.sql" 2>/dev/null || true
    fi

    # Backup Redis data if running
    if docker-compose ps redis | grep -q "Up"; then
        info "Backing up Redis data..."
        docker-compose exec -T redis redis-cli --raw SAVE || true
        docker cp $(docker-compose ps -q redis):/data/dump.rdb "$BACKUP_DIR/redis_backup.rdb" 2>/dev/null || true
    fi

    success "Backup created at: $BACKUP_DIR"
}

# Stop existing deployment
stop_deployment() {
    info "Stopping existing deployment..."

    if docker-compose ps | grep -q "Up"; then
        docker-compose down --timeout 30
        success "Existing deployment stopped"
    else
        info "No existing deployment found"
    fi
}

# Start new deployment
start_deployment() {
    info "Starting new deployment..."

    # Pull latest images
    docker-compose pull

    # Start services
    docker-compose up -d

    success "New deployment started"
}

# Health checks
health_checks() {
    info "Running health checks..."

    local max_attempts=30
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        info "Health check attempt $attempt/$max_attempts..."

        # Check if all services are running
        if ! docker-compose ps | grep -q "Exit"; then
            # Test backend health
            if curl -f -s http://localhost:8010/health >/dev/null 2>&1; then
                # Test frontend
                if curl -f -s http://localhost:3010 >/dev/null 2>&1; then
                    # Test monitoring
                    if curl -f -s http://localhost:8080/health >/dev/null 2>&1; then
                        success "All services are healthy!"
                        return 0
                    fi
                fi
            fi
        fi

        sleep 10
        ((attempt++))
    done

    error_exit "Health checks failed after $max_attempts attempts"
}

# Post-deployment validation
post_deployment_validation() {
    info "Running post-deployment validation..."

    # Run the production validation script
    if [ -f "production-validation.py" ]; then
        if python3 production-validation.py; then
            success "Production validation passed"
        else
            warning "Production validation failed - check logs for details"
        fi
    fi

    # Run performance tests
    if [ -f "performance-test-simple.py" ]; then
        info "Running performance tests..."
        if python3 performance-test-simple.py; then
            success "Performance tests passed"
        else
            warning "Performance tests failed - check logs for details"
        fi
    fi
}

# Rollback deployment
rollback_deployment() {
    warning "Rolling back deployment..."

    # Stop current deployment
    docker-compose down --timeout 30 || true

    # Restore from backup if available
    if [ -d "$BACKUP_DIR" ] && [ -f "$BACKUP_DIR/$ENV_FILE" ]; then
        info "Restoring environment file from backup..."
        cp "$BACKUP_DIR/$ENV_FILE" "$ENV_FILE"
    fi

    # Note: Database and Redis restoration would need manual intervention
    warning "Database and Redis data restoration requires manual steps"
    warning "Check backup directory: $BACKUP_DIR"

    info "Rollback completed"
}

# Main deployment function
deploy() {
    log "Starting NexusLang v2 deployment"

    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                 NexusLang v2 Deployment                     ║"
    echo "║                 Production Ready Platform                   ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""

    # Run deployment steps
    pre_deployment_checks
    backup_deployment
    stop_deployment
    start_deployment
    health_checks
    post_deployment_validation

    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    DEPLOYMENT COMPLETE!                     ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    echo "🌐 Access URLs:"
    echo "   Frontend:    http://localhost:3010"
    echo "   Backend API: http://localhost:8010"
    echo "   API Docs:    http://localhost:8010/docs"
    echo "   Monitoring:  http://localhost:8080"
    echo "   Grafana:     http://localhost:3001 (admin/admin123)"
    echo ""
    echo "📊 Logs: $LOG_FILE"
    echo "💾 Backup: $BACKUP_DIR"
    echo ""
    echo "🎯 NexusLang v2 is now running in production mode!"
    echo ""

    log "Deployment completed successfully"
}

# Command line argument handling
case "${1:-deploy}" in
    "deploy")
        deploy
        ;;
    "backup")
        backup_deployment
        ;;
    "stop")
        stop_deployment
        ;;
    "start")
        start_deployment
        ;;
    "health")
        health_checks
        ;;
    "rollback")
        rollback_deployment
        ;;
    "validate")
        post_deployment_validation
        ;;
    *)
        echo "Usage: $0 [command]"
        echo "Commands:"
        echo "  deploy    - Full deployment (default)"
        echo "  backup    - Create backup only"
        echo "  stop      - Stop deployment"
        echo "  start     - Start deployment"
        echo "  health    - Run health checks"
        echo "  rollback  - Rollback deployment"
        echo "  validate  - Run validation tests"
        exit 1
        ;;
esac
