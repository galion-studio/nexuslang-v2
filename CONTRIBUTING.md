# Contributing to NexusLang v2

**Welcome! We're excited you want to contribute!**

---

## How to Contribute

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/your-username/project-nexus.git
cd project-nexus
```

### 2. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### 3. Make Changes

- Write clean, well-documented code
- Follow existing code style
- Add tests for new features
- Update documentation

### 4. Test Locally

```bash
# Start services
docker-compose up -d

# Run tests
cd v2/backend && pytest
cd v2/frontend && npm test

# Test NexusLang
cd v2/nexuslang && nexuslang run examples/your_example.nx
```

### 5. Commit and Push

```bash
git add .
git commit -m "feat: add your feature description"
git push origin feature/your-feature-name
```

### 6. Create Pull Request

- Go to GitHub
- Create pull request from your branch
- Describe your changes
- Wait for review

---

## Areas to Contribute

### Language Features
- New syntax features
- Compiler optimizations
- Standard library functions
- Example programs

### Platform Features
- IDE improvements
- Grokopedia content
- Community features
- UI/UX enhancements

### Documentation
- Tutorials
- API documentation
- Example code
- Translations

### Testing
- Unit tests
- Integration tests
- Performance tests
- Bug reports

---

## Code Style

### Python

- Follow PEP 8
- Use type hints
- Write docstrings
- Keep functions small (<50 lines)

### TypeScript

- Use TypeScript strict mode
- Define proper types
- Use functional components
- Follow React best practices

### NexusLang

- Follow existing syntax patterns
- Write clear examples
- Document new features

---

## Commit Messages

Use conventional commits:

```
feat: add new feature
fix: fix bug
docs: update documentation
style: formatting changes
refactor: code refactoring
test: add tests
chore: maintenance tasks
```

---

## Questions?

- Open an issue on GitHub
- Join our Discord (coming soon)
- Email: team@nexuslang.dev

---

**Thank you for contributing to the future of AI development!** 🚀

