#!/usr/bin/env python3
"""
Nexus Lang V2 Scientific AI - Complete System Verification
Tests all components, agents, and connectivity after deployment
"""

import requests
import json
import time
import sys
from datetime import datetime

class SystemVerifier:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.timeout = 30
        self.results = []

    def log_result(self, test_name, status, message="", details=None):
        """Log test result"""
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        self.results.append(result)

        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {message}")
        if details:
            for key, value in details.items():
                print(f"   {key}: {value}")

    def test_health_endpoint(self):
        """Test basic health endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                self.log_result("Health Check", "PASS", "API is healthy",
                              {"status": data.get("status"), "version": data.get("version")})
                return True
            else:
                self.log_result("Health Check", "FAIL", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Health Check", "FAIL", str(e))
            return False

    def test_api_docs(self):
        """Test API documentation endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/docs")
            if response.status_code == 200:
                self.log_result("API Documentation", "PASS", "Docs accessible")
                return True
            else:
                self.log_result("API Documentation", "FAIL", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_result("API Documentation", "FAIL", str(e))
            return False

    def test_scientific_capabilities(self):
        """Test scientific capabilities endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/scientific-capabilities")
            if response.status_code == 200:
                data = response.json()
                agents = data.get("agents", [])
                self.log_result("Scientific Capabilities", "PASS",
                              f"Found {len(agents)} agents", {"agents": agents})
                return True
            else:
                self.log_result("Scientific Capabilities", "FAIL", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Scientific Capabilities", "FAIL", str(e))
            return False

    def test_physics_agent(self):
        """Test physics agent with a sample query"""
        return self._test_agent_query("physics", "Explain Newton's laws of motion")

    def test_chemistry_agent(self):
        """Test chemistry agent with a sample query"""
        return self._test_agent_query("chemistry", "What is the periodic table?")

    def test_mathematics_agent(self):
        """Test mathematics agent with a sample query"""
        return self._test_agent_query("mathematics", "What is calculus?")

    def _test_agent_query(self, domain, query):
        """Test agent query for specific domain"""
        try:
            payload = {
                "query": query,
                "domain": domain,
                "include_reasoning": True
            }
            response = self.session.post(f"{self.base_url}/scientific-query",
                                       json=payload, headers={"Content-Type": "application/json"})

            if response.status_code == 200:
                data = response.json()
                confidence = data.get("confidence", 0)
                response_time = data.get("response_time", 0)

                self.log_result(f"{domain.title()} Agent", "PASS",
                              f"Response in {response_time:.2f}s",
                              {"confidence": confidence, "has_reasoning": "reasoning_steps" in data})
                return True
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                self.log_result(f"{domain.title()} Agent", "FAIL",
                              f"HTTP {response.status_code}: {error_data}")
                return False
        except Exception as e:
            self.log_result(f"{domain.title()} Agent", "FAIL", str(e))
            return False

    def test_multi_agent_collaboration(self):
        """Test multi-agent collaboration"""
        try:
            payload = {
                "query": "How does quantum mechanics relate to chemical bonding?",
                "enable_collaboration": True,
                "include_reasoning": True
            }
            response = self.session.post(f"{self.base_url}/scientific-query",
                                       json=payload, headers={"Content-Type": "application/json"})

            if response.status_code == 200:
                data = response.json()
                agents_used = data.get("agents_used", [])
                self.log_result("Multi-Agent Collaboration", "PASS",
                              f"Used {len(agents_used)} agents",
                              {"agents": agents_used, "collaboration": data.get("collaboration_details")})
                return True
            else:
                self.log_result("Multi-Agent Collaboration", "FAIL", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Multi-Agent Collaboration", "FAIL", str(e))
            return False

    def test_first_principles_analysis(self):
        """Test first principles reasoning"""
        try:
            payload = {
                "query": "Why does gravity exist?",
                "first_principles": True,
                "depth": "deep"
            }
            response = self.session.post(f"{self.base_url}/first-principles-analysis",
                                       json=payload, headers={"Content-Type": "application/json"})

            if response.status_code == 200:
                data = response.json()
                fundamentals = data.get("fundamental_principles", [])
                self.log_result("First Principles Analysis", "PASS",
                              f"Found {len(fundamentals)} fundamental principles",
                              {"principles": fundamentals[:3]})  # Show first 3
                return True
            else:
                self.log_result("First Principles Analysis", "FAIL", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_result("First Principles Analysis", "FAIL", str(e))
            return False

    def test_transparency_service(self):
        """Test transparency logging"""
        try:
            response = self.session.get(f"{self.base_url}/transparency/status")
            if response.status_code == 200:
                data = response.json()
                logs_count = data.get("total_logs", 0)
                self.log_result("Transparency Service", "PASS",
                              f"{logs_count} transparency logs available",
                              {"enabled": data.get("enabled"), "retention_days": data.get("retention_days")})
                return True
            else:
                self.log_result("Transparency Service", "FAIL", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Transparency Service", "FAIL", str(e))
            return False

    def test_performance(self):
        """Test system performance with multiple queries"""
        queries = [
            "What is E=mc²?",
            "Explain photosynthesis",
            "What is the Pythagorean theorem?"
        ]

        start_time = time.time()
        successful_queries = 0

        for i, query in enumerate(queries, 1):
            try:
                payload = {"query": query}
                response = self.session.post(f"{self.base_url}/scientific-query",
                                           json=payload, headers={"Content-Type": "application/json"})

                if response.status_code == 200:
                    successful_queries += 1
                    print(f"   Query {i}: ✅ SUCCESS")
                else:
                    print(f"   Query {i}: ❌ FAILED (HTTP {response.status_code})")
            except Exception as e:
                print(f"   Query {i}: ❌ ERROR ({str(e)})")

        total_time = time.time() - start_time
        success_rate = (successful_queries / len(queries)) * 100

        self.log_result("Performance Test", "PASS" if success_rate >= 80 else "FAIL",
                       f"{successful_queries}/{len(queries)} queries successful ({success_rate:.1f}%)",
                       {"total_time": total_time, "avg_time_per_query": total_time/len(queries)})
        return success_rate >= 80

    def run_all_tests(self):
        """Run complete system verification"""
        print("🔬 Nexus Lang V2 Scientific AI - System Verification")
        print("=" * 60)
        print(f"Testing system at: {self.base_url}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # Basic connectivity tests
        print("📡 CONNECTIVITY TESTS")
        health_ok = self.test_health_endpoint()
        docs_ok = self.test_api_docs()
        capabilities_ok = self.test_scientific_capabilities()
        print()

        if not health_ok:
            print("❌ Critical: Health check failed. System may not be running.")
            return False

        # Agent tests
        print("🧠 AGENT TESTS")
        physics_ok = self.test_physics_agent()
        chemistry_ok = self.test_chemistry_agent()
        math_ok = self.test_mathematics_agent()
        collaboration_ok = self.test_multi_agent_collaboration()
        print()

        # Advanced features
        print("⚡ ADVANCED FEATURES")
        first_principles_ok = self.test_first_principles_analysis()
        transparency_ok = self.test_transparency_service()
        print()

        # Performance test
        print("🏃 PERFORMANCE TESTS")
        performance_ok = self.test_performance()
        print()

        # Summary
        print("📊 VERIFICATION SUMMARY")
        print("=" * 60)

        passed = sum(1 for r in self.results if r["status"] == "PASS")
        failed = sum(1 for r in self.results if r["status"] == "FAIL")
        total = len(self.results)

        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(".1f"
        print()

        if failed == 0:
            print("🎉 ALL TESTS PASSED! System is fully operational.")
            return True
        elif failed <= 2:
            print("⚠️  Minor issues detected. System mostly functional.")
            return True
        else:
            print("❌ Critical issues detected. System needs attention.")
            return False

    def save_report(self, filename="system_verification_report.json"):
        """Save detailed test results to file"""
        with open(filename, 'w') as f:
            json.dump({
                "verification_timestamp": datetime.now().isoformat(),
                "base_url": self.base_url,
                "summary": {
                    "total_tests": len(self.results),
                    "passed": sum(1 for r in self.results if r["status"] == "PASS"),
                    "failed": sum(1 for r in self.results if r["status"] == "FAIL")
                },
                "results": self.results
            }, f, indent=2)
        print(f"📄 Detailed report saved to: {filename}")


def main():
    """Main verification function"""
    import argparse

    parser = argparse.ArgumentParser(description="Verify Nexus Lang V2 Scientific AI system")
    parser.add_argument("--url", default="http://localhost:8000",
                       help="Base URL of the API (default: http://localhost:8000)")
    parser.add_argument("--save-report", action="store_true",
                       help="Save detailed report to JSON file")

    args = parser.parse_args()

    verifier = SystemVerifier(args.url)

    try:
        success = verifier.run_all_tests()

        if args.save_report:
            verifier.save_report()

        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n⚠️  Verification interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Verification failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
