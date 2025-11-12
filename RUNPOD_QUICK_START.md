# 🚀 RunPod Quick Start - NexusLang v2 with AI

## One-Command Deploy

```bash
cd /workspace
git clone YOUR_REPO_URL project-nexus
cd project-nexus
chmod +x runpod-quick-deploy.sh
./runpod-quick-deploy.sh
```

## Configure AI

```bash
nano .env
# Add: OPENROUTER_API_KEY=sk-or-your-key-here
# Get from: https://openrouter.ai/keys

docker-compose restart backend
```

## Access

- **API:** `https://YOUR_POD_ID-8000.proxy.runpod.net`
- **Docs:** `https://YOUR_POD_ID-8000.proxy.runpod.net/docs`
- **Frontend:** `https://YOUR_POD_ID-3000.proxy.runpod.net`

## Expose Ports in RunPod

1. Go to RunPod Dashboard
2. Click your pod → Edit
3. Add TCP ports: `8000`, `3000`, `3001`
4. Save

## Test AI

```bash
curl https://YOUR_POD_ID-8000.proxy.runpod.net/health
```

Then visit `/docs` and try:
- `GET /api/v2/ai/models` - See 30+ AI models
- `POST /api/v2/ai/quick` - Test AI query

## Available AI Models

**Fast & Cheap:**
- `openai/gpt-3.5-turbo` - $0.50/1M tokens
- `anthropic/claude-3-haiku` - $0.25/1M tokens
- `meta-llama/llama-3-70b-instruct` - $0.90/1M tokens

**Best Quality:**
- `anthropic/claude-3.5-sonnet` - $3/1M (DEFAULT)
- `openai/gpt-4-turbo` - $10/1M (FALLBACK)

**Specialized:**
- `meta-llama/codellama-70b-instruct` - Code generation
- `perplexity/pplx-70b-online` - Has internet access

## Logs

```bash
docker-compose logs -f backend
```

## Stop

```bash
docker-compose down
```

## Troubleshooting

**Can't access:** Expose ports in RunPod Dashboard

**AI not working:** Add OPENROUTER_API_KEY to .env

**Out of memory:** Reduce workers in docker-compose

## Docs

- Full guide: `AI_ROUTER_GUIDE.md`
- Implementation: `🎉_AI_IMPLEMENTATION_COMPLETE.md`

**Done! Your AI-powered platform is running! 🎉**

