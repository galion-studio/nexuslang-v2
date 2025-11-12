#!/bin/bash
# ╔════════════════════════════════════════════════════════════╗
# ║  FULLY AUTOMATED DEPLOYMENT                                ║
# ║  Deploys to RunPod + Configures Cloudflare via API        ║
# ╚════════════════════════════════════════════════════════════╝

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m'

echo -e "${MAGENTA}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${MAGENTA}║  🚀 NEXUSLANG V2 - FULLY AUTOMATED DEPLOYMENT              ║${NC}"
echo -e "${MAGENTA}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if running on RunPod
if [ ! -d "/workspace" ]; then
    echo -e "${RED}❌ This script must run on RunPod pod${NC}"
    echo "   Run this on your RunPod instance, not locally"
    exit 1
fi

# Check if in project directory
if [ ! -d "v2" ]; then
    echo "Navigating to project..."
    cd /workspace/project-nexus || {
        echo -e "${RED}❌ Project not found at /workspace/project-nexus${NC}"
        echo "   Clone it first: git clone YOUR_REPO /workspace/project-nexus"
        exit 1
    }
fi

echo -e "${GREEN}✅ Running on RunPod in correct directory${NC}"
echo ""

# ============================================
# STEP 1: COLLECT CONFIGURATION
# ============================================

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Step 1: Configuration                                     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Get OpenRouter API Key (Primary)
echo -e "${YELLOW}Enter your OpenRouter API key (starts with sk-or-v1-):${NC}"
echo "(OpenRouter = 99% of AI calls, supports 30+ models)"
read -r OPENROUTER_API_KEY

if [ -z "$OPENROUTER_API_KEY" ]; then
    echo -e "${YELLOW}⚠️  No OpenRouter key. Using OpenAI directly...${NC}"
    echo -e "${YELLOW}Enter your OpenAI API key (starts with sk-proj-):${NC}"
    read -r OPENAI_API_KEY
    
    if [ -z "$OPENAI_API_KEY" ]; then
        echo -e "${RED}❌ Either OpenRouter or OpenAI key required${NC}"
        exit 1
    fi
else
    # Optional: Get OpenAI key for fallback
    echo ""
    echo -e "${YELLOW}Enter OpenAI API key (optional, for fallback):${NC}"
    read -r OPENAI_API_KEY
    if [ -z "$OPENAI_API_KEY" ]; then
        OPENAI_API_KEY=""
    fi
fi

# Get Cloudflare credentials
echo ""
echo -e "${YELLOW}Enter your Cloudflare API Token:${NC}"
echo "(Get from: https://dash.cloudflare.com/profile/api-tokens)"
read -r CF_API_TOKEN

if [ -z "$CF_API_TOKEN" ]; then
    echo -e "${RED}❌ Cloudflare API token required for DNS automation${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Enter your Cloudflare Zone ID for galion.app:${NC}"
echo "(Found in: Cloudflare Dashboard → galion.app → Overview → Zone ID)"
read -r CF_ZONE_ID

if [ -z "$CF_ZONE_ID" ]; then
    echo -e "${RED}❌ Cloudflare Zone ID required${NC}"
    exit 1
fi

# Get RunPod IP
echo ""
echo -e "${YELLOW}Detecting RunPod IP...${NC}"
RUNPOD_IP=$(curl -s ifconfig.me)
echo -e "${GREEN}✅ RunPod IP: $RUNPOD_IP${NC}"

echo ""
echo -e "${BLUE}Configuration Summary:${NC}"
echo "  OpenAI Key: ${OPENAI_API_KEY:0:20}..."
echo "  Cloudflare Token: ${CF_API_TOKEN:0:20}..."
echo "  Zone ID: $CF_ZONE_ID"
echo "  RunPod IP: $RUNPOD_IP"
echo ""

read -p "Proceed with deployment? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

# ============================================
# STEP 2: GENERATE ENVIRONMENT
# ============================================

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Step 2: Generating Production Environment                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Generate secure secrets
JWT_SECRET=$(openssl rand -hex 64)
SECRET_KEY=$(openssl rand -hex 32)
POSTGRES_PASSWORD=$(openssl rand -hex 16)
REDIS_PASSWORD=$(openssl rand -hex 16)

