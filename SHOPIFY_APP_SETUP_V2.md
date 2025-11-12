# 🛒 Shopify App Setup Guide - pay.galion.studio v2

## Overview

This guide helps you configure the `pay.galion.studio` Shopify app for your NexusLang v2 payment processing system.

---

## ✅ Current Configuration (From Shopify Dashboard)

- **App Name**: pay.galion.studio
- **Store**: pay-galion-studio.myshopify.com
- **Contact Email**: finance@galion.studio
- **Location**: Poland
- **Currency**: Polish Zloty (PLN zł)

---

## 🔧 Required App URLs

### 1. App URL (Main Entry Point)
```
https://pay.galion.studio
```
This is where your Shopify app frontend lives.

### 2. Preferences URL (Optional)
```
https://docs.galion.studio/pay/shopify-payment-processor
```
Documentation page for merchants using your app.

### 3. Redirect URLs (OAuth)
Add these to your app settings:
```
https://pay.galion.studio/auth/callback
https://api.galion.studio/shopify/callback
https://pay.galion.studio/billing/confirm
```

---

## 🪝 Webhook Configuration

### Webhooks API Version
**Use**: `2025-10` (Latest stable version)

### Required Webhook Endpoints

Configure these webhooks in your Shopify app dashboard:

#### 1. Subscription Webhooks
```
Endpoint: https://api.galion.studio/webhooks/shopify
Topics to subscribe:
  - subscription/created
  - subscription/updated
  - subscription/cancelled
```

#### 2. Payment Webhooks
```
Endpoint: https://api.galion.studio/webhooks/shopify
Topics to subscribe:
  - orders/paid
  - checkout/created
  - checkout/updated
```

#### 3. Customer Webhooks
```
Endpoint: https://api.galion.studio/webhooks/shopify
Topics to subscribe:
  - customers/create
  - customers/update
  - customers/delete
```

---

## 🔐 API Scopes Required

Click "Select scopes" button in your Shopify app dashboard and enable:

### Essential Scopes
- ✅ `read_customers` - Read customer information
- ✅ `write_customers` - Create and update customers
- ✅ `read_orders` - Read order details
- ✅ `write_orders` - Create orders (if needed)
- ✅ `read_products` - Read product information
- ✅ `write_payment_sessions` - Process payments
- ✅ `read_payment_mandate` - Read payment mandates
- ✅ `write_payment_mandate` - Create payment mandates

### Additional Recommended Scopes
- ✅ `read_price_rules` - For discount management
- ✅ `write_price_rules` - Create discounts
- ✅ `read_checkouts` - Read checkout sessions
- ✅ `write_checkouts` - Manage checkouts

---

## 🔑 API Credentials Setup

After creating your app, you'll receive:

### 1. Get Your Credentials
From Shopify Partner Dashboard → Apps → pay.galion.studio:
- **API Key**: Found in "App credentials" section
- **API Secret**: Found in "App credentials" section (click "Show")
- **Access Token**: Generated after installing app on a store

### 2. Add to Your Environment File

Create or update `.env` file in your `v2/` directory:

```bash
# ==================== SHOPIFY CONFIGURATION ====================
# Store URL (your development/test store)
SHOPIFY_STORE_URL=pay-galion-studio.myshopify.com

# API Credentials (from Shopify Partner Dashboard)
SHOPIFY_API_KEY=your_api_key_here
SHOPIFY_API_SECRET=your_api_secret_here

# Access Token (generated after app installation)
SHOPIFY_ACCESS_TOKEN=shpat_your_access_token_here

# Webhook Secret (for verifying webhook authenticity)
# Found in: Shopify Partner Dashboard → Apps → pay.galion.studio → Webhooks
SHOPIFY_WEBHOOK_SECRET=your_webhook_secret_here

# App URLs
SHOPIFY_APP_URL=https://pay.galion.studio
SHOPIFY_REDIRECT_URL=https://pay.galion.studio/auth/callback
```

