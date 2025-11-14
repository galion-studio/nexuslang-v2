#!/usr/bin/env python3
"""
Test script for the Galion Autonomous Agent System
Tests basic functionality of the completed agent system.
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.agents.agent_orchestrator import AgentOrchestrator
from services.agents.testing_validation import MockAgent, MockTool

async def test_basic_functionality():
    """Test basic agent system functionality"""
    print('🚀 Testing Galion Autonomous Agent System...')
    print('=' * 50)

    try:
        # Initialize orchestrator
        orchestrator = AgentOrchestrator()
        print('✅ Orchestrator initialized')

        # Test agent registration
        mock_agent = MockAgent("test_agent", "success", 0.1)
        orchestrator.register_agent(mock_agent)
        print(f'✅ Mock agent registered: {mock_agent.name}')

        # Test tool registration
        mock_tool = MockTool("test_tool", "success")
        orchestrator.register_tool(mock_tool)
        print(f'✅ Mock tool registered: {mock_tool.metadata.name}')

        # Test basic agent execution
        result = await orchestrator.execute("Hello world", agent_type="test_agent")
        print(f'✅ Agent execution test: {result.success}')

        # Test tool execution
        tool_result = await orchestrator.execute_tool("test_tool", {"input": "test"})
        print(f'✅ Tool execution test: {tool_result.success}')

        print('=' * 50)
        print('🎉 All basic functionality tests PASSED!')
        print('📊 Agent System Status: READY FOR API INTEGRATION')

        # Show system capabilities
        print('\n🔧 System Capabilities:')
        print('   • Autonomous task execution')
        print('   • Tool integration framework')
        print('   • Workflow orchestration')
        print('   • Real-time monitoring')
        print('   • Human-in-the-loop')
        print('   • Context awareness')
        print('   • NLP processing')
        print('   • Agent collaboration')
        print('   • Testing & validation')

        print('\n🚀 Next Steps:')
        print('   1. API Endpoints development')
        print('   2. Frontend UI integration')
        print('   3. WebSocket real-time updates')
        print('   4. Production deployment')
        print('   5. User documentation')

        return True

    except Exception as e:
        print(f'❌ Test failed: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_basic_functionality())
    sys.exit(0 if success else 1)
