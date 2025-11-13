"""
NexusLang v2 - Binary Compiler
Compiles .nx files to .nxb (binary) format for faster AI processing.
Implements token compression and semantic encoding.
"""

import struct
import json
from typing import List, Dict, Any, Optional
from enum import IntEnum
from io import BytesIO

from ..lexer.token import Token, TokenType
from ..syntax_tree.nodes import ASTNode
from ..syntax_tree.ai_nodes import (
    PersonalityBlock, KnowledgeQuery, VoiceBlock,
    SayStatement, ListenExpression, OptimizeSelfStatement
)


class OpCode(IntEnum):
    """
    Binary opcodes for NexusLang v2.
    Each opcode is 1 byte (256 max opcodes).
    """
    # Literals
    LOAD_INT = 0x01
    LOAD_FLOAT = 0x02
    LOAD_STRING = 0x03
    LOAD_TRUE = 0x04
    LOAD_FALSE = 0x05
    LOAD_NULL = 0x06
    
    # Variables
    LOAD_VAR = 0x10
    STORE_VAR = 0x11
    LOAD_CONST = 0x12
    
    # Functions
    CALL_FUNC = 0x20
    DEFINE_FUNC = 0x21
    RETURN = 0x22
    
    # Control Flow
    JUMP = 0x30
    JUMP_IF_FALSE = 0x31
    JUMP_IF_TRUE = 0x32
    LOOP = 0x33
    BREAK = 0x34
    CONTINUE = 0x35
    
    # Operators
    ADD = 0x40
    SUB = 0x41
    MUL = 0x42
    DIV = 0x43
    MOD = 0x44
    POW = 0x45
    
    # Comparisons
    EQ = 0x50
    NE = 0x51
    LT = 0x52
    LE = 0x53
    GT = 0x54
    GE = 0x55
    
    # Logical
    AND = 0x60
    OR = 0x61
    NOT = 0x62
    
    # Data Structures
    BUILD_ARRAY = 0x70
    BUILD_DICT = 0x71
    INDEX = 0x72
    ATTR = 0x73
    
    # AI-Native Operations (v2)
    PERSONALITY = 0x80
    KNOWLEDGE_QUERY = 0x81
    VOICE_SAY = 0x82
    VOICE_LISTEN = 0x83
    OPTIMIZE_SELF = 0x84
    LOAD_MODEL = 0x85
    EMOTION = 0x86
    CONFIDENCE = 0x87
    
    # Tensor Operations
    TENSOR_CREATE = 0x90
    TENSOR_ADD = 0x91
    TENSOR_MUL = 0x92
    TENSOR_MATMUL = 0x93
    TENSOR_RELU = 0x94
    TENSOR_SIGMOID = 0x95
    TENSOR_SOFTMAX = 0x96
    
    # Neural Network
    NN_LINEAR = 0xA0
    NN_CONV2D = 0xA1
    NN_SEQUENTIAL = 0xA2
    NN_FORWARD = 0xA3
    NN_BACKWARD = 0xA4
    
    # Special
    NOP = 0xFF