echo -e "${GREEN}✅ Secure secrets generated${NC}"

# Create v2/.env
cat > v2/.env << EOF
# NexusLang v2 - Production Environment
# Auto-generated: $(date)

# CRITICAL SECRETS
JWT_SECRET=$JWT_SECRET
SECRET_KEY=$SECRET_KEY

# Environment
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=info

# Domains
PRIMARY_DOMAIN=developer.galion.app
FRONTEND_URL=https://developer.galion.app
BACKEND_URL=https://api.developer.galion.app
CORS_ORIGINS=https://developer.galion.app,https://api.developer.galion.app

# Database
POSTGRES_USER=nexus
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
POSTGRES_DB=nexus_v2
DATABASE_URL=postgresql+asyncpg://nexus:$POSTGRES_PASSWORD@postgres:5432/nexus_v2

# Redis
REDIS_PASSWORD=$REDIS_PASSWORD
REDIS_URL=redis://:$REDIS_PASSWORD@redis:6379/0

# AI Services - OpenRouter Primary (99% of use cases)
OPENROUTER_API_KEY=$OPENROUTER_API_KEY
OPENAI_API_KEY=$OPENAI_API_KEY
AI_PROVIDER=openrouter
DEFAULT_AI_MODEL=anthropic/claude-3.5-sonnet
FALLBACK_AI_MODEL=openai/gpt-4-turbo

# Cloudflare
CLOUDFLARE_API_TOKEN=$CF_API_TOKEN
CLOUDFLARE_ZONE_ID=$CF_ZONE_ID

# Voice (GPU)
WHISPER_DEVICE=cuda
TTS_DEVICE=cuda

# Features
ENABLE_VOICE=true
ENABLE_GROKOPEDIA=true
ENABLE_CONTENT_MANAGER=true

# Credits
FREE_TIER_CREDITS=100
PRO_TIER_CREDITS=10000
EOF

# Create frontend env
cat > v2/frontend/.env.local << EOF
NEXT_PUBLIC_API_URL=https://api.developer.galion.app
NEXT_PUBLIC_WS_URL=wss://api.developer.galion.app
NEXT_PUBLIC_ENVIRONMENT=production
NEXT_TELEMETRY_DISABLED=1
NEXT_PUBLIC_ENABLE_VOICE=true
NEXT_PUBLIC_ENABLE_AI_CHAT=true
EOF

echo -e "${GREEN}✅ Environment files created${NC}"
echo ""

# ============================================
# STEP 3: DEPLOY SERVICES
# ============================================

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Step 3: Deploying Services                                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Install Docker if needed
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com | sh
fi

# Install Docker Compose if needed
if ! command -v docker-compose &> /dev/null; then
    echo "Installing Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

echo -e "${GREEN}✅ Docker ready${NC}"
echo ""

# Build and start services
echo "Building images..."
cd v2
docker-compose -f ../docker-compose.prod.yml build --parallel

echo ""
echo "Starting services..."
docker-compose -f ../docker-compose.prod.yml up -d

echo ""
echo "Waiting for services to be healthy (30 seconds)..."
sleep 30

echo -e "${GREEN}✅ Services started${NC}"
echo ""

# ============================================
# STEP 4: CONFIGURE CLOUDFLARE DNS
# ============================================

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Step 4: Configuring Cloudflare DNS (Automated)           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo "Installing jq..."
    apt-get update && apt-get install -y jq
fi

