#!/usr/bin/env python3
"""
Comprehensive Integration Test Suite for Nexus Lang V2 Scientific AI System
Tests all components: API, agents, transparency, integrations, and deployment readiness
"""

import asyncio
import time
import subprocess
import sys
import os
from typing import Dict, List, Any
import json

class IntegrationTestSuite:
    """Comprehensive test suite for the scientific AI system"""

    def __init__(self):
        self.test_results = {}
        self.start_time = time.time()
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def log_test(self, test_name: str, status: str, message: str = "", duration: float = 0):
        """Log a test result"""
        self.test_results[test_name] = {
            "status": status,
            "message": message,
            "duration": duration,
            "timestamp": time.time()
        }
        symbol = "[PASS]" if status == "PASS" else "[FAIL]" if status == "FAIL" else "[SKIP]"
        print(f"{symbol} {test_name}: {message}")

    async def run_async_test(self, test_name: str, test_func):
        """Run an async test and log results"""
        start_time = time.time()
        try:
            result = await test_func()
            duration = time.time() - start_time
            if result["success"]:
                self.log_test(test_name, "PASS", result.get("message", "Test passed"), duration)
            else:
                self.log_test(test_name, "FAIL", result.get("error", "Test failed"), duration)
        except Exception as e:
            duration = time.time() - start_time
            self.log_test(test_name, "FAIL", f"Exception: {str(e)}", duration)

    def run_sync_test(self, test_name: str, test_func):
        """Run a sync test and log results"""
        start_time = time.time()
        try:
            result = test_func()
            duration = time.time() - start_time
            if result["success"]:
                self.log_test(test_name, "PASS", result.get("message", "Test passed"), duration)
            else:
                self.log_test(test_name, "FAIL", result.get("error", "Test failed"), duration)
        except Exception as e:
            duration = time.time() - start_time
            self.log_test(test_name, "FAIL", f"Exception: {str(e)}", duration)

    async def test_api_imports(self):
        """Test that all API components can be imported"""
        try:
            sys.path.insert(0, os.path.join(self.project_root, 'v2', 'backend'))

            # Test main API imports
            from api.grokopedia import router as grokopedia_router

            # Test service imports
            from services.agents.agent_orchestrator import AgentOrchestrator
            from services.agents.physics_agent import PhysicsAgent
            from services.agents.chemistry_agent import ChemistryAgent
            from services.agents.mathematics_agent import MathematicsAgent
            from services.integrations.knowledge_integrator import KnowledgeIntegrator
            from services.transparency_service import TransparencyService

            return {"success": True, "message": "All API components imported successfully"}
        except ImportError as e:
            return {"success": False, "error": f"Import failed: {str(e)}"}

    def test_docker_build(self):
        """Test Docker container build"""
        try:
            # Change to project root
            os.chdir(self.project_root)

            # Test if Dockerfile exists
            if not os.path.exists('runpod.Dockerfile'):
                return {"success": False, "error": "runpod.Dockerfile not found"}

            # Test Docker build (dry run)
            result = subprocess.run(
                ['docker', 'build', '--dry-run', '-f', 'runpod.Dockerfile', '.'],
                capture_output=True, text=True, timeout=30
            )

            if result.returncode == 0:
                return {"success": True, "message": "Docker build validation passed"}
            else:
                return {"success": False, "error": f"Docker build failed: {result.stderr}"}

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Docker build timed out"}
        except FileNotFoundError:
            return {"success": False, "error": "Docker command not found"}
        except Exception as e:
            return {"success": False, "error": f"Docker test failed: {str(e)}"}

    def test_requirements_install(self):
        """Test that requirements can be installed"""
        try:
            os.chdir(self.project_root)

            # Check if requirements.txt exists
            if not os.path.exists('requirements.txt'):
                return {"success": False, "error": "requirements.txt not found"}

            # Test pip install --dry-run
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '--dry-run', '-r', 'requirements.txt'],
                capture_output=True, text=True, timeout=30
            )

            if result.returncode == 0:
                return {"success": True, "message": "Requirements validation passed"}
            else:
                return {"success": False, "error": f"Requirements check failed: {result.stderr}"}

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Requirements check timed out"}
        except Exception as e:
            return {"success": False, "error": f"Requirements test failed: {str(e)}"}

    async def test_agent_orchestration(self):
        """Test agent orchestration functionality"""
        try:
            sys.path.insert(0, os.path.join(self.project_root, 'v2', 'backend'))

            from services.agents.agent_orchestrator import AgentOrchestrator

            # Initialize orchestrator
            orchestrator = AgentOrchestrator()

            # Test scientific query execution
            query = "Explain Newton's laws of motion"
            result = await orchestrator.execute_scientific_query(query)

            if result and "transparency" in result:
                return {"success": True, "message": "Agent orchestration test passed"}
            else:
                return {"success": False, "error": "Agent orchestration returned invalid result"}

        except Exception as e:
            return {"success": False, "error": f"Agent orchestration test failed: {str(e)}"}

    async def test_scientific_agents(self):
        """Test individual scientific agents"""
        try:
            sys.path.insert(0, os.path.join(self.project_root, 'v2', 'backend'))

            from services.agents.physics_agent import PhysicsAgent
            from services.agents.chemistry_agent import ChemistryAgent
            from services.agents.mathematics_agent import MathematicsAgent

            # Test Physics Agent
            physics_agent = PhysicsAgent()
            physics_result = await physics_agent.process_query("Explain quantum mechanics")

            # Test Chemistry Agent
            chemistry_agent = ChemistryAgent()
            chemistry_result = await chemistry_agent.process_query("What is the structure of water?")

            # Test Mathematics Agent
            math_agent = MathematicsAgent()
            math_result = await math_agent.process_query("Solve x^2 + 2x + 1 = 0")

            if all([physics_result, chemistry_result, math_result]):
                return {"success": True, "message": "All scientific agents working"}
            else:
                return {"success": False, "error": "Some agents failed to respond"}

        except Exception as e:
            return {"success": False, "error": f"Scientific agents test failed: {str(e)}"}

    async def test_transparency_service(self):
        """Test transparency service functionality"""
        try:
            sys.path.insert(0, os.path.join(self.project_root, 'v2', 'backend'))

            from services.transparency_service import TransparencyService

            service = TransparencyService()

            # Test transparency tracking
            session_id = service.start_tracking("test_query", {"domain": "physics"})

            service.record_step(session_id, "analysis", "Analyzing physics problem")
            service.record_step(session_id, "computation", "Running calculations")

            result = service.complete_tracking(session_id, "Solution found")

            if result and "session_id" in result:
                return {"success": True, "message": "Transparency service test passed"}
            else:
                return {"success": False, "error": "Transparency service returned invalid result"}

        except Exception as e:
            return {"success": False, "error": f"Transparency service test failed: {str(e)}"}

    def test_sdk_functionality(self):
        """Test SDK imports and basic functionality"""
        try:
            # Test Python SDK
            sys.path.insert(0, os.path.join(self.project_root, 'v2'))
            import scientific_sdk

            # Test basic SDK functionality
            client = scientific_sdk.ScientificAIClient(base_url="http://localhost:8000")

            # Test JavaScript SDK exists
            js_sdk_path = os.path.join(self.project_root, 'v2', 'scientific-sdk-js.js')
            if os.path.exists(js_sdk_path):
                return {"success": True, "message": "SDK functionality test passed"}
            else:
                return {"success": False, "error": "JavaScript SDK file not found"}

        except ImportError as e:
            return {"success": False, "error": f"SDK import failed: {str(e)}"}

    def test_example_applications(self):
        """Test that example applications can be imported"""
        try:
            examples_dir = os.path.join(self.project_root, 'examples')

            # Check if examples directory exists
            if not os.path.exists(examples_dir):
                return {"success": False, "error": "Examples directory not found"}

            # Test importing example applications
            sys.path.insert(0, examples_dir)

            import scientific_research_assistant
            import scientific_education_tool
            import scientific_data_analyzer

            return {"success": True, "message": "Example applications import test passed"}

        except ImportError as e:
            return {"success": False, "error": f"Example import failed: {str(e)}"}

    async def test_performance_benchmarks(self):
        """Run performance benchmarks"""
        try:
            # Import benchmark script
            sys.path.insert(0, os.path.join(self.project_root, 'v2'))
            import scientific_performance_benchmark

            # Run benchmark
            results = await scientific_performance_benchmark.run_benchmarks()

            if results and "total_time" in results:
                return {"success": True, "message": f"Benchmarks completed in {results['total_time']:.2f}s"}
            else:
                return {"success": False, "error": "Benchmark results invalid"}

        except Exception as e:
            return {"success": False, "error": f"Performance benchmark failed: {str(e)}"}

    def generate_report(self):
        """Generate comprehensive test report"""
        total_time = time.time() - self.start_time
        passed = sum(1 for r in self.test_results.values() if r["status"] == "PASS")
        failed = sum(1 for r in self.test_results.values() if r["status"] == "FAIL")
        total = len(self.test_results)

        print("\n" + "="*60)
        print("INTEGRATION TEST REPORT")
        print("="*60)
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(".1f")
        print(".1f")

        if failed > 0:
            print("\nFAILED TESTS:")
            for test_name, result in self.test_results.items():
                if result["status"] == "FAIL":
                    print(f"  - {test_name}: {result['message']}")

        print("\n" + "="*60)

        # Save detailed report
        report_path = os.path.join(self.project_root, 'integration_test_report.json')
        with open(report_path, 'w') as f:
            json.dump({
                "summary": {
                    "total_tests": total,
                    "passed": passed,
                    "failed": failed,
                    "total_time": total_time,
                    "success_rate": (passed/total)*100 if total > 0 else 0
                },
                "results": self.test_results,
                "timestamp": time.time()
            }, f, indent=2)

        print(f"Detailed report saved to: {report_path}")

        return passed == total

    async def run_all_tests(self):
        """Run the complete integration test suite"""
        print("Starting Nexus Lang V2 Scientific AI Integration Tests...")
        print("="*60)

        # Core functionality tests
        await self.run_async_test("API Imports", self.test_api_imports)
        self.run_sync_test("Docker Build Validation", self.test_docker_build)
        self.run_sync_test("Requirements Validation", self.test_requirements_install)
        await self.run_async_test("Agent Orchestration", self.test_agent_orchestration)
        await self.run_async_test("Scientific Agents", self.test_scientific_agents)
        await self.run_async_test("Transparency Service", self.test_transparency_service)

        # Integration tests
        self.run_sync_test("SDK Functionality", self.test_sdk_functionality)
        self.run_sync_test("Example Applications", self.test_example_applications)
        await self.run_async_test("Performance Benchmarks", self.test_performance_benchmarks)

        # Generate final report
        success = self.generate_report()
        return success

async def main():
    """Main test execution"""
    suite = IntegrationTestSuite()
    success = await suite.run_all_tests()

    if success:
        print("\n[SUCCESS] ALL INTEGRATION TESTS PASSED!")
        print("Nexus Lang V2 Scientific AI System is ready for deployment.")
        return 0
    else:
        print("\n[FAILED] SOME TESTS FAILED!")
        print("Please review the test report and fix issues before deployment.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
