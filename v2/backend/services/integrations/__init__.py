"""
External API Integrations for Galion Agents

This module provides integrations with popular external services,
allowing agents to interact with real-world APIs and services.
"""

from .base_integration import BaseIntegration, IntegrationResult
from .integration_manager import IntegrationManager
from .github_integration import GitHubIntegration
from .slack_integration import SlackIntegration
from .webhook_integration import WebhookIntegration
from .n8n_integration import N8nIntegrationService
from .zapier_integration import ZapierIntegrationService

__all__ = [
    'BaseIntegration',
    'IntegrationResult',
    'IntegrationManager',
    'GitHubIntegration',
    'SlackIntegration',
    'WebhookIntegration',
    'N8nIntegrationService',
    'ZapierIntegrationService'
]
