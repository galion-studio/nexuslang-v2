# 🌐 OpenRouter Setup Guide - Primary AI Gateway

**Why OpenRouter**: Access 30+ AI models through one API  
**Cost**: Pay-per-use (no subscription)  
**Usage**: 99% of NexusLang v2 AI features

---

## 🎯 What is OpenRouter?

OpenRouter is a unified API gateway that provides access to multiple AI providers:

### Available Models (30+):
- **Anthropic**: Claude 3.5 Sonnet, Opus, Haiku
- **OpenAI**: GPT-4 Turbo, GPT-4, GPT-3.5 Turbo
- **Meta**: Llama 3 70B, CodeLlama 70B
- **Google**: Gemini Pro, Pro Vision
- **Mistral**: Large, Medium, Small
- **Perplexity**: Online models (internet access!)
- And many more!

### Benefits:
- ✅ **One API key** for all models
- ✅ **Cost optimization** (auto-routes to cheapest)
- ✅ **Automatic fallbacks** (if one model fails)
- ✅ **Pay per use** (no monthly subscriptions)
- ✅ **Transparent pricing** (see costs per request)

---

## 🚀 Quick Setup (2 Minutes)

### Step 1: Get API Key

1. Go to: https://openrouter.ai/
2. Click: **Sign In** (Google/GitHub)
3. Go to: **Keys** → **Create Key**
4. Name: "NexusLang Production"
5. Click: **Create**
6. Copy the key (starts with `sk-or-v1-...`)

### Step 2: Add Credits (Optional)

1. Go to: **Credits**
2. Add: $10-$50 (recommended starting amount)
3. Payment: Credit card or crypto

**Free Tier**: $5 free credits to start!

### Step 3: Configure in NexusLang

**In your v2/.env file:**
```env
OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here
AI_PROVIDER=openrouter
DEFAULT_AI_MODEL=anthropic/claude-3.5-sonnet
```

**That's it!** NexusLang v2 now has access to 30+ models.

---

## 💰 Pricing (OpenRouter vs Direct)

### Cost Comparison:

| Model | Direct | OpenRouter | Savings |
|-------|--------|------------|---------|
| **Claude Sonnet** | $3/1M tokens | $3/1M tokens | Same |
| **GPT-4 Turbo** | $10/1M tokens | $10/1M tokens | Same |
| **GPT-3.5** | $0.50/1M | $0.50/1M | Same |
| **Llama 3 70B** | N/A (self-host) | $0.59/1M | ✅ Huge savings! |
| **CodeLlama 70B** | N/A (self-host) | $0.59/1M | ✅ Huge savings! |
| **Claude Haiku** | $0.25/1M | $0.25/1M | Same |

**Benefit**: Access to models you can't get elsewhere (Llama, CodeLlama, Mistral) without self-hosting.

### Cost Per User (Estimated):

```
Free User (100 credits/month):
  ~20K tokens = $0.06 via OpenRouter
  (Using Claude Sonnet)

Pro User (10,000 credits/month):
  ~2M tokens = $6 via OpenRouter
  Revenue: $19/month
  Profit: $13/month (68% margin!)

Enterprise (unlimited, avg 50K credits):
  ~10M tokens = $30 via OpenRouter
  Revenue: $199/month
  Profit: $169/month (85% margin!)
```

**With OpenRouter**: Higher margins than direct OpenAI! ✅

---

## 🎯 How NexusLang v2 Uses OpenRouter

### Default Configuration:

```python
# Primary model (best quality)
DEFAULT_AI_MODEL = "anthropic/claude-3.5-sonnet"

# Fallback (if Claude fails)
FALLBACK_AI_MODEL = "openai/gpt-4-turbo"

# Fast model (simple queries)
FAST_AI_MODEL = "openai/gpt-3.5-turbo"

# Code model (code generation)
CODE_AI_MODEL = "meta-llama/codellama-70b-instruct"
```

### AI Router Handles:
- ✅ Model selection (automatic or user-specified)
- ✅ Fallback logic (if model unavailable)
- ✅ Error handling
- ✅ Token counting
- ✅ Cost tracking

### Example API Call:

```python
# In NexusLang v2 backend
from services.ai import get_ai_router

ai = get_ai_router()

# Uses OpenRouter automatically
response = await ai.chat_completion(
    messages=[{"role": "user", "content": "Hello!"}],
    model="anthropic/claude-3.5-sonnet"
)

# OpenRouter handles:
# - API call to Anthropic via their gateway
# - Token counting
# - Cost calculation
# - Error handling
# - Fallback if needed
```

---

## 📊 Monitoring Usage

### OpenRouter Dashboard:

1. Go to: https://openrouter.ai/activity
2. See:
   - Requests per model
   - Tokens used
   - Cost per request
   - Total spend
3. Set alerts for spending limits

