# Tree-walk interpreter for the Lox programming language, written in Python3.11

## Requirements

### Runtime requirements
Only `python>=3.11`

### Development requirements
```
pip install -r requirements-dev.txt
```

## pylox-specific roadmap
- [ ] Parser: add error productions to handle each binary operator appearing
      without a left-hand operand. Report as an error, but also parse and discard
      the right-hand operand with the appropriate precedence
- [ ] Resolver: accessing uninitialized variable raise a runtime error
- [ ] Resolver: report an error if a local variable is never used
- [ ] Resolver: extend to associate an unique index for each local variable
      declared in a scope. When resolving, lookup both the scope and its index,
      store. In the interpreter, use both info to quickly lookup, instead of using
      a map
- [ ] Pythonic scanner
  - [ ] Use generator pattern
  - [ ] Or, a separate `Cursor` for traversing source code
  - [ ] Record both token line AND column number
- [ ] Re-consider another approach instead of visitor pattern
- [ ] Implement `Environment` as a persistent data structure,
      as a replacement for environment chaining
