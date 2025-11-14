#!/bin/bash
# Galion Autonomous Agent System - RunPod Startup Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Environment setup
setup_environment() {
    log_info "Setting up environment variables..."

    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        cat > .env << EOF
# Galion Environment Configuration
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8010

# Database
DATABASE_URL=postgresql://galion:password@galion-db:5432/galion
DB_PASSWORD=password

# Redis
REDIS_URL=redis://galion-redis:6379/0
REDIS_PASSWORD=

# Security
JWT_SECRET_KEY=${JWT_SECRET_KEY:-$(openssl rand -hex 32)}
OPENAI_API_KEY=${OPENAI_API_KEY}

# Application
LOG_LEVEL=INFO
MAX_WORKERS=4
REQUEST_TIMEOUT=300

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost

# Monitoring
GRAFANA_PASSWORD=admin
NGINX_PORT=80
NGINX_SSL_PORT=443

# RunPod specific
RUNPOD_POD_ID=${RUNPOD_POD_ID}
RUNPOD_PUBLIC_IP=${RUNPOD_PUBLIC_IP}
EOF
        log_success "Environment file created"
    else
        log_info "Environment file already exists"
    fi
}

# Health check function
wait_for_service() {
    local service_name=$1
    local host=$2
    local port=$3
    local max_attempts=${4:-30}
    local attempt=1

    log_info "Waiting for $service_name to be ready on $host:$port..."

    while [ $attempt -le $max_attempts ]; do
        if nc -z $host $port 2>/dev/null; then
            log_success "$service_name is ready!"
            return 0
        fi

        log_info "Attempt $attempt/$max_attempts: $service_name not ready yet..."
        sleep 2
        ((attempt++))
    done

    log_error "$service_name failed to start after $max_attempts attempts"
    return 1
}

# Start services
start_services() {
    log_info "Starting Galion services..."

    # Start Docker Compose services
    if [ -f "docker-compose.runpod.yml" ]; then
        log_info "Starting services with Docker Compose..."
        docker-compose -f docker-compose.runpod.yml up -d

        # Wait for database
        wait_for_service "PostgreSQL" "galion-db" 5432

        # Wait for Redis
        wait_for_service "Redis" "galion-redis" 6379

        # Wait for backend
        wait_for_service "Backend API" "galion-backend" 8010

        log_success "All services started successfully"
    else
        log_error "docker-compose.runpod.yml not found"
        return 1
    fi
}

# Initialize system
initialize_system() {
    log_info "Initializing Galion system..."

    # Run system initialization
    if docker-compose -f docker-compose.runpod.yml exec -T galion-backend python scripts/init_system.py; then
        log_success "System initialization completed"
    else
        log_error "System initialization failed"
        return 1
    fi

    # Run basic tests
    log_info "Running basic system tests..."
    if docker-compose -f docker-compose.runpod.yml exec -T galion-backend python scripts/test_basic.py; then
        log_success "Basic tests passed"
    else
        log_warning "Basic tests failed - system may still work"
    fi
}

# Setup monitoring
setup_monitoring() {
    log_info "Setting up monitoring..."

    # Configure Prometheus targets
    cat > monitoring/prometheus.yml << EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'galion-backend'
    static_configs:
      - targets: ['galion-backend:8010']
    scrape_interval: 5s
    metrics_path: '/metrics'

  - job_name: 'galion-frontend'
    static_configs:
      - targets: ['galion-frontend:3000']
    scrape_interval: 10s

  - job_name: 'galion-db'
    static_configs:
      - targets: ['galion-db:5432']
    scrape_interval: 30s

  - job_name: 'galion-redis'
    static_configs:
      - targets: ['galion-redis:6379']
    scrape_interval: 30s
EOF

    log_success "Monitoring configuration created"
}

# Display system information
show_system_info() {
    log_info "System Information:"
    echo "========================================"
    echo "Pod ID: ${RUNPOD_POD_ID:-N/A}"
    echo "Public IP: ${RUNPOD_PUBLIC_IP:-N/A}"
    echo "Environment: production"
    echo "========================================"
    echo ""
    echo "Access URLs:"
    echo "🌐 Frontend:    http://${RUNPOD_PUBLIC_IP:-localhost}"
    echo "📚 API Docs:    http://${RUNPOD_PUBLIC_IP:-localhost}:8010/docs"
    echo "🔍 Health:      http://${RUNPOD_PUBLIC_IP:-localhost}:8010/health"
    echo "📊 Monitoring:  http://${RUNPOD_PUBLIC_IP:-localhost}:8010/monitoring/status"
    echo "🎛️  Grafana:     http://${RUNPOD_PUBLIC_IP:-localhost}:3001 (admin/admin)"
    echo "📈 Prometheus:  http://${RUNPOD_PUBLIC_IP:-localhost}:9090"
    echo "========================================"
}

# Main startup sequence
main() {
    log_info "Starting Galion Autonomous Agent System on RunPod..."
    echo "========================================"

    # Setup environment
    setup_environment

    # Start services
    if start_services; then
        # Initialize system
        initialize_system

        # Setup monitoring
        setup_monitoring

        # Show system info
        show_system_info

        log_success "Galion system is now running!"
        log_info "You can now submit autonomous tasks via the API or web interface."

        # Keep container running
        log_info "Keeping services running... (Press Ctrl+C to stop)"
        docker-compose -f docker-compose.runpod.yml logs -f
    else
        log_error "Failed to start services"
        exit 1
    fi
}

# Cleanup function
cleanup() {
    log_info "Shutting down Galion system..."
    docker-compose -f docker-compose.runpod.yml down -v
    log_success "Shutdown complete"
}

# Set trap for cleanup
trap cleanup SIGINT SIGTERM

# Run main function
main "$@"
