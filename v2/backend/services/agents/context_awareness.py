"""
Context Awareness and User Preference Learning System for Galion Platform v2.2
Provides intelligent project context understanding and user preference learning.

Features:
- Project state tracking and analysis
- User preference learning and adaptation
- Context-aware decision making
- Historical interaction analysis
- Intelligent suggestions and recommendations
- Project relationship mapping

"Your imagination is the end."
"""

import asyncio
from typing import Dict, List, Optional, Any, Set, Tuple, Union
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from enum import Enum
import logging
import json
import re
from pathlib import Path
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)

class ContextType(Enum):
    """Types of context information"""
    PROJECT = "project"
    USER = "user"
    SESSION = "session"
    TASK = "task"
    AGENT = "agent"
    ENVIRONMENT = "environment"

class PreferenceType(Enum):
    """Types of user preferences"""
    AGENT_SELECTION = "agent_selection"
    TOOL_CHOICE = "tool_choice"
    PARAMETER_VALUES = "parameter_values"
    WORKFLOW_PATTERNS = "workflow_patterns"
    COMMUNICATION_STYLE = "communication_style"
    PRIORITY_SETTINGS = "priority_settings"

class ContextEntity(BaseModel):
    """An entity in the context graph"""

    id: str
    type: ContextType
    name: str
    properties: Dict[str, Any] = Field(default_factory=dict)
    relationships: Dict[str, List[str]] = Field(default_factory=dict)  # relationship_type -> entity_ids
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    confidence_score: float = 1.0

    def add_relationship(self, relationship_type: str, entity_id: str):
        """Add a relationship to another entity"""
        if relationship_type not in self.relationships:
            self.relationships[relationship_type] = []
        if entity_id not in self.relationships[relationship_type]:
            self.relationships[relationship_type].append(entity_id)
        self.updated_at = datetime.now()

    def remove_relationship(self, relationship_type: str, entity_id: str):
        """Remove a relationship"""
        if relationship_type in self.relationships:
            self.relationships[relationship_type] = [
                eid for eid in self.relationships[relationship_type] if eid != entity_id
            ]
        self.updated_at = datetime.now()

class UserPreference(BaseModel):
    """A learned user preference"""

    user_id: str
    preference_type: PreferenceType
    context_key: str  # What the preference applies to
    preference_value: Any
    confidence_score: float = 0.5
    observation_count: int = 1
    last_observed: datetime = Field(default_factory=datetime.now)
    first_observed: datetime = Field(default_factory=datetime.now)

    def update_observation(self, new_value: Any, weight: float = 1.0):
        """Update preference based on new observation"""
        self.last_observed = datetime.now()

        if self.preference_value == new_value:
            # Reinforce existing preference
            self.confidence_score = min(1.0, self.confidence_score + (weight * 0.1))
            self.observation_count += 1
        else:
            # Conflicting observation - reduce confidence
            self.confidence_score = max(0.1, self.confidence_score - (weight * 0.2))
            if self.confidence_score < 0.3:
                # Switch preference if confidence is low
                self.preference_value = new_value
                self.confidence_score = 0.4
                self.observation_count = 1
                self.first_observed = datetime.now()

class InteractionPattern(BaseModel):
    """A pattern of user-agent interaction"""

    pattern_id: str
    user_id: str
    trigger_context: Dict[str, Any]  # Context that triggers this pattern
    actions: List[Dict[str, Any]]    # Sequence of actions
    outcomes: List[Dict[str, Any]]   # Observed outcomes
    success_rate: float = 0.0
    frequency: int = 1
    last_used: datetime = Field(default_factory=datetime.now)
    first_observed: datetime = Field(default_factory=datetime.now)

class ProjectContext(BaseModel):
    """Context information about a project"""

    project_id: str
    name: str
    description: str = ""
    technologies: List[str] = Field(default_factory=list)
    file_structure: Dict[str, Any] = Field(default_factory=dict)
    dependencies: Dict[str, Any] = Field(default_factory=dict)
    recent_changes: List[Dict[str, Any]] = Field(default_factory=list)
    active_tasks: List[str] = Field(default_factory=list)
    collaborators: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    last_analyzed: datetime = Field(default_factory=datetime.now)

