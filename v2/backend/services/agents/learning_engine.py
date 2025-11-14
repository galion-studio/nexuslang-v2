"""
Advanced Learning Engine for Galion Agents

Implements machine learning capabilities for agent self-improvement,
pattern recognition, and adaptive behavior.
"""

import asyncio
import logging
import json
import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque
import pickle
import os
from pathlib import Path

from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error
import pandas as pd

from .base_agent import AgentResult, AgentContext


logger = logging.getLogger(__name__)


@dataclass
class LearningPattern:
    """Represents a learned pattern or rule."""
    pattern_id: str
    pattern_type: str  # 'success_factor', 'failure_cause', 'optimization'
    conditions: Dict[str, Any]
    outcome: Any
    confidence: float
    sample_size: int
    last_updated: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentExperience:
    """Represents a single agent execution experience."""
    task_type: str
    input_features: Dict[str, Any]
    execution_result: AgentResult
    context: AgentContext
    timestamp: datetime
    performance_metrics: Dict[str, float]
    lessons_learned: List[str] = field(default_factory=list)


@dataclass
class LearningModel:
    """Container for trained ML models."""
    model_type: str
    model: Any
    feature_scaler: Optional[StandardScaler] = None
    label_encoder: Optional[LabelEncoder] = None
    feature_columns: List[str] = field(default_factory=list)
    training_accuracy: float = 0.0
    last_trained: datetime = None
    model_version: str = "1.0.0"


