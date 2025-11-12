#!/bin/bash
# ╔════════════════════════════════════════════════════════════╗
# ║  NexusLang v2 - Production Environment Setup              ║
# ║  Generates secure secrets and configures for deployment   ║
# ╚════════════════════════════════════════════════════════════╝

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  NexusLang v2 - Production Environment Generator          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if running from project root
if [ ! -d "v2" ]; then
    echo "❌ ERROR: Run this from project root (project-nexus/)"
    exit 1
fi

echo "✅ Generating secure secrets..."
echo ""

# Generate secure secrets
JWT_SECRET=$(openssl rand -hex 64)
SECRET_KEY=$(openssl rand -hex 32)
POSTGRES_PASSWORD=$(openssl rand -hex 16)
REDIS_PASSWORD=$(openssl rand -hex 16)
GRAFANA_PASSWORD=$(openssl rand -hex 16)

echo "✅ Secrets generated"
echo ""

# Get OpenAI API key
echo "Enter your OpenAI API key (starts with sk-proj-):"
read -r OPENAI_API_KEY

if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  No OpenAI key provided - AI features will be limited"
    OPENAI_API_KEY="sk-proj-YOUR_KEY_HERE"
fi

echo ""
echo "✅ Creating v2/.env file..."

# Create .env file
cat > v2/.env << EOF
# ╔════════════════════════════════════════════════════════════╗
# ║  NexusLang v2 - Production Environment                    ║
# ║  Generated: $(date)                                        ║
# ╚════════════════════════════════════════════════════════════╝

# CRITICAL: Security Keys (AUTO-GENERATED)
JWT_SECRET=$JWT_SECRET
SECRET_KEY=$SECRET_KEY

# Environment
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=info

# Domains (developer.galion.app)
PRIMARY_DOMAIN=developer.galion.app
FRONTEND_URL=https://developer.galion.app
BACKEND_URL=https://api.developer.galion.app
CORS_ORIGINS=https://developer.galion.app,https://api.developer.galion.app

# Database (AUTO-GENERATED PASSWORDS)
POSTGRES_USER=nexus
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
POSTGRES_DB=nexus_v2
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
DATABASE_URL=postgresql+asyncpg://nexus:$POSTGRES_PASSWORD@postgres:5432/nexus_v2

# Redis (AUTO-GENERATED PASSWORD)
REDIS_PASSWORD=$REDIS_PASSWORD
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_URL=redis://:$REDIS_PASSWORD@redis:6379/0

# AI Services
OPENAI_API_KEY=$OPENAI_API_KEY
OPENROUTER_API_KEY=
DEFAULT_AI_MODEL=anthropic/claude-3.5-sonnet
FALLBACK_AI_MODEL=openai/gpt-4-turbo

# Voice (GPU on RunPod)
WHISPER_MODEL=base
WHISPER_DEVICE=cuda
TTS_MODEL=tts_models/en/ljspeech/tacotron2-DDC
TTS_DEVICE=cuda

# Monitoring
GF_SECURITY_ADMIN_PASSWORD=$GRAFANA_PASSWORD
SENTRY_DSN=
SENTRY_ENVIRONMENT=production

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_AUTH_REQUESTS=10
RATE_LIMIT_CODE_EXEC=30

# Features
ENABLE_VOICE=true
ENABLE_GROKOPEDIA=true
ENABLE_CONTENT_MANAGER=true
ENABLE_COMMUNITY=true
ENABLE_BILLING=false

# Shopify (optional - set these if using billing)
SHOPIFY_STORE_URL=
SHOPIFY_API_KEY=
SHOPIFY_API_SECRET=
SHOPIFY_ACCESS_TOKEN=

# Credits
FREE_TIER_CREDITS=100
PRO_TIER_CREDITS=10000
ENTERPRISE_TIER_CREDITS=999999
EOF

echo "✅ Created v2/.env"
echo ""

# Create frontend .env.local
echo "✅ Creating v2/frontend/.env.local..."

cat > v2/frontend/.env.local << EOF
# NexusLang v2 Frontend - Production Configuration
# Generated: $(date)

# API Configuration
NEXT_PUBLIC_API_URL=https://api.developer.galion.app
NEXT_PUBLIC_WS_URL=wss://api.developer.galion.app

# Environment
NEXT_PUBLIC_ENVIRONMENT=production
NEXT_TELEMETRY_DISABLED=1

# Features
NEXT_PUBLIC_ENABLE_VOICE=true
NEXT_PUBLIC_ENABLE_AI_CHAT=true
NEXT_PUBLIC_ENABLE_GROKOPEDIA=true
NEXT_PUBLIC_ENABLE_CONTENT_MANAGER=true
EOF

echo "✅ Created v2/frontend/.env.local"
echo ""

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  ✅ ENVIRONMENT CONFIGURED                                 ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Files created:"
echo "  - v2/.env (backend configuration)"
echo "  - v2/frontend/.env.local (frontend configuration)"
echo ""
echo "Secrets generated (SAVE THESE SECURELY):"
echo "  JWT_SECRET: $JWT_SECRET"
echo "  POSTGRES_PASSWORD: $POSTGRES_PASSWORD"
echo "  REDIS_PASSWORD: $REDIS_PASSWORD"
echo "  GRAFANA_PASSWORD: $GRAFANA_PASSWORD"
echo ""
echo "⚠️  SECURITY: These files contain sensitive data!"
echo "   - Never commit to git"
echo "   - Store passwords in secure vault"
echo "   - Rotate secrets every 90 days"
echo ""
echo "🚀 Next Steps:"
echo "   1. Review v2/.env file"
echo "   2. Add remaining API keys (Shopify, etc.) if needed"
echo "   3. Start services: cd v2 && docker-compose -f ../docker-compose.prod.yml up -d"
echo "   4. Check health: curl http://localhost:8000/health"
echo ""
echo "✅ Ready to deploy!"
echo ""

