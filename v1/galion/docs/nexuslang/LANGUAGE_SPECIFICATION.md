# NexusLang Language Specification v1.0

**Status:** Draft  
**Version:** 1.0.0  
**Date:** November 9, 2025  
**Philosophy:** First Principles - Question, Delete, Simplify, Accelerate, Automate

---

## Executive Summary

NexusLang is a multi-paradigm programming language designed for the Nexus ecosystem, combining:
- **Domain-Specific** capabilities for Galion workflow definitions
- **General-Purpose** system programming features
- **Configuration/Scripting** for automation and deployment
- **AI-Focused** syntax for ML operations and model training

**Key Design Goals:**
1. **Simplicity** - Easy to learn, clear syntax, minimal keywords
2. **Safety** - Strong type system with compile-time checks
3. **Performance** - JIT compilation, efficient runtime, low memory footprint
4. **Interoperability** - Seamless integration with Python, Go, JavaScript
5. **AI-Native** - Built-in support for tensors, models, pipelines

---

## 1. Language Fundamentals

### 1.1 Syntax Philosophy

**First Principles Applied:**
- **Question:** Do we need complex syntax like C++? **NO** - Use clean, Python-like syntax
- **Delete:** Remove semicolons, verbose declarations, boilerplate
- **Simplify:** One obvious way to do things, minimal syntax variations
- **Accelerate:** Fast compilation, instant feedback, JIT optimization
- **Automate:** Automatic memory management, type inference, optimization

### 1.2 File Structure

```nexuslang
// File extension: .nx
// Encoding: UTF-8
// Line endings: LF (Unix-style)

// Module declaration (optional, inferred from directory structure)
module galion.workflow

// Imports
import nexus.core
import nexus.ai.models
from galion import Task, Workflow

// Code follows...
```

### 1.3 Comments

```nexuslang
// Single-line comment

/* 
 * Multi-line comment
 * Supports markdown formatting
 */

/// Documentation comment (generates docs)
/// @param name: The workflow name
/// @returns: Workflow instance
```

---

## 2. Type System

### 2.1 Primitive Types

```nexuslang
// Integers
int8, int16, int32, int64       // Signed integers
uint8, uint16, uint32, uint64   // Unsigned integers
int                              // Platform-dependent (64-bit default)

// Floating Point
float32, float64                 // IEEE 754
float                            // Alias for float64

// Boolean
bool                             // true or false

// String
string                           // UTF-8 encoded, immutable
char                             // Single Unicode character

// Special
void                             // No value
any                              // Dynamic type (use sparingly)
never                            // Function never returns
```

### 2.2 Composite Types

```nexuslang
// Arrays (fixed size)
array<T, N>                      // Fixed-size array
int[5]                           // Shorthand: array of 5 ints

// Slices (dynamic size)
slice<T>                         // Dynamic array
[]int                            // Shorthand: slice of ints

// Maps
map<K, V>                        // Hash map
map<string, int>                 // String to int mapping

// Tuples
tuple<T1, T2, T3>                // Fixed-size heterogeneous
(string, int, bool)              // Shorthand tuple

// Optionals
optional<T>                      // May be null
int?                             // Shorthand: optional int
```

### 2.3 AI-Native Types

```nexuslang
// Tensors (first-class citizens)
tensor<dtype, shape>             // Multi-dimensional array
tensor<float32, [3, 224, 224]>   // Image tensor

// Models
model<InputType, OutputType>     // ML model type
model<tensor<float32>, string>   // Image classifier

// Datasets
dataset<T>                       // Lazy-loaded data stream
dataset<(image: tensor, label: string)>

// Pipelines
pipeline<In, Out>                // Data processing pipeline
pipeline<string, tensor<float32>>  // Text to embeddings
```

---

## 3. Variables & Constants

### 3.1 Variable Declaration

```nexuslang
// Mutable variables
let x: int = 42
let y = 3.14              // Type inference
let name: string          // Declaration without initialization (default: "")

// Immutable constants
const PI = 3.14159
const MAX_USERS: int = 1000

// Multiple declarations
let (a, b, c) = (1, 2, 3)
let x, y: int             // Both are int
```

### 3.2 Type Inference

```nexuslang
// Compiler infers types from context
let count = 0             // int
let ratio = 0.5           // float64
let name = "Nexus"        // string
let items = [1, 2, 3]     // []int

// Function return type inference
fn add(a: int, b: int) {
    return a + b          // Returns int (inferred)
}
```

---

## 4. Functions

