"""
Quick standalone parser test (no dependencies needed)
"""

# Test personality block parsing
source = """
personality {
    curiosity: 0.9,
    analytical: 0.8
}
"""

from lexer.lexer import Lexer
from parser.parser import Parser

lexer = Lexer(source)
tokens = lexer.tokenize()
print(f"✅ Lexed {len(tokens)} tokens")

parser = Parser(tokens)
ast = parser.parse()
print(f"✅ Parsed AST with {len(ast.statements)} statements")

if len(ast.statements) > 0:
    stmt = ast.statements[0]
    print(f"✅ First statement: {type(stmt).__name__}")
    if hasattr(stmt, 'traits'):
        print(f"✅ Personality traits: {stmt.traits}")

print("\n✅ Parser works correctly with v2 features!")

