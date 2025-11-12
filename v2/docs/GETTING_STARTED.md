# Getting Started with NexusLang v2

**Your guide to building AI applications with NexusLang v2**

---

## What is NexusLang v2?

NexusLang v2 is an AI-native programming language designed from first principles to be:

- **Optimized for AI** - Binary compilation for 10x faster processing
- **Intelligent** - Personality system for customizable AI behavior  
- **Knowledge-aware** - Built-in access to universal knowledge base
- **Voice-first** - Native text-to-speech and speech-to-text
- **Simple** - Clean syntax, minimal boilerplate

---

## Installation

### Quick Start (5 minutes)

```bash
# Clone repository
git clone https://github.com/your-org/project-nexus.git
cd project-nexus

# Start with Docker Compose (recommended)
docker-compose up -d

# Access the IDE
open http://localhost:3000/ide
```

### Manual Installation

**Requirements:**
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+ (or SQLite for development)

**Backend:**
```bash
cd v2/backend
pip install -r requirements.txt
uvicorn main:app --reload
```

**Frontend:**
```bash
cd v2/frontend
npm install
npm run dev
```

**Language CLI:**
```bash
cd v2/nexuslang
pip install -e .
nexus --version
```

---

## Your First Program

### 1. Hello World

Create a file `hello.nx`:

```nexuslang
fn main() {
    print("Hello, NexusLang v2!")
}

main()
```

Run it:
```bash
nexus run hello.nx
```

Output:
```
Hello, NexusLang v2!
```

---

### 2. Add Personality

AI with personality traits:

```nexuslang
// Define AI behavior
personality {
    curiosity: 0.9,      // Highly curious
    analytical: 0.8,     // Systematic thinker
    creative: 0.7        // Creative problem solver
}

fn main() {
    print("I'm an AI with personality!")
}

main()
```

**Personality affects:**
- How AI approaches problems
- Code suggestions
- Error messages
- Optimization strategies

---

### 3. Query Knowledge

Access universal knowledge:

```nexuslang
fn main() {
    // Query Grokopedia
    let facts = knowledge("quantum mechanics")
    
    for fact in facts {
        print(fact["title"])
        print(fact["summary"])
    }
}

main()
```

---

### 4. Voice Interaction

Text-to-speech:

```nexuslang
fn main() {
    say("Hello! I can speak!", emotion="excited")
    say("This is amazing!", emotion="confident")
}

main()
```

---

## Core Concepts

### Functions

```nexuslang
// Simple function
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
```

### Variables

```nexuslang
// Mutable
let counter = 0
counter = counter + 1

// Immutable
const MAX_SIZE = 100
```

### Control Flow

```nexuslang
// If-else
if score > 90 {
    print("Excellent!")
} else if score > 70 {
    print("Good")
} else {
    print("Keep trying")
}

// For loops
for i in 0..5 {
    print(i)
}

// While loops
while condition {
    // code
}
```

### Arrays

```nexuslang
let numbers = [1, 2, 3, 4, 5]
let first = numbers[0]
let length = numbers.length
```

---

## AI Features

### Neural Networks

Build ML models easily:

```nexuslang
// Define a neural network
let model = Sequential(
    Linear(784, 128),  // Input layer
    ReLU(),            // Activation
    Linear(128, 64),   // Hidden layer
    ReLU(),
    Linear(64, 10),    // Output layer
    Softmax()
)

// Train (coming soon)
// model.train(data, epochs=10)

// Predict
// let output = model.forward(input)
```

### Tensors

Work with multi-dimensional arrays:

```nexuslang
// Create tensors
let t = tensor([1, 2, 3])
let matrix = tensor([[1, 2], [3, 4]])

// Special tensors
let zeros = zeros(3, 3)
let ones = ones(2, 4)
let random = randn(10, 10)

// Operations (coming soon)
// let sum = a + b
// let product = a * b
// let matmul = a @ b
```

---

## Web IDE

### Accessing the IDE

1. Open `http://localhost:3000/ide`
2. Register an account (or login)
3. Start coding!

### IDE Features

- **Monaco Editor** - Professional code editor
- **Syntax Highlighting** - NexusLang-specific
- **Auto-complete** - Intelligent suggestions
- **Run Button** - Execute code instantly
- **Save** - Auto-save to cloud
- **File Explorer** - Manage project files
- **Output Panel** - See results in real-time

### Keyboard Shortcuts

