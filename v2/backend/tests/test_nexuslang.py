"""
Tests for NexusLang execution API.
"""

import pytest
from fastapi.testclient import TestClient
from ..main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_run_code_simple():
    """Test running simple NexusLang code."""
    code = """
    fn main() {
        print("Hello, World!")
    }
    main()
    """
    
    response = client.post(
        "/api/v2/nexuslang/run",
        json={"code": code}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "Hello, World!" in data["output"]


def test_run_code_with_personality():
    """Test running code with personality block."""
    code = """
    personality {
        curiosity: 0.9,
        analytical: 0.8
    }
    
    fn main() {
        print("Personality set!")
    }
    main()
    """
    
    response = client.post(
        "/api/v2/nexuslang/run",
        json={"code": code}
    )
    
    assert response.status_code == 200
    assert response.json()["success"] == True


def test_compile_to_binary():
    """Test binary compilation."""
    code = """
    fn factorial(n) {
        if n <= 1 {
            return 1
        }
        return n * factorial(n - 1)
    }
    """
    
    response = client.post(
        "/api/v2/nexuslang/compile",
        json={"code": code, "compile_to_binary": True}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "binary" in data


def test_code_analysis():
    """Test code analysis."""
    code = """
    let x = 10
    print(x)
    """
    
    response = client.post(
        "/api/v2/nexuslang/analyze",
        json={"code": code}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "errors" in data
    assert "warnings" in data
    assert "suggestions" in data


def test_invalid_code():
    """Test handling of invalid code."""
    code = """
    this is not valid nexuslang code
    """
    
    response = client.post(
        "/api/v2/nexuslang/run",
        json={"code": code}
    )
    
    # Should return 200 but with success=False
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == False

