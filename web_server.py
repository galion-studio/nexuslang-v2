#!/usr/bin/env python3
"""
Galion Agent System v2.2 - Web Interface Server
A beautiful web interface for interacting with the AI agents.
"""

import logging
import sys
import os
from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
import asyncio

# Add v2/backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'v2', 'backend'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global agent system
agent_system = None

def initialize_agents():
    """Initialize the agent system synchronously"""
    global agent_system
    if agent_system is not None:
        return agent_system

    try:
        logger.info("🌐 Initializing Web Agent System")

        # Import agent components
        from services.agents.agent_orchestrator import AgentOrchestrator
        from services.agents.financial_advisor import FinancialAdvisorAgent
        from services.agents.customer_support import CustomerSupportAgent
        from services.agents.monitoring_agent import MonitoringAgent

        # Create orchestrator
        orchestrator = AgentOrchestrator()

        # Create and register agents
        fa_agent = FinancialAdvisorAgent()
        cs_agent = CustomerSupportAgent()
        mon_agent = MonitoringAgent()

        orchestrator.register_agent(fa_agent)
        orchestrator.register_agent(cs_agent)
        orchestrator.register_agent(mon_agent)

        # Start the orchestrator
        orchestrator.start_queue_processor()

        agent_system = {
            'orchestrator': orchestrator,
            'agents': orchestrator.agents,
            'request_count': 0
        }

        logger.info("✅ Web Agent System ready")
        return agent_system

    except Exception as e:
        logger.error(f"❌ Failed to initialize web agent system: {e}")
        raise

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# HTML template as string
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Galion Agent System v2.2 - Interactive Demo</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; color: #333; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; margin-bottom: 40px; color: white; }
        .header h1 { font-size: 3rem; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
        .header p { font-size: 1.2rem; opacity: 0.9; }
        .agents-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 30px; margin-bottom: 40px; }
        .agent-card { background: white; border-radius: 20px; padding: 30px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); transition: transform 0.3s ease; }
        .agent-card:hover { transform: translateY(-10px); }
        .agent-icon { width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 24px; margin-bottom: 20px; }
        .financial-icon { background: linear-gradient(45deg, #4CAF50, #45a049); }
        .support-icon { background: linear-gradient(45deg, #2196F3, #1976D2); }
        .monitoring-icon { background: linear-gradient(45deg, #FF9800, #F57C00); }
        .chat-interface { background: white; border-radius: 20px; padding: 30px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); margin-bottom: 30px; }
        .chat-messages { height: 300px; overflow-y: auto; border: 2px solid #f0f0f0; border-radius: 10px; padding: 20px; margin-bottom: 20px; background: #fafafa; }
        .message { margin-bottom: 15px; padding: 12px 16px; border-radius: 18px; max-width: 70%; }
        .message.user { background: linear-gradient(135deg, #667eea, #764ba2); color: white; margin-left: auto; }
        .message.agent { background: #f0f0f0; color: #333; }
        .chat-input { display: flex; gap: 10px; }
        .chat-input select, .chat-input input { flex: 1; padding: 12px 16px; border: 2px solid #e0e0e0; border-radius: 25px; font-size: 1rem; outline: none; }
        .chat-input button { padding: 12px 24px; background: linear-gradient(135deg, #667eea, #764ba2); color: white; border: none; border-radius: 25px; font-size: 1rem; cursor: pointer; }
        .status-bar { background: white; border-radius: 20px; padding: 20px; box-shadow: 0 10px 20px rgba(0,0,0,0.1); display: flex; justify-content: space-around; align-items: center; flex-wrap: wrap; }
        .status-item { text-align: center; padding: 10px; }
        .status-item h4 { color: #666; font-size: 0.9rem; margin-bottom: 5px; }
        .status-item .value { font-size: 1.5rem; font-weight: bold; color: #333; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        .message { animation: fadeIn 0.3s ease; }
        @media (max-width: 768px) { .agents-grid { grid-template-columns: 1fr; } .header h1 { font-size: 2rem; } .status-bar { flex-direction: column; gap: 15px; } }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Galion Agent System v2.2</h1>
            <p>Interactive Multi-Agent AI Platform</p>
        </div>

        <div class="agents-grid">
            <div class="agent-card">
                <div class="agent-icon financial-icon">💰</div>
                <h3>Financial Advisor</h3>
                <p>Expert financial guidance with personalized investment strategies.</p>
            </div>
            <div class="agent-card">
                <div class="agent-icon support-icon">🎧</div>
                <h3>Customer Support</h3>
                <p>Empathetic customer assistance with issue resolution.</p>
            </div>
            <div class="agent-card">
                <div class="agent-icon monitoring-icon">📊</div>
                <h3>Monitoring Agent</h3>
                <p>System health monitoring and performance analytics.</p>
            </div>
        </div>

        <div class="chat-interface">
            <h2 style="margin-bottom: 20px;">Interactive Agent Chat</h2>
            <div id="chat-messages" class="chat-messages">
                <div class="message agent">Welcome to the Galion Agent System v2.2! Choose an agent and ask them anything!</div>
            </div>
            <div class="chat-input">
                <select id="agent-select">
                    <option value="Financial Advisor">💰 Financial Advisor</option>
                    <option value="Customer Support">🎧 Customer Support</option>
                    <option value="Monitoring">📊 Monitoring Agent</option>
                </select>
                <input type="text" id="message-input" placeholder="Ask me anything..." />
                <button id="send-button" onclick="sendMessage()">Send</button>
            </div>
        </div>

        <div class="status-bar">
            <div class="status-item"><h4>System Status</h4><div class="value" id="system-status">Online</div></div>
            <div class="status-item"><h4>Active Agents</h4><div class="value" id="active-agents">3</div></div>
            <div class="status-item"><h4>Requests Today</h4><div class="value" id="requests-count">0</div></div>
            <div class="status-item"><h4>Avg Response</h4><div class="value" id="avg-response-time">~2.5s</div></div>
        </div>
    </div>

    <script>
        async function sendMessage() {
            const agentSelect = document.getElementById('agent-select');
            const messageInput = document.getElementById('message-input');
            const sendButton = document.getElementById('send-button');
            const chatMessages = document.getElementById('chat-messages');

            const agent = agentSelect.value;
            const message = messageInput.value.trim();

            if (!message) return;

            messageInput.disabled = true;
            sendButton.disabled = true;
            sendButton.innerHTML = 'Sending...';

            addMessage('user', 'You', message);

            try {
                const response = await fetch('/api/agents/execute', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ agent: agent, prompt: message })
                });

                const result = await response.json();

                if (result.success) {
                    addMessage('agent', `${agent}`, result.response);
                } else {
                    addMessage('agent', 'System', `Error: ${result.response}`);
                }

                document.getElementById('requests-count').textContent = result.request_id || '1';

            } catch (error) {
                addMessage('agent', 'System', 'Sorry, I encountered an error. Please try again.');
                console.error('Error:', error);
            }

            messageInput.disabled = false;
            sendButton.disabled = false;
            sendButton.innerHTML = 'Send';
            messageInput.value = '';
            messageInput.focus();
        }

        function addMessage(type, sender, content) {
            const chatMessages = document.getElementById('chat-messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}`;
            messageDiv.innerHTML = `<div style="font-weight: bold; margin-bottom: 5px;">${sender}</div><div>${content}</div>`;
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        document.getElementById('message-input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') sendMessage();
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Serve the main web interface"""
    return HTML_TEMPLATE

@app.route('/api/agents/execute', methods=['POST'])
def execute_agent():
    """Execute an agent task via API"""
    global agent_system

    # Initialize agents if needed
    if agent_system is None:
        agent_system = initialize_agents()

    data = request.get_json()
    agent_name = data.get('agent', 'Financial Advisor')
    prompt = data.get('prompt', '')

    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    try:
        # Run async agent execution in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def run_agent():
            result = await agent_system['orchestrator'].execute(prompt, agent_name)
            agent_system['request_count'] += 1
            return {
                "success": result.success,
                "response": result.response,
                "agent": agent_name,
                "cost": result.cost,
                "execution_time": result.execution_time,
                "request_id": agent_system['request_count']
            }

        result = loop.run_until_complete(run_agent())
        loop.close()

        return jsonify(result)

    except Exception as e:
        return jsonify({
            "success": False,
            "response": f"Error: {str(e)}",
            "cost": 0.0,
            "execution_time": 0.0
        })

@app.route('/api/stats')
def get_stats():
    """Get system statistics"""
    global agent_system

    if agent_system:
        stats = {
            "total_requests": agent_system['request_count'],
            "active_agents": len(agent_system['agents']),
            "system_status": "online"
        }
    else:
        stats = {
            "total_requests": 0,
            "active_agents": 0,
            "system_status": "initializing"
        }

    return jsonify(stats)

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    global agent_system

    status = "healthy" if agent_system else "initializing"
    agents_count = len(agent_system['agents']) if agent_system else 0

    return jsonify({
        "status": status,
        "agents": agents_count,
        "timestamp": "2025-01-01T00:00:00Z"
    })

if __name__ == '__main__':
    print("🌐 Starting Galion Agent System Web Interface")
    print("📱 Web Interface: http://localhost:5000")
    print("🤖 API Endpoints: http://localhost:5000/api/")
    print("Press Ctrl+C to stop")

    # Initialize agents synchronously
    initialize_agents()

    print("✅ Agent System Ready!")
    print("🎯 Ready to serve requests!")

    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
