from typing import Optional, Any

from pylox.token import Token
from pylox.error_handling import LoxRuntimeError


class Environment:
    def __init__(self, enclosing: Optional["Environment"] = None) -> None:
        self._values: dict[str, Any] = dict()
        self._enclosing = enclosing

    @property
    def enclosing(self):
        return self._enclosing

    def define(self, name: str, value: Any) -> None:
        self._values[name] = value

    def get(self, name: Token) -> Any:
        if name.lexeme in self._values:
            return self._values[name.lexeme]
        elif self._enclosing:
            return self._enclosing.get(name)
        else:
            raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def get_at(self, distance: int, name: str) -> Any:
        target_env = self.ancestor(distance)
        assert name in target_env._values
        return target_env._values[name]

    def assign(self, name: Token, value: Any) -> None:
        if name.lexeme in self._values:
            self._values[name.lexeme] = value
        elif self._enclosing:
            self._enclosing.assign(name, value)
        else:
            raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def assign_at(self, distance: int, name: Token, value: Any) -> None:
        self.ancestor(distance)._values[name.lexeme] = value

    def ancestor(self, distance: int) -> "Environment":
        env = self
        for _ in range(distance):
            assert env._enclosing
            env = env._enclosing

        return env
