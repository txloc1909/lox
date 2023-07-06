from dataclasses import dataclass

from callable import LoxCallable


@dataclass
class LoxInstance:
    _class: "LoxClass"

    def __repr__(self):
        return f"{self._class.name} instance"


@dataclass
class LoxClass(LoxCallable):
    name: str

    def __repr__(self):
        return self.name

    def call(self, interpreter, *arguments):
        return LoxInstance(_class=self)

    def arity(self) -> int:
        return 0
