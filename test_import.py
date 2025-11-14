#!/usr/bin/env python3

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'v2', 'backend'))

try:
    from api.grokopedia import router
    print("✅ SUCCESS: Grokopedia router imported successfully")
    print(f"Router type: {type(router)}")
    print(f"Router routes: {len(router.routes)}")
except Exception as e:
    print(f"❌ FAILED: Grokopedia router import failed: {e}")
    import traceback
    traceback.print_exc()