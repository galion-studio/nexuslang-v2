"""AST Node definitions for NexusLang"""

from dataclasses import dataclass
from typing import Any, List, Optional, Dict
from abc import ABC, abstractmethod


class ASTNode(ABC):
    """Base class for all AST nodes"""
    
    @abstractmethod
    def __repr__(self) -> str:
        pass


@dataclass
class Program(ASTNode):
    """Root node of the program"""
    statements: List[ASTNode]
    
    def __repr__(self) -> str:
        return f"Program({len(self.statements)} statements)"


# Literals

@dataclass
class IntegerLiteral(ASTNode):
    value: int
    
    def __repr__(self) -> str:
        return f"Int({self.value})"


@dataclass
class FloatLiteral(ASTNode):
    value: float
    
    def __repr__(self) -> str:
        return f"Float({self.value})"


@dataclass
class StringLiteral(ASTNode):
    value: str
    
    def __repr__(self) -> str:
        return f"String({self.value!r})"


@dataclass
class BooleanLiteral(ASTNode):
    value: bool
    
    def __repr__(self) -> str:
        return f"Bool({self.value})"


@dataclass
class ArrayLiteral(ASTNode):
    elements: List[ASTNode]
    
    def __repr__(self) -> str:
        return f"Array([{len(self.elements)} elements])"


# Identifiers

@dataclass
class Identifier(ASTNode):
    name: str
    
    def __repr__(self) -> str:
        return f"Id({self.name})"


# Operators

@dataclass
class BinaryOp(ASTNode):
    left: ASTNode
    operator: str
    right: ASTNode
    
    def __repr__(self) -> str:
        return f"BinaryOp({self.operator})"


@dataclass
class UnaryOp(ASTNode):
    operator: str
    operand: ASTNode
    
    def __repr__(self) -> str:
        return f"UnaryOp({self.operator})"


# Assignments

@dataclass
class Assignment(ASTNode):
    target: Identifier
    value: ASTNode
    
    def __repr__(self) -> str:
        return f"Assignment({self.target.name} = ...)"


# Variable declarations

@dataclass
class VariableDeclaration(ASTNode):
    name: str
    type_annotation: Optional[str]
    value: Optional[ASTNode]
    is_const: bool = False
    
    def __repr__(self) -> str:
        kind = "const" if self.is_const else "let"
        return f"{kind} {self.name}"


# Functions

@dataclass
class Parameter:
    name: str
    type_annotation: Optional[str] = None


@dataclass
class FunctionDeclaration(ASTNode):
    name: str
    parameters: List[Parameter]
    return_type: Optional[str]
    body: 'Block'
    
    def __repr__(self) -> str:
        return f"fn {self.name}({len(self.parameters)} params)"


@dataclass
class FunctionCall(ASTNode):
    function: ASTNode  # Usually Identifier, but could be expression
    arguments: List[ASTNode]
    
    def __repr__(self) -> str:
        return f"Call({len(self.arguments)} args)"


@dataclass
class ReturnStatement(ASTNode):
    value: Optional[ASTNode]
    
    def __repr__(self) -> str:
        return "Return"


# Control flow

@dataclass
class IfStatement(ASTNode):
    condition: ASTNode
    then_block: 'Block'
    else_block: Optional['Block']
    
    def __repr__(self) -> str:
        return "If"


@dataclass
class WhileStatement(ASTNode):
    condition: ASTNode
    body: 'Block'
    
    def __repr__(self) -> str:
        return "While"


@dataclass
class ForStatement(ASTNode):
    variable: str
    iterable: ASTNode
    body: 'Block'
    
    def __repr__(self) -> str:
        return f"For({self.variable} in ...)"


@dataclass
class BreakStatement(ASTNode):
    def __repr__(self) -> str:
        return "Break"


@dataclass
class ContinueStatement(ASTNode):
    def __repr__(self) -> str:
        return "Continue"


# Block

@dataclass
class Block(ASTNode):
    statements: List[ASTNode]
    
    def __repr__(self) -> str:
        return f"Block({len(self.statements)} statements)"


# Array and member access

@dataclass
class IndexAccess(ASTNode):
    object: ASTNode
    index: ASTNode
    
    def __repr__(self) -> str:
        return "IndexAccess"


@dataclass
class MemberAccess(ASTNode):
    object: ASTNode
    member: str
    
    def __repr__(self) -> str:
        return f"MemberAccess(.{self.member})"


# Match statement

@dataclass
class MatchArm:
    pattern: ASTNode
    body: ASTNode


@dataclass
class MatchStatement(ASTNode):
    value: ASTNode
    arms: List[MatchArm]
    
    def __repr__(self) -> str:
        return f"Match({len(self.arms)} arms)"


# Struct definition

@dataclass
class StructField:
    name: str
    type_annotation: str


@dataclass
class StructDeclaration(ASTNode):
    name: str
    fields: List[StructField]
    
    def __repr__(self) -> str:
        return f"struct {self.name}"


# Import statement

@dataclass
class ImportStatement(ASTNode):
    module: str
    items: Optional[List[str]] = None  # None means import whole module
    alias: Optional[str] = None
    
    def __repr__(self) -> str:
        return f"import {self.module}"

