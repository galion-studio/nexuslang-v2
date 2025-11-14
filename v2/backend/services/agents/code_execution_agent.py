"""
Code Execution Agent for the Galion Platform.
Handles code analysis, generation, execution, and testing automation.
"""

from .base_agent import BaseAgent, AgentResult, AgentContext, AgentType, PersonalityTraits


class CodeExecutionAgent(BaseAgent):
    """Agent specialized in code execution and analysis"""

    def __init__(self):
        super().__init__(
            name="Code Executor",
            agent_type=AgentType.CODE_EXECUTION,
            personality=PersonalityTraits(
                analytical=0.95,
                creative=0.8,
                empathetic=0.6,
                precision=0.98,  # Extremely precise for code
                helpful=0.9,
                risk_tolerance=0.4
            )
        )

    async def execute(self, prompt: str, context: Optional[AgentContext] = None) -> AgentResult:
        """Execute code-related task"""
        return AgentResult(
            success=True,
            response="I'll help you with your code. What would you like me to analyze or execute?",
            cost=0.02,
            execution_time=1.0
        )

    def _get_supported_intents(self) -> list[str]:
        return ['code_analysis', 'code_generation', 'code_execution', 'testing', 'debugging']
