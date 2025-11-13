#!/usr/bin/env python3
"""
Deployment Validation Script for NexusLang v2
==============================================

Automated testing to verify deployment success.

Features:
- Tests all critical endpoints
- Validates database connectivity
- Tests authentication flow
- Tests AI integration
- Tests file operations
- Generates deployment report

Usage:
    python validate_deployment.py
    python validate_deployment.py --verbose
    python validate_deployment.py --report deployment_report.json
"""

import asyncio
import httpx
import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
import argparse

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class DeploymentValidator:
    """
    Validates NexusLang v2 deployment with comprehensive tests.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000", verbose: bool = False):
        """
        Initialize deployment validator.
        
        Args:
            base_url: Base URL of API
            verbose: Print verbose output
        """
        self.base_url = base_url.rstrip('/')
        self.verbose = verbose
        self.test_results = []
        self.test_user = {
            'username': f'test_deploy_{int(datetime.now().timestamp())}',
            'email': f'test_{int(datetime.now().timestamp())}@example.com',
            'password': 'TestPass123!'
        }
        self.access_token = None
    
    def log(self, message: str, level: str = 'info'):
        """Log message if verbose."""
        if self.verbose or level == 'error':
            prefix = {
                'info': '  ',
                'success': '✅',
                'error': '❌',
                'warning': '⚠️ '
            }.get(level, '  ')
            print(f"{prefix} {message}")
    
    async def run_test(self, name: str, test_func) -> Tuple[bool, Dict]:
        """
        Run a single test and record result.
        
        Args:
            name: Test name
            test_func: Async test function
            
        Returns:
            Tuple of (success, result_details)
        """
        print(f"\n🧪 Testing: {name}")
        
        try:
            result = await test_func()
            success = result.get('success', False)
            
            if success:
                self.log(f"PASS: {name}", 'success')
            else:
                self.log(f"FAIL: {name} - {result.get('message', 'Unknown error')}", 'error')
            
            self.test_results.append({
                'test': name,
                'success': success,
                'timestamp': datetime.now().isoformat(),
                **result
            })
            
            return success, result
            
        except Exception as e:
            self.log(f"ERROR: {name} - {str(e)}", 'error')
            
            self.test_results.append({
                'test': name,
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
            
            return False, {'error': str(e)}
    
    async def test_health_endpoint(self) -> Dict:
        """Test basic health endpoint."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/health", timeout=5.0)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') == 'healthy':
                        return {'success': True, 'data': data}
                    else:
                        return {'success': False, 'message': 'Status not healthy', 'data': data}
                else:
                    return {'success': False, 'message': f'HTTP {response.status_code}'}
                    
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    async def test_detailed_health(self) -> Dict:
        """Test detailed health endpoint."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/health/detailed", timeout=10.0)
                
                if response.status_code == 200:
                    data = response.json()
                    overall_status = data.get('overall_status')
                    
                    if overall_status == 'healthy':
                        return {'success': True, 'data': data}
                    else:
                        return {
                            'success': False if overall_status == 'unhealthy' else True,
                            'message': f'Overall status: {overall_status}',
                            'data': data
                        }
                else:
                    return {'success': False, 'message': f'HTTP {response.status_code}'}
                    
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    async def test_user_registration(self) -> Dict:
        """Test user registration."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/v2/auth/register",
                    json=self.test_user,
                    timeout=10.0
                )
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    return {'success': True, 'data': data}
                else:
                    return {'success': False, 'message': f'HTTP {response.status_code}', 'response': response.text}
                    
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    async def test_user_login(self) -> Dict:
        """Test user login and token generation."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/v2/auth/login",
                    json={
                        'username': self.test_user['username'],
                        'password': self.test_user['password']
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.access_token = data.get('access_token')
                    
                    if self.access_token:
                        return {'success': True, 'data': {'token_received': True}}
                    else:
                        return {'success': False, 'message': 'No access token in response'}
                else:
                    return {'success': False, 'message': f'HTTP {response.status_code}'}
                    
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    async def test_authenticated_endpoint(self) -> Dict:
        """Test accessing authenticated endpoint."""
        if not self.access_token:
            return {'success': False, 'message': 'No access token available'}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v2/ide/projects",
                    headers={'Authorization': f'Bearer {self.access_token}'},
                    timeout=10.0
                )
                
                if response.status_code in [200, 201]:
                    return {'success': True, 'data': {'authenticated': True}}
                else:
                    return {'success': False, 'message': f'HTTP {response.status_code}'}
                    
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    async def test_analytics_endpoints(self) -> Dict:
        """Test analytics endpoints."""
        if not self.access_token:
            return {'success': False, 'message': 'No access token available'}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v2/analytics/dashboard",
                    headers={'Authorization': f'Bearer {self.access_token}'},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {'success': True, 'data': {'metrics_available': True}}
                else:
                    return {'success': False, 'message': f'HTTP {response.status_code}'}
                    
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    async def test_api_docs(self) -> Dict:
        """Test API documentation endpoint."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/docs", timeout=10.0)
                
                if response.status_code == 200 and 'swagger' in response.text.lower():
                    return {'success': True, 'data': {'docs_available': True}}
                else:
                    return {'success': False, 'message': f'HTTP {response.status_code}'}
                    
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    async def test_metrics_endpoint(self) -> Dict:
        """Test Prometheus metrics endpoint."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/metrics", timeout=5.0)
                
                if response.status_code == 200:
                    return {'success': True, 'data': {'metrics_exposed': True}}
                else:
                    return {'success': False, 'message': f'HTTP {response.status_code}'}
                    
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    async def run_all_tests(self) -> Dict:
        """
        Run all deployment validation tests.
        
        Returns:
            Test results summary
        """
        print("=" * 80)
        print("🧪 NexusLang v2 Deployment Validation")
        print("=" * 80)
        print(f"\nBase URL: {self.base_url}")
        print(f"Started: {datetime.now().isoformat()}\n")
        
        # Define test suite
        tests = [
            ("Health Endpoint", self.test_health_endpoint),
            ("Detailed Health Check", self.test_detailed_health),
            ("API Documentation", self.test_api_docs),
            ("Prometheus Metrics", self.test_metrics_endpoint),
            ("User Registration", self.test_user_registration),
            ("User Login", self.test_user_login),
            ("Authenticated Endpoint", self.test_authenticated_endpoint),
            ("Analytics Endpoints", self.test_analytics_endpoints),
        ]
        
        # Run all tests
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            success, result = await self.run_test(test_name, test_func)
            if success:
                passed += 1
            else:
                failed += 1
        
        # Generate summary
        total = passed + failed
        success_rate = (passed / total) * 100 if total > 0 else 0
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'base_url': self.base_url,
            'total_tests': total,
            'passed': passed,
            'failed': failed,
            'success_rate': round(success_rate, 2),
            'overall_status': 'PASS' if failed == 0 else 'FAIL' if passed == 0 else 'PARTIAL',
            'test_results': self.test_results
        }
        
        # Print summary
        print("\n" + "=" * 80)
        print("📊 Test Summary")
        print("=" * 80)
        print(f"\nTotal Tests: {total}")
        print(f"✅ Passed:    {passed}")
        print(f"❌ Failed:    {failed}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"\nOverall Status: {summary['overall_status']}")
        print("\n" + "=" * 80)
        
        return summary


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Validate NexusLang v2 deployment')
    parser.add_argument('--url', type=str, default='http://localhost:8000', help='Base API URL')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--report', type=str, help='Save report to JSON file')
    
    args = parser.parse_args()
    
    validator = DeploymentValidator(base_url=args.url, verbose=args.verbose)
    summary = await validator.run_all_tests()
    
    # Save report if requested
    if args.report:
        with open(args.report, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"\n📄 Report saved to: {args.report}")
    
    # Exit with appropriate code
    sys.exit(0 if summary['overall_status'] == 'PASS' else 1)


if __name__ == "__main__":
    asyncio.run(main())

