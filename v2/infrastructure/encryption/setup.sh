#!/bin/bash
# Encryption Setup Script for Project Nexus
# Generates encryption keys and sets up secure environment

set -e  # Exit on error

echo "🔐 Project Nexus - Encryption Setup"
echo "===================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to generate a secure random key
generate_key() {
    local length=$1
    openssl rand -hex "$length"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "1. Checking prerequisites..."

if ! command_exists openssl; then
    echo -e "${RED}❌ OpenSSL not found. Please install OpenSSL.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ OpenSSL found${NC}"
echo ""

# Check if .env file exists
ENV_FILE="../../.env"
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from template...${NC}"
    if [ -f "../../env.template" ]; then
        cp "../../env.template" "$ENV_FILE"
        echo -e "${GREEN}✅ Created .env from template${NC}"
    else
        echo -e "${RED}❌ env.template not found${NC}"
        exit 1
    fi
fi

echo ""
echo "2. Generating encryption keys..."
echo ""

# Generate encryption master key (64 bytes = 128 hex chars)
ENCRYPTION_MASTER_KEY=$(generate_key 64)
echo -e "${GREEN}✅ Generated ENCRYPTION_MASTER_KEY (128 chars)${NC}"

# Generate JWT secret (64 bytes = 128 hex chars)
JWT_SECRET_KEY=$(generate_key 64)
echo -e "${GREEN}✅ Generated JWT_SECRET_KEY (128 chars)${NC}"

# Generate database password (32 bytes = 64 hex chars)
POSTGRES_PASSWORD=$(generate_key 32)
echo -e "${GREEN}✅ Generated POSTGRES_PASSWORD (64 chars)${NC}"

# Generate Redis password (32 bytes = 64 hex chars)
REDIS_PASSWORD=$(generate_key 32)
echo -e "${GREEN}✅ Generated REDIS_PASSWORD (64 chars)${NC}"

# Generate session secret
SESSION_SECRET=$(generate_key 32)
echo -e "${GREEN}✅ Generated SESSION_SECRET (64 chars)${NC}"

echo ""
echo "3. Updating .env file..."
echo ""

# Backup existing .env
if [ -f "$ENV_FILE" ]; then
    cp "$ENV_FILE" "${ENV_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
    echo -e "${GREEN}✅ Backed up existing .env${NC}"
fi

# Update or add secrets to .env
update_env_var() {
    local key=$1
    local value=$2
    local file=$3
    
    if grep -q "^${key}=" "$file"; then
        # Key exists, update it
        sed -i.bak "s|^${key}=.*|${key}=${value}|" "$file"
        rm -f "${file}.bak"
    else
        # Key doesn't exist, append it
        echo "${key}=${value}" >> "$file"
    fi
}

update_env_var "ENCRYPTION_MASTER_KEY" "$ENCRYPTION_MASTER_KEY" "$ENV_FILE"
update_env_var "JWT_SECRET_KEY" "$JWT_SECRET_KEY" "$ENV_FILE"
update_env_var "POSTGRES_PASSWORD" "$POSTGRES_PASSWORD" "$ENV_FILE"
update_env_var "REDIS_PASSWORD" "$REDIS_PASSWORD" "$ENV_FILE"
update_env_var "SESSION_SECRET" "$SESSION_SECRET" "$ENV_FILE"
update_env_var "ENCRYPTION_KEY_VERSION" "v1" "$ENV_FILE"

echo -e "${GREEN}✅ Updated .env file with new secrets${NC}"
echo ""

# Create secrets backup (encrypted)
echo "4. Creating encrypted secrets backup..."
BACKUP_FILE="secrets.$(date +%Y%m%d_%H%M%S).txt"
cat > "$BACKUP_FILE" << EOF
Project Nexus - Secrets Backup
Generated: $(date)
================================

ENCRYPTION_MASTER_KEY=$ENCRYPTION_MASTER_KEY
JWT_SECRET_KEY=$JWT_SECRET_KEY
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
REDIS_PASSWORD=$REDIS_PASSWORD
SESSION_SECRET=$SESSION_SECRET

⚠️  KEEP THIS FILE SECURE!
Store in a password manager or encrypted location.
DO NOT commit to version control.
EOF

echo -e "${GREEN}✅ Created backup: $BACKUP_FILE${NC}"
echo ""

# Display summary
echo "===================================="
echo -e "${GREEN}✅ Encryption Setup Complete!${NC}"
echo "===================================="
echo ""
echo "Generated secrets:"
echo "  - ENCRYPTION_MASTER_KEY (128 chars)"
echo "  - JWT_SECRET_KEY (128 chars)"
echo "  - POSTGRES_PASSWORD (64 chars)"
echo "  - REDIS_PASSWORD (64 chars)"
echo "  - SESSION_SECRET (64 chars)"
echo ""
echo "Files updated:"
echo "  - $ENV_FILE (with new secrets)"
echo "  - $BACKUP_FILE (backup copy)"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT SECURITY NOTES:${NC}"
echo "  1. Keep $BACKUP_FILE in a secure location"
echo "  2. Add it to your password manager"
echo "  3. DO NOT commit secrets to Git"
echo "  4. Rotate keys every 90 days"
echo "  5. Use different keys for dev/staging/production"
echo ""
echo -e "${GREEN}Next steps:${NC}"
echo "  1. Store backup file securely"
echo "  2. Delete backup file from disk: rm $BACKUP_FILE"
echo "  3. Test encryption: cd ../../v2/backend && python -m core.encryption"
echo "  4. Start services: docker-compose up -d"
echo ""

