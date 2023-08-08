from scanner import TokenType, Token
from expr import Expr, BinaryExpr, GroupingExpr, LiteralExpr, UnaryExpr


class ASTPrinter:

    def print(self, expr: Expr):
        return getattr(self, f"visit_{type(expr).__name__}")(expr)

    def visit_BinaryExpr(self, expr: BinaryExpr) -> str:
        return self._parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_GroupingExpr(self, expr: GroupingExpr) -> str:
        return self._parenthesize("group", expr.inner)

    def visit_LiteralExpr(self, expr: LiteralExpr) -> str:
        return "nil" if expr.value is None else str(expr.value)

    def visit_UnaryExpr(self, expr: UnaryExpr) -> str:
        return self._parenthesize(expr.operator.lexeme, expr.right)

    def _parenthesize(self, name: str, *exprs: Expr) -> str:
        return f"({name} " + " ".join(self.print(e) for e in exprs) + ")"


if __name__ == "__main__":
    test_expression = BinaryExpr(
        left=UnaryExpr(
            Token(TokenType.MINUS, "-", None, 1),
            LiteralExpr(value=123),
        ),
        operator=Token(TokenType.STAR, "*", None, 1),
        right=GroupingExpr(inner=LiteralExpr(value=45.67)),
    )

    print(ASTPrinter().print(test_expression))
