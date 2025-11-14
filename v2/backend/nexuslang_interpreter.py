"""
NexusLang v2 Interpreter
A simple interpreter for the AI-native programming language
"""

import re
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import json

@dataclass
class ExecutionResult:
    """Result of code execution"""
    stdout: str = ""
    stderr: str = ""
    return_code: int = 0
    execution_time: float = 0.0
    success: bool = True
    error: Optional[str] = None
    credits_used: float = 0.01

class NexusLangInterpreter:
    """Simple interpreter for NexusLang v2"""

    def __init__(self):
        self.variables = {}
        self.personality = {
            "empathetic": 0.5,
            "creative": 0.5,
            "analytical": 0.5,
            "helpful": 0.5
        }
        self.output = []

    def execute(self, code: str) -> ExecutionResult:
        """Execute NexusLang code"""
        start_time = time.time()
        self.output = []

        try:
            # Split code into lines
            lines = [line.strip() for line in code.split('\n') if line.strip()]

            for line in lines:
                self._execute_line(line)

            execution_time = time.time() - start_time

            return ExecutionResult(
                stdout='\n'.join(self.output),
                execution_time=execution_time,
                success=True
            )

        except Exception as e:
            execution_time = time.time() - start_time
            return ExecutionResult(
                stderr=f"Error: {str(e)}",
                execution_time=execution_time,
                success=False,
                error=str(e),
                return_code=1
            )

    def _execute_line(self, line: str):
        """Execute a single line of NexusLang code"""
        line = line.strip()

        # Comments
        if line.startswith('#'):
            return

        # Variable assignment (check this first)
        if '=' in line and not line.startswith('if ') and not line.startswith('for '):
            var_name, value = line.split('=', 1)
            var_name = var_name.strip()
            value = value.strip()

            # Handle AI chat assignments
            if 'ai.chat(' in value:
                match = re.search(r'ai\.chat\(["\']([^"\']+)["\']', value)
                if match:
                    prompt = match.group(1)
                    response = self._simulate_ai_response(prompt)
                    self.variables[var_name] = response
                    return

            # Handle knowledge query assignments
            if 'knowledge(' in value:
                match = re.search(r'knowledge\(["\']([^"\']+)["\']', value)
                if match:
                    query = match.group(1)
                    result = self._simulate_knowledge_query(query)
                    self.variables[var_name] = result
                    return

            # Handle string concatenation
            if '+' in value:
                parts = value.split('+')
                result = ""
                for part in parts:
                    part = part.strip()
                    if part.startswith('"') and part.endswith('"'):
                        result += part[1:-1]
                    elif part.startswith("'") and part.endswith("'"):
                        result += part[1:-1]
                    elif part in self.variables:
                        result += str(self.variables[part])
                    else:
                        result += part
                self.variables[var_name] = result
            else:
                # Remove quotes from strings
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                elif value.isdigit():
                    value = int(value)
                elif value.replace('.', '').isdigit():
                    value = float(value)

                self.variables[var_name] = value
            return

        # Print statements
        if line.strip().startswith('print(') and line.strip().endswith(')'):
            content = line.strip()[6:-1].strip()

            # Handle string concatenation and variable lookups in print
            if '+' in content:
                parts = content.split('+')
                result = ""
                for part in parts:
                    part = part.strip()
                    if part.startswith('"') and part.endswith('"'):
                        result += part[1:-1]
                    elif part.startswith("'") and part.endswith("'"):
                        result += part[1:-1]
                    elif part in self.variables:
                        result += str(self.variables[part])
                    else:
                        result += part
                self.output.append(result)
            elif content in self.variables:
                # Print variable value
                self.output.append(str(self.variables[content]))
            else:
                # Remove quotes if present
                if content.startswith('"') and content.endswith('"'):
                    content = content[1:-1]
                elif content.startswith("'") and content.endswith("'"):
                    content = content[1:-1]
                self.output.append(str(content))
            return

        # Personality settings
        if 'personality {' in line:
            # Extract personality traits - handle nested braces
            start_idx = line.find('{')
            end_idx = line.rfind('}')
            if start_idx != -1 and end_idx != -1:
                traits_text = line[start_idx+1:end_idx]
                traits = {}
                for trait in traits_text.split(','):
                    trait = trait.strip()
                    if ':' in trait:
                        key, val = trait.split(':', 1)
                        key = key.strip()
                        val = val.strip()
                        try:
                            traits[key] = float(val)
                        except ValueError:
                            traits[key] = val

                self.personality.update(traits)
                self.output.append(f"Personality updated: {traits}")
            return

        # Direct AI chat calls (not assignments)
        if 'ai.chat(' in line and '=' not in line:
            match = re.search(r'ai\.chat\(["\']([^"\']+)["\']', line)
            if match:
                prompt = match.group(1)
                response = self._simulate_ai_response(prompt)
                self.output.append(f"AI: {response}")
            return

        # Direct knowledge queries (not assignments)
        if 'knowledge(' in line and '=' not in line:
            match = re.search(r'knowledge\(["\']([^"\']+)["\']', line)
            if match:
                query = match.group(1)
                result = self._simulate_knowledge_query(query)
                self.output.append(f"Knowledge: {result}")
            return

        # Function definitions (basic)
        if line.startswith('fn ') or line.startswith('def '):
            self.output.append(f"Function defined: {line}")
            return

        # Function calls
        if '(' in line and ')' in line and not line.startswith('print('):
            func_name = line.split('(')[0].strip()
            if func_name in ['main', 'run']:
                self.output.append("Executing main function...")
            else:
                self.output.append(f"Calling function: {func_name}")
            return

        # Say command (voice output)
        if line.startswith('say('):
            match = re.search(r'say\(["\']([^"\']+)["\'](?:, emotion=["\']([^"\']+)["\'])?', line)
            if match:
                text = match.group(1)
                emotion = match.group(2) if match.group(2) else "neutral"
                self.output.append(f"[VOICE] {text} (emotion: {emotion})")
            return

        # Unknown command
        if line:
            self.output.append(f"Unknown command: {line}")

    def _simulate_ai_response(self, prompt: str) -> str:
        """Simulate AI response based on personality"""
        responses = {
            "hello": "Hello! How can I help you today?",
            "what is ai": "AI stands for Artificial Intelligence, which refers to machines performing tasks that typically require human intelligence.",
            "tell me a joke": "Why did the AI go to school? To improve its learning algorithm!",
            "how are you": "I'm doing well, thank you for asking! I'm here and ready to help."
        }

        # Find matching response
        for key, response in responses.items():
            if key in prompt.lower():
                return response

        # Default response based on personality
        if self.personality.get("creative", 0) > 0.7:
            return f"That's an interesting question about '{prompt}'. Let me think creatively about this..."
        elif self.personality.get("analytical", 0) > 0.7:
            return f"Analyzing '{prompt}'... Based on logical reasoning, here's what I think:"
        else:
            return f"I understand you're asking about '{prompt}'. Here's my response:"

    def _simulate_knowledge_query(self, query: str) -> str:
        """Simulate knowledge base query"""
        knowledge = {
            "quantum": "Quantum physics is the study of matter and energy at the smallest scales, involving quantum mechanics.",
            "python": "Python is a high-level programming language known for its simplicity and readability.",
            "ai": "Artificial Intelligence is the simulation of human intelligence in machines.",
            "machine learning": "Machine Learning is a subset of AI that enables systems to learn from data."
        }

        for key, info in knowledge.items():
            if key in query.lower():
                return info

        return f"I found information about '{query}' in my knowledge base."

# Global interpreter instance
interpreter = NexusLangInterpreter()

def execute_nexuslang(code: str) -> ExecutionResult:
    """Execute NexusLang code"""
    global interpreter
    return interpreter.execute(code)