### 4.1 Function Declaration

```nexuslang
// Basic function
fn greet(name: string) -> string {
    return "Hello, " + name
}

// Multiple parameters
fn calculate(x: int, y: int, op: string) -> int {
    match op {
        "add" => x + y
        "sub" => x - y
        else => 0
    }
}

// No return value
fn log(message: string) {
    print(message)
}

// Multiple return values
fn divmod(a: int, b: int) -> (int, int) {
    return (a / b, a % b)
}
```

### 4.2 Higher-Order Functions

```nexuslang
// Functions as first-class citizens
fn apply(f: fn(int) -> int, x: int) -> int {
    return f(x)
}

let double = fn(x: int) -> int { x * 2 }
let result = apply(double, 5)  // 10

// Closures
fn makeAdder(x: int) -> fn(int) -> int {
    return fn(y: int) -> int { x + y }
}

let add5 = makeAdder(5)
print(add5(3))  // 8
```

### 4.3 Async Functions

```nexuslang
// Async/await for concurrent operations
async fn fetchUser(id: int) -> User {
    let response = await http.get("/users/" + id)
    return response.json()
}

// Parallel execution
async fn loadData() {
    let (users, posts) = await parallel(
        fetchUsers(),
        fetchPosts()
    )
}
```

---

## 5. Control Flow

### 5.1 Conditionals

```nexuslang
// If-else
if x > 0 {
    print("positive")
} else if x < 0 {
    print("negative")
} else {
    print("zero")
}

// Ternary expression
let sign = x > 0 ? "positive" : "negative"

// If as expression
let result = if condition { value1 } else { value2 }
```

### 5.2 Pattern Matching

```nexuslang
// Match statement (exhaustive)
match value {
    0 => print("zero")
    1..10 => print("small")
    11..100 => print("medium")
    else => print("large")
}

// Match with destructuring
match point {
    (0, 0) => print("origin")
    (x, 0) => print("on x-axis: " + x)
    (0, y) => print("on y-axis: " + y)
    (x, y) => print("point: " + x + ", " + y)
}

// Match with type patterns
match value {
    x: int => print("integer: " + x)
    s: string => print("string: " + s)
    else => print("unknown type")
}
```

### 5.3 Loops

```nexuslang
// For loop (range-based)
for i in 0..10 {
    print(i)
}

// For-each loop
for item in items {
    print(item)
}

// While loop
while condition {
    // body
}

// Loop with break/continue
for i in 0..100 {
    if i % 2 == 0 { continue }
    if i > 50 { break }
    print(i)
}
```

---

## 6. Object-Oriented Features

### 6.1 Structs

```nexuslang
// Struct definition
struct User {
    id: int
    name: string
    email: string
    created_at: timestamp
}

// Constructor
let user = User {
    id: 1,
    name: "Alice",
    email: "alice@example.com",
    created_at: now()
}

// Methods
impl User {
    fn fullName(self) -> string {
        return self.name
    }
    
    fn isAdmin(self) -> bool {
        return self.id == 1
    }
}
```

### 6.2 Interfaces (Traits)

```nexuslang
// Interface definition
interface Drawable {
    fn draw(self)
    fn area(self) -> float
}

// Implementation
struct Circle {
    radius: float
}

impl Drawable for Circle {
    fn draw(self) {
        print("Drawing circle with radius " + self.radius)
    }
    
    fn area(self) -> float {
        return 3.14159 * self.radius * self.radius
    }
}
```

### 6.3 Enums

```nexuslang
// Simple enum
enum Status {
    Pending
    Active
    Completed
    Failed
}

// Enum with associated values
enum Result<T, E> {
    Ok(T)
    Err(E)
}

// Pattern matching with enums
match result {
    Ok(value) => print("Success: " + value)
    Err(error) => print("Error: " + error)
}
```

---

## 7. AI-Specific Features

### 7.1 Tensor Operations

```nexuslang
// Tensor creation
let t1 = tensor<float32>([1, 2, 3, 4])
let t2 = tensor.zeros<float32>([3, 3])
let t3 = tensor.randn<float32>([64, 128])

// Tensor operations (NumPy-like)
let sum = t1 + t2
let product = t1 * t2
let matmul = t1 @ t2      // Matrix multiplication
let transpose = t1.T

// Slicing
let slice = t1[0:10, :]
let element = t1[5, 3]
```

### 7.2 Model Definition

