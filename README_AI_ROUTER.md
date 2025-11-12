# 🤖 NexusLang v2 - AI Multi-Model Router

**Your Gateway to 30+ AI Models Through One Unified API**

---

## 🎉 What's New

**NexusLang v2 now includes a powerful AI Router that gives you access to:**

- **30+ AI Models** from multiple providers
- **Smart Routing** - Best model for each task
- **Automatic Fallback** - Never fails if one model is down
- **Cost Optimization** - Cheap models for simple tasks
- **Code Intelligence** - 9 AI-powered IDE features
- **Enhanced Search** - AI-powered Grokopedia

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd v2/backend
pip install -r requirements.txt
```

### 2. Configure API Key

Add to `.env`:
```bash
OPENROUTER_API_KEY=your-key-here
```

Get key: https://openrouter.ai/keys

### 3. Start Backend

```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### 4. Access API

Visit: http://localhost:8000/docs

---

## 🤖 Available AI Models

### Anthropic Claude (Best for reasoning & coding)
- `anthropic/claude-3.5-sonnet` - $3/1M tokens (DEFAULT)
- `anthropic/claude-3-opus` - $15/1M tokens
- `anthropic/claude-3-haiku` - $0.25/1M tokens

### OpenAI GPT (Reliable & tested)
- `openai/gpt-4-turbo` - $10/1M tokens (FALLBACK)
- `openai/gpt-4` - $30/1M tokens
- `openai/gpt-3.5-turbo` - $0.50/1M tokens

### Meta Llama (Open source)
- `meta-llama/llama-3-70b-instruct` - $0.90/1M tokens
- `meta-llama/codellama-70b-instruct` - $0.90/1M tokens

### Google Gemini
- `google/gemini-pro` - $0.50/1M tokens
- `google/gemini-pro-vision` - $0.50/1M tokens

### Specialized
- `perplexity/pplx-70b-online` - $1/1M tokens (has internet!)
- `mistralai/mistral-large` - $8/1M tokens

And 20+ more!

---

## 📡 API Endpoints

### General AI Endpoints

**POST** `/api/v2/ai/chat` - Chat with any model
```json
{
  "messages": [{"role": "user", "content": "Hello!"}],
  "model": "anthropic/claude-3.5-sonnet"
}
```

**POST** `/api/v2/ai/quick` - Quick query (uses fast model)
```json
{
  "prompt": "What is Python?"
}
```

**POST** `/api/v2/ai/search` - Search with internet
```json
{
  "query": "Latest AI news",
  "context": "Focus on LLMs"
}
```

**GET** `/api/v2/ai/models` - List all available models

---

### IDE AI Endpoints

**POST** `/api/v2/ide/ai/generate` - Generate code
```json
{
  "description": "Create a REST API endpoint",
  "language": "python"
}
```

**POST** `/api/v2/ide/ai/explain` - Explain code
```json
{
  "code": "def factorial(n): ...",
  "language": "python",
  "detail_level": "detailed"
}
```

**POST** `/api/v2/ide/ai/find-bugs` - Find bugs

**POST** `/api/v2/ide/ai/improve` - Get suggestions

**POST** `/api/v2/ide/ai/optimize` - Optimize code

**POST** `/api/v2/ide/ai/document` - Add documentation

**POST** `/api/v2/ide/ai/refactor` - Refactor code

**POST** `/api/v2/ide/ai/chat` - Chat about code

---

## 💡 Usage Examples

### Generate Code

```python
from services.ai import get_ai_router

ai = get_ai_router()

# Generate Python code
result = await ai.generate_code(
    prompt="Create a function to calculate fibonacci",
    language="python"
)

print(result["content"])
```

### Analyze Code

```python
result = await ai.analyze_code(
    code="def foo(x): return x * 2",
    language="python",
    analysis_type="review"
)

print(result["content"])  # AI suggestions
```

### Use Different Models

