#!/bin/bash
# Automated GPU Deployment Script for NexusLang v2 on RunPod
# Production-ready deployment with GPU optimization

set -e

# Configuration
REPO_URL="https://github.com/your-org/project-nexus.git"
BRANCH="main"
DOCKER_COMPOSE_FILE="docker-compose.gpu.yml"
ENV_FILE=".env.production"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✓ $1${NC}"
}

error() {
    echo -e "${RED}✗ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Pre-deployment checks
pre_deployment_checks() {
    log "Running pre-deployment checks..."

    # Check if running on GPU-enabled instance
    if ! command -v nvidia-smi &> /dev/null; then
        error "NVIDIA GPU not detected. This deployment requires GPU support."
        exit 1
    fi

    # Check GPU memory
    GPU_MEMORY=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1)
    if [ "$GPU_MEMORY" -lt 8000 ]; then
        warning "GPU has ${GPU_MEMORY}MB memory. Recommended: 8GB+ for optimal performance."
    fi

    # Check available disk space
    DISK_SPACE=$(df / | tail -1 | awk '{print $4}')
    if [ "$DISK_SPACE" -lt 20000000 ]; then
        error "Insufficient disk space. Required: 20GB+, Available: ${DISK_SPACE}KB"
        exit 1
    fi

    success "Pre-deployment checks passed"
}

# GPU-specific optimizations
gpu_optimizations() {
    log "Applying GPU-specific optimizations..."

    # Set GPU performance mode
    nvidia-smi -pm 1

    # Set GPU clock speeds for maximum performance
    nvidia-smi -ac 5001,1590

    # Enable GPU persistence mode
    nvidia-smi -pm 1

    # Set GPU power limit to maximum
    nvidia-smi -pl $(nvidia-smi --query-gpu=power.max_limit --format=csv,noheader,nounits | head -1)

    success "GPU optimizations applied"
}

# Clone and setup repository
setup_repository() {
    log "Setting up repository..."

    if [ -d "project-nexus" ]; then
        warning "Repository directory exists. Pulling latest changes..."
        cd project-nexus
        git pull origin $BRANCH
    else
        git clone -b $BRANCH $REPO_URL project-nexus
        cd project-nexus
    fi

    success "Repository setup complete"
}

# Environment configuration
setup_environment() {
    log "Setting up environment configuration..."

    if [ ! -f "$ENV_FILE" ]; then
        warning "Environment file not found. Creating from template..."
        if [ -f "config/production.env.template" ]; then
            cp config/production.env.template $ENV_FILE
            warning "Please edit $ENV_FILE with your production secrets before proceeding."
            exit 1
        else
            error "Environment template not found."
            exit 1
        fi
    fi

    # Validate environment variables
    required_vars=("DATABASE_URL" "REDIS_URL" "JWT_SECRET" "OPENAI_API_KEY")
    for var in "${required_vars[@]}"; do
        if ! grep -q "^$var=" "$ENV_FILE" || grep -q "^$var=your_" "$ENV_FILE"; then
            error "Required environment variable $var not set in $ENV_FILE"
            exit 1
        fi
    done

    success "Environment configuration validated"
}

# GPU model optimization
optimize_models() {
    log "Optimizing AI models for GPU deployment..."

    # Pre-download and cache models
    mkdir -p models_cache

    # Download essential models
    python3 -c "
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import os

# Check GPU availability
if torch.cuda.is_available():
    print('GPU detected, optimizing models...')
    device = torch.device('cuda')

    # Pre-load and cache common models
    models_to_cache = [
        'microsoft/DialoGPT-medium',
        'distilbert-base-uncased-finetuned-sst-2-english'
    ]

    for model_name in models_to_cache:
        try:
            print(f'Caching model: {model_name}')
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForCausalLM.from_pretrained(model_name)
            model.to(device)
            model.eval()
            print(f'Successfully cached: {model_name}')
        except Exception as e:
            print(f'Failed to cache {model_name}: {e}')

    print('Model optimization complete')
else:
    print('No GPU detected, skipping model optimization')
"

    success "Model optimization completed"
}

# Deploy services
deploy_services() {
    log "Deploying GPU-optimized services..."

    # Stop any existing services
    docker-compose -f $DOCKER_COMPOSE_FILE down --remove-orphans 2>/dev/null || true

    # Clean up unused resources
    docker system prune -f

    # Deploy with GPU support
    DOCKER_BUILDKIT=1 docker-compose -f $DOCKER_COMPOSE_FILE up -d --build

    success "Services deployed successfully"
}

