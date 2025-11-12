# 🚀 FINAL LAUNCH GUIDE - NexusLang v2 to RunPod

## ✅ What You Have Ready

- ✅ AI Router with 30+ models
- ✅ IDE AI Assistant (9 features)
- ✅ Enhanced Grokopedia
- ✅ All backend services
- ✅ Frontend ready
- ✅ RunPod environment configured

---

## 📤 UPLOAD TO RUNPOD (Choose One Method)

### Method 1: GitHub (Recommended - 5 minutes)

**Step 1: Push to GitHub**

```powershell
# In your project folder
git init
git add .
git commit -m "NexusLang v2 with AI Router"
git remote add origin YOUR_GITHUB_URL
git push -u origin main
```

**Step 2: On RunPod Jupyter Terminal**

```bash
cd /workspace
git clone YOUR_GITHUB_URL nexuslang-v2
cd nexuslang-v2
chmod +x runpod-quick-deploy.sh
./runpod-quick-deploy.sh
```

---

### Method 2: Manual Zip (10 minutes)

**Step 1: Create Zip (on PC)**

Manually zip these folders:
- `v2/backend/`
- `v2/frontend/`
- `docker-compose.runpod.yml`
- `runpod-quick-deploy.sh`
- `.env` (if you have it)
- `*.md` files

Or use 7-Zip/WinRAR to create `project.zip`

**Step 2: Upload to RunPod**

1. Open Jupyter Lab in RunPod
2. Click Upload (⬆️ button)
3. Select your zip file
4. Wait for upload (progress shown in browser)

**Step 3: Extract & Deploy**

```bash
cd /workspace
unzip project.zip -d nexuslang-v2
cd nexuslang-v2
chmod +x runpod-quick-deploy.sh
./runpod-quick-deploy.sh
```

---

## 🔧 CONFIGURE (2 minutes)

**Edit .env file:**

```bash
nano .env
```

**Add your keys:**

```bash
# Required
OPENROUTER_API_KEY=sk-or-your-key-here

# Optional
OPENAI_API_KEY=sk-your-key-here
```

Get OpenRouter key: https://openrouter.ai/keys

**Save and restart:**

```bash
docker-compose restart backend
```

---

## 🌐 EXPOSE PORTS IN RUNPOD

1. Go to RunPod Dashboard
2. Click your pod → **Edit**
3. **Add TCP Ports:**
   - `8000` → HTTP Service
   - `3000` → HTTP Service
   - `3001` → HTTP Service (optional)
4. **Save**

---

## ✨ LAUNCH & ACCESS

### Your URLs:

Replace `YOUR_POD_ID` with your actual pod ID:

- **Backend API:** `https://YOUR_POD_ID-8000.proxy.runpod.net`
- **API Docs:** `https://YOUR_POD_ID-8000.proxy.runpod.net/docs`
- **Frontend:** `https://YOUR_POD_ID-3000.proxy.runpod.net`
- **Grafana:** `https://YOUR_POD_ID-3001.proxy.runpod.net`

### Test It:

```bash
# Check health
curl http://localhost:8000/health

# View logs
docker-compose logs -f backend

# Check containers
docker-compose ps
```

---

## 🤖 TEST AI FEATURES

Visit: `https://YOUR_POD_ID-8000.proxy.runpod.net/docs`

**Try these endpoints:**

1. **GET** `/api/v2/ai/models` - See all 30+ AI models

2. **POST** `/api/v2/ai/quick` - Quick query
   ```json
   {
     "prompt": "Explain quantum computing in one sentence"
   }
   ```

3. **POST** `/api/v2/ide/ai/generate` - Generate code
   ```json
   {
     "description": "Create a hello world function",
     "language": "python"
   }
   ```

4. **POST** `/api/v2/ide/ai/explain` - Explain code
   ```json
   {
     "code": "def factorial(n): return 1 if n <= 1 else n * factorial(n-1)",
     "language": "python"
   }
   ```

---

## 📊 AVAILABLE AI MODELS

### Fast & Cheap:
- `openai/gpt-3.5-turbo` - $0.50/1M tokens
- `anthropic/claude-3-haiku` - $0.25/1M tokens
- `meta-llama/llama-3-70b-instruct` - $0.90/1M tokens

### Best Quality (Default):
- `anthropic/claude-3.5-sonnet` - $3/1M tokens
- `openai/gpt-4-turbo` - $10/1M tokens

### Specialized:
- `meta-llama/codellama-70b-instruct` - Code generation
- `perplexity/pplx-70b-online` - Has internet access!

---

## 🔍 MONITORING

### Check Status:

```bash
# Container status
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Resource usage
docker stats

# Health check
curl http://localhost:8000/health
```

### Grafana Dashboard:

Access: `https://YOUR_POD_ID-3001.proxy.runpod.net`

Username: `admin`  
Password: Check your `.env` file for `GRAFANA_PASSWORD`

---

## 🆘 TROUBLESHOOTING

### Upload Issues:
- **Slow upload?** Use GitHub method instead
- **Zip too large?** Only include `v2/` folder
- **Upload fails?** Split into smaller zips

### Deployment Issues:

```bash
# Check Docker
docker --version
docker-compose --version

# Restart everything
docker-compose down
docker-compose up -d --build

# Check logs for errors
docker-compose logs backend | tail -50
```

### AI Not Working:

```bash
# Check .env has API key
cat .env | grep OPENROUTER_API_KEY

# Restart backend
docker-compose restart backend

# Check logs
docker-compose logs backend | grep -i "ai\|openrouter"
```

### Can't Access URLs:

1. Expose ports in RunPod Dashboard
2. Wait 1-2 minutes after exposing
3. Try with pod ID from dashboard
4. Check services are running: `docker-compose ps`

---

## 📋 QUICK COMMANDS

```bash
# Navigate to project
cd /workspace/nexuslang-v2

# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart a service
docker-compose restart backend

# View logs
docker-compose logs -f

# Check status
docker-compose ps

# Update from git
git pull
docker-compose restart backend

# Clean everything
docker-compose down -v
```

---

## 🎉 YOU'RE LIVE!

Once everything is running:

✅ **Backend** - Processing AI requests  
✅ **Frontend** - User interface  
✅ **30+ AI Models** - Ready to use  
✅ **IDE AI Assistant** - Code help  
✅ **Monitoring** - Grafana dashboards

---

## 📚 DOCUMENTATION

- **AI Router Guide:** `AI_ROUTER_GUIDE.md`
- **Implementation:** `🎉_AI_IMPLEMENTATION_COMPLETE.md`
- **RunPod Quick Start:** `RUNPOD_QUICK_START.md`
- **Upload Options:** `QUICK_UPLOAD_OPTIONS.md`

---

## 💡 NEXT STEPS

1. ✅ Upload to RunPod (GitHub or Zip)
2. ✅ Add OPENROUTER_API_KEY to .env
3. ✅ Expose ports (8000, 3000, 3001)
4. ✅ Test endpoints at /docs
5. ✅ Build amazing AI features!

---

## 🚀 ESTIMATED TIME

- Upload: 5-10 minutes
- Deploy: 3-5 minutes
- Configure: 2 minutes
- **Total: ~15 minutes to live!**

---

**Your NexusLang v2 platform with AI is ready to launch! 🎉**

**Choose your upload method and go! 🚀**