---

## 📋 Step-by-Step Setup Process

### Step 1: Create Shopify Partner Account
1. Go to https://partners.shopify.com/
2. Sign up or log in
3. Navigate to "Apps" section

### Step 2: Create New App (or Update Existing)
1. Click "Create app" or select `pay.galion.studio`
2. Choose "Custom app" or "Public app"
3. Fill in app details:
   - **App name**: pay.galion.studio-v2 (or keep as pay.galion.studio)
   - **App URL**: https://pay.galion.studio
   - **Redirect URL**: https://pay.galion.studio/auth/callback

### Step 3: Configure App URLs
In the "App setup" section:
```
App URL: https://pay.galion.studio
Redirect URLs:
  - https://pay.galion.studio/auth/callback
  - https://api.galion.studio/shopify/callback
  - https://pay.galion.studio/billing/confirm

Preferences URL (optional):
  - https://docs.galion.studio/pay/shopify-payment-processor
```

### Step 4: Set Webhook Subscriptions
1. Go to "Webhooks" section
2. Click "Add webhook"
3. For each webhook, set:
   - **URL**: `https://api.galion.studio/webhooks/shopify`
   - **Format**: JSON
   - **API version**: 2025-10
4. Select topics (see "Required Webhook Endpoints" above)

### Step 5: Request API Scopes
1. Click "Configuration" tab
2. Click "Select scopes" button
3. Enable all scopes listed in "API Scopes Required" section
4. Save changes

### Step 6: Get API Credentials
1. Go to "App credentials" section
2. Copy **API key** and **API secret**
3. Install app on your test store
4. Copy **Access token** after installation

### Step 7: Add Credentials to Environment
1. Open your `.env` file in `v2/` directory
2. Paste all credentials (see "Add to Your Environment File" section)
3. Save the file

### Step 8: Deploy Your Backend
```powershell
# Navigate to v2 directory
cd v2

# Restart backend to load new environment variables
docker-compose restart backend

# Check logs to verify Shopify connection
docker-compose logs backend | Select-String "shopify"
```

### Step 9: Test Webhook Integration
```powershell
# Use Shopify CLI to test webhooks
shopify webhook trigger orders/paid --address https://api.galion.studio/webhooks/shopify

# Or test manually with curl
curl -X POST https://api.galion.studio/webhooks/shopify \
  -H "Content-Type: application/json" \
  -H "X-Shopify-Topic: orders/paid" \
  -H "X-Shopify-Hmac-SHA256: your_hmac_here" \
  -d '{"id": 12345, "total_price": "99.00"}'
```

---

## 🧪 Testing Your Integration

### Test in Development Mode

1. **Create Test Store**
   - Go to https://partners.shopify.com/
   - Create development store
   - Install your app on test store

2. **Test Payment Flow**
   ```
   1. User signs up on pay.galion.studio
   2. User selects a plan (Free/Pro/Enterprise)
   3. User gets redirected to Shopify checkout
   4. User completes payment
   5. Webhook fires to your backend
   6. Credits added to user account
   ```

3. **Verify Webhooks Work**
   - Check backend logs: `docker-compose logs backend`
   - Look for: "Processing webhook: subscription/created"
   - Verify user credits updated in database

---

## 🚀 Production Deployment

### Before Going Live:

1. **✅ Test Mode Off**
   ```bash
   # In .env file
   DEBUG=false
   ENVIRONMENT=production
   ```

2. **✅ SSL Certificate Active**
   - Ensure `https://pay.galion.studio` has valid SSL
   - Shopify requires HTTPS for all webhooks

3. **✅ Domain DNS Configured**
   - Point `pay.galion.studio` to your server IP
   - Or use Cloudflare Tunnel (see CLOUDFLARE_SETUP_DEVELOPER.md)

4. **✅ Webhook Secret Set**
   - Get secret from Shopify dashboard
   - Add to `.env` file: `SHOPIFY_WEBHOOK_SECRET=xxx`

