"""
NexusLang v2 - AI-Native AST Nodes
New node types for personality, knowledge, and voice features
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from .nodes import ASTNode


@dataclass
class PersonalityBlock(ASTNode):
    """
    Personality block defining AI traits and behavior.
    
    Example:
        personality {
            curiosity: 0.9,
            analytical: 0.8,
            creative: 0.7
        }
    """
    traits: Dict[str, float]
    
    def __repr__(self) -> str:
        traits_str = ", ".join(f"{k}: {v}" for k, v in self.traits.items())
        return f"PersonalityBlock({traits_str})"


@dataclass
class KnowledgeQuery(ASTNode):
    """
    Knowledge query accessing Grokopedia.
    
    Example:
        let facts = knowledge("quantum physics")
    """
    query: str
    filters: Optional[Dict[str, Any]] = None
    
    def __repr__(self) -> str:
        return f"KnowledgeQuery({self.query!r})"


@dataclass
class VoiceBlock(ASTNode):
    """
    Voice block for speech synthesis and recognition.
    
    Example:
        voice {
            say("Hello", emotion="friendly")
            let response = listen()
        }
    """
    body: List[ASTNode]
    config: Optional[Dict[str, Any]] = None
    
    def __repr__(self) -> str:
        return f"VoiceBlock({len(self.body)} statements)"


@dataclass
class SayStatement(ASTNode):
    """
    Text-to-speech statement.
    
    Example:
        say("Hello world", emotion="excited", voice_id="galion-1")
    """
    text: str
    emotion: Optional[str] = None
    voice_id: Optional[str] = None
    speed: float = 1.0
    
    def __repr__(self) -> str:
        return f"SayStatement({self.text!r}, emotion={self.emotion})"


@dataclass
class ListenExpression(ASTNode):
    """
    Speech-to-text expression.
    
    Example:
        let user_input = listen()
        let response = listen(timeout=10, language="en")
    """
    timeout: Optional[int] = None
    language: str = "en"
    
    def __repr__(self) -> str:
        return f"ListenExpression(timeout={self.timeout}, lang={self.language})"


@dataclass
class OptimizeSelfStatement(ASTNode):
    """
    Self-improvement directive for AI.
    
    Example:
        optimize_self(metric="accuracy", target=0.95)
    """
    metric: str
    target: Optional[float] = None
    strategy: Optional[str] = None
    
    def __repr__(self) -> str:
        return f"OptimizeSelfStatement(metric={self.metric}, target={self.target})"


@dataclass
class LoadModelExpression(ASTNode):
    """
    Load a pre-trained model.
    
    Example:
        let model = load_model("gpt-4")
        let custom = load_model("./models/my_model.nxb")
    """
    model_name: str
    config: Optional[Dict[str, Any]] = None
    
    def __repr__(self) -> str:
        return f"LoadModelExpression({self.model_name!r})"


@dataclass
class EmotionExpression(ASTNode):
    """
    Express or detect emotion.
    
    Example:
        let current_emotion = emotion()
        emotion("happy", intensity=0.8)
    """
    emotion_type: Optional[str] = None
    intensity: float = 1.0
    
    def __repr__(self) -> str:
        return f"EmotionExpression({self.emotion_type}, intensity={self.intensity})"


@dataclass
class ConfidenceExpression(ASTNode):
    """
    Get or set confidence level for AI decisions.
    
    Example:
        let conf = confidence(prediction)
        if confidence(result) < 0.8 {
            // handle low confidence
        }
    """
    value: Optional[ASTNode] = None
    threshold: Optional[float] = None
    
    def __repr__(self) -> str:
        return f"ConfidenceExpression(value={self.value})"


@dataclass
class BinaryCompilationUnit(ASTNode):
    """
    Represents a compiled binary .nxb file.
    Contains optimized bytecode and metadata.
    """
    version: str
    bytecode: bytes
    metadata: Dict[str, Any]
    symbol_table: Dict[str, int]
    
    def __repr__(self) -> str:
        return f"BinaryCompilationUnit(version={self.version}, size={len(self.bytecode)})"


# Additional utility functions for AI-native features

def create_personality(traits: Dict[str, float]) -> PersonalityBlock:
    """
    Helper to create a personality block with validation.
    Ensures all trait values are between 0.0 and 1.0.
    """
    validated_traits = {}
    for key, value in traits.items():
        if not isinstance(value, (int, float)):
            raise ValueError(f"Personality trait '{key}' must be numeric")
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"Personality trait '{key}' must be between 0 and 1")
        validated_traits[key] = float(value)
    
    return PersonalityBlock(traits=validated_traits)


def create_knowledge_query(query: str, **filters) -> KnowledgeQuery:
    """
    Helper to create a knowledge query with optional filters.
    """
    return KnowledgeQuery(query=query, filters=filters if filters else None)


def create_voice_say(text: str, **kwargs) -> SayStatement:
    """
    Helper to create a say statement with optional parameters.
    """
    return SayStatement(
        text=text,
        emotion=kwargs.get('emotion'),
        voice_id=kwargs.get('voice_id'),
        speed=kwargs.get('speed', 1.0)
    )

