# Cloudflare Setup Guide for GALION
## DDoS Protection, CDN, and SSL Configuration

**Purpose:** Configure Cloudflare for maximum security and performance  
**Time Required:** 15 minutes

---

## Step 1: Add Domains to Cloudflare

1. Log in to Cloudflare dashboard: https://dash.cloudflare.com
2. Click "Add Site"
3. Enter: `galion.app`
4. Choose **Free Plan** (sufficient for most needs)
5. Click "Continue"

---

## Step 2: Configure DNS Records

Add the following DNS records:

```
Type    Name                    Content             Proxy Status    TTL
A       galion.app              54.37.161.67        Proxied         Auto
A       www.galion.app          54.37.161.67        Proxied         Auto
A       api.galion.app          54.37.161.67        Proxied         Auto
A       studio.galion.app       54.37.161.67        Proxied         Auto
A       api.studio.galion.app   54.37.161.67        Proxied         Auto
```

**Important:** Set "Proxy Status" to "Proxied" (orange cloud icon) for all records.

---

## Step 3: SSL/TLS Configuration

Navigate to: **SSL/TLS** tab

1. **SSL/TLS Encryption Mode:** Set to "Full (strict)"
   - Encrypts traffic between Cloudflare and your server
   - Validates SSL certificate on your server

2. **Always Use HTTPS:** Enable (toggle ON)
   - Automatically redirects HTTP to HTTPS

3. **Minimum TLS Version:** TLS 1.2
   - Disables older, insecure protocols

4. **TLS 1.3:** Enable
   - Faster and more secure

5. **Automatic HTTPS Rewrites:** Enable
   - Fixes mixed content issues

---

## Step 4: Firewall Rules

Navigate to: **Security → WAF → Firewall Rules**

### Rule 1: Block Known Bad Bots
```
Field:      User Agent
Operator:   contains
Value:      curl|python|scrapy|bot
Action:     Challenge (CAPTCHA)
```

### Rule 2: Block Suspicious Countries (Optional)
```
Field:      Country
Operator:   is in
Value:      [Select countries with high attack traffic]
Action:     Challenge
```

### Rule 3: Protect API Endpoints
```
Field:      URI Path
Operator:   contains
Value:      /api/
AND
Field:      Request Rate
Operator:   greater than
Value:      100 requests per minute
Action:     Block
```

### Rule 4: Challenge High Request Rates
```
Field:      Request Rate
Operator:   greater than
Value:      300 requests per minute
Action:      Challenge
```

---

## Step 5: Bot Fight Mode

Navigate to: **Security → Bots**

1. **Bot Fight Mode:** Enable (Free)
   - Automatically blocks known bad bots
   - Reduces malicious traffic by 40-60%

2. **Super Bot Fight Mode:** (Pro plan, $20/month)
   - More advanced bot detection
   - Consider for production

---

## Step 6: Page Rules

Navigate to: **Rules → Page Rules**

### Rule 1: Cache Static Assets
```
URL:                *.galion.app/*.{js,css,png,jpg,jpeg,gif,ico,svg,woff,woff2}
Settings:
  - Cache Level:    Cache Everything
  - Edge Cache TTL: 1 month
  - Browser Cache TTL: 1 year
```

### Rule 2: Bypass Cache for API
```
URL:                api.galion.app/*
Settings:
  - Cache Level:    Bypass
```

### Rule 3: Bypass Cache for Studio API
```
URL:                api.studio.galion.app/*
Settings:
  - Cache Level:    Bypass
```

---

## Step 7: Speed Optimizations

Navigate to: **Speed → Optimization**

Enable the following:

1. **Auto Minify:**
   - ✅ JavaScript
   - ✅ CSS
   - ✅ HTML

2. **Brotli Compression:** Enable
   - Better compression than gzip

3. **Early Hints:** Enable
   - Speeds up page load by sending headers early

4. **HTTP/2 to Origin:** Enable
   - Faster connections to your server

5. **HTTP/3 (with QUIC):** Enable
   - Latest HTTP protocol, faster

