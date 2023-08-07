CC=gcc

# Flags for debug build
# CFLAGS=-Wall -Wextra -Wno-unused-parameter -std=c99 -Og -g -fsanitize=address -fsanitize=undefined -fno-omit-frame-pointer
# LDFLAGS=-Og -g -fsanitize=address -fsanitize=undefined

# Flags for release build
CFLAGS=-Wall -Wextra -Wno-unused-parameter -std=c99 -O3 -flto -march=native
LDFLAGS=-O3 -flto -march=native

LDLIBS=-lm

SRC_DIR=src/
BUILD_DIR=build/
DEPS_DIR=$(BUILD_DIR)deps/
OBJS_DIR=$(BUILD_DIR)objs/
MAIN_TARGET=$(BUILD_DIR)clox

SOURCES := $(wildcard $(SRC_DIR)*.c)
OBJECTS := $(SOURCES:$(SRC_DIR)%.c=$(OBJS_DIR)%.o)
DEPENDS := $(SOURCES:$(SRC_DIR)%.c=$(DEPS_DIR)%.d)

.PHONY: all build run clean

all: build

build: $(MAIN_TARGET)

run: build
	$(MAIN_TARGET) example.lox

cleanobj:
	rm -df $(OBJECTS)

cleandeps:
	rm -df $(DEPENDS)

cleanmain:
	rm -f $(MAIN_TARGET)

clean: cleanobj cleandeps cleanmain

$(MAIN_TARGET): $(OBJECTS) | $(BUILD_DIR)
	$(CC) $(LDFLAGS) -o $@ $^ $(LDLIBS)

$(BUILD_DIR) $(DEPS_DIR) $(OBJS_DIR):
	mkdir -p $@

$(DEPENDS): $(DEPS_DIR)%.d: $(SRC_DIR)%.c | $(DEPS_DIR)
	$(CC) $(CFLAGS) -MM -MT $(@:$(DEPS_DIR)%.d=$(OBJS_DIR)%.o) -MT $@ -MP -MF $@ $<

-include $(DEPENDS)

$(OBJECTS): $(OBJS_DIR)%.o: $(SRC_DIR)%.c | $(OBJS_DIR)
	$(CC) $(CFLAGS) -c -o $@ $<
