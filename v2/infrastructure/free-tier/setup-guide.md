# Free Tier Infrastructure Setup Guide
**Project Nexus - Alpha Budget Optimization**

**Goal:** Scale to 2000-5000 users on <$100/month budget using free tiers

---

## 🎯 Architecture Overview

```
Cloudflare (Free CDN/DDoS/WAF)
  ↓
Vercel (Free Frontend - 100GB bandwidth)
  ↓
Your VPS (Core Backend + PostgreSQL + Redis)
  ↓
Cloudflare R2 (Free 10GB object storage)
Backblaze B2 (Free 10GB backup)
Upstash Redis (Free 10K commands/day - fallback)
```

**Total Cost:** $50-66/month (VPS + domain + B2 backups)

---

## 1. Cloudflare (CDN, DNS, DDoS, WAF) - **FREE**

### Setup Steps:

1. **Create Cloudflare Account**
   - Sign up: https://dash.cloudflare.com/sign-up
   - Select Free plan

2. **Add Domains**
   ```bash
   # Add these domains:
   - galion.app
   - nexuslang.dev
   ```

3. **Update Nameservers**
   - Point your domain to Cloudflare nameservers
   - Wait for propagation (usually 5-30 minutes)

4. **Enable Security Features**
   - SSL/TLS: Full (strict)
   - Always Use HTTPS: ON
   - Auto Minify: JS, CSS, HTML
   - Brotli: ON
   - HTTP/3 (with QUIC): ON

5. **Configure WAF Rules (Free)**
   ```
   - Enable "OWASP Core Ruleset"
   - Enable "Cloudflare Managed Ruleset"
   - Add custom rule: Block bots (except good bots)
   - Rate limiting: 100 req/min per IP
   ```

6. **Setup Page Rules (3 free)**
   ```
   Rule 1: *.galion.app/*
     - Cache Level: Standard
     - Browser Cache TTL: 4 hours
   
   Rule 2: api.galion.app/*
     - Cache Level: Bypass
     - Security Level: High
   
   Rule 3: assets.galion.app/*
     - Cache Level: Cache Everything
     - Edge Cache TTL: 1 month
   ```

**API Token for automation:**
```bash
export CLOUDFLARE_API_TOKEN="your_token_here"
```

---

## 2. Cloudflare R2 (Object Storage) - **FREE 10GB**

### Setup Steps:

1. **Enable R2**
   - Dashboard → R2 → Enable R2
   - Free: 10GB storage, 10 million Class A operations, 100 million Class B operations

2. **Create Bucket**
   ```bash
   # Using wrangler CLI
   npm install -g wrangler
   wrangler r2 bucket create nexus-assets
   wrangler r2 bucket create nexus-uploads
   ```

3. **Get API Credentials**
   - Create R2 API token
   - Save Key ID and Secret Key

4. **Configure in Application**
   ```bash
   # .env
   R2_ACCOUNT_ID=your_account_id
   R2_ACCESS_KEY_ID=your_key_id
   R2_SECRET_ACCESS_KEY=your_secret_key
   R2_BUCKET_NAME=nexus-assets
   ```

**Python SDK Integration:**
```python
import boto3

s3 = boto3.client(
    's3',
    endpoint_url=f'https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com',
    aws_access_key_id=R2_ACCESS_KEY_ID,
    aws_secret_access_key=R2_SECRET_ACCESS_KEY
)
```

---

## 3. Backblaze B2 (Backup Storage) - **$6/TB/month**

### Setup Steps:

1. **Create Account**
   - Sign up: https://www.backblaze.com/b2/sign-up.html
   - Free: 10GB storage, 1GB/day download

2. **Create Bucket**
   - Bucket Name: `nexus-backups`
   - Files: Private

3. **Get Credentials**
   - Create App Key
   - Save Key ID and Application Key

4. **Install rclone**
   ```bash
   # Linux/Mac
   curl https://rclone.org/install.sh | sudo bash
   
   # Configure B2
   rclone config
   # Select: b2
   # Enter Key ID and Application Key
   ```

5. **Automated Backups**
   ```bash
   # Test upload
   rclone copy /var/backups/nexus b2:nexus-backups/
   
   # Add to cron (see v2/infrastructure/cron/backup.cron)
   ```

---

## 4. Vercel (Frontend Hosting) - **FREE**

### Setup Steps:

1. **Create Account**
   - Sign up with GitHub: https://vercel.com/signup
   - Free: 100GB bandwidth, unlimited deployments

2. **Deploy Frontend**
   ```bash
   cd v2/frontend
   npm install -g vercel
   vercel login
   vercel --prod
   ```

3. **Configure Environment**
   ```bash
   # Add environment variables in Vercel dashboard
   NEXT_PUBLIC_API_URL=https://api.galion.app
   NEXT_PUBLIC_WS_URL=wss://api.galion.app
   ```

4. **Custom Domain**
   - Add domain in Vercel dashboard
   - Update DNS (automatic with Cloudflare)

---

## 5. UptimeRobot (Monitoring) - **FREE**

### Setup Steps:

1. **Create Account**
   - Sign up: https://uptimerobot.com/signUp
   - Free: 50 monitors, 5-min intervals

2. **Add Monitors**
   ```
   Monitor 1: API Health
     - Type: HTTP(S)
     - URL: https://api.galion.app/health
     - Interval: 5 minutes
   
   Monitor 2: Frontend
     - Type: HTTP(S)
     - URL: https://galion.app
     - Interval: 5 minutes
   
   Monitor 3: Database
     - Type: Port
     - Host: your-vps-ip
     - Port: 5432
     - Interval: 5 minutes
   ```

3. **Alert Contacts**
   - Add email
   - Add Discord webhook (optional)
   - Add Slack webhook (optional)

