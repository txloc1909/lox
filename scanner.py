from token import TokenType, Token
import utils


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

        ### Single-character tokens
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
        ### Two-character
        elif char == "!":
            self._add_token(
                TokenType.BANG_EQUAL if self._match("=") else TokenType.BANG
            )
        elif char == "=":
            self._add_token(
                TokenType.EQUAL_EQUAL if self._match("=") else TokenType.EQUAL
            )
        elif char == "<":
            self._add_token(
                TokenType.LESS_EQUAL if self._match("=") else TokenType.LESS
            )
        elif char == ">":
            self._add_token(
                TokenType.GREATER_EQUAL if self._match("=") else TokenType.GREATER
            )
        elif char == "/":
            # Ignore comments
            if self._match("/"):
                while self._peek() != "\n" and not self._at_end():
                    self._advance()
            else:
                self._add_token(TokenType.SLASH)
        elif char in (" ", "\r", "\t"):
            # do nothing with whitespaces
            pass
        elif char == "\n":
            self._add_token(TokenType.NEWLINE)
            self._line += 1
        elif char == '"':
            self._scan_string_literal()
        else:
            utils.error(self._line, f"Unexpected character: {char}")

    def _at_end(self):
        return self._current >= len(self._src)

    def _advance(self):
        next_char = self._src[self._current]
        self._current += 1
        return next_char

    def _add_token(self, token_type: TokenType, literal=None):
        lexeme = self._src[self._start:self._current]
        self._tokens.append(Token(token_type, lexeme, literal, self._line))

    def _match(self, expected) -> bool:
        if self._at_end():
            return False
        elif self._src[self._current] != expected:
            return False
        else:
            self._current += 1
            return True

    def _peek(self):
        return "\0" if self._at_end() else self._src[self._current]

    def _scan_string_literal(self):
        while self._peek() != '"' and not self._at_end():
            if self._peek() == "\n":
                self._line += 1
            self._advance()

        if self._at_end():
            utils.error(self._line, "Unterminated string.")
            return

        self._advance()             # The closing \"

        # Extract string literal (without the quotes)
        literal = self._src[self._start + 1 : self._current - 1]
        self._add_token(TokenType.STRING, literal=literal)
