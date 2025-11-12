"""
Test suite for NexusLang v2 Lexer
Tests tokenization of all v2 features including AI-native syntax
"""

import sys
import os

# Add parent directory to path to import nexuslang modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import directly from files to avoid loading all dependencies
from lexer.lexer import Lexer
from lexer.token import TokenType


def test_basic_tokens():
    """Test basic token types"""
    source = "let x = 42"
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    
    assert tokens[0].type == TokenType.LET
    assert tokens[1].type == TokenType.IDENTIFIER
    assert tokens[1].value == "x"
    assert tokens[2].type == TokenType.EQUAL
    assert tokens[3].type == TokenType.INTEGER
    assert tokens[3].value == 42
    print("✅ Basic tokens test passed")


def test_v2_keywords():
    """Test v2 AI-native keywords"""
    source = "personality knowledge voice say listen"
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    
    assert tokens[0].type == TokenType.PERSONALITY
    assert tokens[1].type == TokenType.KNOWLEDGE
    assert tokens[2].type == TokenType.VOICE
    assert tokens[3].type == TokenType.SAY
    assert tokens[4].type == TokenType.LISTEN
    print("✅ v2 keywords test passed")


def test_personality_block():
    """Test personality block syntax"""
    source = """
personality {
    curiosity: 0.9,
    analytical: 0.8
}
"""
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    
    # Find tokens (ignoring newlines)
    non_newline = [t for t in tokens if t.type not in [TokenType.NEWLINE, TokenType.EOF]]
    
    assert non_newline[0].type == TokenType.PERSONALITY
    assert non_newline[1].type == TokenType.LBRACE
    assert non_newline[2].type == TokenType.CURIOSITY
    assert non_newline[3].type == TokenType.COLON
    assert non_newline[4].type == TokenType.FLOAT
    assert non_newline[4].value == 0.9
    assert non_newline[5].type == TokenType.COMMA
    print("✅ Personality block test passed")


def test_function_call():
    """Test function call syntax"""
    source = 'say("Hello", emotion="happy")'
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    
    non_newline = [t for t in tokens if t.type not in [TokenType.NEWLINE, TokenType.EOF]]
    
    assert non_newline[0].type == TokenType.SAY
    assert non_newline[1].type == TokenType.LPAREN
    assert non_newline[2].type == TokenType.STRING
    assert non_newline[2].value == "Hello"
    assert non_newline[3].type == TokenType.COMMA
    # emotion is a keyword in v2, that's ok
    assert non_newline[4].type == TokenType.EMOTION or non_newline[4].type == TokenType.IDENTIFIER
    print("✅ Function call test passed")


def test_operators():
    """Test all operators"""
    source = "+ - * / % ** == != < <= > >= && || ! -> =>"
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    
    non_newline = [t for t in tokens if t.type not in [TokenType.NEWLINE, TokenType.EOF]]
    
    expected = [
        TokenType.PLUS, TokenType.MINUS, TokenType.STAR, TokenType.SLASH,
        TokenType.PERCENT, TokenType.POWER, TokenType.EQ, TokenType.NE,
        TokenType.LT, TokenType.LE, TokenType.GT, TokenType.GE,
        TokenType.AND, TokenType.OR, TokenType.NOT, 
        TokenType.ARROW, TokenType.FAT_ARROW
    ]
    
    for i, expected_type in enumerate(expected):
        assert non_newline[i].type == expected_type
    
    print("✅ Operators test passed")


def test_comments():
    """Test comment handling"""
    source = """
// Single line comment
let x = 5

/* Multi-line
   comment */
let y = 10
"""
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    
    # Comments should be skipped
    non_newline = [t for t in tokens if t.type not in [TokenType.NEWLINE, TokenType.EOF]]
    
    assert non_newline[0].type == TokenType.LET
    assert non_newline[1].value == "x"
    assert non_newline[4].type == TokenType.LET
    assert non_newline[5].value == "y"
    print("✅ Comments test passed")


def test_string_escapes():
    """Test string escape sequences"""
    source = r'"Hello\nWorld\t!"'
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    
    assert tokens[0].type == TokenType.STRING
    assert tokens[0].value == "Hello\nWorld\t!"
    print("✅ String escapes test passed")


def test_example_file_personality():
    """Test lexing the personality demo example"""
    with open("examples/personality_demo.nx", "r") as f:
        source = f.read()
    
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    
    # Should tokenize without errors
    assert len(tokens) > 0
    assert tokens[-1].type == TokenType.EOF
    
    # Check for personality keyword
    has_personality = any(t.type == TokenType.PERSONALITY for t in tokens)
    assert has_personality
    
    print("✅ Personality example file test passed")


def test_example_file_knowledge():
    """Test lexing the knowledge demo example"""
    with open("examples/knowledge_demo.nx", "r") as f:
        source = f.read()
    
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    
    # Should tokenize without errors
    assert len(tokens) > 0
    assert tokens[-1].type == TokenType.EOF
    
    # Check for knowledge keyword
    has_knowledge = any(t.type == TokenType.KNOWLEDGE for t in tokens)
    assert has_knowledge
    
    print("✅ Knowledge example file test passed")


def test_example_file_voice():
    """Test lexing the voice demo example"""
    with open("examples/voice_demo.nx", "r") as f:
        source = f.read()
    
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    
    # Should tokenize without errors
    assert len(tokens) > 0
    assert tokens[-1].type == TokenType.EOF
    
    # Check for voice keywords
    has_say = any(t.type == TokenType.SAY for t in tokens)
    has_listen = any(t.type == TokenType.LISTEN for t in tokens)
    assert has_say and has_listen
    
    print("✅ Voice example file test passed")


if __name__ == "__main__":
    print("Running NexusLang v2 Lexer Tests...")
    print("=" * 50)
    
    try:
        test_basic_tokens()
        test_v2_keywords()
        test_personality_block()
        test_function_call()
        test_operators()
        test_comments()
        test_string_escapes()
        test_example_file_personality()
        test_example_file_knowledge()
        test_example_file_voice()
        
        print("=" * 50)
        print("✅ All lexer tests passed!")
        
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

