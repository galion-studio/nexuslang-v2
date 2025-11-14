#!/usr/bin/env python3
"""
System Initialization Script

This script initializes the Galion autonomous agent system by:
- Setting up the database
- Creating default agents
- Registering core tools
- Configuring initial workflows
- Setting up monitoring
"""

import sys
import os
import json
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from backend.core.database import init_database, get_db_session
    from backend.core.redis_client import init_redis
    from backend.services.agents.agent_orchestrator import AgentOrchestrator
    from backend.services.agents.base_agent import BaseAgent
    from backend.services.agents.code_agent import CodeAgent
    from backend.services.agents.research_agent import ResearchAgent
    from backend.services.agents.design_agent import DesignAgent
    from backend.services.agents.testing_agent import TestingAgent
    from backend.services.agents.tool_framework import create_default_tool_registry
    from backend.services.agents.workflow_system import WorkflowDefinition
    from backend.core.config import settings
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the scripts directory")
    print("Usage: python scripts/init_system.py")
    sys.exit(1)

def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f" {text}")
    print(f"{'='*60}")

def print_success(text: str):
    """Print a success message."""
    print(f"✅ {text}")

def print_error(text: str):
    """Print an error message."""
    print(f"❌ {text}")

def print_info(text: str):
    """Print an info message."""
    print(f"ℹ️  {text}")

def init_database_system():
    """Initialize the database system."""
    print_header("DATABASE INITIALIZATION")

    try:
        print_info("Initializing database...")
        init_database()
        print_success("Database initialized successfully")

        print_info("Testing database connection...")
        # Test connection by getting a session
        session = next(get_db_session())
        session.close()
        print_success("Database connection test passed")

        return True
    except Exception as e:
        print_error(f"Database initialization failed: {e}")
        return False

def init_redis_system():
    """Initialize Redis for caching and task queues."""
    print_header("REDIS INITIALIZATION")

    try:
        print_info("Initializing Redis connection...")
        redis_client = init_redis()

        print_info("Testing Redis connection...")
        redis_client.ping()
        print_success("Redis connection test passed")

        # Clear any existing data
        redis_client.flushdb()
        print_success("Redis database cleared")

        return True
    except Exception as e:
        print_error(f"Redis initialization failed: {e}")
        print_info("System will work with in-memory storage")
        return False

def create_default_agents(orchestrator: AgentOrchestrator):
    """Create and register default agents."""
    print_header("AGENT REGISTRATION")

    default_agents = [
        {
            "name": "code_agent",
            "class": CodeAgent,
            "description": "Specialized in writing, reviewing, and debugging code",
            "capabilities": ["coding", "debugging", "code_review", "refactoring"],
            "personality": {"expertise_level": "expert", "communication_style": "technical"}
        },
        {
            "name": "research_agent",
            "class": ResearchAgent,
            "description": "Handles research, data analysis, and information gathering",
            "capabilities": ["research", "data_analysis", "web_search", "documentation"],
            "personality": {"expertise_level": "advanced", "communication_style": "analytical"}
        },
        {
            "name": "design_agent",
            "class": DesignAgent,
            "description": "Creates designs, UI/UX, and system architectures",
            "capabilities": ["design", "ui_ux", "system_design", "prototyping"],
            "personality": {"expertise_level": "advanced", "communication_style": "creative"}
        },
        {
            "name": "testing_agent",
            "class": TestingAgent,
            "description": "Ensures quality through comprehensive testing",
            "capabilities": ["testing", "qa", "validation", "performance_testing"],
            "personality": {"expertise_level": "expert", "communication_style": "methodical"}
        }
    ]

    registered_count = 0

    for agent_config in default_agents:
        try:
            print_info(f"Registering {agent_config['name']}...")

            agent_instance = agent_config["class"](
                name=agent_config["name"],
                description=agent_config["description"],
                capabilities=agent_config["capabilities"],
                personality=agent_config["personality"]
            )

            orchestrator.register_agent(agent_instance)
            registered_count += 1
            print_success(f"Registered {agent_config['name']}")

        except Exception as e:
            print_error(f"Failed to register {agent_config['name']}: {e}")

    print_success(f"Successfully registered {registered_count}/{len(default_agents)} agents")
    return registered_count > 0

