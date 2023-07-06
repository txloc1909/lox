from typing import Any, Optional
from enum import Enum
from dataclasses import dataclass, field

from _token import Token
from callable import LoxCallable
from function import LoxFunction
from error_handling import LoxRuntimeError


class ClassType(Enum):
    CLASS = "CLASS"
    NONE = "NONE"


@dataclass
class LoxClass(LoxCallable):
    name: str
    methods: dict[str, LoxFunction] = field(default_factory=dict)

    def __repr__(self):
        return self.name

    def call(self, interpreter, *arguments) -> "LoxInstance":
        instance = LoxInstance(_class=self)
        initializer = self.find_method("init")
        if initializer:
            initializer.bind(instance).call(interpreter, *arguments)

        return instance

    def arity(self) -> int:
        initializer = self.find_method("init")
        return initializer.arity() if initializer else 0

    def find_method(self, name: str) -> Optional[LoxFunction]:
        return self.methods.get(name, None)


@dataclass
class LoxInstance:
    _class: LoxClass
    _fields: dict[str, Any] = field(default_factory=dict)

    def __repr__(self):
        return f"{self._class.name} instance"

    def get(self, name: Token) -> Any:
        if name.lexeme in self._fields:
            return self._fields[name.lexeme]
        elif method := self._class.find_method(name.lexeme):
            return method.bind(self)
        else:
            raise LoxRuntimeError(name, f"Undefine property {name.lexeme}.")

    def set(self, name: Token, value: Any):
        self._fields[name.lexeme] = value
