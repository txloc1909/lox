from typing import Protocol, runtime_checkable


@runtime_checkable
class LoxCallable(Protocol):

    def arity(self) -> int:
        pass

    def call(self, intepreter, *arguments):
        pass
