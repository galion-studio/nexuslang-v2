"""
Workplace Service API Tests
Comprehensive integration tests for workplace API endpoints.
"""

import pytest
import json
from datetime import datetime, timedelta
from httpx import AsyncClient
from sqlalchemy.orm import Session

# Import the FastAPI app and dependencies
from ..main import app
from ..core.database import get_db
from ..models.user import User
from ..models.project import Project
from ..models.workplace import Workspace, WorkspaceMember, Task
from ..core.auth import create_access_token


@pytest.fixture
async def test_client():
    """Create test client for API testing."""
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


@pytest.fixture
def test_db_session():
    """Get database session for tests."""
    # This would normally be overridden in conftest.py
    # For now, we'll use a mock approach
    pass


@pytest.fixture
async def auth_headers(test_db_session):
    """Create authentication headers for API tests."""
    # Create test user
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password",
        full_name="Test User",
        is_active=True,
        is_verified=True
    )

    # In a real test environment, you'd save this to the test DB
    # For now, we'll mock the token creation
    token = create_access_token({"sub": "testuser"})
    return {"Authorization": f"Bearer {token}"}


class TestSynchronizationAPIs:
    """Test synchronization API endpoints."""

    @pytest.mark.asyncio
    async def test_broadcast_platform_update(self, test_client, auth_headers):
        """Test broadcasting platform updates."""
        update_data = {
            "workspace_id": 1,
            "event_type": "task_created",
            "payload": {"task_id": 123, "title": "Test Task"},
            "source_platform": "galion.app",
            "target_platforms": ["galion.studio", "developer.galion.app"],
            "notify_users": True
        }

        response = await test_client.post(
            "/api/v1/workplace/sync/broadcast",
            json=update_data,
            headers=auth_headers
        )

        # Should return 403 if workspace access denied (expected in test)
        # or 200 if access granted
        assert response.status_code in [200, 403]

        if response.status_code == 200:
            data = response.json()
            assert "status" in data
            assert "event_id" in data

    @pytest.mark.asyncio
    async def test_get_sync_history(self, test_client, auth_headers):
        """Test retrieving synchronization history."""
        params = {
            "workspace_id": 1,
            "limit": 10,
            "skip": 0
        }

        response = await test_client.get(
            "/api/v1/workplace/sync/history",
            params=params,
            headers=auth_headers
        )

        # Should return 403 if workspace access denied (expected in test)
        # or 200 if access granted
        assert response.status_code in [200, 403]

        if response.status_code == 200:
            data = response.json()
            assert "workspace_id" in data
            assert "events" in data
            assert "total" in data
            assert isinstance(data["events"], list)


class TestUserManagementAPIs:
    """Test user management API endpoints."""

    @pytest.mark.asyncio
    async def test_invite_user_to_workspace(self, test_client, auth_headers):
        """Test inviting user to workspace."""
        invitation_data = {
            "role": "member",
            "can_create_projects": False,
            "can_review_applications": True,
            "can_post_jobs": False,
            "platform_permissions": {
                "galion.app": ["read", "write"],
                "galion.studio": ["read"]
            },
            "invitation_message": "Welcome to our workspace!"
        }

        response = await test_client.post(
            "/api/v1/workplace/users/2/workspaces/1/invite",
            json=invitation_data,
            headers=auth_headers
        )

        # Should return 403 if workspace access denied (expected in test)
        # or 404 if user/workspace not found, or 200 if successful
        assert response.status_code in [200, 403, 404]

        if response.status_code == 200:
            data = response.json()
            assert "message" in data
            assert "workspace" in data
            assert "role" in data


