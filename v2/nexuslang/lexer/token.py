"""Token types and definitions for NexusLang"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Any


class TokenType(Enum):
    """All token types in NexusLang"""
    
    # Literals
    INTEGER = auto()
    FLOAT = auto()
    STRING = auto()
    CHAR = auto()
    TRUE = auto()
    FALSE = auto()
    
    # Identifiers and keywords
    IDENTIFIER = auto()
    
    # Keywords
    LET = auto()
    CONST = auto()
    FN = auto()
    RETURN = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    IN = auto()
    MATCH = auto()
    STRUCT = auto()
    ENUM = auto()
    IMPL = auto()
    INTERFACE = auto()
    TRAIT = auto()
    IMPORT = auto()
    FROM = auto()
    EXPORT = auto()
    MODULE = auto()
    ASYNC = auto()
    AWAIT = auto()
    SPAWN = auto()
    BREAK = auto()
    CONTINUE = auto()
    TRY = auto()
    CATCH = auto()
    FINALLY = auto()
    THROW = auto()
    MODEL = auto()
    TRAIN = auto()
    TENSOR = auto()
    DATASET = auto()
    PIPELINE = auto()
    WORKFLOW = auto()
    TASK = auto()
    API = auto()
    ROUTE = auto()
    TEST = auto()
    MUT = auto()
    SELF = auto()
    TYPE = auto()
    
    # NexusLang v2: AI-Native Keywords
    PERSONALITY = auto()
    KNOWLEDGE = auto()
    VOICE = auto()
    SAY = auto()
    LISTEN = auto()
    OPTIMIZE_SELF = auto()
    EMOTION = auto()
    LOAD_MODEL = auto()
    CURIOSITY = auto()
    ANALYTICAL = auto()
    CREATIVE = auto()
    EMPATHETIC = auto()
    CONFIDENCE = auto()
    
    # Operators
    PLUS = auto()           # +
    MINUS = auto()          # -
    STAR = auto()           # *
    SLASH = auto()          # /
    PERCENT = auto()        # %
    POWER = auto()          # **
    
    EQUAL = auto()          # =
    PLUS_EQUAL = auto()     # +=
    MINUS_EQUAL = auto()    # -=
    STAR_EQUAL = auto()     # *=
    SLASH_EQUAL = auto()    # /=
    
    EQ = auto()             # ==
    NE = auto()             # !=
    LT = auto()             # <
    LE = auto()             # <=
    GT = auto()             # >
    GE = auto()             # >=
    
    AND = auto()            # &&
    OR = auto()             # ||
    NOT = auto()            # !
    
    AMPERSAND = auto()      # &
    PIPE = auto()           # |
    CARET = auto()          # ^
    TILDE = auto()          # ~
    LSHIFT = auto()         # <<
    RSHIFT = auto()         # >>
    
    AT = auto()             # @
    ARROW = auto()          # ->
    FAT_ARROW = auto()      # =>
    DOUBLE_COLON = auto()   # ::
    QUESTION = auto()       # ?
    DOT = auto()            # .
    DOUBLE_DOT = auto()     # ..
    TRIPLE_DOT = auto()     # ...
    
    # Delimiters
    LPAREN = auto()         # (
    RPAREN = auto()         # )
    LBRACE = auto()         # {
    RBRACE = auto()         # }
    LBRACKET = auto()       # [
    RBRACKET = auto()       # ]
    COMMA = auto()          # ,
    COLON = auto()          # :
    SEMICOLON = auto()      # ;
    
    # Special
    NEWLINE = auto()
    EOF = auto()
    COMMENT = auto()


# Keywords mapping
KEYWORDS = {
    "let": TokenType.LET,
    "const": TokenType.CONST,
    "fn": TokenType.FN,
    "return": TokenType.RETURN,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "for": TokenType.FOR,
    "in": TokenType.IN,
    "match": TokenType.MATCH,
    "struct": TokenType.STRUCT,
    "enum": TokenType.ENUM,
    "impl": TokenType.IMPL,
    "interface": TokenType.INTERFACE,
    "trait": TokenType.TRAIT,
    "import": TokenType.IMPORT,
    "from": TokenType.FROM,
    "export": TokenType.EXPORT,
    "module": TokenType.MODULE,
    "async": TokenType.ASYNC,
    "await": TokenType.AWAIT,
    "spawn": TokenType.SPAWN,
    "break": TokenType.BREAK,
    "continue": TokenType.CONTINUE,
    "try": TokenType.TRY,
    "catch": TokenType.CATCH,
    "finally": TokenType.FINALLY,
    "throw": TokenType.THROW,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    # AI-related keywords removed - they're functions, not keywords
    # "model": TokenType.MODEL,
    # "train": TokenType.TRAIN,
    # "tensor": TokenType.TENSOR,
    # "dataset": TokenType.DATASET,
    # Following keywords kept for future language features
    # "pipeline": TokenType.PIPELINE,
    # "workflow": TokenType.WORKFLOW,
    # "task": TokenType.TASK,
    # "api": TokenType.API,
    # "route": TokenType.ROUTE,
    # "test": TokenType.TEST,
    "mut": TokenType.MUT,
    "self": TokenType.SELF,
    "type": TokenType.TYPE,
    # NexusLang v2: AI-Native Keywords
    "personality": TokenType.PERSONALITY,
    "knowledge": TokenType.KNOWLEDGE,
    "voice": TokenType.VOICE,
    "say": TokenType.SAY,
    "listen": TokenType.LISTEN,
    "optimize_self": TokenType.OPTIMIZE_SELF,
    "emotion": TokenType.EMOTION,
    "load_model": TokenType.LOAD_MODEL,
    "curiosity": TokenType.CURIOSITY,
    "analytical": TokenType.ANALYTICAL,
    "creative": TokenType.CREATIVE,
    "empathetic": TokenType.EMPATHETIC,
    "confidence": TokenType.CONFIDENCE,
}


@dataclass
class Token:
    """Represents a single token in the source code"""
    
    type: TokenType
    value: Any
    line: int
    column: int
    
    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.value!r}, {self.line}:{self.column})"
    
    def __str__(self) -> str:
        if self.value is None:
            return f"{self.type.name}"
        return f"{self.type.name}({self.value})"

