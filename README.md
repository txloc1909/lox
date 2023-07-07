# Tree-walk interpreter for the Lox programming language, written in Python3.11

## Requirements

### Runtime requirements
Only `python>=3.11`

### Development requirements
```
pip install -r requirements-dev.txt
```

## Roadmap
- Set up tests for pylox
- Implement challenges for pylox
- Pythonic scanner
    - Use generator pattern
    - Or, a separate `Cursor` for traversing source code
    - Record both token line AND column number
- Re-consider another approach instead of visitor pattern
- Implement `Environment` as a persistent data structure,
  as a replacement for environment chaining

## Challenges from the book
- [ ] Scanner: support C-style block comments `/* ... */`, but not allow nesting
- [ ] Parser: support C comma operator
- [ ] Parser: support ternary operator
- [ ] Parser: add error productions to handle each binary operator appearing
      without a left-hand operand. Report as an error, but also parse and discard
      the right-hand operand with the appropriate precedence
- [ ] Extend '+' operator: if either operand is a string, then the operator
      become string concatenation
- [ ] Detect and report division-by-zero as a runtime error
- [ ] Allow the REPL to accept both statement and expression
- [ ] Accessing uninitialized variable raise a runtime error
- [ ] Control flow: support `break` (and probably `continue`) in loops
- [ ] Functions: support anonymous functions / lambdas
- [ ] Resolver: report an error if a local variable is never used
- [ ] Resolver: extend to associate an unique index for each local variable
      declared in a scope. When resolving, lookup both the scope and its index,
      store. In the interpreter, use both info to quickly lookup, instead of using
      a map
- [ ] Class: support static methods using metaclass approach
- [ ] Class: support getter methods
