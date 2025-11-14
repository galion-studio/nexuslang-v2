"""
Dependency injection providers for FastAPI.

Provides centralized dependency management for services and components.
"""

from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .database import DatabaseManager, get_db_session
from .cache import CacheManager
from ..services.integrations import IntegrationManager
from ..services.agents.learning_engine import LearningEngine
from ..services.agents.workflow_builder import WorkflowEngine, AgentOrchestrator
from ..services.agents.advanced_nlp import AdvancedNLPProcessor


# Global service instances (singleton pattern)
_integration_manager: IntegrationManager = None
_learning_engine: LearningEngine = None
_workflow_engine: WorkflowEngine = None
_nlp_processor: AdvancedNLPProcessor = None
_orchestrator: AgentOrchestrator = None


async def get_integration_manager() -> AsyncGenerator[IntegrationManager, None]:
    """Get integration manager instance."""
    global _integration_manager
    if _integration_manager is None:
        _integration_manager = IntegrationManager()
        await _integration_manager.initialize()
    yield _integration_manager


async def get_learning_engine() -> AsyncGenerator[LearningEngine, None]:
    """Get learning engine instance."""
    global _learning_engine
    if _learning_engine is None:
        _learning_engine = LearningEngine()
        await _learning_engine.initialize()
    yield _learning_engine


async def get_workflow_engine(orchestrator: AgentOrchestrator = Depends(get_orchestrator)) -> AsyncGenerator[WorkflowEngine, None]:
    """Get workflow engine instance."""
    global _workflow_engine
    if _workflow_engine is None:
        _workflow_engine = WorkflowEngine(orchestrator)
    yield _workflow_engine


async def get_nlp_processor() -> AsyncGenerator[AdvancedNLPProcessor, None]:
    """Get NLP processor instance."""
    global _nlp_processor
    if _nlp_processor is None:
        _nlp_processor = AdvancedNLPProcessor()
        await _nlp_processor.initialize()
    yield _nlp_processor


async def get_orchestrator() -> AsyncGenerator[AgentOrchestrator, None]:
    """Get agent orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        # Initialize orchestrator with shared state
        import os
        shared_state_path = os.path.join("data", "agent-state.json")
        os.makedirs(os.path.dirname(shared_state_path), exist_ok=True)

        _orchestrator = AgentOrchestrator(shared_state_path)

        # Initialize integrations
        integration_manager = IntegrationManager()
        await integration_manager.initialize()
        _orchestrator.integration_manager = integration_manager

        # Initialize learning engine
        learning_engine = LearningEngine()
        await learning_engine.initialize()
        # Note: Learning engine is not directly attached to orchestrator
        # It's used separately through dependency injection

    yield _orchestrator


async def get_database_manager() -> AsyncGenerator[DatabaseManager, None]:
    """Get database manager instance."""
    # This would be implemented based on your database setup
    # For now, return a placeholder
    db_manager = DatabaseManager("sqlite:///:memory:")
    await db_manager.initialize()
    yield db_manager


async def get_cache_manager() -> AsyncGenerator[CacheManager, None]:
    """Get cache manager instance."""
    cache_manager = CacheManager()
    await cache_manager.initialize()
    yield cache_manager


# Cleanup function for graceful shutdown
async def cleanup_services():
    """Clean up all service instances."""
    global _integration_manager, _learning_engine, _workflow_engine, _nlp_processor, _orchestrator

    cleanup_tasks = []

    if _integration_manager:
        cleanup_tasks.append(_integration_manager.cleanup())

    if _learning_engine:
        cleanup_tasks.append(_learning_engine.cleanup())

    if _nlp_processor:
        # NLP processor doesn't have async cleanup, but we can add it if needed
        pass

    # Note: Workflow engine and orchestrator cleanup would be handled separately

    if cleanup_tasks:
        await asyncio.gather(*cleanup_tasks, return_exceptions=True)
