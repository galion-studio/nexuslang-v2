#!/usr/bin/env python3
"""
NexusLang v2 Production Readiness Validation
Final check before production deployment
"""

import requests
import json
import sys
import time
from typing import Dict, List

# Configuration
SERVICES = {
    "backend": "http://localhost:8010",
    "frontend": "http://localhost:3010",
    "monitoring": "http://localhost:8080",
    "prometheus": "http://localhost:9090",
    "grafana": "http://localhost:3001"
}

def check_service_health(service_name: str, url: str) -> Dict:
    """Check individual service health"""
    result = {
        "service": service_name,
        "url": url,
        "status": "unknown",
        "response_time": None,
        "error": None
    }

    try:
        start_time = time.time()
        response = requests.get(f"{url}/health", timeout=10)
        response_time = (time.time() - start_time) * 1000

        result["response_time"] = round(response_time, 2)

        if response.status_code == 200:
            result["status"] = "healthy"
        else:
            result["status"] = "unhealthy"
            result["error"] = f"HTTP {response.status_code}"

    except requests.exceptions.ConnectionError:
        result["status"] = "down"
        result["error"] = "Connection refused"
    except requests.exceptions.Timeout:
        result["status"] = "timeout"
        result["error"] = "Request timeout"
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)

    return result

def validate_api_endpoints() -> List[Dict]:
    """Validate critical API endpoints"""
    base_url = SERVICES["backend"]
    endpoints = [
        {"path": "/", "method": "GET", "critical": True},
        {"path": "/health", "method": "GET", "critical": True},
        {"path": "/docs", "method": "GET", "critical": False},
        {"path": "/metrics", "method": "GET", "critical": True},
        {"path": "/auth/login", "method": "POST", "critical": True},
        {"path": "/users/", "method": "GET", "critical": False},
        {"path": "/projects/", "method": "GET", "critical": False},
        {"path": "/api/v2/nexuslang/execute", "method": "POST", "critical": True,
         "data": {"code": "print('validation')", "language": "nexuslang"}},
    ]

    results = []

    for endpoint in endpoints:
        result = {
            "endpoint": endpoint["path"],
            "method": endpoint["method"],
            "critical": endpoint["critical"],
            "status": "unknown",
            "response_time": None,
            "error": None
        }

        try:
            start_time = time.time()
            url = f"{base_url}{endpoint['path']}"

            if endpoint["method"] == "GET":
                response = requests.get(url, timeout=5)
            elif endpoint["method"] == "POST":
                data = endpoint.get("data", {})
                response = requests.post(url, json=data, timeout=10)

            response_time = (time.time() - start_time) * 1000
            result["response_time"] = round(response_time, 2)

            if response.status_code in [200, 201]:
                result["status"] = "working"
            else:
                result["status"] = "error"
                result["error"] = f"HTTP {response.status_code}"

        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)

        results.append(result)

    return results

def check_security_headers() -> Dict:
    """Check security headers on API responses"""
    result = {"passed": True, "issues": []}

    try:
        response = requests.get(f"{SERVICES['backend']}/health")
        headers = response.headers

        required_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection",
            "Strict-Transport-Security"
        ]

        for header in required_headers:
            if header not in headers:
                result["passed"] = False
                result["issues"].append(f"Missing security header: {header}")

    except Exception as e:
        result["passed"] = False
        result["issues"].append(f"Security check failed: {e}")

    return result

def run_production_validation():
    """Run complete production validation"""
    print("=" * 70)
    print("NEXUSLANG V2 PRODUCTION READINESS VALIDATION")
    print("=" * 70)
    print()

    validation_results = {
        "services": [],
        "api_endpoints": [],
        "security": {},
        "overall_status": "unknown"
    }

    # 1. Check Service Health
    print("1. Checking Service Health...")
    print("-" * 30)

    for service_name, url in SERVICES.items():
        result = check_service_health(service_name, url)
        validation_results["services"].append(result)

        status_icon = "PASS" if result["status"] == "healthy" else "FAIL"
        print(f"{status_icon}: {service_name} - {result['status']}")

        if result["error"]:
            print(f"     Error: {result['error']}")

    # 2. Validate API Endpoints
    print("\n2. Validating API Endpoints...")
    print("-" * 30)

    api_results = validate_api_endpoints()
    validation_results["api_endpoints"] = api_results

    for result in api_results:
        critical_marker = "[CRITICAL]" if result["critical"] else "[OPTIONAL]"
        status_icon = "PASS" if result["status"] == "working" else "FAIL"
        print(f"{status_icon} {critical_marker} {result['method']} {result['endpoint']} - {result['status']}")

        if result["error"]:
            print(f"     Error: {result['error']}")

    # 3. Check Security Headers
    print("\n3. Checking Security Configuration...")
    print("-" * 30)

    security_result = check_security_headers()
    validation_results["security"] = security_result

    if security_result["passed"]:
        print("PASS: Security headers configured")
    else:
        print("FAIL: Security issues found:")
        for issue in security_result["issues"]:
            print(f"     - {issue}")

    # 4. Overall Assessment
    print("\n4. PRODUCTION READINESS ASSESSMENT")
    print("-" * 40)

    # Calculate scores
    service_score = sum(1 for s in validation_results["services"] if s["status"] == "healthy")
    api_score = sum(1 for a in validation_results["api_endpoints"] if a["status"] == "working")
    critical_api_score = sum(1 for a in validation_results["api_endpoints"]
                           if a["status"] == "working" and a["critical"])

    total_services = len(SERVICES)
    total_apis = len(api_results)
    critical_apis = sum(1 for a in api_results if a["critical"])

    print(f"Services: {service_score}/{total_services} healthy")
    print(f"API Endpoints: {api_score}/{total_apis} working")
    print(f"Critical APIs: {critical_api_score}/{critical_apis} working")
    print(f"Security: {'PASS' if security_result['passed'] else 'FAIL'}")

    # Determine overall status
    critical_failures = []

    if service_score < total_services:
        critical_failures.append("Some services are not healthy")

    if critical_api_score < critical_apis:
        critical_failures.append("Critical API endpoints failing")

    if not security_result["passed"]:
        critical_failures.append("Security configuration issues")

    if not critical_failures:
        validation_results["overall_status"] = "PRODUCTION READY"
        print("\n" + "=" * 70)
        print("🎯 PRODUCTION DEPLOYMENT READY!")
        print("All critical systems are operational and secure.")
        print("=" * 70)
        return True
    else:
        validation_results["overall_status"] = "NOT READY"
        print("\n" + "!" * 70)
        print("⚠️  PRODUCTION DEPLOYMENT BLOCKED")
        print("Critical issues must be resolved:")
        for failure in critical_failures:
            print(f"   - {failure}")
        print("!" * 70)
        return False

def main():
    """Main validation function"""
    try:
        success = run_production_validation()

        print("\nValidation completed.")
        print("Check the detailed results above for any issues.")

        if success:
            print("\nNext steps:")
            print("1. Run: docker-compose up -d")
            print("2. Configure domain and SSL certificates")
            print("3. Set up monitoring alerts")
            print("4. Deploy to production!")

        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n\nValidation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nValidation failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
