from _token import Token
from error_handling import LoxRuntimeError


class Environment:
    def __init__(self):
        self._values = dict()

    def define(self, name: str, value):
        self._values[name] = value

    def get(self, name: Token):
        if name.lexeme in self._values:
            return self._values[name.lexeme]
        else:
            raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def assign(self, name: Token, value):
        if name.lexeme in self._values:
            self._values[name.lexeme] = value
        else:
            raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")