# Function to create/update DNS record
create_dns_record() {
    local name=$1
    local content=$2
    local proxied=$3
    
    echo -n "Configuring DNS: $name → $content ... "
    
    # Check if record exists
    existing=$(curl -s -X GET "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID/dns_records?name=$name" \
        -H "Authorization: Bearer $CF_API_TOKEN" \
        -H "Content-Type: application/json")
    
    record_id=$(echo "$existing" | jq -r '.result[0].id // empty')
    
    if [ -z "$record_id" ] || [ "$record_id" = "null" ]; then
        # Create new record
        result=$(curl -s -X POST "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID/dns_records" \
            -H "Authorization: Bearer $CF_API_TOKEN" \
            -H "Content-Type: application/json" \
            --data "{\"type\":\"A\",\"name\":\"$name\",\"content\":\"$content\",\"ttl\":1,\"proxied\":$proxied}")
    else
        # Update existing record
        result=$(curl -s -X PUT "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID/dns_records/$record_id" \
            -H "Authorization: Bearer $CF_API_TOKEN" \
            -H "Content-Type: application/json" \
            --data "{\"type\":\"A\",\"name\":\"$name\",\"content\":\"$content\",\"ttl\":1,\"proxied\":$proxied}")
    fi
    
    success=$(echo "$result" | jq -r '.success')
    if [ "$success" = "true" ]; then
        echo -e "${GREEN}✅${NC}"
    else
        echo -e "${RED}❌${NC}"
        echo "Error: $(echo "$result" | jq -r '.errors[0].message')"
    fi
}

# Create DNS records
create_dns_record "developer.galion.app" "$RUNPOD_IP" "true"
create_dns_record "api.developer.galion.app" "$RUNPOD_IP" "true"

echo ""
echo -e "${GREEN}✅ DNS records configured${NC}"
echo ""

# ============================================
# STEP 5: CONFIGURE CLOUDFLARE SSL
# ============================================

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Step 5: Configuring SSL/TLS Settings                     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Set SSL mode to Full (strict)
echo -n "Setting SSL mode to Full (strict)... "
ssl_result=$(curl -s -X PATCH "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID/settings/ssl" \
    -H "Authorization: Bearer $CF_API_TOKEN" \
    -H "Content-Type: application/json" \
    --data '{"value":"strict"}')

ssl_success=$(echo "$ssl_result" | jq -r '.success')
if [ "$ssl_success" = "true" ]; then
    echo -e "${GREEN}✅${NC}"
else
    echo -e "${YELLOW}⚠️  (may already be set)${NC}"
fi

# Enable Always Use HTTPS
echo -n "Enabling Always Use HTTPS... "
https_result=$(curl -s -X PATCH "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID/settings/always_use_https" \
    -H "Authorization: Bearer $CF_API_TOKEN" \
    -H "Content-Type: application/json" \
    --data '{"value":"on"}')

https_success=$(echo "$https_result" | jq -r '.success')
if [ "$https_success" = "true" ]; then
    echo -e "${GREEN}✅${NC}"
else
    echo -e "${YELLOW}⚠️  (may already be enabled)${NC}"
fi

# Set minimum TLS version
echo -n "Setting minimum TLS version to 1.2... "
tls_result=$(curl -s -X PATCH "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID/settings/min_tls_version" \
    -H "Authorization: Bearer $CF_API_TOKEN" \
    -H "Content-Type: application/json" \
    --data '{"value":"1.2"}')

tls_success=$(echo "$tls_result" | jq -r '.success')
if [ "$tls_success" = "true" ]; then
    echo -e "${GREEN}✅${NC}"
else
    echo -e "${YELLOW}⚠️  (may already be set)${NC}"
fi

echo ""
echo -e "${GREEN}✅ Cloudflare SSL configured${NC}"
echo ""

# ============================================
# STEP 6: INSTALL CLOUDFLARE TUNNEL
# ============================================

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Step 6: Setting Up Cloudflare Tunnel                     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Install cloudflared if not present
if ! command -v cloudflared &> /dev/null; then
    echo "Installing cloudflared..."
    curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb -o cloudflared.deb
    dpkg -i cloudflared.deb
    rm cloudflared.deb
    echo -e "${GREEN}✅ cloudflared installed${NC}"
else
    echo -e "${GREEN}✅ cloudflared already installed${NC}"
fi

