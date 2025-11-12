#!/bin/bash
# Complete Build and Deploy Script for Nexus Core
# Following Elon Musk's Building Principles: BUILD IT. DEPLOY IT. SHIP IT.

set -e

echo "🚀 Nexus Core - Build & Deploy Script"
echo "======================================"
echo ""
echo "Following Musk's Principles:"
echo "1. Iterate fast"
echo "2. Build in parallel"
echo "3. No bureaucracy"
echo "4. Ship it!"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOCKER_REGISTRY=${DOCKER_REGISTRY:-"nexuscore"}
VERSION=${VERSION:-"latest"}
NAMESPACE="nexus-core"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker not found. Install Docker first."
        exit 1
    fi
    
    if ! command -v kubectl &> /dev/null; then
        log_warn "kubectl not found. Skipping Kubernetes deployment."
        SKIP_K8S=true
    fi
    
    log_success "Prerequisites check passed"
}

# Generate secrets
generate_secrets() {
    log_info "Generating secure secrets..."
    
    if [ ! -f .env ]; then
        if [ -f generate-secrets.ps1 ]; then
            log_info "Running PowerShell secret generation..."
            pwsh generate-secrets.ps1
        elif [ -f scripts/generate-secrets.sh ]; then
            bash scripts/generate-secrets.sh
        else
            log_warn "Using template .env file"
            cp env.production.template .env
        fi
    else
        log_warn ".env file already exists, skipping generation"
    fi
    
    log_success "Secrets configured"
}

# Build Docker images
build_images() {
    log_info "Building Docker images..."
    
    services=(
        "api-gateway"
        "auth-service"
        "user-service"
        "analytics-service"
        "scraping-service"
        "billing-service"
    )
    
    for service in "${services[@]}"; do
        log_info "Building $service..."
        docker build -t $DOCKER_REGISTRY/$service:$VERSION \
            ./services/$service \
            --quiet || {
                log_error "Failed to build $service"
                exit 1
            }
        log_success "Built $service"
    done
    
    log_success "All images built successfully"
}

# Push images to registry
push_images() {
    if [ "$SKIP_PUSH" = true ]; then
        log_warn "Skipping image push"
        return
    fi
    
    log_info "Pushing images to registry..."
    
    services=(
        "api-gateway"
        "auth-service"
        "user-service"
        "analytics-service"
        "scraping-service"
        "billing-service"
    )
    
    for service in "${services[@]}"; do
        log_info "Pushing $service..."
        docker push $DOCKER_REGISTRY/$service:$VERSION || {
            log_warn "Failed to push $service (continuing...)"
        }
    done
    
    log_success "Images pushed to registry"
}

# Deploy with Docker Compose
deploy_docker_compose() {
    log_info "Deploying with Docker Compose..."
    
    # Ensure database migrations directory exists
    mkdir -p database/migrations
    
    # Build and start services
    docker-compose build
    docker-compose up -d
    
    # Wait for services
    log_info "Waiting for services to be healthy..."
    sleep 30
    
    # Check health
    docker-compose ps
    
    log_success "Docker Compose deployment complete"
    log_info "Services available at:"
    log_info "  - API Gateway: http://localhost:8080"
    log_info "  - Grafana: http://localhost:3000"
    log_info "  - Swagger Docs: http://localhost:8000/docs"
}

# Deploy to Kubernetes
deploy_kubernetes() {
    if [ "$SKIP_K8S" = true ]; then
        log_warn "Skipping Kubernetes deployment"
        return
    fi
    
    log_info "Deploying to Kubernetes..."
    
    # Make deploy script executable
    chmod +x k8s/deploy.sh
    
    # Run deployment
    bash k8s/deploy.sh $VERSION
    
    log_success "Kubernetes deployment complete"
    log_info "Services available at:"
    log_info "  - API: https://api.galion.app"
    log_info "  - App: https://app.galion.app"
    log_info "  - Main: https://galion.app"
    log_info "  - Grafana: https://grafana.galion.app"
}

# Run database migrations
run_migrations() {
    log_info "Running database migrations..."
    
    if [ -f database/migrations/003_scraping_service.sql ]; then
        if [ "$SKIP_K8S" = true ]; then
            # Docker Compose
            docker exec nexus-postgres psql -U nexuscore -d nexuscore \
                -f /docker-entrypoint-initdb.d/migrations/003_scraping_service.sql || {
                log_warn "Migration may have already run"
            }
        else
            # Kubernetes
            kubectl exec deployment/postgres -n $NAMESPACE -- \
                psql -U nexuscore -d nexuscore \
                -f /docker-entrypoint-initdb.d/migrations/003_scraping_service.sql || {
                log_warn "Migration may have already run"
            }
        fi
        log_success "Migrations completed"
    else
        log_warn "No migrations found"
    fi
}

# Test deployment
test_deployment() {
    log_info "Testing deployment..."
    
    # Determine API URL
    if [ "$SKIP_K8S" = true ]; then
        API_URL="http://localhost:8080"
    else
        API_URL="https://api.galion.app"
    fi
    
    # Test health endpoint
    log_info "Testing health endpoints..."
    
    if curl -sf "$API_URL/health" > /dev/null 2>&1; then
        log_success "API Gateway is healthy"
    else
        log_error "API Gateway health check failed"
    fi
    
    log_success "Deployment test complete"
}

# Main execution
main() {
    echo ""
    log_info "Starting Nexus Core deployment..."
    echo ""
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-build)
                SKIP_BUILD=true
                shift
                ;;
            --skip-push)
                SKIP_PUSH=true
                shift
                ;;
            --docker-compose)
                SKIP_K8S=true
                shift
                ;;
            --kubernetes)
                FORCE_K8S=true
                shift
                ;;
            *)
                echo "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    # Execute deployment steps
    check_prerequisites
    generate_secrets
    
    if [ "$SKIP_BUILD" != true ]; then
        build_images
        push_images
    fi
    
    if [ "$FORCE_K8S" = true ] || [ "$SKIP_K8S" != true ]; then
        deploy_kubernetes
    else
        deploy_docker_compose
    fi
    
    run_migrations
    test_deployment
    
    echo ""
    log_success "🎉 Deployment Complete!"
    echo ""
    echo "Next steps:"
    echo "1. Access your platform"
    echo "2. Register admin user"
    echo "3. Test all features"
    echo "4. Set up monitoring alerts"
    echo "5. Configure backups"
    echo ""
    echo "Built following Musk's principles: ITERATE. BUILD. SHIP. 🚀"
}

# Run main
main "$@"

