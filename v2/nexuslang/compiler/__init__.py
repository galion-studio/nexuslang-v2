"""
NexusLang v2 Compiler.
Binary compilation for AI-optimized execution.
"""

from .binary import BinaryCompiler, OpCode, compile_to_binary, decompile_binary

__all__ = [
    'BinaryCompiler',
    'OpCode',
    'compile_to_binary',
    'decompile_binary'
]

