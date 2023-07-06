import time

from _token import Token, TokenType
from expr import (Expr, BinaryExpr, GroupingExpr, LiteralExpr, UnaryExpr,
                  VarExpr, AssignExpr, LogicalExpr, CallExpr, GetExpr, SetExpr)
from stmt import (Stmt, ExpressionStmt, PrintStmt, VarStmt, BlockStmt, IfStmt,
                  WhileStmt, FunctionStmt, ReturnStmt, ClassStmt)
from visitor import Visitor
from callable import LoxCallable
from function import LoxFunction, Return
from _class import LoxClass, LoxInstance
from environment import Environment
from error_handling import LoxRuntimeError


def check_number_operand(operator: Token, operand):
    if isinstance(operand, float):
        return
    else:
        raise LoxRuntimeError(operator, "Operand must be a number.")


def check_number_operands(operator: Token, left, right):
    if isinstance(left, float) and isinstance(right, float):
        return
    else:
        raise LoxRuntimeError(operator, "Operands must be numbers.")


def stringify(value):
    if value is None:
        return "nil"
    elif isinstance(value, float):
        s = str(value)
        if s.endswith(".0"):
            s = s[:-2]
        return s
    elif isinstance(value, bool):
        return "true" if value else "false"
    else:
        return str(value)


class _NativeClock:
    def arity(self) -> int:
        return 0

    def call(self, intepreter, *arguments):
        return time.perf_counter()

    def __repr__(self):
        return "<native fn>"


