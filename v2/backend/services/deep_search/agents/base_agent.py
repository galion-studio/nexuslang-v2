"""
Base Agent Class for Deep Search System
Based on MushroomFleet/deep-search-persona architecture
"""

import asyncio
import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class AgentState(Enum):
    """Agent execution states"""
    IDLE = "idle"
    INITIALIZING = "initializing"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class AgentResult:
    """Result from agent execution"""
    agent_name: str
    state: AgentState
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    execution_time: float
    credits_used: float
    success: bool
    error_message: Optional[str] = None
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


class BaseAgent(ABC):
    """
    Base class for all deep search agents

    Provides common functionality:
    - State management
    - Execution timing
    - Error handling
    - Credit tracking
    - Logging
    """

    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        self.state = AgentState.IDLE
        self.start_time = None
        self.execution_time = 0.0
        self.credits_used = 0.0

        # Configure logging
        self.logger = logging.getLogger(f"{__name__}.{name}")

        # Initialize agent-specific components
        self._initialize()

    def _initialize(self):
        """Initialize agent-specific components"""
        pass

    @abstractmethod
    async def execute(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> AgentResult:
        """
        Execute the agent's main logic

        Args:
            input_data: Input data for the agent
            context: Additional context information

        Returns:
            AgentResult with execution results
        """
        pass

    async def _execute_with_monitoring(self, input_data: Dict[str, Any], context: Dict[str, Any] = None) -> AgentResult:
        """
        Execute agent with monitoring and error handling

        This wrapper provides:
        - State management
        - Timing
        - Error handling
        - Logging
        """
        try:
            # Update state
            self.state = AgentState.INITIALIZING
            self.start_time = time.time()

            self.logger.info(f"Starting execution of agent: {self.name}")

            # Execute agent logic
            self.state = AgentState.RUNNING
            result = await self.execute(input_data, context)

            # Calculate execution time
            self.execution_time = time.time() - self.start_time
            result.execution_time = self.execution_time
            result.credits_used = self.credits_used

            # Update final state
            self.state = AgentState.COMPLETED
            result.state = AgentState.COMPLETED
            result.success = True

            self.logger.info(f"Agent {self.name} completed successfully in {self.execution_time:.2f}s")

            return result

        except asyncio.TimeoutError:
            self.state = AgentState.TIMEOUT
            self.execution_time = time.time() - self.start_time
            error_msg = f"Agent {self.name} timed out after {self.execution_time:.2f}s"
            self.logger.error(error_msg)
            return self._create_error_result(error_msg, AgentState.TIMEOUT)

        except Exception as e:
            self.state = AgentState.FAILED
            self.execution_time = time.time() - (self.start_time or time.time())
            error_msg = f"Agent {self.name} failed: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return self._create_error_result(error_msg, AgentState.FAILED)

    def _create_error_result(self, error_message: str, state: AgentState) -> AgentResult:
        """Create an error result"""
        return AgentResult(
            agent_name=self.name,
            state=state,
            data={},
            metadata={"error": error_message},
            execution_time=self.execution_time,
            credits_used=self.credits_used,
            success=False,
            error_message=error_message
        )

    def _track_credits(self, credits: float):
        """Track credits used by this agent"""
        self.credits_used += credits

    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "name": self.name,
            "state": self.state.value,
            "execution_time": self.execution_time,
            "credits_used": self.credits_used,
            "config": self.config
        }

    def reset(self):
        """Reset agent state for reuse"""
        self.state = AgentState.IDLE
        self.start_time = None
        self.execution_time = 0.0
        self.credits_used = 0.0
        self.logger.info(f"Agent {self.name} reset")

    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Validate input data before execution

        Override in subclasses for specific validation
        """
        return True

    async def validate_output(self, result: AgentResult) -> bool:
        """
        Validate output data after execution

        Override in subclasses for specific validation
        """
        return result.success
