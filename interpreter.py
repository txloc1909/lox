from _token import Token, TokenType
from expr import Expr, BinaryExpr, GroupingExpr, LiteralExpr, UnaryExpr, VarExpr, AssignExpr
from stmt import Stmt, ExpressionStmt, PrintStmt, VarStmt
from visitor import Visitor
from environment import Environment
from error_handling import LoxRuntimeError


def check_number_operand(operator: Token, operand):
    if isinstance(operand, float):
        return
    else:
        raise LoxRuntimeError(operator, "Operand must be a number.")


def check_number_operands(operator: Token, left, right):
    if isinstance(left, float) and isinstance(right, float):
        return
    else:
        raise LoxRuntimeError(operator, "Operands must be numbers.")


def stringify(value):
    if value is None:
        return "nil"
    elif isinstance(value, float):
        s = str(value)
        if s.endswith(".0"):
            s = s[:-2]
        return s
    elif isinstance(value, bool):
        return "true" if value else "false"
    else:
        return str(value)


class Interpreter:

    def __init__(self):
        self._env = Environment()

    def evaluate(self, expr: Expr):
        return expr.accept(self)

    def execute(self, stmt: Stmt):
        return stmt.accept(self)

    def interpret(self, statements: list[Stmt]):
        try:
            for s in statements:
                self.execute(s)
        except LoxRuntimeError as e:
            print(e)

    def visit(self, visitee: Expr | Stmt):
        return getattr(self, f"visit_{type(visitee).__name__}")(visitee)

    def visit_ExpressionStmt(self, stmt: ExpressionStmt):
        self.evaluate(stmt.expr)
        return None

    def visit_PrintStmt(self, stmt: PrintStmt):
        value = self.evaluate(stmt.expr)
        print(stringify(value))
        return None

    def visit_VarStmt(self, stmt: VarStmt):
        if stmt.initializer:
            value = self.evaluate(stmt.initializer)
        else:
            value = None

        self._env.define(stmt.name.lexeme, value)

    def visit_VarExpr(self, expr: VarExpr):
        return self._env.get(expr.name)

    def visit_AssignExpr(self, expr: AssignExpr):
        value = self.evaluate(expr.value)
        self._env.assign(expr.name, value)
        return value

    def visit_LiteralExpr(self, expr: LiteralExpr):
        return expr.value

    def visit_GroupingExpr(self, expr: GroupingExpr):
        return self.evaluate(expr.inner)

    def visit_UnaryExpr(self, expr: UnaryExpr):
        right = self.evaluate(expr.right)

        match expr.operator.type_:
            case TokenType.MINUS:
                check_number_operand(expr.operator, right)
                return -float(right)
            case TokenType.BANG:
                return not bool(right)
            case _:
                return None

    def visit_BinaryExpr(self, expr: BinaryExpr):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        match expr.operator.type_:
            case TokenType.MINUS:
                check_number_operands(expr.operator, left, right)
                return left - right
            case TokenType.SLASH:
                check_number_operands(expr.operator, left, right)
                return left / right
            case TokenType.STAR:
                check_number_operands(expr.operator, left, right)
                return left * right
            case TokenType.PLUS:
                if isinstance(left, float) and isinstance(right, float):
                    return left + right
                elif isinstance(left, str) and isinstance(right, str):
                    return left + right
                else:
                    raise LoxRuntimeError(expr.operator, "Operands must be two numbers or two strings")
            case TokenType.GREATER:
                check_number_operands(expr.operator, left, right)
                return left > right
            case TokenType.GREATER_EQUAL:
                check_number_operands(expr.operator, left, right)
                return left >= right
            case TokenType.LESS:
                check_number_operands(expr.operator, left, right)
                return left < right
            case TokenType.LESS_EQUAL:
                check_number_operands(expr.operator, left, right)
                return left <= right
            case TokenType.BANG_EQUAL:
                return left != right
            case TokenType.EQUAL_EQUAL:
                return left == right
            case _:
                return None


if __name__ == "__main__":
    assert issubclass(Interpreter, Visitor)

    expr1 = BinaryExpr(
        left=LiteralExpr(2.0),
        operator=Token(TokenType.STAR, "*", None, 1),
        right=GroupingExpr(
            inner=BinaryExpr(
                left=LiteralExpr(3.0),
                operator=Token(TokenType.SLASH, "/", None, 1),
                right=UnaryExpr(
                    operator=Token(TokenType.MINUS, "-", None, 1),
                    right=LiteralExpr(12.12),
                ),
            )
        ),
    )

    expr2 = UnaryExpr(
        # operator=Token(TokenType.BANG, "!", None, 1),
        operator=Token(TokenType.MINUS, "-", None, 1),
        right=LiteralExpr(12.0),
    )

    interpreter = Interpreter()
    interpreter.interpret(expr1)
    interpreter.interpret(expr2)
