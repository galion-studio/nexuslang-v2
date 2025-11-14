"""
A/B testing models for Deep Search.
Handles test configurations, variants, participants, and results.
"""

from sqlalchemy import Column, String, Text, Integer, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from .base import Base


class ABTest(Base):
    """
    Model for A/B test configurations.

    Defines the overall test setup including variants, metrics, and configuration.
    """

    __tablename__ = "ab_tests"

    id = Column(String, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, default="")
    test_type = Column(String(50), nullable=False, index=True)  # ui, algorithm, feature, personalization, etc.

    # Test status and timing
    status = Column(String(20), default="draft", index=True)  # draft, active, completed, paused
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    paused_at = Column(DateTime(timezone=True), nullable=True)

    # Test configuration
    config = Column(JSON, default=dict)  # Test-specific configuration
    target_metric = Column(String(50), default="conversion_rate")  # Primary metric to optimize
    min_participants = Column(Integer, default=100)
    confidence_level = Column(Float, default=0.95)
    max_duration_days = Column(Integer, default=30)

    # Metadata
    created_by = Column(String, nullable=False, index=True)
    tags = Column(JSON, default=list)

    # Statistics
    total_participants = Column(Integer, default=0)
    winner_variant_id = Column(String, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    variants = relationship("ABTestVariant", back_populates="test", cascade="all, delete-orphan")
    participants = relationship("ABTestParticipant", back_populates="test", cascade="all, delete-orphan")
    results = relationship("ABTestResult", back_populates="test", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ABTest(id='{self.id}', name='{self.name}', status='{self.status}', type='{self.test_type}')>"


class ABTestVariant(Base):
    """
    Model for A/B test variants.

    Defines the different variations being tested.
    """

    __tablename__ = "ab_test_variants"

    id = Column(String, primary_key=True, index=True)
    test_id = Column(String, ForeignKey("ab_tests.id"), nullable=False, index=True)
    variant_id = Column(String(50), nullable=False)  # Unique identifier within test
    name = Column(String(100), nullable=False)
    description = Column(Text, default="")

    # Variant configuration
    config = Column(JSON, default=dict)  # Variant-specific configuration
    weight = Column(Float, default=1.0)  # Traffic allocation weight
    is_control = Column(Boolean, default=False)  # Whether this is the control variant

    # Statistics
    participant_count = Column(Integer, default=0)
    conversion_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    test = relationship("ABTest", back_populates="variants")

    def __repr__(self):
        return f"<ABTestVariant(test_id='{self.test_id}', variant_id='{self.variant_id}', name='{self.name}')>"


class ABTestParticipant(Base):
    """
    Model for A/B test participants.

    Tracks which users are assigned to which test variants.
    """

    __tablename__ = "ab_test_participants"

    id = Column(String, primary_key=True, index=True)
    test_id = Column(String, ForeignKey("ab_tests.id"), nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    variant_id = Column(String, nullable=False, index=True)

    # Assignment details
    assigned_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    user_context = Column(JSON, default=dict)  # User context at assignment time

    # Participant status
    has_converted = Column(Boolean, default=False)
    conversion_type = Column(String(50), nullable=True)
    converted_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    test = relationship("ABTest", back_populates="participants")

    def __repr__(self):
        return f"<ABTestParticipant(test_id='{self.test_id}', user_id='{self.user_id}', variant_id='{self.variant_id}')>"


class ABTestResult(Base):
    """
    Model for A/B test results and conversions.

    Records conversion events and other measurable outcomes.
    """

    __tablename__ = "ab_test_results"

    id = Column(String, primary_key=True, index=True)
    test_id = Column(String, ForeignKey("ab_tests.id"), nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    variant_id = Column(String, nullable=False, index=True)

    # Result details
    conversion_type = Column(String(50), nullable=False)  # primary, secondary, custom
    score = Column(Float, default=1.0)  # Conversion score/weight
    metadata = Column(JSON, default=dict)  # Additional result data

    # Timing
    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    test = relationship("ABTest", back_populates="results")

    def __repr__(self):
        return f"<ABTestResult(test_id='{self.test_id}', user_id='{self.user_id}', type='{self.conversion_type}', score={self.score})>"


class ABTestAnalytics(Base):
    """
    Model for storing A/B test analytics and insights.

    Tracks long-term performance and learning from tests.
    """

    __tablename__ = "ab_test_analytics"

    id = Column(String, primary_key=True, index=True)
    test_id = Column(String, ForeignKey("ab_tests.id"), nullable=False, index=True)

    # Analytics data
    analytics_type = Column(String(50), nullable=False)  # daily, weekly, final
    data = Column(JSON, default=dict)  # Analytics data payload
    insights = Column(JSON, default=dict)  # Generated insights

    # Time period
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)

    # Metadata
    generated_by = Column(String, default="system")
    confidence_score = Column(Float, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    test = relationship("ABTest")

    def __repr__(self):
        return f"<ABTestAnalytics(test_id='{self.test_id}', type='{self.analytics_type}', period='{self.period_start.date()}')>"


class ABTestTemplate(Base):
    """
    Model for storing A/B test templates.

    Pre-defined test configurations for common scenarios.
    """

    __tablename__ = "ab_test_templates"

    id = Column(String, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, default="")
    category = Column(String(50), nullable=False, index=True)

    # Template configuration
    template_config = Column(JSON, default=dict)  # Complete template configuration
    default_variants = Column(JSON, default=list)  # Default variant configurations
    recommended_metrics = Column(JSON, default=list)  # Recommended metrics to track

    # Usage statistics
    usage_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)

    # Metadata
    created_by = Column(String, nullable=False)
    is_public = Column(Boolean, default=True)
    tags = Column(JSON, default=list)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<ABTestTemplate(id='{self.id}', name='{self.name}', category='{self.category}')>"


# Add relationships to User model (if not already present)
# This would typically be in the user.py model file, but shown here for completeness

# User.ab_test_participations = relationship("ABTestParticipant", back_populates="user")
# User.created_ab_tests = relationship("ABTest", foreign_keys="ABTest.created_by")