```nexuslang
// Define ML model
model ImageClassifier {
    conv1: Conv2d(3, 64, kernel_size: 3)
    conv2: Conv2d(64, 128, kernel_size: 3)
    fc1: Linear(128 * 56 * 56, 1000)
    fc2: Linear(1000, 10)
    
    fn forward(self, x: tensor<float32>) -> tensor<float32> {
        let x = self.conv1(x).relu()
        let x = self.conv2(x).relu()
        let x = x.flatten()
        let x = self.fc1(x).relu()
        return self.fc2(x).softmax()
    }
}

// Instantiate and use
let model = ImageClassifier()
let output = model.forward(input_tensor)
```

### 7.3 Training Pipeline

```nexuslang
// Training loop (declarative)
train model on dataset {
    epochs: 10
    batch_size: 32
    optimizer: Adam(lr: 0.001)
    loss: CrossEntropyLoss()
    
    on_batch_end: fn(batch_idx, loss) {
        if batch_idx % 100 == 0 {
            print("Batch " + batch_idx + ", Loss: " + loss)
        }
    }
    
    on_epoch_end: fn(epoch, metrics) {
        print("Epoch " + epoch + " complete")
        print("Accuracy: " + metrics.accuracy)
    }
}
```

---

## 8. Domain-Specific Language (DSL) Features

### 8.1 Workflow Definition

```nexuslang
// Galion workflow DSL
workflow BuildFeature {
    description: "Build and deploy new feature"
    
    task("Design") {
        assignee: role("Designer")
        estimated_hours: 8
        hourly_rate: 100
        
        on_complete: {
            notify(slack, "#design")
            transition_to("Development")
        }
    }
    
    task("Development") {
        depends_on: ["Design"]
        assignee: role("Developer")
        estimated_hours: 40
        hourly_rate: 120
        
        subtasks: [
            "Setup environment",
            "Write code",
            "Write tests"
        ]
    }
    
    task("Review") {
        depends_on: ["Development"]
        assignee: role("TechLead")
        estimated_hours: 4
        hourly_rate: 150
    }
}
```

### 8.2 API Route Definition

```nexuslang
// REST API DSL
api UserAPI {
    base_path: "/api/v1/users"
    
    route GET "/{id}" {
        auth: required
        rate_limit: 100 per minute
        
        handler: async fn(id: int) -> Result<User, Error> {
            let user = await db.users.find(id)
            return user ?? Err("User not found")
        }
    }
    
    route POST "/" {
        auth: required
        body: UserCreate
        
        handler: async fn(data: UserCreate) -> Result<User, Error> {
            validate(data)
            let user = await db.users.create(data)
            await events.publish("user.created", user)
            return Ok(user)
        }
    }
}
```

---

## 9. Error Handling

### 9.1 Result Type

```nexuslang
// Result type for error handling
enum Result<T, E> {
    Ok(T)
    Err(E)
}

fn divide(a: int, b: int) -> Result<int, string> {
    if b == 0 {
        return Err("Division by zero")
    }
    return Ok(a / b)
}

// Using results
let result = divide(10, 2)
match result {
    Ok(value) => print("Result: " + value)
    Err(error) => print("Error: " + error)
}
```

### 9.2 Try/Catch

```nexuslang
// Exception handling
try {
    let file = fs.open("data.txt")
    let content = file.read()
    print(content)
} catch error: IOError {
    print("IO Error: " + error.message)
} catch error {
    print("Unknown error: " + error)
} finally {
    // Always executed
    file.close()
}
```

### 9.3 Error Propagation

```nexuslang
// ? operator for error propagation
fn loadConfig() -> Result<Config, Error> {
    let content = fs.read("config.json")?  // Propagate error
    let config = json.parse(content)?      // Propagate error
    return Ok(config)
}
```

---

## 10. Concurrency & Parallelism

### 10.1 Async/Await

```nexuslang
// Asynchronous programming
async fn fetchData() -> string {
    let response = await http.get("https://api.example.com")
    return response.text()
}

// Parallel execution
async fn loadAllData() {
    let results = await parallel([
        fetchUsers(),
        fetchPosts(),
        fetchComments()
    ])
    return results
}
```

### 10.2 Channels

```nexuslang
// Go-style channels
let ch = channel<int>(buffer_size: 10)

// Send to channel
spawn {
    for i in 0..100 {
        ch.send(i)
    }
    ch.close()
}

// Receive from channel
for value in ch {
    print(value)
}
```

### 10.3 Actors

