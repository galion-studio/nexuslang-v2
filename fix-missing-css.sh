#!/bin/bash
# ============================================
# Fix Missing CSS Files in Galion App
# ============================================

echo "🎨 FIXING MISSING CSS FILES"
echo "============================================"
echo ""

cd /nexuslang-v2 || exit 1

# Create shared styles directory
echo "Step 1: Creating shared styles directory..."
mkdir -p shared/styles
echo "✓ Directory created"
echo ""

# Create design-tokens.css
echo "Step 2: Creating design-tokens.css..."
cat > shared/styles/design-tokens.css << 'EOF'
/* Design Tokens for Galion Platform */

:root {
  /* Colors */
  --color-primary: #2563eb;
  --color-secondary: #7c3aed;
  --color-success: #10b981;
  --color-warning: #f59e0b;
  --color-error: #ef4444;
  --color-background: #ffffff;
  --color-foreground: #1f2937;
  --color-muted: #f3f4f6;
  --color-muted-foreground: #6b7280;
  --color-border: #e5e7eb;
  
  /* Spacing */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;
  
  /* Border Radius */
  --radius-sm: 0.25rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
  --radius-xl: 1rem;
  
  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
}

.dark {
  --color-background: #111827;
  --color-foreground: #f3f4f6;
  --color-muted: #1f2937;
  --color-muted-foreground: #9ca3af;
  --color-border: #374151;
}
EOF

echo "✓ design-tokens.css created"
echo ""

# Restart galion-app
echo "Step 3: Restarting galion-app..."
pm2 restart galion-app
echo ""

# Wait and test
echo "Step 4: Testing (waiting 10 seconds)..."
sleep 10

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)

echo ""
echo "============================================"
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ SUCCESS! Galion App is working!"
    echo "   HTTP Status: $HTTP_CODE"
    echo ""
    echo "🌐 Access at: http://213.173.105.83:3000"
else
    echo "Status: HTTP $HTTP_CODE"
    if [ "$HTTP_CODE" = "500" ]; then
        echo ""
        echo "Remaining errors:"
        pm2 logs galion-app --lines 10 --nostream --err
    fi
fi
echo "============================================"
echo ""

pm2 status

