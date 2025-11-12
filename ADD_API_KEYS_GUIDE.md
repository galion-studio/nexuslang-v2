# 🔑 STEP-BY-STEP API KEYS GUIDE

**Your `.env` file is now open in Notepad!**

Follow this guide to add your API keys in order of priority.

---

## ✅ STEP 1: OpenAI API Key (REQUIRED - Do This First!)

### Why You Need It:
- Core AI features (NexusLang intelligence)
- GPT models for code generation
- Whisper for speech-to-text

### How to Get It:
1. **Go to:** https://platform.openai.com/api-keys
2. **Sign up or log in** to your OpenAI account
3. **Click:** "Create new secret key"
4. **Name it:** "Project Nexus Development"
5. **Copy the key** (starts with `sk-proj-...`)

### Where to Add It:
In your `.env` file (already open), find:
```
OPENAI_API_KEY=
```
Change to:
```
OPENAI_API_KEY=sk-proj-YOUR-KEY-HERE
```

**💰 Cost:** ~$5-20/month for development

---

## 🎙️ STEP 2: ElevenLabs API Key (Optional - Voice Features)

### Why You Need It:
- Text-to-speech (voice generation)
- High-quality voice output

### How to Get It:
1. **Go to:** https://elevenlabs.io/
2. **Sign up** (free tier available)
3. **Go to:** Profile → API Keys
4. **Copy your API key**

### Where to Add It:
```
ELEVENLABS_API_KEY=YOUR-KEY-HERE
```

**💰 Cost:** FREE (10,000 characters/month)

---

## 🤖 STEP 3: OpenRouter API Key (Optional - Enhanced AI)

### Why You Need It:
- Access to multiple AI models
- Fallback routing
- Cost optimization

### How to Get It:
1. **Go to:** https://openrouter.ai/
2. **Sign up** with GitHub or email
3. **Go to:** Keys section
4. **Create new key**
5. **Copy the key** (starts with `sk-or-...`)

### Where to Add It:
```
OPENROUTER_API_KEY=sk-or-YOUR-KEY-HERE
```

**💰 Cost:** Pay per model used

---

## 📱 STEP 4: Social Media Keys (Optional - Content Management)

**Only add these if you plan to use social media features!**

### Twitter/X API
**Get from:** https://developer.twitter.com/

1. Create a Twitter Developer account
2. Create a new Project and App
3. Generate API keys

```
TWITTER_API_KEY=your-key
TWITTER_API_SECRET=your-secret
TWITTER_ACCESS_TOKEN=your-token
TWITTER_ACCESS_SECRET=your-access-secret
TWITTER_BEARER_TOKEN=your-bearer-token
```

### Reddit API
**Get from:** https://www.reddit.com/prefs/apps

1. Click "create app"
2. Choose "script" type
3. Get client ID and secret

```
REDDIT_CLIENT_ID=your-client-id
REDDIT_CLIENT_SECRET=your-client-secret
REDDIT_USERNAME=your-reddit-username
REDDIT_PASSWORD=your-reddit-password
```

### LinkedIn API
**Get from:** https://www.linkedin.com/developers/

```
LINKEDIN_CLIENT_ID=your-client-id
LINKEDIN_CLIENT_SECRET=your-client-secret
LINKEDIN_ACCESS_TOKEN=your-token
```

### Facebook/Instagram API
**Get from:** https://developers.facebook.com/

```
FACEBOOK_APP_ID=your-app-id
FACEBOOK_APP_SECRET=your-app-secret
FACEBOOK_ACCESS_TOKEN=your-token
```

### YouTube API
**Get from:** https://console.cloud.google.com/

1. Create a new Google Cloud project
2. Enable YouTube Data API v3
3. Create credentials

```
YOUTUBE_API_KEY=your-api-key
YOUTUBE_CLIENT_ID=your-client-id
YOUTUBE_CLIENT_SECRET=your-client-secret
```

### TikTok API
**Get from:** https://developers.tiktok.com/

```
TIKTOK_CLIENT_KEY=your-client-key
TIKTOK_CLIENT_SECRET=your-client-secret
```

### Product Hunt API
**Get from:** https://api.producthunt.com/v2/docs

```
PRODUCTHUNT_API_KEY=your-api-key
```

### Dev.to API
**Get from:** https://dev.to/settings/extensions

```
DEV_TO_API_KEY=your-api-key
```

---

