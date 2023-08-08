from typing import Any, Optional
from enum import Enum
from dataclasses import dataclass, field

from pylox._token import Token
from pylox.callable import LoxCallable
from pylox.function import LoxFunction
from pylox.error_handling import LoxRuntimeError


class ClassType(Enum):
    CLASS = "CLASS"
    SUBCLASS = "SUBCLASS"
    NONE = "NONE"


@dataclass
class LoxClass(LoxCallable):
    name: str
    superclass: Optional["LoxClass"] = field(default=None)
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
        if name in self.methods:
            return self.methods[name]
        elif self.superclass:
            return self.superclass.find_method(name)
        else:
            return None


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
            raise LoxRuntimeError(name, f"Undefined property '{name.lexeme}'.")

    def set(self, name: Token, value: Any):
        self._fields[name.lexeme] = value
