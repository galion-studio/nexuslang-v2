#!/bin/bash
# Nexus Lang V2 Scientific Knowledge Enhancement - RunPod Deployment Script
# =========================================================================
#
# This script automates the deployment of the scientific AI system to RunPod.
#
# Usage:
#   ./deploy-runpod.sh [command]
#
# Commands:
#   build     - Build the Docker image
#   push      - Push image to registry
#   deploy    - Deploy to RunPod
#   update    - Update existing deployment
#   logs      - View deployment logs
#   status    - Check deployment status
#   test      - Test the deployment
#   cleanup   - Clean up resources
#
# Environment Variables:
#   RUNPOD_API_KEY    - RunPod API key
#   DOCKER_REGISTRY   - Docker registry URL
#   IMAGE_TAG         - Docker image tag (default: latest)

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
PROJECT_NAME="nexus-lang-v2-scientific"
DOCKER_REGISTRY="${DOCKER_REGISTRY:-runpod}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
IMAGE_NAME="${DOCKER_REGISTRY}/${PROJECT_NAME}:${IMAGE_TAG}"

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

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    # Check if RunPod CLI is installed
    if ! command -v runpodctl &> /dev/null; then
        log_warning "RunPod CLI not found. Installing..."
        curl -sSL https://github.com/runpod/runpodctl/releases/latest/download/runpodctl-linux-amd64.tar.gz | tar -xz
        sudo mv runpodctl /usr/local/bin/
    fi

    # Check RunPod API key
    if [ -z "$RUNPOD_API_KEY" ]; then
        log_error "RUNPOD_API_KEY environment variable not set"
        log_info "Get your API key from: https://runpod.io/console/user/settings"
        exit 1
    fi

    # Login to RunPod
    log_info "Authenticating with RunPod..."
    echo "$RUNPOD_API_KEY" | runpodctl config --api-key

    log_success "Prerequisites check passed"
}

# Build Docker image
build_image() {
    log_info "Building Docker image: ${IMAGE_NAME}"

    cd "$SCRIPT_DIR"

    # Build the image
    docker build -f runpod.Dockerfile -t "$IMAGE_NAME" .

    # Tag as latest
    docker tag "$IMAGE_NAME" "${DOCKER_REGISTRY}/${PROJECT_NAME}:latest"

    log_success "Docker image built successfully"
}

# Push image to registry
push_image() {
    log_info "Pushing image to registry: ${IMAGE_NAME}"

    # Login to registry if needed
    if [ "$DOCKER_REGISTRY" = "runpod" ]; then
        log_info "Using RunPod container registry"
    else
        log_warning "Using custom registry: ${DOCKER_REGISTRY}"
        log_info "Make sure you're logged in: docker login ${DOCKER_REGISTRY}"
    fi

    # Push the image
    docker push "$IMAGE_NAME"
    docker push "${DOCKER_REGISTRY}/${PROJECT_NAME}:latest"

    log_success "Image pushed successfully"
}

# Deploy to RunPod
deploy_to_runpod() {
    log_info "Deploying to RunPod..."

    cd "$SCRIPT_DIR"

    # Create or update deployment
    if runpodctl get pods | grep -q "${PROJECT_NAME}"; then
        log_info "Updating existing deployment..."
        runpodctl update pod "${PROJECT_NAME}" --image "$IMAGE_NAME"
    else
        log_info "Creating new deployment..."
        runpodctl create pod \
            --name "${PROJECT_NAME}" \
            --image "$IMAGE_NAME" \
            --gpu-type "NVIDIA RTX A4000" \
            --ports "8000/http,8080/http" \
            --env "PYTHONPATH=/workspace" \
            --env "LOG_LEVEL=INFO" \
            --volume "/workspace/data:/workspace/data" \
            --volume "/workspace/logs:/workspace/logs"
    fi

    # Wait for deployment to be ready
    log_info "Waiting for deployment to be ready..."
    for i in {1..30}; do
        if runpodctl get pods | grep -q "${PROJECT_NAME}.*Running"; then
            break
        fi
        echo -n "."
        sleep 10
    done

    echo ""

    # Get pod information
    POD_INFO=$(runpodctl get pods | grep "${PROJECT_NAME}")
    if [ -n "$POD_INFO" ]; then
        log_success "Deployment completed successfully"
        echo "$POD_INFO"
    else
        log_error "Deployment failed or pod not found"
        exit 1
    fi
}

# Update existing deployment
update_deployment() {
    log_info "Updating existing deployment..."

    if ! runpodctl get pods | grep -q "${PROJECT_NAME}"; then
        log_error "No existing deployment found. Use 'deploy' command first."
        exit 1
    fi

    # Build and push new image
    build_image
    push_image

    # Update the deployment
    runpodctl update pod "${PROJECT_NAME}" --image "$IMAGE_NAME"

    log_success "Deployment updated successfully"
}

