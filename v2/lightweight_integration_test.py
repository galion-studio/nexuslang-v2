#!/usr/bin/env python3
"""
Lightweight Integration Test for Nexus Lang V2 Scientific AI System
Tests basic file structure, syntax, and configuration without requiring full dependencies
"""

import os
import sys
import ast
import json
import subprocess
from typing import Dict, List, Any

class LightweightIntegrationTest:
    """Lightweight test suite for basic validation"""

    def __init__(self):
        self.test_results = {}
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def log_test(self, test_name: str, status: str, message: str = ""):
        """Log a test result"""
        self.test_results[test_name] = {
            "status": status,
            "message": message,
            "timestamp": os.times().elapsed if hasattr(os.times(), 'elapsed') else 0
        }
        symbol = "[PASS]" if status == "PASS" else "[FAIL]" if status == "FAIL" else "[SKIP]"
        print(f"{symbol} {test_name}: {message}")

    def test_file_structure(self):
        """Test that all expected files exist"""
        expected_files = [
            'v2/backend/api/grokopedia.py',
            'v2/backend/services/agents/agent_orchestrator.py',
            'v2/backend/services/agents/physics_agent.py',
            'v2/backend/services/agents/chemistry_agent.py',
            'v2/backend/services/agents/mathematics_agent.py',
            'v2/backend/services/transparency_service.py',
            'v2/scientific_sdk.py',
            'requirements.txt',
            'runpod.Dockerfile',
            'examples/scientific_research_assistant.py',
            'examples/scientific_education_tool.py',
            'examples/scientific_data_analyzer.py'
        ]

        missing_files = []
        for file_path in expected_files:
            if not os.path.exists(os.path.join(self.project_root, file_path)):
                missing_files.append(file_path)

        if missing_files:
            return {"success": False, "error": f"Missing files: {', '.join(missing_files)}"}

        return {"success": True, "message": f"All {len(expected_files)} expected files found"}

    def test_python_syntax(self):
        """Test that all Python files have valid syntax"""
        python_files = [
            'v2/backend/api/grokopedia.py',
            'v2/backend/services/agents/agent_orchestrator.py',
            'v2/backend/services/agents/physics_agent.py',
            'v2/backend/services/agents/chemistry_agent.py',
            'v2/backend/services/agents/mathematics_agent.py',
            'v2/backend/services/transparency_service.py',
            'v2/scientific_sdk.py',
            'v2/scientific_performance_benchmark.py',
            'v2/simple_scientific_test.py',
            'examples/scientific_research_assistant.py',
            'examples/scientific_education_tool.py',
            'examples/scientific_data_analyzer.py'
        ]

        syntax_errors = []
        for file_path in python_files:
            full_path = os.path.join(self.project_root, file_path)
            if os.path.exists(full_path):
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        source = f.read()
                    ast.parse(source, filename=file_path)
                except SyntaxError as e:
                    syntax_errors.append(f"{file_path}: {e}")
                except Exception as e:
                    syntax_errors.append(f"{file_path}: {e}")

        if syntax_errors:
            return {"success": False, "error": f"Syntax errors: {'; '.join(syntax_errors)}"}

        return {"success": True, "message": f"All {len(python_files)} Python files have valid syntax"}

    def test_dockerfile_exists(self):
        """Test that Dockerfile exists and has basic structure"""
        dockerfile_path = os.path.join(self.project_root, 'runpod.Dockerfile')

        if not os.path.exists(dockerfile_path):
            return {"success": False, "error": "runpod.Dockerfile not found"}

        with open(dockerfile_path, 'r') as f:
            content = f.read()

        required_commands = ['FROM', 'COPY', 'RUN', 'CMD']
        missing_commands = []

        for cmd in required_commands:
            if f'{cmd} ' not in content:
                missing_commands.append(cmd)

        if missing_commands:
            return {"success": False, "error": f"Dockerfile missing commands: {', '.join(missing_commands)}"}

        return {"success": True, "message": "Dockerfile has proper structure"}

    def test_requirements_structure(self):
        """Test that requirements.txt exists and has expected packages"""
        req_path = os.path.join(self.project_root, 'requirements.txt')

        if not os.path.exists(req_path):
            return {"success": False, "error": "requirements.txt not found"}

        with open(req_path, 'r') as f:
            content = f.read()

        expected_packages = ['fastapi', 'pydantic', 'aiohttp', 'psutil']
        missing_packages = []

        for package in expected_packages:
            if package not in content:
                missing_packages.append(package)

        if missing_packages:
            return {"success": False, "error": f"requirements.txt missing packages: {', '.join(missing_packages)}"}

        return {"success": True, "message": "requirements.txt contains all expected packages"}

    def test_configuration_files(self):
        """Test that configuration files exist"""
        config_files = [
            'runpod-config.yaml',
            'runpod-env-template.sh',
            'deploy-runpod.sh'
        ]

        missing_configs = []
        for config_file in config_files:
            if not os.path.exists(os.path.join(self.project_root, config_file)):
                missing_configs.append(config_file)

        if missing_configs:
            return {"success": False, "error": f"Missing configuration files: {', '.join(missing_configs)}"}

        return {"success": True, "message": f"All {len(config_files)} configuration files found"}

    def test_documentation_files(self):
        """Test that documentation files exist"""
        doc_files = [
            ('README.md', ''),
            ('QUICK_START_GUIDE.md', ''),
            ('PROJECT_COMPLETION_SUMMARY.md', ''),
            ('RUNPOD_DEPLOYMENT_README.md', ''),
            ('v2/SCIENTIFIC_KNOWLEDGE_README.md', 'v2/'),
            ('v2/SCIENTIFIC_API_REFERENCE.md', 'v2/'),
            ('v2/SCIENTIFIC_KNOWLEDGE_DEPLOYMENT_GUIDE.md', 'v2/'),
            ('v2/INTEGRATION_GUIDE.md', 'v2/')
        ]

        missing_docs = []
        for doc_file, subdir in doc_files:
            full_path = os.path.join(self.project_root, doc_file)
            if not os.path.exists(full_path):
                missing_docs.append(doc_file)

        if missing_docs:
            return {"success": False, "error": f"Missing documentation files: {', '.join(missing_docs)}"}

        return {"success": True, "message": f"All {len(doc_files)} documentation files found"}

    def test_example_applications(self):
        """Test that example applications are properly structured"""
        examples_dir = os.path.join(self.project_root, 'examples')

        if not os.path.exists(examples_dir):
            return {"success": False, "error": "examples directory not found"}

        example_files = [
            'scientific_research_assistant.py',
            'scientific_education_tool.py',
            'scientific_data_analyzer.py',
            'README.md'
        ]

        missing_examples = []
        for example_file in example_files:
            if not os.path.exists(os.path.join(examples_dir, example_file)):
                missing_examples.append(example_file)

        if missing_examples:
            return {"success": False, "error": f"Missing example files: {', '.join(missing_examples)}"}

        return {"success": True, "message": f"All {len(example_files)} example files found"}

    def generate_report(self):
        """Generate comprehensive test report"""
        passed = sum(1 for r in self.test_results.values() if r["status"] == "PASS")
        failed = sum(1 for r in self.test_results.values() if r["status"] == "FAIL")
        total = len(self.test_results)

        print("\n" + "="*70)
        print("LIGHTWEIGHT INTEGRATION TEST REPORT")
        print("="*70)
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(".1f")

        if failed > 0:
            print("\nFAILED TESTS:")
            for test_name, result in self.test_results.items():
                if result["status"] == "FAIL":
                    print(f"  - {test_name}: {result['message']}")

        print("\n" + "="*70)

        # Save detailed report
        report_path = os.path.join(self.project_root, 'lightweight_test_report.json')
        with open(report_path, 'w') as f:
            json.dump({
                "summary": {
                    "total_tests": total,
                    "passed": passed,
                    "failed": failed,
                    "success_rate": (passed/total)*100 if total > 0 else 0
                },
                "results": self.test_results,
                "timestamp": os.times().elapsed if hasattr(os.times(), 'elapsed') else 0
            }, f, indent=2)

        print(f"Detailed report saved to: {report_path}")

        return passed == total

    def run_all_tests(self):
        """Run the complete lightweight test suite"""
        print("Running Lightweight Integration Tests for Nexus Lang V2 Scientific AI...")
        print("="*70)

        # Run all tests
        result = self.test_file_structure()
        self.log_test("File Structure", "PASS" if result["success"] else "FAIL", result.get("message", result.get("error", "")))

        result = self.test_python_syntax()
        self.log_test("Python Syntax", "PASS" if result["success"] else "FAIL", result.get("message", result.get("error", "")))

        result = self.test_dockerfile_exists()
        self.log_test("Dockerfile Structure", "PASS" if result["success"] else "FAIL", result.get("message", result.get("error", "")))

        result = self.test_requirements_structure()
        self.log_test("Requirements Structure", "PASS" if result["success"] else "FAIL", result.get("message", result.get("error", "")))

        result = self.test_configuration_files()
        self.log_test("Configuration Files", "PASS" if result["success"] else "FAIL", result.get("message", result.get("error", "")))

        result = self.test_documentation_files()
        self.log_test("Documentation Files", "PASS" if result["success"] else "FAIL", result.get("message", result.get("error", "")))

        result = self.test_example_applications()
        self.log_test("Example Applications", "PASS" if result["success"] else "FAIL", result.get("message", result.get("error", "")))

        # Generate final report
        success = self.generate_report()
        return success

if __name__ == "__main__":
    test_suite = LightweightIntegrationTest()
    success = test_suite.run_all_tests()

    if success:
        print("\n[SUCCESS] All lightweight integration tests passed!")
        print("The Nexus Lang V2 Scientific AI system structure is valid.")
        print("Note: Full functionality requires installing dependencies with:")
        print("  pip install -r requirements.txt")
    else:
        print("\n[FAILED] Some tests failed!")
        print("Please review the test report and fix the issues.")

    sys.exit(0 if success else 1)
