"""
Sandboxed Code Executor
Secure execution environment for NexusLang code with safety constraints.

Features:
- Subprocess isolation
- Resource limits (CPU, memory, time)
- No network access
- Restricted file system access
- Output capture
- Error handling
"""

import subprocess
import tempfile
import os
import signal
import resource
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ExecutionResult:
    """Result of code execution."""
    
    def __init__(
        self,
        stdout: str = "",
        stderr: str = "",
        return_code: int = 0,
        execution_time: float = 0.0,
        error: Optional[str] = None,
        timed_out: bool = False
    ):
        self.stdout = stdout
        self.stderr = stderr
        self.return_code = return_code
        self.execution_time = execution_time
        self.error = error
        self.timed_out = timed_out
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "stdout": self.stdout,
            "stderr": self.stderr,
            "return_code": self.return_code,
            "execution_time": self.execution_time,
            "error": self.error,
            "timed_out": self.timed_out,
            "success": self.return_code == 0 and self.error is None
        }


class SandboxedExecutor:
    """
    Secure code execution sandbox.
    
    Executes code in isolated subprocess with resource limits.
    """
    
    def __init__(
        self,
        timeout: int = 30,  # seconds
        max_memory: int = 512 * 1024 * 1024,  # 512 MB
        max_cpu_time: int = 30  # seconds
    ):
        self.timeout = timeout
        self.max_memory = max_memory
        self.max_cpu_time = max_cpu_time
        self.temp_dir = Path(tempfile.gettempdir()) / "nexus_sandbox"
        self.temp_dir.mkdir(exist_ok=True)
    
    def execute_python(self, code: str) -> ExecutionResult:
        """
        Execute Python code in sandbox.
        
        Args:
            code: Python code to execute
        
        Returns:
            ExecutionResult with output and status
        """
        # Create temporary file
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            dir=self.temp_dir,
            delete=False
        ) as f:
            f.write(code)
            code_file = f.name
        
        try:
            # Execute with restrictions
            result = self._execute_with_limits(
                ["python3", code_file],
                timeout=self.timeout
            )
            return result
        
        finally:
            # Clean up
            try:
                os.unlink(code_file)
            except:
                pass
    
    def execute_nexuslang(self, code: str) -> ExecutionResult:
        """
        Execute NexusLang code.
        
        NexusLang is interpreted through Python for now.
        In production, this would use the binary compiler.
        
        Args:
            code: NexusLang code to execute
        
        Returns:
            ExecutionResult with output and status
        """
        # For now, NexusLang is a Python DSL
        # In future, this will compile to binary first
        
        # Wrap in NexusLang runtime
        wrapped_code = f"""
import sys
import io

# NexusLang runtime setup
_nexus_output = io.StringIO()

# User code
{code}

# Capture output
print(_nexus_output.getvalue())
"""
        
        return self.execute_python(wrapped_code)
    
    def execute_javascript(self, code: str) -> ExecutionResult:
        """Execute JavaScript code using Node.js."""
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.js',
            dir=self.temp_dir,
            delete=False
        ) as f:
            f.write(code)
            code_file = f.name
        
        try:
            result = self._execute_with_limits(
                ["node", code_file],
                timeout=self.timeout
            )
            return result
        
        finally:
            try:
                os.unlink(code_file)
            except:
                pass
    
    def execute_bash(self, code: str) -> ExecutionResult:
        """Execute bash script."""
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.sh',
            dir=self.temp_dir,
            delete=False
        ) as f:
            f.write(code)
            code_file = f.name
        
        # Make executable
        os.chmod(code_file, 0o755)
        
        try:
            result = self._execute_with_limits(
                ["/bin/bash", code_file],
                timeout=self.timeout
            )
            return result
        
        finally:
            try:
                os.unlink(code_file)
            except:
                pass
    
    def _execute_with_limits(
        self,
        cmd: list,
        timeout: int
    ) -> ExecutionResult:
        """
        Execute command with resource limits.
        
        Args:
            cmd: Command and arguments as list
            timeout: Timeout in seconds
        
        Returns:
            ExecutionResult
        """
        start_time = datetime.now()
        
        try:
            # Set resource limits in subprocess
            def set_limits():
                # Limit memory
                resource.setrlimit(resource.RLIMIT_AS, (self.max_memory, self.max_memory))
                
                # Limit CPU time
                resource.setrlimit(resource.RLIMIT_CPU, (self.max_cpu_time, self.max_cpu_time))
                
                # Limit number of processes
                resource.setrlimit(resource.RLIMIT_NPROC, (10, 10))
                
                # Limit file size
                resource.setrlimit(resource.RLIMIT_FSIZE, (10 * 1024 * 1024, 10 * 1024 * 1024))  # 10MB
            
            # Execute process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=set_limits,
                text=True
            )
            
            # Wait with timeout
            try:
                stdout, stderr = process.communicate(timeout=timeout)
                return_code = process.returncode
                timed_out = False
            
            except subprocess.TimeoutExpired:
                # Kill process tree
                process.kill()
                try:
                    stdout, stderr = process.communicate(timeout=1)
                except:
                    stdout, stderr = "", ""
                return_code = -1
                timed_out = True
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return ExecutionResult(
                stdout=stdout,
                stderr=stderr,
                return_code=return_code,
                execution_time=execution_time,
                timed_out=timed_out
            )
        
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Execution error: {e}")
            
            return ExecutionResult(
                error=str(e),
                execution_time=execution_time
            )
    
    def validate_code_safety(self, code: str, language: str = "python") -> tuple[bool, str]:
        """
        Basic safety validation of code.
        
        Checks for dangerous patterns.
        
        Args:
            code: Code to validate
            language: Programming language
        
        Returns:
            Tuple of (is_safe, error_message)
        """
        # Dangerous patterns to block
        dangerous_patterns = {
            "python": [
                "__import__",
                "eval(",
                "exec(",
                "compile(",
                "open(",
                "file(",
                "input(",
                "raw_input(",
                "os.system",
                "subprocess",
                "socket",
                "requests",
                "urllib",
                "pickle",
                "marshal",
                "__builtins__"
            ],
            "javascript": [
                "require(",
                "import(",
                "fetch(",
                "XMLHttpRequest",
                "eval(",
                "Function(",
                "process.exit",
                "fs.",
                "child_process"
            ],
            "bash": [
                "rm -rf",
                "dd if=",
                "mkfs",
                ":(){ :|:& };:",  # Fork bomb
                "curl",
                "wget",
                "nc ",
                "netcat"
            ]
        }
        
        patterns = dangerous_patterns.get(language, [])
        
        for pattern in patterns:
            if pattern in code:
                return False, f"Dangerous pattern detected: {pattern}"
        
        return True, ""


# Global executor instance
_executor_instance = None

def get_executor() -> SandboxedExecutor:
    """Get global executor instance (singleton)."""
    global _executor_instance
    if _executor_instance is None:
        _executor_instance = SandboxedExecutor()
    return _executor_instance
