# 🧪 Galion Agent System - Test Suite

Comprehensive testing framework for the Galion autonomous agent platform, ensuring reliability, performance, and quality across all components.

## 📋 Overview

This test suite provides:

- **Unit Tests** - Component-level testing
- **Integration Tests** - End-to-end workflow testing
- **Performance Tests** - Load and stress testing
- **API Tests** - REST endpoint validation
- **Frontend Tests** - UI component testing
- **CI/CD Pipeline** - Automated quality assurance

## 🚀 Quick Start

### Prerequisites

```bash
# Install test dependencies
pip install -r tests/requirements.txt

# Install the package in development mode
pip install -e .

# For frontend testing
cd admin-dashboard && npm install
```

### Run All Tests

```bash
# Using pytest directly
pytest tests/ -v --cov=v2 --cov-report=html

# Using make (recommended)
make test

# Run with specific options
pytest tests/ -v --tb=short --cov=v2 --cov-report=html --cov-fail-under=80
```

### Test Categories

```bash
# Unit tests only
make test-unit
# or
pytest tests/ -m "not (integration or performance or slow or external)"

# Integration tests
make test-integration
# or
pytest tests/ -m "integration"

# Performance tests
make test-performance
# or
pytest tests/test_performance.py -v --benchmark-only

# Frontend tests
make test-frontend
# or
cd admin-dashboard && npm run test
```

## 📁 Test Structure

```
tests/
├── __init__.py                 # Test package initialization
├── conftest.py                 # Pytest configuration and fixtures
├── requirements.txt            # Test dependencies
├── test_agent_orchestrator.py  # Agent orchestrator unit tests
├── test_integrations.py        # Integration framework tests
├── test_api.py                 # API endpoint integration tests
├── test_performance.py         # Performance and load tests
├── load_tests.py              # Locust load testing scripts
└── README.md                  # This file
```

## 🛠️ Test Configuration

### Pytest Configuration (`pytest.ini`)

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --verbose
    --tb=short
    --strict-markers
    --disable-warnings
    --asyncio-mode=auto
    --cov=v2
    --cov-report=html:htmlcov
    --cov-report=xml:coverage.xml
    --cov-report=term-missing
    --cov-fail-under=80
markers =
    unit: Unit tests
    integration: Integration tests
    performance: Performance tests
    slow: Slow running tests
    external: Tests requiring external services
    agent: Agent-specific tests
    integration_test: Integration framework tests
    api: API endpoint tests
asyncio_mode = auto
```

### Test Fixtures (`conftest.py`)

Shared fixtures for all tests:

- `event_loop` - Async event loop for async tests
- `temp_db` - Temporary database for testing
- `temp_cache` - Temporary cache for testing
- `orchestrator` - Test orchestrator instance
- `integration_manager` - Test integration manager
- `mock_agent` - Mock agent for testing
- `mock_integration` - Mock integration for testing
- `sample_task` - Sample task data
- `utils` - Test utility functions

## 🧪 Test Categories

### Unit Tests

Test individual components in isolation:

```python
@pytest.mark.unit
def test_agent_initialization(mock_agent):
    """Test agent initialization."""
    assert mock_agent.name == "test_agent"
    assert mock_agent.get_status() is not None
```

### Integration Tests

Test component interactions and end-to-end workflows:

```python
@pytest.mark.integration
async def test_agent_orchestrator_workflow(orchestrator, sample_task):
    """Test complete agent workflow."""
    # Add task and verify processing
    task_id = await orchestrator.task_queue.add_task(sample_task)
    assert task_id is not None

    # Retrieve task
    task = await orchestrator.task_queue.get_next_task()
    assert task is not None
    assert task["task_id"] == task_id
```

### Performance Tests

Measure system performance under load:

```python
@pytest.mark.performance
async def test_concurrent_task_processing(orchestrator):
    """Test concurrent task processing performance."""
    async def process_tasks_concurrently():
        # Create and process multiple tasks concurrently
        # Measure execution time and resource usage

    metrics = await measure_execution_time(process_tasks_concurrently, 3)
    assert metrics['avg'] < 10.0, "Concurrent processing too slow"
```

### API Tests

Test REST API endpoints:

```python
async def test_get_agents(async_client):
    """Test getting all agents."""
    response = await async_client.get("/agents")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