```nexuslang
// Actor model for concurrent state management
actor Counter {
    let mut count: int = 0
    
    fn increment(self) {
        self.count += 1
    }
    
    fn get(self) -> int {
        return self.count
    }
}

let counter = spawn Counter()
counter.send(increment)
let value = await counter.ask(get)
```

---

## 11. Interoperability

### 11.1 Python Integration

```nexuslang
// Call Python code
import python

let np = python.import("numpy")
let array = np.array([1, 2, 3, 4])
let mean = np.mean(array)

// Define Python function in NexusLang
@python
fn process_data(data: any) -> any {
    """
    import pandas as pd
    df = pd.DataFrame(data)
    return df.describe()
    """
}
```

### 11.2 Go Integration

```nexuslang
// Call Go code
import go

@go
fn highPerformanceTask(data: []byte) -> []byte {
    """
    // Go code here
    result := processData(data)
    return result
    """
}
```

### 11.3 C/C++ Integration (FFI)

```nexuslang
// Foreign Function Interface
extern "C" {
    fn malloc(size: usize) -> *void
    fn free(ptr: *void)
}

// Use C functions
let ptr = malloc(1024)
// ... use ptr
free(ptr)
```

---

## 12. Memory Management

### 12.1 Ownership & Borrowing (Rust-inspired)

```nexuslang
// Ownership
let s1 = "hello"
let s2 = s1           // s1 moved to s2, s1 invalid

// Borrowing (reference)
fn length(s: &string) -> int {
    return s.len()
}

let s = "hello"
let len = length(&s)  // s still valid after call

// Mutable borrowing
fn append(s: &mut string, suffix: string) {
    s += suffix
}
```

### 12.2 Garbage Collection

```nexuslang
// Automatic GC for types without ownership semantics
let list = [1, 2, 3, 4, 5]
let dict = {"key": "value"}
// Automatically freed when out of scope
```

---

## 13. Modules & Packages

### 13.1 Module System

```nexuslang
// File: math/geometry.nx
module math.geometry

export struct Point {
    x: float
    y: float
}

export fn distance(p1: Point, p2: Point) -> float {
    let dx = p1.x - p2.x
    let dy = p1.y - p2.y
    return sqrt(dx * dx + dy * dy)
}

// Private function (not exported)
fn helper() {
    // ...
}
```

### 13.2 Package Management

```nexuslang
// nexus.toml (package manifest)
[package]
name = "my-project"
version = "1.0.0"
authors = ["Your Name"]

[dependencies]
nexus-core = "2.0"
nexus-ai = "1.5"
galion = "3.0"

[dev-dependencies]
nexus-test = "1.0"
```

---

## 14. Standard Library

### 14.1 Core Modules

```nexuslang
// Built-in modules
import nexus.core          // Core utilities
import nexus.io            // I/O operations
import nexus.net           // Networking
import nexus.fs            // File system
import nexus.time          // Time/date
import nexus.json          // JSON parsing
import nexus.http          // HTTP client/server
import nexus.crypto        // Cryptography
import nexus.testing       // Testing framework
```

### 14.2 AI Modules

```nexuslang
import nexus.ai.models     // Pre-trained models
import nexus.ai.tensor     // Tensor operations
import nexus.ai.training   // Training utilities
import nexus.ai.inference  // Inference engine
import nexus.ai.vision     // Computer vision
import nexus.ai.nlp        // Natural language processing
import nexus.ai.voice      // Speech processing
```

---

## 15. Compilation & Execution

### 15.1 Compiler Pipeline

```
Source Code (.nx)
    ↓
Lexer (Tokenization)
    ↓
Parser (AST Generation)
    ↓
Semantic Analysis (Type Checking)
    ↓
IR Generation (LLVM IR / Custom IR)
    ↓
Optimization Passes
    ↓
Code Generation
    ↓
Machine Code / Bytecode
```

### 15.2 Execution Modes

```bash
# Interpreted mode (fast startup)
nexus run main.nx

# JIT compilation (balance)
nexus run --jit main.nx

# AOT compilation (best performance)
nexus build main.nx -o binary
./binary

# REPL (interactive)
nexus repl
```

---

## 16. Tooling

### 16.1 CLI Tools

```bash
# Create new project
nexus new my-project

# Build project
nexus build

# Run project
nexus run

# Test project
nexus test

# Format code
nexus fmt

# Lint code
nexus lint

# Package manager
nexus install package-name
nexus update
```

### 16.2 IDE Integration

- **VS Code Extension** - Syntax highlighting, IntelliSense, debugging
- **LSP Server** - Language Server Protocol for any editor
- **Debugger** - GDB-compatible debugger
- **Profiler** - Performance profiling tools

