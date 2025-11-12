"""REPL (Read-Eval-Print Loop) for NexusLang"""

import sys
from typing import Optional

from nexuslang import Lexer, Parser, Interpreter, __version__
from nexuslang.lexer.token import TokenType


class REPL:
    """Interactive REPL for NexusLang"""
    
    def __init__(self):
        self.interpreter = Interpreter()
        self.history = []
    
    def run(self):
        """Start the REPL"""
        print(f"NexusLang {__version__}")
        print("Type 'exit' or press Ctrl+C to quit")
        print("Type 'help' for more information")
        print()
        
        while True:
            try:
                # Read input
                line = input(">>> ")
                
                if not line.strip():
                    continue
                
                # Handle special commands
                if line.strip() == 'exit':
                    print("Goodbye!")
                    break
                
                if line.strip() == 'help':
                    self.show_help()
                    continue
                
                if line.strip() == 'history':
                    self.show_history()
                    continue
                
                if line.strip() == 'clear':
                    # Clear screen
                    print('\033[2J\033[H', end='')
                    continue
                
                # Add to history
                self.history.append(line)
                
                # Evaluate
                result = self.eval(line)
                
                # Print result (if not None)
                if result is not None:
                    print(result)
                
            except KeyboardInterrupt:
                print("\nKeyboardInterrupt")
                break
            except EOFError:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)
    
    def eval(self, source: str) -> Optional[any]:
        """Evaluate a line of code"""
        try:
            # Lex
            lexer = Lexer(source)
            tokens = lexer.tokenize()
            
            # Check if it's a single expression (for direct eval)
            # If the tokens are: expr + EOF, treat as expression
            # Otherwise, treat as statement
            
            # Parse
            parser = Parser(tokens)
            ast = parser.parse()
            
            # Interpret
            result = self.interpreter.interpret(ast)
            
            return result
            
        except Exception as e:
            raise e
    
    def show_help(self):
        """Show help message"""
        print("""
NexusLang REPL Commands:
  exit      - Exit the REPL
  help      - Show this help message
  history   - Show command history
  clear     - Clear the screen

Quick Start:
  let x = 42              # Variable declaration
  const PI = 3.14159      # Constant
  print("Hello!")         # Print to console
  
  fn add(a, b) {          # Function declaration
      return a + b
  }
  
  add(5, 3)               # Function call
  
  for i in 0..10 {        # For loop
      print(i)
  }
  
  if x > 0 {              # If statement
      print("positive")
  }

For more examples, visit: https://nexus.dev/nexuslang/docs
""")
    
    def show_history(self):
        """Show command history"""
        if not self.history:
            print("No history yet")
            return
        
        print("\nCommand History:")
        for i, cmd in enumerate(self.history, 1):
            print(f"  {i}. {cmd}")
        print()

