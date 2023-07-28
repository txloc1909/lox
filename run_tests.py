#!/usr/bin/env python3

import sys
import re
from pathlib import Path
from collections import namedtuple
import subprocess

PYLOX_EXE = "./pylox/lox"
CLOX_EXE = "./clox/clox"

EXPECTED_OUTPUT_PATTERN = re.compile(r"// expect: ?(.*)")
EXPECTED_ERROR_PATTERN = re.compile(r"// (Error.*)")
ERROR_LINE_PATTERN = re.compile(r"// \[((java|c) )?line (\d+)\] (Error.*)")
EXPECTED_RUNTIME_ERROR_PATTERN = re.compile(r"// expect runtime error: (.+)")
SYNTAX_ERROR_PATTERN = re.compile(r"\[.*line (\d+)\] (Error.+)")
STACK_TRACE_PATTERN = re.compile(r"\[line (\d+)\]")
NONTEST_PATTERN = re.compile(r"// nontest")

_n_passed = 0
_n_failed = 0
_n_skipped = 0
_expectations = 0

Suite = namedtuple("Suite", ["name", "language", "executable", "tests"])

_suite = None                   # Current suite
_custom_interpreter = None
_custom_args = []

_all_suites = {}
_c_suites = []
_py_suites = []


class term:
    '''Rudimentary ANSI terminal supporter'''

    @staticmethod
    def red(text):
        return f"\033[31m{text}\033[0m"

    @staticmethod
    def green(text):
        return f"\033[92m{text}\033[0m"

    @staticmethod
    def gray(text):
        return f"\033[30;1m{text}\033[0m"

    @staticmethod
    def pink(text):
        return f"\033[31;1m{text}\033[0m"

    @staticmethod
    def yellow(text):
        return f"\033[33;1m{text}\033[0m"

    @staticmethod
    def clear_line():
        print("\033[1000D\033[0K", end='')

    @staticmethod
    def update_line(text):
        print("\033[1000D\033[0K" + text, end='', flush=True)



ExpectedOutput = namedtuple("ExpectedOutput", ["line", "output"])

class Test:
    def __init__(self, path):
        self.path = path
        self._expected_output = []
        self._expected_errors = set()
        self._expected_runtime_error = ""
        self._runtime_error_line = 0
        self._expected_exit_code = 0
        self._failures = []

    def parse(self) -> bool:
        global _suite, _n_skipped, _expectations
        state = None    # "pass" or "skip"
        parts = str(self.path).split("/")

        subpart = ""
        for part in parts:
            if len(subpart):
                subpart += "/"
            subpart += part
            if subpart in _suite.tests:
                state = _suite.tests[subpart]

        if not state:
            raise RuntimeError(f"Unknown state for {self.path}")
        elif state == "skip":
            _n_skipped += 1
            return False

        with open(self.path, "r", encoding="utf-8") as f:
            for i, line in enumerate(f.readlines(), start=1):
                if match := NONTEST_PATTERN.search(line):
                    return False

                if match := EXPECTED_OUTPUT_PATTERN.search(line):
                    self._expected_output.append(ExpectedOutput(i, match[1]))
                    _expectations += 1
                    continue

                if match := EXPECTED_ERROR_PATTERN.search(line):
                    self._expected_errors.add(f"[{i}]")
                    self._expected_exit_code = 65
                    _expectations += 1
                    continue

                if match := ERROR_LINE_PATTERN.search(line):
                    language = match[2]
                    if not language or language == _suite.language:
                        self._expected_errors.add(f"[{match[3]}] {match[4]}")
                        self._expected_exit_code = 65
                        _expectations += 1
                    continue

                if match := EXPECTED_RUNTIME_ERROR_PATTERN.search(line):
                    self._runtime_error_line = i
                    self._expected_runtime_error = match[1]
                    self._expected_exit_code = 70
                    _expectations += 1

        if self._expected_errors and self._expected_runtime_error:
            print(f"{term.pink('TEST ERROR')} {self.path}")
            print(f"\tCannot expect both compile and runtime error.")
            print(f"")
            return False

        return True

    def run(self) -> list[str]:
        global _suite

        result = subprocess.run([_suite.executable, self.path],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)

        output_lines = result.stdout.decode("utf-8").split("\n")
        error_lines = result.stderr.decode("utf-8").split("\n")

        if self._expected_runtime_error:
            self._validate_runtime_error(error_lines)
        else:
            self._validate_compile_error(error_lines)

        self._validate_exit_code(result.returncode, error_lines)
        self._validate_output(output_lines)
        return self._failures

    def _validate_runtime_error(self, error_lines):
        pass

    def _validate_compile_error(self, error_lines):
        pass

    def _validate_output(self, output_lines):
        pass

    def _validate_exit_code(self, exit_code, error_lines):
        if exit_code == self._expected_exit_code:
            return

        if len(error_lines) > 10:
            error_lines = error_lines[:10]
            error_lines.append("(truncated...)")

        self._fail(f"Expected return code {self._expected_exit_code} Stderr:",
                   error_lines)

    def _fail(self, message, lines=None):
        self._failures.append(message)
        if lines:
            self._failures.extend(lines)


