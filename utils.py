import sys


def report(line: int, where: str, message: str):
    global _HAS_ERROR
    print(f"[Line {line}] Error {where}: {message}", file=sys.stderr)
    _HAS_ERROR = True


def error(line: int, message: str):
    report(line, "", message)
