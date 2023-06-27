import sys


HAS_ERROR = False

def report(line: int, where: str, message: str):
    global HAS_ERROR
    print(f"[Line {line}] Error {where}: {message}", file=sys.stderr)
    HAS_ERROR = True


def error(line: int, message: str):
    report(line, "", message)
