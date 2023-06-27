from typing import Optional

from _token import TokenType, Token
from expr import (
    Expr,
    Binary,
    Grouping,
    Literal,
    Unary,
)
from utils import report


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

    def parse(self) -> Optional[Expr]:
        try:
            return self._expression()
        except ParserError:
            return None

    def _expression(self) -> Expr:
        return self._equality()

    def _equality(self) -> Expr:
        expr = self._comparison()

        while self._match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self._prev()
            right = self._comparison()
            expr = Binary(expr, operator, right)

        return expr

    def _comparison(self) -> Expr:
        expr = self._terminal()

        while self._match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            operator = self._prev()
            right = self._terminal()
            expr = Binary(expr, operator, right)

        return expr

    def _terminal(self) -> Expr:
        expr = self._factor()

        while self._match(TokenType.MINUS, TokenType.PLUS):
            operator = self._prev()
            right = self._factor()
            expr = Binary(expr, operator, right)

        return expr

    def _factor(self) -> Expr:
        expr = self._unary()

        while self._match(TokenType.SLASH, TokenType.STAR):
            operator = self._prev()
            right = self._unary()
            expr = Binary(expr, operator, right)

        return expr

    def _unary(self) -> Expr:
        if self._match(TokenType.BANG, TokenType.MINUS):
            operator = self._prev()
            right = self._unary()
            return Unary(operator, right)

        return self._primary()

    def _primary(self) -> Expr:
        if self._match(TokenType.FALSE):
            return Literal(False)
        elif self._match(TokenType.TRUE):
            return Literal(True)
        elif self._match(TokenType.NIL):
            return Literal(None)
        elif self._match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self._prev().literal)
        elif self._match(TokenType.LEFT_PAREN):
            expr = self._expression()
            self._consume(TokenType.RIGHT_PAREN, "Expect ')' after expression")
            return Grouping(expr)
        else:
            raise ParserError(self._peek(), "Expect expression.")

    def _synchronize(self):
        self._advance()

        while not self._at_end():
            if self._prev().type_ == TokenType.SEMICOLON:
                return

            if self._peek().type_ in set(
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

    def _consume(self, type_: TokenType, message: str):
        if self._check(type_):
            return self._advance()

        raise ParserError(token=self._peek(), message=message)
