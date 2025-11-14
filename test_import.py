#!/usr/bin/env python3
"""
Test script to verify scientific services can be imported
"""

import sys
import os

# Add project paths
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from v2.backend.services.agents.agent_orchestrator import orchestrator
    print("✅ Agent orchestrator imported successfully")
    print(f"Orchestrator type: {type(orchestrator)}")
    print("✅ Scientific services are available!")
except ImportError as e:
    print(f"❌ Import failed: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)