5. **✅ Rate Limiting Enabled**
   - Backend automatically handles Shopify API rate limits
   - Default: 2 requests per second

---

## 📊 Monitoring & Analytics

### Check Integration Health

```powershell
# View webhook processing logs
docker-compose logs backend | Select-String "webhook"

# Check database for transactions
docker-compose exec postgres psql -U nexus nexuslang_v2 -c "SELECT * FROM transactions ORDER BY created_at DESC LIMIT 10;"

# Monitor Shopify API usage
# Go to: Shopify Partner Dashboard → Apps → pay.galion.studio → Analytics
```

---

## 🔧 Troubleshooting

### Issue: Webhooks Not Arriving

**Check:**
1. Webhook URL is correct: `https://api.galion.studio/webhooks/shopify`
2. SSL certificate is valid on your domain
3. Backend is running: `docker-compose ps backend`
4. Firewall allows incoming HTTPS traffic

**Test:**
```bash
# Test webhook endpoint manually
curl https://api.galion.studio/webhooks/shopify
# Should return: Method Not Allowed (expected for GET requests)
```

### Issue: Webhook Signature Verification Fails

**Solution:**
1. Check `SHOPIFY_WEBHOOK_SECRET` in `.env` file
2. Get correct secret from Shopify dashboard
3. Restart backend: `docker-compose restart backend`

### Issue: API Rate Limit Exceeded

**Solution:**
Backend automatically handles rate limits with exponential backoff.
If you see errors:
1. Reduce API call frequency
2. Implement caching for product/customer data
3. Use bulk operations where possible

### Issue: Payment Not Recorded

**Check:**
1. Webhook received? Check logs: `docker-compose logs backend`
2. Database connection working?
3. Transaction table exists?
4. User ID mapping correct?

**Debug:**
```sql
-- Check recent transactions
SELECT * FROM transactions WHERE created_at > NOW() - INTERVAL '1 hour';

-- Check user credits
SELECT id, email, credits FROM users WHERE email = 'customer@example.com';
```

---

## 📚 Additional Resources

### Official Documentation
- [Shopify App Development](https://shopify.dev/docs/apps)
- [Shopify Webhooks](https://shopify.dev/docs/api/admin-rest/latest/resources/webhook)
- [Payment Apps](https://shopify.dev/docs/apps/payments)

### Your Project Documentation
- `v2/backend/services/billing/shopify_integration.py` - Integration code
- `v2/backend/services/billing/shopify_webhooks.py` - Webhook handlers
- `v2/backend/api/billing.py` - Billing API endpoints

### Testing Tools
- [Shopify CLI](https://shopify.dev/docs/api/shopify-cli) - Test webhooks locally
- [ngrok](https://ngrok.com/) - Expose local backend for testing
- [Postman](https://www.postman.com/) - Test API endpoints

---

## ✅ Checklist: Is My Setup Complete?

- [ ] Shopify app created in Partner Dashboard
- [ ] App URLs configured correctly
- [ ] All required API scopes selected
- [ ] Webhooks configured with correct endpoint
- [ ] API credentials added to `.env` file
- [ ] Backend restarted to load new credentials
- [ ] Test store created
- [ ] App installed on test store
- [ ] Test payment completed successfully
- [ ] Webhook received and processed
- [ ] User credits updated in database
- [ ] Production domain has SSL certificate
- [ ] DNS configured correctly
- [ ] Monitoring and logging enabled

---

## 🎉 You're Ready!

Once all checkboxes are ticked, your Shopify payment integration is live!

**Next Steps:**
1. Create your first subscription plan
2. Test the full payment flow end-to-end
3. Monitor webhooks in production
4. Set up alerts for failed payments

**Need Help?**
- Check logs: `docker-compose logs backend`
- Review code: `v2/backend/services/billing/`
- Test webhooks: Use Shopify CLI

---

**Questions?** Check the Shopify documentation or review the implementation code in `v2/backend/services/billing/`.

