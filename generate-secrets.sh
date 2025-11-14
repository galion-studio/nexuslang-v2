#!/bin/bash
# Generate secure secrets for .env file

echo "Generating secure secrets..."
echo ""

echo "# Generated Secrets - $(date)"
echo ""
echo "POSTGRES_PASSWORD=$(openssl rand -hex 16)"
echo "REDIS_PASSWORD=$(openssl rand -hex 16)"
echo "SECRET_KEY=$(openssl rand -hex 32)"
echo "JWT_SECRET=$(openssl rand -hex 64)"
echo ""
echo "Copy these to your .env file!"

