"""
Base Agent Framework for Galion Platform v2.2
Implements personality-driven AI agents with consistent execution patterns.

"Your imagination is the end."
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
import time
import logging

# Configure logging
logger = logging.getLogger(__name__)

class PersonalityTraits(BaseModel):
    """Personality traits that define agent behavior and response style"""

    analytical: float = Field(default=0.5, ge=0.0, le=1.0, description="Analytical thinking capability")
    creative: float = Field(default=0.5, ge=0.0, le=1.0, description="Creative problem solving")
    empathetic: float = Field(default=0.5, ge=0.0, le=1.0, description="Empathy and emotional intelligence")
    precision: float = Field(default=0.5, ge=0.0, le=1.0, description="Attention to detail and accuracy")
    helpful: float = Field(default=0.5, ge=0.0, le=1.0, description="Helpfulness and user support")
    humor: float = Field(default=0.0, ge=0.0, le=1.0, description="Sense of humor and lightheartedness")
    directness: float = Field(default=0.5, ge=0.0, le=1.0, description="Direct vs. diplomatic communication")
    curiosity: float = Field(default=0.5, ge=0.0, le=1.0, description="Curiosity and learning orientation")

    def get_trait_description(self) -> str:
        """Get a human-readable description of personality traits"""
        traits = []
        if self.analytical > 0.7:
            traits.append("highly analytical")
        if self.creative > 0.7:
            traits.append("highly creative")
        if self.empathetic > 0.7:
            traits.append("deeply empathetic")
        if self.precision > 0.8:
            traits.append("meticulously precise")
        if self.helpful > 0.8:
            traits.append("exceptionally helpful")
        if self.humor > 0.6:
            traits.append("witty and humorous")
        if self.directness > 0.8:
            traits.append("bluntly direct")
        if self.curiosity > 0.7:
            traits.append("intensely curious")

        return ", ".join(traits) if traits else "balanced and adaptable"

class AgentCapabilities(BaseModel):
    """Capabilities and limitations of the agent"""

    can_execute_code: bool = False
    can_access_filesystem: bool = False
    can_make_api_calls: bool = True
    can_generate_content: bool = True
    can_analyze_data: bool = False
    can_interact_with_users: bool = True
    can_schedule_tasks: bool = False
    can_monitor_systems: bool = False

    supported_languages: List[str] = Field(default_factory=lambda: ["en"])
    expertise_domains: List[str] = Field(default_factory=list)
    tool_access: List[str] = Field(default_factory=list)

class AgentResult(BaseModel):
    """Standardized result format for all agent executions"""

    success: bool
    response: str
    cost: float = 0.0
    execution_time: float = 0.0
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    confidence_score: Optional[float] = None
    next_actions: List[str] = Field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return self.model_dump()

class AgentContext(BaseModel):
    """Context information passed to agents"""

    user_id: Optional[str] = None
    session_id: Optional[str] = None
    conversation_history: List[Dict[str, Any]] = Field(default_factory=list)
    user_preferences: Dict[str, Any] = Field(default_factory=dict)
    system_state: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class BaseAgent(ABC):
    """
    Base class for all AI agents in the Galion Platform.

    Each agent has:
    - A unique name and personality
    - Specific capabilities and limitations
    - Standardized execution patterns
    - Cost tracking and performance monitoring
    """

    def __init__(
        self,
        name: str,
        personality: PersonalityTraits,
        capabilities: AgentCapabilities,
        description: str = "",
        version: str = "1.0.0"
    ):
        self.name = name
        self.personality = personality
        self.capabilities = capabilities
        self.description = description or f"AI agent specialized in {', '.join(capabilities.expertise_domains)}"
        self.version = version

        # Runtime state
        self.execution_count = 0
        self.total_cost = 0.0
        self.average_execution_time = 0.0
        self.success_rate = 1.0
        self.last_execution = None

        # Initialize logging
        self.logger = logging.getLogger(f"{__name__}.{self.name}")

    @abstractmethod
    async def execute(
        self,
        prompt: str,
        context: Optional[AgentContext] = None,
        **kwargs
    ) -> AgentResult:
        """
        Execute the agent's primary function.

        Args:
            prompt: The user's request or task
            context: Additional context information
            **kwargs: Agent-specific parameters

        Returns:
            AgentResult with response and metadata
        """
        pass

    async def analyze_intent(self, prompt: str) -> Dict[str, Any]:
        """
        Analyze the user's intent from their prompt.

        Returns:
            Dictionary with intent analysis
        """
        # Basic intent analysis - can be overridden by subclasses
        prompt_lower = prompt.lower()

        intent_data = {
            "primary_intent": "unknown",
            "confidence": 0.5,
            "urgency": "normal",
            "sentiment": "neutral",
            "key_topics": [],
            "requires_action": False,
            "complexity": "simple"
        }

        # Simple keyword-based intent detection
        if any(word in prompt_lower for word in ["help", "assist", "support"]):
            intent_data["primary_intent"] = "help_request"
            intent_data["requires_action"] = True
        elif any(word in prompt_lower for word in ["analyze", "review", "examine"]):
            intent_data["primary_intent"] = "analysis_request"
            intent_data["complexity"] = "complex"
        elif any(word in prompt_lower for word in ["create", "build", "generate"]):
            intent_data["primary_intent"] = "creation_request"
            intent_data["requires_action"] = True
        elif any(word in prompt_lower for word in ["question", "what", "how", "why"]):
            intent_data["primary_intent"] = "information_request"

        return intent_data

    async def validate_request(self, prompt: str, context: Optional[AgentContext] = None) -> Dict[str, Any]:
        """
        Validate that the agent can handle this request.

        Returns:
            Validation result with reasoning
        """
        validation = {
            "can_handle": True,
            "reasoning": [],
            "warnings": [],
            "suggested_alternatives": []
        }

        # Check if prompt is too long
        if len(prompt) > 10000:
            validation["warnings"].append("Prompt is very long, response may be truncated")

        # Check language support
        if context and context.user_preferences.get("language"):
            user_lang = context.user_preferences["language"]
            if user_lang not in self.capabilities.supported_languages:
                validation["warnings"].append(f"Limited support for language: {user_lang}")

        # Check capability alignment
        intent = await self.analyze_intent(prompt)
        if intent["complexity"] == "complex" and not self.capabilities.can_analyze_data:
            validation["warnings"].append("Complex analysis requested but agent has limited analytical capabilities")

        return validation

    def get_status(self) -> Dict[str, Any]:
        """Get current agent status and metrics"""
        return {
            "name": self.name,
            "version": self.version,
            "status": "active",
            "execution_count": self.execution_count,
            "total_cost": self.total_cost,
            "average_execution_time": self.average_execution_time,
            "success_rate": self.success_rate,
            "last_execution": self.last_execution.isoformat() if self.last_execution else None,
            "capabilities": self.capabilities.model_dump(),
            "personality": self.personality.model_dump()
        }

    def update_metrics(self, result: AgentResult, execution_time: float):
        """Update performance metrics after execution"""
        self.execution_count += 1
        self.total_cost += result.cost
        self.last_execution = datetime.now()

        # Update average execution time
        if self.execution_count == 1:
            self.average_execution_time = execution_time
        else:
            self.average_execution_time = (
                (self.average_execution_time * (self.execution_count - 1)) + execution_time
            ) / self.execution_count

        # Update success rate
        success_count = int(result.success)
        self.success_rate = (
            (self.success_rate * (self.execution_count - 1)) + success_count
        ) / self.execution_count

    async def preprocess_prompt(self, prompt: str, context: Optional[AgentContext] = None) -> str:
        """
        Preprocess the prompt based on personality and context.

        This allows agents to adapt their input processing based on their personality traits.
        """
        processed_prompt = prompt

        # Add personality-driven context
        if self.personality.curiosity > 0.7:
            processed_prompt += "\n\nConsider exploring related concepts and asking insightful follow-up questions."

        if self.personality.analytical > 0.8:
            processed_prompt += "\n\nProvide detailed analysis with supporting evidence and data."

        if self.personality.helpful > 0.8:
            processed_prompt += "\n\nFocus on being maximally helpful and providing actionable advice."

        return processed_prompt

    async def postprocess_response(self, response: str, context: Optional[AgentContext] = None) -> str:
        """
        Postprocess the response based on personality and context.

        This allows agents to adapt their output style based on their personality traits.
        """
        processed_response = response

        # Add personality-driven formatting
        if self.personality.humor > 0.6:
            # Could add witty remarks here
            pass

        if self.personality.precise > 0.8:
            # Could add confidence indicators
            pass

        return processed_response

    def __str__(self) -> str:
        """String representation of the agent"""
        return f"{self.name} v{self.version} - {self.description}"

    def __repr__(self) -> str:
        """Detailed representation of the agent"""
        return f"BaseAgent(name='{self.name}', version='{self.version}', personality={self.personality.get_trait_description()})"

