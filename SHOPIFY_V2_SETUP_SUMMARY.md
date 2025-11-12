# 🎯 Shopify App Setup for pay.galion.studio v2 - SUMMARY

## What I've Created for You

I've set up everything you need to integrate your Shopify app (`pay.galion.studio`) with your NexusLang v2 project.

---

## 📁 New Files Created

### 1. **SHOPIFY_APP_SETUP_V2.md**
**Purpose**: Complete step-by-step guide for Shopify integration  
**Use When**: You're setting up Shopify for the first time or need detailed reference

**Contains:**
- Complete setup instructions
- All required URLs and endpoints
- API scopes needed
- Webhook configuration
- Troubleshooting guide
- Testing procedures

### 2. **v2/setup-shopify.ps1**
**Purpose**: Interactive PowerShell script to configure credentials  
**Use When**: You want to quickly add Shopify credentials to your `.env` file

**Run This:**
```powershell
cd v2
.\setup-shopify.ps1
```

**What It Does:**
- Prompts for Shopify credentials (API Key, Secret, etc.)
- Automatically updates your `.env` file
- Validates configuration
- Shows next steps

### 3. **SHOPIFY_CONFIG_QUICK_REF.md**
**Purpose**: Quick reference card  
**Use When**: You need URLs, scopes, or webhooks at a glance while configuring Shopify dashboard

**Contains:**
- All URLs in one place
- List of webhooks to subscribe
- Required API scopes
- Quick test commands
- Checklist

---

## 🚀 What You Need to Do Next

### Step 1: Get Your Shopify Credentials (5 minutes)

1. Go to: https://partners.shopify.com/
2. Navigate to: **Apps** → **pay.galion.studio**
3. Get these from **App credentials** section:
   - API Key
   - API Secret
4. Note down your store URL: `pay-galion-studio.myshopify.com`

### Step 2: Run Setup Script (2 minutes)

```powershell
cd C:\Users\Gigabyte\Documents\project-nexus\v2
.\setup-shopify.ps1
```

Follow the prompts and enter your credentials when asked.

### Step 3: Configure Shopify Dashboard (10 minutes)

Open: https://partners.shopify.com/

#### A. Set App URLs
Go to: **Configuration** tab

**App URL:**
```
https://pay.galion.studio
```

**Redirect URLs:** (click "Add" for each)
```
https://pay.galion.studio/auth/callback
https://api.galion.studio/shopify/callback
https://pay.galion.studio/billing/confirm
```

**Preferences URL (optional):**
```
https://docs.galion.studio/pay/shopify-payment-processor
```

#### B. Select API Scopes
Go to: **Configuration** tab → Click **"Select scopes"**

**Enable These (at minimum):**
- ✅ `read_customers` - Read customer information
- ✅ `write_customers` - Create/update customers
- ✅ `read_orders` - Read order details
- ✅ `read_products` - Read products
- ✅ `write_payment_sessions` - Process payments
- ✅ `read_payment_mandate` - Read payment mandates
- ✅ `write_payment_mandate` - Create payment mandates

**Click "Save"** at the bottom

#### C. Configure Webhooks
Go to: **Webhooks** tab → Click **"Add webhook"**

For each webhook below, click "Add webhook" and fill in:

**Endpoint URL:** `https://api.galion.studio/webhooks/shopify`  
**Format:** JSON  
**API Version:** 2025-10

**Add These Topics:**
1. `subscription/created` - New subscription
2. `subscription/updated` - Subscription changed
3. `subscription/cancelled` - Subscription ended
4. `orders/paid` - Payment received
5. `customers/create` - Customer created
6. `customers/update` - Customer updated

**After adding all webhooks:**
- Copy the **Webhook Secret** shown at the top
- Run setup script again: `.\setup-shopify.ps1`
- Or manually add to `.env` file: `SHOPIFY_WEBHOOK_SECRET=your_secret_here`

### Step 4: Install App on Test Store (5 minutes)

