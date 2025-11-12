# 🤖 AI Router - Multi-Model AI Gateway

## Overview

Your NexusLang v2 platform now has a **unified AI gateway** that provides access to **multiple AI models** through OpenRouter! This means you can use Claude, GPT-4, Llama, Gemini, and many other models through a single API.

---

## ✅ What's Configured

### Primary Setup: OpenRouter
- **Provider:** OpenRouter (https://openrouter.ai/)
- **Access to:** 30+ AI models from different providers
- **Default Model:** Claude 3.5 Sonnet (best reasoning)
- **Fallback Model:** GPT-4 Turbo (if primary fails)
- **Fast Model:** GPT-3.5 Turbo (for quick queries)

### Available AI Models

#### 🎯 **Anthropic Claude** (Best for reasoning, coding, analysis)
- `anthropic/claude-3.5-sonnet` - Latest, most capable (Default)
- `anthropic/claude-3-opus` - Most powerful, expensive
- `anthropic/claude-3-haiku` - Fastest, cheapest

#### 🤖 **OpenAI GPT** (General purpose, widely tested)
- `openai/gpt-4-turbo` - Best GPT-4 version (Fallback)
- `openai/gpt-4` - Standard GPT-4
- `openai/gpt-3.5-turbo` - Fast and cheap (Quick queries)

#### 🌐 **Google Gemini** (Good for multimodal)
- `google/gemini-pro` - Google's latest
- `google/gemini-pro-vision` - With vision capabilities

#### 🦙 **Meta Llama** (Open source, good value)
- `meta-llama/llama-3-70b-instruct` - Most capable
- `meta-llama/llama-3-8b-instruct` - Fastest
- `meta-llama/codellama-70b-instruct` - Best for code

#### 🔮 **Mistral** (European, privacy-focused)
- `mistralai/mistral-large` - Most capable
- `mistralai/mistral-medium` - Balanced
- `mistralai/mistral-small` - Fast

#### 🔍 **Specialized Models**
- `perplexity/pplx-70b-online` - **Has internet access!**
- And 20+ more models available!

---

## 🚀 How to Use

### 1. Basic Chat Completion

```python
from services.ai import get_ai_router

ai = get_ai_router()

# Simple chat with default model (Claude 3.5 Sonnet)
response = await ai.chat_completion(
    messages=[
        {"role": "user", "content": "Explain quantum computing"}
    ]
)

print(response["content"])  # AI's response
print(response["model"])    # Model that was used
print(response["usage"])    # Token usage stats
```

### 2. Use Specific Model

```python
# Use GPT-4 instead
response = await ai.chat_completion(
    messages=[
        {"role": "user", "content": "Write a poem"}
    ],
    model="openai/gpt-4-turbo"
)

# Use Llama for open-source option
response = await ai.chat_completion(
    messages=[
        {"role": "user", "content": "Summarize this text"}
    ],
    model="meta-llama/llama-3-70b-instruct"
)
```

### 3. Code Generation

```python
# Automatically uses best code model (CodeLlama 70B)
result = await ai.generate_code(
    prompt="Create a function to calculate fibonacci numbers",
    language="python"
)

print(result["content"])  # Generated code
```

### 4. Code Analysis

```python
code = """
def calculate(x, y):
    return x + y
"""

# Automatically uses Claude Sonnet for best analysis
result = await ai.analyze_code(
    code=code,
    language="python",
    analysis_type="review"  # Options: review, debug, explain, optimize
)

print(result["content"])  # Analysis and suggestions
```

### 5. Quick Queries (Fast & Cheap)

```python
# Uses GPT-3.5 Turbo for speed
answer = await ai.quick_response("What is 2+2?")
print(answer)  # Just the text response
```

### 6. AI Search (With Internet Access!)

```python
# Uses Perplexity model with real-time web access
result = await ai.search_with_ai(
    query="What are the latest developments in AI for November 2025?"
)

print(result["content"])  # Answer with current information
```

---

## 🌐 API Endpoints

All endpoints are available at `/api/v2/ai/`

### POST `/api/v2/ai/chat`
General chat completion with any model

**Request:**
```json
{
  "messages": [
    {"role": "user", "content": "Hello!"}
  ],
  "model": "anthropic/claude-3.5-sonnet",
  "temperature": 0.7,
  "max_tokens": 2000
}
```

### POST `/api/v2/ai/code/generate`
Generate code (uses CodeLlama 70B)

**Request:**
```json
{
  "prompt": "Create a REST API endpoint",
  "language": "python",
  "context": "Using FastAPI framework"
}
```

### POST `/api/v2/ai/code/analyze`
Analyze code (uses Claude Sonnet)

**Request:**
```json
{
  "code": "def foo(): pass",
  "language": "python",
  "analysis_type": "review"
}
```

### POST `/api/v2/ai/quick`
Quick answer (uses GPT-3.5 Turbo)

**Request:**
```json
{
  "prompt": "What is Python?"
}
```

### POST `/api/v2/ai/search`
AI search with internet (uses Perplexity Online)

**Request:**
```json
{
  "query": "Latest AI news",
  "context": "Focus on LLMs"
}
```

### GET `/api/v2/ai/models`
List all available models

### GET `/api/v2/ai/models/{model}`
Get info about specific model

---

## 💡 Best Practices

### 1. Choose the Right Model for the Task

| Task | Recommended Model | Why |
|------|------------------|-----|
| Deep reasoning | Claude 3.5 Sonnet | Best at complex analysis |
| Code generation | CodeLlama 70B | Specialized for code |
| Quick answers | GPT-3.5 Turbo | Fast and cheap |
| Creative writing | Claude Opus | Most creative |
| Current info | Perplexity Online | Has internet access |
| Cost-effective | Llama 3 70B | Open source, good value |

### 2. Temperature Settings

```python
# Focused, deterministic (good for code, analysis)
temperature=0.2

# Balanced (default for most tasks)
temperature=0.7

# Creative, varied (good for writing, brainstorming)
temperature=1.2
```

### 3. Use Fallbacks

The system automatically falls back to GPT-4 Turbo if the primary model fails. You can customize this in `.env`:

```bash
DEFAULT_AI_MODEL=anthropic/claude-3.5-sonnet
FALLBACK_AI_MODEL=openai/gpt-4-turbo
FAST_AI_MODEL=openai/gpt-3.5-turbo
```

### 4. Monitor Costs

Different models have different costs. Check pricing:

```python
ai = get_ai_router()
info = ai.get_model_info("anthropic/claude-3.5-sonnet")
print(info["cost_per_1m_tokens"])  # Cost per million tokens
```

---

## 💰 Cost Estimates

| Model | Cost per 1M tokens | Best for |
|-------|-------------------|----------|
| Claude Haiku | $0.25 | Simple tasks |
| GPT-3.5 Turbo | $0.50 | Quick queries |
| Llama 3 70B | $0.90 | Cost-effective general use |
| CodeLlama 70B | $0.90 | Code generation |
| Perplexity Online | $1.00 | Search with internet |
| Claude Sonnet | $3.00 | Best reasoning |
| GPT-4 Turbo | $10.00 | Reliable general use |
| Claude Opus | $15.00 | Most powerful tasks |

**Average development costs:** $10-30/month with moderate usage

---

## 🔧 Configuration

### Environment Variables (`.env`)

```bash
# Primary AI Gateway
OPENROUTER_API_KEY=sk-or-your-key-here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# Model Selection
DEFAULT_AI_MODEL=anthropic/claude-3.5-sonnet
FALLBACK_AI_MODEL=openai/gpt-4-turbo
FAST_AI_MODEL=openai/gpt-3.5-turbo

# Provider Selection
AI_PROVIDER=openrouter  # Options: openrouter, openai, auto

# OpenAI (optional, for direct access)
OPENAI_API_KEY=sk-your-key-here
```

---

## 🎯 Use Cases

### 1. Interactive Coding Assistant
```python
# User asks for help
user_code = "# My buggy code here"

analysis = await ai.analyze_code(
    code=user_code,
    analysis_type="debug"
)

# AI finds bugs and suggests fixes
```

### 2. Multi-Model Comparison
```python
# Get answers from different models
models = [
    "anthropic/claude-3.5-sonnet",
    "openai/gpt-4-turbo",
    "meta-llama/llama-3-70b-instruct"
]

question = "Explain recursion"

for model in models:
    response = await ai.chat_completion(
        messages=[{"role": "user", "content": question}],
        model=model
    )
    print(f"{model}: {response['content']}\n")
```

### 3. Smart Content Generation
```python
# Use specialized models for different content types

# Code
code = await ai.generate_code("Create API endpoint")

# Analysis  
analysis = await ai.analyze_code(code["content"])

# Quick summary
summary = await ai.quick_response("Summarize this: ...")

# Current info
latest = await ai.search_with_ai("Latest tech news")
```

---

## 📊 Model Comparison

### Speed vs Quality

```
Fast & Cheap          Balanced              Slow & Expensive
│                     │                     │
GPT-3.5 ──> Llama 3 ──> Claude Sonnet ──> Claude Opus
           70B                            
```

### Code Generation

```
Good                  Better                Best
│                     │                     │
GPT-4 ──> Claude Sonnet ──> CodeLlama 70B
```

### Reasoning & Analysis

```
Good                  Better                Best
│                     │                     │
Llama 3 ──> GPT-4 Turbo ──> Claude Sonnet
```

---

## 🔍 Testing Your Setup

### Quick Test

```bash
# Start your services
docker-compose up -d

# Access API docs
http://localhost:8000/docs

# Go to: POST /api/v2/ai/quick
# Test with: {"prompt": "Hello, AI!"}
```

### Test Different Models

```bash
# In API docs, try POST /api/v2/ai/models
# See all available models

# Then test each in POST /api/v2/ai/chat
```

---

## 🎓 Learn More

- **OpenRouter Docs:** https://openrouter.ai/docs
- **Model Comparison:** https://openrouter.ai/models
- **Pricing:** https://openrouter.ai/docs#models

---

## 🆘 Troubleshooting

### Error: "No AI provider configured"
- Check that `OPENROUTER_API_KEY` is set in `.env`
- Restart services: `docker-compose restart backend`

### Error: "Model not found"
- Check available models: GET `/api/v2/ai/models`
- Verify model name format: `provider/model-name`

### High costs
- Use cheaper models for simple tasks (GPT-3.5, Haiku, Llama)
- Set `max_tokens` limits
- Monitor usage in OpenRouter dashboard

---

**You're now connected to the world of AI through one unified gateway! 🚀**