class BinaryCompiler:
    """
    Compiles NexusLang AST to binary .nxb format.
    
    .nxb File Format:
    - Header (32 bytes):
        - Magic number: "NXB2" (4 bytes)
        - Version: major.minor.patch (3 bytes)
        - Flags: (1 byte)
        - Timestamp: (8 bytes)
        - Code size: (4 bytes)
        - Data size: (4 bytes)
        - Symbol table size: (4 bytes)
        - Reserved: (4 bytes)
    - Code section: bytecode
    - Data section: constants pool
    - Symbol table: variable names and offsets
    - Metadata: JSON
    """
    
    MAGIC = b'NXB2'
    VERSION = (2, 0, 0)  # v2.0.0
    
    def __init__(self):
        self.bytecode = BytesIO()
        self.constants = []
        self.constant_map = {}
        self.symbols = {}
        self.symbol_counter = 0
        
    def compile(self, ast: List[ASTNode], metadata: Optional[Dict] = None) -> bytes:
        """
        Compile AST to binary format.
        Returns complete .nxb file as bytes.
        """
        # Generate bytecode
        for node in ast:
            self.visit(node)
        
        # Build data section (constants pool)
        data_section = self._build_data_section()
        
        # Build symbol table
        symbol_section = self._build_symbol_section()
        
        # Build metadata
        meta_section = self._build_metadata_section(metadata or {})
        
        # Get bytecode
        code_section = self.bytecode.getvalue()
        
        # Build header
        header = self._build_header(
            len(code_section),
            len(data_section),
            len(symbol_section)
        )
        
        # Combine all sections
        result = header + code_section + data_section + symbol_section + meta_section
        
        return result
    
    def _build_header(self, code_size: int, data_size: int, symbol_size: int) -> bytes:
        """
        Build 32-byte header.
        """
        import time
        
        header = BytesIO()
        header.write(self.MAGIC)  # Magic number (4 bytes)
        header.write(struct.pack('BBB', *self.VERSION))  # Version (3 bytes)
        header.write(struct.pack('B', 0))  # Flags (1 byte)
        header.write(struct.pack('Q', int(time.time())))  # Timestamp (8 bytes)
        header.write(struct.pack('I', code_size))  # Code size (4 bytes)
        header.write(struct.pack('I', data_size))  # Data size (4 bytes)
        header.write(struct.pack('I', symbol_size))  # Symbol table size (4 bytes)
        header.write(struct.pack('I', 0))  # Reserved (4 bytes)
        
        return header.getvalue()
    
    def _build_data_section(self) -> bytes:
        """
        Build data section containing constants pool.
        """
        data = BytesIO()
        
        # Write number of constants
        data.write(struct.pack('I', len(self.constants)))
        
        # Write each constant
        for const in self.constants:
            if isinstance(const, int):
                data.write(struct.pack('B', 1))  # Type: int
                data.write(struct.pack('q', const))  # Value (8 bytes)
            elif isinstance(const, float):
                data.write(struct.pack('B', 2))  # Type: float
                data.write(struct.pack('d', const))  # Value (8 bytes)
            elif isinstance(const, str):
                data.write(struct.pack('B', 3))  # Type: string
                encoded = const.encode('utf-8')
                data.write(struct.pack('I', len(encoded)))  # Length
                data.write(encoded)  # Value
            elif isinstance(const, bool):
                data.write(struct.pack('B', 4))  # Type: bool
                data.write(struct.pack('?', const))  # Value (1 byte)
            elif const is None:
                data.write(struct.pack('B', 0))  # Type: null
        
        return data.getvalue()
    
    def _build_symbol_section(self) -> bytes:
        """
        Build symbol table section.
        Maps variable names to their IDs.
        """
        symbol_data = BytesIO()
        
        # Write number of symbols
        symbol_data.write(struct.pack('I', len(self.symbols)))
        
        # Write each symbol
        for name, symbol_id in self.symbols.items():
            encoded_name = name.encode('utf-8')
            symbol_data.write(struct.pack('I', len(encoded_name)))
            symbol_data.write(encoded_name)
            symbol_data.write(struct.pack('I', symbol_id))
        
        return symbol_data.getvalue()
    
    def _build_metadata_section(self, metadata: Dict) -> bytes:
        """
        Build metadata section (JSON).
        """
        meta_json = json.dumps(metadata).encode('utf-8')
        meta_data = BytesIO()
        meta_data.write(struct.pack('I', len(meta_json)))
        meta_data.write(meta_json)
        return meta_data.getvalue()
    
    def add_constant(self, value: Any) -> int:
        """
        Add a constant to the pool and return its index.
        Reuses existing constants.
        """
        if value in self.constant_map:
            return self.constant_map[value]
        
        index = len(self.constants)
        self.constants.append(value)
        self.constant_map[value] = index
        return index
    
    def add_symbol(self, name: str) -> int:
        """
        Add a symbol to the table and return its ID.
        """
        if name in self.symbols:
            return self.symbols[name]
        
        symbol_id = self.symbol_counter
        self.symbols[name] = symbol_id
        self.symbol_counter += 1
        return symbol_id
    
    def emit(self, opcode: OpCode, *args):
        """
        Emit a bytecode instruction.
        """
        self.bytecode.write(struct.pack('B', opcode))
        
        for arg in args:
            if isinstance(arg, int):
                # Use variable-length encoding for efficiency
                if arg < 256:
                    self.bytecode.write(struct.pack('B', arg))
                else:
                    self.bytecode.write(struct.pack('I', arg))
            elif isinstance(arg, bytes):
                self.bytecode.write(arg)
    
    def visit(self, node: ASTNode):
        """
        Visit an AST node and generate bytecode.
        Dispatches to specific visit methods.
        """
        method_name = f'visit_{node.__class__.__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)
    
    def generic_visit(self, node: ASTNode):
        """
        Default visitor for unhandled nodes.
        """
        raise NotImplementedError(f"No visitor for {node.__class__.__name__}")
    
    # Visitor methods for AI-native nodes
    
    def visit_PersonalityBlock(self, node: PersonalityBlock):
        """
        Compile personality block to bytecode.
        """
        self.emit(OpCode.PERSONALITY)
        
        # Encode traits as a dictionary
        self.emit(OpCode.BUILD_DICT)
        self.bytecode.write(struct.pack('B', len(node.traits)))
        
        for key, value in node.traits.items():
            # Key
            key_idx = self.add_constant(key)
            self.emit(OpCode.LOAD_STRING, key_idx)
            
            # Value
            value_idx = self.add_constant(value)
            self.emit(OpCode.LOAD_FLOAT, value_idx)
    
    def visit_KnowledgeQuery(self, node: KnowledgeQuery):
        """
        Compile knowledge query to bytecode.
        """
        # Load query string
        query_idx = self.add_constant(node.query)
        self.emit(OpCode.LOAD_STRING, query_idx)
        
        # Execute knowledge query
        self.emit(OpCode.KNOWLEDGE_QUERY)
    
    def visit_SayStatement(self, node: SayStatement):
        """
        Compile say statement to bytecode.
        """
        # Load text
        text_idx = self.add_constant(node.text)
        self.emit(OpCode.LOAD_STRING, text_idx)
        
        # Load options (emotion, voice_id, speed)
        if node.emotion:
            emotion_idx = self.add_constant(node.emotion)
            self.emit(OpCode.LOAD_STRING, emotion_idx)
        else:
            self.emit(OpCode.LOAD_NULL)
        
        # Execute say
        self.emit(OpCode.VOICE_SAY)
    
    def visit_ListenExpression(self, node: ListenExpression):
        """
        Compile listen expression to bytecode.
        """
        # Load timeout
        if node.timeout:
            timeout_idx = self.add_constant(node.timeout)
            self.emit(OpCode.LOAD_INT, timeout_idx)
        else:
            self.emit(OpCode.LOAD_NULL)
        
        # Execute listen
        self.emit(OpCode.VOICE_LISTEN)
    
    def visit_OptimizeSelfStatement(self, node: OptimizeSelfStatement):
        """
        Compile optimize_self statement to bytecode.
        """
        # Load metric
        metric_idx = self.add_constant(node.metric)
        self.emit(OpCode.LOAD_STRING, metric_idx)
        
        # Load target
        if node.target:
            target_idx = self.add_constant(node.target)
            self.emit(OpCode.LOAD_FLOAT, target_idx)
        else:
            self.emit(OpCode.LOAD_NULL)
        
        # Execute optimize_self
        self.emit(OpCode.OPTIMIZE_SELF)
    
    # Visitor methods for standard AST nodes
    
    def visit_Program(self, node):
        """Compile a program (list of statements)"""
        for stmt in node.statements:
            self.visit(stmt)
    
    def visit_IntegerLiteral(self, node):
        """Compile integer literal"""
        const_idx = self.add_constant(node.value)
        self.emit(OpCode.LOAD_INT, const_idx)
    
    def visit_FloatLiteral(self, node):
        """Compile float literal"""
        const_idx = self.add_constant(node.value)
        self.emit(OpCode.LOAD_FLOAT, const_idx)
    
    def visit_StringLiteral(self, node):
        """Compile string literal"""
        const_idx = self.add_constant(node.value)
        self.emit(OpCode.LOAD_STRING, const_idx)
    
    def visit_BooleanLiteral(self, node):
        """Compile boolean literal"""
        if node.value:
            self.emit(OpCode.LOAD_TRUE)
        else:
            self.emit(OpCode.LOAD_FALSE)
    
    def visit_Identifier(self, node):
        """Compile identifier (variable load)"""
        symbol_id = self.add_symbol(node.name)
        self.emit(OpCode.LOAD_VAR, symbol_id)
    
    def visit_BinaryOp(self, node):
        """Compile binary operation"""
        # Compile operands
        self.visit(node.left)
        self.visit(node.right)
        
        # Emit operator
        op_map = {
            '+': OpCode.ADD,
            '-': OpCode.SUB,
            '*': OpCode.MUL,
            '/': OpCode.DIV,
            '%': OpCode.MOD,
            '==': OpCode.EQ,
            '!=': OpCode.NE,
            '<': OpCode.LT,
            '<=': OpCode.LE,
            '>': OpCode.GT,
            '>=': OpCode.GE,
            '&&': OpCode.AND,
            '||': OpCode.OR,
        }
        
        if node.operator in op_map:
            self.emit(op_map[node.operator])
        else:
            raise NotImplementedError(f"Binary operator {node.operator} not implemented")
    
    def visit_UnaryOp(self, node):
        """Compile unary operation"""
        self.visit(node.operand)
        
        if node.operator == '-':
            # Negate
            self.emit(OpCode.LOAD_INT, self.add_constant(-1))
            self.emit(OpCode.MUL)
        elif node.operator == '!':
            self.emit(OpCode.NOT)
        else:
            raise NotImplementedError(f"Unary operator {node.operator} not implemented")
    
    def visit_VariableDeclaration(self, node):
        """Compile variable declaration"""
        if node.value:
            self.visit(node.value)
        else:
            self.emit(OpCode.LOAD_NULL)
        
        symbol_id = self.add_symbol(node.name)
        self.emit(OpCode.STORE_VAR, symbol_id)
    
    def visit_Assignment(self, node):
        """Compile assignment"""
        self.visit(node.value)
        symbol_id = self.add_symbol(node.target.name)
        self.emit(OpCode.STORE_VAR, symbol_id)
    
    def visit_FunctionCall(self, node):
        """Compile function call"""
        # Load function
        if hasattr(node.function, 'name'):
            self.visit(node.function)
        
        # Load arguments
        for arg in node.arguments:
            self.visit(arg)
        
        # Call with argument count
        self.emit(OpCode.CALL_FUNC, len(node.arguments))
    
    def visit_ReturnStatement(self, node):
        """Compile return statement"""
        if node.value:
            self.visit(node.value)
        else:
            self.emit(OpCode.LOAD_NULL)
        self.emit(OpCode.RETURN)
    
    def visit_ArrayLiteral(self, node):
        """Compile array literal"""
        for elem in node.elements:
            self.visit(elem)
        self.emit(OpCode.BUILD_ARRAY, len(node.elements))
    
    def visit_IndexAccess(self, node):
        """Compile array index access"""
        self.visit(node.object)
        self.visit(node.index)
        self.emit(OpCode.INDEX)


