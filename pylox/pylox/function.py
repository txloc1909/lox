from enum import Enum

from pylox.stmt import FunctionStmt
from pylox.environment import Environment
from pylox.callable import LoxCallable


class FunctionType(Enum):
    NONE = "NONE"
    FUNCTION = "FUNCTION"
    METHOD = "METHOD"
    INITIALIZER = "INITIALIZER"


class Return(Exception):
    def __init__(self, value):
        super().__init__()
        self.value = value


class LoxFunction(LoxCallable):

    def __init__(self, declaration: FunctionStmt, closure: Environment,
                 is_initializer: bool = False):
        self._declaration = declaration
        self._closure = closure
        self._is_initializer = is_initializer

    def arity(self) -> int:
        return len(self._declaration.params)

    def call(self, intepreter, *arguments):
        assert len(arguments) == self.arity()

        env = Environment(enclosing=self._closure)
        for name, value in zip(self._declaration.params, arguments):
            env.define(name.lexeme, value)

        try:
            intepreter.execute_block(self._declaration.body, env)
        except Return as _return:
            if self._is_initializer:
                # `init` method always return `this`
                return self._closure.get_at(0, "this")
            return _return.value

        if self._is_initializer:
            return self._closure.get_at(0, "this")

    def __repr__(self) -> str:
        return f"<fn {self._declaration.name.lexeme}>"

    def bind(self, instance):
        env = Environment(enclosing=self._closure)
        env.define("this", instance)
        return LoxFunction(self._declaration,
                           closure=env,
                           is_initializer=self._is_initializer)