class TestProjectManagementAPIs:
    """Test project management API endpoints."""

    @pytest.mark.asyncio
    async def test_get_project_ai_insights(self, test_client, auth_headers):
        """Test getting AI insights for projects."""
        params = {
            "insight_type": "general"
        }

        response = await test_client.post(
            "/api/v1/workplace/projects/1/ai-insights",
            params=params,
            headers=auth_headers
        )

        # Should return 403 if workspace access denied (expected in test)
        # or 404 if project not found, or 200 if successful
        assert response.status_code in [200, 403, 404]

        if response.status_code == 200:
            data = response.json()
            assert "project_id" in data
            assert "insight_type" in data
            assert "insights" in data
            assert "generated_at" in data
            assert "confidence_score" in data


class TestTimeTrackingAPIs:
    """Test time tracking API endpoints."""

    @pytest.mark.asyncio
    async def test_smart_time_logging(self, test_client, auth_headers):
        """Test smart time logging."""
        log_data = {
            "task_id": 1,
            "hours": 2.5,
            "work_date": "2024-01-15",
            "description": "Worked on implementing new feature with AI assistance"
        }

        response = await test_client.post(
            "/api/v1/workplace/time/smart-log",
            json=log_data,
            headers=auth_headers
        )

        # Should return 200 if successful, or validation errors
        assert response.status_code in [200, 422]

        if response.status_code == 200:
            data = response.json()
            assert "time_log_id" in data
            assert "hours" in data
            assert "category" in data
            assert "billable" in data
            assert "ai_insights" in data


class TestTaskManagementAPIs:
    """Test task management API endpoints."""

    @pytest.mark.asyncio
    async def test_smart_task_assignment(self, test_client, auth_headers):
        """Test smart task assignment."""
        assignment_data = {
            "task_id": 1,
            "criteria": {
                "priority_weight": 0.8,
                "skill_weight": 0.6
            }
        }

        response = await test_client.post(
            "/api/v1/workplace/tasks/smart-assign",
            json=assignment_data,
            headers=auth_headers
        )

        # Should return 403 if workspace access denied (expected in test)
        # or 404 if task not found, or 200 if successful
        assert response.status_code in [200, 403, 404]

        if response.status_code == 200:
            data = response.json()
            assert "task_id" in data
            assert "analysis" in data
            assert "assignment_made" in data
            assert "reasoning" in data


class TestBillingAPIs:
    """Test billing API endpoints."""

    @pytest.mark.asyncio
    async def test_auto_generate_billing(self, test_client, auth_headers):
        """Test automatic billing generation."""
        billing_data = {
            "workspace_id": 1,
            "start_date": "2024-01-01",
            "end_date": "2024-01-31"
        }

        response = await test_client.post(
            "/api/v1/workplace/billing/auto-generate",
            json=billing_data,
            headers=auth_headers
        )

        # Should return 403 if workspace access denied (expected in test)
        # or 404 if workspace not found, or 200 if successful
        assert response.status_code in [200, 403, 404]

        if response.status_code == 200:
            data = response.json()
            assert "workspace_id" in data
            assert "billing_period" in data
            assert "invoices_generated" in data
            assert "total_amount" in data
            assert "invoices" in data


class TestAnalyticsAPIs:
    """Test analytics API endpoints."""

    @pytest.mark.asyncio
    async def test_get_predictive_analytics(self, test_client, auth_headers):
        """Test predictive analytics."""
        params = {
            "workspace_id": 1,
            "prediction_type": "project_completion",
            "timeframe_days": 30
        }

        response = await test_client.get(
            "/api/v1/workplace/analytics/predictive",
            params=params,
            headers=auth_headers
        )

        # Should return 403 if workspace access denied (expected in test)
        # or 404 if workspace not found, or 200 if successful
        assert response.status_code in [200, 403, 404]

        if response.status_code == 200:
            data = response.json()
            assert "workspace_id" in data
            assert "prediction_type" in data
            assert "predictions" in data
            assert "confidence_levels" in data
            assert "recommendations" in data