# View deployment logs
view_logs() {
    log_info "Fetching deployment logs..."

    if ! runpodctl get pods | grep -q "${PROJECT_NAME}"; then
        log_error "No deployment found"
        exit 1
    fi

    runpodctl logs "${PROJECT_NAME}"
}

# Check deployment status
check_status() {
    log_info "Checking deployment status..."

    POD_INFO=$(runpodctl get pods | grep "${PROJECT_NAME}")
    if [ -n "$POD_INFO" ]; then
        echo "$POD_INFO"

        # Extract pod ID and get more details
        POD_ID=$(echo "$POD_INFO" | awk '{print $1}')
        if [ -n "$POD_ID" ]; then
            log_info "Pod details:"
            runpodctl get pod "$POD_ID"
        fi
    else
        log_error "No deployment found"
    fi
}

# Test the deployment
test_deployment() {
    log_info "Testing deployment..."

    # Get pod endpoint
    POD_INFO=$(runpodctl get pods | grep "${PROJECT_NAME}")
    if [ -z "$POD_INFO" ]; then
        log_error "No deployment found"
        exit 1
    fi

    # Extract endpoint (this might need adjustment based on RunPod output format)
    ENDPOINT=$(echo "$POD_INFO" | grep -o 'https://[^ ]*')

    if [ -z "$ENDPOINT" ]; then
        log_warning "Could not extract endpoint from pod info"
        log_info "Pod info:"
        echo "$POD_INFO"
        exit 1
    fi

    log_info "Testing API endpoint: ${ENDPOINT}/health"

    # Test health endpoint
    if curl -s -f "${ENDPOINT}/health" > /dev/null; then
        log_success "Health check passed"

        # Test scientific query
        log_info "Testing scientific query..."
        QUERY_RESPONSE=$(curl -s -X POST "${ENDPOINT}/api/v1/grokopedia/scientific-query" \
            -H "Content-Type: application/json" \
            -d '{"query": "Explain Newton'\''s first law", "domain_focus": "physics"}')

        if echo "$QUERY_RESPONSE" | grep -q "success"; then
            log_success "Scientific query test passed"
        else
            log_warning "Scientific query test may have issues"
            echo "Response: $QUERY_RESPONSE"
        fi

    else
        log_error "Health check failed"
        exit 1
    fi
}

# Clean up resources
cleanup_resources() {
    log_info "Cleaning up resources..."

    # Stop and remove pod
    if runpodctl get pods | grep -q "${PROJECT_NAME}"; then
        log_info "Removing deployment..."
        runpodctl delete pod "${PROJECT_NAME}"
        log_success "Deployment removed"
    else
        log_warning "No deployment found to remove"
    fi

    # Remove local images
    log_info "Cleaning up local Docker images..."
    docker rmi "$IMAGE_NAME" 2>/dev/null || true
    docker rmi "${DOCKER_REGISTRY}/${PROJECT_NAME}:latest" 2>/dev/null || true

    log_success "Cleanup completed"
}

# Show usage information
show_usage() {
    cat << EOF
Nexus Lang V2 Scientific Knowledge Enhancement - RunPod Deployment

Usage: $0 [command]

Commands:
    build     - Build the Docker image
    push      - Push image to registry
    deploy    - Deploy to RunPod (build + push + deploy)
    update    - Update existing deployment
    logs      - View deployment logs
    status    - Check deployment status
    test      - Test the deployment
    cleanup   - Clean up resources
    help      - Show this help message

Environment Variables:
    RUNPOD_API_KEY    - RunPod API key (required)
    DOCKER_REGISTRY   - Docker registry URL (default: runpod)
    IMAGE_TAG         - Docker image tag (default: latest)

Examples:
    export RUNPOD_API_KEY="your-api-key-here"
    $0 deploy
    $0 logs
    $0 test

For more information, see: https://docs.runpod.io/
EOF
}

# Main script logic
main() {
    COMMAND=${1:-"help"}

    case $COMMAND in
        build)
            check_prerequisites
            build_image
            ;;
        push)
            check_prerequisites
            push_image
            ;;
        deploy)
            check_prerequisites
            build_image
            push_image
            deploy_to_runpod
            ;;
        update)
            check_prerequisites
            update_deployment
            ;;
        logs)
            check_prerequisites
            view_logs
            ;;
        status)
            check_prerequisites
            check_status
            ;;
        test)
            check_prerequisites
            test_deployment
            ;;
        cleanup)
            check_prerequisites
            cleanup_resources
            ;;
        help|--help|-h)
            show_usage
            ;;
        *)
            log_error "Unknown command: $COMMAND"
            echo ""
            show_usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