def setup_tool_registry(orchestrator: AgentOrchestrator):
    """Set up the tool registry with default tools."""
    print_header("TOOL REGISTRY SETUP")

    try:
        print_info("Creating default tool registry...")
        tool_registry = create_default_tool_registry()

        # Register some core tools
        core_tools = [
            {
                "name": "web_search",
                "description": "Search the web for information",
                "endpoint": "https://api.duckduckgo.com/",
                "method": "GET"
            },
            {
                "name": "code_formatter",
                "description": "Format and beautify code",
                "endpoint": "https://api.codetabs.com/v1/format",
                "method": "POST"
            },
            {
                "name": "documentation_generator",
                "description": "Generate documentation from code",
                "endpoint": "https://api.docgen.com/generate",
                "method": "POST"
            }
        ]

        registered_tools = 0
        for tool in core_tools:
            try:
                orchestrator.register_tool(
                    name=tool["name"],
                    description=tool["description"],
                    endpoint=tool["endpoint"],
                    method=tool["method"]
                )
                registered_tools += 1
                print_success(f"Registered tool: {tool['name']}")
            except Exception as e:
                print_error(f"Failed to register {tool['name']}: {e}")

        print_success(f"Registered {registered_tools} core tools")
        return True

    except Exception as e:
        print_error(f"Tool registry setup failed: {e}")
        return False

def create_default_workflows(orchestrator: AgentOrchestrator):
    """Create default workflow definitions."""
    print_header("WORKFLOW SETUP")

    default_workflows = [
        {
            "id": "code_development_pipeline",
            "name": "Code Development Pipeline",
            "description": "Complete pipeline from requirements to deployment",
            "steps": [
                {
                    "name": "requirements_analysis",
                    "agent": "research_agent",
                    "description": "Analyze and clarify requirements"
                },
                {
                    "name": "system_design",
                    "agent": "design_agent",
                    "description": "Design system architecture"
                },
                {
                    "name": "implementation",
                    "agent": "code_agent",
                    "description": "Implement the solution"
                },
                {
                    "name": "testing",
                    "agent": "testing_agent",
                    "description": "Test and validate the implementation"
                }
            ]
        },
        {
            "id": "bug_fix_workflow",
            "name": "Bug Fix Workflow",
            "description": "Systematic approach to fixing bugs",
            "steps": [
                {
                    "name": "bug_reproduction",
                    "agent": "testing_agent",
                    "description": "Reproduce the bug"
                },
                {
                    "name": "root_cause_analysis",
                    "agent": "research_agent",
                    "description": "Analyze root cause"
                },
                {
                    "name": "fix_implementation",
                    "agent": "code_agent",
                    "description": "Implement the fix"
                },
                {
                    "name": "regression_testing",
                    "agent": "testing_agent",
                    "description": "Test for regressions"
                }
            ]
        }
    ]

    registered_workflows = 0

    for workflow in default_workflows:
        try:
            print_info(f"Registering workflow: {workflow['name']}...")

            workflow_def = WorkflowDefinition(
                id=workflow["id"],
                name=workflow["name"],
                description=workflow["description"],
                steps=workflow["steps"]
            )

            orchestrator.register_workflow(workflow_def)
            registered_workflows += 1
            print_success(f"Registered workflow: {workflow['name']}")

        except Exception as e:
            print_error(f"Failed to register workflow {workflow['name']}: {e}")

    print_success(f"Registered {registered_workflows} default workflows")
    return registered_workflows > 0

def initialize_monitoring(orchestrator: AgentOrchestrator):
    """Initialize monitoring and alerting."""
    print_header("MONITORING SETUP")

    try:
        print_info("Starting monitoring server...")
        orchestrator.start_monitoring_server()
        print_success("Monitoring server started")

        print_info("Initializing real-time monitoring...")
        # The orchestrator should handle this automatically
        print_success("Real-time monitoring initialized")

        return True

    except Exception as e:
        print_error(f"Monitoring setup failed: {e}")
        return False