def run_test(path: Path | str):
    global _n_passed, _n_failed, _n_skipped
    if "benchmark" in str(path):
        return

    # Update status line
    term.update_line(f"Passed: {term.green(_n_passed)} " \
                     f"Failed: {term.green(_n_failed)} " \
                     f"Skipped: {term.yellow(_n_skipped)} " \
                     f"{term.gray(path)}")

    test = Test(path)
    if not test.parse():
        return

    failures = test.run()
    if not failures:
        _n_passed += 1
    else:
        _n_failed += 1
        term.clear_line()
        print(f"{term.red('FAIL')} {path}")
        for failure in failures:
            print(f"\t{term.pink(failure)}")
        print("")


def run_suite(name: str):
    global _suite, _all_suites, _n_passed, _n_failed, _n_skipped, _expectations
    _suite = _all_suites[name]
    _n_passed = 0
    _n_failed = 0
    _n_skipped = 0
    _expectations = 0

    for file_ in Path("./tests").rglob("*.lox"):
        run_test(file_)

    term.clear_line()
    if _n_failed == 0:
        print(f"All {term.green(_n_passed)} tests passed ({_expectations} expectations).")
    else:
        print(f"{term.green(_n_passed)} tests passed. {term.red(_n_failed)} tests failed.")

    return _n_failed == 0


def run_suites(names: list[str]) -> bool:
    def _run(name: str):
        global run_suite
        print(f"=== {name} ===")
        return run_suite(name)

    all_success = all(_run(name) for name in names)
    if not all_success:
        sys.exit(1)


def _define_test_suites():
    def c_suite(name: str, tests: dict[str, str]):
        global _all_suites, _c_suite
        _all_suites[name] = Suite(
                name, language="c", executable=CLOX_EXE, tests=tests)
        _c_suites.append(name)

    def py_suite(name: str, tests: dict[str, str]):
        global _all_suites, _py_suites
        _all_suites[name] = Suite(
                name, language="java",  # pylox is essentially jlox
                executable=PYLOX_EXE, tests=tests)
        _py_suites.append(name)

    all = { "tests": "pass" }

    early_chapters = {
        "tests/scanning": "skip",
        "tests/expressions": "skip",
    }
    nan_equality = { "tests/number/nan_equality.lox": "skip" }
    no_limits = { "tests/limit": "skip" }

    py_suite("pylox", all | early_chapters | nan_equality | no_limits)
    c_suite("clox", all | early_chapters)


def main(args):
    global _suite
    _define_test_suites()
    if len(args) > 2:
        sys.exit(f"Usage: {sys.argv[0]} suite")
    elif len(args) == 2:
        run_suite(args[1])
    else:
        run_suite("pylox")


if __name__ == "__main__":
    main(sys.argv)
