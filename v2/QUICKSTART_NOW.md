# NexusLang v2 - Quick Start Guide

**Get running in 5 minutes!**

---

## 🚀 Option 1: Development Mode (Simplest)

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git

### Step 1: Backend Setup

```bash
# Navigate to backend
cd v2/backend

# Install dependencies
pip install -r requirements.txt

# Start the server
python -m uvicorn main:app --reload --port 8000
```

**Backend will be running at:** `http://localhost:8000`  
**API Docs:** `http://localhost:8000/docs`

### Step 2: Frontend Setup

```bash
# Open new terminal
cd v2/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

**Frontend will be running at:** `http://localhost:3000`

### Step 3: Start Coding!

Open browser to `http://localhost:3000/ide`

---

## 📝 Try NexusLang v2 Features

### 1. Hello World
```nexuslang
fn main() {
    print("Hello, NexusLang v2!")
}

main()
```

### 2. Personality System
```nexuslang
personality {
    curiosity: 0.9,
    analytical: 0.8
}

fn main() {
    print("AI with personality!")
}

main()
```

### 3. Knowledge Queries
```nexuslang
fn main() {
    let facts = knowledge("AI")
    print("Found facts:", facts)
}

main()
```

### 4. Voice Commands
```nexuslang
fn main() {
    say("Hello world!", emotion="excited")
}

main()
```

---

## 🔧 Using the CLI

```bash
# Navigate to language directory
cd v2/nexuslang

# Run a file
python -m nexuslang.cli.cli run examples/01_hello_world.nx

# Compile to binary
python -m nexuslang.cli.cli compile examples/01_hello_world.nx --benchmark

# Start REPL
python -m nexuslang.cli.cli repl

# View tokens (debug)
python -m nexuslang.cli.cli tokens examples/01_hello_world.nx

# View AST (debug)
python -m nexuslang.cli.cli ast examples/01_hello_world.nx
```

---

## 📚 Example Programs

All examples are in `v2/nexuslang/examples/`:

1. `01_hello_world.nx` - Basic syntax
2. `02_personality_traits.nx` - Personality system
3. `03_knowledge_query.nx` - Knowledge base
4. `04_simple_neural_network.nx` - Build ML models
5. `05_binary_compilation.nx` - Binary optimization
6. `06_voice_interaction.nx` - Voice commands
7. `07_loops_and_arrays.nx` - Control flow
8. `08_functions_and_recursion.nx` - Functions
9. `09_ai_decision_making.nx` - Confidence scoring
10. `10_complete_ai_assistant.nx` - Full AI assistant
11. `11_error_handling.nx` - Error handling
12. `12_tensor_operations.nx` - Tensor math

---

## 🎮 IDE Keyboard Shortcuts

- **Ctrl+S** (or Cmd+S) - Save file
- **Ctrl+Enter** (or Cmd+Enter) - Run code
- **Ctrl+/** - Toggle comment

---

## 🐛 Troubleshooting

### Backend won't start?
```bash
# Make sure you're in the right directory
cd v2/backend

# Try with uvicorn directly
uvicorn main:app --reload
```

### Frontend won't start?
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Database issues?
The backend uses SQLite by default (no setup needed). For PostgreSQL:
```bash
# Install and start PostgreSQL
# Update DATABASE_URL in config.py
```

---

## 🎯 First Steps

1. **Open IDE:** `http://localhost:3000/ide`
2. **Register account** (or use existing)
3. **Try examples** - Click on example files
4. **Write code** - Use Monaco editor
5. **Run code** - Press green Run button or Ctrl+Enter
6. **Save changes** - Press Save button or Ctrl+S

---

## 📖 Learn More

- **Language Reference:** `v2/docs/LANGUAGE_REFERENCE.md` (coming soon)
- **API Documentation:** `http://localhost:8000/docs`
- **Architecture:** See `ARCHITECTURE.md`
- **Vision:** See `v2/VISION.md`

---

## 💬 Get Help

- **GitHub Issues:** Report bugs or request features
- **Discord:** Join our community (link in README)
- **Email:** team@nexuslang.dev

---

## ⚡ Pro Tips

1. **Auto-save** - IDE saves on Ctrl+S
2. **Quick run** - Use Ctrl+Enter to run instantly
3. **Examples** - Learn from included examples
4. **Binary compile** - For production, compile to .nxb
5. **REPL** - Test snippets in interactive mode

---

**Ready to build the future of AI development?** 🚀

Start coding with NexusLang v2 now!