class ContextAwarenessEngine:
    """
    Main engine for context awareness and user preference learning.

    Features:
    - Context graph management
    - User preference learning
    - Project state analysis
    - Intelligent recommendations
    - Pattern recognition
    """

    def __init__(self):
        self.entities: Dict[str, ContextEntity] = {}
        self.user_preferences: Dict[str, Dict[str, UserPreference]] = defaultdict(dict)
        self.interaction_patterns: Dict[str, InteractionPattern] = {}
        self.project_contexts: Dict[str, ProjectContext] = {}

        # Configuration
        self.max_context_age = timedelta(days=30)
        self.preference_decay_factor = 0.95  # Daily decay
        self.min_confidence_threshold = 0.3
        self.pattern_similarity_threshold = 0.7

        self.logger = logging.getLogger(f"{__name__}.engine")

    def add_entity(self, entity: ContextEntity) -> bool:
        """Add an entity to the context graph"""
        if entity.id in self.entities:
            # Update existing entity
            existing = self.entities[entity.id]
            existing.properties.update(entity.properties)
            existing.relationships.update(entity.relationships)
            existing.updated_at = datetime.now()
            existing.confidence_score = entity.confidence_score
        else:
            self.entities[entity.id] = entity

        self.logger.debug(f"Added/updated entity: {entity.id} ({entity.type.value})")
        return True

    def get_entity(self, entity_id: str) -> Optional[ContextEntity]:
        """Get an entity by ID"""
        return self.entities.get(entity_id)

    def find_entities(
        self,
        entity_type: Optional[ContextType] = None,
        properties: Optional[Dict[str, Any]] = None,
        limit: int = 50
    ) -> List[ContextEntity]:
        """Find entities matching criteria"""
        matches = []

        for entity in self.entities.values():
            if entity_type and entity.type != entity_type:
                continue

            if properties:
                match = True
                for key, value in properties.items():
                    if entity.properties.get(key) != value:
                        match = False
                        break
                if not match:
                    continue

            matches.append(entity)

            if len(matches) >= limit:
                break

        return matches

    def add_relationship(self, from_id: str, to_id: str, relationship_type: str):
        """Add a relationship between entities"""
        if from_id in self.entities and to_id in self.entities:
            self.entities[from_id].add_relationship(relationship_type, to_id)
            # Add reverse relationship if applicable
            reverse_type = self._get_reverse_relationship(relationship_type)
            if reverse_type:
                self.entities[to_id].add_relationship(reverse_type, from_id)

    def _get_reverse_relationship(self, relationship_type: str) -> Optional[str]:
        """Get the reverse relationship type"""
        reverse_map = {
            "uses": "used_by",
            "used_by": "uses",
            "belongs_to": "contains",
            "contains": "belongs_to",
            "depends_on": "depended_on_by",
            "depended_on_by": "depends_on",
            "collaborates_with": "collaborates_with"
        }
        return reverse_map.get(relationship_type)

    def learn_user_preference(
        self,
        user_id: str,
        preference_type: PreferenceType,
        context_key: str,
        value: Any,
        weight: float = 1.0
    ):
        """Learn a user preference from interaction"""
        pref_key = f"{preference_type.value}:{context_key}"

        if pref_key not in self.user_preferences[user_id]:
            self.user_preferences[user_id][pref_key] = UserPreference(
                user_id=user_id,
                preference_type=preference_type,
                context_key=context_key,
                preference_value=value
            )
        else:
            self.user_preferences[user_id][pref_key].update_observation(value, weight)

    def get_user_preference(
        self,
        user_id: str,
        preference_type: PreferenceType,
        context_key: str,
        default_value: Any = None
    ) -> Any:
        """Get a learned user preference"""
        pref_key = f"{preference_type.value}:{context_key}"
        preference = self.user_preferences[user_id].get(pref_key)

        if preference and preference.confidence_score >= self.min_confidence_threshold:
            return preference.preference_value

        return default_value

    def get_user_preferences(
        self,
        user_id: str,
        preference_type: Optional[PreferenceType] = None,
        min_confidence: float = 0.3
    ) -> Dict[str, Any]:
        """Get all preferences for a user"""
        preferences = {}

        for pref_key, preference in self.user_preferences[user_id].items():
            if preference.confidence_score < min_confidence:
                continue

            if preference_type and preference.preference_type != preference_type:
                continue

            preferences[preference.context_key] = preference.preference_value

        return preferences

    def analyze_project_context(self, project_path: str, project_id: str) -> ProjectContext:
        """Analyze project structure and create context"""
        # This would analyze actual project files
        # For now, create a basic context

        context = ProjectContext(
            project_id=project_id,
            name=Path(project_path).name,
            description=f"Project at {project_path}",
            technologies=self._detect_technologies(project_path),
            file_structure=self._analyze_file_structure(project_path),
            last_analyzed=datetime.now()
        )

        self.project_contexts[project_id] = context
        return context

    def _detect_technologies(self, project_path: str) -> List[str]:
        """Detect technologies used in project"""
        technologies = []

        try:
            path = Path(project_path)

            # Check for package.json
            if (path / "package.json").exists():
                technologies.extend(["javascript", "nodejs"])

            # Check for requirements.txt
            if (path / "requirements.txt").exists():
                technologies.extend(["python"])

            # Check for Cargo.toml
            if (path / "Cargo.toml").exists():
                technologies.extend(["rust"])

            # Check for go.mod
            if (path / "go.mod").exists():
                technologies.extend(["go"])

            # Check for pom.xml
            if (path / "pom.xml").exists():
                technologies.extend(["java", "maven"])

        except Exception as e:
            self.logger.error(f"Error detecting technologies: {e}")

        return technologies

    def _analyze_file_structure(self, project_path: str) -> Dict[str, Any]:
        """Analyze project file structure"""
        try:
            path = Path(project_path)
            structure = {}

            # Count files by extension
            extensions = Counter()
            for file_path in path.rglob("*"):
                if file_path.is_file():
                    extensions[file_path.suffix] += 1

            structure["file_counts"] = dict(extensions)

            # Find important directories
            important_dirs = []
            for dir_path in path.rglob("*"):
                if dir_path.is_dir() and dir_path.name in ["src", "lib", "app", "components", "tests", "docs"]:
                    important_dirs.append(str(dir_path.relative_to(path)))

            structure["important_directories"] = important_dirs[:10]  # Limit

            return structure

        except Exception as e:
            self.logger.error(f"Error analyzing file structure: {e}")
            return {}

    def learn_interaction_pattern(
        self,
        user_id: str,
        context: Dict[str, Any],
        actions: List[Dict[str, Any]],
        outcome: Dict[str, Any]
    ):
        """Learn an interaction pattern from user behavior"""
        # Create pattern signature
        pattern_sig = self._create_pattern_signature(context, actions)

        if pattern_sig in self.interaction_patterns:
            # Update existing pattern
            pattern = self.interaction_patterns[pattern_sig]
            pattern.frequency += 1
            pattern.last_used = datetime.now()
            pattern.outcomes.append(outcome)

            # Recalculate success rate
            success_count = sum(1 for o in pattern.outcomes if o.get("success", False))
            pattern.success_rate = success_count / len(pattern.outcomes)

        else:
            # Create new pattern
            pattern = InteractionPattern(
                pattern_id=pattern_sig,
                user_id=user_id,
                trigger_context=context,
                actions=actions,
                outcomes=[outcome],
                success_rate=1.0 if outcome.get("success", False) else 0.0
            )
            self.interaction_patterns[pattern_sig] = pattern

    def _create_pattern_signature(self, context: Dict[str, Any], actions: List[Dict[str, Any]]) -> str:
        """Create a signature for an interaction pattern"""
        # Simplify context and actions for pattern matching
        context_sig = []
        for key in sorted(context.keys()):
            if key in ["task_type", "agent_type", "project_type"]:
                context_sig.append(f"{key}:{context[key]}")

        action_sig = []
        for action in actions[:3]:  # First 3 actions
            if "agent_type" in action:
                action_sig.append(f"agent:{action['agent_type']}")
            if "tool" in action:
                action_sig.append(f"tool:{action['tool']}")

        signature = f"{'|'.join(context_sig)}->{'|'.join(action_sig)}"
        return signature

    def find_similar_patterns(
        self,
        user_id: str,
        current_context: Dict[str, Any],
        current_actions: List[Dict[str, Any]]
    ) -> List[InteractionPattern]:
        """Find similar interaction patterns"""
        current_sig = self._create_pattern_signature(current_context, current_actions)
        similar_patterns = []

        for pattern in self.interaction_patterns.values():
            if pattern.user_id != user_id:
                continue

            # Calculate similarity
            similarity = self._calculate_pattern_similarity(current_sig, pattern.pattern_id)
            if similarity >= self.pattern_similarity_threshold:
                similar_patterns.append(pattern)

        # Sort by success rate and frequency
        similar_patterns.sort(key=lambda p: (p.success_rate, p.frequency), reverse=True)
        return similar_patterns[:5]  # Top 5

    def _calculate_pattern_similarity(self, sig1: str, sig2: str) -> float:
        """Calculate similarity between two pattern signatures"""
        # Simple string similarity for now
        # Could be enhanced with more sophisticated NLP

        words1 = set(sig1.split('|'))
        words2 = set(sig2.split('|'))

        intersection = words1 & words2
        union = words1 | words2

        return len(intersection) / len(union) if union else 0.0

    def get_context_recommendations(
        self,
        user_id: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get intelligent recommendations based on context"""
        recommendations = {
            "suggested_agents": [],
            "suggested_tools": [],
            "parameter_suggestions": {},
            "workflow_patterns": []
        }

        # Get user preferences
        agent_prefs = self.get_user_preferences(user_id, PreferenceType.AGENT_SELECTION)
        tool_prefs = self.get_user_preferences(user_id, PreferenceType.TOOL_CHOICE)
        param_prefs = self.get_user_preferences(user_id, PreferenceType.PARAMETER_VALUES)

        # Task type from context
        task_type = context.get("task_type", "")

        # Suggest agents based on preferences and task type
        if task_type:
            for agent_type, preference in agent_prefs.items():
                if task_type.lower() in agent_type.lower() or agent_type.lower() in task_type.lower():
                    recommendations["suggested_agents"].append({
                        "agent_type": agent_type,
                        "confidence": preference.confidence_score
                    })

        # Suggest tools
        for tool_name, preference in tool_prefs.items():
            if self._tool_matches_context(tool_name, context):
                recommendations["suggested_tools"].append({
                    "tool_name": tool_name,
                    "confidence": preference.confidence_score
                })

        # Parameter suggestions
        for param_key, param_value in param_prefs.items():
            recommendations["parameter_suggestions"][param_key] = param_value

        # Workflow patterns
        similar_patterns = self.find_similar_patterns(user_id, context, [])
        for pattern in similar_patterns:
            recommendations["workflow_patterns"].append({
                "pattern_id": pattern.pattern_id,
                "success_rate": pattern.success_rate,
                "frequency": pattern.frequency
            })

        return recommendations

    def _tool_matches_context(self, tool_name: str, context: Dict[str, Any]) -> bool:
        """Check if a tool matches the current context"""
        # Simple matching logic
        context_text = json.dumps(context).lower()
        return tool_name.lower() in context_text

    def update_project_context(self, project_id: str, changes: Dict[str, Any]):
        """Update project context with new information"""
        if project_id in self.project_contexts:
            context = self.project_contexts[project_id]

            # Update recent changes
            context.recent_changes.append({
                "timestamp": datetime.now(),
                "changes": changes
            })

            # Keep only recent changes (last 50)
            context.recent_changes = context.recent_changes[-50:]

            context.last_analyzed = datetime.now()

            # Update other fields if provided
            for key, value in changes.items():
                if hasattr(context, key):
                    setattr(context, key, value)

    def get_project_insights(self, project_id: str) -> Dict[str, Any]:
        """Get insights about a project"""
        context = self.project_contexts.get(project_id)
        if not context:
            return {}

        insights = {
            "technology_stack": context.technologies,
            "file_distribution": context.file_structure.get("file_counts", {}),
            "active_tasks": len(context.active_tasks),
            "recent_activity": len(context.recent_changes),
            "team_size": len(context.collaborators)
        }

        # Add trend analysis
        if context.recent_changes:
            recent_changes = context.recent_changes[-10:]  # Last 10 changes
            insights["activity_trend"] = "increasing" if len(recent_changes) > 5 else "stable"

        return insights

    async def cleanup_old_context(self):
        """Clean up old context information"""
        cutoff = datetime.now() - self.max_context_age

        # Clean up old entities
        to_remove = []
        for entity_id, entity in self.entities.items():
            if entity.updated_at < cutoff and entity.confidence_score < 0.5:
                to_remove.append(entity_id)

        for entity_id in to_remove:
            del self.entities[entity_id]

        # Apply preference decay
        for user_prefs in self.user_preferences.values():
            for preference in user_prefs.values():
                age_days = (datetime.now() - preference.last_observed).days
                decay = self.preference_decay_factor ** age_days
                preference.confidence_score *= decay

                # Remove very old/low confidence preferences
                if preference.confidence_score < 0.1 or age_days > 90:
                    # Mark for removal (would be cleaned up in a real implementation)
                    pass

        self.logger.info(f"Cleaned up {len(to_remove)} old entities")

# Global context awareness engine instance
context_engine = ContextAwarenessEngine()

# Helper functions for easy integration

def learn_user_preference(
    user_id: str,
    preference_type: PreferenceType,
    context_key: str,
    value: Any,
    weight: float = 1.0
):
    """Helper to learn user preferences"""
    context_engine.learn_user_preference(user_id, preference_type, context_key, value, weight)

def get_user_preference(
    user_id: str,
    preference_type: PreferenceType,
    context_key: str,
    default_value: Any = None
) -> Any:
    """Helper to get user preferences"""
    return context_engine.get_user_preference(user_id, preference_type, context_key, default_value)

def get_context_recommendations(user_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Helper to get context-aware recommendations"""
    return context_engine.get_context_recommendations(user_id, context)
