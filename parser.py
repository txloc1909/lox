from typing import Optional

from _token import TokenType, Token
from expr import (Expr, BinaryExpr, GroupingExpr, LiteralExpr, UnaryExpr,
                  VarExpr, AssignExpr, LogicalExpr, CallExpr, GetExpr, SetExpr,
                  ThisExpr, SuperExpr)
from stmt import (Stmt, ExpressionStmt, PrintStmt, VarStmt, BlockStmt, IfStmt,
                  WhileStmt, FunctionStmt, ReturnStmt, ClassStmt)
from error_handling import report


class ParserError(RuntimeError):
    def __init__(self, token: Token, message: str):
        super().__init__(message)
        if token.type_ == TokenType.EOF:
            report(token.line, " at end", message)
        else:
            report(token.line, f"at '{token.lexeme}'", message)


class Parser:
    def __init__(self, tokens: list[Token]):
        self._tokens = tokens
        self._current = 0

    def parse(self) -> list[Stmt]:
        statements: list[Stmt] = []

        while not self._at_end():
            stmt = self._declaration()
            if stmt:
                statements.append(stmt)

        return statements

    def _declaration(self) -> Optional[Stmt]:
        try:
            if self._match(TokenType.VAR):
                return self._var_declaration()
            elif self._match(TokenType.CLASS):
                return self._class_declaration()
            elif self._match(TokenType.FUN):
                return self._func_declaration(kind="function")
            else:
                return self._statement()
        except ParserError:
            self._synchronize()
            return None

    def _statement(self) -> Stmt:
        if self._match(TokenType.FOR):
            return self._for_stmt()
        if self._match(TokenType.IF):
            return self._if_stmt()
        elif self._match(TokenType.PRINT):
            return self._print_stmt()
        elif self._match(TokenType.WHILE):
            return self._while_stmt()
        elif self._match(TokenType.LEFT_BRACE):
            return BlockStmt(self._block_stmt())
        elif self._match(TokenType.RETURN):
            return self._return_stmt()
        else:
            return self._expression_stmt()

    def _print_stmt(self) -> PrintStmt:
        value = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return PrintStmt(value)

    def _expression_stmt(self) -> ExpressionStmt:
        expr = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return ExpressionStmt(expr)

    def _var_declaration(self) -> VarStmt:
        name = self._consume(TokenType.IDENTIFIER, "Expect variable name.")
        initializer = self._expression() if self._match(TokenType.EQUAL) else None
        self._consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return VarStmt(name, initializer)

    def _func_declaration(self, kind: str):
        # NOTE: `kind` should take an Enum, instead of str?
        name = self._consume(TokenType.IDENTIFIER, f"Expect {kind} name.")
        self._consume(TokenType.LEFT_PAREN, f"Expect '(' after {kind} name.")
        parameters: list[Token] = []
        if not self._check(TokenType.RIGHT_PAREN):
            while True:
                if len(parameters) >= 255:
                    raise ParserError(self._peek(), "Can't have more than 255 parameters.")

                parameters.append(self._consume(TokenType.IDENTIFIER, "Expect parameter name."))
                if not self._match(TokenType.COMMA):
                    break

        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")
        self._consume(TokenType.LEFT_BRACE, f"Expect open brace before {kind} body")
        body = self._block_stmt()
        return FunctionStmt(name, parameters, body)

    def _class_declaration(self):
        name = self._consume(TokenType.IDENTIFIER, "Expect class name.")

        if self._match(TokenType.LESS):
            self._consume(TokenType.IDENTIFIER, "Expect superclass name.")
            superclass = VarExpr(self._prev())
        else:
            superclass = None

        self._consume(TokenType.LEFT_BRACE, "Expect '{' before class body.")
        methods: list[FunctionStmt] = []
        while not self._check(TokenType.RIGHT_BRACE) and not self._at_end():
            methods.append(self._func_declaration(kind="method"))
        self._consume(TokenType.RIGHT_BRACE, "Expect '}' before class body.")
        return ClassStmt(name, superclass, methods)


    def _block_stmt(self) -> list[Stmt]:
        statements: list[Stmt] = []

        while not self._check(TokenType.RIGHT_BRACE) and not self._at_end():
            if declr := self._declaration():
                statements.append(declr)

        self._consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements

    def _if_stmt(self) -> IfStmt:
        self._consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after if condition.")

        then_branch = self._statement()

        # Dangling-else problem:
        # since Lox doesn't care about whitespaces (like Python),
        # `else` is bind to the nearest `if` that precedes it
        else_branch = self._statement() if self._match(TokenType.ELSE) else None
        return IfStmt(condition, then_branch, else_branch)

    def _while_stmt(self) -> WhileStmt:
        self._consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        condition = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after while condition.")
        body = self._statement()
        return WhileStmt(condition, body)

    def _for_stmt(self) -> Stmt:
        # `for` loop is just a syntactic sugar over `while` loop :shrug:
        self._consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")

        initializer: Optional[Stmt] = None
        if self._match(TokenType.SEMICOLON):
            initializer = None
        elif self._match(TokenType.VAR):
            initializer = self._var_declaration()
        else:
            initializer = self._expression_stmt()

        if not self._check(TokenType.SEMICOLON):
            condition = self._expression()
        else:
            condition = None
        self._consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")

        if not self._check(TokenType.RIGHT_PAREN):
            increment = self._expression()
        else:
            increment = None
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after for clauses.")

        body = self._statement()
        if increment:
            body = BlockStmt([body, ExpressionStmt(increment)])
        if not condition:
            condition = LiteralExpr(True)
        body = WhileStmt(condition, body)
        if initializer:
            body = BlockStmt([initializer, body])
        return body

    def _return_stmt(self) -> ReturnStmt:
        keyword = self._prev()
        if not self._check(TokenType.SEMICOLON):
            value = self._expression()
        else:
            value = None

        self._consume(TokenType.SEMICOLON, "Expect ';' after return value.")
        return ReturnStmt(keyword, value)

    def _expression(self) -> Expr:
        return self._assignment()

    def _assignment(self) -> Expr:
        expr = self._or_expr()

        if self._match(TokenType.EQUAL):
            equals = self._prev()
            value = self._assignment()

            if isinstance(expr, VarExpr):
                return AssignExpr(expr.name, value)
            elif isinstance(expr, GetExpr):
                return SetExpr(expr.obj, expr.name, value)
            else:
                raise ParserError(equals, "Invalid assignment target.")
        else:
            return expr

    def _or_expr(self) -> Expr:
        expr = self._and_expr()

        while self._match(TokenType.OR):
            operator = self._prev()
            right = self._and_expr()
            expr = LogicalExpr(expr, operator, right)

        return expr

    def _and_expr(self) -> Expr:
        expr = self._equality()

        while self._match(TokenType.AND):
            operator = self._prev()
            right = self._and_expr()
            expr = LogicalExpr(expr, operator, right)

        return expr

    def _equality(self) -> Expr:
        expr = self._comparison()

        while self._match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self._prev()
            right = self._comparison()
            expr = BinaryExpr(expr, operator, right)

        return expr

    def _comparison(self) -> Expr:
        expr = self._terminal()

        while self._match(TokenType.GREATER,
                          TokenType.GREATER_EQUAL,
                          TokenType.LESS,
                          TokenType.LESS_EQUAL):
            operator = self._prev()
            right = self._terminal()
            expr = BinaryExpr(expr, operator, right)

        return expr

    def _terminal(self) -> Expr:
        expr = self._factor()

        while self._match(TokenType.MINUS, TokenType.PLUS):
            operator = self._prev()
            right = self._factor()
            expr = BinaryExpr(expr, operator, right)

        return expr

    def _factor(self) -> Expr:
        expr = self._unary()

        while self._match(TokenType.SLASH, TokenType.STAR):
            operator = self._prev()
            right = self._unary()
            expr = BinaryExpr(expr, operator, right)

        return expr

    def _unary(self) -> Expr:
        if self._match(TokenType.BANG, TokenType.MINUS):
            operator = self._prev()
            right = self._unary()
            return UnaryExpr(operator, right)

        return self._call()

    def _call(self) -> Expr:
        expr = self._primary()

        while True:
            if self._match(TokenType.LEFT_PAREN):
                expr = self._finish_call(expr)
            elif self._match(TokenType.DOT):
                name = self._consume(TokenType.IDENTIFIER, "Expect property name after '.'.")
                expr = GetExpr(expr, name)
            else:
                break

        return expr

    def _finish_call(self, callee: Expr) -> Expr:
        arguments: list[Expr] = []
        if not self._check(TokenType.RIGHT_PAREN):
            while True:
                if len(arguments) >= 255:
                    raise ParserError(self._peek(), "Can't have more than 255 arguments.")
                arguments.append(self._expression());
                if not self._match(TokenType.COMMA):
                    break

        paren = self._consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments.")
        return CallExpr(callee, paren, arguments)

    def _primary(self) -> Expr:
        if self._match(TokenType.FALSE):
            return LiteralExpr(False)
        elif self._match(TokenType.TRUE):
            return LiteralExpr(True)
        elif self._match(TokenType.NIL):
            return LiteralExpr(None)
        elif self._match(TokenType.NUMBER, TokenType.STRING):
            return LiteralExpr(self._prev().literal)
        elif self._match(TokenType.SUPER):
            keyword = self._prev()
            self._consume(TokenType.DOT, "Expect '.' after 'super'.")
            method = self._consume(TokenType.IDENTIFIER, "Expect superclass method name.")
            return SuperExpr(keyword, method)
        elif self._match(TokenType.THIS):
            return ThisExpr(self._prev())
        elif self._match(TokenType.IDENTIFIER):
            return VarExpr(self._prev())
        elif self._match(TokenType.LEFT_PAREN):
            expr = self._expression()
            self._consume(TokenType.RIGHT_PAREN, "Expect ')' after expression")
            return GroupingExpr(expr)
        else:
            raise ParserError(self._peek(), "Expect expression.")

    def _synchronize(self):
        self._advance()

        while not self._at_end():
            if self._prev().type_ == TokenType.SEMICOLON:
                return

            if self._peek().type_ in (
                    TokenType.CLASS,
                    TokenType.FUN,
                    TokenType.VAR,
                    TokenType.FOR,
                    TokenType.IF,
                    TokenType.WHILE,
                    TokenType.PRINT,
                    TokenType.RETURN,
                ):
                return

            self._advance()

    ### Helpers
    def _match(self, *types: TokenType) -> bool:
        for t in types:
            if self._check(t):
                self._advance()
                return True

        return False

    def _check(self, type_: TokenType) -> bool:
        if self._at_end():
            return False
        return self._peek().type_ == type_

    def _advance(self) -> Token:
        if not self._at_end():
            self._current += 1
        return self._prev()

    def _at_end(self) -> bool:
        return self._peek().type_ == TokenType.EOF

    def _peek(self) -> Token:
        return self._tokens[self._current]

    def _prev(self) -> Token:
        return self._tokens[self._current - 1]

    def _consume(self, type_: TokenType, message: str) -> Token:
        if self._check(type_):
            return self._advance()

        raise ParserError(token=self._peek(), message=message)