```

## 📊 Code Coverage

### Coverage Requirements

- **Minimum Coverage**: 80%
- **Target Coverage**: 90%+
- **Critical Paths**: 95%+

### Generating Coverage Reports

```bash
# HTML report (recommended)
pytest tests/ --cov=v2 --cov-report=html
open htmlcov/index.html

# Terminal summary
pytest tests/ --cov=v2 --cov-report=term-missing

# XML for CI/CD
pytest tests/ --cov=v2 --cov-report=xml
```

### Coverage Configuration

```ini
[coverage:run]
source = v2
omit =
    */tests/*
    */migrations/*
    v2/backend/core/config.py

[coverage:report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    class .*\bProtocol\):
    @(abc\.)?abstractmethod
```

## ⚡ Performance Testing

### Benchmarking

```bash
# Run performance benchmarks
pytest tests/test_performance.py --benchmark-only --benchmark-json=benchmark.json

# Compare with previous results
pytest tests/test_performance.py --benchmark-compare=benchmark.json
```

### Load Testing with Locust

```bash
# Install locust
pip install locust

# Run load tests
locust -f tests/load_tests.py

# Distributed load testing
locust -f tests/load_tests.py --master
locust -f tests/load_tests.py --worker --master-host=localhost
```

### Performance Metrics Tracked

- **Response Time**: API endpoint response times
- **Throughput**: Operations per second
- **Resource Usage**: CPU, memory, disk I/O
- **Scalability**: Performance under increased load
- **Memory Leaks**: Memory usage stability
- **Error Rates**: Error frequency under load

## 🔧 CI/CD Pipeline

### GitHub Actions Workflow

The CI/CD pipeline includes:

1. **Code Quality Checks**
   - Black formatting
   - isort import sorting
   - flake8 linting
   - mypy type checking
   - Security scanning

2. **Unit Tests**
   - PostgreSQL and Redis test databases
   - Coverage reporting
   - Codecov integration

3. **Integration Tests**
   - Full system integration
   - Docker Compose testing
   - API endpoint testing

4. **Performance Tests**
   - Benchmarking (on main branch only)
   - Load testing
   - Performance regression detection

5. **Frontend Tests**
   - TypeScript checking
   - Unit tests
   - Build verification

6. **Docker Build Test**
   - Multi-stage build verification
   - Image size optimization

7. **Security Scanning**
   - Trivy vulnerability scanning
   - Bandit security linting

8. **Deployment**
   - Staging deployment
   - Production deployment
   - Rollback capabilities

### Pipeline Triggers

```yaml
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  workflow_dispatch:
```

### Environment Variables

```bash
# Required secrets for CI/CD
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
SLACK_WEBHOOK_URL
DOCKER_HUB_USERNAME
DOCKER_HUB_TOKEN
```

## 🐳 Testing with Docker

### Test Environment Setup

```bash
# Start test services
docker-compose -f docker-compose.test.yml up -d

# Run tests against containerized services
pytest tests/ -m "integration"

# Stop test services
docker-compose -f docker-compose.test.yml down
```

### Docker Test Compose

```yaml
version: '3.8'
services:
  postgres-test:
    image: postgres:15
    environment:
      POSTGRES_DB: galion_test
      POSTGRES_USER: galion
      POSTGRES_PASSWORD: test_password
    ports:
      - "5433:5432"

  redis-test:
    image: redis:7-alpine
    ports:
      - "6380:6379"

  backend-test:
    build:
      context: .
      dockerfile: Dockerfile.test
    depends_on:
      - postgres-test
      - redis-test
    environment:
      DATABASE_URL: postgresql://galion:test_password@postgres-test:5432/galion_test
      REDIS_URL: redis://redis-test:6379/1
```

## 🔍 Debugging Tests

### Common Issues

1. **Async Test Issues**
   ```python
   # Use pytest.mark.asyncio
   @pytest.mark.asyncio
   async def test_async_function():
       result = await async_operation()
       assert result is not None
   ```

2. **Database Connection Issues**
   ```python
   # Use fixtures for database setup
   async def test_with_database(temp_db):
       async with temp_db.session() as session:
           # Test database operations
           pass
   ```

3. **Mock Setup Issues**
   ```python
   # Proper mock setup
   def test_with_mocks(mock_agent):
       mock_agent.execute_task.return_value = expected_result
       # Test with mocked agent
   ```

### Debug Commands

```bash
# Run specific test with debugging
pytest tests/test_specific.py::TestClass::test_method -v -s --pdb

# Run tests with coverage details
pytest tests/ --cov=v2 --cov-report=html --cov-report=term-missing

# Run slow tests only
pytest tests/ -m "slow" -v

# Profile test performance
pytest tests/ --durations=10
```

## 📈 Test Metrics & Reporting

### Test Results

- **Test Execution Time**: Tracked per test and suite
- **Coverage Percentage**: Overall and per module
- **Failure Rate**: Test failure statistics
- **Performance Benchmarks**: Response times and throughput

### Reporting Tools

- **Coverage.py**: HTML and XML reports
- **pytest-html**: Detailed HTML test reports
- **Codecov**: Online coverage tracking
- **Benchmarking**: Performance regression detection

### Quality Gates

```yaml
# Quality gate configuration
coverage:
  status:
    project:
      default:
        target: 80%
        threshold: 1%
    patch:
      default:
        target: 80%
        threshold: 1%
```

## 🚀 Best Practices

### Writing Tests

1. **Test Isolation**: Each test should be independent
2. **Descriptive Names**: Clear test method names
3. **Arrange-Act-Assert**: Standard test structure
4. **Mock External Dependencies**: Use fixtures for external services
5. **Test Edge Cases**: Cover error conditions and boundaries

### Test Organization

1. **One Test Per Behavior**: Single responsibility principle
2. **Descriptive Assertions**: Clear failure messages
3. **Test Data Factories**: Reusable test data creation
4. **Fixture Reuse**: Share setup/teardown code
5. **Parameterized Tests**: Test multiple inputs efficiently

### Performance Testing

1. **Realistic Load**: Test with production-like data volumes
2. **Resource Monitoring**: Track CPU, memory, and I/O usage
3. **Baseline Comparison**: Compare against previous runs
4. **Scalability Testing**: Test with increasing load levels
5. **Memory Leak Detection**: Monitor memory usage over time

## 📚 Advanced Testing Features

### Property-Based Testing

```python
from hypothesis import given, strategies as st

@given(st.text(min_size=1, max_size=100))
def test_task_description_validation(description):
    """Test task description validation with various inputs."""
    task = create_test_task(description=description)
    assert validate_task(task) is True
```

### Mutation Testing

```bash
# Install mutmut
pip install mutmut

# Run mutation testing
mutmut run --paths-to-mutate v2/backend --tests-dir tests/

# Generate report
mutmut html
```

### Fuzz Testing

```python
import atheris

def test_fuzz_input(data):
    """Fuzz test for input validation."""
    try:
        process_input(data)
    except ValidationError:
        pass  # Expected for invalid input
    except Exception as e:
        raise AssertionError(f"Unexpected error: {e}")

atheris.Setup(sys.argv, test_fuzz_input)
atheris.Fuzz()
```

## 🎯 Contributing to Tests

### Adding New Tests

1. **Follow Naming Conventions**: `test_*.py` for files, `test_*` for functions
2. **Use Appropriate Markers**: `@pytest.mark.unit`, `@pytest.mark.integration`, etc.
3. **Add Docstrings**: Document what each test verifies
4. **Include Edge Cases**: Test error conditions and boundaries
5. **Update Fixtures**: Add new fixtures to `conftest.py` if needed

### Test Maintenance

1. **Regular Review**: Review and update tests regularly
2. **Remove Flaky Tests**: Fix or remove unreliable tests
3. **Update Dependencies**: Keep test dependencies current
4. **Performance Monitoring**: Monitor test execution times
5. **Coverage Goals**: Maintain or improve coverage targets

---

## 📞 Support

For testing issues or questions:

- Check the [Makefile](./Makefile) for common commands
- Review [CI/CD pipeline](.github/workflows/ci-cd.yml) configuration
- Examine [test fixtures](conftest.py) for setup examples
- Review [performance tests](test_performance.py) for benchmarking examples

**Happy Testing! 🧪✨**
