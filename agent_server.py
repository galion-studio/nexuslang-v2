#!/usr/bin/env python3
"""
Galion Platform v2.2 - Standalone Agent Server
A fluid, independent agent orchestration system that works beautifully.

This server provides:
- Multi-agent AI orchestration
- RESTful API for agent interaction
- Real-time agent management
- Voice-first capabilities
- Production-ready architecture

Run with: python agent_server.py
"""

import asyncio
import logging
import sys
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add v2/backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'v2', 'backend'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global agent system
agent_system = None

class AgentSystem:
    """Standalone agent orchestration system"""

    def __init__(self):
        self.orchestrator = None
        self.agents = {}
        self.is_initialized = False

    async def initialize(self):
        """Initialize the agent system"""
        try:
            logger.info("🚀 Initializing Galion Agent System v2.2")

            # Import agent components
            from services.agents.agent_orchestrator import AgentOrchestrator
            from services.agents.financial_advisor import FinancialAdvisorAgent
            from services.agents.customer_support import CustomerSupportAgent
            from services.agents.monitoring_agent import MonitoringAgent

            # Create orchestrator
            self.orchestrator = AgentOrchestrator()

            # Create and register agents
            fa_agent = FinancialAdvisorAgent()
            cs_agent = CustomerSupportAgent()
            mon_agent = MonitoringAgent()

            self.orchestrator.register_agent(fa_agent)
            self.orchestrator.register_agent(cs_agent)
            self.orchestrator.register_agent(mon_agent)

            # Start the orchestrator
            await self.orchestrator.start()

            self.agents = self.orchestrator.agents
            self.is_initialized = True

            logger.info(f"✅ Agent system initialized with {len(self.agents)} agents")
            logger.info("🎯 Financial Advisor: Expert financial guidance")
            logger.info("🎧 Customer Support: Empathetic assistance")
            logger.info("📊 Monitoring Agent: System health & analytics")

        except Exception as e:
            logger.error(f"❌ Failed to initialize agent system: {e}")
            raise

    async def get_health(self) -> Dict[str, Any]:
        """Get system health status"""
        if not self.is_initialized:
            return {"status": "initializing", "agents": 0}

        return {
            "status": "healthy",
            "agents": len(self.agents),
            "orchestrator_running": self.orchestrator is not None,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def list_agents(self) -> List[Dict[str, Any]]:
        """List all available agents"""
        if not self.is_initialized:
            return []

        agents_info = []
        for name, agent in self.agents.items():
            agents_info.append({
                "name": agent.name,
                "type": name,
                "status": "active",
                "capabilities": getattr(agent.personality, 'capabilities', {}),
                "personality": agent.personality.model_dump() if hasattr(agent.personality, 'model_dump') else {}
            })
        return agents_info

    async def execute_agent_task(self, agent_type: str, prompt: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute a task using a specific agent"""
        if not self.is_initialized:
            raise HTTPException(status_code=503, detail="Agent system not ready")

        try:
            result = await self.orchestrator.execute(prompt, agent_type, context or {})
            return {
                "success": result.success,
                "response": result.response,
                "agent": agent_type,
                "cost": result.cost,
                "execution_time": result.execution_time,
                "error": result.error
            }
        except Exception as e:
            logger.error(f"Error executing agent task: {e}")
            raise HTTPException(status_code=500, detail=str(e))

# API Models
class ExecuteRequest(BaseModel):
    prompt: str
    agent_type: Optional[str] = "auto"
    context: Optional[Dict[str, Any]] = None

class ExecuteResponse(BaseModel):
    success: bool
    response: str
    agent: str
    cost: float
    execution_time: float
    error: Optional[str] = None

# FastAPI App
app = FastAPI(
    title="Galion Agent System v2.2",
    description="Multi-Agent AI Orchestration Platform",
    version="2.2.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize agent system on startup"""
    global agent_system
    agent_system = AgentSystem()
    await agent_system.initialize()

# Routes
@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Galion Agent System v2.2",
        "status": "running",
        "agents": await agent_system.list_agents() if agent_system else [],
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """System health check"""
    return await agent_system.get_health() if agent_system else {"status": "initializing"}

@app.get("/agents")
async def list_agents():
    """List all available agents"""
    return {"agents": await agent_system.list_agents()}

@app.post("/execute", response_model=ExecuteResponse)
async def execute_task(request: ExecuteRequest):
    """Execute a task using an AI agent"""
    return await agent_system.execute_agent_task(
        request.agent_type,
        request.prompt,
        request.context
    )

@app.get("/agents/{agent_type}")
async def get_agent_info(agent_type: str):
    """Get information about a specific agent"""
    agents = await agent_system.list_agents()
    for agent in agents:
        if agent["type"] == agent_type:
            return agent
    raise HTTPException(status_code=404, detail=f"Agent {agent_type} not found")

if __name__ == "__main__":
    print("🎯 Starting Galion Agent System v2.2")
    print("📖 API Documentation: http://localhost:8001/docs")
    print("🌐 Agent Playground: http://localhost:8001")
    print("Press Ctrl+C to stop")

    uvicorn.run(
        "agent_server:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