### In NexusLang v2:

```bash
# Check AI usage in admin dashboard
# /admin → AI Usage Statistics

Shows:
  - Total AI requests
  - Tokens consumed
  - Cost breakdown by model
  - Most used models
```

---

## 🔧 Configuration Examples

### Development (Use Cheaper Models):

```env
OPENROUTER_API_KEY=sk-or-v1-your-key
DEFAULT_AI_MODEL=openai/gpt-3.5-turbo  # Cheaper for testing
FALLBACK_AI_MODEL=meta-llama/llama-3-8b-instruct
```

### Production (Use Best Models):

```env
OPENROUTER_API_KEY=sk-or-v1-your-key
DEFAULT_AI_MODEL=anthropic/claude-3.5-sonnet  # Best quality
FALLBACK_AI_MODEL=openai/gpt-4-turbo
CODE_AI_MODEL=meta-llama/codellama-70b-instruct
```

### Cost-Optimized (Use Open Source):

```env
OPENROUTER_API_KEY=sk-or-v1-your-key
DEFAULT_AI_MODEL=meta-llama/llama-3-70b-instruct  # Free!
FALLBACK_AI_MODEL=openai/gpt-3.5-turbo
```

---

## ⚡ Why OpenRouter for NexusLang v2?

### 1. Flexibility
- Switch models instantly (no code changes)
- A/B test different models
- Use best model for each task

### 2. Cost Efficiency
- Automatic routing to cheapest option
- No wasted API subscriptions
- Pay only for what you use

### 3. Reliability
- Automatic fallbacks
- Multiple providers = higher uptime
- No single point of failure

### 4. Future-Proof
- New models added automatically
- No integration work needed
- Stay cutting-edge effortlessly

### 5. Simplicity
- One API key
- One integration
- Works with everything

---

## 🔥 OpenRouter + NexusLang = Perfect Match

**For NexusLang v2:**
- Binary compilation needs fast processing → Use fast models
- IDE assistance needs smart models → Use Claude
- Code generation needs specialized models → Use CodeLlama
- All through OpenRouter! ✅

**Cost Example (1,000 users):**
```
Without OpenRouter:
  - Separate API keys for Claude, GPT-4, etc.
  - Separate billing
  - Complex cost tracking
  - Estimated: $8,000/month

With OpenRouter:
  - One API key
  - One bill
  - Automatic optimization
  - Estimated: $6,500/month

Savings: $1,500/month ($18K/year!) 💰
```

---

## 📋 Setup Checklist

- [ ] Create OpenRouter account
- [ ] Generate API key
- [ ] Add $10+ credits
- [ ] Add OPENROUTER_API_KEY to v2/.env
- [ ] Set AI_PROVIDER=openrouter
- [ ] Test: Send chat message in IDE
- [ ] Monitor: Check OpenRouter dashboard
- [ ] Optimize: Adjust models based on costs

---

## 🎯 Recommended Models for NexusLang

### Chat & General (Use Claude):
```
Model: anthropic/claude-3.5-sonnet
Cost: $3/1M tokens
Use: 60% of requests
Why: Best reasoning, accurate, helpful
```

### Code Generation (Use CodeLlama):
```
Model: meta-llama/codellama-70b-instruct
Cost: $0.59/1M tokens (5x cheaper!)
Use: 25% of requests
Why: Specialized for code, fast, cheap
```

### Quick Tasks (Use GPT-3.5):
```
Model: openai/gpt-3.5-turbo
Cost: $0.50/1M tokens
Use: 10% of requests
Why: Fast, cheap, good enough
```

### With Internet (Use Perplexity):
```
Model: perplexity/pplx-70b-online
Cost: $1/1M tokens
Use: 5% of requests
Why: Has internet access for current info
```

**Mix optimization**: Average cost ~$2/1M tokens (30% cheaper than all Claude!)

---

## 🚀 Getting Started

**Already in NexusLang v2:**
- ✅ OpenRouter integration built-in
- ✅ All models pre-configured
- ✅ Smart routing implemented
- ✅ Cost tracking ready

**You just need:**
1. OpenRouter API key
2. Add to v2/.env
3. Deploy
4. Done!

---

## 📞 Support

**OpenRouter Help:**
- Dashboard: https://openrouter.ai/
- Discord: https://discord.gg/openrouter
- Docs: https://openrouter.ai/docs

**NexusLang Help:**
- See: `v2/backend/services/ai/ai_router.py`
- Docs: API_DOCUMENTATION.md

---

**Status**: ✅ OpenRouter is primary AI provider (99% of use)  
**Setup**: 2 minutes  
**Cost**: Lower than direct APIs  
**Result**: Best models, lowest cost, highest flexibility

🌐 **Get your key**: https://openrouter.ai/keys

🚀 **Then deploy!**

