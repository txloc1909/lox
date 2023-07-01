from typing import Optional

from _token import Token
from error_handling import LoxRuntimeError


class Environment:
    def __init__(self, enclosing: Optional["Environment"] = None):
        self._values = dict()
        self._enclosing = enclosing

    def define(self, name: str, value):
        self._values[name] = value

    def get(self, name: Token):
        if name.lexeme in self._values:
            return self._values[name.lexeme]
        elif self._enclosing:
            return self._enclosing.get(name)
        else:
            raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def assign(self, name: Token, value):
        if name.lexeme in self._values:
            self._values[name.lexeme] = value
        elif self._enclosing:
            self._enclosing.assign(name, value)
        else:
            raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")
