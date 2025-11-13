# 🔧 LocalTunnel IP Error - Quick Fix

**Error**: "endpoint IP is not correct"

This happens because LocalTunnel uses your public IP as a password, and it needs to be refreshed.

---

## ✅ Quick Fix (Recommended)

### Run the fix script:

```bash
bash fix_localtunnel.sh
```

This will:
1. Get your current public IP
2. Restart all LocalTunnel connections
3. Display your new password (public IP)

---

## 🔑 Manual Fix

### Step 1: Find Your Public IP

```bash
curl ifconfig.me
```

Copy the IP address shown.

### Step 2: Restart LocalTunnel

```bash
# Stop existing tunnels
pkill -f "lt --port"

# Wait a moment
sleep 3

# Start new tunnels
lt --port 8000 --subdomain nexuslang-studio &
lt --port 3000 --subdomain nexuslang-frontend &
lt --port 3001 --subdomain nexuslang-studio &
```

### Step 3: Use Your New IP as Password

When you visit the URLs, use the IP from Step 1 as the password.

---

## 🌐 Alternative: Use Cloudflare Tunnel (Permanent Solution)

LocalTunnel is great for testing but has IP limitations. For production, use Cloudflare Tunnel:

### Install Cloudflared:

```bash
# Download cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
chmod +x cloudflared-linux-amd64
sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared

# Login to Cloudflare
cloudflared tunnel login

# Create tunnel
cloudflared tunnel create galion

# Configure tunnel
cat > ~/.cloudflared/config.yml << EOF
tunnel: galion
credentials-file: /root/.cloudflared/<YOUR-TUNNEL-ID>.json

ingress:
  - hostname: studio.yourdomain.com
    service: http://localhost:3001
  - hostname: api.yourdomain.com
    service: http://localhost:8000
  - hostname: app.yourdomain.com
    service: http://localhost:3000
  - service: http_status:404
EOF

# Start tunnel
cloudflared tunnel run galion
```

**Benefits**:
- ✅ No IP password required
- ✅ Permanent URLs
- ✅ Better performance
- ✅ SSL included
- ✅ More reliable

---

## 🚀 Alternative: Use Ngrok

Another option is ngrok:

```bash
# Install ngrok
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar xvzf ngrok-v3-stable-linux-amd64.tgz
sudo mv ngrok /usr/local/bin/

# Add auth token (get from ngrok.com)
ngrok config add-authtoken YOUR_TOKEN

# Start tunnels
ngrok http 8000 &
ngrok http 3000 &
ngrok http 3001 &
```

---

## 📊 Check Current Status

```bash
# Check if services are running
curl http://localhost:8000/health
curl http://localhost:3000
curl http://localhost:3001

# Check LocalTunnel processes
ps aux | grep "lt --port"

# View LocalTunnel logs
cat /workspace/logs/lt-*.log
```

---

## 🔄 Why This Happens

LocalTunnel uses your public IP as a security feature:
- When the tunnel starts, it records your IP
- When someone visits, they must enter that IP as password
- If your IP changes (dynamic IP, VPN, etc.), it won't match
- Solution: Restart tunnels to update the IP

---

## 💡 Best Practices

### For Development (LocalTunnel):
- Restart tunnels when IP changes
- Keep the fix script handy
- Check logs if issues persist

### For Production:
- Use Cloudflare Tunnel (free, reliable)
- Or use ngrok with paid plan
- Or setup proper domain with nginx reverse proxy

---

## 🆘 Still Having Issues?

### Check if services are actually running:

```bash
galion-health
```

### Make sure ports are accessible:

```bash
curl http://localhost:8000/health
curl http://localhost:3000
curl http://localhost:3001
```

### Check firewall:

```bash
# If on RunPod, ports should be open by default
# If on VPS, you might need to open ports
sudo ufw allow 8000
sudo ufw allow 3000
sudo ufw allow 3001
```

---

## 📞 Quick Commands

```bash
# Fix LocalTunnel
bash fix_localtunnel.sh

# Get current public IP
curl ifconfig.me

# Restart all services
galion-restart

# Check health
galion-health

# View logs
galion-logs
```

---

🔧 **Run the fix script and you'll be back online!**

```bash
bash fix_localtunnel.sh
```

