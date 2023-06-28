import sys

from _token import Token


HAS_ERROR = False
HAS_RUNTIME_ERROR = False


class LoxRuntimeError(RuntimeError):
    def __init__(self, token: Token, message: str):
        super().__init__(message)
        self.token = token


def report(line: int, where: str, message: str):
    global HAS_ERROR
    print(f"[Line {line}] Error {where}: {message}", file=sys.stderr)
    HAS_ERROR = True


def error(line: int, message: str):
    report(line, "", message)


def runtime_error(error: LoxRuntimeError):
    global HAS_RUNTIME_ERROR
    print(f"{error}\n[line {error.token.line}]")
    HAS_RUNTIME_ERROR = True
