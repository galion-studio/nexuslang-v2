"""
External API Integrations for Galion Agents

This module provides integrations with popular external services,
allowing agents to interact with real-world APIs and services.
"""

from .base_integration import BaseIntegration, IntegrationResult
from .integration_manager import IntegrationManager
from .github_integration import GitHubIntegration
from .slack_integration import SlackIntegration
from .jira_integration import JiraIntegration
from .google_workspace_integration import GoogleWorkspaceIntegration
from .webhook_integration import WebhookIntegration

__all__ = [
    'BaseIntegration',
    'IntegrationResult',
    'IntegrationManager',
    'GitHubIntegration',
    'SlackIntegration',
    'JiraIntegration',
    'GoogleWorkspaceIntegration',
    'WebhookIntegration'
]
