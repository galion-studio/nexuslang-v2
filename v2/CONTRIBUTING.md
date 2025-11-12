# Contributing to NexusLang v2

**Thank you for your interest in contributing to NexusLang v2!**

We're building the future of AI development together, and your contributions are valuable.

---

## 🎯 Ways to Contribute

### 1. Report Bugs 🐛
Found a bug? Help us fix it!
- Check if it's already reported in [Issues](https://github.com/galion-studio/nexuslang-v2/issues)
- Create a new issue with:
  - Clear title
  - Steps to reproduce
  - Expected vs actual behavior
  - Screenshots if applicable

### 2. Suggest Features 💡
Have an idea? We want to hear it!
- Open a [Feature Request](https://github.com/galion-studio/nexuslang-v2/issues/new)
- Explain the problem it solves
- Describe your proposed solution
- Share use cases

### 3. Improve Documentation 📚
- Fix typos or clarify explanations
- Add examples
- Translate to other languages
- Write tutorials

### 4. Write Code 💻
- Fix bugs
- Implement features
- Optimize performance
- Add tests

### 5. Create Examples 🎨
- Write example programs
- Create tutorials
- Make demo videos
- Share your projects

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git
- Basic understanding of compilers (for language core) OR web development (for IDE)

### Setup Development Environment

```bash
# 1. Fork the repository
# Click "Fork" button on GitHub

# 2. Clone your fork
git clone https://github.com/YOUR-USERNAME/nexuslang-v2.git
cd nexuslang-v2

# 3. Add upstream remote
git remote add upstream https://github.com/galion-studio/nexuslang-v2.git

# 4. Create a branch
git checkout -b feature/my-awesome-feature

# 5. Set up backend
cd backend
pip install -r requirements.txt

# 6. Set up frontend
cd ../frontend
npm install

# 7. Set up language
cd ../nexuslang
pip install -e .

# 8. Run tests
python tests/run_all_tests.py
```

---

## 📝 Development Workflow

### 1. Create a Branch

```bash
# Update your main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### 2. Make Your Changes

**Follow our code style:**
- Use clear, descriptive names
- Add comments explaining WHY, not just WHAT
- Keep functions small and focused (<50 lines)
- Write tests for new features

**Coding Standards:**
```python
# Python: Follow PEP 8
# Use type hints
def function_name(param: str) -> int:
    """
    Clear docstring explaining what this does.
    
    Args:
        param: Description of parameter
        
    Returns:
        Description of return value
    """
    return len(param)

# Keep files small (<200 lines when possible)
# One responsibility per function/class
```

### 3. Test Your Changes

```bash
# Run language tests
cd nexuslang
python tests/run_all_tests.py

# Test manually
nexus run examples/01_hello_world.nx

# Test backend
cd backend
pytest

# Test frontend
cd frontend
npm run lint
npm run build
```

### 4. Commit Your Changes

```bash
# Add files
git add .

# Commit with clear message
git commit -m "Add feature: description of what you did

- Detailed change 1
- Detailed change 2
- Why this change matters"

# Good commit messages:
# ✅ "Add binary compilation benchmarking tool"
# ✅ "Fix: Parser error with nested personality blocks"
# ✅ "Docs: Add tutorial for voice commands"

# Bad commit messages:
# ❌ "Update"
# ❌ "Fix bug"
# ❌ "Changes"
```

### 5. Push and Create Pull Request

```bash
# Push to your fork
git push origin feature/your-feature-name

# Go to GitHub and create Pull Request
# Fill in the template with details
```

---

## 🎨 Code Style Guidelines

### Python (Backend & Language)

```python
# Use meaningful names
def calculate_compression_ratio(source_size: int, binary_size: int) -> float:
    """Calculate how much smaller the binary is."""
    return source_size / binary_size

# Not this:
def calc(a, b):  # ❌ Unclear
    return a / b
```

### TypeScript (Frontend)

```typescript
// Use interfaces
interface CodeExecutionResult {
  output: string
  executionTime: number
  success: boolean
}

// Clear component names
function PersonalityEditor({ onInsert, onClose }: PersonalityEditorProps) {
  // Component logic
}
```

### NexusLang (Examples)

```nexuslang
// Clear function names
fn analyze_sentiment(text) {
    // Analysis logic
}

// Add comments explaining complex logic
// Use consistent formatting
```

---

## 🧪 Testing Guidelines

### Writing Tests

```python
def test_personality_parsing():
    """Test that personality blocks parse correctly"""
    code = """
    personality {
        curiosity: 0.9,
        analytical: 0.8
    }
    """
    
    lexer = Lexer(code)
    parser = Parser(lexer.tokenize())
    ast = parser.parse()
    
    # Clear assertions
    assert isinstance(ast.statements[0], PersonalityBlock)
    assert ast.statements[0].traits['curiosity'] == 0.9
```

### Test Coverage

- Aim for >80% code coverage
- Test edge cases
- Test error conditions
- Test with invalid input

---

## 📋 Pull Request Process

### Before Submitting

- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] Examples added (if new feature)
- [ ] No console.log or debug prints
- [ ] Commit messages are clear

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation
- [ ] Performance improvement
- [ ] Refactoring

## Testing
How did you test this?

## Screenshots
If UI changes, add screenshots

## Checklist
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Code follows style guide
```

### Review Process

1. **Automated checks** run (tests, linting)
2. **Maintainer review** (usually within 48 hours)
3. **Feedback** addressed
4. **Approved** and merged!

---

## 🌟 Recognition

### Contributors

All contributors are recognized:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- GitHub contributor graph
- Special badges for significant contributions

### Levels

- **Contributor:** 1+ merged PR
- **Regular Contributor:** 5+ merged PRs
- **Core Contributor:** 20+ merged PRs
- **Maintainer:** Trusted with merge access

---

## 💬 Communication

### Where to Ask Questions

- **GitHub Discussions:** General questions, ideas
- **GitHub Issues:** Bug reports, feature requests
- **Discord:** Real-time chat (coming soon)
- **Email:** contribute@galion.app (for private matters)

### Response Times

- Issues: Within 48 hours
- PRs: Within 48 hours
- Questions: Within 24 hours

---

## 🎯 Good First Issues

New to the project? Look for issues labeled:
- `good first issue` - Beginner friendly
- `documentation` - Help improve docs
- `help wanted` - We need your expertise!

### Suggested Areas

**Easy:**
- Add examples
- Fix typos
- Improve error messages
- Add comments to code

**Medium:**
- Add built-in functions
- Improve CLI
- Add UI components
- Write tests

**Hard:**
- Optimize compiler
- Add language features
- Implement voice integration
- Performance improvements

---

## 📜 Code of Conduct

We follow the [Code of Conduct](./CODE_OF_CONDUCT.md).

**Summary:**
- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Assume good intentions
- Report unacceptable behavior

---

## 🏆 Project Goals & Vision

### Our Mission

Build the programming language AI would create for itself.

### Core Values

1. **First Principles** - Question assumptions
2. **Simplicity** - Make complex things simple
3. **Performance** - Speed is a feature
4. **Openness** - Transparent development
5. **Innovation** - Lead, don't follow

### Roadmap

See [ROADMAP.md](./ROADMAP.md) for detailed timeline.

**Short-term (Month 1-3):**
- Stabilize alpha
- Add more examples
- Improve documentation
- Build community

**Mid-term (Month 4-6):**
- Voice-to-voice integration
- Real-time collaboration
- Mobile support
- Advanced ML features

**Long-term (Year 1):**
- 10,000+ users
- Production voice system
- Enterprise features
- Self-improving AI

---

## 🔧 Development Tips

### Running Locally

```bash
# Backend
cd backend
uvicorn main:app --reload --port 8100

# Frontend
cd frontend
npm run dev -- -p 3100

# Language
cd nexuslang
nexus run examples/01_hello_world.nx
```

### Debugging

```bash
# Enable debug logging
export DEBUG=true

# Run with verbose output
nexus run --verbose mycode.nx

# Check API logs
tail -f backend.log
```

### Common Issues

**Import errors:**
```bash
# Reinstall in development mode
pip install -e .
```

**Port conflicts:**
```bash
# Use different ports
uvicorn main:app --port 8101
```

---

## 📊 Metrics We Track

**Code Quality:**
- Test coverage: >80% target
- Code review: All PRs reviewed
- CI/CD: Automated checks
- Performance: Benchmarks on every release

**Community:**
- Contributors: Monthly growth
- PRs: Merge rate and time
- Issues: Response time
- Stars: Community interest

---

## 🎁 Benefits of Contributing

### You Get:

- **Recognition:** Your name in contributors list
- **Learning:** Work on cutting-edge AI tech
- **Portfolio:** Show employers real impact
- **Network:** Connect with AI researchers
- **Early Access:** New features before release

### We Get:

- Better code
- More perspectives
- Faster innovation
- Stronger community
- Global reach

**It's win-win!** 🎉

---

## 📞 Questions?

**Not sure where to start?**
- Read [Getting Started](./docs/GETTING_STARTED.md)
- Browse [Good First Issues](https://github.com/galion-studio/nexuslang-v2/labels/good%20first%20issue)
- Ask in GitHub Discussions
- Email: contribute@galion.app

---

## 🙏 Thank You!

Every contribution matters:
- Code, docs, examples, feedback
- All make NexusLang better
- You're building the future of AI development

**Welcome to the NexusLang community!** 🚀

---

_Built with first principles. Designed for the 22nd century. Open for everyone._

**Star the repo ⭐ | Fork and contribute 🍴 | Share with friends 📢**