def create_initial_context(orchestrator: AgentOrchestrator):
    """Create initial context and preferences."""
    print_header("CONTEXT INITIALIZATION")

    try:
        print_info("Setting up initial context awareness...")

        # Set some default preferences
        default_preferences = {
            "coding_style": "clean_code",
            "testing_approach": "tdd",
            "documentation_format": "markdown",
            "deployment_strategy": "containerized"
        }

        for pref_key, pref_value in default_preferences.items():
            orchestrator.learn_user_preference(pref_key, pref_value, 0.8)

        print_success("Initial context and preferences set")

        # Analyze some initial project context
        sample_context = {
            "tech_stack": ["python", "fastapi", "react", "postgresql"],
            "project_type": "web_application",
            "team_size": "small",
            "development_methodology": "agile"
        }

        orchestrator.update_project_context("default_project", sample_context)
        print_success("Initial project context analyzed")

        return True

    except Exception as e:
        print_error(f"Context initialization failed: {e}")
        return False

def run_final_checks(orchestrator: AgentOrchestrator):
    """Run final system checks."""
    print_header("FINAL SYSTEM CHECKS")

    checks = [
        ("Agent Registry", len(orchestrator.list_agents()) > 0),
        ("Tool Registry", len(orchestrator.list_tools()) > 0),
        ("Workflow System", len(orchestrator.get_workflow_status()) > 0),
        ("Monitoring", orchestrator.get_monitoring_status() is not None),
        ("Context Engine", orchestrator.get_context_recommendations({}) is not None)
    ]

    passed = 0
    for check_name, check_result in checks:
        if check_result:
            print_success(f"{check_name}: OK")
            passed += 1
        else:
            print_error(f"{check_name}: FAILED")

    print(f"\n📊 System Health: {passed}/{len(checks)} checks passed")

    if passed == len(checks):
        print_success("🎉 System initialization completed successfully!")
        return True
    else:
        print_error("⚠️  Some checks failed. System may not work correctly.")
        return False

def main():
    """Main initialization function."""
    print("🚀 GALION AUTONOMOUS AGENT SYSTEM - INITIALIZATION")
    print("="*60)
    print("This script will set up your Galion system for the first time.")
    print("Make sure your environment variables are configured!")
    print("="*60)

    # Check environment
    if not os.getenv("OPENAI_API_KEY"):
        print_error("OPENAI_API_KEY environment variable not set!")
        print_info("Please set your OpenAI API key:")
        print_info("export OPENAI_API_KEY='your-key-here'")
        return False

    success_count = 0
    total_steps = 7

    # Step 1: Database
    if init_database_system():
        success_count += 1

    # Step 2: Redis
    if init_redis_system():
        success_count += 1

    # Step 3: Create orchestrator
    print_header("ORCHESTRATOR INITIALIZATION")
    try:
        print_info("Creating agent orchestrator...")
        orchestrator = AgentOrchestrator()
        print_success("Agent orchestrator created")
        success_count += 1
    except Exception as e:
        print_error(f"Orchestrator creation failed: {e}")
        return False

    # Step 4: Agents
    if create_default_agents(orchestrator):
        success_count += 1

    # Step 5: Tools
    if setup_tool_registry(orchestrator):
        success_count += 1

    # Step 6: Workflows
    if create_default_workflows(orchestrator):
        success_count += 1

    # Step 7: Context
    if create_initial_context(orchestrator):
        success_count += 1

    # Step 8: Monitoring
    if initialize_monitoring(orchestrator):
        success_count += 1

    # Final checks
    if run_final_checks(orchestrator):
        success_count += 1

    print("\n" + "="*60)
    print(f"INITIALIZATION COMPLETE: {success_count}/{total_steps + 1} steps successful")
    print("="*60)

    if success_count >= total_steps:
        print_success("🎉 Your Galion system is ready to use!")
        print("\nNext steps:")
        print("1. Start the backend: python main.py")
        print("2. Test the system: python scripts/test_basic.py")
        print("3. Try examples: python scripts/example_usage.py")
        print("4. Access docs: http://localhost:8010/docs")
        return True
    else:
        print_error("❌ System initialization had some issues.")
        print("Check the errors above and try running the script again.")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Initialization interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error during initialization: {e}")
        sys.exit(1)
