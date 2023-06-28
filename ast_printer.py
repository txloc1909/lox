from scanner import TokenType, Token
from expr import Visitor, Expr, Binary, Grouping, Literal, Unary


class ASTPrinter:

    def print(self, expr: Expr):
        return expr.accept(self)

    def visit(self, expr: Expr):
        return getattr(self, f"visit_{type(expr).__name__}")(expr)

    def visit_Binary(self, expr: Binary):
        return self._parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_Grouping(self, expr: Grouping):
        return self._parenthesize("group", expr.inner)

    def visit_Literal(self, expr: Literal):
        return "nil" if expr.value is None else str(expr.value)

    def visit_Unary(self, expr: Unary):
        return self._parenthesize(expr.operator.lexeme, expr.right)

    def _parenthesize(self, name: str, *exprs: Expr):
        return f"({name} " + " ".join(e.accept(self) for e in exprs) + ")"



if __name__ == "__main__":
    assert issubclass(ASTPrinter, Visitor)

    test_expression = Binary(
        left=Unary(
            Token(TokenType.MINUS, "-", None, 1),
            Literal(value=123),
        ),
        operator=Token(TokenType.STAR, "*", None, 1),
        right=Grouping(inner=Literal(value=45.67)),
    )

    print(ASTPrinter().print(test_expression))
