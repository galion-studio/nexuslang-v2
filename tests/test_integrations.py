"""
Tests for external integrations framework.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import json

from v2.backend.services.integrations import IntegrationManager, IntegrationResult
from v2.backend.services.integrations.base_integration import BaseIntegration
from v2.backend.services.integrations.webhook_integration import WebhookIntegration


class TestIntegrationResult:
    """Test IntegrationResult dataclass."""

    def test_success_result(self):
        """Test successful integration result."""
        result = IntegrationResult(
            success=True,
            data={"test": "data"},
            metadata={"status_code": 200}
        )

        assert result.success is True
        assert result.data == {"test": "data"}
        assert result.error is None
        assert isinstance(result.timestamp, object)  # datetime object

    def test_error_result(self):
        """Test error integration result."""
        result = IntegrationResult(
            success=False,
            error="Test error message",
            metadata={"status_code": 500}
        )

        assert result.success is False
        assert result.data is None
        assert result.error == "Test error message"
        assert result.metadata == {"status_code": 500}


class TestBaseIntegration:
    """Test the BaseIntegration class."""

    @pytest.fixture
    def base_integration(self):
        """Create a test base integration."""
        class TestIntegration(BaseIntegration):
            def __init__(self, name: str, config: dict):
                super().__init__(name, config)
                self.test_connection_called = False
                self.get_capabilities_called = False

            def get_required_config_fields(self):
                return ["api_key"]

            async def test_connection(self):
                self.test_connection_called = True
                return IntegrationResult(success=True)

            async def get_capabilities(self):
                self.get_capabilities_called = True
                return ["test_operation"]

            async def execute_operation(self, operation: str, **kwargs):
                return IntegrationResult(success=True, data={"operation": operation})

        return TestIntegration("test_integration", {"api_key": "test_key"})

    def test_initialization(self, base_integration):
        """Test integration initialization."""
        assert base_integration.name == "test_integration"
        assert base_integration.config == {"api_key": "test_key"}
        assert base_integration.session is None

    async def test_initialize(self, base_integration):
        """Test integration initialization."""
        success = await base_integration.initialize()

        assert success is True
        assert base_integration.session is not None

        # Cleanup
        await base_integration.cleanup()
        assert base_integration.session is None or base_integration.session.closed

    def test_validate_config_valid(self, base_integration):
        """Test config validation with valid config."""
        assert base_integration.validate_config() is True

    def test_validate_config_invalid(self):
        """Test config validation with invalid config."""
        class TestIntegration(BaseIntegration):
            def get_required_config_fields(self):
                return ["required_field"]

            async def test_connection(self):
                return IntegrationResult(success=True)

            async def get_capabilities(self):
                return []

            async def execute_operation(self, operation: str, **kwargs):
                return IntegrationResult(success=True)

        integration = TestIntegration("test", {})  # Missing required field
        assert integration.validate_config() is False

    async def test_make_request_success(self, base_integration):
        """Test successful HTTP request."""
        await base_integration.initialize()

        with patch.object(base_integration.session, 'request') as mock_request:
            # Mock successful response
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={"test": "data"})
            mock_response.text = AsyncMock(return_value='{"test": "data"}')
            mock_response.headers = {"Content-Type": "application/json"}
            mock_response.url = "https://api.example.com/test"

            mock_request.return_value.__aenter__ = AsyncMock(return_value=mock_response)
            mock_request.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await base_integration._make_request("GET", "https://api.example.com/test")

            assert result.success is True
            assert result.data == {"test": "data"}
            assert result.metadata["status_code"] == 200

        await base_integration.cleanup()

    async def test_make_request_error(self, base_integration):
        """Test HTTP request with error response."""
        await base_integration.initialize()

        with patch.object(base_integration.session, 'request') as mock_request:
            # Mock error response
            mock_response = AsyncMock()
            mock_response.status = 404
            mock_response.text = AsyncMock(return_value="Not Found")
            mock_response.url = "https://api.example.com/test"

            mock_request.return_value.__aenter__ = AsyncMock(return_value=mock_response)
            mock_request.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await base_integration._make_request("GET", "https://api.example.com/test")

            assert result.success is False
            assert "404" in result.error
            assert result.metadata["status_code"] == 404

        await base_integration.cleanup()


class TestWebhookIntegration:
    """Test the WebhookIntegration class."""

    @pytest.fixture
    async def webhook_integration(self):
        """Create a test webhook integration."""
        integration = WebhookIntegration("test_webhook", {
            "webhook_url": "https://httpbin.org/post",
            "secret": "test_secret"
        })

        await integration.initialize()
        yield integration
        await integration.cleanup()

    async def test_initialization(self):
        """Test webhook integration initialization."""
        integration = WebhookIntegration("test_webhook", {
            "webhook_url": "https://httpbin.org/post"
        })

        assert integration.webhook_url == "https://httpbin.org/post"
        assert integration.secret == ""
        assert integration.headers == {}

    async def test_test_connection(self, webhook_integration):
        """Test webhook connection testing."""
        result = await webhook_integration.test_connection()

        # Should attempt to send a test payload
        assert isinstance(result, IntegrationResult)

    async def test_get_capabilities(self, webhook_integration):
        """Test getting webhook capabilities."""
        capabilities = await webhook_integration.get_capabilities()

        expected_capabilities = [
            'send_notification', 'send_alert', 'send_status_update',
            'send_task_update', 'send_agent_status', 'send_system_metrics',
            'send_custom_payload', 'verify_signature', 'retry_failed_webhooks',
            'batch_notifications'
        ]

        assert capabilities == expected_capabilities

    async def test_send_notification(self, webhook_integration):
        """Test sending a notification."""
        result = await webhook_integration.execute_operation(
            "send_notification",
            title="Test Notification",
            message="This is a test message",
            priority="normal"
        )

        assert isinstance(result, IntegrationResult)

    async def test_send_custom_payload(self, webhook_integration):
        """Test sending a custom payload."""
        custom_data = {"custom": "data", "test": True}

        result = await webhook_integration.execute_operation(
            "send_custom_payload",
            payload=custom_data,
            event_type="custom_test"
        )

        assert isinstance(result, IntegrationResult)

    async def test_batch_notifications(self, webhook_integration):
        """Test sending batch notifications."""
        notifications = [
            {"title": "Notification 1", "message": "Message 1"},
            {"title": "Notification 2", "message": "Message 2"}
        ]

        result = await webhook_integration.execute_operation(
            "batch_notifications",
            notifications=notifications
        )

        assert isinstance(result, IntegrationResult)

    def test_verify_signature_valid(self, webhook_integration):
        """Test signature verification with valid signature."""
        payload = {"test": "data"}
        payload_str = json.dumps(payload, separators=(',', ':'), sort_keys=True)

        # Generate signature
        import hmac
        import hashlib
        expected_signature = hmac.new(
            webhook_integration.secret.encode('utf-8'),
            payload_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        signature = f'sha256={expected_signature}'

        result = webhook_integration.validate_incoming_webhook(payload_str, signature)
        assert result is True

    def test_verify_signature_invalid(self, webhook_integration):
        """Test signature verification with invalid signature."""
        payload = {"test": "data"}
        payload_str = json.dumps(payload, separators=(',', ':'), sort_keys=True)

        # Wrong signature
        signature = "sha256=invalid_signature"

        result = webhook_integration.validate_incoming_webhook(payload_str, signature)
        assert result is False

    def test_get_webhook_signature(self, webhook_integration):
        """Test webhook signature generation."""
        payload = {"test": "data", "timestamp": "2024-01-01T00:00:00Z"}

        signature = webhook_integration.get_webhook_signature(payload)

        assert signature.startswith("sha256=")
        assert len(signature) == 71  # sha256= + 64 hex chars


class TestIntegrationManager:
    """Test the IntegrationManager class."""

    @pytest.fixture
    async def integration_manager(self):
        """Create a test integration manager."""
        manager = IntegrationManager()
        yield manager
        await manager.cleanup()

    def test_initialization(self, integration_manager):
        """Test integration manager initialization."""
        assert isinstance(integration_manager.integrations, dict)
        assert isinstance(integration_manager.status_cache, dict)
        assert isinstance(integration_manager.capabilities_cache, dict)

        # Should have webhook integration available
        assert "webhook" in integration_manager.available_integrations

    async def test_register_integration_success(self, integration_manager):
        """Test successful integration registration."""
        config = {
            "webhook_url": "https://httpbin.org/post",
            "secret": "test_secret"
        }

        success = integration_manager.register_integration("test_webhook", "webhook", config)

        assert success is True
        assert "test_webhook" in integration_manager.integrations

    async def test_register_integration_invalid_type(self, integration_manager):
        """Test registration with invalid integration type."""
        success = integration_manager.register_integration(
            "test_invalid", "invalid_type", {}
        )

        assert success is False
        assert "test_invalid" not in integration_manager.integrations

    async def test_unregister_integration(self, integration_manager):
        """Test integration unregistration."""
        # First register an integration
        config = {"webhook_url": "https://httpbin.org/post"}
        integration_manager.register_integration("test_webhook", "webhook", config)

        # Then unregister it
        success = integration_manager.unregister_integration("test_webhook")

        assert success is True
        assert "test_webhook" not in integration_manager.integrations

    async def test_execute_operation_success(self, integration_manager):
        """Test successful operation execution."""
        # Register webhook integration
        config = {"webhook_url": "https://httpbin.org/post"}
        integration_manager.register_integration("test_webhook", "webhook", config)

        # Execute operation
        result = await integration_manager.execute_operation(
            "test_webhook", "send_notification",
            title="Test", message="Test message"
        )

        assert isinstance(result, IntegrationResult)

    async def test_execute_operation_integration_not_found(self, integration_manager):
        """Test operation execution with non-existent integration."""
        result = await integration_manager.execute_operation(
            "non_existent", "test_operation"
        )

        assert result.success is False
        assert "not found" in result.error.lower()

    async def test_get_integration_status(self, integration_manager):
        """Test getting integration status."""
        # Register integration
        config = {"webhook_url": "https://httpbin.org/post"}
        integration_manager.register_integration("test_webhook", "webhook", config)

        # Get status
        status = await integration_manager.get_integration_status("test_webhook")

        assert status is not None
        assert hasattr(status, 'name')
        assert hasattr(status, 'healthy')
        assert hasattr(status, 'last_check')

    async def test_get_all_statuses(self, integration_manager):
        """Test getting all integration statuses."""
        # Register multiple integrations
        config = {"webhook_url": "https://httpbin.org/post"}
        integration_manager.register_integration("webhook1", "webhook", config)
        integration_manager.register_integration("webhook2", "webhook", config)

        statuses = await integration_manager.get_all_statuses()

        assert isinstance(statuses, dict)
        assert len(statuses) >= 2  # At least the two we registered

    async def test_get_capabilities(self, integration_manager):
        """Test getting integration capabilities."""
        # Register integration
        config = {"webhook_url": "https://httpbin.org/post"}
        integration_manager.register_integration("test_webhook", "webhook", config)

        capabilities = await integration_manager.get_integration_capabilities("test_webhook")

        assert isinstance(capabilities, list)
        assert len(capabilities) > 0
        assert "send_notification" in capabilities

    async def test_search_integrations(self, integration_manager):
        """Test searching integrations."""
        # Register integration
        config = {"webhook_url": "https://httpbin.org/post"}
        integration_manager.register_integration("test_webhook", "webhook", config)

        # Search for webhook integrations
        results = await integration_manager.search_integrations("webhook")

        assert isinstance(results, list)
        assert len(results) > 0

        # Check result structure
        result = results[0]
        assert "name" in result
        assert "capabilities" in result
        assert "healthy" in result

    async def test_bulk_operations(self, integration_manager):
        """Test bulk operation execution."""
        # Register integration
        config = {"webhook_url": "https://httpbin.org/post"}
        integration_manager.register_integration("test_webhook", "webhook", config)

        # Prepare bulk operations
        operations = [
            {
                'integration': 'test_webhook',
                'operation': 'send_notification',
                'kwargs': {'title': 'Test 1', 'message': 'Message 1'}
            },
            {
                'integration': 'test_webhook',
                'operation': 'send_notification',
                'kwargs': {'title': 'Test 2', 'message': 'Message 2'}
            }
        ]

        results = await integration_manager.execute_bulk_operation(operations)

        assert isinstance(results, list)
        assert len(results) == 2
        assert all(isinstance(result, IntegrationResult) for result in results)

    def test_get_available_integrations(self, integration_manager):
        """Test getting available integration types."""
        available = integration_manager.get_available_integrations()

        assert isinstance(available, list)
        assert "webhook" in available

    def test_get_registered_integrations(self, integration_manager):
        """Test getting registered integration instances."""
        # Register integration
        config = {"webhook_url": "https://httpbin.org/post"}
        integration_manager.register_integration("test_webhook", "webhook", config)

        registered = integration_manager.get_registered_integrations()

        assert isinstance(registered, list)
        assert "test_webhook" in registered

    def test_get_stats(self, integration_manager):
        """Test getting integration statistics."""
        # Register integration
        config = {"webhook_url": "https://httpbin.org/post"}
        integration_manager.register_integration("test_webhook", "webhook", config)

        stats = integration_manager.get_integration_stats()

        assert isinstance(stats, dict)
        assert "total_integrations" in stats
        assert "healthy_integrations" in stats
        assert "uptime_percentage" in stats
        assert stats["total_integrations"] >= 1