class LearningEngine:
    """
    Advanced learning engine for agent self-improvement.

    Features:
    - Pattern recognition and learning
    - Performance prediction
    - Adaptive behavior optimization
    - Experience-based learning
    - Collaborative learning across agents
    """

    def __init__(self, storage_path: str = "data/learning"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Learning data structures
        self.patterns: Dict[str, LearningPattern] = {}
        self.experiences: List[AgentExperience] = []
        self.models: Dict[str, LearningModel] = {}

        # Learning queues
        self.experience_queue = asyncio.Queue()
        self.learning_tasks: List[asyncio.Task] = []

        # Configuration
        self.learning_enabled = True
        self.min_samples_for_learning = 10
        self.max_experiences_stored = 10000
        self.learning_interval = 300  # 5 minutes
        self.model_retraining_threshold = 100  # Retrain after N new experiences

        # Learning state
        self.is_learning = False
        self.last_learning_cycle = datetime.now()

        # Load existing learning data
        self._load_learning_data()

    async def initialize(self) -> bool:
        """Initialize the learning engine."""
        try:
            # Start background learning tasks
            self.learning_tasks = [
                asyncio.create_task(self._continuous_learning_loop()),
                asyncio.create_task(self._pattern_discovery_loop()),
                asyncio.create_task(self._model_retraining_loop())
            ]

            logger.info("Learning engine initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize learning engine: {e}")
            return False

    async def cleanup(self) -> None:
        """Clean up learning engine resources."""
        # Cancel all learning tasks
        for task in self.learning_tasks:
            if not task.done():
                task.cancel()

        # Wait for tasks to complete
        if self.learning_tasks:
            await asyncio.gather(*self.learning_tasks, return_exceptions=True)

        # Save learning data
        await self._save_learning_data()

        logger.info("Learning engine cleaned up")

    def record_experience(self, experience: AgentExperience) -> None:
        """Record an agent execution experience for learning."""
        try:
            # Add to experiences list
            self.experiences.append(experience)

            # Limit experience storage
            if len(self.experiences) > self.max_experiences_stored:
                # Remove oldest experiences (keep 80% most recent)
                keep_count = int(self.max_experiences_stored * 0.8)
                self.experiences = self.experiences[-keep_count:]

            # Queue for immediate processing
            self.experience_queue.put_nowait(experience)

            logger.debug(f"Recorded experience for task type: {experience.task_type}")

        except Exception as e:
            logger.error(f"Failed to record experience: {e}")

    async def get_performance_prediction(self, task_type: str, features: Dict[str, Any]) -> Dict[str, Any]:
        """Predict task execution performance."""
        try:
            model_key = f"performance_{task_type}"
            if model_key not in self.models:
                return {"prediction": None, "confidence": 0.0, "available": False}

            model = self.models[model_key]

            # Prepare features for prediction
            feature_vector = self._prepare_features(features, model.feature_columns)

            if model.feature_scaler:
                feature_vector = model.feature_scaler.transform([feature_vector])

            # Make prediction
            prediction = model.model.predict(feature_vector)[0]

            # Get prediction confidence (if available)
            confidence = 0.8  # Default confidence
            if hasattr(model.model, 'predict_proba'):
                proba = model.model.predict_proba(feature_vector)[0]
                confidence = max(proba)
            elif hasattr(model.model, 'score'):
                confidence = model.model.score(feature_vector, [prediction])

            return {
                "prediction": float(prediction),
                "confidence": float(confidence),
                "available": True,
                "model_version": model.model_version,
                "last_trained": model.last_trained.isoformat() if model.last_trained else None
            }

        except Exception as e:
            logger.error(f"Failed to get performance prediction: {e}")
            return {"prediction": None, "confidence": 0.0, "available": False, "error": str(e)}

    def get_success_patterns(self, task_type: str) -> List[LearningPattern]:
        """Get learned patterns for successful task execution."""
        return [
            pattern for pattern in self.patterns.values()
            if pattern.pattern_type == 'success_factor' and
            pattern.conditions.get('task_type') == task_type
        ]

    def get_failure_patterns(self, task_type: str) -> List[LearningPattern]:
        """Get learned patterns for task failures."""
        return [
            pattern for pattern in self.patterns.values()
            if pattern.pattern_type == 'failure_cause' and
            pattern.conditions.get('task_type') == task_type
        ]

    def get_optimization_suggestions(self, task_type: str) -> List[Dict[str, Any]]:
        """Get optimization suggestions based on learned patterns."""
        suggestions = []

        # Get relevant patterns
        patterns = [
            pattern for pattern in self.patterns.values()
            if pattern.pattern_type == 'optimization' and
            pattern.conditions.get('task_type') == task_type and
            pattern.confidence > 0.7  # High confidence patterns only
        ]

        for pattern in patterns:
            suggestions.append({
                "suggestion": pattern.outcome,
                "confidence": pattern.confidence,
                "sample_size": pattern.sample_size,
                "conditions": pattern.conditions,
                "expected_improvement": pattern.metadata.get('expected_improvement', 'unknown')
            })

        return sorted(suggestions, key=lambda x: x['confidence'], reverse=True)

    async def collaborative_learning(self, other_agents_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform collaborative learning with other agents."""
        try:
            insights_gained = 0
            patterns_learned = 0

            for agent_data in other_agents_data:
                # Process experiences from other agents
                for exp_data in agent_data.get('experiences', []):
                    experience = AgentExperience(**exp_data)
                    self.record_experience(experience)
                    insights_gained += 1

                # Learn patterns from other agents
                for pattern_data in agent_data.get('patterns', []):
                    pattern = LearningPattern(**pattern_data)
                    if pattern.confidence > 0.6:  # Only high-confidence patterns
                        self.patterns[pattern.pattern_id] = pattern
                        patterns_learned += 1

            # Trigger learning cycle after collaborative learning
            await self._perform_learning_cycle()

            return {
                "insights_gained": insights_gained,
                "patterns_learned": patterns_learned,
                "learning_triggered": True
            }

        except Exception as e:
            logger.error(f"Collaborative learning failed: {e}")
            return {"error": str(e)}

    async def _continuous_learning_loop(self) -> None:
        """Continuous learning loop for processing experiences."""
        while self.learning_enabled:
            try:
                # Wait for experiences to process
                experience = await asyncio.wait_for(
                    self.experience_queue.get(),
                    timeout=self.learning_interval
                )

                # Process individual experience
                await self._process_experience(experience)

                # Check if we should trigger a learning cycle
                if len(self.experiences) % self.model_retraining_threshold == 0:
                    await self._perform_learning_cycle()

            except asyncio.TimeoutError:
                # No experiences to process, trigger periodic learning
                if (datetime.now() - self.last_learning_cycle).seconds >= self.learning_interval:
                    await self._perform_learning_cycle()

            except Exception as e:
                logger.error(f"Error in continuous learning loop: {e}")
                await asyncio.sleep(5)  # Brief pause before retry

    async def _pattern_discovery_loop(self) -> None:
        """Pattern discovery loop for finding new patterns."""
        while self.learning_enabled:
            try:
                await asyncio.sleep(self.learning_interval * 2)  # Less frequent than learning

                if len(self.experiences) >= self.min_samples_for_learning:
                    await self._discover_patterns()

            except Exception as e:
                logger.error(f"Error in pattern discovery loop: {e}")
                await asyncio.sleep(30)

    async def _model_retraining_loop(self) -> None:
        """Model retraining loop for updating ML models."""
        while self.learning_enabled:
            try:
                await asyncio.sleep(self.learning_interval * 4)  # Less frequent

                if len(self.experiences) >= self.min_samples_for_learning:
                    await self._retrain_models()

            except Exception as e:
                logger.error(f"Error in model retraining loop: {e}")
                await asyncio.sleep(60)

    async def _process_experience(self, experience: AgentExperience) -> None:
        """Process a single experience for immediate learning."""
        try:
            # Extract lessons from the experience
            lessons = await self._extract_lessons(experience)

            # Update existing patterns
            for lesson in lessons:
                await self._update_patterns(lesson, experience)

            # Store processed experience
            experience.lessons_learned = lessons

        except Exception as e:
            logger.error(f"Failed to process experience: {e}")

    async def _perform_learning_cycle(self) -> None:
        """Perform a complete learning cycle."""
        if self.is_learning:
            return  # Prevent concurrent learning cycles

        self.is_learning = True
        self.last_learning_cycle = datetime.now()

        try:
            logger.info("Starting learning cycle...")

            # Analyze recent experiences
            recent_experiences = [
                exp for exp in self.experiences
                if (datetime.now() - exp.timestamp).days <= 7  # Last 7 days
            ]

            if len(recent_experiences) >= self.min_samples_for_learning:
                # Update performance models
                await self._update_performance_models(recent_experiences)

                # Discover new patterns
                await self._discover_patterns()

                # Optimize existing patterns
                await self._optimize_patterns()

            logger.info(f"Learning cycle completed. Patterns: {len(self.patterns)}, Models: {len(self.models)}")

        except Exception as e:
            logger.error(f"Learning cycle failed: {e}")
        finally:
            self.is_learning = False

    async def _extract_lessons(self, experience: AgentExperience) -> List[str]:
        """Extract lessons from an experience."""
        lessons = []

        try:
            # Success/failure analysis
            if experience.execution_result.success:
                if experience.performance_metrics.get('response_time', 0) < 5.0:
                    lessons.append("fast_success")
                lessons.append("success_pattern")
            else:
                error_type = experience.execution_result.error or "unknown_error"
                lessons.append(f"failure_{error_type}")

            # Performance analysis
            response_time = experience.performance_metrics.get('response_time', 0)
            if response_time > 30.0:
                lessons.append("slow_execution")
            elif response_time < 2.0:
                lessons.append("fast_execution")

            # Resource usage analysis
            memory_usage = experience.performance_metrics.get('memory_mb', 0)
            if memory_usage > 500:
                lessons.append("high_memory_usage")

            cpu_usage = experience.performance_metrics.get('cpu_percent', 0)
            if cpu_usage > 80:
                lessons.append("high_cpu_usage")

            # Context analysis
            if experience.context.user_preferences:
                lessons.append("user_preference_utilized")

            if len(experience.context.collaboration_history) > 0:
                lessons.append("collaboration_used")

        except Exception as e:
            logger.error(f"Failed to extract lessons: {e}")

        return lessons

    async def _update_patterns(self, lesson: str, experience: AgentExperience) -> None:
        """Update or create patterns based on lessons learned."""
        try:
            # Create pattern key
            task_type = experience.task_type
            pattern_key = f"{task_type}_{lesson}"

            # Check if pattern exists
            if pattern_key in self.patterns:
                pattern = self.patterns[pattern_key]
                pattern.sample_size += 1
                pattern.last_updated = datetime.now()

                # Update confidence based on consistency
                if lesson.startswith('success'):
                    pattern.confidence = min(1.0, pattern.confidence + 0.05)
                elif lesson.startswith('failure'):
                    pattern.confidence = max(0.0, pattern.confidence - 0.05)

            else:
                # Create new pattern
                pattern_type = 'success_factor' if lesson.startswith('success') else \
                             'failure_cause' if lesson.startswith('failure') else \
                             'optimization'

                pattern = LearningPattern(
                    pattern_id=pattern_key,
                    pattern_type=pattern_type,
                    conditions={
                        'task_type': task_type,
                        'lesson_type': lesson
                    },
                    outcome=lesson,
                    confidence=0.5,  # Start with moderate confidence
                    sample_size=1,
                    last_updated=datetime.now(),
                    metadata={
                        'first_seen': experience.timestamp.isoformat(),
                        'performance_impact': experience.performance_metrics
                    }
                )

                self.patterns[pattern_key] = pattern

        except Exception as e:
            logger.error(f"Failed to update patterns: {e}")

    async def _update_performance_models(self, experiences: List[AgentExperience]) -> None:
        """Update ML models for performance prediction."""
        try:
            # Group experiences by task type
            task_groups = defaultdict(list)
            for exp in experiences:
                task_groups[exp.task_type].append(exp)

            for task_type, task_experiences in task_groups.items():
                if len(task_experiences) >= self.min_samples_for_learning:
                    await self._train_performance_model(task_type, task_experiences)

        except Exception as e:
            logger.error(f"Failed to update performance models: {e}")

    async def _train_performance_model(self, task_type: str, experiences: List[AgentExperience]) -> None:
        """Train a performance prediction model for a task type."""
        try:
            # Prepare training data
            X, y = self._prepare_training_data(experiences)

            if len(X) < self.min_samples_for_learning:
                return

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            # Train model
            model = GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=3,
                random_state=42
            )

            model.fit(X_train, y_train)

            # Evaluate model
            y_pred = model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            training_score = model.score(X_test, y_test)

            # Create learning model container
            feature_columns = [
                'input_length', 'context_size', 'collaboration_count',
                'user_preference_count', 'time_of_day', 'day_of_week'
            ]

            learning_model = LearningModel(
                model_type=f"performance_{task_type}",
                model=model,
                feature_columns=feature_columns,
                training_accuracy=training_score,
                last_trained=datetime.now(),
                model_version=f"1.{len(self.models)}"
            )

            # Store model
            model_key = f"performance_{task_type}"
            self.models[model_key] = learning_model

            logger.info(f"Trained performance model for {task_type}: accuracy={training_score:.3f}, mse={mse:.3f}")

        except Exception as e:
            logger.error(f"Failed to train performance model for {task_type}: {e}")

    def _prepare_training_data(self, experiences: List[AgentExperience]) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare training data from experiences."""
        X_data = []
        y_data = []

        for exp in experiences:
            # Extract features
            features = {
                'input_length': len(str(exp.input_features)),
                'context_size': len(str(exp.context.__dict__)),
                'collaboration_count': len(exp.context.collaboration_history),
                'user_preference_count': len(exp.context.user_preferences) if exp.context.user_preferences else 0,
                'time_of_day': exp.timestamp.hour,
                'day_of_week': exp.timestamp.weekday()
            }

            # Target: response time (or other performance metric)
            target = exp.performance_metrics.get('response_time', 10.0)

            X_data.append(list(features.values()))
            y_data.append(target)

        return np.array(X_data), np.array(y_data)

    def _prepare_features(self, features: Dict[str, Any], feature_columns: List[str]) -> np.ndarray:
        """Prepare feature vector for prediction."""
        feature_vector = []

        for col in feature_columns:
            if col in features:
                feature_vector.append(features[col])
            else:
                # Default values for missing features
                defaults = {
                    'input_length': 100,
                    'context_size': 50,
                    'collaboration_count': 0,
                    'user_preference_count': 0,
                    'time_of_day': 12,
                    'day_of_week': 1
                }
                feature_vector.append(defaults.get(col, 0))

        return np.array(feature_vector)

    async def _discover_patterns(self) -> None:
        """Discover new patterns in the experience data."""
        try:
            if len(self.experiences) < self.min_samples_for_learning * 2:
                return

            # Convert experiences to DataFrame for analysis
            df = pd.DataFrame([
                {
                    'task_type': exp.task_type,
                    'success': exp.execution_result.success,
                    'response_time': exp.performance_metrics.get('response_time', 0),
                    'memory_mb': exp.performance_metrics.get('memory_mb', 0),
                    'cpu_percent': exp.performance_metrics.get('cpu_percent', 0),
                    'input_length': len(str(exp.input_features)),
                    'collaboration_used': len(exp.context.collaboration_history) > 0,
                    'user_prefs_used': bool(exp.context.user_preferences),
                    'timestamp': exp.timestamp
                }
                for exp in self.experiences[-1000:]  # Last 1000 experiences
            ])

            # Discover success patterns
            success_patterns = await self._find_success_patterns(df)

            # Discover failure patterns
            failure_patterns = await self._find_failure_patterns(df)

            # Discover optimization opportunities
            optimization_patterns = await self._find_optimization_patterns(df)

            # Store discovered patterns
            all_patterns = success_patterns + failure_patterns + optimization_patterns

            for pattern in all_patterns:
                if pattern.confidence > 0.6:  # Only store high-confidence patterns
                    self.patterns[pattern.pattern_id] = pattern

            logger.info(f"Discovered {len(all_patterns)} new patterns")

        except Exception as e:
            logger.error(f"Pattern discovery failed: {e}")

    async def _find_success_patterns(self, df: pd.DataFrame) -> List[LearningPattern]:
        """Find patterns that correlate with success."""
        patterns = []

        try:
            # Group by task type and analyze success factors
            for task_type in df['task_type'].unique():
                task_data = df[df['task_type'] == task_type]

                if len(task_data) < self.min_samples_for_learning:
                    continue

                # Analyze collaboration impact
                collab_success = task_data[task_data['collaboration_used'] == True]['success'].mean()
                no_collab_success = task_data[task_data['collaboration_used'] == False]['success'].mean()

                if collab_success > no_collab_success + 0.1:  # 10% improvement
                    pattern = LearningPattern(
                        pattern_id=f"{task_type}_collaboration_success",
                        pattern_type="success_factor",
                        conditions={'task_type': task_type, 'collaboration_used': True},
                        outcome="Use collaboration for better success rates",
                        confidence=min(collab_success, 0.95),
                        sample_size=len(task_data),
                        last_updated=datetime.now(),
                        metadata={'improvement': collab_success - no_collab_success}
                    )
                    patterns.append(pattern)

                # Analyze user preferences impact
                pref_success = task_data[task_data['user_prefs_used'] == True]['success'].mean()
                no_pref_success = task_data[task_data['user_prefs_used'] == False]['success'].mean()

                if pref_success > no_pref_success + 0.1:
                    pattern = LearningPattern(
                        pattern_id=f"{task_type}_preferences_success",
                        pattern_type="success_factor",
                        conditions={'task_type': task_type, 'user_prefs_used': True},
                        outcome="Utilize user preferences for better outcomes",
                        confidence=min(pref_success, 0.95),
                        sample_size=len(task_data),
                        last_updated=datetime.now(),
                        metadata={'improvement': pref_success - no_pref_success}
                    )
                    patterns.append(pattern)

        except Exception as e:
            logger.error(f"Success pattern discovery failed: {e}")

        return patterns

    async def _find_failure_patterns(self, df: pd.DataFrame) -> List[LearningPattern]:
        """Find patterns that correlate with failures."""
        patterns = []

        try:
            # Analyze failure causes
            failure_data = df[df['success'] == False]

            if len(failure_data) >= self.min_samples_for_learning:
                # High memory usage failures
                high_memory_failures = failure_data[failure_data['memory_mb'] > 400]
                if len(high_memory_failures) > len(failure_data) * 0.3:  # 30% of failures
                    pattern = LearningPattern(
                        pattern_id="high_memory_failures",
                        pattern_type="failure_cause",
                        conditions={'memory_mb': '>400'},
                        outcome="High memory usage increases failure risk",
                        confidence=len(high_memory_failures) / len(failure_data),
                        sample_size=len(failure_data),
                        last_updated=datetime.now(),
                        metadata={'failure_rate': len(high_memory_failures) / len(failure_data)}
                    )
                    patterns.append(pattern)

                # High CPU usage failures
                high_cpu_failures = failure_data[failure_data['cpu_percent'] > 80]
                if len(high_cpu_failures) > len(failure_data) * 0.3:
                    pattern = LearningPattern(
                        pattern_id="high_cpu_failures",
                        pattern_type="failure_cause",
                        conditions={'cpu_percent': '>80'},
                        outcome="High CPU usage increases failure risk",
                        confidence=len(high_cpu_failures) / len(failure_data),
                        sample_size=len(failure_data),
                        last_updated=datetime.now(),
                        metadata={'failure_rate': len(high_cpu_failures) / len(failure_data)}
                    )
                    patterns.append(pattern)

        except Exception as e:
            logger.error(f"Failure pattern discovery failed: {e}")

        return patterns

    async def _find_optimization_patterns(self, df: pd.DataFrame) -> List[LearningPattern]:
        """Find optimization opportunities."""
        patterns = []

        try:
            # Analyze performance optimization opportunities
            for task_type in df['task_type'].unique():
                task_data = df[df['task_type'] == task_type]

                if len(task_data) < self.min_samples_for_learning:
                    continue

                # Response time optimization
                fast_executions = task_data[task_data['response_time'] < 5.0]
                slow_executions = task_data[task_data['response_time'] > 30.0]

                if len(fast_executions) > len(task_data) * 0.4:  # 40% fast executions
                    pattern = LearningPattern(
                        pattern_id=f"{task_type}_fast_execution_pattern",
                        pattern_type="optimization",
                        conditions={'task_type': task_type, 'response_time': '<5.0'},
                        outcome="Optimize for fast execution patterns",
                        confidence=len(fast_executions) / len(task_data),
                        sample_size=len(task_data),
                        last_updated=datetime.now(),
                        metadata={'expected_improvement': 'faster_execution'}
                    )
                    patterns.append(pattern)

                # Memory optimization
                low_memory = task_data[task_data['memory_mb'] < 200]
                high_memory = task_data[task_data['memory_mb'] > 500]

                if len(low_memory) > len(task_data) * 0.4:
                    pattern = LearningPattern(
                        pattern_id=f"{task_type}_memory_efficient",
                        pattern_type="optimization",
                        conditions={'task_type': task_type, 'memory_mb': '<200'},
                        outcome="Use memory-efficient execution patterns",
                        confidence=len(low_memory) / len(task_data),
                        sample_size=len(task_data),
                        last_updated=datetime.now(),
                        metadata={'expected_improvement': 'lower_memory_usage'}
                    )
                    patterns.append(pattern)

        except Exception as e:
            logger.error(f"Optimization pattern discovery failed: {e}")

        return patterns

    async def _optimize_patterns(self) -> None:
        """Optimize existing patterns for better accuracy."""
        try:
            # Remove low-confidence patterns
            low_confidence = [
                pid for pid, pattern in self.patterns.items()
                if pattern.confidence < 0.3 or pattern.sample_size < 5
            ]

            for pid in low_confidence:
                del self.patterns[pid]

            # Consolidate similar patterns
            pattern_groups = defaultdict(list)
            for pattern in self.patterns.values():
                key = f"{pattern.pattern_type}_{pattern.conditions.get('task_type', 'general')}"
                pattern_groups[key].append(pattern)

            for group_key, group_patterns in pattern_groups.items():
                if len(group_patterns) > 1:
                    # Keep the highest confidence pattern
                    best_pattern = max(group_patterns, key=lambda p: p.confidence)

                    # Remove others
                    for pattern in group_patterns:
                        if pattern.pattern_id != best_pattern.pattern_id:
                            if pattern.pattern_id in self.patterns:
                                del self.patterns[pattern.pattern_id]

                    # Update best pattern with combined sample size
                    best_pattern.sample_size = sum(p.sample_size for p in group_patterns)

        except Exception as e:
            logger.error(f"Pattern optimization failed: {e}")

    async def _retrain_models(self) -> None:
        """Retrain ML models with new data."""
        try:
            # Retrain models that have enough new data
            for model_key, model in self.models.items():
                task_type = model_key.replace('performance_', '')

                # Get recent experiences for this task type
                recent_experiences = [
                    exp for exp in self.experiences[-self.model_retraining_threshold:]
                    if exp.task_type == task_type
                ]

                if len(recent_experiences) >= self.min_samples_for_learning:
                    await self._train_performance_model(task_type, recent_experiences)
                    logger.info(f"Retrained model for {task_type}")

        except Exception as e:
            logger.error(f"Model retraining failed: {e}")

    def _load_learning_data(self) -> None:
        """Load learning data from disk."""
        try:
            # Load patterns
            patterns_file = self.storage_path / "patterns.json"
            if patterns_file.exists():
                with open(patterns_file, 'r') as f:
                    patterns_data = json.load(f)
                    for pid, pdata in patterns_data.items():
                        self.patterns[pid] = LearningPattern(**pdata)

            # Load experiences
            experiences_file = self.storage_path / "experiences.pkl"
            if experiences_file.exists():
                with open(experiences_file, 'rb') as f:
                    self.experiences = pickle.load(f)

            # Load models
            models_dir = self.storage_path / "models"
            if models_dir.exists():
                for model_file in models_dir.glob("*.pkl"):
                    try:
                        with open(model_file, 'rb') as f:
                            model_data = pickle.load(f)
                            model_key = model_file.stem
                            self.models[model_key] = model_data
                    except Exception as e:
                        logger.error(f"Failed to load model {model_file}: {e}")

            logger.info(f"Loaded learning data: {len(self.patterns)} patterns, {len(self.experiences)} experiences, {len(self.models)} models")

        except Exception as e:
            logger.error(f"Failed to load learning data: {e}")

    async def _save_learning_data(self) -> None:
        """Save learning data to disk."""
        try:
            # Save patterns
            patterns_file = self.storage_path / "patterns.json"
            patterns_data = {
                pid: {
                    **pattern.__dict__,
                    'last_updated': pattern.last_updated.isoformat()
                }
                for pid, pattern in self.patterns.items()
            }

            with open(patterns_file, 'w') as f:
                json.dump(patterns_data, f, indent=2)

            # Save experiences (limit to recent ones)
            experiences_file = self.storage_path / "experiences.pkl"
            recent_experiences = self.experiences[-5000:]  # Keep last 5000

            with open(experiences_file, 'wb') as f:
                pickle.dump(recent_experiences, f)

            # Save models
            models_dir = self.storage_path / "models"
            models_dir.mkdir(exist_ok=True)

            for model_key, model in self.models.items():
                model_file = models_dir / f"{model_key}.pkl"
                try:
                    with open(model_file, 'wb') as f:
                        pickle.dump(model, f)
                except Exception as e:
                    logger.error(f"Failed to save model {model_key}: {e}")

            logger.info("Saved learning data to disk")

        except Exception as e:
            logger.error(f"Failed to save learning data: {e}")

    def get_learning_stats(self) -> Dict[str, Any]:
        """Get learning engine statistics."""
        return {
            "patterns_learned": len(self.patterns),
            "experiences_processed": len(self.experiences),
            "models_trained": len(self.models),
            "learning_enabled": self.learning_enabled,
            "is_learning": self.is_learning,
            "last_learning_cycle": self.last_learning_cycle.isoformat() if self.last_learning_cycle else None,
            "storage_path": str(self.storage_path)
        }
