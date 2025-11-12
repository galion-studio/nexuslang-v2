"""
AI Code Assistant for IDE
Provides AI-powered code completion, analysis, and assistance using AI Router.
"""

from typing import List, Dict, Optional, Any
from ..ai import get_ai_router, AIModel


class IDEAIAssistant:
    """
    AI-powered code assistant for the IDE.
    
    Features:
    - Code completion and suggestions
    - Code explanation and documentation
    - Bug detection and fixing
    - Code refactoring suggestions
    - Natural language to code conversion
    """
    
    def __init__(self):
        """Initialize AI assistant with AI router."""
        self.ai_router = get_ai_router()
    
    
    async def complete_code(
        self,
        code: str,
        cursor_position: int,
        language: str = "nexuslang",
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate code completion suggestions.
        
        Args:
            code: Current code content
            cursor_position: Position of cursor in code
            language: Programming language
            context: Additional context about the project
        
        Returns:
            Completion suggestions with confidence scores
        """
        # Split code at cursor position
        before_cursor = code[:cursor_position]
        after_cursor = code[cursor_position:]
        
        prompt = f"""Complete this {language} code at the cursor position:

Code before cursor:
```{language}
{before_cursor}
```

Code after cursor:
```{language}
{after_cursor}
```

Provide 3 likely completions, ranked by relevance.
Format as JSON: {{"completions": [{{"text": "...", "confidence": 0.9}}]}}"""
        
        if context:
            prompt += f"\n\nProject context: {context}"
        
        try:
            # Use CodeLlama for best code completion
            result = await self.ai_router.chat_completion(
                messages=[
                    {"role": "system", "content": f"You are an expert {language} code completion assistant."},
                    {"role": "user", "content": prompt}
                ],
                model=AIModel.CODELLAMA_70B,
                temperature=0.3,  # Lower for more consistent completions
                max_tokens=500
            )
            
            return {
                "success": True,
                "completions": result["content"],
                "model": result["model"]
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    
    async def explain_code(
        self,
        code: str,
        language: str = "nexuslang",
        detail_level: str = "medium"
    ) -> Dict[str, Any]:
        """
        Explain what the code does.
        
        Args:
            code: Code to explain
            language: Programming language
            detail_level: "simple", "medium", or "detailed"
        
        Returns:
            Explanation of the code
        """
        detail_prompts = {
            "simple": "Explain in one sentence what this code does:",
            "medium": "Explain what this code does and how it works:",
            "detailed": "Provide a detailed explanation of this code, including purpose, logic, and any important details:"
        }
        
        prompt = f"""{detail_prompts.get(detail_level, detail_prompts["medium"])}

```{language}
{code}
```"""
        
        try:
            # Use Claude for best explanations
            result = await self.ai_router.analyze_code(
                code=code,
                language=language,
                analysis_type="explain"
            )
            
            return {
                "success": True,
                "explanation": result["content"],
                "model": result["model"]
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    
    async def find_bugs(
        self,
        code: str,
        language: str = "nexuslang"
    ) -> Dict[str, Any]:
        """
        Detect potential bugs and issues in code.
        
        Args:
            code: Code to analyze
            language: Programming language
        
        Returns:
            List of potential bugs and suggestions
        """
        try:
            # Use Claude for best analysis
            result = await self.ai_router.analyze_code(
                code=code,
                language=language,
                analysis_type="debug"
            )
            
            return {
                "success": True,
                "analysis": result["content"],
                "model": result["model"],
                "usage": result["usage"]
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    
    async def suggest_improvements(
        self,
        code: str,
        language: str = "nexuslang"
    ) -> Dict[str, Any]:
        """
        Suggest code improvements and best practices.
        
        Args:
            code: Code to analyze
            language: Programming language
        
        Returns:
            Improvement suggestions
        """
        try:
            # Use Claude for best code review
            result = await self.ai_router.analyze_code(
                code=code,
                language=language,
                analysis_type="review"
            )
            
            return {
                "success": True,
                "suggestions": result["content"],
                "model": result["model"],
                "usage": result["usage"]
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    
    async def optimize_code(
        self,
        code: str,
        language: str = "nexuslang"
    ) -> Dict[str, Any]:
        """
        Suggest performance optimizations.
        
        Args:
            code: Code to optimize
            language: Programming language
        
        Returns:
            Optimization suggestions
        """
        try:
            # Use Claude for optimization analysis
            result = await self.ai_router.analyze_code(
                code=code,
                language=language,
                analysis_type="optimize"
            )
            
            return {
                "success": True,
                "optimizations": result["content"],
                "model": result["model"],
                "usage": result["usage"]
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    
    async def natural_language_to_code(
        self,
        description: str,
        language: str = "nexuslang",
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Convert natural language description to code.
        
        Args:
            description: What the code should do
            language: Target programming language
            context: Additional context about the project
        
        Returns:
            Generated code
        """
        try:
            # Use CodeLlama for code generation
            result = await self.ai_router.generate_code(
                prompt=description,
                language=language,
                context=context
            )
            
            return {
                "success": True,
                "code": result["content"],
                "model": result["model"],
                "usage": result["usage"]
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    
    async def generate_documentation(
        self,
        code: str,
        language: str = "nexuslang",
        doc_style: str = "inline"
    ) -> Dict[str, Any]:
        """
        Generate documentation for code.
        
        Args:
            code: Code to document
            language: Programming language
            doc_style: "inline" for inline comments or "docstring" for documentation blocks
        
        Returns:
            Documented code
        """
        style_prompts = {
            "inline": "Add clear inline comments explaining each section:",
            "docstring": "Add comprehensive docstring/documentation blocks:"
        }
        
        prompt = f"""{style_prompts.get(doc_style, style_prompts["inline"])}

```{language}
{code}
```

Return the code with added documentation."""
        
        try:
            result = await self.ai_router.chat_completion(
                messages=[
                    {"role": "system", "content": f"You are a {language} documentation expert."},
                    {"role": "user", "content": prompt}
                ],
                model=AIModel.CLAUDE_SONNET,  # Best for documentation
                temperature=0.5
            )
            
            return {
                "success": True,
                "documented_code": result["content"],
                "model": result["model"]
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    
    async def refactor_code(
        self,
        code: str,
        refactoring_goal: str,
        language: str = "nexuslang"
    ) -> Dict[str, Any]:
        """
        Refactor code according to specified goal.
        
        Args:
            code: Code to refactor
            refactoring_goal: What to achieve (e.g., "extract function", "simplify logic")
            language: Programming language
        
        Returns:
            Refactored code
        """
        prompt = f"""Refactor this {language} code to: {refactoring_goal}

Original code:
```{language}
{code}
```

Provide the refactored code and explain the changes."""
        
        try:
            result = await self.ai_router.chat_completion(
                messages=[
                    {"role": "system", "content": f"You are an expert {language} code refactoring assistant."},
                    {"role": "user", "content": prompt}
                ],
                model=AIModel.CLAUDE_SONNET,
                temperature=0.4
            )
            
            return {
                "success": True,
                "refactored_code": result["content"],
                "model": result["model"]
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    
    async def chat_about_code(
        self,
        code: str,
        question: str,
        language: str = "nexuslang",
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Have a conversation about code.
        
        Args:
            code: The code being discussed
            question: User's question about the code
            language: Programming language
            conversation_history: Previous messages in the conversation
        
        Returns:
            AI's response
        """
        messages = conversation_history or []
        
        # Add system message if this is the start
        if not messages:
            messages.append({
                "role": "system",
                "content": f"You are an expert {language} programming assistant. Help the user understand and work with their code."
            })
            messages.append({
                "role": "user",
                "content": f"Here's my code:\n\n```{language}\n{code}\n```"
            })
        
        # Add current question
        messages.append({
            "role": "user",
            "content": question
        })
        
        try:
            result = await self.ai_router.chat_completion(
                messages=messages,
                model=AIModel.CLAUDE_SONNET,  # Best for conversational code help
                temperature=0.7
            )
            
            return {
                "success": True,
                "response": result["content"],
                "model": result["model"],
                "conversation_history": messages + [
                    {"role": "assistant", "content": result["content"]}
                ]
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Global IDE AI assistant instance
_ide_ai_assistant: Optional[IDEAIAssistant] = None


def get_ide_ai_assistant() -> IDEAIAssistant:
    """Get or create global IDE AI assistant instance."""
    global _ide_ai_assistant
    if _ide_ai_assistant is None:
        _ide_ai_assistant = IDEAIAssistant()
    return _ide_ai_assistant

