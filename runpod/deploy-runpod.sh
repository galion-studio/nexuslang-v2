#!/bin/bash
# Galion Autonomous Agent System - RunPod Deployment Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
RUNPOD_API_KEY=${RUNPOD_API_KEY:-""}
TEMPLATE_NAME="galion-agent-system"
IMAGE_NAME="galion-agent:latest"
TEMPLATE_FILE="runpod-template.json"

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

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    # Check if RunPod CLI is available or API key is set
    if [ -z "$RUNPOD_API_KEY" ] && ! command -v runpod &> /dev/null; then
        log_error "RunPod API key not set and CLI not found."
        log_info "Please set RUNPOD_API_KEY environment variable or install RunPod CLI."
        exit 1
    fi

    # Check if template file exists
    if [ ! -f "$TEMPLATE_FILE" ]; then
        log_error "Template file $TEMPLATE_FILE not found!"
        exit 1
    fi

    log_success "Prerequisites check passed"
}

# Build Docker image
build_image() {
    log_info "Building Docker image..."

    if docker build -t $IMAGE_NAME -f runpod/Dockerfile .; then
        log_success "Docker image built successfully"
    else
        log_error "Failed to build Docker image"
        exit 1
    fi
}

# Push image to registry (if needed)
push_image() {
    log_info "Pushing image to registry..."

    # For RunPod, you might need to push to a registry
    # This is optional if you're using local Docker
    if [ -n "$REGISTRY_URL" ]; then
        docker tag $IMAGE_NAME $REGISTRY_URL/$IMAGE_NAME
        docker push $REGISTRY_URL/$IMAGE_NAME
        log_success "Image pushed to registry"
    else
        log_info "Skipping registry push (using local image)"
    fi
}

