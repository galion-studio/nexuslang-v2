#!/bin/bash

# Diagnose directory structure and fix issues

echo "🔍 DIAGNOSING PROJECT STRUCTURE"
echo "==============================="

pwd
echo ""

echo "Directory contents:"
ls -la
echo ""

echo "Checking for frontend directories:"
for dir in galion-app galion-studio developer-platform; do
    if [[ -d "$dir" ]]; then
        echo "✅ $dir exists"
        ls -la "$dir" | head -5
    else
        echo "❌ $dir missing"
    fi
done

echo ""
echo "Checking backend:"
if [[ -d "v2/backend" ]]; then
    echo "✅ v2/backend exists"
    ls -la v2/backend | head -5
else
    echo "❌ v2/backend missing"
fi

echo ""
echo "Checking node_modules and Next.js:"
for dir in galion-app galion-studio developer-platform; do
    if [[ -d "$dir" ]]; then
        echo "$dir node_modules: $([[ -d "$dir/node_modules" ]] && echo "✅ exists" || echo "❌ missing")"
        echo "$dir next binary: $([[ -f "$dir/node_modules/.bin/next" ]] && echo "✅ exists" || echo "❌ missing")"
    fi
done

echo ""
echo "Current PATH:"
echo "$PATH"

echo ""
echo "Node and npm versions:"
which node && node --version || echo "node not found"
which npm && npm --version || echo "npm not found"
