from scanner import Scanner
from parser import Parser
from resolver import Resolver
from interpreter import Interpreter
from error_handling import ErrorHandler


class PyLox:
    def __init__(self):
        self.error_handler = ErrorHandler()
        self.interpreter = Interpreter(error_handler=self.error_handler)
        self.resolver = Resolver(self.interpreter,
                                 error_handler=self.error_handler)

    def run(self, src: str):
        tokens = Scanner(src, self.error_handler).scan_tokens()
        statements = Parser(tokens, self.error_handler).parse()

        if self.error_handler.has_error:
            return

        self.resolver.resolve(statements)
        if self.error_handler.has_error:
            return

        self.interpreter.interpret(statements)

    def run_file(self, fname):
        self.run(open(fname).read())
        if self.error_handler.has_error:
            sys.exit(65)
        if self.error_handler.has_runtime_error:
            sys.exit(70)

    def run_prompt(self):
        while True:
            try:
                line = input(">>> ")
            except EOFError:
                # Ctrl-D exit the REPL
                break

            if line:
                self.run(line)
                self.error_handler.has_error = False
