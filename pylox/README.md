# Tree-walk interpreter for the Lox programming language, written in Python

## Requirements

### Runtime requirements
Only `python>=3.10`

### Development requirements
```
pip install -r requirements-dev.txt
```

## pylox-specific roadmap
- [ ] Resolver: extend to associate an unique index for each local variable
      declared in a scope. When resolving, lookup both the scope and its index,
      store. In the interpreter, use both info to quickly lookup, instead of using
      a map
- [x] Scanner: record both token line AND column number
- [ ] Scanner: scanning on demand, using generator/iterator pattern
- [x] Remove visitor pattern
