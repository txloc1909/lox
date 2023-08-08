import sys

from pylox._token import Token, TokenType


class ParserError(RuntimeError):
    pass


class LoxRuntimeError(RuntimeError):
    def __init__(self, token: Token, message: str):
        super().__init__(message)
        self.token = token


class ErrorHandler:
    def __init__(self):
        self.has_error = False
        self.has_runtime_error = False

    def report(self, line: int, where: str, message: str):
        if len(where):
            where = " " + where
        print(f"[line {line}] Error{where}: {message}", file=sys.stderr)
        self.has_error = True

    def error(self, at: int | Token, message: str):
        if isinstance(at, int):
            self.report(at, "", message)
        elif isinstance(at, Token):
            token = at
            if token.type_ == TokenType.EOF:
                self.report(token.line, "at end", message)
            else:
                self.report(token.line, f"at '{token.lexeme}'", message)

    def parser_error(self, token: Token, message: str):
        self.error(at=token, message=message)
        return ParserError()


    def runtime_error(self, error: LoxRuntimeError):
        print(f"{error}\n[line {error.token.line}]", file=sys.stderr)
        self.has_runtime_error = True
