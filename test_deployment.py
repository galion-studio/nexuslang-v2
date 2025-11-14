#!/usr/bin/env python3
"""
Quick deployment test script for Nexus Lang V2 Scientific AI
Run this after your RunPod deployment is complete
"""

import requests
import json
import time
from datetime import datetime

def test_endpoint(url, description):
    """Test a single endpoint"""
    try:
        start_time = time.time()
        response = requests.get(url, timeout=10)
        end_time = time.time()
        response_time = end_time - start_time

        if response.status_code == 200:
            print(f"✅ {description}: SUCCESS ({response_time:.2f}s)")
            return True, response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
        else:
            print(f"❌ {description}: FAILED (HTTP {response.status_code})")
            return False, None
    except Exception as e:
        print(f"❌ {description}: ERROR ({str(e)})")
        return False, None

def test_scientific_query(base_url, query):
    """Test scientific query endpoint"""
    try:
        payload = {"query": query}
        start_time = time.time()
        response = requests.post(f"{base_url}/scientific-query",
                               json=payload,
                               headers={"Content-Type": "application/json"},
                               timeout=30)
        end_time = time.time()
        response_time = end_time - start_time

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Scientific Query: SUCCESS ({response_time:.2f}s)")
            print(f"   Confidence: {data.get('confidence', 'N/A')}")
            print(f"   Agents used: {len(data.get('agents_used', []))}")
            return True
        else:
            print(f"❌ Scientific Query: FAILED (HTTP {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Scientific Query: ERROR ({str(e)})")
        return False

def main():
    print("🔬 Nexus Lang V2 Scientific AI - Deployment Test")
    print("=" * 50)
    print(f"Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Get pod URL from user
    pod_url = input("Enter your RunPod pod URL (e.g., abc123.runpod.net): ").strip()
    if not pod_url.startswith('http'):
        pod_url = f"https://{pod_url}"

    base_url = pod_url.rstrip('/')
    print(f"Testing deployment at: {base_url}")
    print()

    # Test basic endpoints
    print("📡 BASIC CONNECTIVITY TESTS")
    health_ok, health_data = test_endpoint(f"{base_url}/health", "Health Check")
    docs_ok, _ = test_endpoint(f"{base_url}/docs", "API Documentation")
    capabilities_ok, capabilities_data = test_endpoint(f"{base_url}/scientific-capabilities", "Scientific Capabilities")

    print()

    # Test scientific queries
    print("🧠 SCIENTIFIC AI TESTS")
    physics_ok = test_scientific_query(base_url, "Explain Newton's laws of motion")
    chemistry_ok = test_scientific_query(base_url, "What is the periodic table?")
    math_ok = test_scientific_query(base_url, "What is calculus?")

    print()

    # Summary
    print("📊 DEPLOYMENT TEST SUMMARY")
    print("=" * 50)

    tests_passed = sum([health_ok, docs_ok, capabilities_ok, physics_ok, chemistry_ok, math_ok])
    total_tests = 6

    print(f"Tests passed: {tests_passed}/{total_tests}")

    if health_ok:
        print("✅ System is healthy and responding")
    else:
        print("❌ System health check failed")

    if capabilities_ok and capabilities_data:
        agents = capabilities_data.get('agents', [])
        print(f"✅ Found {len(agents)} scientific agents: {', '.join(agents)}")

    if physics_ok and chemistry_ok and math_ok:
        print("✅ All scientific agents are working")
    else:
        print("⚠️  Some scientific agents may have issues")

    print()

    if tests_passed >= 4:  # At least basic functionality working
        print("🎉 DEPLOYMENT SUCCESSFUL!")
        print("Your scientific AI is live and ready to use!")
        print()
        print("🚀 Access your system:")
        print(f"   API: {base_url}")
        print(f"   Docs: {base_url}/docs")
        print(f"   Dashboard: {base_url}:8080")
        print()
        print("💡 Try these queries:")
        print("   - 'Explain quantum mechanics'")
        print("   - 'What is photosynthesis?'")
        print("   - 'Solve x² + 2x + 1 = 0'")
    else:
        print("⚠️  DEPLOYMENT ISSUES DETECTED")
        print("Check your RunPod logs for more details")

if __name__ == "__main__":
    main()
