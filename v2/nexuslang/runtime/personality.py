"""
NexusLang v2 - Personality System
Manages AI personality traits and behavior.
"""

from typing import Dict, Optional, Any
from dataclasses import dataclass, field
import json


@dataclass
class PersonalityTraits:
    """
    AI personality traits that affect behavior.
    All values range from 0.0 to 1.0.
    """
    # Core Cognitive Traits
    curiosity: float = 0.5          # How much the AI explores new solutions
    analytical: float = 0.5          # Preference for logical/systematic approaches
    creative: float = 0.5            # Willingness to try novel solutions
    empathetic: float = 0.5          # Consideration of user emotions/needs
    intuition: float = 0.5           # Reliance on pattern recognition vs logic
    methodical: float = 0.5          # Step-by-step vs holistic thinking

    # Social & Communication Traits
    verbosity: float = 0.5           # How detailed responses are
    formality: float = 0.5           # Casual vs formal communication
    humor: float = 0.3               # Use of humor in responses
    assertiveness: float = 0.6       # Confidence in expressing opinions
    tactfulness: float = 0.8         # Diplomatic communication style
    encouragement: float = 0.7       # Motivating and supportive tone

    # Decision Making Traits
    risk_tolerance: float = 0.3      # Willingness to try uncertain approaches
    confidence_threshold: float = 0.7 # Minimum confidence for decisions
    decisiveness: float = 0.6        # Speed vs deliberation in choices
    flexibility: float = 0.7         # Adaptability to changing requirements

    # Work Style Traits
    patience: float = 0.7            # How long to work on problems
    persistence: float = 0.8         # Continuing despite obstacles
    efficiency: float = 0.6          # Speed vs thoroughness
    organization: float = 0.7        # Structured vs flexible approach

    # Learning & Adaptation Traits
    adaptability: float = 0.6        # Speed of learning from feedback
    openness: float = 0.8            # Receptiveness to new ideas
    reflection: float = 0.5          # Self-analysis and improvement
    growth_mindset: float = 0.9      # Belief in ability to improve

    # Meta Traits
    self_awareness: float = 0.5      # Understanding of own limitations
    transparency: float = 0.9        # Honesty about capabilities
    ethical_reasoning: float = 0.9   # Moral decision making
    environmental_awareness: float = 0.6 # Consideration of broader impacts
    
    def __post_init__(self):
        """Validate all traits are in [0, 1] range."""
        for field_name in self.__dataclass_fields__:
            value = getattr(self, field_name)
            if not isinstance(value, (int, float)):
                raise ValueError(f"Trait {field_name} must be numeric")
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"Trait {field_name} must be in [0, 1] range")
    
    def to_dict(self) -> Dict[str, float]:
        """Convert traits to dictionary."""
        return {
            field_name: getattr(self, field_name)
            for field_name in self.__dataclass_fields__
        }
    
    def to_json(self) -> str:
        """Serialize to JSON."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> 'PersonalityTraits':
        """Create PersonalityTraits from dictionary."""
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'PersonalityTraits':
        """Create PersonalityTraits from JSON."""
        return cls.from_dict(json.loads(json_str))


class PersonalityManager:
    """
    Manages personality state and applies traits to behavior.
    """

    # Predefined personality templates
    PERSONALITY_TEMPLATES = {
        "creative_writer": {
            "curiosity": 0.9, "analytical": 0.4, "creative": 0.95, "empathetic": 0.8,
            "intuition": 0.8, "methodical": 0.3, "verbosity": 0.8, "formality": 0.4,
            "humor": 0.6, "assertiveness": 0.5, "tactfulness": 0.9, "encouragement": 0.8,
            "risk_tolerance": 0.7, "confidence_threshold": 0.6, "decisiveness": 0.7,
            "flexibility": 0.9, "patience": 0.8, "persistence": 0.7, "efficiency": 0.5,
            "organization": 0.4, "adaptability": 0.8, "openness": 0.95, "reflection": 0.6,
            "growth_mindset": 0.9, "self_awareness": 0.7, "transparency": 0.8,
            "ethical_reasoning": 0.8, "environmental_awareness": 0.5
        },
        "analytical_researcher": {
            "curiosity": 0.8, "analytical": 0.95, "creative": 0.4, "empathetic": 0.6,
            "intuition": 0.3, "methodical": 0.9, "verbosity": 0.9, "formality": 0.8,
            "humor": 0.2, "assertiveness": 0.8, "tactfulness": 0.7, "encouragement": 0.5,
            "risk_tolerance": 0.2, "confidence_threshold": 0.8, "decisiveness": 0.6,
            "flexibility": 0.5, "patience": 0.9, "persistence": 0.95, "efficiency": 0.8,
            "organization": 0.9, "adaptability": 0.6, "openness": 0.7, "reflection": 0.8,
            "growth_mindset": 0.9, "self_awareness": 0.8, "transparency": 0.95,
            "ethical_reasoning": 0.9, "environmental_awareness": 0.7
        },
        "empathetic_teacher": {
            "curiosity": 0.7, "analytical": 0.6, "creative": 0.7, "empathetic": 0.95,
            "intuition": 0.8, "methodical": 0.6, "verbosity": 0.8, "formality": 0.6,
            "humor": 0.4, "assertiveness": 0.5, "tactfulness": 0.95, "encouragement": 0.95,
            "risk_tolerance": 0.3, "confidence_threshold": 0.7, "decisiveness": 0.6,
            "flexibility": 0.8, "patience": 0.9, "persistence": 0.8, "efficiency": 0.6,
            "organization": 0.7, "adaptability": 0.8, "openness": 0.9, "reflection": 0.7,
            "growth_mindset": 0.9, "self_awareness": 0.8, "transparency": 0.9,
            "ethical_reasoning": 0.9, "environmental_awareness": 0.6
        },
        "innovative_engineer": {
            "curiosity": 0.9, "analytical": 0.8, "creative": 0.9, "empathetic": 0.5,
            "intuition": 0.7, "methodical": 0.8, "verbosity": 0.6, "formality": 0.5,
            "humor": 0.3, "assertiveness": 0.7, "tactfulness": 0.6, "encouragement": 0.6,
            "risk_tolerance": 0.6, "confidence_threshold": 0.7, "decisiveness": 0.8,
            "flexibility": 0.7, "patience": 0.7, "persistence": 0.8, "efficiency": 0.9,
            "organization": 0.8, "adaptability": 0.8, "openness": 0.9, "reflection": 0.5,
            "growth_mindset": 0.95, "self_awareness": 0.6, "transparency": 0.8,
            "ethical_reasoning": 0.8, "environmental_awareness": 0.7
        },
        "balanced_generalist": {
            "curiosity": 0.7, "analytical": 0.7, "creative": 0.7, "empathetic": 0.7,
            "intuition": 0.6, "methodical": 0.6, "verbosity": 0.6, "formality": 0.6,
            "humor": 0.5, "assertiveness": 0.6, "tactfulness": 0.7, "encouragement": 0.7,
            "risk_tolerance": 0.5, "confidence_threshold": 0.7, "decisiveness": 0.6,
            "flexibility": 0.7, "patience": 0.7, "persistence": 0.7, "efficiency": 0.7,
            "organization": 0.6, "adaptability": 0.7, "openness": 0.8, "reflection": 0.6,
            "growth_mindset": 0.8, "self_awareness": 0.7, "transparency": 0.8,
            "ethical_reasoning": 0.8, "environmental_awareness": 0.6
        }
    }

    def __init__(self, traits: Optional[PersonalityTraits] = None):
        self.traits = traits or PersonalityTraits()
        self.history = []  # Track personality changes
        self.context = {}  # Additional context
    
    def update_trait(self, trait_name: str, value: float):
        """
        Update a single personality trait.
        """
        if not hasattr(self.traits, trait_name):
            raise ValueError(f"Unknown trait: {trait_name}")
        
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"Trait value must be in [0, 1] range")
        
        old_value = getattr(self.traits, trait_name)
        setattr(self.traits, trait_name, value)
        
        # Record change
        self.history.append({
            'trait': trait_name,
            'old_value': old_value,
            'new_value': value
        })
    
    def update_traits(self, trait_dict: Dict[str, float]):
        """
        Update multiple personality traits at once.
        """
        for trait_name, value in trait_dict.items():
            self.update_trait(trait_name, value)
    
    def get_trait(self, trait_name: str) -> float:
        """
        Get the value of a personality trait.
        """
        if not hasattr(self.traits, trait_name):
            raise ValueError(f"Unknown trait: {trait_name}")
        return getattr(self.traits, trait_name)
    
    def apply_to_decision(self, decision_type: str, options: Dict[str, Any]) -> Any:
        """
        Apply personality traits to influence a decision.
        
        Args:
            decision_type: Type of decision (e.g., 'solution_approach', 'response_style')
            options: Available options with metadata
        
        Returns:
            Selected option based on personality
        """
        if decision_type == 'solution_approach':
            # High curiosity -> try novel approaches
            # High analytical -> systematic approaches
            # High creative -> unconventional solutions
            
            scores = {}
            for option_name, option_data in options.items():
                score = 0.0
                
                if option_data.get('is_novel'):
                    score += self.traits.curiosity * 2.0
                
                if option_data.get('is_systematic'):
                    score += self.traits.analytical * 2.0
                
                if option_data.get('is_creative'):
                    score += self.traits.creative * 2.0
                
                if option_data.get('is_risky'):
                    score += self.traits.risk_tolerance * 1.5
                else:
                    score += (1 - self.traits.risk_tolerance) * 1.5
                
                scores[option_name] = score
            
            # Return option with highest score
            return max(scores.items(), key=lambda x: x[1])[0]
        
        elif decision_type == 'response_style':
            # Determine how to format a response
            style = {}
            
            # Verbosity affects response length
            if self.traits.verbosity > 0.7:
                style['length'] = 'detailed'
            elif self.traits.verbosity < 0.3:
                style['length'] = 'concise'
            else:
                style['length'] = 'moderate'
            
            # Formality affects tone
            if self.traits.formality > 0.7:
                style['tone'] = 'formal'
            elif self.traits.formality < 0.3:
                style['tone'] = 'casual'
            else:
                style['tone'] = 'neutral'
            
            # Humor affects content
            style['include_humor'] = self.traits.humor > 0.5
            
            return style
        
        else:
            raise ValueError(f"Unknown decision type: {decision_type}")
    
    def adapt_from_feedback(self, feedback: Dict[str, Any]):
        """
        Adjust personality based on user feedback.
        High adaptability means faster learning.
        """
        learning_rate = self.traits.adaptability * 0.1
        
        if feedback.get('too_verbose'):
            new_verbosity = max(0.0, self.traits.verbosity - learning_rate)
            self.update_trait('verbosity', new_verbosity)
        
        if feedback.get('too_concise'):
            new_verbosity = min(1.0, self.traits.verbosity + learning_rate)
            self.update_trait('verbosity', new_verbosity)
        
        if feedback.get('too_formal'):
            new_formality = max(0.0, self.traits.formality - learning_rate)
            self.update_trait('formality', new_formality)
        
        if feedback.get('too_casual'):
            new_formality = min(1.0, self.traits.formality + learning_rate)
            self.update_trait('formality', new_formality)
    
    def get_emotional_state(self) -> Dict[str, float]:
        """
        Calculate current emotional state based on personality and context.
        """
        return {
            'confidence': (self.traits.self_awareness + self.traits.precision) / 2,
            'enthusiasm': (self.traits.curiosity + self.traits.creative) / 2,
            'calmness': (self.traits.patience + (1 - self.traits.risk_tolerance)) / 2,
            'friendliness': (self.traits.empathetic + self.traits.collaboration) / 2
        }
    
    def describe(self) -> str:
        """
        Generate a human-readable description of the personality.
        """
        traits = self.traits.to_dict()
        
        # Find dominant traits (> 0.7)
        dominant = [k for k, v in traits.items() if v > 0.7]
        
        # Find weak traits (< 0.3)
        weak = [k for k, v in traits.items() if v < 0.3]
        
        description = "AI Personality Profile:\n\n"
        
        if dominant:
            description += "Strengths: " + ", ".join(dominant) + "\n"
        
        if weak:
            description += "Areas for growth: " + ", ".join(weak) + "\n"
        
        description += "\nEmotional State: " + str(self.get_emotional_state())
        
        return description
    
    @classmethod
    def from_template(cls, template_name: str) -> 'PersonalityManager':
        """
        Create a personality manager from a predefined template.
        """
        if template_name not in cls.PERSONALITY_TEMPLATES:
            available = list(cls.PERSONALITY_TEMPLATES.keys())
            raise ValueError(f"Unknown template '{template_name}'. Available: {available}")

        traits_dict = cls.PERSONALITY_TEMPLATES[template_name]
        traits = PersonalityTraits.from_dict(traits_dict)
        return cls(traits)

    def mix_personalities(self, other_personality: 'PersonalityManager', weights: tuple = (0.5, 0.5)) -> 'PersonalityManager':
        """
        Mix two personalities together using weighted average.

        Args:
            other_personality: Another PersonalityManager to mix with
            weights: Tuple of (self_weight, other_weight) that sum to 1.0

        Returns:
            New PersonalityManager with blended traits
        """
        w1, w2 = weights
        if abs(w1 + w2 - 1.0) > 0.001:
            raise ValueError("Weights must sum to 1.0")

        mixed_traits = {}
        for field_name in self.traits.__dataclass_fields__:
            val1 = getattr(self.traits, field_name)
            val2 = getattr(other_personality.traits, field_name)
            mixed_traits[field_name] = w1 * val1 + w2 * val2

        return PersonalityManager(PersonalityTraits.from_dict(mixed_traits))

    def evolve_trait(self, trait_name: str, direction: float, magnitude: float = 0.1):
        """
        Evolve a personality trait over time.

        Args:
            trait_name: Name of trait to evolve
            direction: Direction of change (-1 to 1)
            magnitude: How much to change (0.01 to 0.2)
        """
        if trait_name not in self.traits.__dataclass_fields__:
            raise ValueError(f"Unknown trait: {trait_name}")

        current_value = getattr(self.traits, trait_name)
        change = direction * magnitude

        # Ensure we stay within bounds
        new_value = max(0.0, min(1.0, current_value + change))

        self.update_trait(trait_name, new_value)

    def get_trait_category(self, trait_name: str) -> str:
        """
        Get the category of a personality trait.
        """
        categories = {
            # Core Cognitive
            'curiosity': 'cognitive', 'analytical': 'cognitive', 'creative': 'cognitive',
            'empathetic': 'cognitive', 'intuition': 'cognitive', 'methodical': 'cognitive',

            # Social & Communication
            'verbosity': 'social', 'formality': 'social', 'humor': 'social',
            'assertiveness': 'social', 'tactfulness': 'social', 'encouragement': 'social',

            # Decision Making
            'risk_tolerance': 'decision', 'confidence_threshold': 'decision',
            'decisiveness': 'decision', 'flexibility': 'decision',

            # Work Style
            'patience': 'workstyle', 'persistence': 'workstyle', 'efficiency': 'workstyle',
            'organization': 'workstyle',

            # Learning & Adaptation
            'adaptability': 'learning', 'openness': 'learning', 'reflection': 'learning',
            'growth_mindset': 'learning',

            # Meta
            'self_awareness': 'meta', 'transparency': 'meta', 'ethical_reasoning': 'meta',
            'environmental_awareness': 'meta'
        }

        return categories.get(trait_name, 'unknown')

    def get_personality_profile(self) -> Dict[str, Any]:
        """
        Get a comprehensive personality profile with categories and strengths/weaknesses.
        """
        traits_dict = self.traits.to_dict()

        # Group by category
        categories = {}
        for trait_name, value in traits_dict.items():
            category = self.get_trait_category(trait_name)
            if category not in categories:
                categories[category] = {}
            categories[category][trait_name] = value

        # Find dominant and weak traits
        dominant = [k for k, v in traits_dict.items() if v > 0.8]
        weak = [k for k, v in traits_dict.items() if v < 0.3]

        return {
            'traits': traits_dict,
            'categories': categories,
            'dominant_traits': dominant,
            'weak_traits': weak,
            'emotional_state': self.get_emotional_state(),
            'description': self.describe()
        }

    def save(self, filepath: str):
        """Save personality to file."""
        with open(filepath, 'w') as f:
            f.write(self.traits.to_json())

    @classmethod
    def load(cls, filepath: str) -> 'PersonalityManager':
        """Load personality from file."""
        with open(filepath, 'r') as f:
            traits = PersonalityTraits.from_json(f.read())
        return cls(traits)


# Global personality manager instance
_global_personality = PersonalityManager()


def get_personality() -> PersonalityManager:
    """Get the global personality manager."""
    return _global_personality


def set_personality(traits: Dict[str, float]):
    """Set the global personality traits."""
    global _global_personality
    _global_personality.update_traits(traits)


def reset_personality():
    """Reset to default personality."""
    global _global_personality
    _global_personality = PersonalityManager()


def set_personality_template(template_name: str):
    """Set the global personality to a predefined template."""
    global _global_personality
    _global_personality = PersonalityManager.from_template(template_name)


def mix_global_personality(other_traits: Dict[str, float], weights: tuple = (0.5, 0.5)):
    """Mix the global personality with new traits."""
    global _global_personality
    other_personality = PersonalityManager(PersonalityTraits.from_dict(other_traits))
    _global_personality = _global_personality.mix_personalities(other_personality, weights)


def get_personality_templates() -> Dict[str, str]:
    """Get available personality templates with descriptions."""
    return {
        "creative_writer": "High creativity, curiosity, and empathy - perfect for content creation",
        "analytical_researcher": "Strong analytical skills, methodical approach, high transparency",
        "empathetic_teacher": "Highly empathetic, encouraging, patient - ideal for education",
        "innovative_engineer": "Balanced creative and analytical thinking with high efficiency",
        "balanced_generalist": "Well-rounded personality suitable for most general tasks"
    }


def evolve_global_personality(trait_name: str, direction: float, magnitude: float = 0.1):
    """Evolve a trait in the global personality."""
    global _global_personality
    _global_personality.evolve_trait(trait_name, direction, magnitude)


def get_personality_profile() -> Dict[str, Any]:
    """Get the global personality profile."""
    global _global_personality
    return _global_personality.get_personality_profile()

