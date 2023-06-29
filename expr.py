from dataclasses import dataclass

from scanner import Token
from visitor import Visitor


class Expr:
    def accept(self, visitor: Visitor):
        return visitor.visit(self)


@dataclass
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr


@dataclass
class Grouping(Expr):
    inner: Expr


@dataclass
class Literal(Expr):
    value: float | str | bool | None


@dataclass
class Unary(Expr):
    operator: Token
    right: Expr
