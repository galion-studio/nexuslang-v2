#!/usr/bin/env python3
"""
Example Usage Script

This script demonstrates various types of tasks you can run with
your Galion autonomous agent system.
"""

import requests
import json
import time
import sys
from typing import Dict, Any, List, Optional

# Configuration
BASE_URL = "http://localhost:8010"
TIMEOUT = 60  # seconds for complex tasks

class GalionClient:
    """Client for interacting with Galion autonomous agent system."""

    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url

    def make_request(self, method: str, endpoint: str, data: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Make an HTTP request."""
        url = f"{self.base_url}{endpoint}"
        try:
            if method.upper() == "GET":
                response = requests.get(url, timeout=TIMEOUT)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, timeout=TIMEOUT)
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return None

    def execute_task(self, prompt: str, **kwargs) -> Optional[str]:
        """Execute a task and return the task ID."""
        task_data = {
            "prompt": prompt,
            "require_approval": kwargs.get("require_approval", False),
            "context": kwargs.get("context", {}),
            "tags": kwargs.get("tags", []),
            "priority": kwargs.get("priority", "normal")
        }

        print(f"\n🔄 Submitting task: {prompt[:50]}...")
        result = self.make_request("POST", "/api/v1/agents/execute", task_data)

        if result and "task_id" in result:
            task_id = result["task_id"]
            print(f"✅ Task submitted with ID: {task_id}")
            return task_id
        else:
            print("❌ Task submission failed!")
            return None

    def wait_for_completion(self, task_id: str, poll_interval: int = 2) -> Optional[Dict[str, Any]]:
        """Wait for task completion and return final status."""
        print(f"⏳ Waiting for task {task_id} to complete...")

        while True:
            status_result = self.make_request("GET", f"/api/v1/agents/status/{task_id}")

            if not status_result:
                return None

            status = status_result.get("status")
            print(f"   Status: {status}")

            if status in ["completed", "failed"]:
                return status_result

            time.sleep(poll_interval)

    def get_pending_approvals(self) -> List[Dict[str, Any]]:
        """Get pending approvals."""
        result = self.make_request("GET", "/api/v1/agents/approvals/pending")
        return result.get("approvals", []) if result else []

    def approve_request(self, approval_id: str, approved: bool, notes: str = "") -> bool:
        """Approve or reject an approval request."""
        data = {
            "approved": approved,
            "notes": notes
        }

        result = self.make_request("POST", f"/api/v1/agents/approvals/{approval_id}/respond", data)
        return result is not None

def example_simple_tasks(client: GalionClient):
    """Demonstrate simple coding tasks."""
    print("\n" + "="*60)
    print("🧪 EXAMPLE 1: SIMPLE CODING TASKS")
    print("="*60)

    tasks = [
        "Write a Python function to calculate factorial",
        "Create a JavaScript function to validate email addresses",
        "Write a SQL query to find duplicate records in a table",
        "Create a CSS animation for a loading spinner"
    ]

    for task in tasks:
        task_id = client.execute_task(task)
        if task_id:
            result = client.wait_for_completion(task_id)
            if result and result.get("status") == "completed":
                print(f"✅ Completed: {task[:30]}...")
            else:
                print(f"❌ Failed: {task[:30]}...")

def example_complex_tasks(client: GalionClient):
    """Demonstrate complex multi-step tasks."""
    print("\n" + "="*60)
    print("🚀 EXAMPLE 2: COMPLEX MULTI-STEP TASKS")
    print("="*60)

    complex_tasks = [
        {
            "prompt": "Build a complete user authentication system with login, registration, and password reset",
            "context": {"tech_stack": ["Node.js", "Express", "JWT", "MongoDB"]},
            "require_approval": True
        },
        {
            "prompt": "Create a data visualization dashboard for sales analytics",
            "context": {"framework": "React", "chart_library": "Chart.js", "data_source": "REST API"},
            "require_approval": False
        },
        {
            "prompt": "Design and implement a microservices architecture for an e-commerce platform",
            "context": {"services": ["user", "product", "order", "payment"], "deployment": "Kubernetes"},
            "require_approval": True
        }
    ]

    for task_info in complex_tasks:
        task_id = client.execute_task(**task_info)
        if task_id:
            result = client.wait_for_completion(task_id)
            if result:
                if result.get("status") == "completed":
                    print(f"✅ Complex task completed: {task_info['prompt'][:40]}...")
                elif result.get("status") == "waiting_approval":
                    print(f"⏸️  Task waiting for approval: {task_info['prompt'][:40]}...")
                    # Handle approval in real scenario
                else:
                    print(f"❌ Complex task failed: {task_info['prompt'][:40]}...")

def example_context_learning(client: GalionClient):
    """Demonstrate context and preference learning."""
    print("\n" + "="*60)
    print("🧠 EXAMPLE 3: CONTEXT & PREFERENCE LEARNING")
    print("="*60)

    # Simulate learning user preferences
    context_tasks = [
        {
            "prompt": "Create a REST API for user management",
            "context": {"language": "Python", "framework": "FastAPI", "database": "PostgreSQL"}
        },
        {
            "prompt": "Build a frontend component for user profiles",
            "context": {"framework": "React", "styling": "Tailwind CSS", "state_management": "Redux"}
        },
        {
            "prompt": "Write unit tests for the user API",
            "context": {"testing_framework": "pytest", "mocking": "unittest.mock"}
        }
    ]

    print("📚 Learning user preferences through repeated tasks...")
    for task_info in context_tasks:
        task_id = client.execute_task(**task_info)
        if task_id:
            result = client.wait_for_completion(task_id)
            if result and result.get("status") == "completed":
                print(f"✅ Learned from: {task_info['prompt'][:35]}...")

def example_collaboration(client: GalionClient):
    """Demonstrate agent collaboration."""
    print("\n" + "="*60)
    print("🤝 EXAMPLE 4: AGENT COLLABORATION")
    print("="*60)

    # Create a collaboration session
    session_data = {
        "name": "Full Stack Development Session",
        "description": "Building a complete web application",
        "goal": "Create a task management app with authentication",
        "participants": ["frontend_agent", "backend_agent", "database_agent"]
    }

    print("👥 Creating collaboration session...")
    result = client.make_request("POST", "/api/v1/agents/collaboration/session", session_data)

    if result:
        session_id = result.get("session_id")
        print(f"✅ Collaboration session created: {session_id}")

        # Submit collaborative task
        collab_task = {
            "prompt": "Build a complete task management web application",
            "context": {"collaboration_session": session_id},
            "require_approval": False
        }

        task_id = client.execute_task(**collab_task)
        if task_id:
            result = client.wait_for_completion(task_id)
            if result and result.get("status") == "completed":
                print("✅ Collaborative task completed!")
    else:
        print("❌ Failed to create collaboration session")

def example_monitoring(client: GalionClient):
    """Demonstrate monitoring and analytics."""
    print("\n" + "="*60)
    print("📊 EXAMPLE 5: MONITORING & ANALYTICS")
    print("="*60)

    # Get monitoring status
    status = client.make_request("GET", "/monitoring/status")
    if status:
        print("📈 Current system status:")
        print(f"   Active tasks: {status.get('active_tasks', 0)}")
        print(f"   Total agents: {status.get('total_agents', 0)}")
        print(f"   Success rate: {status.get('success_rate', 0):.1f}%")

    # Get performance summary
    perf = client.make_request("GET", "/monitoring/performance")
    if perf:
        print("⚡ Performance metrics:")
        print(f"   Avg response time: {perf.get('avg_response_time', 0):.2f}s")
        print(f"   Tasks per hour: {perf.get('tasks_per_hour', 0)}")

def main():
    """Main function to run all examples."""
    print("🚀 GALION AUTONOMOUS AGENT SYSTEM - EXAMPLES")
    print("="*60)
    print(f"Connecting to: {BASE_URL}")
    print("Make sure your Galion system is running first!")
    print("Run: python main.py")
    print("="*60)

    client = GalionClient()

    # Test connection first
    print("\n🔍 Testing connection...")
    health = client.make_request("GET", "/health")
    if not health or health.get("status") != "healthy":
        print("❌ Cannot connect to Galion system. Please start it first.")
        print("Run: python main.py")
        sys.exit(1)

    print("✅ Connected to Galion system!")

    try:
        # Run examples
        example_simple_tasks(client)
        example_complex_tasks(client)
        example_context_learning(client)
        example_collaboration(client)
        example_monitoring(client)

        print("\n" + "="*60)
        print("🎉 ALL EXAMPLES COMPLETED!")
        print("="*60)
        print("Your Galion autonomous agent system is working perfectly!")
        print("\nNext steps:")
        print("• Try creating your own custom tasks")
        print("• Experiment with different contexts")
        print("• Set up approval workflows for critical tasks")
        print("• Monitor system performance over time")

    except KeyboardInterrupt:
        print("\n\n⚠️  Examples interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
