"""
Natural Language Task Processing System for Galion Platform v2.2
Provides advanced NLP capabilities for task understanding and decomposition.

Features:
- Task intent recognition and classification
- Entity extraction and relationship analysis
- Context-aware task decomposition
- Risk and complexity assessment
- Multi-step task planning
- Dependency analysis
- Ambiguity detection and resolution

"Your imagination is the end."
"""

import re
from typing import Dict, List, Optional, Any, Tuple, Set
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
import logging
import json

logger = logging.getLogger(__name__)

class TaskIntent(Enum):
    """Types of task intents"""
    CREATE = "create"
    MODIFY = "modify"
    ANALYZE = "analyze"
    DELETE = "delete"
    EXECUTE = "execute"
    SEARCH = "search"
    COMMUNICATE = "communicate"
    MANAGE = "manage"
    DEBUG = "debug"
    DEPLOY = "deploy"
    TEST = "test"
    DOCUMENT = "document"

class TaskComplexity(Enum):
    """Task complexity levels"""
    SIMPLE = "simple"       # Single action, no dependencies
    MODERATE = "moderate"   # Multiple steps, some dependencies
    COMPLEX = "complex"     # Many steps, complex dependencies
    VERY_COMPLEX = "very_complex"  # Multi-phase, high coordination needed