class Interpreter:

    def __init__(self):
        self._GLOBAL_ENV: Environment = Environment()
        self._env: Environment = self._GLOBAL_ENV
        self._locals: dict[Expr, int] = {}

        self._GLOBAL_ENV.define("clock", _NativeClock())

    @property
    def global_env(self) -> Environment:
        return self._GLOBAL_ENV

    def evaluate(self, expr: Expr):
        return expr.accept(self)

    def execute(self, stmt: Stmt):
        return stmt.accept(self)

    def resolve(self, expr: Expr, depth: int):
        if expr in self._locals:
            print(f"WARNING: locals override: {expr}: from {self._locals[expr]} to {depth}")
        self._locals[expr] = depth

    def interpret(self, statements: list[Stmt]):
        try:
            for s in statements:
                self.execute(s)
        except LoxRuntimeError as e:
            print(e)

    def visit(self, visitee: Expr | Stmt):
        return getattr(self, f"visit_{type(visitee).__name__}")(visitee)

    def visit_ExpressionStmt(self, stmt: ExpressionStmt):
        self.evaluate(stmt.expr)

    def visit_PrintStmt(self, stmt: PrintStmt):
        value = self.evaluate(stmt.expr)
        print(stringify(value))

    def visit_VarStmt(self, stmt: VarStmt):
        if stmt.initializer:
            value = self.evaluate(stmt.initializer)
        else:
            value = None

        self._env.define(stmt.name.lexeme, value)

    def visit_BlockStmt(self, stmt: BlockStmt):
        self.execute_block(stmt.statements, Environment(enclosing=self._env))

    def visit_IfStmt(self, stmt: IfStmt):
        if bool(self.evaluate(stmt.condition)):
            self.execute(stmt.then_branch)
        elif stmt.else_branch:
            self.execute(stmt.else_branch)

    def visit_WhileStmt(self, stmt: WhileStmt):
        while self.evaluate(stmt.condition):
            self.execute(stmt.body)

    def visit_FunctionStmt(self, stmt: FunctionStmt):
        function = LoxFunction(declaration=stmt, closure=self._env)
        self._env.define(stmt.name.lexeme, function)

    def visit_ReturnStmt(self, stmt: ReturnStmt):
        value = self.evaluate(stmt.value) if stmt.value else None
        raise Return(value)

    def visit_ClassStmt(self, stmt: ClassStmt):
        self._env.define(stmt.name.lexeme, None)

        methods: dict[str, LoxFunction] = {
            m.name.lexeme : LoxFunction(m, closure=self._env)
            for m in stmt.methods
        }

        self._env.assign(stmt.name, LoxClass(stmt.name.lexeme, methods))

    def visit_VarExpr(self, expr: VarExpr):
        return self._lookup_variable(expr.name, expr)

    def visit_AssignExpr(self, expr: AssignExpr):
        value = self.evaluate(expr.value)

        distance = self._locals.get(expr)
        if distance is not None:
            self._env.assign_at(distance, expr.name, value)
        else:
            self.global_env.assign(expr.name, value)

        return value

    def visit_LiteralExpr(self, expr: LiteralExpr):
        return expr.value

    def visit_GroupingExpr(self, expr: GroupingExpr):
        return self.evaluate(expr.inner)

    def visit_UnaryExpr(self, expr: UnaryExpr):
        right = self.evaluate(expr.right)

        match expr.operator.type_:
            case TokenType.MINUS:
                check_number_operand(expr.operator, right)
                return -float(right)
            case TokenType.BANG:
                return not bool(right)
            case _:
                return None

    def visit_BinaryExpr(self, expr: BinaryExpr):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        match expr.operator.type_:
            case TokenType.MINUS:
                check_number_operands(expr.operator, left, right)
                return left - right
            case TokenType.SLASH:
                check_number_operands(expr.operator, left, right)
                return left / right
            case TokenType.STAR:
                check_number_operands(expr.operator, left, right)
                return left * right
            case TokenType.PLUS:
                if isinstance(left, float) and isinstance(right, float):
                    return left + right
                elif isinstance(left, str) and isinstance(right, str):
                    return left + right
                else:
                    raise LoxRuntimeError(expr.operator, "Operands must be two numbers or two strings")
            case TokenType.GREATER:
                check_number_operands(expr.operator, left, right)
                return left > right
            case TokenType.GREATER_EQUAL:
                check_number_operands(expr.operator, left, right)
                return left >= right
            case TokenType.LESS:
                check_number_operands(expr.operator, left, right)
                return left < right
            case TokenType.LESS_EQUAL:
                check_number_operands(expr.operator, left, right)
                return left <= right
            case TokenType.BANG_EQUAL:
                return left != right
            case TokenType.EQUAL_EQUAL:
                return left == right
            case _:
                return None

    def visit_LogicalExpr(self, expr: LogicalExpr):
        left = self.evaluate(expr.left)

        # Short-circuit:
        # return the object, with its appropriate truthiness,
        # not the literal True or false, and let the caller decide how to use
        if expr.operator.type_ == TokenType.OR:
            if left:
                return left
        else:
            if not left:
                return left

        return self.evaluate(expr.right)

    def visit_CallExpr(self, expr: CallExpr):
        callee = self.evaluate(expr.callee)

        # Important: order of evaluating arguments is kept
        arguments = [self.evaluate(arg) for arg in expr.arguments]

        if not isinstance(callee, LoxCallable):
            raise LoxRuntimeError(expr.paren, "Can only call functions and classes.")

        n_arguments = len(arguments)
        f_arity = callee.arity()
        if n_arguments != f_arity:
            raise LoxRuntimeError(expr.paren, f"Expected {f_arity} arguments but got {n_arguments}.")

        return callee.call(self, *arguments)

    def visit_GetExpr(self, expr: GetExpr):
        obj = self.evaluate(expr.obj)
        if isinstance(obj, LoxInstance):
            return obj.get(expr.name)

        raise LoxRuntimeError(expr.name, "Only instances have properties")

    def visit_SetExpr(self, expr: SetExpr):
        obj = self.evaluate(expr.obj)
        if not isinstance(obj, LoxInstance):
            raise LoxRuntimeError(expr.name, "Only instances have fields.")

        value = self.evaluate(expr.value)

        obj.set(expr.name, value)
        return value

    def execute_block(self, statements: list[Stmt], env: Environment):
        # NOTE: use context manager, probably?
        prev_env = self._env
        try:
            self._env = env
            for stmt in statements:
                self.execute(stmt)
        finally:
            self._env = prev_env

    def _lookup_variable(self, name: Token, expr: Expr):
        distance = self._locals.get(expr)
        if distance is not None:
            return self._env.get_at(distance, name.lexeme)
        else:
            return self.global_env.get(name)


if __name__ == "__main__":
    assert issubclass(Interpreter, Visitor)