---

## 17. Performance Characteristics

### 17.1 Design Goals

- **Startup Time:** <10ms (interpreted), <1ms (compiled)
- **Memory Overhead:** <5MB runtime
- **Compilation Speed:** >100K lines/second
- **Runtime Performance:** Within 2x of C/Go for compute-intensive tasks

### 17.2 Optimization Strategies

- **JIT Compilation:** Hot path optimization
- **Escape Analysis:** Stack allocation when possible
- **Inline Expansion:** Function inlining
- **SIMD:** Automatic vectorization
- **Zero-Cost Abstractions:** No overhead for language features

---

## 18. Security Features

### 18.1 Memory Safety

- **No buffer overflows** - Bounds checking on arrays
- **No null pointer dereference** - Optional types
- **No use-after-free** - Ownership system
- **No data races** - Borrow checker

### 18.2 Cryptographic Primitives

```nexuslang
import nexus.crypto

// Hashing
let hash = crypto.sha256("message")

// Encryption
let encrypted = crypto.aes256_gcm.encrypt(data, key)
let decrypted = crypto.aes256_gcm.decrypt(encrypted, key)

// Digital signatures
let signature = crypto.ed25519.sign(message, private_key)
let valid = crypto.ed25519.verify(message, signature, public_key)
```

---

## 19. Testing Framework

### 19.1 Unit Tests

```nexuslang
import nexus.testing

test "addition works correctly" {
    assert 1 + 1 == 2
    assert 2 + 2 == 4
}

test "division by zero fails" {
    let result = divide(10, 0)
    assert result.is_err()
}
```

### 19.2 Integration Tests

```nexuslang
integration_test "API endpoint" {
    let client = http.client()
    let response = await client.get("/api/users")
    
    assert response.status == 200
    assert response.json().users.len() > 0
}
```

---

## 20. Future Extensions

### 20.1 Planned Features

- **Macros & Metaprogramming** - Compile-time code generation
- **Distributed Computing** - Built-in cluster support
- **Formal Verification** - Proof-checking for critical code
- **GPU Kernels** - CUDA-like GPU programming
- **Web Assembly Target** - Compile to WASM

### 20.2 Research Areas

- **Dependent Types** - More expressive type system
- **Effect System** - Track side effects in types
- **Linear Types** - Resource management
- **Gradual Typing** - Mix static and dynamic typing

---

## Appendices

### A. Grammar (EBNF)

```ebnf
program        ::= module_decl? import_stmt* item*
module_decl    ::= "module" IDENT ("." IDENT)*
import_stmt    ::= "import" IDENT ("." IDENT)* ("as" IDENT)?
item           ::= fn_def | struct_def | enum_def | const_def | impl_block
fn_def         ::= "fn" IDENT "(" params? ")" ("->" type)? block
struct_def     ::= "struct" IDENT "{" field_list "}"
enum_def       ::= "enum" IDENT "{" enum_variant_list "}"
```

### B. Keyword List

```
Keywords (Reserved):
async, await, break, const, continue, else, enum, export, 
extern, false, fn, for, if, impl, import, in, interface, 
let, match, model, module, mut, return, self, spawn, struct, 
test, trait, true, try, type, use, while, workflow

Contextual Keywords (Special meaning in context):
actor, api, dataset, on, parallel, pipeline, route, task, 
tensor, train, where
```

### C. Operator Precedence

```
1. () [] . (call, index, member access)
2. ! - (unary)
3. * / % (multiplication, division, modulo)
4. + - (addition, subtraction)
5. << >> (bit shift)
6. & (bitwise AND)
7. ^ (bitwise XOR)
8. | (bitwise OR)
9. < <= > >= (comparison)
10. == != (equality)
11. && (logical AND)
12. || (logical OR)
13. = += -= *= /= (assignment)
```

---

## Conclusion

NexusLang provides a modern, safe, and performant programming language designed specifically for the Nexus ecosystem. It combines the best features from Python (simplicity), Rust (safety), Go (concurrency), and adds AI-native capabilities.

**Next Steps:**
1. Implement lexer and parser
2. Build type checker and semantic analyzer
3. Create LLVM backend for code generation
4. Develop standard library
5. Build tooling and IDE support

**Status:** Specification Complete - Ready for Implementation

---

**Document Version:** 1.0  
**Last Updated:** November 9, 2025  
**Authors:** Project Nexus Team  
**License:** Proprietary



