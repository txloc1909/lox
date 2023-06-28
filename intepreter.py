from _token import Token, TokenType
from expr import Visitor, Expr, Binary, Grouping, Literal, Unary
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

    def evaluate(self, expr: Expr):
        return expr.accept(self)

    def interpret(self, expr: Expr):
        try:
            value = self.evaluate(expr)
            print(stringify(value))
        except LoxRuntimeError as e:
            print(e)

    def visit(self, expr: Expr):
        return getattr(self, f"visit_{type(expr).__name__}")(expr)

    def visit_Literal(self, expr: Literal):
        return expr.value

    def visit_Grouping(self, expr: Grouping):
        return self.evaluate(expr.inner)

    def visit_Unary(self, expr: Unary):
        right = self.evaluate(expr.right)

        match expr.operator.type_:
            case TokenType.MINUS:
                check_number_operand(expr.operator, right)
                return -float(right)
            case TokenType.BANG:
                return not bool(right)
            case _:
                return None

    def visit_Binary(self, expr: Binary):
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

    expr1 = Binary(
        left=Literal(2.0),
        operator=Token(TokenType.STAR, "*", None, 1),
        right=Grouping(
            inner=Binary(
                left=Literal(3.0),
                operator=Token(TokenType.SLASH, "/", None, 1),
                right=Unary(
                    operator=Token(TokenType.MINUS, "-", None, 1),
                    right=Literal(12.12),
                ),
            )
        ),
    )

    expr2 = Unary(
        # operator=Token(TokenType.BANG, "!", None, 1),
        operator=Token(TokenType.MINUS, "-", None, 1),
        right=Literal(12.0),
    )

    interpreter = Interpreter()
    interpreter.interpret(expr1)
    interpreter.interpret(expr2)
