# Bytecode VM for the Lox programming language

## clox-specific roadmap
- [x] VM: Encourage C compiler to put `ip` in a register. Measure the speedup
- [x] Hash table: refactor the use of tombstone slot -> make code more readable
- [x] Native func: add arity checking for native func
- [ ] Native func: signal runtime error from native func
- [x] Chunk: change encoding of line infomation to run-length encoding
- [ ] Chunk: implement `OP_CONSTANT_LONG` storing 24-bit constant
    - Note: by supporting 24-bits constant, no more limit of 255 parameters

## Notable branches
- `clox/trace-parser` at `1b89a0b`: trace execution of the Pratt parser
- `clox/register-ip` at `a89451d`: Encourage C compiler to put `ip` in a register
    - Speedup some benchmarks, make some others slower.
