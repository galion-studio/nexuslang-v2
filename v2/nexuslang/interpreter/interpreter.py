"""Interpreter for executing NexusLang AST"""

from typing import Any, List, Optional
from ..syntax_tree.nodes import *
from ..syntax_tree.ai_nodes import (
    PersonalityBlock, KnowledgeQuery, SayStatement,
    ListenExpression, VoiceBlock, OptimizeSelfStatement,
    LoadModelExpression, EmotionExpression, ConfidenceExpression
)
from .environment import Environment
from ..runtime.builtins import get_builtins
from ..runtime.ai_builtins import get_ai_builtins


class RuntimeError(Exception):
    """Raised when interpreter encounters a runtime error"""
    pass


class ReturnValue(Exception):
    """Used to unwind the stack on return"""
    def __init__(self, value: Any):
        self.value = value


class BreakException(Exception):
    """Used to break out of loops"""
    pass


class ContinueException(Exception):
    """Used to continue to next iteration"""
    pass


class NexusFunction:
    """Represents a NexusLang function"""
    
    def __init__(self, declaration: FunctionDeclaration, closure: Environment):
        self.declaration = declaration
        self.closure = closure
    
    def call(self, interpreter: 'Interpreter', arguments: List[Any]) -> Any:
        # Create new environment for function scope
        env = Environment(self.closure)
        
        # Bind parameters
        for i, param in enumerate(self.declaration.parameters):
            if i < len(arguments):
                env.define(param.name, arguments[i])
            else:
                env.define(param.name, None)  # Default to None
        
        # Execute function body
        try:
            interpreter.execute_block(self.declaration.body, env)
        except ReturnValue as ret:
            return ret.value
        
        return None