6. **Rocket Loader:** Disable for now
   - Can break React/Next.js apps

---

## Step 8: Caching Configuration

Navigate to: **Caching → Configuration**

1. **Caching Level:** Standard

2. **Browser Cache TTL:** Respect Existing Headers

3. **Always Online:** Enable
   - Serves cached pages if your server is down

4. **Development Mode:** OFF (for production)

---

## Step 9: Network Settings

Navigate to: **Network**

1. **WebSockets:** Enable
   - Required for real-time features

2. **gRPC:** Enable (if using gRPC)

3. **Onion Routing:** Enable
   - Allows Tor users to access your site

4. **HTTP/2:** Enable

5. **HTTP/3 (with QUIC):** Enable

6. **0-RTT Connection Resumption:** Enable
   - Faster repeat connections

---

## Step 10: Security Level

Navigate to: **Security → Settings**

1. **Security Level:** Medium
   - Balance between security and user experience
   - Change to "High" if under attack

2. **Challenge Passage:** 30 minutes
   - How long users stay whitelisted after passing challenge

3. **Browser Integrity Check:** Enable
   - Blocks requests from modified browsers

---

## Step 11: Rate Limiting (Pro Feature)

If you upgrade to Pro ($20/month):

Navigate to: **Security → WAF → Rate Limiting Rules**

### Create Rate Limit: API Endpoints
```
Match:
  - Hostname: api.galion.app, api.studio.galion.app
  - URI Path: /api/*

Rate Limit:
  - Requests: 100 per 1 minute
  - Action: Block for 1 hour
```

---

## Step 12: Analytics & Monitoring

Navigate to: **Analytics & Logs**

1. **Web Analytics:** Enable
   - Free, privacy-friendly analytics
   - Alternative to Google Analytics

2. **Performance Insights:** Review
   - Identify slow pages and resources

---

## Verification Checklist

After configuration, verify:

- [ ] DNS records are proxied (orange cloud)
- [ ] SSL/TLS mode is "Full (strict)"
- [ ] Always Use HTTPS is enabled
- [ ] Bot Fight Mode is enabled
- [ ] Page Rules are active
- [ ] Static assets are cached
- [ ] WebSockets are enabled
- [ ] HTTP/3 is enabled

Test:
```bash
# Check SSL grade
curl -I https://galion.app

# Check if proxied through Cloudflare
dig galion.app
# Should show Cloudflare IPs

# Test WebSocket
wscat -c wss://api.galion.app/ws
```

---

## Emergency: Under Attack Mode

If experiencing DDoS attack:

1. Navigate to: **Overview**
2. Toggle **Under Attack Mode** to ON
3. All visitors will see interstitial challenge page
4. Turn OFF once attack subsides

---

## Cost Optimization

**Free Plan includes:**
- Unlimited bandwidth
- Basic DDoS protection
- Shared SSL certificate
- Basic page rules (3 rules)
- Basic analytics
- Bot Fight Mode

**Pro Plan ($20/month) adds:**
- Advanced DDoS protection
- Super Bot Fight Mode
- Advanced rate limiting
- More page rules (20 rules)
- Image optimization
- Mobile optimization

**Recommendation:** Start with Free, upgrade to Pro when revenue > $500/month

---

## Monitoring Cloudflare

Check these metrics weekly:

1. **Bandwidth:** Should see 50-80% cached
2. **Requests:** Check for suspicious patterns
3. **Threats:** Review blocked threats
4. **Performance:** Page load times

Navigate to: **Analytics → Traffic**

---

## Troubleshooting

### Issue: "Too many redirects" error
**Solution:** Set SSL/TLS mode to "Full (strict)"

### Issue: WebSockets not working
**Solution:** Ensure WebSockets are enabled in Network settings

### Issue: API responses cached incorrectly
**Solution:** Add Page Rule to bypass cache for API endpoints

### Issue: Origin IP exposed
**Solution:** Ensure all DNS records are "Proxied" (orange cloud)

---

**Setup complete! Your sites are now protected and accelerated by Cloudflare.**

