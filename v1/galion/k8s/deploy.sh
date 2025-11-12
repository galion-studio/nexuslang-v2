#!/bin/bash
# Kubernetes Deployment Script for Nexus Core
# Deploy to production with galion.app domains

set -e

echo "🚀 Deploying Nexus Core to Kubernetes"
echo "========================================"

# Configuration
NAMESPACE="nexus-core"
REGISTRY="nexuscore"  # Docker registry
VERSION=${1:-latest}

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}kubectl not found. Please install kubectl.${NC}"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo -e "${RED}docker not found. Please install Docker.${NC}"
    exit 1
fi

# Create namespace
echo -e "${GREEN}Creating namespace...${NC}"
kubectl apply -f k8s/namespace.yaml

# Create secrets (if not exists)
echo -e "${GREEN}Creating secrets...${NC}"
if ! kubectl get secret nexus-secrets -n $NAMESPACE &> /dev/null; then
    echo -e "${YELLOW}Warning: Creating default secrets. Update with actual values!${NC}"
    kubectl apply -f k8s/secrets.yaml
else
    echo "Secrets already exist, skipping..."
fi

# Create config maps
echo -e "${GREEN}Creating config maps...${NC}"
kubectl apply -f k8s/configmap.yaml

# Build and push Docker images
echo -e "${GREEN}Building Docker images...${NC}"
echo "Building API Gateway..."
docker build -t $REGISTRY/api-gateway:$VERSION ./services/api-gateway
docker push $REGISTRY/api-gateway:$VERSION

echo "Building Auth Service..."
docker build -t $REGISTRY/auth-service:$VERSION ./services/auth-service
docker push $REGISTRY/auth-service:$VERSION

echo "Building User Service..."
docker build -t $REGISTRY/user-service:$VERSION ./services/user-service
docker push $REGISTRY/user-service:$VERSION

echo "Building Analytics Service..."
docker build -t $REGISTRY/analytics-service:$VERSION ./services/analytics-service
docker push $REGISTRY/analytics-service:$VERSION

echo "Building Scraping Service..."
docker build -t $REGISTRY/scraping-service:$VERSION ./services/scraping-service
docker push $REGISTRY/scraping-service:$VERSION

# Deploy database
echo -e "${GREEN}Deploying PostgreSQL...${NC}"
kubectl apply -f k8s/postgres.yaml

# Deploy Redis
echo -e "${GREEN}Deploying Redis...${NC}"
kubectl apply -f k8s/redis.yaml

# Wait for databases
echo -e "${YELLOW}Waiting for databases to be ready...${NC}"
kubectl wait --for=condition=ready pod -l app=postgres -n $NAMESPACE --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis -n $NAMESPACE --timeout=300s

# Deploy Kafka (if exists)
if [ -f k8s/kafka.yaml ]; then
    echo -e "${GREEN}Deploying Kafka...${NC}"
    kubectl apply -f k8s/kafka.yaml
    kubectl wait --for=condition=ready pod -l app=kafka -n $NAMESPACE --timeout=300s
fi

# Deploy application services
echo -e "${GREEN}Deploying application services...${NC}"
kubectl apply -f k8s/auth-service.yaml
kubectl apply -f k8s/user-service.yaml
kubectl apply -f k8s/analytics-service.yaml
kubectl apply -f k8s/scraping-service.yaml
kubectl apply -f k8s/api-gateway.yaml

# Deploy monitoring (if exists)
if [ -f k8s/prometheus.yaml ]; then
    echo -e "${GREEN}Deploying monitoring stack...${NC}"
    kubectl apply -f k8s/prometheus.yaml
    kubectl apply -f k8s/grafana.yaml
fi

# Deploy ingress
echo -e "${GREEN}Deploying ingress...${NC}"
kubectl apply -f k8s/ingress.yaml

# Wait for deployments
echo -e "${YELLOW}Waiting for deployments to be ready...${NC}"
kubectl wait --for=condition=available deployment --all -n $NAMESPACE --timeout=300s

# Get service status
echo -e "${GREEN}Deployment Status:${NC}"
kubectl get pods -n $NAMESPACE
kubectl get services -n $NAMESPACE
kubectl get ingress -n $NAMESPACE

# Get ingress URL
echo -e "${GREEN}=========================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}=========================${NC}"
echo ""
echo "Access your services at:"
echo "  🌐 Main site:    https://galion.app"
echo "  🔌 API:          https://api.galion.app"
echo "  💻 App:          https://app.galion.app"
echo "  📊 Grafana:      https://grafana.galion.app"
echo ""
echo "View logs:"
echo "  kubectl logs -f deployment/api-gateway -n $NAMESPACE"
echo ""
echo "Scale services:"
echo "  kubectl scale deployment/scraping-service --replicas=5 -n $NAMESPACE"
echo ""
echo -e "${YELLOW}Note: Ensure DNS records are configured for galion.app domains${NC}"
echo -e "${YELLOW}Note: SSL certificates will be automatically provisioned by cert-manager${NC}"