# Post-deployment verification
verify_deployment() {
    log "Verifying deployment..."

    # Wait for services to be healthy
    max_attempts=30
    attempt=1

    while [ $attempt -le $max_attempts ]; do
        log "Health check attempt $attempt/$max_attempts..."

        # Check core services
        services_healthy=true

        # Check nginx
        if ! curl -f -s http://localhost/nginx-health > /dev/null; then
            services_healthy=false
        fi

        # Check backend
        if ! curl -f -s http://localhost:8010/health > /dev/null; then
            services_healthy=false
        fi

        # Check AI models (if deployed)
        if curl -f -s http://localhost:8011/health > /dev/null 2>&1; then
            success "AI Models service is healthy"
        else
            warning "AI Models service not yet ready (may be initializing)"
        fi

        if $services_healthy; then
            success "All core services are healthy!"
            break
        fi

        sleep 10
        ((attempt++))
    done

    if [ $attempt -gt $max_attempts ]; then
        error "Deployment verification failed - services not healthy"
        exit 1
    fi
}

# Performance benchmarking
run_benchmarks() {
    log "Running GPU performance benchmarks..."

    # GPU memory benchmark
    nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader,nounits

    # PyTorch GPU benchmark
    python3 -c "
import torch
import time

if torch.cuda.is_available():
    device = torch.device('cuda')
    print(f'GPU: {torch.cuda.get_device_name(0)}')

    # Memory benchmark
    total_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
    print(f'Total GPU Memory: {total_memory:.1f} GB')

    # Computation benchmark
    size = 5000
    A = torch.randn(size, size, device=device)
    B = torch.randn(size, size, device=device)

    start_time = time.time()
    C = torch.mm(A, B)
    torch.cuda.synchronize()
    end_time = time.time()

    print(f'Matrix multiplication ({size}x{size}): {(end_time - start_time)*1000:.2f} ms')
    print('GPU benchmark completed successfully')
else:
    print('No GPU available for benchmarking')
"

    success "Performance benchmarks completed"
}

# Setup monitoring and alerts
setup_monitoring() {
    log "Setting up production monitoring..."

    # GPU monitoring
    cat > gpu_monitor.sh << 'EOF'
#!/bin/bash
while true; do
    TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
    GPU_INFO=$(nvidia-smi --query-gpu=index,name,memory.used,memory.total,utilization.gpu,utilization.memory,temperature.gpu --format=csv,noheader,nounits)

    # Log to file and send to monitoring
    echo "[$TIMESTAMP] GPU Status: $GPU_INFO" >> /app/logs/gpu_monitor.log

    # Check for critical conditions
    GPU_UTIL=$(echo $GPU_INFO | cut -d',' -f5)
    GPU_TEMP=$(echo $GPU_INFO | cut -d',' -f7)

    if [ "$GPU_UTIL" -gt 95 ]; then
        echo "[$TIMESTAMP] CRITICAL: GPU utilization at ${GPU_UTIL}%" >> /app/logs/alerts.log
    fi

    if [ "$GPU_TEMP" -gt 85 ]; then
        echo "[$TIMESTAMP] WARNING: GPU temperature at ${GPU_TEMP}°C" >> /app/logs/alerts.log
    fi

    sleep 30
done
EOF

    chmod +x gpu_monitor.sh
    nohup ./gpu_monitor.sh > /dev/null 2>&1 &

    success "GPU monitoring setup completed"
}

# Main deployment function
main() {
    log "Starting NexusLang v2 GPU Deployment on RunPod"
    echo "=================================================="

    pre_deployment_checks
    gpu_optimizations
    setup_repository
    setup_environment
    optimize_models
    deploy_services
    verify_deployment
    run_benchmarks
    setup_monitoring

    echo ""
    echo "=================================================="
    success "NEXUSLANG V2 GPU DEPLOYMENT COMPLETE!"
    echo ""
    echo "🌐 Access URLs:"
    echo "   • Main Application: http://localhost"
    echo "   • API Documentation: http://localhost:8010/docs"
    echo "   • Monitoring Dashboard: http://localhost:8080"
    echo "   • Grafana: http://localhost:3001 (admin/admin123)"
    echo ""
    echo "🎯 GPU Services:"
    echo "   • AI Models API: http://localhost:8011"
    echo "   • GPU Status: http://localhost/gpu-status"
    echo ""
    echo "📊 Monitoring:"
    echo "   • Prometheus: http://localhost:9090"
    echo "   • GPU Metrics: http://localhost/metrics/gpu"
    echo ""
    warning "Remember to:"
    warning "  1. Configure SSL certificates for production"
    warning "  2. Set up proper domain names and DNS"
    warning "  3. Configure backup and disaster recovery"
    warning "  4. Set up alerting and notifications"
}

# Run main function
main "$@"
