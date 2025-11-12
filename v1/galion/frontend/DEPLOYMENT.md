# GALION.APP Frontend - Deployment Guide

## Production Deployment Options

### Option 1: Vercel (Recommended for Next.js)

**Pros**: Automatic deployments, edge network, zero-config
**Cost**: Free for hobby, $20/mo for team

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel

# Deploy to production
vercel --prod
```

**Environment Variables in Vercel:**
1. Go to Project Settings → Environment Variables
2. Add all variables from `.env.local.example`
3. Update URLs to production backend URLs

### Option 2: Docker + Cloud Provider

**DigitalOcean / AWS / GCP**

```bash
# Build Docker image
docker build -t galion-frontend:latest .

# Tag for registry
docker tag galion-frontend:latest registry.digitalocean.com/yourusername/galion-frontend:latest

# Push to registry
docker push registry.digitalocean.com/yourusername/galion-frontend:latest

# Deploy to server
ssh user@your-server
docker pull registry.digitalocean.com/yourusername/galion-frontend:latest
docker run -d -p 3000:3000 --name galion-frontend \
  -e NEXT_PUBLIC_API_URL=https://api.galion.app \
  registry.digitalocean.com/yourusername/galion-frontend:latest
```

### Option 3: Static Export (CDN)

If you want to deploy to a CDN (Cloudflare Pages, Netlify, etc.):

**Update next.config.ts:**
```typescript
const nextConfig: NextConfig = {
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true,
  },
};
```

**Build and deploy:**
```bash
npm run build
# Upload .next folder to your CDN
```

## DNS Configuration

### Cloudflare DNS Setup

1. **A Records** (if using server):
```
Type: A
Name: app (or @)
Content: YOUR_SERVER_IP
Proxy status: Proxied
TTL: Auto
```

2. **CNAME Records** (if using Vercel):
```
Type: CNAME
Name: app
Content: cname.vercel-dns.com
TTL: Auto
```

### SSL/TLS Configuration

**Cloudflare Settings:**
- SSL/TLS mode: Full (strict)
- Always Use HTTPS: On
- Automatic HTTPS Rewrites: On
- Minimum TLS Version: TLS 1.2

## Environment Variables for Production

```env
# Production Backend URLs
NEXT_PUBLIC_API_URL=https://api.galion.app
NEXT_PUBLIC_AUTH_SERVICE_URL=https://auth.galion.app
NEXT_PUBLIC_USER_SERVICE_URL=https://users.galion.app
NEXT_PUBLIC_VOICE_SERVICE_URL=https://voice.galion.app
NEXT_PUBLIC_DOCUMENT_SERVICE_URL=https://docs.galion.app
NEXT_PUBLIC_PERMISSIONS_SERVICE_URL=https://permissions.galion.app
NEXT_PUBLIC_ANALYTICS_SERVICE_URL=https://analytics.galion.app

# AI APIs (optional)
NEXT_PUBLIC_OPENAI_API_KEY=sk-...
NEXT_PUBLIC_ANTHROPIC_API_KEY=sk-ant-...

# App Configuration
NEXT_PUBLIC_APP_NAME=GALION.APP
NEXT_PUBLIC_APP_URL=https://app.galion.app
```

## Health Checks & Monitoring

### Health Check Endpoint

The app responds on all routes. Check:
- `https://app.galion.app/` → Should redirect to `/login`
- `https://app.galion.app/dashboard` → Should show login if not authenticated

### Uptime Monitoring

**Free Options:**
- UptimeRobot: https://uptimerobot.com
- Cronitor: https://cronitor.io
- Pingdom: https://www.pingdom.com

**Setup:**
1. Monitor URL: `https://app.galion.app`
2. Check interval: 5 minutes
3. Alert on: 2 consecutive failures
4. Notification: Email, Slack, or SMS

### Error Tracking

**Sentry Integration** (optional):
```bash
npm install @sentry/nextjs

# Initialize
npx @sentry/wizard@latest -i nextjs
```

## Performance Optimization

### Before Deployment Checklist

