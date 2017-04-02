# Aceto
Aceto is a simple stack language that is based on a 2D Hilbert curve grid. The
name is a reference to Aceto Balsamico (balsamic vinegar), and to
[OIL](https://github.com/L3viathan/OIL).

## Concept
A program written in Aceto consists of a square grid of characters. The side
length of that square can be any power of two, although source files that aren't
square will also work, as they will be transformed to one before execution.

For a grid of side length 2^n, during execution the interpreter will go in the
path of a 2D Hilbert curve of grade n. The starting point is the bottom left
corner.

Every character corresponds to a command. There are many commands, most of them
are concerned with the manipulation of a stack. Aceto comes with an unlimited
amount of stacks, one of which is the active stack (by default 0).

## Installation

    git clone https://github.com/L3viathan/aceto --recursive

## Commands

Unless otherwise specified, commands that perform an action with an element from
the stack end up removing it.

- ` ` (a space): Do nothing. Any undefined character will also nop.
- `0`, `1`, `2`, ..., `9`: Push that number on the active stack.
- `<`, `>`, `v`, `^`: Special commands that make the interpreter ignore the
  shape of the Hilbert curve for this turn and instead move in the direction
  indicated by the character.
- `+`, `-`, `*`, `%`: Perform that operation (`%` means modulo) with the top two
  elements of the stack. For operations where the order matters, the operation
  will take the top element on the stack as the second argument; i.e. `5`, `3`,
  `-` will leave a 2 on the stack, not a -2.
- `=`: Take two elements a and b from the stack and put the result of `a==b` on
  the stack (a boolean value).
- `p`: Print the element on the stack.
- `r`: Read a string from the user and put it on the stack.
- `s`: Swap the top two elements on the stack.
- `i`: Pop a value, cast it to an integer (if possible, otherwise to 0), and put
  the result on the stack.
- `f`: Like `i`, but with float.
- `I`: Pop a value, increment it, and push it.
- `D`: Pop a value, decrement it, and push it.
- `c`: Pop a value, convert it to the character of the unicode value and push
  it. If the value doesn't correspond to a unicode codepoint, push `U+FFFD`
  instead.
- `o`: The opposite of `c`; Pop a character and convert it to the number of its
  unicode codepoint and push the result. When anything fails, push a 0 instead.
- `d`: Pop a value and push it twice (duplicate).
- `(`, `)`: Change the active stack to the left or right stack relative to the
  currently active stack.
- `{`, `}`: Pop a value and push it on the stack to the left or right (but don't
  change which stack is active).
- `!`: Push the negation of a popped value.
- `X`: Exit the interpreter abruptly.
- `|`, `_`: Special commands that make the interpreter ignore the shape of the
  Hilbert curve for this turn and instead move to the point on the grid mirrored
  vertically/horizontally.