4. **Public Status Page**
   - Enable public status page
   - Custom domain: status.galion.app

---

## 6. Sentry (Error Tracking) - **FREE**

### Setup Steps:

1. **Create Account**
   - Sign up: https://sentry.io/signup/
   - Free: 5K events/month, 1 user

2. **Create Project**
   - Project name: nexus-backend
   - Platform: Python/FastAPI

3. **Get DSN**
   ```bash
   export SENTRY_DSN="https://...@sentry.io/..."
   ```

4. **Integrate in Backend**
   ```python
   # v2/backend/main.py
   import sentry_sdk
   
   sentry_sdk.init(
       dsn=os.getenv("SENTRY_DSN"),
       traces_sample_rate=0.1,  # 10% of transactions
       profiles_sample_rate=0.1,
   )
   ```

---

## 7. Mailgun (Transactional Email) - **FREE**

### Setup Steps:

1. **Create Account**
   - Sign up: https://signup.mailgun.com/
   - Free: 5K emails/month (first 3 months)

2. **Verify Domain**
   - Add DNS records (SPF, DKIM)
   - Verify domain

3. **Get API Key**
   ```bash
   export MAILGUN_API_KEY="your_api_key"
   export MAILGUN_DOMAIN="mg.galion.app"
   ```

4. **Send Test Email**
   ```python
   import requests
   
   def send_email(to, subject, text):
       return requests.post(
           f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
           auth=("api", MAILGUN_API_KEY),
           data={
               "from": f"Nexus <noreply@{MAILGUN_DOMAIN}>",
               "to": [to],
               "subject": subject,
               "text": text
           }
       )
   ```

---

## 8. GitHub (Code + CI/CD) - **FREE**

### Setup Steps:

1. **Create Repository**
   - Private or public repository
   - Enable GitHub Actions (2000 minutes/month free)

2. **Setup CI/CD**
   ```yaml
   # .github/workflows/deploy.yml
   name: Deploy
   
   on:
     push:
       branches: [main]
   
   jobs:
     deploy:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         - name: Deploy to VPS
           run: |
             ssh user@vps 'cd /opt/project-nexus && git pull && docker-compose up -d'
   ```

---

## 9. Discord (Community) - **FREE**

### Setup Steps:

1. **Create Server**
   - Create community server
   - Channels: announcements, general, support, feedback

2. **Setup Webhook**
   ```bash
   export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."
   ```

3. **Automated Notifications**
   ```python
   import requests
   
   def send_discord_notification(message):
       requests.post(DISCORD_WEBHOOK_URL, json={"content": message})
   ```

---

## 📊 Resource Limits & Scaling Plan

| Service | Free Tier Limit | Alpha Usage (100 users) | Beta Usage (2000 users) | When to Upgrade |
|---------|----------------|------------------------|------------------------|-----------------|
| **Cloudflare** | Unlimited | <1% | <5% | Never (free forever) |
| **Cloudflare R2** | 10GB | 2GB | 8GB | When >10GB storage |
| **Backblaze B2** | 10GB free, then $6/TB | 15GB ($6/mo) | 50GB ($18/mo) | Immediate (for backups) |
| **Vercel** | 100GB bandwidth | 10GB | 80GB | When >100GB/month |
| **UptimeRobot** | 50 monitors | 5 monitors | 10 monitors | Never (within limits) |
| **Sentry** | 5K events/month | 500 events | 4K events | When >5K errors/month |
| **Mailgun** | 5K emails/month | 100 emails | 2K emails | When >5K emails/month |
| **GitHub** | 2000 min/month | 100 min | 500 min | Never (within limits) |

---

## 💰 Total Cost Breakdown

**Month 1-3 (Alpha - 100 users):**
- VPS: $50/month
- Domain: $10/month (one-time first year)
- Backblaze B2: $6/month (15GB backups)
- **Total: $66/month**

**Month 4-6 (Beta - 2000 users):**
- VPS: $100/month (upgraded)
- Backblaze B2: $18/month (50GB backups)
- Optional upgrades: $50/month (if limits exceeded)
- **Total: $168/month**

**Month 7+ (Production - 5000+ users):**
- VPS: $200/month (scaled)
- Backblaze B2: $30/month (100GB backups)
- Paid services: $100/month (email, monitoring, CDN overage)
- **Total: $330/month**

---

## 🚀 Quick Setup Script

```bash
#!/bin/bash
# Quick setup for all free tier services

echo "🚀 Setting up Project Nexus free tier services..."

# 1. Install tools
npm install -g wrangler vercel
curl https://rclone.org/install.sh | sudo bash

# 2. Configure Cloudflare
echo "Configure Cloudflare manually: https://dash.cloudflare.com"

# 3. Configure R2
wrangler r2 bucket create nexus-assets
wrangler r2 bucket create nexus-uploads

# 4. Configure rclone for B2
rclone config

# 5. Deploy frontend to Vercel
cd v2/frontend
vercel --prod

# 6. Setup monitoring
echo "Configure UptimeRobot: https://uptimerobot.com"
echo "Configure Sentry: https://sentry.io"

echo "✅ Setup complete! Check setup-guide.md for details."
```

---

## 📝 Checklist

- [ ] Cloudflare account created and domains added
- [ ] Cloudflare R2 buckets created
- [ ] Backblaze B2 account and bucket configured
- [ ] rclone configured for automated backups
- [ ] Vercel account and frontend deployed
- [ ] UptimeRobot monitors configured
- [ ] Sentry project created and integrated
- [ ] Mailgun domain verified
- [ ] GitHub Actions CI/CD configured
- [ ] Discord server and webhooks setup
- [ ] All credentials added to .env

---

**Built with frugality. Scaled with intelligence.** 💰