1. Create a development store (if you haven't):
   - Shopify Partner Dashboard → **Stores** → **Add store**
   - Select "Development store"
   - Fill in details

2. Install your app:
   - Go to: **Apps** → **pay.galion.studio**
   - Click: **"Select store"**
   - Choose your development store
   - Click: **"Install app"**

3. Copy the **Access Token** after installation
4. Add it to `.env` file:
   ```
   SHOPIFY_ACCESS_TOKEN=shpat_your_token_here
   ```

### Step 5: Deploy Backend (2 minutes)

```powershell
# Navigate to v2 directory
cd C:\Users\Gigabyte\Documents\project-nexus\v2

# Restart backend to load new credentials
docker-compose restart backend

# Verify it's working
docker-compose logs backend | Select-String "shopify"
```

You should see: "Shopify integration enabled" in the logs.

### Step 6: Test Integration (5 minutes)

#### Test 1: Webhook Endpoint
```powershell
# Should return: Method Not Allowed (that's correct for GET request)
curl https://api.galion.studio/webhooks/shopify
```

#### Test 2: Create Test Payment
1. Log into your development store
2. Create a test order
3. Complete payment
4. Check logs:
   ```powershell
   docker-compose logs backend | Select-String "webhook"
   ```

You should see: "Processing webhook: orders/paid"

#### Test 3: Check Database
```powershell
docker-compose exec postgres psql -U nexus nexuslang_v2 -c "SELECT * FROM transactions ORDER BY created_at DESC LIMIT 5;"
```

You should see your test transaction.

---

## ✅ Success Checklist

### Configuration Complete When:
- ✅ All credentials in `.env` file
- ✅ Backend starts without Shopify errors
- ✅ Webhook endpoint accessible via HTTPS
- ✅ Test payment creates transaction in database
- ✅ User credits updated after payment

### You'll Know It's Working When:
1. No Shopify-related errors in backend logs
2. Webhooks show "delivered" status in Shopify dashboard
3. Test payments create transactions in database
4. User accounts receive credits after purchase

---

## 🔧 Your Current Setup (From Screenshots)

Based on the Shopify dashboard screenshot you shared:

**App Name:** pay.galion.studio  
**Store:** pay-galion-studio.myshopify.com  
**Currency:** Polish Zloty (PLN zł)  
**Location:** Poland  
**Email:** finance@galion.studio

**URLs Currently Set:**
- App URL: https://pay.galion.studio
- Preferences URL: https://docs.galion.studio/pay/shopify-payment-processor
- Webhooks API: 2025-10 ✅

**What You Still Need to Do:**
1. Add redirect URLs (see Step 3A above)
2. Select API scopes (see Step 3B above)
3. Configure webhooks (see Step 3C above)
4. Get credentials and run setup script (see Steps 1-2 above)

---

## 📚 Documentation Reference

| Document | Purpose | When to Use |
|----------|---------|-------------|
| **SHOPIFY_APP_SETUP_V2.md** | Complete guide | Full setup, troubleshooting |
| **SHOPIFY_CONFIG_QUICK_REF.md** | Quick reference | Configuring Shopify dashboard |
| **SHOPIFY_V2_SETUP_SUMMARY.md** | This file | Understanding what to do |
| **v2/setup-shopify.ps1** | Setup script | Adding credentials |

---

## 🆘 Common Issues & Solutions

### Issue: "Shopify credentials not configured"
**Solution:** Run `.\setup-shopify.ps1` and enter your credentials

### Issue: "Webhook signature verification failed"
**Solution:** 
1. Get webhook secret from Shopify dashboard
2. Add to `.env`: `SHOPIFY_WEBHOOK_SECRET=your_secret`
3. Restart: `docker-compose restart backend`

### Issue: "Cannot connect to webhook endpoint"
**Solution:**
1. Ensure backend is running: `docker-compose ps`
2. Check SSL certificate: `curl https://api.galion.studio/health`
3. Verify domain DNS is correct

### Issue: "Payment processed but credits not added"
**Solution:**
1. Check logs: `docker-compose logs backend`
2. Verify database connection
3. Check transaction table for errors

---

## 🎉 You're All Set!

After completing Steps 1-6 above, your Shopify integration will be fully functional!

**Questions?**
- Read: `SHOPIFY_APP_SETUP_V2.md` (detailed guide)
- Check: `v2/backend/services/billing/shopify_integration.py` (code)
- Test: Use Shopify CLI to trigger test webhooks

**Need Help?**
- Shopify Docs: https://shopify.dev/docs/apps
- Your Backend Code: `v2/backend/services/billing/`
- Webhook Logs: `docker-compose logs backend | Select-String "webhook"`

---

**Total Time Needed:** ~30 minutes  
**Difficulty:** Moderate (follow steps carefully)  
**Reward:** Fully integrated payment system! 🎉

