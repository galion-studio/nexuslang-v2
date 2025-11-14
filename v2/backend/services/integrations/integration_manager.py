"""
Integration Manager

Manages all external API integrations and provides a unified interface
for agents to interact with external services.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Type
from dataclasses import dataclass
from datetime import datetime

from .base_integration import BaseIntegration, IntegrationResult
from .github_integration import GitHubIntegration
from .slack_integration import SlackIntegration
from .jira_integration import JiraIntegration
from .google_workspace_integration import GoogleWorkspaceIntegration
from .webhook_integration import WebhookIntegration

logger = logging.getLogger(__name__)


@dataclass
class IntegrationStatus:
    """Status of an integration."""
    name: str
    healthy: bool
    last_check: datetime
    error_message: Optional[str] = None
    capabilities: List[str] = None


class IntegrationManager:
    """Manages all external integrations."""

    def __init__(self):
        self.integrations: Dict[str, BaseIntegration] = {}
        self.status_cache: Dict[str, IntegrationStatus] = {}
        self.capabilities_cache: Dict[str, List[str]] = {}

        # Register available integrations
        self._register_integrations()

    def _register_integrations(self):
        """Register all available integrations."""
        self.available_integrations = {
            'github': GitHubIntegration,
            'slack': SlackIntegration,
            'jira': JiraIntegration,
            'google_workspace': GoogleWorkspaceIntegration,
            'webhook': WebhookIntegration,
        }

    async def initialize(self) -> bool:
        """Initialize all configured integrations."""
        success_count = 0
        total_count = len(self.integrations)

        for name, integration in self.integrations.items():
            try:
                if await integration.initialize():
                    logger.info(f"Initialized integration: {name}")
                    success_count += 1
                else:
                    logger.error(f"Failed to initialize integration: {name}")
            except Exception as e:
                logger.error(f"Error initializing {name}: {str(e)}")

        logger.info(f"Initialized {success_count}/{total_count} integrations")
        return success_count == total_count

    async def cleanup(self) -> None:
        """Clean up all integrations."""
        cleanup_tasks = []
        for integration in self.integrations.values():
            cleanup_tasks.append(integration.cleanup())

        await asyncio.gather(*cleanup_tasks, return_exceptions=True)
        logger.info("Cleaned up all integrations")

    def register_integration(self, name: str, integration_class: Type[BaseIntegration],
                           config: Dict[str, Any]) -> bool:
        """Register a new integration."""
        try:
            if name in self.integrations:
                logger.warning(f"Integration {name} already exists, replacing")

            integration = integration_class(name, config)

            if not integration.validate_config():
                logger.error(f"Invalid configuration for {name}")
                return False

            self.integrations[name] = integration
            logger.info(f"Registered integration: {name}")
            return True

        except Exception as e:
            logger.error(f"Failed to register integration {name}: {str(e)}")
            return False

    def unregister_integration(self, name: str) -> bool:
        """Unregister an integration."""
        if name in self.integrations:
            # Clean up the integration
            integration = self.integrations[name]
            asyncio.create_task(integration.cleanup())

            del self.integrations[name]

            # Clear caches
            if name in self.status_cache:
                del self.status_cache[name]
            if name in self.capabilities_cache:
                del self.capabilities_cache[name]

            logger.info(f"Unregistered integration: {name}")
            return True

        return False

    async def execute_operation(self, integration_name: str, operation: str,
                               **kwargs) -> IntegrationResult:
        """Execute an operation on a specific integration."""
        if integration_name not in self.integrations:
            return IntegrationResult(
                success=False,
                error=f"Integration '{integration_name}' not found"
            )

        integration = self.integrations[integration_name]

        try:
            result = await integration.execute_operation(operation, **kwargs)
            logger.info(f"Executed {operation} on {integration_name}: {result.success}")
            return result

        except Exception as e:
            logger.error(f"Error executing {operation} on {integration_name}: {str(e)}")
            return IntegrationResult(
                success=False,
                error=f"Integration error: {str(e)}"
            )

    async def get_integration_status(self, name: str) -> Optional[IntegrationStatus]:
        """Get the status of a specific integration."""
        if name not in self.integrations:
            return None

        # Check cache first (cache for 5 minutes)
        if name in self.status_cache:
            cached_status = self.status_cache[name]
            if (datetime.now() - cached_status.last_check).seconds < 300:
                return cached_status

        integration = self.integrations[name]

        try:
            test_result = await integration.test_connection()

            status = IntegrationStatus(
                name=name,
                healthy=test_result.success,
                last_check=datetime.now(),
                error_message=test_result.error if not test_result.success else None
            )

            # Cache the status
            self.status_cache[name] = status
            return status

        except Exception as e:
            logger.error(f"Error checking status for {name}: {str(e)}")
            return IntegrationStatus(
                name=name,
                healthy=False,
                last_check=datetime.now(),
                error_message=str(e)
            )

    async def get_all_statuses(self) -> Dict[str, IntegrationStatus]:
        """Get status of all integrations."""
        statuses = {}
        status_tasks = []

        for name in self.integrations.keys():
            status_tasks.append(self.get_integration_status(name))

        results = await asyncio.gather(*status_tasks, return_exceptions=True)

        for name, result in zip(self.integrations.keys(), results):
            if isinstance(result, Exception):
                statuses[name] = IntegrationStatus(
                    name=name,
                    healthy=False,
                    last_check=datetime.now(),
                    error_message=str(result)
                )
            else:
                statuses[name] = result

        return statuses

    async def get_integration_capabilities(self, name: str) -> Optional[List[str]]:
        """Get capabilities of a specific integration."""
        if name not in self.integrations:
            return None

        # Check cache first
        if name in self.capabilities_cache:
            return self.capabilities_cache[name]

        integration = self.integrations[name]

        try:
            capabilities = await integration.get_capabilities()
            self.capabilities_cache[name] = capabilities
            return capabilities

        except Exception as e:
            logger.error(f"Error getting capabilities for {name}: {str(e)}")
            return []

    def get_available_integrations(self) -> List[str]:
        """Get list of available integration types."""
        return list(self.available_integrations.keys())

    def get_registered_integrations(self) -> List[str]:
        """Get list of registered integration instances."""
        return list(self.integrations.keys())

    def get_integration_config_schema(self, integration_type: str) -> Optional[Dict[str, Any]]:
        """Get configuration schema for an integration type."""
        if integration_type not in self.available_integrations:
            return None

        integration_class = self.available_integrations[integration_type]

        # Create a dummy instance to get the schema
        dummy_config = {}
        dummy_integration = integration_class("dummy", dummy_config)

        return dummy_integration.get_config_schema()

    async def search_integrations(self, query: str, **filters) -> List[Dict[str, Any]]:
        """Search integrations based on capabilities or other criteria."""
        results = []

        for name, integration in self.integrations.items():
            try:
                capabilities = await self.get_integration_capabilities(name)
                status = await self.get_integration_status(name)

                # Check if integration matches search criteria
                matches = True

                if 'capability' in filters:
                    if filters['capability'] not in capabilities:
                        matches = False

                if 'healthy' in filters:
                    if status.healthy != filters['healthy']:
                        matches = False

                if query and query.lower() not in name.lower():
                    if not any(query.lower() in cap.lower() for cap in capabilities):
                        matches = False

                if matches:
                    results.append({
                        'name': name,
                        'capabilities': capabilities,
                        'healthy': status.healthy,
                        'last_check': status.last_check.isoformat(),
                        'error_message': status.error_message
                    })

            except Exception as e:
                logger.error(f"Error searching integration {name}: {str(e)}")

        return results

    async def execute_bulk_operation(self, operations: List[Dict[str, Any]]) -> List[IntegrationResult]:
        """Execute multiple operations across different integrations."""
        tasks = []

        for op in operations:
            integration_name = op.get('integration')
            operation = op.get('operation')
            kwargs = op.get('kwargs', {})

            if integration_name and operation:
                task = self.execute_operation(integration_name, operation, **kwargs)
                tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Convert exceptions to IntegrationResult objects
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                processed_results.append(IntegrationResult(
                    success=False,
                    error=str(result)
                ))
            else:
                processed_results.append(result)

        return processed_results

    def get_integration_stats(self) -> Dict[str, Any]:
        """Get statistics about integrations."""
        total_integrations = len(self.integrations)
        healthy_count = 0
        error_count = 0

        for status in self.status_cache.values():
            if status.healthy:
                healthy_count += 1
            else:
                error_count += 1

        return {
            'total_integrations': total_integrations,
            'healthy_integrations': healthy_count,
            'error_integrations': error_count,
            'uptime_percentage': (healthy_count / total_integrations * 100) if total_integrations > 0 else 0,
            'last_updated': datetime.now().isoformat()
        }
