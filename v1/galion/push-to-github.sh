#!/bin/bash
# ============================================================================
# NEXUS CORE - Push Documentation to GitHub
# ============================================================================
# This script helps you push ONLY documentation to GitHub (no code files)
# ============================================================================

echo ""
echo "====================================="
echo "  NEXUS CORE - GitHub Push Helper"
echo "====================================="
echo ""

# Check if Git is initialized
if [ ! -d ".git" ]; then
    echo "ERROR: Git not initialized!"
    echo "Run: git init"
    exit 1
fi

echo "Step 1: Git Configuration"
echo "-------------------------"
echo ""

# Check if Git is configured
GIT_NAME=$(git config --global user.name)
GIT_EMAIL=$(git config --global user.email)

if [ -z "$GIT_NAME" ] || [ -z "$GIT_EMAIL" ]; then
    echo "Git identity not configured!"
    echo ""
    read -p "Enter your name: " name
    read -p "Enter your email: " email
    
    git config --global user.name "$name"
    git config --global user.email "$email"
    
    echo "✓ Git configured!"
else
    echo "✓ Already configured:"
    echo "  Name: $GIT_NAME"
    echo "  Email: $GIT_EMAIL"
fi

echo ""
echo "Step 2: Create Commit"
echo "--------------------"
echo ""

# Check if there's already a commit
COMMIT_COUNT=$(git rev-list --all --count 2>/dev/null || echo "0")

if [ "$COMMIT_COUNT" = "0" ]; then
    echo "Creating initial commit..."
    git commit -m "docs: Initial commit - Nexus Core documentation and architecture

- Complete project documentation (25+ .md files)
- Implementation roadmap and guides  
- Architecture documentation
- Service documentation (Auth, User, API Gateway, Analytics)
- Docker and infrastructure configuration
- Testing guides and Postman collection
- Setup scripts

Note: Code files (.py, .go) are intentionally excluded.
This repository contains documentation only."
    
    if [ $? -eq 0 ]; then
        echo "✓ Commit created!"
    else
        echo "ERROR: Failed to create commit"
        exit 1
    fi
else
    echo "✓ Commit already exists"
fi

echo ""
echo "Step 3: GitHub Repository"
echo "------------------------"
echo ""
echo "Please create a GitHub repository:"
echo "  1. Go to: https://github.com/new"
echo "  2. Repository name: nexus-core (or your choice)"
echo "  3. Description: Nexus Core - AI Platform Documentation"
echo "  4. Public or Private: Your choice"
echo "  5. DO NOT initialize with README"
echo "  6. Click 'Create repository'"
echo ""

read -p "Have you created the repository? (y/n): " created

if [ "$created" != "y" ]; then
    echo ""
    echo "Please create the repository first, then run this script again."
    exit 0
fi

echo ""
read -p "Enter your GitHub username: " username
read -p "Enter repository name (default: nexus-core): " reponame

if [ -z "$reponame" ]; then
    reponame="nexus-core"
fi

echo ""
echo "Step 4: Push to GitHub"
echo "---------------------"
echo ""

# Check if remote already exists
REMOTE_URL=$(git remote get-url origin 2>/dev/null)

if [ ! -z "$REMOTE_URL" ]; then
    echo "Remote 'origin' already exists: $REMOTE_URL"
    read -p "Do you want to change it? (y/n): " change
    
    if [ "$change" = "y" ]; then
        git remote remove origin
        git remote add origin "https://github.com/$username/$reponame.git"
    fi
else
    git remote add origin "https://github.com/$username/$reponame.git"
    echo "✓ Remote added: https://github.com/$username/$reponame.git"
fi

echo ""
echo "Renaming branch to 'main'..."
git branch -M main

echo ""
echo "Pushing to GitHub..."
echo ""
echo "IMPORTANT: When prompted for password, use a Personal Access Token!"
echo "Create token at: https://github.com/settings/tokens"
echo "Required scope: repo (full control)"
echo ""

git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "====================================="
    echo "  SUCCESS!"
    echo "====================================="
    echo ""
    echo "✓ Your documentation is now on GitHub!"
    echo ""
    echo "View your repository at:"
    echo "  https://github.com/$username/$reponame"
    echo ""
    echo "Files pushed: 59 documentation files"
    echo "Code files excluded: ALL (.py, .go, etc.)"
    echo ""
else
    echo ""
    echo "ERROR: Push failed!"
    echo ""
    echo "Common issues:"
    echo "  1. Wrong Personal Access Token"
    echo "  2. Token doesn't have 'repo' scope"
    echo "  3. Repository doesn't exist"
    echo ""
    echo "Try again or push manually:"
    echo "  git push -u origin main"
fi

echo ""

