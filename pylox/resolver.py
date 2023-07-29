from typing import Iterator
from contextlib import contextmanager, nullcontext, ExitStack

from _token import Token
from expr import (Expr, VarExpr, AssignExpr, BinaryExpr, CallExpr, GroupingExpr,
                  LiteralExpr, LogicalExpr, UnaryExpr, GetExpr, SetExpr,
                  ThisExpr, SuperExpr)
from stmt import (Stmt, BlockStmt, VarStmt, FunctionStmt, ExpressionStmt, IfStmt,
                  PrintStmt, WhileStmt, ReturnStmt, ClassStmt)
from visitor import Visitor
from function import FunctionType
from _class import ClassType
from error_handling import LoxRuntimeError, ErrorHandler


class Resolver:

    def __init__(self, interpreter, error_handler: ErrorHandler):
        self.interpreter = interpreter
        self._handler = error_handler
        self._scopes: list[dict[str, bool]] = []
        self._curr_func = FunctionType.NONE
        self._curr_class = ClassType.NONE

    def visit(self, visitee: Expr | Stmt):
        try:
            return getattr(self, f"visit_{type(visitee).__name__}")(visitee)
        except AttributeError:
            pass

    def _resolve(self, ast_node: Expr | Stmt):
        ast_node.accept(self)

    def resolve(self, statements: list[Stmt]):
        for s in statements:
            self._resolve(s)

    def visit_BlockStmt(self, stmt: BlockStmt):
        with self._new_scope():
            self.resolve(stmt.statements)

    def visit_VarStmt(self, stmt: VarStmt):
        self._declare(stmt.name)
        if stmt.initializer:
            self._resolve(stmt.initializer)
        self._define(stmt.name)

    def visit_FunctionStmt(self, stmt: FunctionStmt):
        self._declare(stmt.name)
        self._define(stmt.name)
        self._resolve_function(stmt, FunctionType.FUNCTION)

    def visit_ReturnStmt(self, stmt: ReturnStmt):
        if self._curr_func is FunctionType.NONE:
            self._handler.error(at=stmt.keyword,
                                message="Can't return from top-level code.")
        if stmt.value:
            if self._curr_func is FunctionType.INITIALIZER:
                self._handler.error(
                    at=stmt.keyword,
                    message="Can't return a value from an initializer."
                )
            self._resolve(stmt.value)

    def visit_ExpressionStmt(self, stmt: ExpressionStmt):
        self._resolve(stmt.expr)

    def visit_IfStmt(self, stmt: IfStmt):
        self._resolve(stmt.condition)
        self._resolve(stmt.then_branch)
        if stmt.else_branch:
            self._resolve(stmt.else_branch)

    def visit_PrintStmt(self, stmt: PrintStmt):
        self._resolve(stmt.expr)

    def visit_WhileStmt(self, stmt: WhileStmt):
        self._resolve(stmt.condition)
        self._resolve(stmt.body)

    def visit_ClassStmt(self, stmt: ClassStmt):
        with ExitStack() as stack:
            stack.enter_context(self._new_class(ClassType.CLASS))
            self._declare(stmt.name)
            self._define(stmt.name)

            if stmt.superclass and stmt.name.lexeme == stmt.superclass.name.lexeme:
                self._handler.error(at=stmt.superclass.name,
                                    message="A class can't inherit from itself.")
            if stmt.superclass:
                stack.enter_context(self._new_class(ClassType.SUBCLASS))
                self._resolve(stmt.superclass)
                superclass_scope = stack.enter_context(self._new_scope())
                superclass_scope["super"] = True

            class_scope = stack.enter_context(self._new_scope())
            class_scope["this"] = True
            for method in stmt.methods:
                method_name = method.name.lexeme
                declaration = FunctionType.INITIALIZER if method_name == "init" \
                        else FunctionType.METHOD
                self._resolve_function(method, declaration)

    def visit_VarExpr(self, expr: VarExpr):
        if self._scopes and (expr.name.lexeme in self._scopes[-1]) \
                and (not self._scopes[-1][expr.name.lexeme]):
            self._handler.error(
                at=expr.name,
                message="Can't read local variable in its own initializer."
            )

        self._resolve_local(expr, expr.name)

    def visit_AssignExpr(self, expr: AssignExpr):
        self._resolve(expr.value)
        self._resolve_local(expr, expr.name)

    def visit_BinaryExpr(self, expr: BinaryExpr):
        self._resolve(expr.left)
        self._resolve(expr.right)

    def visit_CallExpr(self, expr: CallExpr):
        self._resolve(expr.callee)
        for arg in expr.arguments:
            self._resolve(arg)

    def visit_GetExpr(self, expr: GetExpr):
        # since properties are looked up dynamically,
        # only resolve the left side of the dot
        self._resolve(expr.obj)

    def visit_SetExpr(self, expr: SetExpr):
        self._resolve(expr.value)
        self._resolve(expr.obj)

    def visit_SuperExpr(self, expr: SuperExpr):
        match self._curr_class:
            case ClassType.SUBCLASS:
                self._resolve_local(expr, expr.keyword)
            case ClassType.NONE:
                self._handler.error(expr.keyword,
                                    "Can't use 'super' outside of a class.")
            case ClassType.CLASS:
                self._handler.error(expr.keyword,
                                    "Can't use 'super' in a class with no superclass.")

    def visit_GroupingExpr(self, expr: GroupingExpr):
        self._resolve(expr.inner)

    def visit_LiteralExpr(self, expr: LiteralExpr):
        pass

    def visit_ThisExpr(self, expr: ThisExpr):
        if self._curr_class is ClassType.NONE:
            self._handler.error(at=expr.keyword,
                                message="Can't use 'this' outside of a class.")

        self._resolve_local(expr, expr.keyword)

    def visit_LogicalExpr(self, expr: LogicalExpr):
        self._resolve(expr.left)
        self._resolve(expr.right)

    def visit_UnaryExpr(self, expr: UnaryExpr):
        self._resolve(expr.right)

    def _resolve_local(self, expr: Expr, name: Token):
        for depth, scope in enumerate(reversed(self._scopes)):
            if name.lexeme in scope:
                self.interpreter.resolve(expr, depth=depth)
                return

    def _resolve_function(self, function: FunctionStmt, func_type: FunctionType):
        with self._new_function(func_type):
            for param in function.params:
                self._declare(param)
                self._define(param)
            self.resolve(function.body)

    def _declare(self, name: Token):
        if not self._scopes:
            return

        scope = self._scopes[-1]
        if name.lexeme in scope:
            self._handler.error(
                at=name,
                message="Already a variable with this name in this scope."
            )

        scope[name.lexeme] = False

    def _define(self, name: Token):
        if not self._scopes:
            return
        self._scopes[-1][name.lexeme] = True

    @contextmanager
    def _new_scope(self) -> Iterator[dict[str, bool]]:
        new_scope: dict[str, bool] = {}
        self._scopes.append(new_scope)
        yield new_scope
        self._scopes.pop()

    @contextmanager
    def _new_function(self, func_type: FunctionType):
        enclosing_func = self._curr_func
        self._curr_func = func_type
        with self._new_scope():     # function gets its own scope
            yield
        self._curr_func = enclosing_func

    @contextmanager
    def _new_class(self, class_type: ClassType):
        enclosing_class = self._curr_class
        self._curr_class = class_type
        yield
        self._curr_class = enclosing_class
