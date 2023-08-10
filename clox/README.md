# Bytecode VM for the Lox programming language

## clox-specific roadmap
- [ ] VM: Encourage C compiler to put `ip` in a register. Measure the speedup
- [x] Hash table: refactor the use of tombstone slot -> make code more readable
- [x] Native func: add arity checking for native func
- [ ] Native func: signal runtime error from native func
- [x] Chunk: change encoding of line infomation to run-length encoding
- [ ] Chunk: implement `OP_CONSTANT_LONG` storing 24-bit constant

## Notable branches
- `clox/trace-parser` at `1b89a0b`: trace execution of the Pratt parser
