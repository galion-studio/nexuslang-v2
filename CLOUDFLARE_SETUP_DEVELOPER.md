# Cloudflare Setup for developer.galion.app

**Configure NexusLang v2 Platform with Cloudflare**

---

## Prerequisites

- Cloudflare account
- galion.app domain in Cloudflare
- Server with Docker installed

---

## Step 1: DNS Configuration

### Add DNS Records in Cloudflare

1. Log into Cloudflare dashboard
2. Select `galion.app` domain
3. Go to DNS settings
4. Add these records:

```
Type    Name                  Content                     Proxy Status
----    ----                  -------                     ------------
A       developer.galion.app  YOUR_SERVER_IP              Proxied (🟠)
A       api.developer         YOUR_SERVER_IP              Proxied (🟠)
```

**Important:** Enable "Proxied" (orange cloud) for both records

---

## Step 2: SSL Configuration

### Option A: Cloudflare Origin Certificate (Recommended)

1. Go to SSL/TLS → Origin Server
2. Click "Create Certificate"
3. Select both hostnames:
   - `developer.galion.app`
   - `api.developer.galion.app`
4. Choose 15 years validity
5. Click "Create"
6. Save the certificate and private key

7. On your server:

```bash
# Create directory
sudo mkdir -p /etc/cloudflare/certs

# Save certificate
sudo nano /etc/cloudflare/certs/developer.galion.app.pem
# Paste the certificate

# Save private key
sudo nano /etc/cloudflare/certs/developer.galion.app.key
# Paste the private key

# Set permissions
sudo chmod 600 /etc/cloudflare/certs/developer.galion.app.key
```

### Option B: Let's Encrypt

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot --nginx -d developer.galion.app -d api.developer.galion.app
```

---

## Step 3: Cloudflare Configuration

### SSL/TLS Settings

1. **SSL/TLS Encryption Mode:** Full (strict)
2. **Always Use HTTPS:** On
3. **Minimum TLS Version:** TLS 1.2
4. **Automatic HTTPS Rewrites:** On

### Speed Settings

1. **Auto Minify:** Enable for HTML, CSS, JS
2. **Brotli:** On
3. **Rocket Loader:** On (for faster JS)

### Firewall Settings

1. **Security Level:** Medium
2. **Bot Fight Mode:** On
3. **Challenge Passage:** 30 minutes

### Page Rules (Optional)

Create page rules for caching:

```
URL: developer.galion.app/_next/static/*
Settings:
  - Cache Level: Cache Everything
  - Edge Cache TTL: 1 month
```

---

## Step 4: Deploy Application

```bash
# Run deployment script
chmod +x deploy-to-developer-galion.sh
./deploy-to-developer-galion.sh

# Or use PowerShell on Windows
powershell -ExecutionPolicy Bypass -File deploy-to-developer-galion.ps1
```

---

## Step 5: Update Environment

Edit `.env` and add:

```env
# Production URLs
NEXT_PUBLIC_API_URL=https://api.developer.galion.app
NEXT_PUBLIC_WS_URL=wss://api.developer.galion.app
CORS_ORIGINS=https://developer.galion.app,https://api.developer.galion.app

# Cloudflare
CLOUDFLARE_ZONE_ID=your_zone_id
CLOUDFLARE_API_TOKEN=your_api_token
```

Restart services:

```bash
docker-compose restart
```

---

## Step 6: Verify Deployment

### Test URLs

```bash
# Test frontend
curl -I https://developer.galion.app

# Test backend
curl https://api.developer.galion.app/health

# Test API docs
# Visit: https://api.developer.galion.app/docs
```

### Check SSL

```bash
# SSL Labs test
# Visit: https://www.ssllabs.com/ssltest/analyze.html?d=developer.galion.app
```

---

## Step 7: Enable Cloudflare Features

### Page Rules (Create these)

1. **Cache Everything for Static Files**
   ```
   URL: developer.galion.app/_next/static/*
   Cache Level: Cache Everything
   ```

2. **Bypass Cache for API**
   ```
   URL: api.developer.galion.app/*
   Cache Level: Bypass
   ```

### Firewall Rules

1. **Rate Limiting**
   ```
   If: (http.host eq "api.developer.galion.app" and http.request.uri.path contains "/api/v2/nexuslang/run")
   Then: Rate limit to 60 requests per minute
   ```

2. **Block Bad Bots**
   ```
   If: (cf.client.bot)
   Then: Challenge (CAPTCHA)
   ```

---

## Monitoring

### Cloudflare Analytics

- Visit Cloudflare dashboard
- Check Analytics for traffic
- Monitor threats blocked
- Review cache performance

### Application Monitoring

```bash
# Check Prometheus
# Visit: http://YOUR_SERVER_IP:9090

# Check Grafana
# Visit: http://YOUR_SERVER_IP:3001
```

---

## Troubleshooting

### SSL Not Working

```bash
# Check certificate
openssl s_client -connect developer.galion.app:443 -servername developer.galion.app

# Restart nginx
sudo systemctl restart nginx
```

### DNS Not Resolving

```bash
# Check DNS
nslookup developer.galion.app

# Wait for DNS propagation (can take 1-24 hours)
```

### Services Not Accessible

```bash
# Check if services are running
docker-compose ps

# Check nginx
sudo nginx -t
sudo systemctl status nginx

# Check logs
docker-compose logs -f
```

---

## Performance Optimization

### Cloudflare

1. Enable Argo Smart Routing (paid)
2. Enable Image Optimization
3. Configure Cache Rules
4. Enable Workers (for edge computing)

### Application

1. Enable Redis caching
2. Optimize database queries
3. Use CDN for static assets
4. Enable Gzip compression

---

## Security Checklist

- [x] HTTPS enabled
- [x] Origin certificates configured
- [x] Security headers added
- [x] Firewall rules active
- [x] Rate limiting enabled
- [x] Bot protection on
- [x] DDoS protection (automatic with Cloudflare)

---

## Cost

### Cloudflare

- **Free Plan:** $0/month
  - Includes: SSL, CDN, DDoS protection, analytics
  - Sufficient for launch

- **Pro Plan:** $20/month (optional)
  - Includes: Advanced analytics, more page rules, image optimization

### Infrastructure

- **VPS:** $50-100/month (Hetzner, DigitalOcean)
- **API Costs:** $50-500/month (OpenAI, etc.)
- **Shopify:** 2.9% + 30¢ per transaction

**Total:** ~$100-600/month depending on traffic

---

## Launch Checklist

- [ ] DNS configured in Cloudflare
- [ ] SSL certificate installed
- [ ] .env configured with production values
- [ ] Services deployed and running
- [ ] Nginx configured
- [ ] Firewall rules active
- [ ] Monitoring enabled
- [ ] Test all features
- [ ] Announce launch! 🚀

---

## Support

**For issues:**
- Check TROUBLESHOOTING section in docs
- Review docker-compose logs
- Check Cloudflare Analytics
- See 🎯_MASTER_LAUNCH_DOCUMENT.md

---

**Your platform is ready for developer.galion.app!** 🚀

**Just configure DNS and deploy!**

