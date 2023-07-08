#include "common.h"
#include "chunk.h"
#include "debug.h"
#include "vm.h"


int main(int argc, const char* argv[]) {
    initVM();
    const int line = 1;
    Chunk chunk;
    initChunk(&chunk);

    int constant = addConstant(&chunk, 1.2);
    writeChunk(&chunk, OP_CONSTANT, line);
    writeChunk(&chunk, constant, line);

    constant = addConstant(&chunk, 3.4);
    writeChunk(&chunk, OP_CONSTANT, line);
    writeChunk(&chunk, constant, line);

    writeChunk(&chunk, OP_ADD, line);

    constant = addConstant(&chunk, 5.6);
    writeChunk(&chunk, OP_CONSTANT, line);
    writeChunk(&chunk, constant, line);

    writeChunk(&chunk, OP_SUBTRACT, line);

    writeChunk(&chunk, OP_NEGATE, line);

    writeChunk(&chunk, OP_RETURN, line);

    // disassembleChunk(&chunk, "test chunk");
    interpret(&chunk);

    freeVM();
    freeChunk(&chunk);
    return 0;
}

