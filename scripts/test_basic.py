#!/usr/bin/env python3
"""
Basic System Test Script

This script performs basic health checks and simple tests
to verify that your Galion autonomous agent system is working correctly.
"""

import requests
import json
import time
import sys
from typing import Dict, Any, List

# Configuration
BASE_URL = "http://localhost:8010"
TIMEOUT = 30  # seconds

def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f" {text}")
    print(f"{'='*60}")

def print_success(text: str):
    """Print a success message."""
    print(f"✅ {text}")

def print_error(text: str):
    """Print an error message."""
    print(f"❌ {text}")

def print_info(text: str):
    """Print an info message."""
    print(f"ℹ️  {text}")

def make_request(method: str, endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Make an HTTP request and return the response."""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method.upper() == "GET":
            response = requests.get(url, timeout=TIMEOUT)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, timeout=TIMEOUT)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {e}")
        return None

def test_health():
    """Test basic health endpoint."""
    print_header("HEALTH CHECK")

    print_info("Testing basic health endpoint...")
    result = make_request("GET", "/health")

    if result and result.get("status") == "healthy":
        print_success("Health check passed!")
        return True
    else:
        print_error("Health check failed!")
        return False

def test_detailed_health():
    """Test detailed health endpoint."""
    print_info("Testing detailed health endpoint...")
    result = make_request("GET", "/health/detailed")

    if result:
        print_success("Detailed health check passed!")
        print(f"   System info: {result.get('system', 'N/A')}")
        return True
    else:
        print_error("Detailed health check failed!")
        return False

def test_system_info():
    """Test system information endpoint."""
    print_info("Testing system information endpoint...")
    result = make_request("GET", "/info")

    if result:
        print_success("System info retrieved!")
        print(f"   Version: {result.get('version', 'N/A')}")
        print(f"   Environment: {result.get('environment', 'N/A')}")
        return True
    else:
        print_error("System info retrieval failed!")
        return False

def test_simple_task():
    """Test a simple autonomous task."""
    print_header("SIMPLE TASK EXECUTION")

    task_data = {
        "prompt": "Write a Python function that returns 'Hello, World!'",
        "require_approval": False
    }

    print_info("Submitting simple task...")
    result = make_request("POST", "/api/v1/agents/execute", task_data)

    if not result:
        print_error("Task submission failed!")
        return False

    task_id = result.get("task_id")
    if not task_id:
        print_error("No task ID received!")
        return False

    print_success(f"Task submitted with ID: {task_id}")

    # Poll for completion
    print_info("Waiting for task completion...")
    max_attempts = 10
    for attempt in range(max_attempts):
        time.sleep(2)
        status_result = make_request("GET", f"/api/v1/agents/status/{task_id}")

        if status_result:
            status = status_result.get("status")
            print(f"   Attempt {attempt + 1}/{max_attempts}: Status = {status}")

            if status == "completed":
                print_success("Task completed successfully!")
                print(f"   Result: {status_result.get('result', 'N/A')}")
                return True
            elif status == "failed":
                print_error("Task failed!")
                print(f"   Error: {status_result.get('error', 'Unknown error')}")
                return False

    print_error("Task timed out!")
    return False

def test_monitoring():
    """Test monitoring endpoints."""
    print_header("MONITORING CHECK")

    print_info("Testing monitoring status...")
    result = make_request("GET", "/monitoring/status")

    if result:
        print_success("Monitoring status retrieved!")
        print(f"   Active tasks: {result.get('active_tasks', 0)}")
        print(f"   Total agents: {result.get('total_agents', 0)}")
        return True
    else:
        print_error("Monitoring check failed!")
        return False

def run_all_tests():
    """Run all basic tests."""
    print_header("GALION SYSTEM - BASIC TESTS")
    print(f"Testing against: {BASE_URL}")

    tests = [
        ("Health Check", test_health),
        ("Detailed Health", test_detailed_health),
        ("System Info", test_system_info),
        ("Simple Task", test_simple_task),
        ("Monitoring", test_monitoring),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print_error(f"{test_name} failed!")
        except Exception as e:
            print_error(f"{test_name} failed with exception: {e}")

    print_header("TEST RESULTS")
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print_success("🎉 All tests passed! Your Galion system is working correctly.")
        return True
    else:
        print_error("❌ Some tests failed. Please check the errors above.")
        return False

def main():
    """Main function."""
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
