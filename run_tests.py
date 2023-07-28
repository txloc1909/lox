#!/usr/bin/env python3

import sys
import re
from pathlib import Path
from collections import namedtuple
from itertools import zip_longest
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
                    self._expected_errors.add(f"[line {i}] {match[1]}")
                    self._expected_exit_code = 65
                    _expectations += 1
                    continue

                if match := ERROR_LINE_PATTERN.search(line):
                    language = match[2]
                    if not language or language == _suite.language:
                        self._expected_errors.add(f"[line {match[3]}] {match[4]}")
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
            print(f"    Cannot expect both compile and runtime error.")
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
        while len(error_lines) and error_lines[-1]:
            error_lines.pop()

        if len(error_lines) < 2:
            self._fail(f"Expected runtime error {self._expected_runtime_error} and got none.")

        if error_lines[0] != self._expected_runtime_error:
            self._fail(f"Expected runtime error {self._expected_runtime_error} and got:")
            self._fail(error_lines[0])

        stack_lines = error_lines[1:]
        matches = (STACK_TRACE_PATTERN.search(l) for l in stack_lines)
        match = next((m for m in matches if m), None)
        if not match:
            self._fail("Expected stack trace and got: ", stack_lines)
        else:
            stack_line = int(match[1])
            if stack_line != self._runtime_error_line:
                self._fail(f"Expected runtime error on line " \
                           f"{self._runtime_error_line} but was on line " \
                           f"{stack_line}.")

    def _validate_compile_error(self, error_lines):
        if len(error_lines) and not error_lines[-1]:
            error_lines.pop()

        errors_found = set()
        unexpected_count = 0
        for line in error_lines:
            if match := SYNTAX_ERROR_PATTERN.search(line):
                error = f"[line {match[1]}] {match[2]}"
                if error in self._expected_errors:
                    errors_found.add(error)
                else:
                    if unexpected_count < 10:
                        self._fail("Unexpected error:")
                        self._fail(line)
                    unexpected_count += 1
            elif len(line):
                if unexpected_count < 10:
                    self._fail("Unexpected error:")
                    self._fail(line)
                unexpected_count += 1

        if unexpected_count > 10:
            self._fail(f"(truncated {unexpected_count - 1} more...)")

        for error in self._expected_errors.difference(errors_found):
            self._fail(f"Missing expected error: {error}")


    def _validate_output(self, output_lines):
        if len(output_lines) and output_lines[-1] == "":
            output_lines.pop()

        for output, expected in zip_longest(output_lines, self._expected_output,
                                            fillvalue=None):
            if expected is None:
                self._fail(f"Got output {output} when none was expected.")
            elif output is None:
                self._fail(f"Expected output {expected.output} on line " \
                           f"{expected.line}.")
            elif expected.output != output:
                self._fail(f"Expected output {expected.output} on line " \
                           f"{expected.line} and got {output}")


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
                     f"Failed: {term.red(_n_failed)} " \
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
            print(f"    {term.pink(failure)}")
        print("")


def run_suite(name: str) -> bool:
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
