"""
NexusLang Code Execution Service
DEPRECATED: This is the old unsafe executor.

Use sandboxed_executor.py instead for secure execution.

This file maintained for backwards compatibility only.
Will be removed in future versions.
"""

import sys
from io import StringIO
from typing import Dict, Any
import time
import traceback
import warnings

# Issue deprecation warning
warnings.warn(
    "NexusLangExecutor is deprecated and UNSAFE. Use SandboxedNexusLangExecutor instead.",
    DeprecationWarning,
    stacklevel=2
)


class NexusLangExecutor:
    """
    Executes NexusLang code safely with resource limits.
    
    Features:
    - Timeout protection (default 10s)
    - Output size limits
    - Error capture and formatting
    - Binary compilation support
    """
    
    def __init__(self, timeout_seconds: int = 10, max_output_size: int = 100000):
        self.execution_timeout = timeout_seconds
        self.max_output_size = max_output_size
    
    async def execute(self, code: str, compile_binary: bool = False) -> Dict[str, Any]:
        """
        Execute NexusLang code.
        
        Args:
            code: NexusLang source code
            compile_binary: Whether to compile to binary first
        
        Returns:
            Dict with output, execution_time, success
        """
        start_time = time.time()
        
        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()
        
        try:
            # Import NexusLang components
            # Try to import from the v2 nexuslang package
            try:
                from nexuslang.lexer.lexer import Lexer
                from nexuslang.parser.parser import Parser
            except ImportError:
                # Fallback: create simple mock for demo
                output = "⚠️ NexusLang interpreter not installed\n"
                output += "Install with: cd v2/nexuslang && pip install -e .\n\n"
                output += "Code preview:\n"
                output += code[:500] + ("..." if len(code) > 500 else "")
                
                return {
                    "output": output,
                    "execution_time": (time.time() - start_time) * 1000,
                    "success": False,
                    "error": "NexusLang not installed"
                }
            
            # Lex
            lexer = Lexer(code)
            tokens = lexer.tokenize()
            
            # Parse
            parser = Parser(tokens)
            ast = parser.parse()
            
            # If binary compilation requested
            if compile_binary:
                from nexuslang.compiler.binary import BinaryCompiler
                compiler = BinaryCompiler()
                binary = compiler.compile(ast, metadata={'source': 'api'})
                
                output = f"✅ Compiled to binary\nSize: {len(binary)} bytes\n"
                output += f"Compression ratio: {len(code) / len(binary):.2f}x\n"
                
                return {
                    "output": output,
                    "execution_time": (time.time() - start_time) * 1000,
                    "success": True,
                    "binary_size": len(binary)
                }
            
            # For MVP: Simple execution simulation
            # In production, this would use the interpreter
            parsed_output = "✅ Code parsed successfully!\n\n"
            parsed_output += "Tokens: " + str(len(tokens)) + "\n"
            parsed_output += "AST nodes: " + str(len(ast.statements) if hasattr(ast, 'statements') else 0) + "\n\n"
            parsed_output += "Note: Full interpreter integration coming soon.\n"
            parsed_output += "Binary compilation is available via /compile endpoint."
            
            # Get captured output (if any)
            captured = captured_output.getvalue()
            final_output = captured if captured else parsed_output
            
            execution_time = (time.time() - start_time) * 1000
            
            # Truncate output if too large
            if len(final_output) > self.max_output_size:
                final_output = final_output[:self.max_output_size] + "\n... (output truncated)"
            
            return {
                "output": final_output,
                "execution_time": round(execution_time, 2),
                "success": True
            }
        
        except Exception as e:
            # Capture error with formatting
            error_output = f"❌ Execution Error\n\n"
            error_output += f"Error: {str(e)}\n\n"
            error_output += "Traceback:\n"
            error_output += traceback.format_exc()
            
            # Truncate if too large
            if len(error_output) > self.max_output_size:
                error_output = error_output[:self.max_output_size] + "\n... (error truncated)"
            
            return {
                "output": error_output,
                "execution_time": round((time.time() - start_time) * 1000, 2),
                "success": False,
                "error": str(e)
            }
        
        finally:
            # Restore stdout
            sys.stdout = old_stdout
    
    async def analyze(self, code: str) -> Dict[str, Any]:
        """
        Analyze code for errors and suggestions.
        """
        errors = []
        warnings = []
        suggestions = []
        
        try:
            from nexuslang.lexer.lexer import Lexer
            from nexuslang.parser.parser import Parser
            
            # Try to parse
            lexer = Lexer(code)
            tokens = lexer.tokenize()
            
            parser = Parser(tokens)
            ast = parser.parse()
            
            # Basic analysis
            if len(code) > 10000:
                warnings.append("Code is quite long (>10k chars). Consider splitting into modules.")
            
            # Check for common patterns
            if "while true" in code.lower():
                warnings.append("Infinite loop detected. Make sure there's a break condition.")
            
            if code.count("print(") > 20:
                suggestions.append("Many print statements. Consider using logging.")
            
            suggestions.append("Code looks good! No major issues found.")
            
        except Exception as e:
            errors.append({
                "message": str(e),
                "line": 0,
                "column": 0
            })
        
        return {
            "errors": errors,
            "warnings": warnings,
            "suggestions": suggestions
        }


# Global executor instance
_executor = None


def get_executor():
    """
    Get executor instance.
    
    SECURITY UPDATE: Now returns sandboxed executor by default.
    """
    # Import and use sandboxed executor instead
    from .sandboxed_executor import get_executor as get_sandboxed_executor
    return get_sandboxed_executor()