class Interpreter:
    """Tree-walking interpreter for NexusLang"""
    
    def __init__(self):
        self.globals = Environment()
        self.environment = self.globals
        
        # Load built-in functions
        for name, func in get_builtins().items():
            self.globals.define(name, func)
        
        # Load AI-native built-ins
        for name, func in get_ai_builtins().items():
            self.globals.define(name, func)
    
    def interpret(self, program: Program) -> Any:
        """Interpret a program"""
        result = None
        for statement in program.statements:
            result = self.evaluate(statement)
        return result
    
    def evaluate(self, node: ASTNode) -> Any:
        """Evaluate an AST node"""
        
        # Literals
        if isinstance(node, IntegerLiteral):
            return node.value
        
        if isinstance(node, FloatLiteral):
            return node.value
        
        if isinstance(node, StringLiteral):
            return node.value
        
        if isinstance(node, BooleanLiteral):
            return node.value
        
        if isinstance(node, ArrayLiteral):
            return [self.evaluate(elem) for elem in node.elements]
        
        # Identifier
        if isinstance(node, Identifier):
            return self.environment.get(node.name)
        
        # Binary operations
        if isinstance(node, BinaryOp):
            return self.evaluate_binary_op(node)
        
        # Unary operations
        if isinstance(node, UnaryOp):
            return self.evaluate_unary_op(node)
        
        # Variable declaration
        if isinstance(node, VariableDeclaration):
            value = None
            if node.value:
                value = self.evaluate(node.value)
            self.environment.define(node.name, value, node.is_const)
            return None
        
        # Assignment
        if isinstance(node, Assignment):
            value = self.evaluate(node.value)
            self.environment.set(node.target.name, value)
            return value
        
        # Function declaration
        if isinstance(node, FunctionDeclaration):
            func = NexusFunction(node, self.environment)
            self.environment.define(node.name, func)
            return None
        
        # Function call
        if isinstance(node, FunctionCall):
            return self.evaluate_function_call(node)
        
        # Return statement
        if isinstance(node, ReturnStatement):
            value = None
            if node.value:
                value = self.evaluate(node.value)
            raise ReturnValue(value)
        
        # If statement
        if isinstance(node, IfStatement):
            condition = self.evaluate(node.condition)
            if self.is_truthy(condition):
                self.execute_block(node.then_block, Environment(self.environment))
            elif node.else_block:
                self.execute_block(node.else_block, Environment(self.environment))
            return None
        
        # While statement
        if isinstance(node, WhileStatement):
            try:
                while self.is_truthy(self.evaluate(node.condition)):
                    try:
                        self.execute_block(node.body, Environment(self.environment))
                    except ContinueException:
                        continue
            except BreakException:
                pass
            return None
        
        # For statement
        if isinstance(node, ForStatement):
            iterable = self.evaluate(node.iterable)
            
            # Handle range (start..end)
            if isinstance(iterable, tuple) and len(iterable) == 2:
                start, end = iterable
                iterable = range(start, end)
            
            try:
                for value in iterable:
                    loop_env = Environment(self.environment)
                    loop_env.define(node.variable, value)
                    
                    try:
                        self.execute_block(node.body, loop_env)
                    except ContinueException:
                        continue
            except BreakException:
                pass
            
            return None
        
        # Break statement
        if isinstance(node, BreakStatement):
            raise BreakException()
        
        # Continue statement
        if isinstance(node, ContinueStatement):
            raise ContinueException()
        
        # Block
        if isinstance(node, Block):
            self.execute_block(node, Environment(self.environment))
            return None
        
        # Array index access
        if isinstance(node, IndexAccess):
            obj = self.evaluate(node.object)
            index = self.evaluate(node.index)
            return obj[index]
        
        # Member access
        if isinstance(node, MemberAccess):
            obj = self.evaluate(node.object)
            
            # Handle array methods
            if isinstance(obj, list):
                if node.member == "len":
                    return lambda: len(obj)
                elif node.member == "push":
                    return lambda x: obj.append(x)
            
            # Handle string methods
            if isinstance(obj, str):
                if node.member == "len":
                    return lambda: len(obj)
                elif node.member == "upper":
                    return lambda: obj.upper()
                elif node.member == "lower":
                    return lambda: obj.lower()
            
            # Handle Python object attributes (for Tensor and other AI objects)
            if hasattr(obj, node.member):
                attr = getattr(obj, node.member)
                return attr
            
            raise RuntimeError(f"Object has no member: {node.member}")
        
        # Import statement (stub for now)
        if isinstance(node, ImportStatement):
            # TODO: Implement module loading
            return None
        
        # ====== v2 AI-Native Nodes ======
        
        # Personality block
        if isinstance(node, PersonalityBlock):
            # Store personality traits in global environment
            self.globals.define("__personality__", node.traits)
            return None
        
        # Knowledge query
        if isinstance(node, KnowledgeQuery):
            # Call the knowledge() runtime function
            knowledge_func = self.globals.get("knowledge")
            if knowledge_func:
                return knowledge_func(node.query, node.filters or {})
            return []
        
        # Say statement (voice output)
        if isinstance(node, SayStatement):
            # Call the say() runtime function
            say_func = self.globals.get("say")
            if say_func:
                kwargs = {}
                if node.emotion:
                    kwargs['emotion'] = node.emotion
                if node.voice_id:
                    kwargs['voice_id'] = node.voice_id
                if node.speed != 1.0:
                    kwargs['speed'] = node.speed
                return say_func(node.text, **kwargs)
            # Fallback: just print
            print(f"[SAY] {node.text}")
            return None
        
        # Listen expression (voice input)
        if isinstance(node, ListenExpression):
            # Call the listen() runtime function
            listen_func = self.globals.get("listen")
            if listen_func:
                kwargs = {}
                if node.timeout:
                    kwargs['timeout'] = node.timeout
                if node.language:
                    kwargs['language'] = node.language
                return listen_func(**kwargs)
            # Fallback: return empty string
            return ""
        
        # Voice block
        if isinstance(node, VoiceBlock):
            # Execute voice block statements
            for stmt in node.body:
                self.evaluate(stmt)
            return None
        
        # Optimize self statement
        if isinstance(node, OptimizeSelfStatement):
            # Call the optimize_self() runtime function
            optimize_func = self.globals.get("optimize_self")
            if optimize_func:
                kwargs = {'metric': node.metric}
                if node.target:
                    kwargs['target'] = node.target
                if node.strategy:
                    kwargs['strategy'] = node.strategy
                return optimize_func(**kwargs)
            return None
        
        # Load model expression
        if isinstance(node, LoadModelExpression):
            # Call the load_model() runtime function
            load_model_func = self.globals.get("load_model")
            if load_model_func:
                return load_model_func(node.model_name, node.config or {})
            return None
        
        # Emotion expression
        if isinstance(node, EmotionExpression):
            # Call the emotion() runtime function
            emotion_func = self.globals.get("emotion")
            if emotion_func:
                if node.emotion_type:
                    return emotion_func(node.emotion_type, node.intensity)
                else:
                    return emotion_func()
            return None
        
        # Confidence expression
        if isinstance(node, ConfidenceExpression):
            # Call the confidence() runtime function
            confidence_func = self.globals.get("confidence")
            if confidence_func:
                value = self.evaluate(node.value) if node.value else None
                if node.threshold:
                    return confidence_func(value, node.threshold)
                else:
                    return confidence_func(value) if value else confidence_func()
            return 0.5  # Default confidence
        
        raise RuntimeError(f"Cannot evaluate node: {type(node).__name__}")
    
    def evaluate_binary_op(self, node: BinaryOp) -> Any:
        """Evaluate binary operation"""
        left = self.evaluate(node.left)
        
        # Short-circuit evaluation for logical operators
        if node.operator == "&&":
            if not self.is_truthy(left):
                return False
            return self.is_truthy(self.evaluate(node.right))
        
        if node.operator == "||":
            if self.is_truthy(left):
                return True
            return self.is_truthy(self.evaluate(node.right))
        
        right = self.evaluate(node.right)
        
        # Arithmetic
        if node.operator == "+":
            return left + right
        if node.operator == "-":
            return left - right
        if node.operator == "*":
            return left * right
        if node.operator == "/":
            if right == 0:
                raise RuntimeError("Division by zero")
            return left / right
        if node.operator == "%":
            return left % right
        
        # Comparison
        if node.operator == "==":
            return left == right
        if node.operator == "!=":
            return left != right
        if node.operator == "<":
            return left < right
        if node.operator == "<=":
            return left <= right
        if node.operator == ">":
            return left > right
        if node.operator == ">=":
            return left >= right
        
        # Range
        if node.operator == "..":
            return (left, right)  # Return tuple for range
        
        raise RuntimeError(f"Unknown binary operator: {node.operator}")
    
    def evaluate_unary_op(self, node: UnaryOp) -> Any:
        """Evaluate unary operation"""
        operand = self.evaluate(node.operand)
        
        if node.operator == "-":
            return -operand
        if node.operator == "!":
            return not self.is_truthy(operand)
        
        raise RuntimeError(f"Unknown unary operator: {node.operator}")
    
    def evaluate_function_call(self, node: FunctionCall) -> Any:
        """Evaluate function call"""
        callee = self.evaluate(node.function)
        arguments = [self.evaluate(arg) for arg in node.arguments]
        
        # Handle built-in functions
        if callable(callee) and not isinstance(callee, NexusFunction):
            return callee(*arguments)
        
        # Handle user-defined functions
        if isinstance(callee, NexusFunction):
            return callee.call(self, arguments)
        
        raise RuntimeError(f"Not a function: {callee}")
    
    def execute_block(self, block: Block, environment: Environment):
        """Execute a block of statements in a new environment"""
        previous = self.environment
        try:
            self.environment = environment
            for statement in block.statements:
                self.evaluate(statement)
        finally:
            self.environment = previous
    
    def is_truthy(self, value: Any) -> bool:
        """Determine if a value is truthy"""
        if value is None or value is False:
            return False
        if value == 0 or value == "":
            return False
        return True

