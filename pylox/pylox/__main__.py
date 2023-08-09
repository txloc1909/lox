import sys
from functools import partial

from pylox import PyLox


def _main(args):
    if len(args) > 2:
        print("Usage: ./lox [script]")
        sys.exit(65)
    elif len(args) == 2:
        PyLox().run_file(args[1])
    else:
        PyLox().run_prompt()


main = partial(_main, sys.argv)

if __name__ == "__main__":
    main()
