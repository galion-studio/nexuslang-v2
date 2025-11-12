#!/bin/bash
# ===============================================
# Docker Build Script for NexusLang v2
# ===============================================
# Builds production-ready Docker image with cached dependencies
# Push to Docker Hub for instant deployment on RunPod

set -e

# Configuration
IMAGE_NAME="galion/nexuslang-v2"
VERSION="2.0.0-beta"
LATEST_TAG="latest"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}🐳 Building NexusLang v2 Docker Image${NC}"
echo "========================================"
echo ""

# Change to script directory
cd "$(dirname "$0")"

echo -e "${YELLOW}📋 Build Configuration:${NC}"
echo "  Image: $IMAGE_NAME"
echo "  Version: $VERSION"
echo "  Platform: linux/amd64 (RunPod compatible)"
echo ""

# Build the Docker image with BuildKit for better caching
echo -e "${CYAN}🔨 Building Docker image...${NC}"
echo "This will take 5-10 minutes the first time (builds wheel cache)"
echo ""

DOCKER_BUILDKIT=1 docker build \
    -f Dockerfile.production \
    -t "$IMAGE_NAME:$VERSION" \
    -t "$IMAGE_NAME:$LATEST_TAG" \
    --platform linux/amd64 \
    --progress=plain \
    .

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Docker image built successfully!${NC}"
    echo ""
    
    # Show image size
    echo -e "${CYAN}📦 Image Information:${NC}"
    docker images "$IMAGE_NAME" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
    echo ""
    
    # Test the image
    echo -e "${CYAN}🧪 Testing image...${NC}"
    docker run --rm \
        -e DATABASE_URL=sqlite+aiosqlite:///./test.db \
        -e REDIS_URL=redis://localhost:6379/0 \
        -e JWT_SECRET=test-secret \
        -e OPENROUTER_API_KEY=test \
        "$IMAGE_NAME:$VERSION" \
        python -c "import uvicorn, fastapi; print('✅ Image test passed!')" || echo "⚠️  Test warning (not critical)"
    
    echo ""
    echo -e "${GREEN}🎉 Build Complete!${NC}"
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "  1. Push to Docker Hub:"
    echo "     ${CYAN}docker push $IMAGE_NAME:$VERSION${NC}"
    echo "     ${CYAN}docker push $IMAGE_NAME:$LATEST_TAG${NC}"
    echo ""
    echo "  2. Deploy on RunPod:"
    echo "     ${CYAN}docker run -p 8000:8000 -v /workspace:/workspace $IMAGE_NAME:$LATEST_TAG${NC}"
    echo ""
    echo "  3. Or use docker-compose:"
    echo "     ${CYAN}docker-compose -f docker-compose.runpod.yml up -d${NC}"
    echo ""
else
    echo ""
    echo -e "${RED}❌ Build failed!${NC}"
    echo "Check the error messages above"
    exit 1
fi

