"""
Test suite for NexusLang v2 Backend.

Tests are organized by module:
- test_security.py - Security features (auth, rate limiting, sandboxing)
- test_api.py - API endpoints
- test_services.py - Service layer
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
