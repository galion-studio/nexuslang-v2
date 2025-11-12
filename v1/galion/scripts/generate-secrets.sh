#!/bin/bash
# Generate secure secrets for GALION.APP & GALION.STUDIO
# Usage: ./scripts/generate-secrets.sh

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║      GALION Secrets Generator                          ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Generate secure random strings
generate_password() {
    openssl rand -base64 32 | tr -d "=+/" | cut -c1-32
}

generate_jwt_secret() {
    openssl rand -base64 64 | tr -d "\n"
}

# Generate secrets
POSTGRES_PASSWORD=$(generate_password)
REDIS_PASSWORD=$(generate_password)
JWT_SECRET=$(generate_jwt_secret)

# Create .env file
ENV_FILE=".env"

if [ -f "$ENV_FILE" ]; then
    echo -e "${YELLOW}Warning: .env file already exists!${NC}"
    read -p "Overwrite? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled. Secrets not updated."
        exit 0
    fi
    # Backup existing .env
    cp "$ENV_FILE" "${ENV_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
    echo -e "${GREEN}✓ Backup created${NC}"
fi

# Write .env file
cat > "$ENV_FILE" <<EOF
# ╔════════════════════════════════════════════════════════╗
# ║  GALION Environment Configuration                      ║
# ║  Generated: $(date)                        ║
# ╚════════════════════════════════════════════════════════╝

# ==================== DATABASE ====================
POSTGRES_USER=galion
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
POSTGRES_DB=galion

# Database URLs
DATABASE_URL=postgresql://galion:${POSTGRES_PASSWORD}@postgres:5432/galion
DATABASE_URL_STUDIO=postgresql://galion:${POSTGRES_PASSWORD}@postgres:5432/galion_studio

# ==================== REDIS ====================
REDIS_PASSWORD=${REDIS_PASSWORD}
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0

# ==================== AUTHENTICATION ====================
JWT_SECRET=${JWT_SECRET}
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=15

# ==================== APIs ====================
# Get these from: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-your-openai-key-here

# Get this from: https://elevenlabs.io/app/settings/api-keys
ELEVENLABS_API_KEY=your-elevenlabs-key-here

# ==================== APPLICATION ====================
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Frontend URLs
VITE_API_URL=https://api.galion.app
VITE_WS_URL=wss://api.galion.app
NEXT_PUBLIC_API_URL=https://api.studio.galion.app
NEXT_PUBLIC_WS_URL=wss://api.studio.galion.app

# Backend URLs (internal)
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

# ==================== STORAGE ====================
UPLOAD_DIR=/app/uploads
MAX_UPLOAD_SIZE=100M

# S3 (optional - for production scaling)
# AWS_ACCESS_KEY_ID=your-key-here
# AWS_SECRET_ACCESS_KEY=your-secret-here
# S3_BUCKET_NAME=galion-uploads
# S3_REGION=us-east-1

# ==================== EMAIL ====================
# SMTP settings (optional)
# SMTP_HOST=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USER=your-email@gmail.com
# SMTP_PASSWORD=your-app-password
# SMTP_FROM=noreply@galion.app

# ==================== MONITORING ====================
# Grafana Cloud (optional)
# GRAFANA_CLOUD_API_KEY=your-key-here
# GRAFANA_CLOUD_URL=https://prometheus-prod-XX.grafana.net

# Sentry (optional - error tracking)
# SENTRY_DSN=https://your-sentry-dsn-here

# ==================== SECURITY ====================
# CORS settings
CORS_ORIGINS=https://galion.app,https://studio.galion.app
CORS_ALLOW_CREDENTIALS=true

# Rate limiting
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_BURST=20

# Session
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=lax

# ==================== BACKUPS ====================
BACKUP_DIR=/home/deploy/galion/backups
BACKUP_RETENTION_DAYS=30

# Backblaze B2 (optional - for remote backups)
# B2_APPLICATION_KEY_ID=your-key-id
# B2_APPLICATION_KEY=your-key
# B2_BUCKET_NAME=galion-backups

# ==================== FEATURE FLAGS ====================
ENABLE_VOICE=true
ENABLE_ANALYTICS=true
ENABLE_REGISTRATION=true
ENABLE_SOCIAL_LOGIN=false

# ==================== DEVELOPMENT ====================
# Only for local development
# POSTGRES_HOST=localhost
# POSTGRES_PORT=5432
# REDIS_HOST=localhost
# REDIS_PORT=6379
EOF

# Set permissions
chmod 600 "$ENV_FILE"

echo -e "${GREEN}✓ .env file created successfully!${NC}"
echo ""
echo -e "${YELLOW}Generated secrets:${NC}"
echo "  ✓ PostgreSQL password"
echo "  ✓ Redis password"
echo "  ✓ JWT secret"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT:${NC}"
echo "  1. Edit .env and add your API keys:"
echo "     - OPENAI_API_KEY"
echo "     - ELEVENLABS_API_KEY"
echo ""
echo "  2. Keep this file secure:"
echo "     chmod 600 .env"
echo ""
echo "  3. NEVER commit .env to git!"
echo "     (Already in .gitignore)"
echo ""
echo -e "${GREEN}Next step: nano .env${NC}"
echo ""

# Create .env.example (template without secrets)
cat > .env.example <<EOF
# ╔════════════════════════════════════════════════════════╗
# ║  GALION Environment Configuration Template             ║
# ║  Copy this to .env and fill in your values             ║
# ╚════════════════════════════════════════════════════════╝

# Database
POSTGRES_USER=galion
POSTGRES_PASSWORD=generate-with-scripts/generate-secrets.sh
POSTGRES_DB=galion
DATABASE_URL=postgresql://galion:PASSWORD@postgres:5432/galion

# Redis
REDIS_PASSWORD=generate-with-scripts/generate-secrets.sh
REDIS_URL=redis://:PASSWORD@redis:6379/0

# Authentication
JWT_SECRET=generate-with-scripts/generate-secrets.sh

# APIs
OPENAI_API_KEY=sk-your-key-here
ELEVENLABS_API_KEY=your-key-here

# Environment
ENVIRONMENT=production
DEBUG=false

# Frontend URLs
VITE_API_URL=https://api.galion.app
NEXT_PUBLIC_API_URL=https://api.studio.galion.app
EOF

echo -e "${GREEN}✓ .env.example template also created${NC}"

exit 0

