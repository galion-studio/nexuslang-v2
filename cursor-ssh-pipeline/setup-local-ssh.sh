#!/bin/bash
# ============================================
# Setup SSH Connection from Local Machine to RunPod
# ============================================
# This script configures your local machine for seamless SSH access

set -e

# Parse arguments
RUNPOD_IP="$1"
SSH_KEY_PATH="${2:-$HOME/.ssh/id_ed25519}"

if [ -z "$RUNPOD_IP" ]; then
    echo "Usage: $0 <RUNPOD_IP> [SSH_KEY_PATH]"
    echo "Example: $0 123.45.67.89"
    exit 1
fi

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  SSH PIPELINE SETUP FOR RUNPOD${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Step 1: Check SSH directory
echo -e "${BLUE}Step 1: Checking SSH directory...${NC}"
if [ ! -d "$HOME/.ssh" ]; then
    echo -e "${YELLOW}Creating .ssh directory...${NC}"
    mkdir -p "$HOME/.ssh"
    chmod 700 "$HOME/.ssh"
    echo -e "${GREEN}✓ Created $HOME/.ssh${NC}"
else
    echo -e "${GREEN}✓ SSH directory exists${NC}"
fi

# Step 2: Check SSH key
echo -e "${BLUE}Step 2: Checking SSH key...${NC}"
if [ ! -f "$SSH_KEY_PATH" ]; then
    echo -e "${YELLOW}SSH key not found at $SSH_KEY_PATH${NC}"
    echo -e "${BLUE}Generating new SSH key...${NC}"
    
    ssh-keygen -t ed25519 -f "$SSH_KEY_PATH" -N "" -C "galion-pipeline-$(hostname)"
    
    if [ -f "$SSH_KEY_PATH" ]; then
        echo -e "${GREEN}✓ SSH key generated successfully${NC}"
    else
        echo -e "${RED}✗ Failed to generate SSH key${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ SSH key found at $SSH_KEY_PATH${NC}"
fi

# Step 3: Create SSH config
echo -e "${BLUE}Step 3: Configuring SSH...${NC}"
SSH_CONFIG="$HOME/.ssh/config"

# Backup existing config if it contains runpod
if [ -f "$SSH_CONFIG" ] && grep -q "Host runpod" "$SSH_CONFIG"; then
    echo -e "${YELLOW}RunPod config already exists, backing up...${NC}"
    cp "$SSH_CONFIG" "$SSH_CONFIG.backup.$(date +%Y%m%d-%H%M%S)"
    echo -e "${GREEN}✓ Backup created${NC}"
fi

# Add configuration
cat >> "$SSH_CONFIG" << EOF

# ============================================
# RunPod Configuration - Added by Galion Pipeline
# ============================================

Host runpod
    HostName $RUNPOD_IP
    User root
    Port 22
    IdentityFile $SSH_KEY_PATH
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
    ServerAliveInterval 60
    ServerAliveCountMax 3
    ForwardAgent yes

Host runpod-tunnel
    HostName $RUNPOD_IP
    User root
    Port 22
    IdentityFile $SSH_KEY_PATH
    LocalForward 8000 localhost:8000
    LocalForward 3001 localhost:3001
    LocalForward 3002 localhost:3002
    LocalForward 3003 localhost:3003
    LocalForward 80 localhost:80
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
    ServerAliveInterval 60
    ServerAliveCountMax 3

EOF

chmod 600 "$SSH_CONFIG"
echo -e "${GREEN}✓ SSH config updated${NC}"

# Step 4: Get public key
echo -e "${BLUE}Step 4: Preparing public key...${NC}"
PUBLIC_KEY_PATH="$SSH_KEY_PATH.pub"
if [ -f "$PUBLIC_KEY_PATH" ]; then
    PUBLIC_KEY=$(cat "$PUBLIC_KEY_PATH")
    echo -e "${GREEN}✓ Public key ready${NC}"
    echo ""
    echo -e "${YELLOW}============================================${NC}"
    echo -e "${YELLOW}  PUBLIC KEY (copy this):${NC}"
    echo -e "${YELLOW}============================================${NC}"
    echo "$PUBLIC_KEY"
    echo -e "${YELLOW}============================================${NC}"
else
    echo -e "${RED}✗ Public key not found${NC}"
    exit 1
fi

# Step 5: Instructions for RunPod
echo ""
echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  NEXT STEPS:${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""
echo -e "1. Copy the public key above"
echo ""
echo -e "2. In your RunPod terminal, run:"
echo ""
echo -e "${GREEN}   mkdir -p ~/.ssh && echo '$PUBLIC_KEY' >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys${NC}"
echo ""
echo -e "3. Test connection from this machine:"
echo ""
echo -e "${GREEN}   ssh runpod${NC}"
echo ""
echo -e "4. Start tunnel for all services:"
echo ""
echo -e "${GREEN}   ssh runpod-tunnel -N${NC}"
echo ""
echo -e "${BLUE}============================================${NC}"
echo ""

# Save connection info
cat > "$(dirname "$0")/connection-info.json" << EOF
{
  "runpod_ip": "$RUNPOD_IP",
  "ssh_key_path": "$SSH_KEY_PATH",
  "public_key": "$PUBLIC_KEY",
  "configured_at": "$(date -Iseconds)"
}
EOF

echo -e "${GREEN}✓ Connection info saved to connection-info.json${NC}"
echo ""
echo -e "${GREEN}✓ SSH pipeline setup complete!${NC}"
echo ""

