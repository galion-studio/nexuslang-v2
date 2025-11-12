"""
NexusLang v2 - AI-Native Programming Language
"""

__version__ = "2.0.0-beta"
__author__ = "NexusLang Team"

from .lexer.lexer import Lexer
from .parser.parser import Parser
from .interpreter.interpreter import Interpreter
from .compiler.binary import BinaryCompiler, compile_to_binary

# AI-native runtime
from .runtime.personality import PersonalityManager, get_personality
from .runtime.knowledge import knowledge, knowledge_get, knowledge_related
from .runtime.voice import say, listen, clone_voice

__all__ = [
    "Lexer",
    "Parser", 
    "Interpreter",
    "BinaryCompiler",
    "compile_to_binary",
    "PersonalityManager",
    "get_personality",
    "knowledge",
    "knowledge_get",
    "knowledge_related",
    "say",
    "listen",
    "clone_voice"
]
