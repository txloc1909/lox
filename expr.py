from dataclasses import dataclass
from typing import Protocol, runtime_checkable
from numbers import Real

from scanner import Token


@runtime_checkable
class Visitor(Protocol):
    def visit(self, expr):
        '''
        Dynamically dispatching according to the type of `expr`
        '''
        pass


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
