# 🔑 API KEYS CHECKLIST - Project Nexus

## ✅ COMPLETED
- [x] PostgreSQL Password - Generated
- [x] Redis Password - Generated
- [x] JWT Secret Keys - Generated
- [x] Grafana Admin Password - Generated (`pSaje9dx6vCyZzt4`)

---

## 🎯 PRIORITY 1: Required to Start (Get These First)

### OpenAI API
**Status:** ⚠️ REQUIRED  
**Purpose:** Core AI features, GPT models, Whisper speech-to-text  
**Get it from:** https://platform.openai.com/api-keys  
**Cost:** Pay-as-you-go (~$0.002/1K tokens for GPT-4)  
**How to get:**
1. Sign up at https://platform.openai.com/
2. Go to API Keys section
3. Create new secret key
4. Copy the key (starts with `sk-proj-...`)
5. Add to `.env` file: `OPENAI_API_KEY=sk-proj-your-key-here`

---

## 🎙️ PRIORITY 2: Voice Features (Optional but Recommended)

### ElevenLabs API
**Status:** Optional  
**Purpose:** Text-to-speech (voice generation)  
**Get it from:** https://elevenlabs.io/speech-synthesis  
**Cost:** FREE tier - 10,000 characters/month  
**How to get:**
1. Sign up at https://elevenlabs.io/
2. Go to Profile → API Keys
3. Copy your API key
4. Add to `.env` file: `ELEVENLABS_API_KEY=your-key-here`

### OpenRouter API
**Status:** Optional  
**Purpose:** Enhanced AI routing and model fallbacks  
**Get it from:** https://openrouter.ai/keys  
**Cost:** Pay per model used  
**How to get:**
1. Sign up at https://openrouter.ai/
2. Go to Keys section
3. Create new API key
4. Add to `.env` file: `OPENROUTER_API_KEY=sk-or-your-key-here`

---

## 🛒 PRIORITY 3: E-Commerce (Optional - Only if using marketplace)

### Shopify Integration
**Status:** Optional  
**Purpose:** Marketplace and billing features  
**Get it from:** https://partners.shopify.com/  
**How to get:**
1. Create Shopify Partner account
2. Create a new app
3. Get API credentials
4. Add to `.env` file:
   ```
   SHOPIFY_API_KEY=your-api-key
   SHOPIFY_API_SECRET=your-api-secret
   SHOPIFY_ACCESS_TOKEN=your-access-token
   SHOPIFY_STORE_URL=your-store.myshopify.com
   ```

---

## 📱 PRIORITY 4: Social Media (Optional - For content management)

### Twitter/X API
**Get from:** https://developer.twitter.com/  
**Keys needed:**
- `TWITTER_API_KEY`
- `TWITTER_API_SECRET`
- `TWITTER_ACCESS_TOKEN`
- `TWITTER_ACCESS_SECRET`
- `TWITTER_BEARER_TOKEN`

### Reddit API
**Get from:** https://www.reddit.com/prefs/apps  
**Keys needed:**
- `REDDIT_CLIENT_ID`
- `REDDIT_CLIENT_SECRET`
- `REDDIT_USERNAME`
- `REDDIT_PASSWORD`

### LinkedIn API
**Get from:** https://www.linkedin.com/developers/  
**Keys needed:**
- `LINKEDIN_CLIENT_ID`
- `LINKEDIN_CLIENT_SECRET`
- `LINKEDIN_ACCESS_TOKEN`

### Facebook/Instagram API
**Get from:** https://developers.facebook.com/  
**Keys needed:**
- `FACEBOOK_APP_ID`
- `FACEBOOK_APP_SECRET`
- `FACEBOOK_ACCESS_TOKEN`

### TikTok API
**Get from:** https://developers.tiktok.com/  
**Keys needed:**
- `TIKTOK_CLIENT_KEY`
- `TIKTOK_CLIENT_SECRET`

### YouTube API
**Get from:** https://console.cloud.google.com/  
**Keys needed:**
- `YOUTUBE_API_KEY`
- `YOUTUBE_CLIENT_ID`
- `YOUTUBE_CLIENT_SECRET`

### Product Hunt API
**Get from:** https://api.producthunt.com/v2/docs  
**Keys needed:**
- `PRODUCTHUNT_API_KEY`

### Dev.to API
**Get from:** https://dev.to/settings/extensions  
**Keys needed:**
- `DEV_TO_API_KEY`

---

## ☁️ PRIORITY 5: Cloud Services (Optional - For production)

### Cloudflare
**Get from:** https://dash.cloudflare.com/  
**Purpose:** CDN, DNS, R2 storage  
**Keys needed:**
- `CLOUDFLARE_ZONE_ID`
- `CLOUDFLARE_ACCOUNT_ID`
- `CLOUDFLARE_API_KEY`
- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_EMAIL`

### Cloudflare R2 Storage
**Purpose:** Object storage (S3-compatible)  
**Keys needed:**
- `CLOUDFLARE_R2_ACCOUNT_ID`
- `CLOUDFLARE_R2_ACCESS_KEY_ID`
- `CLOUDFLARE_R2_SECRET_ACCESS_KEY`

---

## 📧 PRIORITY 6: Email Service (Optional - For notifications)

### SMTP Email
**Purpose:** Password resets, notifications  
**For Gmail users:**
1. Go to Google Account settings
2. Enable 2-Factor Authentication
3. Generate "App Password"
4. Add to `.env` file:
   ```
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   ```

---

## 📊 PRIORITY 7: Monitoring (Optional - For production)

### Sentry
**Get from:** https://sentry.io/  
**Purpose:** Error tracking and monitoring  
**Keys needed:**
- `SENTRY_DSN`

---

## 🚀 QUICK START (Minimum Viable Setup)

To get started immediately, you only need:

1. ✅ **Core Infrastructure** (Already done!)
   - PostgreSQL, Redis, JWT keys are generated

2. 🔑 **OpenAI API Key** (Required for AI features)
   - Get from: https://platform.openai.com/api-keys
   - Add to `.env` file

3. 🚀 **Start Services**
   ```powershell
   docker-compose up -d
   ```

4. 🌐 **Access Platform**
   - Frontend: http://localhost:3000
   - Backend: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Grafana: http://localhost:3001

---

## 📝 Notes

- All other API keys are **optional** and can be added later as needed
- The platform will work with just the core infrastructure + OpenAI key
- Social media keys are only needed if you use the content management features
- Email service is only needed for password resets and notifications
- Cloud services are only needed for production deployment

---

## 🔒 Security Reminders

- ❌ NEVER commit `.env` file to version control
- ✅ Keep API keys secure and backed up
- ✅ Use different keys for development and production
- ✅ Regularly rotate sensitive credentials
- ✅ Monitor API usage and costs

---

## 💰 Cost Estimates (Monthly)

**Minimum Setup (Development):**
- OpenAI: ~$5-20/month (light usage)
- Total: **~$5-20/month**

**With Voice Features:**
- OpenAI: ~$5-20/month
- ElevenLabs: FREE (10K chars/month)
- Total: **~$5-20/month**

**Full Production Setup:**
- OpenAI: ~$50-200/month
- Cloudflare R2: ~$5-10/month
- Email: FREE (Gmail) or ~$10/month (SendGrid)
- Monitoring: FREE (Sentry free tier)
- Total: **~$55-220/month**

---

**Last Updated:** November 11, 2025  
**Generated by:** Project Nexus Setup Script

