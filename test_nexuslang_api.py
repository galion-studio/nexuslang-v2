#!/usr/bin/env python3
"""
Test script to verify NexusLang API functionality.
Tests the execute endpoint directly.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'v2', 'backend'))

# Set required environment variables
os.environ['JWT_SECRET'] = 'dev_jwt_secret_key_for_testing_with_64_chars_minimum_security'

def test_nexuslang_api():
    """Test the NexusLang API router directly."""
    try:
        from api.nexuslang import router, execute_nexuslang_code
        print("SUCCESS: NexusLang API router imported")

        # Test the execution function directly
        from api.nexuslang import ExecuteRequest
        request = ExecuteRequest(code='print("Hello, NexusLang!")')
        result = execute_nexuslang_code(request.code)
        print(f"SUCCESS: Code execution result: {result.stdout}")

        return True
    except Exception as e:
        print(f"FAILED: NexusLang API test failed: {e}")
        return False

def test_imports():
    """Test all the imports that main.py uses."""
    try:
        # Test core imports
        from core.errors import handle_galion_exception
        from core.performance import performance_middleware
        from core.monitoring import monitoring_middleware
        from core.backup import get_backup_manager
        from core.health_checks import get_health_check_system

        # Test API imports
        from api import auth, ai, nexuslang, billing, video, projects, teams, analytics, grokopedia, marketing, errors, rbac, mail, workplace

        print("SUCCESS: All main.py imports work")
        return True
    except Exception as e:
        print(f"FAILED: Import test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing NexusLang API functionality...")
    print("=" * 50)

    success1 = test_imports()
    success2 = test_nexuslang_api()

    if success1 and success2:
        print("\n" + "=" * 50)
        print("SUCCESS: NexusLang API router is working!")
        print("The import issues are just due to running from outside the package.")
        print("The backend should work fine when run with proper PYTHONPATH.")
    else:
        print("\n" + "=" * 50)
        print("FAILED: There are still issues with the NexusLang API.")
