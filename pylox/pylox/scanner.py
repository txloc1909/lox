from typing import Iterator, Optional
from collections.abc import Mapping

from pylox._token import TokenType, Token
from pylox.error_handling import ErrorHandler

_KEYWORDS: Mapping[str, TokenType] = {
        "and" :         TokenType.AND,
        "class":        TokenType.CLASS,
        "else":         TokenType.ELSE,
        "false":        TokenType.FALSE,
        "for":          TokenType.FOR,
        "fun":          TokenType.FUN,
        "if":           TokenType.IF,
        "nil":          TokenType.NIL,
        "or":           TokenType.OR,
        "print":        TokenType.PRINT,
        "return":       TokenType.RETURN,
        "super":        TokenType.SUPER,
        "this":         TokenType.THIS,
        "true":         TokenType.TRUE,
        "var":          TokenType.VAR,
        "while":        TokenType.WHILE,
}


class Scanner:
    def __init__(self, src: str, error_handler: ErrorHandler):
        self._src: str = src
        self._start: int = 0
        self._current: int = 0
        self._line: int = 1
        self._col: int = 1
        self._handler = error_handler

    def scan_tokens(self) -> Iterator[Token]:
        while not self._at_end():
            self._start = self._current
            if token := self._scan_one_token():
                yield token

        yield Token(TokenType.EOF, "", None, self._line, self._col)

    def _scan_one_token(self) -> Optional[Token]:
        char = self._advance()
        match char:
        ### Single-character tokens
            case "(":
                return self._create_token(TokenType.LEFT_PAREN)
            case ")":
                return self._create_token(TokenType.RIGHT_PAREN)
            case "{":
                return self._create_token(TokenType.LEFT_BRACE)
            case "}":
                return self._create_token(TokenType.RIGHT_BRACE)
            case ",":
                return self._create_token(TokenType.COMMA)
            case ".":
                return self._create_token(TokenType.DOT)
            case "-":
                return self._create_token(TokenType.MINUS)
            case "+":
                return self._create_token(TokenType.PLUS)
            case ";":
                return self._create_token(TokenType.SEMICOLON)
            case "*":
                return self._create_token(TokenType.STAR)
            ### Two-character
            case "!":
                return self._create_token(
                    TokenType.BANG_EQUAL if self._match("=") else TokenType.BANG
                )
            case "=":
                return self._create_token(
                    TokenType.EQUAL_EQUAL if self._match("=") else TokenType.EQUAL
                )
            case "<":
                return self._create_token(
                    TokenType.LESS_EQUAL if self._match("=") else TokenType.LESS
                )
            case ">":
                return self._create_token(
                    TokenType.GREATER_EQUAL if self._match("=") else TokenType.GREATER
                )
            case "/":
                # Ignore comments
                if self._match("/"):
                    while self._peek() != "\n" and not self._at_end():
                        self._advance()
                    return None
                else:
                    return self._create_token(TokenType.SLASH)
            case " " | "\r" | "\t":
                # do nothing with whitespaces
                return None
            case "\n":
                self._bump_line()
                return None
            case '"':
                return self._scan_string_literal()
            case _:
                if char.isdigit():
                    return self._scan_number_literal()
                elif char.isalpha():
                    return self._scan_identifier()
                else:
                    self._handler.error(at=self._line,
                                        message=f"Unexpected character.")
                    return None

    def _at_end(self) -> bool:
        return self._current >= len(self._src)

    def _advance(self) -> str:
        next_char = self._src[self._current]
        self._current += 1
        self._col += 1
        return next_char

    def _bump_line(self):
        self._line += 1
        self._col = 1

    def _create_token(self, token_type: TokenType, literal=None):
        lexeme = self._src[self._start:self._current]
        return Token(type_=token_type,
                     lexeme=lexeme,
                     literal=literal,
                     line=self._line,
                     col=self._col - self._current + self._start)

    def _match(self, expected) -> bool:
        if self._at_end():
            return False
        elif self._src[self._current] != expected:
            return False
        else:
            self._current += 1
            self._col += 1
            return True

    def _peek(self) -> str:
        return "\0" if self._at_end() else self._src[self._current]

    def _peek_next(self) -> str:
        return "\0" if self._current + 1 >= len(self._src) else \
                self._src[self._current + 1]

    def _scan_string_literal(self) -> Optional[Token]:
        while self._peek() != '"' and not self._at_end():
            if self._peek() == "\n":
                self._bump_line()
            self._advance()

        if self._at_end():
            self._handler.error(at=self._line, message="Unterminated string.")
            return None

        self._advance()             # The closing \"

        # Extract string literal (without the quotes)
        literal = self._src[self._start + 1 : self._current - 1]
        return self._create_token(TokenType.STRING, literal=literal)

    def _scan_number_literal(self) -> Token:
        while self._peek().isdigit():
            self._advance()

        # Look for a fractional part (.)
        if self._peek() == "." and self._peek_next().isdigit():
            # Consume the dot (.)
            self._advance()

            while self._peek().isdigit():
                self._advance()

        return self._create_token(
            TokenType.NUMBER,
            literal=float(self._src[self._start:self._current])
        )

    def _scan_identifier(self) -> Token:
        while self._peek().isalnum() or self._peek() == "_":
            self._advance()

        lexeme = self._src[self._start : self._current]
        token_type = _KEYWORDS.get(lexeme, TokenType.IDENTIFIER)
        return self._create_token(token_type)


if __name__ == "__main__":
    src = """var x = 1;
if (x > 0) {
    print x;
}
"""
    lines = src.split("\n")
    for line in lines:
        print(line)

    from pylox.error_handling import ErrorHandler
    scanner = Scanner(src, error_handler=ErrorHandler())
    for token in scanner.scan_tokens():
        print(token, token.line, token.col)
