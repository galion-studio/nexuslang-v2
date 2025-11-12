"""Environment for variable and function storage"""

from typing import Any, Dict, Optional


class Environment:
    """Represents a scope with variables and functions"""
    
    def __init__(self, parent: Optional['Environment'] = None):
        self.parent = parent
        self.variables: Dict[str, Any] = {}
        self.constants: set = set()
    
    def define(self, name: str, value: Any, is_const: bool = False):
        """Define a new variable"""
        self.variables[name] = value
        if is_const:
            self.constants.add(name)
    
    def get(self, name: str) -> Any:
        """Get variable value"""
        if name in self.variables:
            return self.variables[name]
        
        if self.parent:
            return self.parent.get(name)
        
        raise NameError(f"Undefined variable: {name}")
    
    def set(self, name: str, value: Any):
        """Set variable value"""
        if name in self.constants:
            raise ValueError(f"Cannot reassign constant: {name}")
        
        if name in self.variables:
            self.variables[name] = value
            return
        
        if self.parent:
            self.parent.set(name, value)
            return
        
        raise NameError(f"Undefined variable: {name}")
    
    def exists(self, name: str) -> bool:
        """Check if variable exists"""
        if name in self.variables:
            return True
        
        if self.parent:
            return self.parent.exists(name)
        
        return False

