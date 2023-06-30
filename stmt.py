from dataclasses import dataclass

from expr import Expr
from visitor import Visitor


class Stmt:
    def accept(self, visitor: Visitor):
        return visitor.visit(self)


@dataclass
class ExpressionStmt(Stmt):
    expr: Expr


@dataclass
class PrintStmt(Stmt):
    expr: Expr