- `Ctrl+S` / `Cmd+S` - Save file
- `Ctrl+Enter` / `Cmd+Enter` - Run code
- `Ctrl+/` - Toggle comment

---

## Binary Compilation

Compile your code for production:

```bash
# Compile with benchmarking
nexus compile myprogram.nx --benchmark
```

**Output:**
```
📝 Compiling myprogram.nx...
   Source size: 1234 bytes

⏱️  Benchmarking compilation speed...
   Text parsing:   2.34ms per iteration

✅ Compilation successful!
   Output: myprogram.nxb
   Binary size: 456 bytes
   Compression ratio: 2.71x
   Compile time: 12.45ms

🚀 Estimated AI processing speedup: 13.5x faster!
```

---

## Best Practices

### 1. Structure Your Code

```nexuslang
// Import helpers (coming soon)
// from utils import helper_function

// Define personality at top
personality {
    curiosity: 0.9
}

// Helper functions
fn helper() {
    // ...
}

// Main function
fn main() {
    // Entry point
}

// Execute
main()
```

### 2. Use Comments

```nexuslang
// Explain what your code does
fn complex_algorithm() {
    // Step 1: Initialize variables
    let data = []
    
    // Step 2: Process data
    // ...
}
```

### 3. Handle Errors

```nexuslang
fn safe_operation(value) {
    if value < 0 {
        print("Error: Invalid value")
        return null
    }
    return process(value)
}
```

### 4. Query Knowledge When Needed

```nexuslang
// Instead of hardcoding information
let facts = knowledge("topic")
```

### 5. Use Voice for UX

```nexuslang
say("Starting process...", emotion="confident")
// ... do work ...
say("Complete!", emotion="excited")
```

---

## Development Workflow

### 1. Code Locally

```bash
# Edit code in IDE or text editor
# v2/frontend/app/ide opens in browser

# Or use local text editor + CLI
nexus run mycode.nx
```

### 2. Test Frequently

```bash
# Run after changes
nexus run mycode.nx

# Check for errors
nexus analyze mycode.nx
```

### 3. Save to Cloud

In the IDE:
- Changes save automatically (Ctrl+S)
- All files stored in your account
- Access from anywhere

### 4. Deploy

```bash
# Compile for production
nexus compile myapp.nx

# Deploy .nxb file
# Upload to server or share with users
```

---

## Examples to Learn From

### See All Examples
```bash
cd v2/nexuslang/examples
ls *.nx
```

### Run Examples
```bash
nexus run examples/01_hello_world.nx
nexus run examples/02_personality_traits.nx
nexus run examples/04_simple_neural_network.nx
```

### Example Topics
1. Basic syntax
2. Personality system
3. Knowledge queries
4. Neural networks
5. Binary compilation
6. Voice interaction
7. Control flow
8. Functions
9. AI decision making
10. Complete assistant
11. Error handling
12. Tensors

---

## Common Patterns

### AI Assistant Pattern

```nexuslang
personality {
    empathetic: 0.95,
    helpful: 1.0
}

fn assist_user(query) {
    let knowledge = knowledge(query)
    
    if knowledge.length > 0 {
        say("I found information!", emotion="helpful")
        return knowledge[0]
    } else {
        say("Let me research that", emotion="curious")
        return null
    }
}
```

### Model Training Pattern (Coming Soon)

```nexuslang
fn train_model() {
    let model = create_network()
    let data = load_dataset()
    
    for epoch in 0..100 {
        loss = train_step(model, data)
        print("Epoch", epoch, "Loss:", loss)
    }
    
    save_model(model, "trained_model.nxb")
}
```

---

## Next Steps

1. **Try all examples** - Run each example file
2. **Build something** - Create your first project
3. **Read language ref** - Learn all features
4. **Join community** - Share what you build
5. **Contribute** - Help improve NexusLang

---

## Resources

- **Language Reference:** `docs/LANGUAGE_REFERENCE.md`
- **API Documentation:** `docs/API_DOCUMENTATION.md`
- **Examples:** `v2/nexuslang/examples/`
- **CLI Help:** `nexus --help`
- **API Docs:** `http://localhost:8000/docs`

---

## Get Help

- **Discord:** https://discord.gg/nexuslang
- **GitHub Issues:** Report bugs
- **Email:** help@nexuslang.dev
- **Documentation:** https://docs.nexuslang.dev

---

**Welcome to the future of AI development!** 🚀

Happy coding with NexusLang v2!

