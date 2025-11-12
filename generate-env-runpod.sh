#!/bin/bash
# ╔════════════════════════════════════════════════════════════╗
# ║  Generate Final Production .env with Real Secrets          ║
# ║  Uses your OpenRouter key + generates other secrets       ║
# ╚════════════════════════════════════════════════════════════╝

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  🔐 Generating Production Environment                      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Your actual OpenRouter key
OPENROUTER_KEY="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"

# Generate secure secrets
echo "✅ Generating secure secrets..."
JWT_SECRET=$(openssl rand -hex 64)
SECRET_KEY=$(openssl rand -hex 32)
POSTGRES_PASSWORD=$(openssl rand -hex 16)
REDIS_PASSWORD=$(openssl rand -hex 16)
GRAFANA_PASSWORD=$(openssl rand -hex 16)

echo "✅ Secrets generated"
echo ""

# Create v2/.env
cat > v2/.env << EOF
# NexusLang v2 - Production Environment
# Generated: $(date)

# CRITICAL SECRETS (AUTO-GENERATED)
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
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
DATABASE_URL=postgresql+asyncpg://nexus:$POSTGRES_PASSWORD@postgres:5432/nexus_v2

# Redis
REDIS_PASSWORD=$REDIS_PASSWORD
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_URL=redis://:$REDIS_PASSWORD@redis:6379/0

# AI - OpenRouter Primary (Your actual key)
OPENROUTER_API_KEY=$OPENROUTER_KEY
AI_PROVIDER=openrouter
DEFAULT_AI_MODEL=anthropic/claude-3.5-sonnet
FALLBACK_AI_MODEL=openai/gpt-4-turbo
FAST_AI_MODEL=openai/gpt-3.5-turbo
CODE_AI_MODEL=meta-llama/codellama-70b-instruct

# OpenAI (Optional)
OPENAI_API_KEY=

# Shopify (Disabled)
ENABLE_BILLING=false

# Voice (GPU)
WHISPER_DEVICE=cuda
TTS_DEVICE=cuda

# Features
ENABLE_VOICE=true
ENABLE_GROKOPEDIA=true
ENABLE_CONTENT_MANAGER=true
ENABLE_COMMUNITY=true

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_AUTH_REQUESTS=10
RATE_LIMIT_CODE_EXEC=30

# Credits
FREE_TIER_CREDITS=100
PRO_TIER_CREDITS=10000
ENTERPRISE_TIER_CREDITS=999999

# Monitoring
GF_SECURITY_ADMIN_PASSWORD=$GRAFANA_PASSWORD
SENTRY_ENVIRONMENT=production
EOF

# Create frontend .env.local
cat > v2/frontend/.env.local << EOF
# Frontend Production Configuration
NEXT_PUBLIC_API_URL=https://api.developer.galion.app
NEXT_PUBLIC_WS_URL=wss://api.developer.galion.app
NEXT_PUBLIC_ENVIRONMENT=production
NEXT_TELEMETRY_DISABLED=1
NEXT_PUBLIC_ENABLE_VOICE=true
NEXT_PUBLIC_ENABLE_AI_CHAT=true
NEXT_PUBLIC_ENABLE_GROKOPEDIA=true
NEXT_PUBLIC_ENABLE_CONTENT_MANAGER=true
EOF

echo "✅ Created v2/.env"
echo "✅ Created v2/frontend/.env.local"
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  ✅ ENVIRONMENT READY FOR DEPLOYMENT                       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "🔐 Generated Secrets (SAVE THESE):"
echo "  JWT_SECRET: $JWT_SECRET"
echo "  POSTGRES_PASSWORD: $POSTGRES_PASSWORD"
echo "  REDIS_PASSWORD: $REDIS_PASSWORD"
echo ""
echo "🌐 OpenRouter: Configured with your key"
echo "🚀 Ready to deploy!"
echo ""
echo "Next: ./deploy-to-runpod-production.sh"
echo ""

