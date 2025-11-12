# 🛒 Shopify App Configuration - Quick Reference

**App Name**: `pay.galion.studio` (or `pay.galion.studio-v2`)

---

## 📍 URLs to Configure in Shopify Dashboard

### App URL
```
https://pay.galion.studio
```

### Redirect URLs (OAuth)
```
https://pay.galion.studio/auth/callback
https://api.galion.studio/shopify/callback
https://pay.galion.studio/billing/confirm
```

### Preferences URL (optional)
```
https://docs.galion.studio/pay/shopify-payment-processor
```

### Webhook Endpoint
```
https://api.galion.studio/webhooks/shopify
```
**Format**: JSON  
**API Version**: 2025-10

---

## 🪝 Webhooks to Subscribe

| Topic | Purpose |
|-------|---------|
| `subscription/created` | New subscription started |
| `subscription/updated` | Subscription plan changed |
| `subscription/cancelled` | Subscription ended |
| `orders/paid` | Payment received |
| `customers/create` | New customer created |
| `customers/update` | Customer info updated |

---

## 🔐 API Scopes to Enable

### Essential (Required)
- ✅ `read_customers`
- ✅ `write_customers`
- ✅ `read_orders`
- ✅ `read_products`
- ✅ `write_payment_sessions`
- ✅ `read_payment_mandate`
- ✅ `write_payment_mandate`

### Optional (Recommended)
- ✅ `write_orders`
- ✅ `read_price_rules`
- ✅ `write_price_rules`
- ✅ `read_checkouts`
- ✅ `write_checkouts`

---

## 🔑 Credentials Needed

Get from: **Shopify Partner Dashboard** → **Apps** → **pay.galion.studio**

1. **API Key** (from "App credentials")
2. **API Secret** (from "App credentials")
3. **Access Token** (after installing app on store)
4. **Webhook Secret** (from "Webhooks" section)
5. **Store URL** (e.g., `pay-galion-studio.myshopify.com`)

---

## ⚡ Quick Setup Commands

```powershell
# Run interactive setup
cd v2
.\setup-shopify.ps1

# Manually edit .env file
notepad .env

# Restart backend to load new config
docker-compose restart backend

# View logs
docker-compose logs backend
```

---

## ✅ Configuration Checklist

- [ ] App created in Shopify Partner Dashboard
- [ ] App URL set to `https://pay.galion.studio`
- [ ] All redirect URLs added
- [ ] API scopes selected (at least essential ones)
- [ ] Webhooks configured with correct endpoint
- [ ] Webhook topics subscribed
- [ ] API Key copied to `.env` file
- [ ] API Secret copied to `.env` file
- [ ] Test store created
- [ ] App installed on test store
- [ ] Access Token copied to `.env` file
- [ ] Webhook Secret copied to `.env` file
- [ ] Backend restarted
- [ ] Test payment completed successfully

---

## 🧪 Quick Test

```powershell
# Test webhook endpoint is accessible
curl https://api.galion.studio/webhooks/shopify

# View recent backend logs
docker-compose logs backend --tail 50

# Check database for transactions
docker-compose exec postgres psql -U nexus nexuslang_v2 -c "SELECT * FROM transactions LIMIT 5;"
```

---

## 📚 Full Documentation

See: `SHOPIFY_APP_SETUP_V2.md` for complete step-by-step guide

---

**Need Help?**
- Shopify Docs: https://shopify.dev/docs/apps
- Backend Code: `v2/backend/services/billing/shopify_integration.py`
- Webhook Handler: `v2/backend/services/billing/shopify_webhooks.py`

