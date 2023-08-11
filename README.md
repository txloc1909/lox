# Implementations of the Lox programming language

From the book [Crafting Interpreters](https://craftinginterpreters.com)
by Robert Nystrom.

- pylox: tree-walk interpreter
- clox: bytecode virtual machine

## Roadmap for language features

### Do-able
- [ ] REPL print value evaluated by expression
- [ ] C-style block comments, without nesting
- [ ] Native function: `hasField` `getField` `setField` `deleteField`

### Considering
- [ ] REPL with `readline` support
- [ ] `break` and `continue` in `while` & `for` loop
- [ ] Operator + do concat when either operand is string OR support string
      interpolation
- [ ] Anonymous function / `lambda`
- [ ] Ternary operator
- [ ] Extend comparison between strings
- [ ] Traits for multi-inheritance
- [ ] Switch-case statement: with or without `break` and fallthrough?
- [ ] Class: support static methods using metaclass approach
- [ ] Class: support getter methods

### Useful features
- [ ] General data structures: list/array, map/dictionary
    - Alternatively, implement fixed-size array as the only native data
      structure, then implement others on top of it
- [ ] Read/write to file
    - [ ] text file
    - [ ] binary file
