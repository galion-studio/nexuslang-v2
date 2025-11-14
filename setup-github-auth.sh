#!/bin/bash
# Setup GitHub authentication using environment variables

# Load environment variables from runpod.env
if [ -f "runpod.env" ]; then
    export $(grep -v '^#' runpod.env | xargs)
fi

# Configure git with credentials
if [ ! -z "$GITHUB_USERNAME" ] && [ ! -z "$GITHUB_TOKEN" ]; then
    echo "Setting up GitHub authentication..."
    git config --global user.name "$GITHUB_USERNAME"
    git config --global user.email "info@gmail.studio"

    # Set remote to use token authentication
    git remote set-url origin "https://$GITHUB_USERNAME:$GITHUB_TOKEN@github.com/galion-studio/nexuslang-v2.git"

    echo "✅ GitHub authentication configured"
    echo "Username: $GITHUB_USERNAME"
    echo "Remote URL updated with token"
else
    echo "❌ GITHUB_USERNAME or GITHUB_TOKEN not found in runpod.env"
    exit 1
fi
