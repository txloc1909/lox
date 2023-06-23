from token import TokenType, Token


class Scanner:
    def __init__(self, src: str):
        self._src: str = src
        self._start: int = 0
        self._current: int = 0
        self._line: int = 1
        self._tokens: list[Token] = []

    def scan_tokens(self) -> list[Token]:
        while not self._at_end():
            self._start = self._current
            self._scan_one_token()

        self._tokens.append(Token(TokenType.EOF, "", None, self._line))
        return self._tokens

    def _scan_one_token(self):
        char = self._advance()
        if char == "(":
            self._add_token(TokenType.LEFT_PAREN)
        elif char == ")":
            self._add_token(TokenType.RIGHT_PAREN)
        elif char == "{":
            self._add_token(TokenType.LEFT_BRACE)
        elif char == "}":
            self._add_token(TokenType.RIGHT_BRACE)
        elif char == ",":
            self._add_token(TokenType.COMMA)
        elif char == ".":
            self._add_token(TokenType.DOT)
        elif char == "-":
            self._add_token(TokenType.MINUS)
        elif char == "+":
            self._add_token(TokenType.PLUS)
        elif char == ";":
            self._add_token(TokenType.SEMICOLON)
        elif char == "*":
            self._add_token(TokenType.STAR)
        elif char == "\n":
            self._add_token(TokenType.NEWLINE)
        else:
            raise ValueError(f"Unexpected character: {char} at line {self._line}")

    def _at_end(self):
        return self._current > len(self._src) - 1

    def _advance(self):
        next_char = self._src[self._current]
        self._current += 1
        return next_char

    def _add_token(self, token_type: TokenType, literal=None):
        text = self._src[self._start:self._current]
        self._tokens.append(Token(token_type, text, literal, self._line))