class TaskRisk(Enum):
    """Task risk levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ExtractedEntity(BaseModel):
    """An entity extracted from text"""

    text: str
    type: str  # "file", "function", "class", "url", "email", "number", etc.
    start_pos: int
    end_pos: int
    confidence: float = 1.0
    metadata: Dict[str, Any] = Field(default_factory=dict)

class TaskComponent(BaseModel):
    """A component of a decomposed task"""

    id: str
    description: str
    intent: TaskIntent
    primary_action: str
    target_entities: List[str] = Field(default_factory=list)
    required_tools: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    estimated_effort: float = 1.0  # hours
    risk_level: TaskRisk = TaskRisk.LOW
    requires_approval: bool = False
    priority: int = 1  # 1-5, higher is more important

class TaskAnalysis(BaseModel):
    """Complete analysis of a task"""

    original_text: str
    intent: TaskIntent
    complexity: TaskComplexity
    risk_level: TaskRisk
    confidence_score: float

    # Extracted information
    entities: List[ExtractedEntity] = Field(default_factory=list)
    key_phrases: List[str] = Field(default_factory=list)
    action_verbs: List[str] = Field(default_factory=list)

    # Decomposed components
    components: List[TaskComponent] = Field(default_factory=list)
    dependencies: List[Tuple[str, str]] = Field(default_factory=list)

    # Context and metadata
    domain_context: str = ""  # "development", "business", "analysis", etc.
    urgency_indicators: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)

    # Analysis metadata
    analysis_timestamp: datetime = Field(default_factory=datetime.now)
    processing_time: float = 0.0

class NLPProcessor:
    """
    Advanced NLP processor for task understanding and decomposition.

    Provides intelligent analysis of user requests to enable better
    autonomous task execution.
    """

    def __init__(self):
        # Intent classification patterns
        self.intent_patterns = self._load_intent_patterns()

        # Entity extraction patterns
        self.entity_patterns = self._load_entity_patterns()

        # Complexity assessment rules
        self.complexity_rules = self._load_complexity_rules()

        # Risk assessment keywords
        self.risk_keywords = self._load_risk_keywords()

        # Domain-specific patterns
        self.domain_patterns = self._load_domain_patterns()

        logger.info("NLP Processor initialized")

    def _load_intent_patterns(self) -> Dict[TaskIntent, List[str]]:
        """Load patterns for intent classification"""
        return {
            TaskIntent.CREATE: [
                r'\b(create|build|make|develop|generate|produce|write)\b',
                r'\b(add|insert|new)\b',
                r'\b(implement|design)\b'
            ],
            TaskIntent.MODIFY: [
                r'\b(update|change|modify|edit|alter|fix|improve|enhance)\b',
                r'\b(refactor|restructure)\b',
                r'\b(optimize|improve|enhance)\b'
            ],
            TaskIntent.ANALYZE: [
                r'\b(analyze|examine|review|check|inspect|investigate)\b',
                r'\b(measure|evaluate|assess)\b',
                r'\b(find|discover|identify|detect)\b'
            ],
            TaskIntent.DELETE: [
                r'\b(delete|remove|destroy|erase|clear)\b',
                r'\b(clean|purge|uninstall)\b'
            ],
            TaskIntent.EXECUTE: [
                r'\b(run|execute|start|launch|perform)\b',
                r'\b(process|handle|manage)\b',
                r'\b(activate|enable|trigger)\b'
            ],
            TaskIntent.SEARCH: [
                r'\b(find|search|locate|look.*for)\b',
                r'\b(query|retrieve|fetch|get)\b'
            ],
            TaskIntent.COMMUNICATE: [
                r'\b(send|email|message|notify|contact)\b',
                r'\b(share|distribute|broadcast)\b'
            ],
            TaskIntent.MANAGE: [
                r'\b(manage|administer|configure|setup)\b',
                r'\b(monitor|track|control)\b'
            ],
            TaskIntent.DEBUG: [
                r'\b(debug|fix|resolve|troubleshoot)\b',
                r'\b(error|issue|problem|bug)\b'
            ],
            TaskIntent.DEPLOY: [
                r'\b(deploy|release|publish|push)\b',
                r'\b(install|setup|configure)\b'
            ],
            TaskIntent.TEST: [
                r'\b(test|validate|verify|check)\b',
                r'\b(quality|assurance|qa)\b'
            ],
            TaskIntent.DOCUMENT: [
                r'\b(document|doc|readme|comment)\b',
                r'\b(describe|explain|record)\b'
            ]
        }

    def _load_entity_patterns(self) -> Dict[str, List[str]]:
        """Load patterns for entity extraction"""
        return {
            "file": [
                r'\b\w+\.(py|js|ts|java|cpp|c|cs|php|rb|go|rs|html|css|md|txt|json|xml|yaml|yml)\b',
                r'\b[a-zA-Z0-9_/-]+\.(py|js|ts|java|cpp|c|cs|php|rb|go|rs|html|css|md|txt|json|xml|yaml|yml)\b'
            ],
            "function": [
                r'\bdef\s+\w+\s*\(',
                r'\bfunction\s+\w+\s*\(',
                r'\w+\s*\([^)]*\)\s*\{'
            ],
            "class": [
                r'\bclass\s+\w+',
                r'\binterface\s+\w+'
            ],
            "url": [
                r'https?://[^\s]+',
                r'www\.[^\s]+'
            ],
            "email": [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            ],
            "number": [
                r'\b\d+(\.\d+)?\b'
            ],
            "date": [
                r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',
                r'\b\d{4}-\d{2}-\d{2}\b'
            ]
        }

    def _load_complexity_rules(self) -> Dict[str, int]:
        """Load rules for complexity assessment"""
        return {
            "multiple_actions": 2,      # Text contains multiple action verbs
            "dependencies": 3,          # Explicit dependencies mentioned
            "coordination": 2,          # Multiple actors/agents needed
            "time_constraints": 2,      # Urgency or deadlines mentioned
            "high_risk": 3,             # High-risk operations
            "external_integration": 2,  # External systems involved
            "complex_logic": 2,         # Conditional or complex logic
            "large_scope": 3            # Broad scope or many components
        }

    def _load_risk_keywords(self) -> Dict[TaskRisk, List[str]]:
        """Load keywords for risk assessment"""
        return {
            TaskRisk.CRITICAL: [
                r'\b(delete.*all|drop.*database|format.*disk)\b',
                r'\b(shutdown|power.*off|restart.*server)\b',
                r'\b(overwrite|replace.*production)\b'
            ],
            TaskRisk.HIGH: [
                r'\b(delete|remove|drop|erase)\b.*\b(production|live|main)\b',
                r'\b(modify|change|update)\b.*\b(security|auth|permission)\b',
                r'\b(deploy|push)\b.*\b(production|live)\b',
                r'\b(migrate|transfer)\b.*\b(data|database)\b'
            ],
            TaskRisk.MEDIUM: [
                r'\b(update|modify|change)\b.*\b(database|data)\b',
                r'\b(install|add)\b.*\b(dependency|package|library)\b',
                r'\b(configure|setup)\b.*\b(server|network|security)\b'
            ],
            TaskRisk.LOW: []  # Default case
        }

    def _load_domain_patterns(self) -> Dict[str, List[str]]:
        """Load domain-specific patterns"""
        return {
            "development": [
                r'\b(code|program|develop|implement|function|class|module)\b',
                r'\b(git|commit|push|pull|merge|branch)\b',
                r'\b(build|compile|test|debug|deploy)\b'
            ],
            "business": [
                r'\b(sales|revenue|profit|budget|financial|market)\b',
                r'\b(customer|client|user|stakeholder)\b',
                r'\b(report|analysis|metric|kpi|dashboard)\b'
            ],
            "analysis": [
                r'\b(analyze|data|metric|report|insight|trend)\b',
                r'\b(visualization|chart|graph|dashboard)\b',
                r'\b(statistics|correlation|prediction|model)\b'
            ],
            "infrastructure": [
                r'\b(server|database|network|cloud|aws|docker|kubernetes)\b',
                r'\b(monitor|alert|log|performance|scalability)\b',
                r'\b(backup|security|compliance|audit)\b'
            ]
        }

    async def analyze_task(self, text: str, context: Dict[str, Any] = None) -> TaskAnalysis:
        """
        Perform comprehensive NLP analysis of a task description.

        Args:
            text: The task description text
            context: Additional context information

        Returns:
            Complete task analysis
        """
        start_time = datetime.now()

        # Initialize analysis
        analysis = TaskAnalysis(
            original_text=text,
            intent=TaskIntent.EXECUTE,  # default
            complexity=TaskComplexity.SIMPLE,
            risk_level=TaskRisk.LOW,
            confidence_score=0.5
        )

        try:
            # Step 1: Intent Classification
            analysis.intent = self._classify_intent(text)

            # Step 2: Entity Extraction
            analysis.entities = self._extract_entities(text)

            # Step 3: Key Phrase and Action Extraction
            analysis.key_phrases = self._extract_key_phrases(text)
            analysis.action_verbs = self._extract_action_verbs(text)

            # Step 4: Domain Context
            analysis.domain_context = self._identify_domain(text)

            # Step 5: Complexity Assessment
            analysis.complexity = self._assess_complexity(text, analysis)

            # Step 6: Risk Assessment
            analysis.risk_level = self._assess_risk(text, analysis)

            # Step 7: Urgency and Constraints
            analysis.urgency_indicators = self._extract_urgency_indicators(text)
            analysis.constraints = self._extract_constraints(text)

            # Step 8: Task Decomposition
            analysis.components = self._decompose_task(text, analysis)
            analysis.dependencies = self._analyze_dependencies(analysis.components)

            # Step 9: Confidence Scoring
            analysis.confidence_score = self._calculate_confidence(analysis)

            # Step 10: Processing time
            analysis.processing_time = (datetime.now() - start_time).total_seconds()

        except Exception as e:
            logger.error(f"Error in task analysis: {e}")
            analysis.confidence_score = 0.1

        return analysis

    def _classify_intent(self, text: str) -> TaskIntent:
        """Classify the primary intent of the text"""
        text_lower = text.lower()
        scores = {}

        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, text_lower, re.IGNORECASE))
                score += matches
            scores[intent] = score

        # Return intent with highest score
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]

        return TaskIntent.EXECUTE

    def _extract_entities(self, text: str) -> List[ExtractedEntity]:
        """Extract entities from text"""
        entities = []

        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    entities.append(ExtractedEntity(
                        text=match.group(),
                        type=entity_type,
                        start_pos=match.start(),
                        end_pos=match.end(),
                        confidence=0.8
                    ))

        # Remove duplicates based on text and type
        unique_entities = []
        seen = set()
        for entity in entities:
            key = (entity.text.lower(), entity.type)
            if key not in seen:
                seen.add(key)
                unique_entities.append(entity)

        return unique_entities

    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract important phrases from text"""
        # Simple noun phrase extraction
        # In a real implementation, use spaCy or similar NLP library

        phrases = []

        # Extract quoted phrases
        quotes = re.findall(r'"([^"]*)"', text)
        phrases.extend(quotes)

        # Extract phrases with specific patterns
        patterns = [
            r'\b\d+\s+\w+\b',  # "3 files", "2 hours"
            r'\b\w+\s+and\s+\w+\b',  # "code and test"
            r'\b\w+\s+to\s+\w+\b',  # "login to system"
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            phrases.extend(matches)

        return list(set(phrases))[:10]  # Limit and deduplicate

    def _extract_action_verbs(self, text: str) -> List[str]:
        """Extract action verbs from text"""
        action_verbs = [
            "create", "build", "make", "develop", "implement", "add", "update", "change",
            "modify", "delete", "remove", "analyze", "check", "test", "run", "execute",
            "deploy", "install", "configure", "setup", "fix", "debug", "optimize",
            "document", "write", "read", "search", "find", "get", "set", "process"
        ]

        found_verbs = []
        text_lower = text.lower()

        for verb in action_verbs:
            if verb in text_lower:
                found_verbs.append(verb)

        return found_verbs

    def _identify_domain(self, text: str) -> str:
        """Identify the domain context of the text"""
        text_lower = text.lower()
        domain_scores = {}

        for domain, patterns in self.domain_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, text_lower, re.IGNORECASE))
                score += matches
            domain_scores[domain] = score

        if domain_scores:
            return max(domain_scores.items(), key=lambda x: x[1])[0]

        return "general"

    def _assess_complexity(self, text: str, analysis: TaskAnalysis) -> TaskComplexity:
        """Assess the complexity of the task"""
        complexity_score = 0

        # Count action verbs
        if len(analysis.action_verbs) > 3:
            complexity_score += self.complexity_rules.get("multiple_actions", 1)

        # Check for dependencies
        if any(word in text.lower() for word in ["after", "before", "then", "depends", "requires"]):
            complexity_score += self.complexity_rules.get("dependencies", 1)

        # Check for coordination
        if any(word in text.lower() for word in ["team", "together", "coordinate", "multiple"]):
            complexity_score += self.complexity_rules.get("coordination", 1)

        # Check for time constraints
        if any(word in text.lower() for word in ["urgent", "asap", "deadline", "today", "now"]):
            complexity_score += self.complexity_rules.get("time_constraints", 1)

        # Check for external integrations
        if any(word in text.lower() for word in ["api", "webhook", "integration", "external"]):
            complexity_score += self.complexity_rules.get("external_integration", 1)

        # Map score to complexity level
        if complexity_score >= 8:
            return TaskComplexity.VERY_COMPLEX
        elif complexity_score >= 5:
            return TaskComplexity.COMPLEX
        elif complexity_score >= 3:
            return TaskComplexity.MODERATE
        else:
            return TaskComplexity.SIMPLE

    def _assess_risk(self, text: str, analysis: TaskAnalysis) -> TaskRisk:
        """Assess the risk level of the task"""
        text_lower = text.lower()

        # Check for critical risk keywords
        for pattern in self.risk_keywords[TaskRisk.CRITICAL]:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return TaskRisk.CRITICAL

        # Check for high risk keywords
        for pattern in self.risk_keywords[TaskRisk.HIGH]:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return TaskRisk.HIGH

        # Check for medium risk keywords
        for pattern in self.risk_keywords[TaskRisk.MEDIUM]:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return TaskRisk.MEDIUM

        return TaskRisk.LOW

    def _extract_urgency_indicators(self, text: str) -> List[str]:
        """Extract urgency indicators from text"""
        indicators = []
        text_lower = text.lower()

        urgent_words = [
            "urgent", "asap", "immediately", "right away", "now", "today",
            "deadline", "critical", "emergency", "priority", "rush"
        ]

        for word in urgent_words:
            if word in text_lower:
                indicators.append(word)

        return indicators

    def _extract_constraints(self, text: str) -> List[str]:
        """Extract constraints from text"""
        constraints = []

        # Look for constraint patterns
        constraint_patterns = [
            r'\b(must|should|need to|have to)\b[^.]*',
            r'\b(without|no|never)\b[^.]*',
            r'\b(before|after|when)\b[^.]*',
            r'\b(limit|maximum|minimum)\b[^.]*'
        ]

        for pattern in constraint_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            constraints.extend(matches[:2])  # Limit per pattern

        return constraints[:5]  # Limit total constraints

    def _decompose_task(self, text: str, analysis: TaskAnalysis) -> List[TaskComponent]:
        """Decompose task into components"""
        components = []

        # Simple decomposition based on sentences and action verbs
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        for i, sentence in enumerate(sentences):
            if not sentence:
                continue

            # Create component for each sentence with actions
            component = TaskComponent(
                id=f"component_{i+1}",
                description=sentence,
                intent=analysis.intent,
                primary_action=self._extract_primary_action(sentence),
                target_entities=[e.text for e in analysis.entities if e.start_pos >= text.find(sentence)],
                estimated_effort=self._estimate_effort(sentence, analysis.complexity),
                risk_level=analysis.risk_level,
                requires_approval=analysis.risk_level in [TaskRisk.HIGH, TaskRisk.CRITICAL]
            )

            components.append(component)

        # If no components found, create a single one
        if not components:
            components.append(TaskComponent(
                id="main_component",
                description=text,
                intent=analysis.intent,
                primary_action="execute",
                estimated_effort=1.0,
                risk_level=analysis.risk_level
            ))

        return components

    def _extract_primary_action(self, sentence: str) -> str:
        """Extract the primary action from a sentence"""
        sentence_lower = sentence.lower()

        # Find first action verb
        for verb in self.intent_patterns.keys():
            for pattern in self.intent_patterns[verb]:
                if re.search(pattern, sentence_lower, re.IGNORECASE):
                    return verb.value

        return "execute"

    def _estimate_effort(self, sentence: str, complexity: TaskComplexity) -> float:
        """Estimate effort for a task component"""
        base_effort = 1.0

        # Adjust based on complexity
        complexity_multipliers = {
            TaskComplexity.SIMPLE: 0.5,
            TaskComplexity.MODERATE: 1.0,
            TaskComplexity.COMPLEX: 2.0,
            TaskComplexity.VERY_COMPLEX: 4.0
        }

        multiplier = complexity_multipliers.get(complexity, 1.0)

        # Adjust based on content
        if len(sentence.split()) > 20:
            multiplier *= 1.5

        return base_effort * multiplier

    def _analyze_dependencies(self, components: List[TaskComponent]) -> List[Tuple[str, str]]:
        """Analyze dependencies between components"""
        dependencies = []

        # Simple dependency analysis based on keywords
        for i, component in enumerate(components):
            for j, other in enumerate(components):
                if i != j:
                    # Check for dependency indicators
                    if any(word in component.description.lower() for word in ["after", "then", "following"]):
                        if other.description.lower() in component.description.lower():
                            dependencies.append((component.id, other.id))
                    elif any(word in other.description.lower() for word in ["before", "first", "initially"]):
                        if component.description.lower() in other.description.lower():
                            dependencies.append((other.id, component.id))

        return dependencies

    def _calculate_confidence(self, analysis: TaskAnalysis) -> float:
        """Calculate overall confidence score"""
        confidence_factors = [
            0.8 if len(analysis.entities) > 0 else 0.6,  # Entity extraction
            0.9 if analysis.intent != TaskIntent.EXECUTE else 0.7,  # Intent classification
            0.8 if len(analysis.key_phrases) > 0 else 0.6,  # Key phrases
            0.7 if analysis.domain_context != "general" else 0.5,  # Domain identification
        ]

        return sum(confidence_factors) / len(confidence_factors)

    async def generate_task_plan(self, analysis: TaskAnalysis, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate a detailed execution plan from task analysis.

        Args:
            analysis: The task analysis result
            context: Additional context information

        Returns:
            Detailed execution plan
        """
        plan = {
            "task_summary": {
                "intent": analysis.intent.value,
                "complexity": analysis.complexity.value,
                "risk_level": analysis.risk_level.value,
                "estimated_total_effort": sum(c.estimated_effort for c in analysis.components),
                "requires_approval": any(c.requires_approval for c in analysis.components)
            },
            "execution_steps": [],
            "dependencies": analysis.dependencies,
            "risk_assessment": {
                "overall_risk": analysis.risk_level.value,
                "risk_factors": self._identify_risk_factors(analysis),
                "mitigation_suggestions": self._suggest_mitigations(analysis)
            },
            "resource_requirements": self._calculate_resource_requirements(analysis),
            "quality_checks": self._generate_quality_checks(analysis)
        }

        # Generate execution steps
        for component in analysis.components:
            step = {
                "id": component.id,
                "description": component.description,
                "action": component.primary_action,
                "agent_type": self._suggest_agent_type(component, analysis),
                "tools_required": component.required_tools,
                "estimated_time": component.estimated_effort,
                "risk_level": component.risk_level.value,
                "requires_approval": component.requires_approval,
                "priority": component.priority
            }
            plan["execution_steps"].append(step)

        return plan

    def _identify_risk_factors(self, analysis: TaskAnalysis) -> List[str]:
        """Identify specific risk factors"""
        factors = []

        if analysis.risk_level == TaskRisk.CRITICAL:
            factors.append("Critical operations that could cause system failure")
        elif analysis.risk_level == TaskRisk.HIGH:
            factors.append("High-impact operations affecting production systems")

        if analysis.complexity == TaskComplexity.VERY_COMPLEX:
            factors.append("Very complex task with multiple interdependent steps")

        if len(analysis.dependencies) > 5:
            factors.append("High number of dependencies increases failure risk")

        return factors

    def _suggest_mitigations(self, analysis: TaskAnalysis) -> List[str]:
        """Suggest risk mitigation strategies"""
        mitigations = []

        if analysis.risk_level in [TaskRisk.HIGH, TaskRisk.CRITICAL]:
            mitigations.append("Require human approval before execution")
            mitigations.append("Create backup/rollback plan")
            mitigations.append("Test in staging environment first")

        if analysis.complexity in [TaskComplexity.COMPLEX, TaskComplexity.VERY_COMPLEX]:
            mitigations.append("Break down into smaller, manageable tasks")
            mitigations.append("Add validation checkpoints between steps")

        if len(analysis.dependencies) > 3:
            mitigations.append("Document all dependencies clearly")
            mitigations.append("Test dependency resolution before execution")

        return mitigations

    def _calculate_resource_requirements(self, analysis: TaskAnalysis) -> Dict[str, Any]:
        """Calculate resource requirements for the task"""
        total_effort = sum(c.estimated_effort for c in analysis.components)
        high_priority_components = sum(1 for c in c.priority > 3)

        return {
            "estimated_person_hours": total_effort,
            "parallel_execution_possible": len(analysis.dependencies) < len(analysis.components) * 0.5,
            "specialized_skills_required": self._identify_required_skills(analysis),
            "tools_needed": list(set(
                tool for component in analysis.components for tool in component.required_tools
            )),
            "high_priority_items": high_priority_components
        }

    def _identify_required_skills(self, analysis: TaskAnalysis) -> List[str]:
        """Identify required skills for the task"""
        skills = []

        if analysis.domain_context == "development":
            skills.extend(["programming", "software development"])
        elif analysis.domain_context == "analysis":
            skills.extend(["data analysis", "statistics"])
        elif analysis.domain_context == "infrastructure":
            skills.extend(["system administration", "devops"])

        if analysis.complexity in [TaskComplexity.COMPLEX, TaskComplexity.VERY_COMPLEX]:
            skills.append("project management")

        return list(set(skills))

    def _generate_quality_checks(self, analysis: TaskAnalysis) -> List[str]:
        """Generate quality assurance checks"""
        checks = [
            "Validate input parameters and constraints",
            "Check for required permissions and access",
            "Verify system state before execution"
        ]

        if analysis.risk_level in [TaskRisk.HIGH, TaskRisk.CRITICAL]:
            checks.extend([
                "Create system backup before execution",
                "Test rollback procedures",
                "Monitor system health during execution"
            ])

        if len(analysis.components) > 3:
            checks.append("Validate intermediate results between steps")

        return checks

    def _suggest_agent_type(self, component: TaskComponent, analysis: TaskAnalysis) -> str:
        """Suggest appropriate agent type for a component"""
        # Map intents to agent types
        intent_agent_map = {
            TaskIntent.CREATE: "code_execution",
            TaskIntent.MODIFY: "code_execution",
            TaskIntent.ANALYZE: "code_execution",
            TaskIntent.DELETE: "code_execution",
            TaskIntent.EXECUTE: "code_execution",
            TaskIntent.SEARCH: "code_execution",
            TaskIntent.COMMUNICATE: "customer_support",
            TaskIntent.MANAGE: "code_execution",
            TaskIntent.DEBUG: "code_execution",
            TaskIntent.DEPLOY: "code_execution",
            TaskIntent.TEST: "code_execution",
            TaskIntent.DOCUMENT: "code_execution"
        }

        return intent_agent_map.get(component.intent, "code_execution")

# Global NLP processor instance
nlp_processor = NLPProcessor()

# Helper functions for easy integration

async def analyze_task_request(text: str, context: Dict[str, Any] = None) -> TaskAnalysis:
    """Helper to analyze a task request"""
    return await nlp_processor.analyze_task(text, context)

async def generate_execution_plan(text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Helper to generate an execution plan from text"""
    analysis = await nlp_processor.analyze_task(text, context)
    return await nlp_processor.generate_task_plan(analysis, context)
