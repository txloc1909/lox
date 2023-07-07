import sys

from _token import Token, TokenType


HAS_ERROR = False
HAS_RUNTIME_ERROR = False


class ParserError(RuntimeError):
    pass


class LoxRuntimeError(RuntimeError):
    def __init__(self, token: Token, message: str):
        super().__init__(message)
        self.token = token


def report(line: int, where: str, message: str):
    global HAS_ERROR
    print(f"[Line {line}] Error {where}: {message}", file=sys.stderr)
    HAS_ERROR = True


def error(at: int | Token, message: str):
    if isinstance(at, int):
        line = at
        report(line, "", message)
    elif isinstance(at, Token):
        token = at
        if token.type_ == TokenType.EOF:
            report(token.line, " at end", message)
        else:
            report(token.line, f"at '{token.lexeme}'", message)


def runtime_error(error: LoxRuntimeError):
    global HAS_RUNTIME_ERROR
    print(f"{error}\n[line {error.token.line}]", file=sys.stderr)
    HAS_RUNTIME_ERROR = True