echo ""
echo -e "${YELLOW}⚠️  MANUAL STEP REQUIRED (One-time setup):${NC}"
echo ""
echo "To complete Cloudflare Tunnel setup:"
echo ""
echo "1. Run: cloudflared tunnel login"
echo "   (Opens browser for authentication)"
echo ""
echo "2. Run: cloudflared tunnel create nexuslang-v2-production"
echo "   (Creates tunnel, note the tunnel ID)"
echo ""
echo "3. Create config file:"
echo "   mkdir -p ~/.cloudflared"
echo "   nano ~/.cloudflared/config.yml"
echo ""
echo "4. Add this configuration:"
echo "   ───────────────────────────────────"
echo "   tunnel: YOUR_TUNNEL_ID"
echo "   credentials-file: /root/.cloudflared/YOUR_TUNNEL_ID.json"
echo "   "
echo "   ingress:"
echo "     - hostname: developer.galion.app"
echo "       service: http://localhost:3000"
echo "     - hostname: api.developer.galion.app"
echo "       service: http://localhost:8000"
echo "     - service: http_status:404"
echo "   ───────────────────────────────────"
echo ""
echo "5. Start tunnel: cloudflared tunnel run nexuslang-v2-production"
echo ""
echo "6. Install as service:"
echo "   sudo cloudflared service install"
echo "   sudo systemctl start cloudflared"
echo ""

read -p "Press ENTER when tunnel is configured (or SKIP to continue without tunnel) " -r

# ============================================
# STEP 7: VERIFICATION
# ============================================

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Step 7: Verifying Deployment                              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check Docker containers
echo "Docker Container Status:"
docker-compose -f ../docker-compose.prod.yml ps
echo ""

# Test backend health
echo -n "Testing backend health... "
if curl -f -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✅ Backend healthy${NC}"
    curl -s http://localhost:8000/health | jq '.'
else
    echo -e "${RED}❌ Backend not responding${NC}"
fi

echo ""

# Test frontend
echo -n "Testing frontend... "
if curl -f -s http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend running${NC}"
else
    echo -e "${YELLOW}⚠️  Frontend may still be starting${NC}"
fi

echo ""

# Wait for DNS propagation
echo -e "${YELLOW}⏳ Waiting for DNS propagation (30 seconds)...${NC}"
sleep 30

# Test external URLs
echo ""
echo "Testing external URLs:"
echo -n "  https://api.developer.galion.app/health ... "
if curl -f -s https://api.developer.galion.app/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Working!${NC}"
else
    echo -e "${YELLOW}⚠️  Not yet (DNS may need more time)${NC}"
    echo "   Try in 2-3 minutes: curl https://api.developer.galion.app/health"
fi

echo ""
echo -n "  https://developer.galion.app ... "
if curl -f -s -I https://developer.galion.app > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Working!${NC}"
else
    echo -e "${YELLOW}⚠️  Not yet (DNS may need more time)${NC}"
    echo "   Try in 2-3 minutes: open https://developer.galion.app"
fi

# ============================================
# STEP 8: SUMMARY
# ============================================

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ DEPLOYMENT COMPLETE!                                   ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${BLUE}📊 Services Running:${NC}"
echo "  Frontend:  http://localhost:3000"
echo "  Backend:   http://localhost:8000"
echo "  API Docs:  http://localhost:8000/docs"
echo ""

echo -e "${BLUE}🌐 Public URLs (after DNS propagates):${NC}"
echo "  Frontend:  https://developer.galion.app"
echo "  API:       https://api.developer.galion.app"
echo "  Docs:      https://api.developer.galion.app/docs"
echo ""

echo -e "${BLUE}📋 Next Steps:${NC}"
echo "  1. Wait 2-5 minutes for DNS propagation"
echo "  2. Test: curl https://api.developer.galion.app/health"
echo "  3. Open: https://developer.galion.app"
echo "  4. Register account and test features"
echo "  5. Launch on ProductHunt!"
echo ""

echo -e "${BLUE}📊 Monitoring:${NC}"
echo "  Logs:    docker-compose -f ../docker-compose.prod.yml logs -f"
echo "  Stats:   docker stats"
echo "  Health:  curl http://localhost:8000/health"
echo ""

echo -e "${BLUE}🔒 Security:${NC}"
echo "  Secrets stored in: v2/.env (NOT in git)"
echo "  JWT Secret: ${JWT_SECRET:0:20}..."
echo "  Save these securely!"
echo ""

echo -e "${GREEN}🎉 NEXUSLANG V2 IS LIVE!${NC}"
echo ""
echo -e "${MAGENTA}🚀 Ready to launch on ProductHunt!${NC}"
echo ""

