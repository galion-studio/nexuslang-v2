"""
Planning Agent for the Galion Platform.
Handles task planning, resource allocation, and timeline estimation.
"""

from typing import Optional
from .base_agent import BaseAgent, AgentResult, AgentContext, AgentType, PersonalityTraits


class PlanningAgent(BaseAgent):
    """Agent specialized in project planning and resource management"""

    def __init__(self):
        super().__init__(
            name="Project Planner",
            agent_type=AgentType.PLANNING,
            personality=PersonalityTraits(
                analytical=0.9,
                creative=0.7,
                empathetic=0.7,
                precision=0.85,
                helpful=0.9,
                risk_tolerance=0.5
            )
        )

    async def execute(self, prompt: str, context: Optional[AgentContext] = None) -> AgentResult:
        """Execute planning task"""
        return AgentResult(
            success=True,
            response="I'll help you plan and organize your project. What goals do you want to achieve?",
            cost=0.02,
            execution_time=1.5
        )

    def _get_supported_intents(self) -> list[str]:
        return ['project_planning', 'resource_allocation', 'timeline_estimation', 'risk_assessment']