```python
# Use Claude for reasoning
response = await ai.chat_completion(
    messages=[{"role": "user", "content": "Explain quantum computing"}],
    model="anthropic/claude-3.5-sonnet"
)

# Use GPT-3.5 for quick queries
response = await ai.quick_response("What is 2+2?")

# Use Perplexity for current info
response = await ai.search_with_ai("Latest tech news")
```

---

## 🎯 Best Practices

### Choose Right Model for Task

| Task | Model | Cost |
|------|-------|------|
| Deep reasoning | Claude Sonnet | $3/1M |
| Code generation | CodeLlama 70B | $0.90/1M |
| Quick answers | GPT-3.5 | $0.50/1M |
| Creative writing | Claude Opus | $15/1M |
| Current info | Perplexity Online | $1/1M |
| Cost-effective | Llama 3 70B | $0.90/1M |

### Temperature Settings

```python
# Focused (code, facts)
temperature=0.2

# Balanced (default)
temperature=0.7

# Creative (writing)
temperature=1.2
```

---

## 🔧 Configuration

### Environment Variables

```bash
# Primary AI Gateway (REQUIRED)
OPENROUTER_API_KEY=sk-or-your-key

# Model Defaults (Optional)
DEFAULT_AI_MODEL=anthropic/claude-3.5-sonnet
FALLBACK_AI_MODEL=openai/gpt-4-turbo
FAST_AI_MODEL=openai/gpt-3.5-turbo

# Provider Selection
AI_PROVIDER=openrouter  # or "openai", "auto"

# OpenAI Direct (Optional)
OPENAI_API_KEY=sk-your-key
```

---

## 📊 Cost Estimates

### Development (Light usage)
- ~1M tokens/month
- Mix of cheap models
- **$10-30/month**

### Production (Moderate)
- ~10M tokens/month
- Balanced model usage
- **$50-200/month**

### Cost Reduction Tips
1. Use GPT-3.5 or Haiku for simple tasks
2. Use Llama 3 instead of GPT-4
3. Set `max_tokens` limits
4. Cache frequent responses

---

## 🛠️ Implementation Details

### Files Created

**AI Router:**
- `v2/backend/services/ai/ai_router.py` - Multi-model gateway
- `v2/backend/services/ai/__init__.py` - Module exports
- `v2/backend/api/ai.py` - AI API endpoints

**IDE AI Assistant:**
- `v2/backend/services/ide/ai_assistant.py` - Code intelligence
- `v2/backend/api/ide.py` - Enhanced with 9 AI endpoints

**Configuration:**
- `v2/backend/core/config.py` - Updated with AI settings

**Integration:**
- `v2/backend/main.py` - AI router registered

---

## 🎓 Documentation

- **AI_ROUTER_GUIDE.md** - Complete usage guide
- **🎉_AI_IMPLEMENTATION_COMPLETE.md** - Implementation details
- **API_KEYS_CHECKLIST.md** - All API keys reference
- **RUNPOD_QUICK_START.md** - RunPod deployment

---

## 🔒 Security

- ✅ API keys in environment variables
- ✅ No keys in code
- ✅ Rate limiting built-in
- ✅ Secure authentication
- ✅ CORS configuration

---

## 🆘 Troubleshooting

### AI Not Working
1. Check `OPENROUTER_API_KEY` is set in `.env`
2. Restart backend
3. Check logs: `docker-compose logs backend`

### High Costs
1. Use cheaper models (GPT-3.5, Haiku, Llama)
2. Set `max_tokens` limits
3. Monitor OpenRouter dashboard

### Model Errors
1. Check model name: GET `/api/v2/ai/models`
2. Try fallback model
3. Check OpenRouter status

---

## 📞 Support

- **OpenRouter Docs:** https://openrouter.ai/docs
- **Model Comparison:** https://openrouter.ai/models
- **Pricing:** https://openrouter.ai/docs#models

---

## 🎊 Summary

✅ **30+ AI models** through one API  
✅ **Smart routing** & fallbacks  
✅ **9 IDE AI features**  
✅ **Cost optimized**  
✅ **Production ready**  
✅ **Comprehensive docs**  

**Repository:** https://github.com/galion-studio/nexuslang-v2

**Your AI-powered platform is ready! 🚀**

