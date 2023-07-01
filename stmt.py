from dataclasses import dataclass
from typing import Optional

from _token import Token
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


@dataclass
class VarStmt(Stmt):
    name: Token
    initializer: Optional[Expr]


@dataclass
class BlockStmt(Stmt):
    statements: list[Stmt]

@dataclass
class IfStmt(Stmt):
    condition: Expr
    then_branch: Stmt
    else_branch: Stmt
