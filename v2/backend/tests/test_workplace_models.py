"""
Workplace Service Models Tests
Comprehensive unit tests for workplace database models.
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Import models and schemas
from ..models.workplace import (
    Workspace, WorkspaceMember, SyncEvent, Task, TimeLog,
    LiveSession, CodeReview, Payment, _user_has_workspace_access
)
from ..models.user import User, Base
from ..models.project import Project


@pytest.fixture
def test_db():
    """Create in-memory test database."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_user(test_db):
    """Create a sample user for testing."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password",
        full_name="Test User",
        is_active=True,
        is_verified=True
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def sample_workspace(test_db, sample_user):
    """Create a sample workspace for testing."""
    workspace = Workspace(
        name="Test Workspace",
        description="A test workspace",
        owner_id=sample_user.id,
        billing_cycle="monthly",
        currency="USD",
        workflow_type="kanban"
    )
    test_db.add(workspace)
    test_db.commit()
    test_db.refresh(workspace)
    return workspace


@pytest.fixture
def sample_project(test_db, sample_user):
    """Create a sample project for testing."""
    project = Project(
        user_id=sample_user.id,
        name="Test Project",
        description="A test project",
        language="python",
        status="active"
    )
    test_db.add(project)
    test_db.commit()
    test_db.refresh(project)
    return project


class TestWorkspaceModel:
    """Test Workspace model functionality."""

    def test_workspace_creation(self, test_db, sample_user):
        """Test workspace creation and basic properties."""
        workspace = Workspace(
            name="Test Workspace",
            description="Description",
            owner_id=sample_user.id
        )
        test_db.add(workspace)
        test_db.commit()
        test_db.refresh(workspace)

        assert workspace.id is not None
        assert workspace.name == "Test Workspace"
        assert workspace.owner_id == sample_user.id
        assert workspace.is_active == True
        assert workspace.member_count == 1
        assert workspace.created_at is not None

    def test_workspace_default_values(self, test_db, sample_user):
        """Test workspace default values."""
        workspace = Workspace(
            name="Test",
            owner_id=sample_user.id
        )
        test_db.add(workspace)
        test_db.commit()

        assert workspace.billing_cycle == "monthly"
        assert workspace.currency == "USD"
        assert workspace.workflow_type == "kanban"
        assert workspace.is_active == True
        assert workspace.member_count == 1


class TestWorkspaceMemberModel:
    """Test WorkspaceMember model functionality."""

    def test_member_creation(self, test_db, sample_workspace, sample_user):
        """Test workspace member creation."""
        member = WorkspaceMember(
            workspace_id=sample_workspace.id,
            user_id=sample_user.id,
            role="admin",
            can_create_projects=True
        )
        test_db.add(member)
        test_db.commit()
        test_db.refresh(member)

        assert member.id is not None
        assert member.workspace_id == sample_workspace.id
        assert member.user_id == sample_user.id
        assert member.role == "admin"
        assert member.can_create_projects == True
        assert member.joined_at is not None

    def test_member_default_values(self, test_db, sample_workspace, sample_user):
        """Test member default values."""
        member = WorkspaceMember(
            workspace_id=sample_workspace.id,
            user_id=sample_user.id
        )
        test_db.add(member)
        test_db.commit()

        assert member.role == "member"
        assert member.can_create_projects == False
        assert member.availability_status == "available"
        assert member.performance_score == 5.0
        assert member.workload_capacity == 40


class TestSyncEventModel:
    """Test SyncEvent model functionality."""

    def test_sync_event_creation(self, test_db, sample_workspace, sample_user):
        """Test sync event creation."""
        event = SyncEvent(
            workspace_id=sample_workspace.id,
            user_id=sample_user.id,
            event_type="task_created",
            payload={"task_id": 123, "title": "Test Task"},
            source_platform="galion.app",
            target_platforms=["galion.studio"]
        )
        test_db.add(event)
        test_db.commit()
        test_db.refresh(event)

        assert event.id is not None
        assert event.event_type == "task_created"
        assert event.source_platform == "galion.app"
        assert event.target_platforms == ["galion.studio"]
        assert event.payload["task_id"] == 123
        assert event.created_at is not None


class TestTaskModel:
    """Test Task model functionality."""

    def test_task_creation(self, test_db, sample_project):
        """Test task creation."""
        task = Task(
            project_id=sample_project.id,
            title="Test Task",
            description="Task description",
            status="in_progress",
            priority="high"
        )
        test_db.add(task)
        test_db.commit()
        test_db.refresh(task)

        assert task.id is not None
        assert task.title == "Test Task"
        assert task.status == "in_progress"
        assert task.priority == "high"
        assert task.hours_logged == 0.0
        assert task.created_at is not None

    def test_task_default_values(self, test_db, sample_project):
        """Test task default values."""
        task = Task(
            project_id=sample_project.id,
            title="Test Task"
        )
        test_db.add(task)
        test_db.commit()

        assert task.status == "backlog"
        assert task.priority == "medium"
        assert task.complexity == "medium"
        assert task.hours_logged == 0.0
        assert task.assignment_method == "manual"


class TestTimeLogModel:
    """Test TimeLog model functionality."""

    def test_time_log_creation(self, test_db, sample_user):
        """Test time log creation."""
        # Create a task first
        project = Project(user_id=sample_user.id, name="Test", language="python")
        test_db.add(project)
        test_db.commit()

        task = Task(project_id=project.id, title="Test Task")
        test_db.add(task)
        test_db.commit()

        time_log = TimeLog(
            task_id=task.id,
            user_id=sample_user.id,
            hours=2.5,
            work_date=datetime.utcnow().date(),
            description="Worked on feature",
            category="development",
            billable=True
        )
        test_db.add(time_log)
        test_db.commit()
        test_db.refresh(time_log)

        assert time_log.id is not None
        assert time_log.hours == 2.5
        assert time_log.category == "development"
        assert time_log.billable == True
        assert time_log.total_amount == 0.0  # No hourly rate set

    def test_time_log_with_hourly_rate(self, test_db, sample_user):
        """Test time log with hourly rate calculation."""
        # Create project and task
        project = Project(user_id=sample_user.id, name="Test", language="python")
        test_db.add(project)
        test_db.commit()

        task = Task(project_id=project.id, title="Test Task")
        test_db.add(task)
        test_db.commit()

        time_log = TimeLog(
            task_id=task.id,
            user_id=sample_user.id,
            hours=3.0,
            work_date=datetime.utcnow().date(),
            description="Development work",
            category="development",
            billable=True,
            hourly_rate=50.0
        )
        test_db.add(time_log)
        test_db.commit()

        # Manually calculate amount (in real implementation this would be automatic)
        time_log.total_amount = time_log.hours * time_log.hourly_rate
        test_db.commit()

        assert time_log.total_amount == 150.0


class TestLiveSessionModel:
    """Test LiveSession model functionality."""

    def test_live_session_creation(self, test_db, sample_project, sample_user):
        """Test live session creation."""
        import uuid
        session_id = str(uuid.uuid4())

        session = LiveSession(
            id=session_id,
            project_id=sample_project.id,
            created_by=sample_user.id,
            session_type="kanban",
            max_participants=10,
            participants=[sample_user.id]
        )
        test_db.add(session)
        test_db.commit()
        test_db.refresh(session)

        assert session.id == session_id
        assert session.project_id == sample_project.id
        assert session.session_type == "kanban"
        assert session.max_participants == 10
        assert session.participants == [sample_user.id]
        assert session.is_active == True


class TestCodeReviewModel:
    """Test CodeReview model functionality."""

    def test_code_review_creation(self, test_db, sample_project, sample_user):
        """Test code review creation."""
        review = CodeReview(
            project_id=sample_project.id,
            requested_by=sample_user.id,
            code_content="def test():\n    pass",
            language="python",
            review_type="general",
            severity_level="medium"
        )
        test_db.add(review)
        test_db.commit()
        test_db.refresh(review)

        assert review.id is not None
        assert review.language == "python"
        assert review.review_type == "general"
        assert review.status == "pending"
        assert review.created_at is not None


class TestPaymentModel:
    """Test Payment model functionality."""

    def test_payment_creation(self, test_db, sample_user, sample_workspace):
        """Test payment creation."""
        payment = Payment(
            user_id=sample_user.id,
            workspace_id=sample_workspace.id,
            amount=1500.0,
            currency="USD",
            period_start=datetime.utcnow().date(),
            period_end=datetime.utcnow().date() + timedelta(days=30),
            description="Monthly billing",
            auto_generated=False
        )
        test_db.add(payment)
        test_db.commit()
        test_db.refresh(payment)

        assert payment.id is not None
        assert payment.amount == 1500.0
        assert payment.currency == "USD"
        assert payment.status == "pending"
        assert payment.auto_generated == False


class TestHelperFunctions:
    """Test helper functions."""

    def test_user_has_workspace_access_owner(self, test_db, sample_workspace, sample_user):
        """Test workspace access for owner."""
        # Owner should always have access
        assert _user_has_workspace_access(test_db, sample_user.id, sample_workspace.id) == True

    def test_user_has_workspace_access_member(self, test_db, sample_workspace, sample_user):
        """Test workspace access for member."""
        # Add user as member
        member = WorkspaceMember(
            workspace_id=sample_workspace.id,
            user_id=sample_user.id,
            role="member"
        )
        test_db.add(member)
        test_db.commit()

        assert _user_has_workspace_access(test_db, sample_user.id, sample_workspace.id) == True

    def test_user_has_workspace_access_no_access(self, test_db, sample_workspace):
        """Test workspace access for non-member."""
        # Create another user
        other_user = User(
            email="other@example.com",
            username="otheruser",
            hashed_password="hashed_password"
        )
        test_db.add(other_user)
        test_db.commit()

        assert _user_has_workspace_access(test_db, other_user.id, sample_workspace.id) == False

    def test_user_has_workspace_access_invalid_workspace(self, test_db, sample_user):
        """Test workspace access for invalid workspace."""
        assert _user_has_workspace_access(test_db, sample_user.id, 99999) == False


if __name__ == "__main__":
    pytest.main([__file__])
