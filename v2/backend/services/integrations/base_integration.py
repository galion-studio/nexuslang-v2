"""
Base Integration Framework

Provides the foundation for all external API integrations.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from datetime import datetime
import aiohttp
import json

logger = logging.getLogger(__name__)


@dataclass
class IntegrationResult:
    """Result of an integration operation."""
    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class BaseIntegration(ABC):
    """Base class for all external integrations."""

    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.logger = logging.getLogger(f"{__name__}.{name}")

    async def initialize(self) -> bool:
        """Initialize the integration."""
        try:
            if self.session and not self.session.closed:
                await self.session.close()

            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers=self._get_default_headers()
            )
            self.logger.info(f"Initialized {self.name} integration")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize {self.name}: {str(e)}")
            return False

    async def cleanup(self) -> None:
        """Clean up resources."""
        if self.session and not self.session.closed:
            await self.session.close()
            self.logger.info(f"Cleaned up {self.name} integration")

    def _get_default_headers(self) -> Dict[str, str]:
        """Get default headers for API requests."""
        return {
            'User-Agent': 'Galion-Agent/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    async def _make_request(self, method: str, url: str, **kwargs) -> IntegrationResult:
        """Make an HTTP request with error handling."""
        if not self.session:
            return IntegrationResult(
                success=False,
                error="Integration not initialized"
            )

        try:
            async with self.session.request(method, url, **kwargs) as response:
                if response.status >= 200 and response.status < 300:
                    try:
                        data = await response.json()
                    except:
                        data = await response.text()

                    return IntegrationResult(
                        success=True,
                        data=data,
                        metadata={
                            'status_code': response.status,
                            'headers': dict(response.headers),
                            'url': str(response.url)
                        }
                    )
                else:
                    error_text = await response.text()
                    return IntegrationResult(
                        success=False,
                        error=f"HTTP {response.status}: {error_text}",
                        metadata={
                            'status_code': response.status,
                            'url': str(response.url)
                        }
                    )
        except aiohttp.ClientError as e:
            return IntegrationResult(
                success=False,
                error=f"Network error: {str(e)}"
            )
        except Exception as e:
            return IntegrationResult(
                success=False,
                error=f"Unexpected error: {str(e)}"
            )

    @abstractmethod
    async def test_connection(self) -> IntegrationResult:
        """Test the connection to the external service."""
        pass

    @abstractmethod
    async def get_capabilities(self) -> List[str]:
        """Get the capabilities provided by this integration."""
        pass

    @abstractmethod
    async def execute_operation(self, operation: str, **kwargs) -> IntegrationResult:
        """Execute a specific operation on the external service."""
        pass

    def validate_config(self) -> bool:
        """Validate the integration configuration."""
        required_fields = self.get_required_config_fields()
        missing_fields = []

        for field in required_fields:
            if field not in self.config or not self.config[field]:
                missing_fields.append(field)

        if missing_fields:
            self.logger.error(f"Missing required configuration fields: {missing_fields}")
            return False

        return True

    @abstractmethod
    def get_required_config_fields(self) -> List[str]:
        """Get the required configuration fields for this integration."""
        pass

    def get_config_schema(self) -> Dict[str, Any]:
        """Get the configuration schema for this integration."""
        return {
            'type': 'object',
            'properties': {
                field: {
                    'type': 'string',
                    'description': f'Required {field} for {self.name} integration'
                }
                for field in self.get_required_config_fields()
            },
            'required': self.get_required_config_fields()
        }
