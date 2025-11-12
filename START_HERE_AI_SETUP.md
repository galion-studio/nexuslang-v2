# 🎯 QUICK START - AI Multi-Model Setup Complete!

## ✅ What's Done

Your NexusLang v2 platform is now configured with:

1. **✅ Core Infrastructure**
   - PostgreSQL database (with secure password)
   - Redis cache (with secure password)
   - JWT authentication (secure keys generated)
   - Grafana monitoring

2. **✅ AI Multi-Model Gateway**
   - OpenRouter integration (access to 30+ AI models!)
   - Claude 3.5 Sonnet (default - best reasoning)
   - GPT-4 Turbo (fallback)
   - GPT-3.5 Turbo (fast queries)
   - CodeLlama 70B (code generation)
   - Perplexity Online (has internet access!)
   - Llama 3, Gemini, Mistral, and more!

---

## 🚀 Start Your Platform

```powershell
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
```

---

## 🌐 Access Your Services

Once running:

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | http://localhost:3000 | Web interface |
| **Backend API** | http://localhost:8000 | REST API |
| **API Docs** | http://localhost:8000/docs | Interactive API testing |
| **Grafana** | http://localhost:3001 | Monitoring (admin/pSaje9dx6vCyZzt4) |

---

## 🤖 Test Your AI Setup

### 1. Open API Docs
Go to: http://localhost:8000/docs

### 2. Try Quick Query
Navigate to: **POST /api/v2/ai/quick**

Click "Try it out" and use:
```json
{
  "prompt": "Explain what NexusLang is in one sentence"
}
```

### 3. Test Different Models
Navigate to: **GET /api/v2/ai/models**

See all 30+ available models!

### 4. Generate Code
Navigate to: **POST /api/v2/ai/code/generate**

```json
{
  "prompt": "Create a hello world function",
  "language": "python"
}
```

---

## 🎯 Available AI Models

### Fast & Cheap (Good for development)
- `openai/gpt-3.5-turbo` - $0.50 per 1M tokens
- `anthropic/claude-3-haiku` - $0.25 per 1M tokens
- `meta-llama/llama-3-70b-instruct` - $0.90 per 1M tokens

### Balanced (Recommended for most tasks)
- `anthropic/claude-3.5-sonnet` - $3.00 per 1M tokens (DEFAULT)
- `openai/gpt-4-turbo` - $10.00 per 1M tokens (FALLBACK)

### Specialized
- `meta-llama/codellama-70b-instruct` - Best for code
- `perplexity/pplx-70b-online` - Has internet access!

### Premium (For complex tasks)
- `anthropic/claude-3-opus` - $15.00 per 1M tokens
- `openai/gpt-4` - $30.00 per 1M tokens

---

## 💡 Quick Examples

### Chat with Claude (Default)
```bash
curl -X POST "http://localhost:8000/api/v2/ai/quick" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello!"}'
```

### Generate Code
```bash
curl -X POST "http://localhost:8000/api/v2/ai/code/generate" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a Fibonacci function",
    "language": "python"
  }'
```

### Use Specific Model
```bash
curl -X POST "http://localhost:8000/api/v2/ai/chat" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello!"}],
    "model": "meta-llama/llama-3-70b-instruct"
  }'
```

---

## 📚 Documentation

- **Full AI Guide:** `AI_ROUTER_GUIDE.md` (comprehensive guide)
- **API Keys Checklist:** `API_KEYS_CHECKLIST.md` (all API keys info)
- **Next Steps:** `NEXT_STEPS_API_KEYS.md` (getting started)

---

## 🔧 Configuration Files

Your `.env` file is configured with:
```bash
# AI Configuration (OpenRouter - Primary)
OPENROUTER_API_KEY=your-key-here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# Default Models
DEFAULT_AI_MODEL=anthropic/claude-3.5-sonnet
FALLBACK_AI_MODEL=openai/gpt-4-turbo
FAST_AI_MODEL=openai/gpt-3.5-turbo

# Provider
AI_PROVIDER=openrouter
```

---

## 💰 Cost Estimate

**Development usage (moderate):**
- ~1M tokens per month
- Using mix of models
- **Estimated cost: $10-30/month**

**Tips to reduce costs:**
1. Use GPT-3.5 or Haiku for simple tasks
2. Use Llama 3 70B for cost-effective option
3. Reserve Claude/GPT-4 for complex tasks
4. Set `max_tokens` limits

---

## 🎓 Learn More

### Model Selection Guide

**For your task, use:**
- **Complex reasoning:** Claude 3.5 Sonnet
- **Code generation:** CodeLlama 70B
- **Quick answers:** GPT-3.5 Turbo
- **Creative writing:** Claude Opus
- **Current info:** Perplexity Online
- **Cost-effective:** Llama 3 70B

### Advanced Features

See `AI_ROUTER_GUIDE.md` for:
- Streaming responses
- Multi-turn conversations
- Custom temperature settings
- Token usage monitoring
- Model comparison
- And more!

---

## 🆘 Troubleshooting

### Services won't start
```powershell
docker-compose down
docker-compose up -d
docker-compose logs backend
```

### AI not working
1. Check `OPENROUTER_API_KEY` in `.env`
2. Restart backend: `docker-compose restart backend`
3. Check logs: `docker-compose logs backend`

### Can't access API
- Make sure services are running: `docker-compose ps`
- Check http://localhost:8000/health
- View API docs: http://localhost:8000/docs

---

## ✨ You're Ready!

Your platform now has access to:
- ✅ Claude (Anthropic) - Best reasoning
- ✅ GPT-4 (OpenAI) - Reliable general use  
- ✅ Llama (Meta) - Open source option
- ✅ Gemini (Google) - Multimodal capabilities
- ✅ Mistral - European privacy-focused
- ✅ CodeLlama - Specialized for code
- ✅ Perplexity - Has internet access
- ✅ And 20+ more models!

**All through one unified API! 🚀**

---

**Next:** Start your services and test the AI endpoints!

```powershell
docker-compose up -d
```

Then visit: http://localhost:8000/docs

