# Implementations of the Lox programming language

From the book [Crafting Interpreters](https://craftinginterpreters.com)
by Robert Nystrom.

- pylox: tree-walk interpreter
- clox: bytecode virtual machine

## Roadmap for language features

### Do-able
- [ ] REPL print value evaluated by expression
- [ ] `break` and `continue` in `while` & `for` loop
- [ ] Ternary operator
- [ ] Anonymous function / `lambda`

### Considering
- [ ] Extend comparison between strings, using lexicographical order
- [ ] Operator + do concat when either operand is string OR support string
      interpolation
- [ ] REPL with `readline` support
- [ ] Traits for multi-inheritance

### Useful features
- [ ] Native function: `hasField` `getField` `setField` `deleteField`
    - [ ] Signal runtime error from native function
- [ ] General data structures: list/array, map/dictionary
    - Alternatively, implement fixed-size array as the only native data
      structure, then implement others on top of it
- [ ] Read/write to file
    - [ ] text file
    - [ ] binary file
