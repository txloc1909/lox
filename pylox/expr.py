from dataclasses import dataclass

from scanner import Token
from visitor import Visitor


class Expr:
    def accept(self, visitor: Visitor):
        return visitor.visit(self)


@dataclass(frozen=True, slots=True)
class BinaryExpr(Expr):
    left: Expr
    operator: Token
    right: Expr


@dataclass(frozen=True, slots=True)
class GroupingExpr(Expr):
    inner: Expr


@dataclass(frozen=True, slots=True)
class LiteralExpr(Expr):
    value: float | str | bool | None


@dataclass(frozen=True, slots=True)
class UnaryExpr(Expr):
    operator: Token
    right: Expr


@dataclass(frozen=True, slots=True)
class VarExpr(Expr):
    name: Token


@dataclass(frozen=True, slots=True)
class AssignExpr(Expr):
    name: Token
    value: Expr


@dataclass(frozen=True, slots=True)
class LogicalExpr(Expr):
    left: Expr
    operator: Token
    right: Expr


@dataclass(frozen=True, slots=True)
class CallExpr(Expr):
    callee: Expr
    paren: Token    # store the closing paren, for error handling
    arguments: tuple[Expr, ...]


@dataclass(frozen=True, slots=True)
class GetExpr(Expr):
    obj: Expr
    name: Token


@dataclass(frozen=True, slots=True)
class SetExpr(Expr):
    obj: Expr
    name: Token
    value: Expr


@dataclass(frozen=True, slots=True)
class ThisExpr(Expr):
    keyword: Token


@dataclass(frozen=True, slots=True)
class SuperExpr(Expr):
    keyword: Token
    method: Token
