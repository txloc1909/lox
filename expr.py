from dataclasses import dataclass

from scanner import Token
from visitor import Visitor


class Expr:
    def accept(self, visitor: Visitor):
        return visitor.visit(self)


@dataclass
class BinaryExpr(Expr):
    left: Expr
    operator: Token
    right: Expr


@dataclass
class GroupingExpr(Expr):
    inner: Expr


@dataclass
class LiteralExpr(Expr):
    value: float | str | bool | None


@dataclass
class UnaryExpr(Expr):
    operator: Token
    right: Expr


@dataclass
class VarExpr(Expr):
    name: Token


@dataclass
class AssignExpr(Expr):
    name: Token
    value: Expr


@dataclass
class LogicalExpr(Expr):
    left: Expr
    operator: Token
    right: Expr


@dataclass
class CallExpr(Expr):
    callee: Expr
    paren: Token    # store the closing paren, for error handling
    arguments: list[Expr]
