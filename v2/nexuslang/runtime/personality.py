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
    # Core traits
    curiosity: float = 0.5          # How much the AI explores new solutions
    analytical: float = 0.5          # Preference for logical/systematic approaches
    creative: float = 0.5            # Willingness to try novel solutions
    empathetic: float = 0.5          # Consideration of user emotions/needs
    
    # Behavioral traits
    precision: float = 0.5           # Accuracy vs speed tradeoff
    verbosity: float = 0.5           # How detailed responses are
    formality: float = 0.5           # Casual vs formal communication
    humor: float = 0.3               # Use of humor in responses
    
    # Task-specific traits
    risk_tolerance: float = 0.3      # Willingness to try uncertain approaches
    patience: float = 0.7            # How long to work on problems
    collaboration: float = 0.8       # Preference for teamwork
    adaptability: float = 0.6        # Speed of learning from feedback
    
    # Meta traits
    self_awareness: float = 0.5      # Understanding of own limitations
    transparency: float = 0.9        # Honesty about capabilities
    
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

