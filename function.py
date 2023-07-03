from stmt import FunctionStmt
from environment import Environment
from callable import LoxCallable


class Return(Exception):
    def __init__(self, value):
        super().__init__()
        self.value = value


class LoxFunction(LoxCallable):

    def __init__(self, declaration: FunctionStmt, closure: Environment):
        self._declaration = declaration
        self._closure = closure

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
            return _return.value

    def __repr__(self) -> str:
        return f"<fn {self._declaration.name.lexeme}>"
