# 🌐 DOMAIN & LINK MANAGEMENT

## Overview

Galion operates across three interconnected platforms:
- **galion.app** - Voice-first main application
- **api.galion.app** - API gateway and WebSocket endpoint
- **developer.galion.app** - IDE and development platform

---

## 📋 Domain Configuration

### DNS Records Required

Add these DNS records to your domain registrar:

#### For galion.app (Main App)
```
Type: A
Name: @
Value: YOUR_SERVER_IP

Type: CNAME
Name: www
Value: galion.app

Type: CNAME
Name: api
Value: galion.app

Type: CNAME
Name: developer
Value: galion.app
```

#### SSL Certificate Setup

Using Let's Encrypt (automatic):
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificates for all domains
sudo certbot --nginx \
  -d galion.app \
  -d www.galion.app \
  -d api.galion.app \
  -d developer.galion.app \
  --email admin@galion.app
```

---

## 🔗 Link Structure

### Main Application (galion.app)
- **Frontend**: `https://galion.app`
- **API Proxy**: `https://galion.app/api/*` → `http://localhost:8000`
- **WebSocket**: `https://galion.app/ws/*` → `ws://localhost:8000`

### API Gateway (api.galion.app)
- **REST API**: `https://api.galion.app/*` → `http://localhost:8000`
- **WebSocket**: `https://api.galion.app/ws/*` → `ws://localhost:8000`
- **Health**: `https://api.galion.app/health`
- **Docs**: `https://api.galion.app/docs`

### Developer Platform (developer.galion.app)
- **IDE**: `https://developer.galion.app`
- **API**: `https://developer.galion.app/api/*` → `http://localhost:8000`

---

## 🚀 Deployment Options

### Option 1: Nginx (Recommended for Production)

```bash
# Setup nginx
sudo ./scripts/setup-nginx.sh

# Setup SSL
sudo ./scripts/setup-ssl.sh

# Deploy application
sudo ./scripts/deploy-production.sh
```

### Option 2: Docker Compose

```bash
# Start all services
docker-compose -f docker-compose.prod.yml up -d

# Setup SSL certificates
docker-compose -f docker-compose.prod.yml run --rm certbot
```

### Option 3: Caddy (Simplest SSL)

```bash
# Install Caddy
sudo apt install caddy

# Copy configuration
sudo cp Caddyfile /etc/caddy/Caddyfile

# Restart Caddy
sudo systemctl restart caddy
```

---

## 🔒 Security Configuration

### Firewall Rules (UFW)
```bash
# Allow SSH
sudo ufw allow ssh

# Allow HTTP/HTTPS
sudo ufw allow 'Nginx Full'

# Enable firewall
sudo ufw --force enable
```

### SSL/TLS Settings
- **Protocol**: TLS 1.2/1.3 only
- **Ciphers**: Secure ECDHE suites
- **HSTS**: Enabled with preload
- **Certificate**: Let's Encrypt auto-renewal

---

## 📊 Monitoring & Health Checks

### Health Endpoints
- `https://galion.app/health` - Frontend health
- `https://api.galion.app/health` - Backend health
- `https://api.galion.app/docs` - API documentation

### Log Files
- **Nginx**: `/var/log/nginx/`
- **Backend**: `/var/log/galion/backend.log`
- **Frontend**: `/var/log/galion/frontend.log`

---

## 🔄 Load Balancing (Future)

For high-traffic deployment:

```nginx
upstream galion_backend {
    server backend1:8000 weight=5;
    server backend2:8000 weight=5;
    server backend3:8000 weight=5;
}

upstream galion_frontend {
    server frontend1:3003;
    server frontend2:3003;
}
```

---

## 🧪 Testing Your Setup

### Domain Resolution
```bash
# Test DNS
nslookup galion.app
nslookup api.galion.app
nslookup developer.galion.app
```

### SSL Certificates
```bash
# Check SSL
openssl s_client -connect galion.app:443 -servername galion.app < /dev/null
```

### HTTP Response
```bash
# Test HTTPS
curl -I https://galion.app
curl -I https://api.galion.app/health
curl -I https://developer.galion.app
```

---

## 📞 Support

If you encounter issues:

1. **Check logs**: `sudo tail -f /var/log/nginx/error.log`
2. **Test services**: `sudo systemctl status nginx`
3. **DNS propagation**: May take 24-48 hours
4. **SSL issues**: Run `sudo certbot certificates`

---

## 🎯 Next Steps

1. ✅ Configure DNS records
2. ✅ Setup SSL certificates
3. ✅ Deploy with nginx/Caddy
4. ✅ Test all endpoints
5. 🔄 Setup monitoring
6. 🚀 Go live!

**Your voice-first platform will be accessible at:**  
**https://galion.app** 🎉

