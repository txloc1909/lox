from dataclasses import dataclass
from typing import Optional

from _token import Token
from expr import Expr
from visitor import Visitor


class Stmt:
    def accept(self, visitor: Visitor):
        return visitor.visit(self)


@dataclass(frozen=True, slots=True)
class ExpressionStmt(Stmt):
    expr: Expr


@dataclass(frozen=True, slots=True)
class PrintStmt(Stmt):
    expr: Expr


@dataclass(frozen=True, slots=True)
class VarStmt(Stmt):
    name: Token
    initializer: Optional[Expr]


@dataclass(frozen=True, slots=True)
class BlockStmt(Stmt):
    statements: list[Stmt]


@dataclass(frozen=True, slots=True)
class IfStmt(Stmt):
    condition: Expr
    then_branch: Stmt
    else_branch: Optional[Stmt]


@dataclass(frozen=True, slots=True)
class WhileStmt(Stmt):
    condition: Expr
    body: Stmt


@dataclass(frozen=True, slots=True)
class FunctionStmt(Stmt):
    name: Token
    params: list[Token]
    body: list[Stmt]


@dataclass(frozen=True, slots=True)
class ReturnStmt(Stmt):
    keyword: Token
    value: Optional[Expr]
