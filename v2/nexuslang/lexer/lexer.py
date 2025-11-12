"""Lexer for NexusLang - converts source code into tokens"""

from typing import List, Optional
from .token import Token, TokenType, KEYWORDS


class LexerError(Exception):
    """Raised when lexer encounters an error"""
    pass


class Lexer:
    """Tokenizes NexusLang source code"""
    
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
    
    def current_char(self) -> Optional[str]:
        """Get current character without advancing"""
        if self.pos >= len(self.source):
            return None
        return self.source[self.pos]
    
    def peek_char(self, offset: int = 1) -> Optional[str]:
        """Peek ahead at character"""
        pos = self.pos + offset
        if pos >= len(self.source):
            return None
        return self.source[pos]
    
    def advance(self) -> Optional[str]:
        """Move to next character"""
        if self.pos >= len(self.source):
            return None
        
        char = self.source[self.pos]
        self.pos += 1
        
        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        
        return char
    
    def skip_whitespace(self):
        """Skip whitespace except newlines"""
        while self.current_char() and self.current_char() in ' \t\r':
            self.advance()
    
    def skip_line_comment(self):
        """Skip single-line comment //"""
        # Skip the //
        self.advance()
        self.advance()
        
        # Skip until newline
        while self.current_char() and self.current_char() != '\n':
            self.advance()
    
    def skip_block_comment(self):
        """Skip multi-line comment /* */"""
        # Skip the /*
        self.advance()
        self.advance()
        
        # Skip until */
        while self.current_char():
            if self.current_char() == '*' and self.peek_char() == '/':
                self.advance()  # *
                self.advance()  # /
                break
            self.advance()
    
    def read_string(self, quote: str) -> str:
        """Read string literal"""
        value = ""
        self.advance()  # Skip opening quote
        
        while self.current_char() and self.current_char() != quote:
            char = self.current_char()
            
            # Handle escape sequences
            if char == '\\':
                self.advance()
                next_char = self.current_char()
                
                if next_char == 'n':
                    value += '\n'
                elif next_char == 't':
                    value += '\t'
                elif next_char == 'r':
                    value += '\r'
                elif next_char == '\\':
                    value += '\\'
                elif next_char == quote:
                    value += quote
                else:
                    value += next_char
                
                self.advance()
            else:
                value += char
                self.advance()
        
        if self.current_char() != quote:
            raise LexerError(f"Unterminated string at {self.line}:{self.column}")
        
        self.advance()  # Skip closing quote
        return value
    
    def read_number(self) -> Token:
        """Read numeric literal (integer or float)"""
        start_line = self.line
        start_col = self.column
        value = ""
        is_float = False
        
        while self.current_char() and (self.current_char().isdigit() or self.current_char() == '.'):
            if self.current_char() == '.':
                # Check if it's a range operator (..)
                if self.peek_char() == '.':
                    break
                is_float = True
            value += self.current_char()
            self.advance()
        
        if is_float:
            return Token(TokenType.FLOAT, float(value), start_line, start_col)
        else:
            return Token(TokenType.INTEGER, int(value), start_line, start_col)
    
    def read_identifier(self) -> Token:
        """Read identifier or keyword"""
        start_line = self.line
        start_col = self.column
        value = ""
        
        while self.current_char() and (self.current_char().isalnum() or self.current_char() == '_'):
            value += self.current_char()
            self.advance()
        
        # Check if it's a keyword
        token_type = KEYWORDS.get(value, TokenType.IDENTIFIER)
        
        # Handle boolean literals
        if token_type == TokenType.TRUE:
            return Token(token_type, True, start_line, start_col)
        elif token_type == TokenType.FALSE:
            return Token(token_type, False, start_line, start_col)
        
        return Token(token_type, value, start_line, start_col)
    
    def tokenize(self) -> List[Token]:
        """Convert source code into list of tokens"""
        self.tokens = []
        
        while self.current_char():
            self.skip_whitespace()
            
            if not self.current_char():
                break
            
            char = self.current_char()
            line = self.line
            col = self.column
            
            # Comments
            if char == '/' and self.peek_char() == '/':
                self.skip_line_comment()
                continue
            elif char == '/' and self.peek_char() == '*':
                self.skip_block_comment()
                continue
            
            # Newlines
            elif char == '\n':
                self.tokens.append(Token(TokenType.NEWLINE, None, line, col))
                self.advance()
            
            # String literals
            elif char == '"' or char == "'":
                value = self.read_string(char)
                self.tokens.append(Token(TokenType.STRING, value, line, col))
            
            # Numbers
            elif char.isdigit():
                self.tokens.append(self.read_number())
            
            # Identifiers and keywords
            elif char.isalpha() or char == '_':
                self.tokens.append(self.read_identifier())
            
            # Operators and delimiters
            elif char == '+':
                if self.peek_char() == '=':
                    self.advance()
                    self.advance()
                    self.tokens.append(Token(TokenType.PLUS_EQUAL, "+=", line, col))
                else:
                    self.advance()
                    self.tokens.append(Token(TokenType.PLUS, "+", line, col))
            
            elif char == '-':
                if self.peek_char() == '=':
                    self.advance()
                    self.advance()
                    self.tokens.append(Token(TokenType.MINUS_EQUAL, "-=", line, col))
                elif self.peek_char() == '>':
                    self.advance()
                    self.advance()
                    self.tokens.append(Token(TokenType.ARROW, "->", line, col))
                else:
                    self.advance()
                    self.tokens.append(Token(TokenType.MINUS, "-", line, col))
            
            elif char == '*':
                if self.peek_char() == '=':
                    self.advance()
                    self.advance()
                    self.tokens.append(Token(TokenType.STAR_EQUAL, "*=", line, col))
                elif self.peek_char() == '*':
                    self.advance()
                    self.advance()
                    self.tokens.append(Token(TokenType.POWER, "**", line, col))
                else:
                    self.advance()
                    self.tokens.append(Token(TokenType.STAR, "*", line, col))
            
            elif char == '/':
                if self.peek_char() == '=':
                    self.advance()
                    self.advance()
                    self.tokens.append(Token(TokenType.SLASH_EQUAL, "/=", line, col))
                else:
                    self.advance()
                    self.tokens.append(Token(TokenType.SLASH, "/", line, col))
            
            elif char == '%':
                self.advance()
                self.tokens.append(Token(TokenType.PERCENT, "%", line, col))
            
            elif char == '=':
                if self.peek_char() == '=':
                    self.advance()
                    self.advance()
                    self.tokens.append(Token(TokenType.EQ, "==", line, col))
                elif self.peek_char() == '>':
                    self.advance()
                    self.advance()
                    self.tokens.append(Token(TokenType.FAT_ARROW, "=>", line, col))
                else:
                    self.advance()
                    self.tokens.append(Token(TokenType.EQUAL, "=", line, col))
            
            elif char == '!':
                if self.peek_char() == '=':
                    self.advance()
                    self.advance()
                    self.tokens.append(Token(TokenType.NE, "!=", line, col))
                else:
                    self.advance()
                    self.tokens.append(Token(TokenType.NOT, "!", line, col))
            
            elif char == '<':
                if self.peek_char() == '=':
                    self.advance()
                    self.advance()
                    self.tokens.append(Token(TokenType.LE, "<=", line, col))
                elif self.peek_char() == '<':
                    self.advance()
                    self.advance()
                    self.tokens.append(Token(TokenType.LSHIFT, "<<", line, col))
                else:
                    self.advance()
                    self.tokens.append(Token(TokenType.LT, "<", line, col))
            
            elif char == '>':
                if self.peek_char() == '=':
                    self.advance()
                    self.advance()
                    self.tokens.append(Token(TokenType.GE, ">=", line, col))
                elif self.peek_char() == '>':
                    self.advance()
                    self.advance()
                    self.tokens.append(Token(TokenType.RSHIFT, ">>", line, col))
                else:
                    self.advance()
                    self.tokens.append(Token(TokenType.GT, ">", line, col))
            
            elif char == '&':
                if self.peek_char() == '&':
                    self.advance()
                    self.advance()
                    self.tokens.append(Token(TokenType.AND, "&&", line, col))
                else:
                    self.advance()
                    self.tokens.append(Token(TokenType.AMPERSAND, "&", line, col))
            
            elif char == '|':
                if self.peek_char() == '|':
                    self.advance()
                    self.advance()
                    self.tokens.append(Token(TokenType.OR, "||", line, col))
                else:
                    self.advance()
                    self.tokens.append(Token(TokenType.PIPE, "|", line, col))
            
            elif char == '^':
                self.advance()
                self.tokens.append(Token(TokenType.CARET, "^", line, col))
            
            elif char == '~':
                self.advance()
                self.tokens.append(Token(TokenType.TILDE, "~", line, col))
            
            elif char == '@':
                self.advance()
                self.tokens.append(Token(TokenType.AT, "@", line, col))
            
            elif char == '?':
                self.advance()
                self.tokens.append(Token(TokenType.QUESTION, "?", line, col))
            
            elif char == '.':
                if self.peek_char() == '.' and self.peek_char(2) == '.':
                    self.advance()
                    self.advance()
                    self.advance()
                    self.tokens.append(Token(TokenType.TRIPLE_DOT, "...", line, col))
                elif self.peek_char() == '.':
                    self.advance()
                    self.advance()
                    self.tokens.append(Token(TokenType.DOUBLE_DOT, "..", line, col))
                else:
                    self.advance()
                    self.tokens.append(Token(TokenType.DOT, ".", line, col))
            
            elif char == ':':
                if self.peek_char() == ':':
                    self.advance()
                    self.advance()
                    self.tokens.append(Token(TokenType.DOUBLE_COLON, "::", line, col))
                else:
                    self.advance()
                    self.tokens.append(Token(TokenType.COLON, ":", line, col))
            
            elif char == '(':
                self.advance()
                self.tokens.append(Token(TokenType.LPAREN, "(", line, col))
            
            elif char == ')':
                self.advance()
                self.tokens.append(Token(TokenType.RPAREN, ")", line, col))
            
            elif char == '{':
                self.advance()
                self.tokens.append(Token(TokenType.LBRACE, "{", line, col))
            
            elif char == '}':
                self.advance()
                self.tokens.append(Token(TokenType.RBRACE, "}", line, col))
            
            elif char == '[':
                self.advance()
                self.tokens.append(Token(TokenType.LBRACKET, "[", line, col))
            
            elif char == ']':
                self.advance()
                self.tokens.append(Token(TokenType.RBRACKET, "]", line, col))
            
            elif char == ',':
                self.advance()
                self.tokens.append(Token(TokenType.COMMA, ",", line, col))
            
            elif char == ';':
                self.advance()
                self.tokens.append(Token(TokenType.SEMICOLON, ";", line, col))
            
            else:
                raise LexerError(f"Unexpected character '{char}' at {line}:{col}")
        
        # Add EOF token
        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        
        return self.tokens

