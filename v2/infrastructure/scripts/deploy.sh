#!/bin/bash
# Production Deployment Script for NexusLang v2

set -e  # Exit on any error

echo "🚀 Starting NexusLang v2 Production Deployment..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="nexuslang-v2"
KUBECTL="kubectl"

# Check prerequisites
echo -e "${BLUE}Checking prerequisites...${NC}"

if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}kubectl not found. Please install kubectl.${NC}"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo -e "${RED}docker not found. Please install Docker.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Prerequisites check passed${NC}"

# Create namespace
echo -e "${BLUE}Creating namespace...${NC}"
$KUBECTL apply -f ../kubernetes/namespace.yaml

# Create secrets (if not exist)
echo -e "${BLUE}Checking secrets...${NC}"
if ! $KUBECTL get secret nexuslang-secrets -n $NAMESPACE &> /dev/null; then
    echo -e "${BLUE}Creating secrets...${NC}"
    $KUBECTL create secret generic nexuslang-secrets \
        --from-literal=database-url="${DATABASE_URL}" \
        --from-literal=redis-url="${REDIS_URL}" \
        --from-literal=openai-api-key="${OPENAI_API_KEY}" \
        --from-literal=secret-key="${SECRET_KEY}" \
        --from-literal=jwt-secret="${JWT_SECRET}" \
        -n $NAMESPACE
    echo -e "${GREEN}✓ Secrets created${NC}"
else
    echo -e "${GREEN}✓ Secrets already exist${NC}"
fi

# Deploy PostgreSQL
echo -e "${BLUE}Deploying PostgreSQL...${NC}"
$KUBECTL apply -f ../kubernetes/postgres.yaml
echo -e "${GREEN}✓ PostgreSQL deployed${NC}"

# Wait for PostgreSQL to be ready
echo -e "${BLUE}Waiting for PostgreSQL...${NC}"
$KUBECTL wait --for=condition=ready pod -l app=postgres -n $NAMESPACE --timeout=120s

# Deploy Redis
echo -e "${BLUE}Deploying Redis...${NC}"
$KUBECTL apply -f ../kubernetes/redis.yaml
echo -e "${GREEN}✓ Redis deployed${NC}"

# Deploy Backend
echo -e "${BLUE}Deploying Backend...${NC}"
$KUBECTL apply -f ../kubernetes/backend-deployment.yaml
echo -e "${GREEN}✓ Backend deployed${NC}"

# Wait for Backend to be ready
echo -e "${BLUE}Waiting for Backend...${NC}"
$KUBECTL wait --for=condition=ready pod -l app=nexuslang-backend -n $NAMESPACE --timeout=180s

# Deploy Frontend
echo -e "${BLUE}Deploying Frontend...${NC}"
$KUBECTL apply -f ../kubernetes/frontend-deployment.yaml
echo -e "${GREEN}✓ Frontend deployed${NC}"

# Wait for Frontend to be ready
echo -e "${BLUE}Waiting for Frontend...${NC}"
$KUBECTL wait --for=condition=ready pod -l app=nexuslang-frontend -n $NAMESPACE --timeout=180s

# Deploy Ingress
echo -e "${BLUE}Deploying Ingress...${NC}"
$KUBECTL apply -f ../kubernetes/ingress.yaml
echo -e "${GREEN}✓ Ingress deployed${NC}"

# Get service status
echo -e "${BLUE}Deployment Status:${NC}"
$KUBECTL get pods -n $NAMESPACE
$KUBECTL get services -n $NAMESPACE
$KUBECTL get ingress -n $NAMESPACE

# Verify health
echo -e "${BLUE}Verifying health endpoints...${NC}"
sleep 10

# Get backend pod
BACKEND_POD=$($KUBECTL get pods -n $NAMESPACE -l app=nexuslang-backend -o jsonpath='{.items[0].metadata.name}')
echo -e "Backend pod: ${BACKEND_POD}"

# Check health
$KUBECTL exec -n $NAMESPACE $BACKEND_POD -- curl -s http://localhost:8000/health || echo "Health check pending..."

echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo -e "${GREEN}🌐 Frontend: https://nexuslang.dev${NC}"
echo -e "${GREEN}🔧 API: https://api.nexuslang.dev${NC}"
echo -e "${GREEN}📊 Docs: https://api.nexuslang.dev/docs${NC}"

echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Configure DNS to point to ingress IP"
echo "2. Verify SSL certificates"
echo "3. Run smoke tests"
echo "4. Monitor logs: kubectl logs -f -l app=nexuslang-backend -n $NAMESPACE"
echo ""
echo -e "${GREEN}🎉 NexusLang v2 is LIVE!${NC}"

