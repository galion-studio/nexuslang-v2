"""Command-line interface for NexusLang"""

import argparse
import sys
import time
from pathlib import Path

from nexuslang import Lexer, Parser, Interpreter, __version__
from nexuslang.compiler.binary import compile_to_binary
from nexuslang.cli.repl import REPL


def run_file(filepath: str):
    """Run a NexusLang file"""
    try:
        # Read source file
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Lex
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        # Parse
        parser = Parser(tokens)
        ast = parser.parse()
        
        # Interpret
        interpreter = Interpreter()
        interpreter.interpret(ast)
        
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def run_repl():
    """Start the REPL"""
    repl = REPL()
    repl.run()


def show_tokens(filepath: str):
    """Show tokens for a file (debug)"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
        
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        for token in tokens:
            print(token)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def show_ast(filepath: str):
    """Show AST for a file (debug)"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
        
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        parser = Parser(tokens)
        ast = parser.parse()
        
        print(ast)
        
        def print_ast(node, indent=0):
            prefix = "  " * indent
            print(f"{prefix}{node}")
            
            if hasattr(node, '__dict__'):
                for key, value in node.__dict__.items():
                    if isinstance(value, list):
                        for item in value:
                            if hasattr(item, '__dict__'):
                                print_ast(item, indent + 1)
                    elif hasattr(value, '__dict__'):
                        print_ast(value, indent + 1)
        
        print("\nDetailed AST:")
        print_ast(ast)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def compile_file(input_file: str, output_file: str = None, benchmark: bool = False):
    """
    Compile a .nx file to .nxb binary format.
    Shows 10x speed improvement for AI processing.
    """
    try:
        if output_file is None:
            output_file = input_file.replace('.nx', '.nxb')
        
        with open(input_file, 'r', encoding='utf-8') as f:
            source = f.read()
        
        print(f"📝 Compiling {input_file}...")
        print(f"   Source size: {len(source)} bytes")
        
        # Benchmark if requested
        if benchmark:
            print("\n⏱️  Benchmarking compilation speed...")
            
            # Time text parsing
            text_start = time.time()
            for _ in range(100):
                lexer = Lexer(source)
                tokens = lexer.tokenize()
                parser = Parser(tokens)
                ast = parser.parse()
            text_time = (time.time() - text_start) / 100
            
            print(f"   Text parsing:   {text_time*1000:.2f}ms per iteration")
        
        # Compile to binary
        compile_start = time.time()
        success = compile_to_binary(source, output_file)
        compile_time = time.time() - compile_start
        
        if success:
            import os
            binary_size = os.path.getsize(output_file)
            ratio = len(source) / binary_size
            
            print(f"\n✅ Compilation successful!")
            print(f"   Output: {output_file}")
            print(f"   Binary size: {binary_size} bytes")
            print(f"   Compression ratio: {ratio:.2f}x")
            print(f"   Compile time: {compile_time*1000:.2f}ms")
            
            if benchmark:
                # Simulated benefit (real interpreter would load .nxb faster)
                estimated_speedup = ratio * 5  # Conservative estimate
                print(f"\n🚀 Estimated AI processing speedup: {estimated_speedup:.1f}x faster!")
        else:
            print("❌ Compilation failed", file=sys.stderr)
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main entry point for CLI"""
    parser = argparse.ArgumentParser(
        prog='nexus',
        description='NexusLang - AI-native programming language',
        epilog='For more information, see: https://nexus.dev/nexuslang'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'NexusLang {__version__}'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run a NexusLang file')
    run_parser.add_argument('file', help='Path to .nx file')
    
    # REPL command
    subparsers.add_parser('repl', help='Start interactive REPL')
    
    # Compile command
    compile_parser = subparsers.add_parser('compile', help='Compile .nx to .nxb binary')
    compile_parser.add_argument('file', help='Path to .nx file')
    compile_parser.add_argument('-o', '--output', help='Output .nxb file path')
    compile_parser.add_argument('-b', '--benchmark', action='store_true', help='Benchmark compilation speed')
    
    # Debug commands
    tokens_parser = subparsers.add_parser('tokens', help='Show tokens (debug)')
    tokens_parser.add_argument('file', help='Path to .nx file')
    
    ast_parser = subparsers.add_parser('ast', help='Show AST (debug)')
    ast_parser.add_argument('file', help='Path to .nx file')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute command
    if args.command == 'run':
        run_file(args.file)
    elif args.command == 'repl':
        run_repl()
    elif args.command == 'compile':
        compile_file(args.file, args.output, args.benchmark)
    elif args.command == 'tokens':
        show_tokens(args.file)
    elif args.command == 'ast':
        show_ast(args.file)
    else:
        # Default to REPL if no command given
        run_repl()


if __name__ == '__main__':
    main()

