from _token import Token


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