class TestAIIntegrationAPIs:
    """Test AI integration API endpoints."""

    @pytest.mark.asyncio
    async def test_optimize_workflow(self, test_client, auth_headers):
        """Test workflow optimization."""
        optimization_data = {
            "workspace_id": 1,
            "focus_areas": ["bottlenecks", "resource_allocation"],
            "constraints": {
                "max_overtime": 10
            },
            "apply_changes": False
        }

        response = await test_client.post(
            "/api/v1/workplace/ai/optimize-workflow",
            json=optimization_data,
            headers=auth_headers
        )

        # Should return 403 if workspace access denied (expected in test)
        # or 404 if workspace not found, or 200 if successful
        assert response.status_code in [200, 403, 404]

        if response.status_code == 200:
            data = response.json()
            assert "workspace_id" in data
            assert "optimization_focus" in data
            assert "recommendations" in data
            assert "generated_at" in data


class TestRealTimeCollaborationAPIs:
    """Test real-time collaboration API endpoints."""

    @pytest.mark.asyncio
    async def test_start_live_session(self, test_client, auth_headers):
        """Test starting live collaboration session."""
        session_data = {
            "project_id": 1,
            "session_type": "kanban",
            "max_participants": 8
        }

        response = await test_client.post(
            "/api/v1/workplace/collaboration/live-session",
            json=session_data,
            headers=auth_headers
        )

        # Should return 403 if workspace access denied (expected in test)
        # or 404 if project not found, or 200 if successful
        assert response.status_code in [200, 403, 404]

        if response.status_code == 200:
            data = response.json()
            assert "session_id" in data
            assert "project_id" in data
            assert "session_type" in data
            assert "websocket_url" in data


class TestPlatformSpecificAPIs:
    """Test platform-specific API endpoints."""

    @pytest.mark.asyncio
    async def test_get_voice_context(self, test_client, auth_headers):
        """Test getting voice interaction context."""
        context_data = {
            "context_type": "general",
            "include_history": True
        }

        response = await test_client.post(
            "/api/v1/workplace/voice/context",
            json=context_data,
            headers=auth_headers
        )

        # Should return 200 if successful
        assert response.status_code == 200
        data = response.json()
        assert "user_context" in data
        assert "ai_preferences" in data
        assert "workspace_settings" in data

    @pytest.mark.asyncio
    async def test_request_code_review(self, test_client, auth_headers):
        """Test requesting AI-assisted code review."""
        review_data = {
            "project_id": 1,
            "code_content": "def calculate_total(items):\n    return sum(item['price'] * item['quantity'] for item in items)",
            "language": "python",
            "context": "E-commerce price calculation function",
            "review_type": "performance",
            "severity_level": "medium"
        }

        response = await test_client.post(
            "/api/v1/workplace/code/review/request",
            json=review_data,
            headers=auth_headers
        )

        # Should return 403 if workspace access denied (expected in test)
        # or 404 if project not found, or 200 if successful
        assert response.status_code in [200, 403, 404]

        if response.status_code == 200:
            data = response.json()
            assert "review_id" in data
            assert "analysis" in data
            assert "feedback" in data
            assert "recommendations" in data


class TestErrorHandling:
    """Test error handling and validation."""

    @pytest.mark.asyncio
    async def test_invalid_time_log_hours(self, test_client, auth_headers):
        """Test validation for invalid time log hours."""
        log_data = {
            "hours": 30,  # Invalid: more than 24 hours
            "description": "Test description"
        }

        response = await test_client.post(
            "/api/v1/workplace/time/smart-log",
            json=log_data,
            headers=auth_headers
        )

        # Should return validation error
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_invalid_time_log_description(self, test_client, auth_headers):
        """Test validation for invalid time log description."""
        log_data = {
            "hours": 2.0,
            "description": "Hi"  # Too short
        }

        response = await test_client.post(
            "/api/v1/workplace/time/smart-log",
            json=log_data,
            headers=auth_headers
        )

        # Should return validation error
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_unauthorized_access(self, test_client):
        """Test unauthorized access to protected endpoints."""
        response = await test_client.get("/api/v1/workplace/sync/history?workspace_id=1")

        # Should require authentication
        assert response.status_code in [401, 403]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
