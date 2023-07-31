# Tree-walk interpreter for the Lox programming language, written in Python3.11

## Requirements

### Runtime requirements
Only `python>=3.11`

### Development requirements
```
pip install -r requirements-dev.txt
```

## pylox-specific roadmap
- [ ] Resolver: extend to associate an unique index for each local variable
      declared in a scope. When resolving, lookup both the scope and its index,
      store. In the interpreter, use both info to quickly lookup, instead of using
      a map
- [ ] Pythonic scanner
  - [ ] a separate `Cursor` for traversing source code
  - [ ] Record both token line AND column number
- [x] Remove visitor pattern
