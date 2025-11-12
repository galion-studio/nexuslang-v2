"""Parser for NexusLang - converts tokens into AST"""

from typing import List, Optional
from ..lexer.token import Token, TokenType
from ..syntax_tree.nodes import *
from ..syntax_tree.ai_nodes import (
    PersonalityBlock, KnowledgeQuery, VoiceBlock, 
    SayStatement, ListenExpression, OptimizeSelfStatement,
    LoadModelExpression, EmotionExpression, ConfidenceExpression
)


class ParseError(Exception):
    """Raised when parser encounters an error"""
    pass


class Parser:
    """Recursive descent parser for NexusLang"""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = [t for t in tokens if t.type != TokenType.NEWLINE]  # Skip newlines
        self.pos = 0
    
    def current_token(self) -> Token:
        """Get current token"""
        if self.pos >= len(self.tokens):
            return self.tokens[-1]  # Return EOF
        return self.tokens[self.pos]
    
    def peek_token(self, offset: int = 1) -> Token:
        """Peek ahead at token"""
        pos = self.pos + offset
        if pos >= len(self.tokens):
            return self.tokens[-1]  # Return EOF
        return self.tokens[pos]
    
    def advance(self) -> Token:
        """Move to next token"""
        token = self.current_token()
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return token
    
    def expect(self, token_type: TokenType) -> Token:
        """Expect a specific token type"""
        token = self.current_token()
        if token.type != token_type:
            raise ParseError(
                f"Expected {token_type.name}, got {token.type.name} at {token.line}:{token.column}"
            )
        return self.advance()
    
    def match(self, *token_types: TokenType) -> bool:
        """Check if current token matches any of the given types"""
        return self.current_token().type in token_types
    
    def parse(self) -> Program:
        """Parse tokens into AST"""
        statements = []
        
        while not self.match(TokenType.EOF):
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        
        return Program(statements)
    
    def parse_statement(self) -> Optional[ASTNode]:
        """Parse a single statement"""
        # Import statement
        if self.match(TokenType.IMPORT, TokenType.FROM):
            return self.parse_import()
        
        # Variable declaration
        if self.match(TokenType.LET, TokenType.CONST):
            return self.parse_variable_declaration()
        
        # Function declaration
        if self.match(TokenType.FN):
            return self.parse_function_declaration()
        
        # Struct declaration
        if self.match(TokenType.STRUCT):
            return self.parse_struct_declaration()
        
        # AI-Native v2: Personality block
        if self.match(TokenType.PERSONALITY):
            return self.parse_personality_block()
        
        # AI-Native v2: Voice block
        if self.match(TokenType.VOICE):
            return self.parse_voice_block()
        
        # Control flow
        if self.match(TokenType.IF):
            return self.parse_if_statement()
        
        if self.match(TokenType.WHILE):
            return self.parse_while_statement()
        
        if self.match(TokenType.FOR):
            return self.parse_for_statement()
        
        if self.match(TokenType.RETURN):
            return self.parse_return_statement()
        
        if self.match(TokenType.BREAK):
            self.advance()
            return BreakStatement()
        
        if self.match(TokenType.CONTINUE):
            self.advance()
            return ContinueStatement()
        
        # Expression statement or assignment
        expr = self.parse_expression()
        
        # Check for assignment
        if self.match(TokenType.EQUAL):
            if isinstance(expr, Identifier):
                self.advance()  # =
                value = self.parse_expression()
                return Assignment(expr, value)
            else:
                raise ParseError("Invalid assignment target")
        
        return expr
    
    def parse_import(self) -> ImportStatement:
        """Parse import statement"""
        if self.match(TokenType.FROM):
            self.advance()
            module = self.expect(TokenType.IDENTIFIER).value
            self.expect(TokenType.IMPORT)
            
            items = []
            items.append(self.expect(TokenType.IDENTIFIER).value)
            
            while self.match(TokenType.COMMA):
                self.advance()
                items.append(self.expect(TokenType.IDENTIFIER).value)
            
            return ImportStatement(module, items)
        else:
            self.advance()  # import
            module = self.expect(TokenType.IDENTIFIER).value
            
            # Handle dotted imports (e.g., nexus.core)
            while self.match(TokenType.DOT):
                self.advance()
                module += "." + self.expect(TokenType.IDENTIFIER).value
            
            return ImportStatement(module)
    
    def parse_variable_declaration(self) -> VariableDeclaration:
        """Parse let/const declaration"""
        is_const = self.current_token().type == TokenType.CONST
        self.advance()  # let or const
        
        name = self.expect(TokenType.IDENTIFIER).value
        
        # Optional type annotation
        type_annotation = None
        if self.match(TokenType.COLON):
            self.advance()
            type_annotation = self.expect(TokenType.IDENTIFIER).value
        
        # Optional initialization
        value = None
        if self.match(TokenType.EQUAL):
            self.advance()
            value = self.parse_expression()
        
        return VariableDeclaration(name, type_annotation, value, is_const)
    
    def parse_function_declaration(self) -> FunctionDeclaration:
        """Parse function declaration"""
        self.advance()  # fn
        
        name = self.expect(TokenType.IDENTIFIER).value
        
        self.expect(TokenType.LPAREN)
        
        # Parse parameters
        parameters = []
        if not self.match(TokenType.RPAREN):
            parameters.append(self.parse_parameter())
            
            while self.match(TokenType.COMMA):
                self.advance()
                parameters.append(self.parse_parameter())
        
        self.expect(TokenType.RPAREN)
        
        # Optional return type
        return_type = None
        if self.match(TokenType.ARROW):
            self.advance()
            return_type = self.expect(TokenType.IDENTIFIER).value
        
        # Function body
        body = self.parse_block()
        
        return FunctionDeclaration(name, parameters, return_type, body)
    
    def parse_parameter(self) -> Parameter:
        """Parse function parameter"""
        name = self.expect(TokenType.IDENTIFIER).value
        
        type_annotation = None
        if self.match(TokenType.COLON):
            self.advance()
            type_annotation = self.expect(TokenType.IDENTIFIER).value
        
        return Parameter(name, type_annotation)
    
    def parse_struct_declaration(self) -> StructDeclaration:
        """Parse struct declaration"""
        self.advance()  # struct
        
        name = self.expect(TokenType.IDENTIFIER).value
        
        self.expect(TokenType.LBRACE)
        
        fields = []
        while not self.match(TokenType.RBRACE):
            field_name = self.expect(TokenType.IDENTIFIER).value
            self.expect(TokenType.COLON)
            field_type = self.expect(TokenType.IDENTIFIER).value
            
            fields.append(StructField(field_name, field_type))
            
            # Optional comma
            if self.match(TokenType.COMMA):
                self.advance()
        
        self.expect(TokenType.RBRACE)
        
        return StructDeclaration(name, fields)
    
    def parse_if_statement(self) -> IfStatement:
        """Parse if statement"""
        self.advance()  # if
        
        condition = self.parse_expression()
        then_block = self.parse_block()
        
        else_block = None
        if self.match(TokenType.ELSE):
            self.advance()
            else_block = self.parse_block()
        
        return IfStatement(condition, then_block, else_block)
    
    def parse_while_statement(self) -> WhileStatement:
        """Parse while loop"""
        self.advance()  # while
        
        condition = self.parse_expression()
        body = self.parse_block()
        
        return WhileStatement(condition, body)
    
    def parse_for_statement(self) -> ForStatement:
        """Parse for loop"""
        self.advance()  # for
        
        variable = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.IN)
        iterable = self.parse_expression()
        body = self.parse_block()
        
        return ForStatement(variable, iterable, body)
    
    def parse_return_statement(self) -> ReturnStatement:
        """Parse return statement"""
        self.advance()  # return
        
        value = None
        if not self.match(TokenType.RBRACE, TokenType.EOF):
            value = self.parse_expression()
        
        return ReturnStatement(value)
    
    def parse_block(self) -> Block:
        """Parse block of statements"""
        self.expect(TokenType.LBRACE)
        
        statements = []
        while not self.match(TokenType.RBRACE):
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        
        self.expect(TokenType.RBRACE)
        
        return Block(statements)
    
    def parse_expression(self) -> ASTNode:
        """Parse expression (entry point for expression parsing)"""
        return self.parse_logical_or()
    
    def parse_logical_or(self) -> ASTNode:
        """Parse logical OR expression"""
        left = self.parse_logical_and()
        
        while self.match(TokenType.OR):
            op = self.advance().value
            right = self.parse_logical_and()
            left = BinaryOp(left, op, right)
        
        return left
    
    def parse_logical_and(self) -> ASTNode:
        """Parse logical AND expression"""
        left = self.parse_equality()
        
        while self.match(TokenType.AND):
            op = self.advance().value
            right = self.parse_equality()
            left = BinaryOp(left, op, right)
        
        return left
    
    def parse_equality(self) -> ASTNode:
        """Parse equality expression"""
        left = self.parse_comparison()
        
        while self.match(TokenType.EQ, TokenType.NE):
            op = self.advance().value
            right = self.parse_comparison()
            left = BinaryOp(left, op, right)
        
        return left
    
    def parse_comparison(self) -> ASTNode:
        """Parse comparison expression"""
        left = self.parse_range()
        
        while self.match(TokenType.LT, TokenType.LE, TokenType.GT, TokenType.GE):
            op = self.advance().value
            right = self.parse_range()
            left = BinaryOp(left, op, right)
        
        return left
    
    def parse_range(self) -> ASTNode:
        """Parse range expression (e.g., 0..10)"""
        left = self.parse_additive()
        
        if self.match(TokenType.DOUBLE_DOT):
            op = self.advance().value
            right = self.parse_additive()
            return BinaryOp(left, op, right)
        
        return left
    
    def parse_additive(self) -> ASTNode:
        """Parse addition/subtraction"""
        left = self.parse_multiplicative()
        
        while self.match(TokenType.PLUS, TokenType.MINUS):
            op = self.advance().value
            right = self.parse_multiplicative()
            left = BinaryOp(left, op, right)
        
        return left
    
    def parse_multiplicative(self) -> ASTNode:
        """Parse multiplication/division/modulo"""
        left = self.parse_unary()
        
        while self.match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            op = self.advance().value
            right = self.parse_unary()
            left = BinaryOp(left, op, right)
        
        return left
    
    def parse_unary(self) -> ASTNode:
        """Parse unary expression"""
        if self.match(TokenType.MINUS, TokenType.NOT):
            op = self.advance().value
            operand = self.parse_unary()
            return UnaryOp(op, operand)
        
        return self.parse_postfix()
    
    def parse_postfix(self) -> ASTNode:
        """Parse postfix expression (function calls, array access, member access)"""
        expr = self.parse_primary()
        
        while True:
            # Function call
            if self.match(TokenType.LPAREN):
                self.advance()
                arguments = []
                
                if not self.match(TokenType.RPAREN):
                    arguments.append(self.parse_expression())
                    
                    while self.match(TokenType.COMMA):
                        self.advance()
                        arguments.append(self.parse_expression())
                
                self.expect(TokenType.RPAREN)
                expr = FunctionCall(expr, arguments)
            
            # Array index access
            elif self.match(TokenType.LBRACKET):
                self.advance()
                index = self.parse_expression()
                self.expect(TokenType.RBRACKET)
                expr = IndexAccess(expr, index)
            
            # Member access
            elif self.match(TokenType.DOT):
                self.advance()
                member = self.expect(TokenType.IDENTIFIER).value
                expr = MemberAccess(expr, member)
            
            else:
                break
        
        return expr
    
    def parse_primary(self) -> ASTNode:
        """Parse primary expression (literals, identifiers, parenthesized expressions)"""
        token = self.current_token()
        
        # Integer literal
        if token.type == TokenType.INTEGER:
            self.advance()
            return IntegerLiteral(token.value)
        
        # Float literal
        if token.type == TokenType.FLOAT:
            self.advance()
            return FloatLiteral(token.value)
        
        # String literal
        if token.type == TokenType.STRING:
            self.advance()
            return StringLiteral(token.value)
        
        # Boolean literals
        if token.type in (TokenType.TRUE, TokenType.FALSE):
            self.advance()
            return BooleanLiteral(token.value)
        
        # Identifier
        if token.type == TokenType.IDENTIFIER:
            self.advance()
            return Identifier(token.value)
        
        # Parenthesized expression
        if token.type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return expr
        
        # Array literal
        if token.type == TokenType.LBRACKET:
            self.advance()
            elements = []
            
            if not self.match(TokenType.RBRACKET):
                elements.append(self.parse_expression())
                
                while self.match(TokenType.COMMA):
                    self.advance()
                    if self.match(TokenType.RBRACKET):  # Trailing comma
                        break
                    elements.append(self.parse_expression())
            
            self.expect(TokenType.RBRACKET)
            return ArrayLiteral(elements)
        
        # AI-Native v2: Special function-like keywords
        if token.type == TokenType.SAY:
            return self.parse_say_statement()
        
        if token.type == TokenType.LISTEN:
            return self.parse_listen_expression()
        
        if token.type == TokenType.KNOWLEDGE:
            return self.parse_knowledge_query()
        
        if token.type == TokenType.LOAD_MODEL:
            return self.parse_load_model()
        
        if token.type == TokenType.EMOTION:
            return self.parse_emotion()
        
        if token.type == TokenType.CONFIDENCE:
            return self.parse_confidence()
        
        if token.type == TokenType.OPTIMIZE_SELF:
            return self.parse_optimize_self()
        
        raise ParseError(
            f"Unexpected token {token.type.name} at {token.line}:{token.column}"
        )
    
    # ====== NexusLang v2 AI-Native Parsing Methods ======
    
    def parse_personality_block(self) -> PersonalityBlock:
        """
        Parse personality block.
        
        Syntax:
            personality {
                curiosity: 0.9,
                analytical: 0.8,
                creative: 0.7
            }
        """
        self.advance()  # personality
        self.expect(TokenType.LBRACE)
        
        traits = {}
        
        while not self.match(TokenType.RBRACE):
            # Parse trait name (identifier or keyword)
            trait_name_token = self.current_token()
            
            # Accept both identifiers and trait keywords
            if trait_name_token.type == TokenType.IDENTIFIER:
                trait_name = self.advance().value
            elif trait_name_token.type in (
                TokenType.CURIOSITY, TokenType.ANALYTICAL, 
                TokenType.CREATIVE, TokenType.EMPATHETIC,
                TokenType.CONFIDENCE
            ):
                trait_name = self.advance().value if hasattr(self.advance(), 'value') else trait_name_token.type.name.lower()
                # Go back and advance properly
                self.pos -= 1
                trait_name = self.advance().type.name.lower()
            else:
                trait_name = self.expect(TokenType.IDENTIFIER).value
            
            self.expect(TokenType.COLON)
            
            # Parse trait value (must be a number between 0 and 1)
            value_token = self.current_token()
            if value_token.type == TokenType.FLOAT:
                trait_value = self.advance().value
            elif value_token.type == TokenType.INTEGER:
                trait_value = float(self.advance().value)
            else:
                raise ParseError(f"Expected number for trait value at {value_token.line}:{value_token.column}")
            
            # Validate range
            if not 0.0 <= trait_value <= 1.0:
                raise ParseError(f"Personality trait value must be between 0.0 and 1.0, got {trait_value}")
            
            traits[trait_name] = trait_value
            
            # Optional comma
            if self.match(TokenType.COMMA):
                self.advance()
        
        self.expect(TokenType.RBRACE)
        
        return PersonalityBlock(traits=traits)
    
    def parse_voice_block(self) -> VoiceBlock:
        """
        Parse voice block.
        
        Syntax:
            voice {
                say("Hello")
                let response = listen()
            }
        """
        self.advance()  # voice
        body = self.parse_block()
        
        return VoiceBlock(body=body.statements if hasattr(body, 'statements') else [body])
    
    def parse_say_statement(self) -> SayStatement:
        """
        Parse say statement.
        
        Syntax:
            say("Hello world")
            say("Excited!", emotion="excited")
            say("Fast speech", speed=1.5)
        """
        self.advance()  # say
        self.expect(TokenType.LPAREN)
        
        # First argument: text (required)
        text_expr = self.parse_expression()
        if not isinstance(text_expr, StringLiteral):
            raise ParseError("say() first argument must be a string literal")
        text = text_expr.value
        
        # Optional named arguments
        emotion = None
        voice_id = None
        speed = 1.0
        
        while self.match(TokenType.COMMA):
            self.advance()
            
            # Parse named argument
            if self.match(TokenType.IDENTIFIER):
                arg_name = self.advance().value
                self.expect(TokenType.EQUAL)
                arg_value = self.parse_expression()
                
                if arg_name == "emotion" and isinstance(arg_value, StringLiteral):
                    emotion = arg_value.value
                elif arg_name == "voice_id" and isinstance(arg_value, StringLiteral):
                    voice_id = arg_value.value
                elif arg_name == "speed" and isinstance(arg_value, (IntegerLiteral, FloatLiteral)):
                    speed = float(arg_value.value)
        
        self.expect(TokenType.RPAREN)
        
        return SayStatement(text=text, emotion=emotion, voice_id=voice_id, speed=speed)
    
    def parse_listen_expression(self) -> ListenExpression:
        """
        Parse listen expression.
        
        Syntax:
            listen()
            listen(timeout=10)
            listen(timeout=5, language="en")
        """
        self.advance()  # listen
        self.expect(TokenType.LPAREN)
        
        timeout = None
        language = "en"
        
        if not self.match(TokenType.RPAREN):
            # Parse named arguments
            while True:
                if self.match(TokenType.IDENTIFIER):
                    arg_name = self.advance().value
                    self.expect(TokenType.EQUAL)
                    arg_value = self.parse_expression()
                    
                    if arg_name == "timeout" and isinstance(arg_value, IntegerLiteral):
                        timeout = arg_value.value
                    elif arg_name == "language" and isinstance(arg_value, StringLiteral):
                        language = arg_value.value
                
                if not self.match(TokenType.COMMA):
                    break
                self.advance()
        
        self.expect(TokenType.RPAREN)
        
        return ListenExpression(timeout=timeout, language=language)
    
    def parse_knowledge_query(self) -> KnowledgeQuery:
        """
        Parse knowledge query.
        
        Syntax:
            knowledge("quantum physics")
            knowledge("AI", verified=true, limit=10)
        """
        self.advance()  # knowledge
        self.expect(TokenType.LPAREN)
        
        # First argument: query string (required)
        query_expr = self.parse_expression()
        if not isinstance(query_expr, StringLiteral):
            raise ParseError("knowledge() first argument must be a string")
        query = query_expr.value
        
        # Optional filters as named arguments
        filters = {}
        
        while self.match(TokenType.COMMA):
            self.advance()
            
            if self.match(TokenType.IDENTIFIER):
                filter_name = self.advance().value
                self.expect(TokenType.EQUAL)
                filter_value = self.parse_expression()
                
                # Convert to Python value
                if isinstance(filter_value, StringLiteral):
                    filters[filter_name] = filter_value.value
                elif isinstance(filter_value, (IntegerLiteral, FloatLiteral)):
                    filters[filter_name] = filter_value.value
                elif isinstance(filter_value, BooleanLiteral):
                    filters[filter_name] = filter_value.value
        
        self.expect(TokenType.RPAREN)
        
        return KnowledgeQuery(query=query, filters=filters if filters else None)
    
    def parse_load_model(self) -> LoadModelExpression:
        """
        Parse load_model expression.
        
        Syntax:
            load_model("gpt-4")
            load_model("./my_model.nxb", config={...})
        """
        self.advance()  # load_model
        self.expect(TokenType.LPAREN)
        
        model_name_expr = self.parse_expression()
        if not isinstance(model_name_expr, StringLiteral):
            raise ParseError("load_model() requires a string argument")
        model_name = model_name_expr.value
        
        config = None
        # TODO: Parse optional config dict
        
        self.expect(TokenType.RPAREN)
        
        return LoadModelExpression(model_name=model_name, config=config)
    
    def parse_emotion(self) -> EmotionExpression:
        """
        Parse emotion expression.
        
        Syntax:
            emotion()  // get current emotion
            emotion("happy", intensity=0.8)  // set emotion
        """
        self.advance()  # emotion
        self.expect(TokenType.LPAREN)
        
        emotion_type = None
        intensity = 1.0
        
        if not self.match(TokenType.RPAREN):
            # First argument: emotion type
            emotion_expr = self.parse_expression()
            if isinstance(emotion_expr, StringLiteral):
                emotion_type = emotion_expr.value
            
            # Optional intensity
            if self.match(TokenType.COMMA):
                self.advance()
                if self.match(TokenType.IDENTIFIER):
                    arg_name = self.advance().value
                    if arg_name == "intensity":
                        self.expect(TokenType.EQUAL)
                        intensity_expr = self.parse_expression()
                        if isinstance(intensity_expr, (IntegerLiteral, FloatLiteral)):
                            intensity = float(intensity_expr.value)
        
        self.expect(TokenType.RPAREN)
        
        return EmotionExpression(emotion_type=emotion_type, intensity=intensity)
    
    def parse_confidence(self) -> ConfidenceExpression:
        """
        Parse confidence expression.
        
        Syntax:
            confidence(prediction)
            confidence(result, threshold=0.8)
        """
        self.advance()  # confidence
        self.expect(TokenType.LPAREN)
        
        value = None
        threshold = None
        
        if not self.match(TokenType.RPAREN):
            value = self.parse_expression()
            
            if self.match(TokenType.COMMA):
                self.advance()
                if self.match(TokenType.IDENTIFIER):
                    arg_name = self.advance().value
                    if arg_name == "threshold":
                        self.expect(TokenType.EQUAL)
                        threshold_expr = self.parse_expression()
                        if isinstance(threshold_expr, (IntegerLiteral, FloatLiteral)):
                            threshold = float(threshold_expr.value)
        
        self.expect(TokenType.RPAREN)
        
        return ConfidenceExpression(value=value, threshold=threshold)
    
    def parse_optimize_self(self) -> OptimizeSelfStatement:
        """
        Parse optimize_self statement.
        
        Syntax:
            optimize_self(metric="accuracy", target=0.95)
        """
        self.advance()  # optimize_self
        self.expect(TokenType.LPAREN)
        
        metric = None
        target = None
        strategy = None
        
        # Parse named arguments
        while not self.match(TokenType.RPAREN):
            if self.match(TokenType.IDENTIFIER):
                arg_name = self.advance().value
                self.expect(TokenType.EQUAL)
                arg_value = self.parse_expression()
                
                if arg_name == "metric" and isinstance(arg_value, StringLiteral):
                    metric = arg_value.value
                elif arg_name == "target" and isinstance(arg_value, (IntegerLiteral, FloatLiteral)):
                    target = float(arg_value.value)
                elif arg_name == "strategy" and isinstance(arg_value, StringLiteral):
                    strategy = arg_value.value
            
            if self.match(TokenType.COMMA):
                self.advance()
        
        self.expect(TokenType.RPAREN)
        
        if metric is None:
            raise ParseError("optimize_self() requires 'metric' argument")
        
        return OptimizeSelfStatement(metric=metric, target=target, strategy=strategy)

