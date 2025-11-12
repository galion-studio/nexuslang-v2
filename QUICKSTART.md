# NexusLang v2 - Quick Start Guide

Get up and running with NexusLang v2 in under 5 minutes.

---

## Prerequisites

- **Docker** - For running services
- **Node.js 18+** - For frontend development
- **Python 3.11+** - For backend development
- **Git** - For version control

---

## Step 1: Clone Repository

```bash
git clone https://github.com/your-org/project-nexus.git
cd project-nexus
```

---

## Step 2: Environment Setup

Create environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
# Required API Keys
OPENAI_API_KEY=your_openai_key
SHOPIFY_API_KEY=your_shopify_key
SHOPIFY_API_SECRET=your_shopify_secret

# Database
POSTGRES_PASSWORD=secure_random_password
REDIS_PASSWORD=another_secure_password

# Application
SECRET_KEY=generate_random_secret_key
JWT_SECRET=another_random_secret
```

---

## Step 3: Start Development Environment

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

Services will be available at:

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Grokopedia:** http://localhost:3000/grokopedia
- **IDE:** http://localhost:3000/ide

---

## Step 4: Run Your First NexusLang Program

Create a file `hello.nx`:

```nexuslang
fn main() {
    print("Hello from NexusLang v2!")
    
    // AI-native features
    let model = Sequential(
        Linear(10, 64),
        ReLU(),
        Linear(64, 2)
    )
    
    print("Model created:", model)
}

main()
```

Run it:

```bash
# Using the NexusLang CLI
nexuslang run hello.nx

# Or through the web IDE
# Visit http://localhost:3000/ide
```

---

## Step 5: Explore Features

### Try the Interactive REPL

```bash
nexuslang repl
```

```nexuslang
>>> let x = tensor([1, 2, 3, 4, 5])
>>> print(x.mean())
3.0

>>> let facts = knowledge("artificial intelligence")
>>> print(facts.summary)
```

### Explore Grokopedia

Visit http://localhost:3000/grokopedia and search for any topic.

### Try Voice Features

```nexuslang
voice {
    say("Hello, I'm Galion", emotion="friendly")
}

let response = listen()
print("You said:", response)
```

---

## Development Workflow

### Frontend Development

```bash
cd v2/frontend
npm install
npm run dev
```

Frontend runs on http://localhost:3000

### Backend Development

```bash
cd v2/backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Backend API runs on http://localhost:8000

### NexusLang Development

```bash
cd v2/nexuslang
pip install -e .
nexuslang --help
```

---

## Common Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f [service-name]

# Rebuild services
docker-compose up -d --build

# Run tests
docker-compose exec backend pytest
docker-compose exec frontend npm test

# Database migrations
docker-compose exec backend alembic upgrade head

# Access database
docker-compose exec postgres psql -U nexus -d nexus_v2
```

---

## Troubleshooting

### Port Already in Use

```bash
# Check what's using the port
netstat -ano | findstr :3000  # Windows
lsof -i :3000                 # Linux/Mac

# Change ports in docker-compose.yml if needed
```

### Database Connection Issues

```bash
# Reset database
docker-compose down -v
docker-compose up -d
```

### API Keys Not Working

- Verify keys are correctly added to `.env`
- Restart services: `docker-compose restart`
- Check logs: `docker-compose logs backend`

---

## Next Steps

1. **Read the Vision** - [v2/VISION.md](v2/VISION.md)
2. **Understand Architecture** - [ARCHITECTURE.md](ARCHITECTURE.md)
3. **Browse Examples** - [v2/nexuslang/examples/](v2/nexuslang/examples/)
4. **Join Community** - https://community.nexuslang.dev
5. **Contribute** - [docs/v2/CONTRIBUTING.md](docs/v2/CONTRIBUTING.md)

---

## Getting Help

- **Documentation:** https://docs.nexuslang.dev
- **Discord:** https://discord.gg/nexuslang
- **GitHub Issues:** https://github.com/your-org/project-nexus/issues
- **Email:** support@nexuslang.dev

---

**Welcome to NexusLang v2! Let's build the future of AI development together.** 🚀

