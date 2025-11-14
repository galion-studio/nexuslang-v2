"""
Analytics Model - Database model for platform analytics and metrics
Tracks user behavior, platform usage, and performance metrics
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from ..core.database import Base


class AnalyticsEvent(Base):
    """
    Analytics Event model for tracking user interactions and platform events

    Stores structured event data for analytics and insights
    """
    __tablename__ = "analytics_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    session_id = Column(UUID(as_uuid=True))  # User session identifier
    event_type = Column(String(100), nullable=False, index=True)
    event_category = Column(String(50), index=True)  # ui, api, voice, error, etc.
    event_action = Column(String(100))  # click, submit, view, etc.
    event_label = Column(String(255))  # Additional context
    event_value = Column(Float)  # Numeric value (duration, count, etc.)
    event_data = Column(JSONB)  # Structured event data
    platform = Column(String(50))  # galion-app, developer-platform, galion-studio
    page_url = Column(String(500))  # Current page URL
    referrer_url = Column(String(500))  # Referrer URL
    user_agent = Column(Text)  # Browser/client information
    ip_address = Column(String(45))  # IPv4/IPv6 address (anonymized)
    device_info = Column(JSONB)  # Device and browser details
    geo_location = Column(JSONB)  # Geographic location data (anonymized)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User")

    def __repr__(self):
        return f"<AnalyticsEvent(id={self.id}, type={self.event_type}, user_id={self.user_id})>"


class AnalyticsMetric(Base):
    """
    Analytics Metric model for aggregated metrics and KPIs

    Stores calculated metrics for dashboards and reporting
    """
    __tablename__ = "analytics_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    metric_name = Column(String(100), nullable=False, index=True)
    metric_category = Column(String(50), index=True)  # user, voice, performance, revenue
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(20))  # users, seconds, dollars, percentage, etc.
    time_period = Column(String(20), index=True)  # hourly, daily, weekly, monthly
    period_start = Column(DateTime, nullable=False, index=True)
    period_end = Column(DateTime, nullable=False, index=True)
    dimensions = Column(JSONB)  # Dimension filters (platform, region, etc.)
    metadata = Column(JSONB)  # Additional metric metadata
    calculated_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<AnalyticsMetric(name={self.metric_name}, value={self.metric_value}, period={self.time_period})>"


class UserSession(Base):
    """
    User Session model for tracking user sessions and engagement

    Records session start/end times, duration, and engagement metrics
    """
    __tablename__ = "user_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_token = Column(String(255), unique=True, index=True)
    platform = Column(String(50), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow, index=True)
    ended_at = Column(DateTime)
    duration_seconds = Column(Integer)
    page_views = Column(Integer, default=0)
    events_count = Column(Integer, default=0)
    voice_commands = Column(Integer, default=0)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    device_info = Column(JSONB)
    geo_location = Column(JSONB)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User")
    events = relationship("AnalyticsEvent", backref="user_session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<UserSession(id={self.id}, user_id={self.user_id}, duration={self.duration_seconds}s, active={self.is_active})>"

    @property
    def is_expired(self) -> bool:
        """Check if session has expired (30 minutes of inactivity)"""
        if not self.ended_at:
            return False
        return (datetime.utcnow() - self.ended_at).total_seconds() > 1800  # 30 minutes

    def end_session(self):
        """End the user session and calculate duration"""
        if self.ended_at is None:
            self.ended_at = datetime.utcnow()
            if self.started_at:
                self.duration_seconds = int((self.ended_at - self.started_at).total_seconds())
            self.is_active = False

    def update_activity(self):
        """Update last activity timestamp (keep session alive)"""
        self.ended_at = datetime.utcnow()  # Reset inactivity timer


class PerformanceMetric(Base):
    """
    Performance Metric model for tracking system performance

    Records API response times, error rates, and system health metrics
    """
    __tablename__ = "performance_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    metric_type = Column(String(50), nullable=False, index=True)  # api_response, error_rate, cpu_usage, etc.
    metric_name = Column(String(100), nullable=False, index=True)
    metric_value = Column(Float, nullable=False)
    unit = Column(String(20))  # ms, %, count, bytes, etc.
    endpoint = Column(String(255))  # API endpoint (for API metrics)
    method = Column(String(10))  # HTTP method
    status_code = Column(Integer)  # HTTP status code
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    session_id = Column(UUID(as_uuid=True))
    tags = Column(JSONB)  # Custom tags for filtering
    metadata = Column(JSONB)  # Additional metric data
    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User")

    def __repr__(self):
        return f"<PerformanceMetric(type={self.metric_type}, name={self.metric_name}, value={self.metric_value})>"


class ABTest(Base):
    """
    A/B Test model for tracking experiment results

    Manages A/B tests and multivariate experiments
    """
    __tablename__ = "ab_tests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    test_name = Column(String(100), nullable=False, unique=True)
    test_description = Column(Text)
    test_type = Column(String(20), default="ab")  # ab, multivariate
    variants = Column(JSONB, nullable=False)  # Variant definitions
    audience_criteria = Column(JSONB)  # Who qualifies for the test
    status = Column(String(20), default="draft", index=True)  # draft, active, paused, completed
    started_at = Column(DateTime)
    ended_at = Column(DateTime)
    winner_variant = Column(String(50))
    confidence_level = Column(Float)  # Statistical confidence
    results = Column(JSONB)  # Test results and statistics
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    creator = relationship("User")

    def __repr__(self):
        return f"<ABTest(name={self.test_name}, status={self.status}, variants={len(self.variants or {})})>"

    def start_test(self):
        """Start the A/B test"""
        self.status = "active"
        self.started_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def end_test(self, winner_variant: str = None):
        """End the A/B test"""
        self.status = "completed"
        self.ended_at = datetime.utcnow()
        self.winner_variant = winner_variant
        self.updated_at = datetime.utcnow()

    def pause_test(self):
        """Pause the A/B test"""
        self.status = "paused"
        self.updated_at = datetime.utcnow()


class ABTestParticipant(Base):
    """
    A/B Test Participant model for tracking user assignments

    Records which users are in which test variants
    """
    __tablename__ = "ab_test_participants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    test_id = Column(UUID(as_uuid=True), ForeignKey("ab_tests.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    variant_assigned = Column(String(50), nullable=False)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    conversion_events = Column(JSONB)  # Events that count as conversions
    metadata = Column(JSONB)  # Additional participant data

    # Relationships
    test = relationship("ABTest")
    user = relationship("User")

    def __repr__(self):
        return f"<ABTestParticipant(test_id={self.test_id}, user_id={self.user_id}, variant={self.variant_assigned})>"