# Create RunPod template
create_template() {
    log_info "Creating RunPod template..."

    if [ -n "$RUNPOD_API_KEY" ]; then
        # Using API
        log_info "Using RunPod API..."

        # Read template file
        template_data=$(cat $TEMPLATE_FILE)

        # Create template via API
        response=$(curl -s -X POST \
            -H "Authorization: Bearer $RUNPOD_API_KEY" \
            -H "Content-Type: application/json" \
            -d "$template_data" \
            https://api.runpod.io/v1/templates)

        if echo "$response" | grep -q "id"; then
            template_id=$(echo "$response" | jq -r '.id')
            log_success "Template created with ID: $template_id"
            echo $template_id > .runpod_template_id
        else
            log_error "Failed to create template: $response"
            exit 1
        fi

    elif command -v runpod &> /dev/null; then
        # Using CLI
        log_info "Using RunPod CLI..."

        if runpod template create -f $TEMPLATE_FILE; then
            log_success "Template created via CLI"
        else
            log_error "Failed to create template via CLI"
            exit 1
        fi
    else
        log_error "No RunPod authentication method available"
        exit 1
    fi
}

# Deploy pod
deploy_pod() {
    log_info "Deploying RunPod pod..."

    # Get template ID if it exists
    if [ -f .runpod_template_id ]; then
        template_id=$(cat .runpod_template_id)
    else
        log_error "Template ID not found. Please create template first."
        exit 1
    fi

    # Set environment variables
    env_vars=""
    if [ -n "$OPENAI_API_KEY" ]; then
        env_vars="$env_vars --env OPENAI_API_KEY=$OPENAI_API_KEY"
    fi

    if [ -n "$JWT_SECRET_KEY" ]; then
        env_vars="$env_vars --env JWT_SECRET_KEY=$JWT_SECRET_KEY"
    fi

    # Deploy pod
    if [ -n "$RUNPOD_API_KEY" ]; then
        # Using API
        deploy_data="{
            \"templateId\": \"$template_id\",
            \"name\": \"galion-agent-pod\",
            \"imageName\": \"$IMAGE_NAME\",
            \"env\": [
                {\"key\": \"OPENAI_API_KEY\", \"value\": \"$OPENAI_API_KEY\"},
                {\"key\": \"JWT_SECRET_KEY\", \"value\": \"$JWT_SECRET_KEY\"}
            ]
        }"

        response=$(curl -s -X POST \
            -H "Authorization: Bearer $RUNPOD_API_KEY" \
            -H "Content-Type: application/json" \
            -d "$deploy_data" \
            https://api.runpod.io/v1/pods)

        if echo "$response" | grep -q "id"; then
            pod_id=$(echo "$response" | jq -r '.id')
            log_success "Pod deployed with ID: $pod_id"
            echo $pod_id > .runpod_pod_id

            # Wait for pod to be ready
            wait_for_pod $pod_id
        else
            log_error "Failed to deploy pod: $response"
            exit 1
        fi

    elif command -v runpod &> /dev/null; then
        # Using CLI
        if runpod pod create $template_id --name galion-agent-pod $env_vars; then
            log_success "Pod deployed via CLI"
        else
            log_error "Failed to deploy pod via CLI"
            exit 1
        fi
    fi
}

# Wait for pod to be ready
wait_for_pod() {
    local pod_id=$1
    local max_attempts=30
    local attempt=1

    log_info "Waiting for pod $pod_id to be ready..."

    while [ $attempt -le $max_attempts ]; do
        if [ -n "$RUNPOD_API_KEY" ]; then
            # Check status via API
            status=$(curl -s -H "Authorization: Bearer $RUNPOD_API_KEY" \
                https://api.runpod.io/v1/pods/$pod_id | jq -r '.status')

            if [ "$status" = "RUNNING" ]; then
                log_success "Pod is now running!"
                return 0
            fi
        elif command -v runpod &> /dev/null; then
            # Check status via CLI
            if runpod pod status $pod_id | grep -q "RUNNING"; then
                log_success "Pod is now running!"
                return 0
            fi
        fi

        log_info "Attempt $attempt/$max_attempts: Pod not ready yet..."
        sleep 10
        ((attempt++))
    done

    log_error "Pod failed to start after $max_attempts attempts"
    return 1
}

# Get pod information
get_pod_info() {
    log_info "Getting pod information..."

    if [ -f .runpod_pod_id ]; then
        pod_id=$(cat .runpod_pod_id)

        if [ -n "$RUNPOD_API_KEY" ]; then
            pod_info=$(curl -s -H "Authorization: Bearer $RUNPOD_API_KEY" \
                https://api.runpod.io/v1/pods/$pod_id)

            public_ip=$(echo "$pod_info" | jq -r '.publicIp')
            status=$(echo "$pod_info" | jq -r '.status')

            echo "========================================"
            echo "Pod Information:"
            echo "ID: $pod_id"
            echo "Status: $status"
            echo "Public IP: $public_ip"
            echo "========================================"
            echo ""
            echo "Access URLs:"
            echo "🌐 Frontend:    http://$public_ip"
            echo "📚 API Docs:    http://$public_ip:8010/docs"
            echo "🔍 Health:      http://$public_ip:8010/health"
            echo "📊 Monitoring:  http://$public_ip:8010/monitoring/status"
            echo "🎛️  Grafana:     http://$public_ip:3001 (admin/admin)"
            echo "📈 Prometheus:  http://$public_ip:9090"
            echo "========================================"

        elif command -v runpod &> /dev/null; then
            runpod pod info $pod_id
        fi
    else
        log_error "Pod ID not found"
    fi
}

# Cleanup function
cleanup() {
    log_info "Cleaning up..."

    # Stop and remove pod if it exists
    if [ -f .runpod_pod_id ]; then
        pod_id=$(cat .runpod_pod_id)

        if [ -n "$RUNPOD_API_KEY" ]; then
            curl -s -X DELETE \
                -H "Authorization: Bearer $RUNPOD_API_KEY" \
                https://api.runpod.io/v1/pods/$pod_id >/dev/null
        elif command -v runpod &> /dev/null; then
            runpod pod stop $pod_id
        fi

        rm .runpod_pod_id
        log_success "Pod cleaned up"
    fi

    # Remove template if it exists
    if [ -f .runpod_template_id ]; then
        template_id=$(cat .runpod_template_id)

        if [ -n "$RUNPOD_API_KEY" ]; then
            curl -s -X DELETE \
                -H "Authorization: Bearer $RUNPOD_API_KEY" \
                https://api.runpod.io/v1/templates/$template_id >/dev/null
        elif command -v runpod &> /dev/null; then
            runpod template delete $template_id
        fi

        rm .runpod_template_id
        log_success "Template cleaned up"
    fi
}

# Show usage
show_usage() {
    echo "Galion Autonomous Agent System - RunPod Deployment"
    echo ""
    echo "Usage:"
    echo "  $0 [command]"
    echo ""
    echo "Commands:"
    echo "  deploy    - Full deployment (build, push, create template, deploy pod)"
    echo "  build     - Build Docker image only"
    echo "  template  - Create template only"
    echo "  pod       - Deploy pod only"
    echo "  info      - Show pod information"
    echo "  cleanup   - Clean up resources"
    echo "  help      - Show this help"
    echo ""
    echo "Environment Variables:"
    echo "  RUNPOD_API_KEY     - RunPod API key (required)"
    echo "  OPENAI_API_KEY     - OpenAI API key (required)"
    echo "  JWT_SECRET_KEY     - JWT secret (optional)"
    echo "  REGISTRY_URL       - Docker registry URL (optional)"
}

# Main function
main() {
    case "${1:-deploy}" in
        "deploy")
            check_prerequisites
            build_image
            push_image
            create_template
            deploy_pod
            get_pod_info
            ;;
        "build")
            check_prerequisites
            build_image
            ;;
        "template")
            check_prerequisites
            create_template
            ;;
        "pod")
            check_prerequisites
            deploy_pod
            get_pod_info
            ;;
        "info")
            get_pod_info
            ;;
        "cleanup")
            cleanup
            ;;
        "help"|*)
            show_usage
            ;;
    esac
}

# Run main function with all arguments
main "$@"
