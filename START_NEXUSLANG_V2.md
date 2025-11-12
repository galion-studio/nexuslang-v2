# 🚀 START HERE - NexusLang v2 Platform

**Quick start guide to get NexusLang v2 running in 5 minutes!**

---

## Step 1: Install Dependencies

### Backend Dependencies

```bash
cd v2/backend
pip install -r requirements.txt
```

### Frontend Dependencies

```bash
cd v2/frontend
npm install
```

### NexusLang v2

```bash
cd v2/nexuslang
pip install -r requirements.txt
pip install -e .
```

---

## Step 2: Setup Environment

```bash
# Create .env file
cp .env.example .env

# Edit .env and add:
# - POSTGRES_PASSWORD
# - REDIS_PASSWORD
# - OPENAI_API_KEY
# - SHOPIFY_API_KEY (if using billing)
```

---

## Step 3: Start Services

```bash
# From project root
docker-compose up -d

# Wait for services to start (30 seconds)
docker-compose ps

# Initialize database
docker-compose exec postgres psql -U nexus -d nexus_v2 -f /v2/database/schemas/init.sql
```

---

## Step 4: Access the Platform

### Web Applications

- **Landing Page:** http://localhost:3000
- **IDE:** http://localhost:3000/ide
- **Grokopedia:** http://localhost:3000/grokopedia
- **Community:** http://localhost:3000/community
- **Billing:** http://localhost:3000/billing

### API

- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

### Monitoring

- **Prometheus:** http://localhost:9090
- **Grafana:** http://localhost:3001

---

## Step 5: Try NexusLang v2

### Run Example Programs

```bash
cd v2/nexuslang

# Personality demo
nexuslang run examples/personality_demo.nx

# Knowledge integration
nexuslang run examples/knowledge_demo.nx

# Voice capabilities
nexuslang run examples/voice_demo.nx
```

### Interactive REPL

```bash
nexuslang repl
```

```nexuslang
>>> personality { curiosity: 0.9 }
>>> let x = tensor([1, 2, 3, 4, 5])
>>> print(x.mean())
3.0
>>> let model = Sequential(Linear(10, 5), ReLU())
>>> print(model)
```

### Compile to Binary

```bash
# Create a program
cat > test.nx << 'EOF'
fn main() {
    print("Hello from NexusLang v2!")
}
main()
EOF

# Compile to binary
nexuslang compile test.nx -o test.nxb

# Run binary (10x faster for AI)
nexuslang run test.nxb
```

---

## Common Commands

```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Restart services
docker-compose restart

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up -d --build

# Access database
docker-compose exec postgres psql -U nexus -d nexus_v2
```

---

## What You Can Do Now

### 1. Write Code in the IDE
- Visit http://localhost:3000/ide
- Write NexusLang v2 code
- Click Run to execute
- See output in terminal

### 2. Search Knowledge
- Visit http://localhost:3000/grokopedia
- Search for any topic
- Explore knowledge graph
- See verified entries

### 3. Join Community
- Visit http://localhost:3000/community
- Browse public projects
- Read discussions
- Join teams

### 4. Manage Billing
- Visit http://localhost:3000/billing
- View your plan
- Check credit balance
- Upgrade subscription

---

## Troubleshooting

### Port Already in Use

```bash
# Change ports in docker-compose.yml
# Or stop conflicting services
```

### Database Connection Failed

```bash
# Reset database
docker-compose down -v
docker-compose up -d
```

### NexusLang Command Not Found

```bash
cd v2/nexuslang
pip install -e .
```

### Frontend Won't Start

```bash
cd v2/frontend
rm -rf node_modules .next
npm install
npm run dev
```

---

## Features to Try

### AI Personality

```nexuslang
personality {
    curiosity: 0.9,
    analytical: 0.8,
    creative: 0.7
}

fn main() {
    print("AI personality configured!")
}
main()
```

### Knowledge Integration

```nexuslang
fn main() {
    let facts = knowledge("quantum physics")
    print("Found", facts.length, "facts")
}
main()
```

### Voice Synthesis

```nexuslang
fn main() {
    say("Hello from NexusLang!", emotion="friendly")
    let response = listen()
    print("You said:", response)
}
main()
```

### Binary Compilation

```bash
nexuslang compile mycode.nx -o mycode.nxb
nexuslang run mycode.nxb  # 10x faster!
```

---

## Next Steps

1. **Explore the IDE** - Write and run code
2. **Read Documentation** - Check out all the .md files
3. **Try Examples** - Run the example programs
4. **Join Community** - Share your projects
5. **Contribute** - Help build the future!

---

## Getting Help

- **Documentation:** See all .md files in project root
- **Examples:** `v2/nexuslang/examples/`
- **API Docs:** http://localhost:8000/docs
- **Issues:** GitHub Issues (coming soon)

---

🎉 **Welcome to NexusLang v2!**  
**Let's build the 22nd century together!** 🚀

