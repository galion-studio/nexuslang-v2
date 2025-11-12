# NexusLang v2 - Language Reference

**Complete reference for NexusLang v2 syntax and features**

---

## Table of Contents

1. [Basic Syntax](#basic-syntax)
2. [Variables and Types](#variables-and-types)
3. [Functions](#functions)
4. [Control Flow](#control-flow)
5. [Data Structures](#data-structures)
6. [AI-Native Features](#ai-native-features)
7. [Built-in Functions](#built-in-functions)

---

## Basic Syntax

### Comments

```nexuslang
// Single-line comment

/* Multi-line
   comment */
```

### Print Output

```nexuslang
print("Hello")
print("Value:", 42)
print("Multiple", "values", "separated")
```

---

## Variables and Types

### Variable Declaration

```nexuslang
// Mutable variable
let x = 42
let name = "Alice"
let value = 3.14

// Constant (immutable)
const PI = 3.14159
const MAX_SIZE = 1000
```

### Type Annotations (Optional)

```nexuslang
let age: int = 25
let temperature: float = 98.6
let username: string = "user123"
```

### Supported Types

- `int` - Integer numbers
- `float` - Floating-point numbers
- `string` - Text strings
- `bool` - Boolean (true/false)
- `array` - Lists of values
- `tensor` - Multi-dimensional arrays (for AI)

---

## Functions

### Function Declaration

```nexuslang
fn add(a, b) {
    return a + b
}

// With type annotations
fn multiply(a: int, b: int) -> int {
    return a * b
}
```

### Function Calls

```nexuslang
let result = add(5, 3)
print(result)  // 8
```

### Recursive Functions

```nexuslang
fn factorial(n) {
    if n <= 1 {
        return 1
    }
    return n * factorial(n - 1)
}
```

---

## Control Flow

### If-Else

```nexuslang
if x > 10 {
    print("Greater than 10")
} else if x > 5 {
    print("Greater than 5")
} else {
    print("5 or less")
}
```

### While Loops

```nexuslang
let i = 0
while i < 5 {
    print(i)
    i = i + 1
}
```

### For Loops

```nexuslang
// Iterate over array
for item in [1, 2, 3, 4, 5] {
    print(item)
}

// Range syntax
for i in 0..10 {
    print(i)
}
```

### Break and Continue

```nexuslang
for i in 0..100 {
    if i > 10 {
        break
    }
    if i % 2 == 0 {
        continue
    }
    print(i)
}
```

---

## Data Structures

### Arrays

```nexuslang
// Array literal
let numbers = [1, 2, 3, 4, 5]

// Access elements
let first = numbers[0]

// Array methods
let length = numbers.length
```

### Nested Arrays (Matrices)

```nexuslang
let matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]

let element = matrix[1][1]  // 5
```

---

## AI-Native Features

### Personality Blocks

Define how your AI thinks and behaves:

```nexuslang
personality {
    curiosity: 0.9,       // 0.0 to 1.0
    analytical: 0.8,
    creative: 0.7,
    empathetic: 0.85,
    precision: 0.95,
    verbosity: 0.6
}
```

**Personality Traits:**
- `curiosity` - How much the AI explores new solutions
- `analytical` - Systematic vs intuitive thinking
- `creative` - Novel solution generation
- `empathetic` - Understanding user needs
- `precision` - Accuracy vs speed tradeoff
- `verbosity` - Brief vs detailed explanations

### Knowledge Queries

Access universal knowledge base:

```nexuslang
// Simple query
let facts = knowledge("quantum mechanics")

// With filters
let recent = knowledge("AI", verified=true, limit=5)

// Get related topics
let related = knowledge_related("machine learning")
```

**Returns:** Array of knowledge entries with:
- `title` - Entry title
- `summary` - Brief description
- `confidence` - Accuracy score (0.0-1.0)
- `verified` - Whether fact-checked

### Voice Commands

Native text-to-speech and speech-to-text:

```nexuslang
// Text-to-speech
say("Hello world!")
say("I'm excited!", emotion="excited")
say("Speaking slowly", speed=0.8)

// Speech-to-text
let input = listen()
let response = listen(timeout=10, language="en")
```

**Say Options:**
- `emotion` - friendly, excited, thoughtful, apologetic, confident
- `voice_id` - Custom voice model ID
- `speed` - Speech speed (0.5 to 2.0)

**Listen Options:**
- `timeout` - Maximum seconds to wait
- `language` - Language code (en, es, fr, etc.)

### Confidence Scoring

Get AI confidence in predictions:

```nexuslang
let prediction = model.predict(data)
let conf = confidence(prediction)

if conf < 0.8 {
    print("Low confidence - need more data")
}
```

### Self-Optimization

Tell AI to improve itself:

```nexuslang
optimize_self(metric="accuracy", target=0.95)
```

---

## Built-in Functions

### Standard Library

```nexuslang
// Math
let abs_val = abs(-5)
let max_val = max(10, 20)
let min_val = min(5, 3)

// String
let upper = "hello".upper()
let lower = "WORLD".lower()
let length = "text".len()

// Array
let arr_len = [1, 2, 3].length
```

### AI/ML Functions

```nexuslang
// Tensors
let t = tensor([1, 2, 3])
let zeros_t = zeros(3, 3)
let ones_t = ones(2, 4)
let random_t = randn(2, 3)

// Neural Network Layers
let layer = Linear(784, 128)
let activation = ReLU()
let conv = Conv2d(3, 64, kernel_size=3)

// Models
let model = Sequential(
    Linear(10, 64),
    ReLU(),
    Linear(64, 2)
)

// Loss Functions
let loss = MSELoss()
let ce_loss = CrossEntropyLoss()

// Optimizers
let optimizer = Adam(lr=0.001)
let sgd = SGD(lr=0.01, momentum=0.9)
```

---

## Operators

### Arithmetic

```nexuslang
+ - * / %      // Add, subtract, multiply, divide, modulo
**             // Power
```

### Comparison

```nexuslang
== != < <= > >=
```

### Logical

```nexuslang
&& ||          // And, or
!              // Not
```

### Assignment

```nexuslang
=              // Assign
+= -= *= /=    // Compound assignment
```

---

## Binary Compilation

Compile your code to optimized binary format:

```bash
# Command line
nexus compile myprogram.nx --benchmark

# Shows compression ratio and speed improvement
```

**Benefits:**
- 2-3x smaller file size
- 10-15x faster AI processing
- Optimized constant pooling
- Efficient for production deployment

---

## Examples

See `v2/nexuslang/examples/` for complete working examples:

1. Hello World
2. Personality Traits
3. Knowledge Queries
4. Neural Networks
5. Binary Compilation
6. Voice Interaction
7. Loops and Arrays
8. Functions and Recursion
9. AI Decision Making
10. Complete AI Assistant
11. Error Handling
12. Tensor Operations

---

## Best Practices

### 1. Use Personality Blocks

Define AI behavior at the start of your program:

```nexuslang
personality {
    curiosity: 0.9,
    precision: 0.95
}
```

### 2. Query Knowledge When Needed

```nexuslang
// Instead of hardcoding facts
let facts = knowledge("topic")
```

### 3. Handle Errors Gracefully

```nexuslang
fn safe_divide(a, b) {
    if b == 0 {
        return null
    }
    return a / b
}
```

### 4. Use Voice for User Interaction

```nexuslang
say("Process starting...", emotion="confident")
// ... do work ...
say("Complete!", emotion="excited")
```

### 5. Compile for Production

```bash
# Development: use .nx files
nexus run myapp.nx

# Production: compile to .nxb
nexus compile myapp.nx
```

---

## Advanced Features

### Coming Soon

- Async/await for concurrent execution
- Module system for code organization
- Pattern matching
- Traits and interfaces
- GPU acceleration (CUDA/Metal)
- Distributed computing

---

## Getting Help

- **Documentation:** https://docs.nexuslang.dev
- **Examples:** Browse `v2/nexuslang/examples/`
- **Community:** https://community.nexuslang.dev
- **GitHub:** Report issues and contribute

---

**NexusLang v2** - The language AI would create for itself 🚀

