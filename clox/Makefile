CC=gcc
CFLAGS=-Wall -Wextra -Og -g -fsanitize=address -fsanitize=undefined -fno-omit-frame-pointer
LDFLAGS= -Og -g -fsanitize=address -fsanitize=undefined
LDLIBS=-lm

SOURCES := $(wildcard *.c)
OBJECTS := $(patsubst %.c,%.o,$(SOURCES))
DEPENDS := $(patsubst %.c,%.d,$(SOURCES))

.PHONY: all clean run

all: run

clean:
	rm $(OBJECTS) $(DEPENDS) clox

clox: $(OBJECTS)
	$(CC) $(LDFLAGS) -o $@ $^ $(LDLIBS)

-include $(DEPENDS)

%.o: %.c Makefile
	$(CC) $(CFLAGS) -MMD -MP -c -o $@ $<

run: clox
	./clox
