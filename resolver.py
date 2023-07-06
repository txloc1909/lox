from _token import Token
from expr import (Expr, VarExpr, AssignExpr, BinaryExpr, CallExpr, GroupingExpr,
                  LiteralExpr, LogicalExpr, UnaryExpr, GetExpr, SetExpr)
from stmt import (Stmt, BlockStmt, VarStmt, FunctionStmt, ExpressionStmt, IfStmt,
                  PrintStmt, WhileStmt, ReturnStmt, ClassStmt)
from visitor import Visitor
from function import FunctionType
from error_handling import LoxRuntimeError


class Resolver:

    def __init__(self, interpreter):
        self.interpreter = interpreter
        self._scopes: list[dict[str, bool]] = []
        self._curr_func = FunctionType.NONE

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
        # NOTE: use context manager
        self._begin_scope()
        self.resolve(stmt.statements)
        self._end_scope()

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
            raise LoxRuntimeError(stmt.keyword, "Cannot return from top-level code.")
        if stmt.value:
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
        self._declare(stmt.name)
        self._define(stmt.name)

    def visit_VarExpr(self, expr: VarExpr):
        if self._scopes and (expr.name.lexeme in self._scopes[-1]) \
                and (not self._scopes[-1][expr.name.lexeme]):
            raise LoxRuntimeError(expr.name, "Can't read local variable in its own initializer.")

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

    def visit_GroupingExpr(self, expr: GroupingExpr):
        self._resolve(expr.inner)

    def visit_LiteralExpr(self, expr: LiteralExpr):
        pass

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
        # NOTE: use context manager
        enclosing_func = self._curr_func
        self._curr_func = func_type

        self._begin_scope()
        for param in function.params:
            self._declare(param)
            self._define(param)
        self.resolve(function.body)
        self._end_scope()

        self._curr_func = enclosing_func


    def _declare(self, name: Token):
        if not self._scopes:
            return

        scope = self._scopes[-1]
        if name.lexeme in scope:
            raise LoxRuntimeError(name, "Already a variable with this name in this scope")

        scope[name.lexeme] = False

    def _define(self, name: Token):
        if not self._scopes:
            return
        self._scopes[-1][name.lexeme] = True

    def _begin_scope(self):
        self._scopes.append(dict())

    def _end_scope(self):
        self._scopes.pop()