## 🛒 STEP 5: Shopify (Optional - E-Commerce)

**Only if you're building marketplace features!**

**Get from:** https://partners.shopify.com/

1. Create a Shopify Partner account
2. Create a new app
3. Get API credentials

```
SHOPIFY_API_KEY=your-api-key
SHOPIFY_API_SECRET=your-api-secret
SHOPIFY_ACCESS_TOKEN=your-access-token
SHOPIFY_WEBHOOK_SECRET=your-webhook-secret
SHOPIFY_STORE_URL=yourstore.myshopify.com
```

---

## ☁️ STEP 6: Cloudflare (Optional - Production Deployment)

**Get from:** https://dash.cloudflare.com/

1. Log in to Cloudflare dashboard
2. Select your domain
3. Get Zone ID from Overview page
4. Create API token in My Profile → API Tokens

```
CLOUDFLARE_ZONE_ID=your-zone-id
CLOUDFLARE_ACCOUNT_ID=your-account-id
CLOUDFLARE_API_KEY=your-api-key
CLOUDFLARE_API_TOKEN=your-api-token
CLOUDFLARE_EMAIL=your-email@example.com
```

### Cloudflare R2 Storage
In Cloudflare dashboard:
1. Go to R2 Object Storage
2. Create a bucket
3. Generate API tokens

```
CLOUDFLARE_R2_ACCOUNT_ID=your-r2-account-id
CLOUDFLARE_R2_ACCESS_KEY_ID=your-access-key
CLOUDFLARE_R2_SECRET_ACCESS_KEY=your-secret-key
CLOUDFLARE_R2_BUCKET_NAME=nexus-content
```

---

## 📧 STEP 7: Email SMTP (Optional - Notifications)

### For Gmail Users:
1. Go to Google Account settings
2. Enable 2-Factor Authentication
3. Go to Security → App Passwords
4. Generate password for "Mail"

```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=noreply@nexuslang.dev
```

### For SendGrid:
**Get from:** https://sendgrid.com/

```
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your-sendgrid-api-key
SMTP_FROM=noreply@yourdomain.com
```

---

## 📊 STEP 8: Sentry (Optional - Error Monitoring)

**Get from:** https://sentry.io/

1. Create Sentry account
2. Create new project
3. Copy the DSN

```
SENTRY_DSN=https://your-dsn@sentry.io/project-id
SENTRY_ENVIRONMENT=development
```

---

## ✅ CHECKLIST

Use this to track what you've added:

- [ ] **REQUIRED:** OpenAI API Key
- [ ] **Optional:** ElevenLabs API Key (voice)
- [ ] **Optional:** OpenRouter API Key
- [ ] **Optional:** Twitter/X API
- [ ] **Optional:** Reddit API
- [ ] **Optional:** LinkedIn API
- [ ] **Optional:** Facebook/Instagram API
- [ ] **Optional:** YouTube API
- [ ] **Optional:** TikTok API
- [ ] **Optional:** Product Hunt API
- [ ] **Optional:** Dev.to API
- [ ] **Optional:** Shopify API
- [ ] **Optional:** Cloudflare API
- [ ] **Optional:** Email SMTP
- [ ] **Optional:** Sentry DSN

---

## 🎯 MINIMUM TO START

**You only need:**
1. ✅ Core infrastructure (already done!)
2. 🔑 OpenAI API Key

**Everything else is optional!**

---

## 💾 WHEN YOU'RE DONE

1. **Save the `.env` file** in Notepad (Ctrl+S)
2. **Close Notepad**
3. **Return to terminal and run:**
   ```powershell
   docker-compose up -d
   ```

---

## 💰 COST SUMMARY

| Service | Tier | Monthly Cost |
|---------|------|--------------|
| OpenAI | Pay-as-you-go | $5-20 (dev) |
| ElevenLabs | Free | $0 (10K chars) |
| OpenRouter | Pay-as-you-go | Variable |
| Social Media APIs | Mostly Free | $0 |
| Cloudflare | Free tier | $0-5 |
| Email (Gmail) | Free | $0 |
| Sentry | Free tier | $0 |

**Total for basic dev:** **$5-20/month**

---

## 🔒 SECURITY TIPS

- ✅ Never commit `.env` to Git
- ✅ Use different keys for dev/production
- ✅ Rotate keys regularly
- ✅ Monitor API usage/costs
- ✅ Keep this file backed up securely

---

**Need help? Each API provider has documentation linked above!**