- [ ] Minify and bundle code (automatic with Next.js)
- [ ] Optimize images (use Next.js Image component)
- [ ] Enable compression (automatic with Next.js)
- [ ] Set up CDN (Vercel Edge or Cloudflare)
- [ ] Configure caching headers
- [ ] Enable HTTP/2
- [ ] Test with Lighthouse (aim for 90+ score)

### Cloudflare Optimization

**Speed Settings:**
- Auto Minify: HTML, CSS, JavaScript (On)
- Brotli: On
- Early Hints: On
- HTTP/2: On
- HTTP/3 (with QUIC): On

**Caching:**
```
# Cloudflare Page Rules for app.galion.app/*
Cache Level: Standard
Browser Cache TTL: 4 hours
Edge Cache TTL: 2 hours
```

## Security Checklist

- [ ] SSL/TLS enabled (HTTPS only)
- [ ] Security headers configured
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] DDoS protection (Cloudflare)
- [ ] WAF rules active
- [ ] Regular security updates

### Security Headers

These are already included in middleware:
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block
- Strict-Transport-Security
- Content-Security-Policy
- Permissions-Policy

## Rollback Procedure

### Vercel
```bash
# View deployments
vercel ls

# Rollback to previous
vercel rollback
```

### Docker
```bash
# Stop current
docker stop galion-frontend

# Start previous version
docker start galion-frontend-backup
```

## Troubleshooting

### Issue: White screen / 500 error

**Check:**
1. Environment variables are set correctly
2. Backend services are running
3. CORS is configured properly
4. Check browser console for errors

### Issue: API calls failing

**Check:**
1. Backend URLs in environment variables
2. Backend services are accessible
3. CORS headers from backend
4. Network tab in browser DevTools

### Issue: Authentication not working

**Check:**
1. JWT tokens are being sent
2. Token expiration time
3. Backend auth service is running
4. Cookies are enabled

## Monitoring & Alerts

### What to Monitor

1. **Uptime**: 99.9% target
2. **Response Time**: < 200ms target
3. **Error Rate**: < 0.1% target
4. **CPU/Memory**: < 80% usage
5. **Disk Space**: > 20% free

### Alert Thresholds

- **Critical**: Service down > 2 minutes
- **Warning**: Response time > 1 second
- **Info**: Error rate > 1%

## Backup & Recovery

### Backup Strategy

- Code: Git repository (GitHub/GitLab)
- Environment Variables: Secure vault (1Password, LastPass)
- User Data: Backend database backups

### Recovery Time Objective (RTO)

- **Target**: < 15 minutes
- **Process**:
  1. Identify issue (5 min)
  2. Rollback deployment (5 min)
  3. Verify fix (5 min)

## Post-Deployment Checklist

- [ ] All pages load correctly
- [ ] Login/Registration works
- [ ] API calls succeed
- [ ] Voice features work
- [ ] Document upload works
- [ ] Analytics display correctly
- [ ] Mobile responsive
- [ ] SSL certificate valid
- [ ] Monitoring active
- [ ] Alerts configured
- [ ] Team notified

## Continuous Deployment

### GitHub Actions (Optional)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run build
      - uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: '--prod'
```

## Cost Estimation

### Vercel
- **Hobby**: $0/month (100GB bandwidth, 100GB-hrs compute)
- **Pro**: $20/month (1TB bandwidth, 1000GB-hrs compute)

### DigitalOcean
- **Basic Droplet**: $4-6/month (1-2 GB RAM)
- **App Platform**: $5/month (Basic)

### Cloudflare
- **Free Tier**: $0/month (Unlimited bandwidth, 100k requests/day)
- **Pro**: $20/month (Advanced DDoS, custom SSL)

### Recommended for Production
**Total: ~$20-40/month**
- Vercel Pro: $20/month
- Cloudflare Free: $0/month
- (Optional) Sentry: $26/month

## Support & Maintenance

### Weekly Tasks
- [ ] Check error logs
- [ ] Review performance metrics
- [ ] Update dependencies (npm update)

### Monthly Tasks
- [ ] Security audit
- [ ] Performance review
- [ ] User feedback review
- [ ] Backup verification

---

**Deployment Complete! 🚀**

Your GALION.APP frontend is now ready for production deployment.

