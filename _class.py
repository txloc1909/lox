from typing import Any
from dataclasses import dataclass, field

from _token import Token
from callable import LoxCallable
from error_handling import LoxRuntimeError


@dataclass
class LoxInstance:
    _class: "LoxClass"
    _fields: dict[str, Any] = field(default_factory=dict)

    def __repr__(self):
        return f"{self._class.name} instance"

    def get(self, name: Token) -> Any:
        try:
            return self._fields[name.lexeme]
        except KeyError:
            raise LoxRuntimeError(name, f"Undefine property {name.lexeme}.")

    def set(self, name: Token, value: Any):
        self._fields[name.lexeme] = value


@dataclass
class LoxClass(LoxCallable):
    name: str

    def __repr__(self):
        return self.name

    def call(self, interpreter, *arguments):
        return LoxInstance(_class=self)

    def arity(self) -> int:
        return 0
