"""
A/B testing framework for Deep Search.
Enables data-driven experimentation and optimization of research strategies.
"""

import logging
import hashlib
import random
import asyncio
from typing import Dict, Any, List, Optional, Tuple, Callable
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict
import json

from ...models.ab_testing import ABTest, ABTestVariant, ABTestParticipant, ABTestResult

logger = logging.getLogger(__name__)


@dataclass
class TestVariant:
    """Represents a test variant in an A/B test."""
    id: str
    name: str
    config: Dict[str, Any]
    weight: float = 1.0  # Relative weight for traffic allocation

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TestMetrics:
    """Metrics collected for a test variant."""
    participant_count: int = 0
    conversion_count: int = 0
    conversion_rate: float = 0.0
    average_score: float = 0.0
    total_score: float = 0.0
    custom_metrics: Dict[str, Any] = None

    def __post_init__(self):
        if self.custom_metrics is None:
            self.custom_metrics = {}

    def update_conversion(self, converted: bool, score: float = 0.0):
        """Update metrics with a new participant result."""
        self.participant_count += 1
        if converted:
            self.conversion_count += 1
        self.total_score += score

        # Recalculate rates
        self.conversion_rate = (self.conversion_count / self.participant_count) if self.participant_count > 0 else 0.0
        self.average_score = self.total_score / self.participant_count if self.participant_count > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ABTestingService:
    """
    Comprehensive A/B testing framework for Deep Search.

    Features:
    - Multiple test types (UI, algorithm, feature, research strategy)
    - Traffic allocation and user segmentation
    - Real-time metrics collection
    - Statistical significance testing
    - Automated winner determination
    - Integration with analytics systems
    """

    def __init__(self):
        self.active_tests = {}  # test_id -> ABTest
        self.test_cache = {}    # user_id -> {test_id: variant_id}
        self.metrics_cache = {}  # test_id -> {variant_id: TestMetrics}

        # Default test configurations
        self.default_test_configs = {
            'ui_variation': {
                'type': 'ui',
                'allocation_method': 'random',
                'min_participants': 100,
                'confidence_level': 0.95,
                'max_duration_days': 30
            },
            'research_strategy': {
                'type': 'algorithm',
                'allocation_method': 'consistent',  # Same variant per user
                'min_participants': 50,
                'confidence_level': 0.90,
                'max_duration_days': 14
            },
            'feature_rollout': {
                'type': 'feature',
                'allocation_method': 'percentage',
                'min_participants': 200,
                'confidence_level': 0.95,
                'max_duration_days': 60
            },
            'personalization': {
                'type': 'personalization',
                'allocation_method': 'segmented',
                'min_participants': 150,
                'confidence_level': 0.90,
                'max_duration_days': 45
            }
        }

    async def create_test(self, session, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new A/B test.

        Args:
            session: Database session
            test_data: Test configuration

        Returns:
            Test creation result
        """
        try:
            # Validate test data
            validation = self._validate_test_data(test_data)
            if not validation["valid"]:
                return {
                    "success": False,
                    "error": f"Invalid test data: {', '.join(validation['errors'])}"
                }

            # Generate test ID
            test_id = self._generate_test_id(test_data["name"])

            # Create test record
            ab_test = ABTest(
                id=test_id,
                name=test_data["name"],
                description=test_data.get("description", ""),
                test_type=test_data["test_type"],
                status="draft",
                config=json.dumps(test_data.get("config", {})),
                target_metric=test_data.get("target_metric", "conversion_rate"),
                min_participants=test_data.get("min_participants", 100),
                confidence_level=test_data.get("confidence_level", 0.95),
                max_duration_days=test_data.get("max_duration_days", 30),
                created_by=test_data.get("created_by", "system")
            )

            session.add(ab_test)
            await session.commit()
            await session.refresh(ab_test)

            # Create variants
            variants_data = test_data.get("variants", [])
            for variant_data in variants_data:
                variant = ABTestVariant(
                    test_id=test_id,
                    variant_id=variant_data["id"],
                    name=variant_data["name"],
                    config=json.dumps(variant_data.get("config", {})),
                    weight=variant_data.get("weight", 1.0),
                    is_control=variant_data.get("is_control", False)
                )
                session.add(variant)

            await session.commit()

            # Initialize test in memory
            self.active_tests[test_id] = ab_test
            self.metrics_cache[test_id] = {}

            logger.info(f"Created A/B test: {test_data['name']} (ID: {test_id})")

            return {
                "success": True,
                "test_id": test_id,
                "name": ab_test.name,
                "status": ab_test.status,
                "variant_count": len(variants_data),
                "created_at": ab_test.created_at.isoformat()
            }

        except Exception as e:
            logger.error(f"Test creation failed: {e}")
            await session.rollback()
            return {
                "success": False,
                "error": str(e)
            }

    async def start_test(self, session, test_id: str) -> Dict[str, Any]:
        """
        Start an A/B test.

        Args:
            session: Database session
            test_id: Test ID to start

        Returns:
            Test start result
        """
        try:
            # Get test
            test = await session.get(ABTest, test_id)
            if not test:
                return {"success": False, "error": "Test not found"}

            if test.status != "draft":
                return {"success": False, "error": f"Test is already {test.status}"}

            # Update test status
            test.status = "active"
            test.started_at = datetime.utcnow()
            await session.commit()

            # Initialize metrics for all variants
            variants = await session.execute(
                session.query(ABTestVariant).filter(ABTestVariant.test_id == test_id)
            )
            for variant in variants.scalars():
                self.metrics_cache[test_id][variant.variant_id] = TestMetrics()

            logger.info(f"Started A/B test: {test.name} (ID: {test_id})")

            return {
                "success": True,
                "test_id": test_id,
                "status": "active",
                "started_at": test.started_at.isoformat()
            }

        except Exception as e:
            logger.error(f"Test start failed: {e}")
            return {"success": False, "error": str(e)}

    async def assign_variant(self, session, test_id: str, user_id: str,
                           user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Assign a test variant to a user.

        Args:
            session: Database session
            test_id: Test ID
            user_id: User ID
            user_context: User context for segmentation

        Returns:
            Variant assignment result
        """
        try:
            # Check cache first
            if user_id in self.test_cache and test_id in self.test_cache[user_id]:
                cached_variant = self.test_cache[user_id][test_id]
                return {
                    "success": True,
                    "test_id": test_id,
                    "variant_id": cached_variant,
                    "cached": True
                }

            # Get test
            test = await session.get(ABTest, test_id)
            if not test or test.status != "active":
                return {"success": False, "error": "Test not found or not active"}

            # Get variants
            variants_query = session.query(ABTestVariant).filter(ABTestVariant.test_id == test_id)
            variants_result = await session.execute(variants_query)
            variants = variants_result.scalars().all()

            if not variants:
                return {"success": False, "error": "No variants configured for test"}

            # Check if user already participated
            participant_query = session.query(ABTestParticipant).filter(
                ABTestParticipant.test_id == test_id,
                ABTestParticipant.user_id == user_id
            )
            participant_result = await session.execute(participant_query)
            existing_participant = participant_result.scalar_one_or_none()

            if existing_participant:
                return {
                    "success": True,
                    "test_id": test_id,
                    "variant_id": existing_participant.variant_id,
                    "existing": True
                }

            # Assign variant based on test configuration
            test_config = json.loads(test.config) if test.config else {}
            allocation_method = test_config.get("allocation_method", "random")

            variant_id = self._allocate_variant(variants, user_id, allocation_method, user_context)

            # Record participant
            participant = ABTestParticipant(
                test_id=test_id,
                user_id=user_id,
                variant_id=variant_id,
                assigned_at=datetime.utcnow(),
                user_context=json.dumps(user_context or {})
            )

            session.add(participant)
            await session.commit()

            # Update cache
            if user_id not in self.test_cache:
                self.test_cache[user_id] = {}
            self.test_cache[user_id][test_id] = variant_id

            # Update metrics
            if test_id in self.metrics_cache and variant_id in self.metrics_cache[test_id]:
                self.metrics_cache[test_id][variant_id].participant_count += 1

            return {
                "success": True,
                "test_id": test_id,
                "variant_id": variant_id,
                "new_assignment": True
            }

        except Exception as e:
            logger.error(f"Variant assignment failed: {e}")
            return {"success": False, "error": str(e)}

    async def record_conversion(self, session, test_id: str, user_id: str,
                              conversion_type: str = "primary", score: float = 1.0,
                              metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Record a conversion event for a test participant.

        Args:
            session: Database session
            test_id: Test ID
            user_id: User ID
            conversion_type: Type of conversion
            score: Conversion score/value
            metadata: Additional metadata

        Returns:
            Conversion recording result
        """
        try:
            # Get participant
            participant_query = session.query(ABTestParticipant).filter(
                ABTestParticipant.test_id == test_id,
                ABTestParticipant.user_id == user_id
            )
            participant_result = await session.execute(participant_query)
            participant = participant_result.scalar_one_or_none()

            if not participant:
                return {"success": False, "error": "Participant not found in test"}

            # Record result
            result = ABTestResult(
                test_id=test_id,
                user_id=user_id,
                variant_id=participant.variant_id,
                conversion_type=conversion_type,
                score=score,
                metadata=json.dumps(metadata or {}),
                recorded_at=datetime.utcnow()
            )

            session.add(result)
            await session.commit()

            # Update metrics
            if test_id in self.metrics_cache and participant.variant_id in self.metrics_cache[test_id]:
                metrics = self.metrics_cache[test_id][participant.variant_id]
                metrics.update_conversion(True, score)

            return {
                "success": True,
                "test_id": test_id,
                "variant_id": participant.variant_id,
                "conversion_type": conversion_type,
                "score": score
            }

        except Exception as e:
            logger.error(f"Conversion recording failed: {e}")
            return {"success": False, "error": str(e)}

    async def get_test_results(self, session, test_id: str) -> Dict[str, Any]:
        """
        Get comprehensive results for an A/B test.

        Args:
            session: Database session
            test_id: Test ID

        Returns:
            Test results with statistical analysis
        """
        try:
            # Get test
            test = await session.get(ABTest, test_id)
            if not test:
                return {"success": False, "error": "Test not found"}

            # Get variants and their metrics
            variants_query = session.query(ABTestVariant).filter(ABTestVariant.test_id == test_id)
            variants_result = await session.execute(variants_query)
            variants = variants_result.scalars().all()

            # Get results
            results_query = session.query(ABTestResult).filter(ABTestResult.test_id == test_id)
            results_result = await session.execute(results_query)
            results = results_result.scalars().all()

            # Calculate metrics per variant
            variant_metrics = {}
            for variant in variants:
                variant_results = [r for r in results if r.variant_id == variant.variant_id]
                participant_count = len(set(r.user_id for r in variant_results))

                if participant_count > 0:
                    conversion_count = len([r for r in variant_results if r.score > 0])
                    total_score = sum(r.score for r in variant_results)
                    avg_score = total_score / len(variant_results) if variant_results else 0

                    variant_metrics[variant.variant_id] = {
                        "name": variant.name,
                        "participant_count": participant_count,
                        "conversion_count": conversion_count,
                        "conversion_rate": conversion_count / participant_count,
                        "average_score": avg_score,
                        "total_score": total_score,
                        "is_control": variant.is_control
                    }
                else:
                    variant_metrics[variant.variant_id] = {
                        "name": variant.name,
                        "participant_count": 0,
                        "conversion_count": 0,
                        "conversion_rate": 0.0,
                        "average_score": 0.0,
                        "total_score": 0.0,
                        "is_control": variant.is_control
                    }

            # Statistical analysis
            statistical_analysis = self._perform_statistical_analysis(variant_metrics, test.target_metric)

            # Determine winner if test is complete
            winner = self._determine_winner(variant_metrics, test.min_participants, test.confidence_level)

            return {
                "success": True,
                "test_id": test_id,
                "test_name": test.name,
                "status": test.status,
                "target_metric": test.target_metric,
                "variant_metrics": variant_metrics,
                "statistical_analysis": statistical_analysis,
                "winner": winner,
                "total_participants": sum(m["participant_count"] for m in variant_metrics.values()),
                "total_conversions": sum(m["conversion_count"] for m in variant_metrics.values()),
                "generated_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Test results retrieval failed: {e}")
            return {"success": False, "error": str(e)}

    async def stop_test(self, session, test_id: str) -> Dict[str, Any]:
        """
        Stop an active A/B test.

        Args:
            session: Database session
            test_id: Test ID to stop

        Returns:
            Test stop result
        """
        try:
            # Get test
            test = await session.get(ABTest, test_id)
            if not test:
                return {"success": False, "error": "Test not found"}

            if test.status != "active":
                return {"success": False, "error": f"Test is not active (status: {test.status})"}

            # Update test status
            test.status = "completed"
            test.completed_at = datetime.utcnow()
            await session.commit()

            # Get final results
            results = await self.get_test_results(session, test_id)

            logger.info(f"Stopped A/B test: {test.name} (ID: {test_id})")

            return {
                "success": True,
                "test_id": test_id,
                "status": "completed",
                "final_results": results,
                "completed_at": test.completed_at.isoformat()
            }

        except Exception as e:
            logger.error(f"Test stop failed: {e}")
            return {"success": False, "error": str(e)}

    def get_active_tests(self) -> List[Dict[str, Any]]:
        """
        Get all active A/B tests.

        Returns:
            List of active tests
        """
        active_tests = []
        for test_id, test in self.active_tests.items():
            if test.status == "active":
                active_tests.append({
                    "id": test_id,
                    "name": test.name,
                    "type": test.test_type,
                    "started_at": test.started_at.isoformat() if test.started_at else None,
                    "participant_count": sum(
                        self.metrics_cache.get(test_id, {}).get(vid, TestMetrics()).participant_count
                        for vid in self.metrics_cache.get(test_id, {})
                    )
                })

        return active_tests

    def get_test_templates(self) -> Dict[str, Any]:
        """
        Get available A/B test templates and configurations.

        Returns:
            Test templates and configurations
        """
        return {
            "test_types": {
                "ui_variation": {
                    "description": "Test different UI layouts, colors, or user flows",
                    "example_variants": ["current_ui", "new_ui_v1", "new_ui_v2"],
                    "metrics": ["click_through_rate", "time_on_page", "completion_rate"]
                },
                "research_strategy": {
                    "description": "Test different research algorithms or approaches",
                    "example_variants": ["standard_search", "deep_dive", "quick_summary"],
                    "metrics": ["response_quality", "user_satisfaction", "response_time"]
                },
                "feature_rollout": {
                    "description": "Gradually roll out new features to test adoption",
                    "example_variants": ["feature_off", "feature_on"],
                    "metrics": ["feature_usage", "user_engagement", "error_rate"]
                },
                "personalization": {
                    "description": "Test personalized vs generic experiences",
                    "example_variants": ["generic", "personalized_v1", "personalized_v2"],
                    "metrics": ["engagement_rate", "conversion_rate", "user_satisfaction"]
                },
                "citation_style": {
                    "description": "Test different citation style preferences",
                    "example_variants": ["apa_default", "mla_style", "chicago_style"],
                    "metrics": ["citation_usage", "user_preference", "accuracy_rate"]
                },
                "voice_commands": {
                    "description": "Test different voice command interpretations",
                    "example_variants": ["strict_matching", "fuzzy_matching", "context_aware"],
                    "metrics": ["command_success_rate", "user_frustration", "voice_usage"]
                }
            },
            "default_configs": self.default_test_configs,
            "allocation_methods": {
                "random": "Random assignment with equal weights",
                "consistent": "Same variant per user for consistency",
                "percentage": "Percentage-based traffic allocation",
                "segmented": "User segmentation based criteria"
            },
            "confidence_levels": {
                0.80: "80% confidence (quick results, less certainty)",
                0.90: "90% confidence (balanced)",
                0.95: "95% confidence (thorough, slower results)",
                0.99: "99% confidence (very thorough, much slower)"
            }
        }

    # Helper methods

    def _validate_test_data(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate A/B test configuration data."""
        errors = []

        # Required fields
        required_fields = ["name", "test_type", "variants"]
        for field in required_fields:
            if field not in test_data:
                errors.append(f"Missing required field: {field}")

        # Validate test type
        if "test_type" in test_data:
            valid_types = ["ui", "algorithm", "feature", "personalization", "research_strategy"]
            if test_data["test_type"] not in valid_types:
                errors.append(f"Invalid test_type. Must be one of: {', '.join(valid_types)}")

        # Validate variants
        if "variants" in test_data:
            variants = test_data["variants"]
            if not isinstance(variants, list) or len(variants) < 2:
                errors.append("At least 2 variants are required")

            variant_ids = []
            has_control = False
            for i, variant in enumerate(variants):
                if not isinstance(variant, dict):
                    errors.append(f"Variant {i} must be a dictionary")
                    continue

                if "id" not in variant or "name" not in variant:
                    errors.append(f"Variant {i} missing required 'id' or 'name' field")

                if variant.get("id") in variant_ids:
                    errors.append(f"Duplicate variant ID: {variant['id']}")
                else:
                    variant_ids.append(variant["id"])

                if variant.get("is_control"):
                    has_control = True

            if not has_control:
                errors.append("At least one variant must be marked as control (is_control: true)")

        # Validate numeric fields
        if "min_participants" in test_data and test_data["min_participants"] < 10:
            errors.append("min_participants must be at least 10")

        if "confidence_level" in test_data:
            confidence = test_data["confidence_level"]
            if not 0.5 <= confidence <= 0.99:
                errors.append("confidence_level must be between 0.5 and 0.99")

        return {
            "valid": len(errors) == 0,
            "errors": errors
        }

    def _generate_test_id(self, test_name: str) -> str:
        """Generate a unique test ID."""
        name_hash = hashlib.md5(test_name.encode()).hexdigest()[:6]
        timestamp = str(int(datetime.utcnow().timestamp()))
        return f"test_{name_hash}_{timestamp}"

    def _allocate_variant(self, variants: List[ABTestVariant], user_id: str,
                         method: str, user_context: Optional[Dict[str, Any]] = None) -> str:
        """
        Allocate a variant to a user based on the allocation method.

        Args:
            variants: List of available variants
            user_id: User ID for consistent allocation
            method: Allocation method
            user_context: User context for segmentation

        Returns:
            Selected variant ID
        """
        if method == "random":
            # Random allocation with weights
            total_weight = sum(v.weight for v in variants)
            rand_val = random.uniform(0, total_weight)
            cumulative_weight = 0

            for variant in variants:
                cumulative_weight += variant.weight
                if rand_val <= cumulative_weight:
                    return variant.variant_id

        elif method == "consistent":
            # Consistent allocation based on user ID hash
            user_hash = hashlib.md5(user_id.encode()).hexdigest()
            hash_int = int(user_hash[:8], 16)
            variant_index = hash_int % len(variants)
            return variants[variant_index].variant_id

        elif method == "percentage":
            # Percentage-based (simplified to equal distribution)
            variant_index = hash(user_id) % len(variants)
            return variants[variant_index].variant_id

        elif method == "segmented":
            # Simple segmentation based on user context
            if user_context and user_context.get("user_type") == "premium":
                # Premium users get variant with highest weight
                return max(variants, key=lambda v: v.weight).variant_id
            else:
                # Regular users get random allocation
                return random.choice(variants).variant_id

        # Default to random
        return random.choice(variants).variant_id

    def _perform_statistical_analysis(self, variant_metrics: Dict[str, Any],
                                   target_metric: str) -> Dict[str, Any]:
        """
        Perform statistical analysis on test results.

        Args:
            variant_metrics: Metrics for each variant
            target_metric: Target metric for analysis

        Returns:
            Statistical analysis results
        """
        # Simplified statistical analysis (would use proper statistical tests in production)
        analysis = {
            "has_significant_difference": False,
            "confidence_level": 0.0,
            "recommended_sample_size": 100,
            "analysis_method": "simplified_comparison"
        }

        if len(variant_metrics) >= 2:
            # Compare conversion rates or scores
            values = []
            for metrics in variant_metrics.values():
                if target_metric == "conversion_rate":
                    values.append(metrics["conversion_rate"])
                elif target_metric == "average_score":
                    values.append(metrics["average_score"])
                else:
                    values.append(metrics["conversion_rate"])  # Default

            if len(values) >= 2:
                max_val = max(values)
                min_val = min(values)
                difference = max_val - min_val

                # Simple significance check (very basic)
                total_participants = sum(m["participant_count"] for m in variant_metrics.values())
                if total_participants >= 100 and difference > 0.05:  # 5% difference threshold
                    analysis["has_significant_difference"] = True
                    analysis["confidence_level"] = min(0.95, 0.5 + (total_participants / 1000))  # Simplified

        return analysis

    def _determine_winner(self, variant_metrics: Dict[str, Any], min_participants: int,
                         confidence_level: float) -> Optional[Dict[str, Any]]:
        """
        Determine the winning variant based on results.

        Args:
            variant_metrics: Metrics for each variant
            min_participants: Minimum participants required
            confidence_level: Required confidence level

        Returns:
            Winner information or None
        """
        # Check if we have enough data
        total_participants = sum(m["participant_count"] for m in variant_metrics.values())
        if total_participants < min_participants:
            return None

        # Find variant with best performance
        best_variant = None
        best_score = -1

        for variant_id, metrics in variant_metrics.items():
            # Use conversion rate as primary metric
            score = metrics["conversion_rate"]
            if score > best_score:
                best_score = score
                best_variant = {
                    "variant_id": variant_id,
                    "name": metrics["name"],
                    "score": score,
                    "confidence_level": 0.90,  # Simplified
                    "improvement": score - min(m["conversion_rate"] for m in variant_metrics.values() if m != metrics)
                }

        return best_variant

    async def cleanup_completed_tests(self, session, days_to_keep: int = 90):
        """
        Clean up old completed tests and their data.

        Args:
            session: Database session
            days_to_keep: Days to keep completed test data
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)

            # Find old completed tests
            old_tests_query = session.query(ABTest).filter(
                ABTest.status == "completed",
                ABTest.completed_at < cutoff_date
            )

            old_tests = await session.execute(old_tests_query)
            old_test_ids = [test.id for test in old_tests.scalars()]

            # Delete associated data
            for test_id in old_test_ids:
                # Delete results
                await session.execute(
                    session.query(ABTestResult).filter(ABTestResult.test_id == test_id).delete()
                )

                # Delete participants
                await session.execute(
                    session.query(ABTestParticipant).filter(ABTestParticipant.test_id == test_id).delete()
                )

                # Delete variants
                await session.execute(
                    session.query(ABTestVariant).filter(ABTestVariant.test_id == test_id).delete()
                )

                # Delete test
                await session.execute(
                    session.query(ABTest).filter(ABTest.id == test_id).delete()
                )

            if old_test_ids:
                await session.commit()
                logger.info(f"Cleaned up {len(old_test_ids)} old A/B tests")

        except Exception as e:
            logger.error(f"Test cleanup failed: {e}")
            await session.rollback()
