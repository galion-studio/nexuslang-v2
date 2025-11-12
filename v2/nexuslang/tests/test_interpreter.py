"""
Test suite for NexusLang v2 Interpreter
Tests execution of v2 AI-native features
"""

import sys
import os
import io

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lexer.lexer import Lexer
from parser.parser import Parser
from interpreter.interpreter import Interpreter


def capture_output(code):
    """Helper to capture print output from code execution"""
    old_stdout = sys.stdout
    sys.stdout = captured = io.StringIO()
    
    try:
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        interpreter = Interpreter()
        interpreter.interpret(ast)
        output = captured.getvalue()
    finally:
        sys.stdout = old_stdout
    
    return output


def test_basic_execution():
    """Test basic code execution"""
    code = '''
fn main() {
    print("Hello, World!")
}
main()
'''
    output = capture_output(code)
    assert "Hello, World!" in output
    print("✅ Basic execution test passed")


def test_variables():
    """Test variable declaration and usage"""
    code = '''
let x = 42
let y = 10
print(x + y)
'''
    output = capture_output(code)
    assert "52" in output
    print("✅ Variables test passed")


def test_functions():
    """Test function declaration and calls"""
    code = '''
fn add(a, b) {
    return a + b
}

let result = add(5, 3)
print(result)
'''
    output = capture_output(code)
    assert "8" in output
    print("✅ Functions test passed")


def test_personality_block():
    """Test personality block execution"""
    code = '''
personality {
    curiosity: 0.9,
    analytical: 0.8
}

fn main() {
    print("Personality defined")
}

main()
'''
    output = capture_output(code)
    assert "Personality defined" in output
    print("✅ Personality block test passed")


def test_knowledge_function():
    """Test knowledge query function"""
    code = '''
fn main() {
    let facts = knowledge("AI")
    print("Found facts")
}

main()
'''
    output = capture_output(code)
    assert "Found facts" in output
    print("✅ Knowledge function test passed")


def test_say_function():
    """Test say function (voice output)"""
    code = '''
fn main() {
    say("Test message", emotion="happy")
    print("Say executed")
}

main()
'''
    output = capture_output(code)
    # say() function should print with emoji
    assert "🎤" in output or "Say executed" in output
    print("✅ Say function test passed")


def test_loops():
    """Test loop execution"""
    code = '''
fn main() {
    for i in 0..3 {
        print(i)
    }
}

main()
'''
    output = capture_output(code)
    assert "0" in output and "1" in output and "2" in output
    print("✅ Loops test passed")


def test_recursion():
    """Test recursive functions"""
    code = '''
fn factorial(n) {
    if n <= 1 {
        return 1
    }
    return n * factorial(n - 1)
}

print(factorial(5))
'''
    output = capture_output(code)
    assert "120" in output
    print("✅ Recursion test passed")


def test_arrays():
    """Test array operations"""
    code = '''
let arr = [1, 2, 3, 4, 5]
print(arr[0])
print(arr[4])
'''
    output = capture_output(code)
    assert "1" in output and "5" in output
    print("✅ Arrays test passed")


def test_example_programs():
    """Test that example programs execute without errors"""
    example_files = [
        "examples/01_hello_world.nx",
        "examples/02_personality_traits.nx",
        "examples/03_knowledge_query.nx",
    ]
    
    for example_file in example_files:
        if os.path.exists(example_file):
            with open(example_file, 'r') as f:
                code = f.read()
            
            try:
                output = capture_output(code)
                assert len(output) > 0  # Should produce some output
                print(f"✅ Example {os.path.basename(example_file)} executed successfully")
            except Exception as e:
                print(f"❌ Example {os.path.basename(example_file)} failed: {e}")
                raise


if __name__ == "__main__":
    print("Running NexusLang v2 Interpreter Tests...")
    print("=" * 50)
    
    try:
        test_basic_execution()
        test_variables()
        test_functions()
        test_personality_block()
        test_knowledge_function()
        test_say_function()
        test_loops()
        test_recursion()
        test_arrays()
        test_example_programs()
        
        print("=" * 50)
        print("✅ All interpreter tests passed!")
        
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

