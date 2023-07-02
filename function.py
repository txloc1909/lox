from stmt import FunctionStmt
from environment import Environment
from callable import LoxCallable


class LoxFunction(LoxCallable):

    def __init__(self, declaration: FunctionStmt):
        self._declaration = declaration

    def arity(self) -> int:
        return len(self._declaration.params)

    def call(self, intepreter, *arguments):
        assert len(arguments) == self.arity()
        env = Environment(enclosing=intepreter.global_env)
        for name, value in zip(self._declaration.params, arguments):
            env.define(name.lexeme, value)
        intepreter.execute_block(self._declaration.body, env)

    def __repr__(self) -> str:
        return f"<fn {self._declaration.name.lexeme}>"
