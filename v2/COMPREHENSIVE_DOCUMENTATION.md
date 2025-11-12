# 📚 NexusLang v2 - Comprehensive Documentation

**Complete technical reference for NexusLang v2 platform**

**Last Updated:** November 11, 2025  
**Version:** 2.0.0-beta  
**Platform:** https://developer.galion.app

---

## 📋 Table of Contents

1. [Platform Overview](#platform-overview)
2. [Language Specification](#language-specification)
3. [API Reference](#api-reference)
4. [Deployment Guide](#deployment-guide)
5. [Development Guide](#development-guide)
6. [Security & Best Practices](#security)
7. [Troubleshooting](#troubleshooting)

---

## 1. Platform Overview

### What is NexusLang v2?

NexusLang v2 is an AI-native programming language designed from first principles to be:

**Optimized for AI:**
- Binary compilation for 10-15x faster processing
- Native tensor operations
- GPU-ready architecture

**Intelligent:**
- Personality system for customizable AI behavior
- Confidence scoring for decisions
- Self-optimization capabilities

**Knowledge-Aware:**
- Built-in access to universal knowledge base (Grokopedia)
- Verified, confidence-scored facts
- Related concept discovery

**Voice-First:**
- Native text-to-speech (say function)
- Native speech-to-text (listen function)
- Emotion and tone control

---

## 2. Language Specification

### 2.1 Syntax Overview

**File Extension:** `.nx` (source), `.nxb` (binary)

**Basic Structure:**
```nexuslang
// Optional personality definition
personality {
    trait_name: value  // 0.0 to 1.0
}

// Function definitions
fn function_name(params) {
    // function body
}

// Main execution
function_name()
```

### 2.2 Data Types

**Primitive Types:**
- `int` - Integer numbers (e.g., 42, -10)
- `float` - Floating-point numbers (e.g., 3.14, -0.5)
- `string` - Text strings (e.g., "hello")
- `bool` - Boolean values (true, false)

**Composite Types:**
- `array` - Ordered collections (e.g., [1, 2, 3])
- `tensor` - Multi-dimensional arrays for ML

**AI Types:**
- `model` - Neural network models
- `personality` - AI behavior configuration

### 2.3 Variables

```nexuslang
// Mutable variable
let x = 42
x = 50  // OK

// Immutable constant
const PI = 3.14159
// PI = 3.14  // Error!

// Type annotations (optional)
let age: int = 25
let name: string = "Alice"
```

### 2.4 Functions

```nexuslang
// Basic function
fn greet(name) {
    print("Hello,", name)
}

// With return value
fn add(a, b) {
    return a + b
}

// With type annotations
fn multiply(a: int, b: int) -> int {
    return a * b
}

// Recursive function
fn factorial(n) {
    if n <= 1 { return 1 }
    return n * factorial(n - 1)
}
```

### 2.5 Control Flow

**If-Else:**
```nexuslang
if condition {
    // code
} else if other_condition {
    // code
} else {
    // code
}
```

**Loops:**
```nexuslang
// For loop with range
for i in 0..10 {
    print(i)
}

// For loop with array
for item in [1, 2, 3] {
    print(item)
}

// While loop
while condition {
    // code
}
```

**Break and Continue:**
```nexuslang
for i in 0..100 {
    if i > 10 { break }
    if i % 2 == 0 { continue }
    print(i)
}
```

### 2.6 AI-Native Features

#### Personality Blocks

```nexuslang
personality {
    curiosity: 0.9,       // How much AI explores (0.0-1.0)
    analytical: 0.8,      // Systematic vs intuitive
    creative: 0.7,        // Novel solution generation
    empathetic: 0.85,     // Understanding user needs
    precision: 0.95,      // Accuracy vs speed tradeoff
    verbosity: 0.6        // Brief vs detailed output
}
```

**Personality affects:**
- Problem-solving approach
- Code suggestions
- Error messages
- Optimization strategies

#### Knowledge Queries

```nexuslang
// Simple query
let facts = knowledge("quantum mechanics")

// With filters
let verified_facts = knowledge("AI", verified=true, limit=5)

// Related concepts
let related = knowledge_related("machine learning")

// Fact structure:
// {
//   "title": "Fact title",
//   "summary": "Brief description",
//   "confidence": 0.95,
//   "verified": true
// }
```

#### Voice Commands

```nexuslang
// Text-to-speech
say("Hello world!")
say("I'm excited!", emotion="excited")
say("Speaking slowly...", speed=0.8)

// Supported emotions:
// friendly, excited, thoughtful, apologetic, confident

// Speech-to-text
let user_input = listen()
let response = listen(timeout=10, language="en")
```

#### Confidence Scoring

```nexuslang
let prediction = model.predict(data)
let conf = confidence(prediction)

if conf < 0.8 {
    print("Low confidence - need more data")
}
```

#### Self-Optimization

```nexuslang
// Tell AI to optimize itself
optimize_self(metric="accuracy", target=0.95)
```

### 2.7 ML/AI Built-ins

**Tensors:**
```nexuslang
let t = tensor([1, 2, 3])
let zeros = zeros(3, 3)
let random = randn(10, 10)
```

**Neural Network Layers:**
```nexuslang
let linear = Linear(784, 128)
let activation = ReLU()
let conv = Conv2d(3, 64, kernel_size=3)
```

**Models:**
```nexuslang
let model = Sequential(
    Linear(784, 256),
    ReLU(),
    Linear(256, 128),
    ReLU(),
    Linear(128, 10),
    Softmax()
)
```

---

## 3. API Reference

### Base URL
```
Production: https://api.developer.galion.app/api/v2
Local: http://localhost:8100/api/v2
```

### Authentication

All protected endpoints require JWT token:
```
Authorization: Bearer <your_jwt_token>
```

### Endpoints Summary

**Authentication:**
- `POST /auth/register` - Create account
- `POST /auth/login` - Get JWT token
- `GET /auth/me` - Current user info

**Code Execution:**
- `POST /nexuslang/run` - Execute code
- `POST /nexuslang/compile` - Compile to binary
- `POST /nexuslang/analyze` - Code analysis
- `GET /nexuslang/examples` - Get examples

**Projects:**
- `GET /ide/projects` - List projects
- `POST /ide/projects` - Create project
- `GET /ide/projects/{id}` - Get project
- `PUT /ide/projects/{id}` - Update project
- `DELETE /ide/projects/{id}` - Delete project

**Files:**
- `GET /ide/projects/{id}/files` - List files
- `POST /ide/projects/{id}/files` - Create file
- `GET /ide/files/{id}` - Get file
- `PUT /ide/files/{id}` - Update file (save)
- `DELETE /ide/files/{id}` - Delete file

**Full API Docs:** https://api.developer.galion.app/docs

---

## 4. Deployment Guide

### RunPod Deployment (Production)

**Current Setup:**
- **Platform:** RunPod (galion-nexus pod)
- **Frontend:** Port 3100 → https://developer.galion.app
- **Backend:** Port 8100 → https://api.developer.galion.app
- **Database:** Shared PostgreSQL (galion-postgres)
- **Cache:** Shared Redis (galion-redis, DB 1)

**Deployment Command:**
```bash
cd /workspace/project-nexus/v2
./deploy-nexuslang-to-runpod.sh
```

**Port Configuration:**
- Galion.app: Ports 3000/8000 (existing)
- NexusLang v2: Ports 3100/8100 (new)
- No conflicts!

### Docker Compose

**File:** `docker-compose.nexuslang.yml`

**Services:**
- `nexuslang-backend` - FastAPI application
- `nexuslang-frontend` - Next.js application

**Shared Resources:**
- PostgreSQL (separate database: nexuslang_v2)
- Redis (separate DB number: 1)
- Network: galion-network

---

## 5. Development Guide

### Project Structure

```
v2/
├── nexuslang/              # Language implementation
│   ├── lexer/              # Tokenization
│   ├── parser/             # AST generation
│   ├── interpreter/        # Execution engine
│   ├── compiler/           # Binary compilation
│   ├── runtime/            # Built-in functions
│   ├── syntax_tree/        # AST definitions
│   ├── cli/                # Command-line tools
│   ├── examples/           # Example programs
│   └── tests/              # Test suites
│
├── backend/                # API server
│   ├── api/                # REST endpoints
│   ├── core/               # Config, database, security
│   ├── models/             # Database models
│   └── services/           # Business logic
│
├── frontend/               # Web application
│   ├── app/                # Pages and routing
│   ├── components/         # React components
│   └── lib/                # API client
│
├── database/               # Database schemas
└── docs/                   # Documentation
```

### Development Workflow

```bash
# 1. Make changes to code
# 2. Test locally
nexus run mycode.nx

# 3. Run tests
cd nexuslang
python tests/run_all_tests.py

# 4. Commit changes
git add .
git commit -m "Description"

# 5. Push to GitHub
git push origin main

# 6. Deploy to RunPod
ssh into RunPod
git pull
restart services
```

---

## 6. Security

### Authentication Flow

1. User registers → Password hashed with bcrypt
2. User logs in → JWT token generated (24h expiration)
3. Token sent with requests → Verified on backend
4. User data accessed → Based on token claims

### Code Execution Safety

**Sandboxing:**
- Timeout: 10 seconds max
- Memory limit: 512MB
- Output size: 100KB max
- Isolated environment

**Input Validation:**
- Code length limits
- SQL injection protection
- XSS prevention
- CORS restrictions

---

## 7. Troubleshooting

### Common Issues

**Backend won't start:**
```bash
# Check logs
docker logs nexuslang-backend

# Verify dependencies
pip list | grep fastapi

# Restart
pkill uvicorn
uvicorn main:app --host 0.0.0.0 --port 8100 &
```

**Frontend 404 errors:**
```bash
# Check if server running
netstat -tlnp | grep 3100

# Restart
pkill -f "http.server 3100"
python3 -m http.server 3100 &
```

**Database connection fails:**
```bash
# Check PostgreSQL
docker ps | grep postgres

# Test connection
psql -h galion-postgres -U nexus -d nexuslang_v2
```

---

## 📞 Contact & Support

**For questions:**
- Email: support@galion.app
- GitHub: https://github.com/galion-studio/project-nexus
- Platform: https://developer.galion.app

---

**🚀 Happy coding with NexusLang v2!**

