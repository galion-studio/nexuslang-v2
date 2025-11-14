#!/bin/bash
# Setup SSH key authentication on RunPod

echo "🔑 Setting up SSH Key Authentication"
echo "===================================="

# Create .ssh directory if it doesn't exist
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Add the public key to authorized_keys
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAILEaRXnBtexd4Epq1RPLDXj7gmB6yuOp33XiFMNFJlgN polskitygrys111@gmail.com" >> ~/.ssh/authorized_keys

# Set proper permissions
chmod 600 ~/.ssh/authorized_keys

echo "✅ SSH key added to authorized_keys"
echo ""
echo "🧪 Test the SSH connection (run from your local machine):"
echo "ssh root@213.173.105.83"
echo ""
echo "🚀 Then create the tunnel:"
echo "ssh -L 8080:localhost:36277 root@213.173.105.83 -N"
echo ""
echo "📱 Access your API at: http://localhost:8080"
