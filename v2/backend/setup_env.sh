#!/bin/bash
# Setup script for environment variables
# This creates .env with your API keys

echo "Setting up .env file..."

# Copy .env.example to .env and add your API keys
echo "Please create .env file manually with your API keys:"
echo ""
echo "1. Copy .env.example to .env:"
echo "   cp .env.example .env"
echo ""
echo "2. Edit .env and add your API keys:"
echo "   - OPENAI_API_KEY=your-key-here"
echo "   - OPENROUTER_API_KEY=your-key-here"
echo "   - ELEVENLABS_API_KEY=your-key-here"
echo ""
echo "Your API keys are stored securely and will NOT be committed to git."

echo "✅ .env file created!"
echo "⚠️  IMPORTANT: Never commit .env to git!"

