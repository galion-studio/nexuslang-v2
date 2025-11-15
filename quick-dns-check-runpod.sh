#!/bin/bash
# Quick DNS Check for RunPod - Verify Cloudflare Setup

echo "🔍 Quick DNS Check - RunPod Server"
echo "=================================="

# Check if domains resolve to this server or Cloudflare
echo "Checking domain resolution..."
echo ""

# Function to check domain
check_domain() {
    local domain=$1
    echo -n "$domain: "

    # Get IP address
    local ip=$(nslookup $domain 2>/dev/null | grep -A1 "Name:" | tail -1 | awk '{print $2}')

    if [ -z "$ip" ]; then
        echo "❌ DNS lookup failed"
        return 1
    fi

    # Check if it's Cloudflare IP range
    if echo "$ip" | grep -qE "^(104\.|172\.6[4-7]\.|172\.7[0-1]\.)"; then
        echo "✅ Cloudflare IP ($ip) - DNS working!"
    elif [ "$ip" = "213.173.105.83" ]; then
        echo "⚠️  Direct IP ($ip) - Cloudflare proxy not active"
    else
        echo "❓ Unknown IP ($ip) - Check DNS settings"
    fi
}

# Check main domains
check_domain "galion.studio"
check_domain "api.galion.studio"
check_domain "studio.galion.studio"
check_domain "app.galion.studio"
check_domain "dev.galion.studio"

echo ""
echo "Next steps:"
echo "1. If showing Cloudflare IPs: DNS is working! ✅"
echo "2. If showing direct IP: Enable proxy in Cloudflare ⚠️"
echo "3. If DNS fails: Wait for propagation or check records ❌"
