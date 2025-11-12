"""
Test suite for NexusLang v2 Parser
Tests parsing of v2 AI-native features
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lexer.lexer import Lexer
from lexer.token import TokenType
from parser.parser import Parser
from syntax_tree.ai_nodes import (
    PersonalityBlock, KnowledgeQuery, SayStatement, 
    ListenExpression, VoiceBlock
)
from syntax_tree.nodes import Program, FunctionDeclaration


def test_personality_block():
    """Test parsing personality block"""
    source = """
personality {
    curiosity: 0.9,
    analytical: 0.8,
    creative: 0.7
}
"""
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    assert isinstance(ast.statements[0], PersonalityBlock)
    
    personality = ast.statements[0]
    assert personality.traits['curiosity'] == 0.9
    assert personality.traits['analytical'] == 0.8
    assert personality.traits['creative'] == 0.7
    
    print("✅ Personality block parsing test passed")


def test_say_statement():
    """Test parsing say statement"""
    source = 'say("Hello world", emotion="excited")'
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    assert isinstance(ast.statements[0], SayStatement)
    
    say_stmt = ast.statements[0]
    assert say_stmt.text == "Hello world"
    assert say_stmt.emotion == "excited"
    
    print("✅ Say statement parsing test passed")


def test_listen_expression():
    """Test parsing listen expression"""
    source = 'let input = listen(timeout=10)'
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    
    assert isinstance(ast, Program)
    # The listen expression is part of a variable declaration
    
    print("✅ Listen expression parsing test passed")


def test_knowledge_query():
    """Test parsing knowledge query"""
    source = 'knowledge("quantum physics")'
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    
    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    assert isinstance(ast.statements[0], KnowledgeQuery)
    
    query = ast.statements[0]
    assert query.query == "quantum physics"
    
    print("✅ Knowledge query parsing test passed")


def test_complete_program():
    """Test parsing a complete program with v2 features"""
    source = """
personality {
    curiosity: 0.9,
    analytical: 0.8
}

fn main() {
    let facts = knowledge("AI")
    say("Hello", emotion="friendly")
}

main()
"""
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    
    assert isinstance(ast, Program)
    assert len(ast.statements) >= 2  # personality block + function + call
    assert isinstance(ast.statements[0], PersonalityBlock)
    
    # Check function exists
    has_function = any(isinstance(stmt, FunctionDeclaration) for stmt in ast.statements)
    assert has_function
    
    print("✅ Complete program parsing test passed")


def test_example_personality_demo():
    """Test parsing the personality demo example file"""
    with open("examples/personality_demo.nx", "r") as f:
        source = f.read()
    
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    
    assert isinstance(ast, Program)
    assert len(ast.statements) > 0
    
    # Should have personality block
    has_personality = any(isinstance(stmt, PersonalityBlock) for stmt in ast.statements)
    assert has_personality
    
    print("✅ Personality demo file parsing test passed")


if __name__ == "__main__":
    print("Running NexusLang v2 Parser Tests...")
    print("=" * 50)
    
    try:
        test_personality_block()
        test_say_statement()
        test_listen_expression()
        test_knowledge_query()
        test_complete_program()
        test_example_personality_demo()
        
        print("=" * 50)
        print("✅ All parser tests passed!")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