def compile_to_binary(source_code: str, output_path: str) -> bool:
    """
    Convenience function to compile .nx file to .nxb file.
    
    Args:
        source_code: NexusLang source code
        output_path: Path to output .nxb file
    
    Returns:
        True if compilation succeeded
    """
    from ..lexer.lexer import Lexer
    from ..parser.parser import Parser
    
    try:
        # Lex and parse
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        
        parser = Parser(tokens)
        ast = parser.parse()
        
        # Compile to binary
        compiler = BinaryCompiler()
        binary = compiler.compile(ast, metadata={
            'source_file': output_path.replace('.nxb', '.nx'),
            'compiler_version': '2.0.0'
        })
        
        # Write to file
        with open(output_path, 'wb') as f:
            f.write(binary)
        
        print(f"✅ Compiled to {output_path} ({len(binary)} bytes)")
        print(f"   Compression ratio: {len(source_code) / len(binary):.2f}x")
        
        return True
    
    except Exception as e:
        print(f"❌ Compilation failed: {e}")
        return False


def decompile_binary(binary_path: str) -> Dict[str, Any]:
    """
    Read and parse a .nxb binary file.
    Returns header info, bytecode, and metadata.
    """
    with open(binary_path, 'rb') as f:
        data = f.read()
    
    # Verify magic number
    if data[:4] != BinaryCompiler.MAGIC:
        raise ValueError("Invalid .nxb file: wrong magic number")
    
    # Parse header
    version = struct.unpack('BBB', data[4:7])
    flags = struct.unpack('B', data[7:8])[0]
    timestamp = struct.unpack('Q', data[8:16])[0]
    code_size = struct.unpack('I', data[16:20])[0]
    data_size = struct.unpack('I', data[20:24])[0]
    symbol_size = struct.unpack('I', data[24:28])[0]
    
    # Extract sections
    offset = 32
    code_section = data[offset:offset + code_size]
    offset += code_size
    
    data_section = data[offset:offset + data_size]
    offset += data_size
    
    symbol_section = data[offset:offset + symbol_size]
    offset += symbol_size
    
    # Read metadata size and content
    meta_size = struct.unpack('I', data[offset:offset + 4])[0]
    offset += 4
    metadata = json.loads(data[offset:offset + meta_size].decode('utf-8'))
    
    return {
        'version': version,
        'flags': flags,
        'timestamp': timestamp,
        'code_size': code_size,
        'data_size': data_size,
        'symbol_size': symbol_size,
        'bytecode': code_section,
        'metadata': metadata
    }

