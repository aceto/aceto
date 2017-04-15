# Aceto
This is Aceto v1.1.

Aceto is a simple stack language that is based on a 2D Hilbert curve grid. The
name is a reference to Aceto Balsamico (balsamic vinegar), and to
[OIL](https://github.com/L3viathan/OIL). It was a birthday present for
[@sarnthil](https://github.com/sarnthil).

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

## Example

As an example, let's look at the following code:

    5+24
    *cp+
    6+ v
    37 p

Without knowing the corresponding Hilbert curve, this can be hard to read. But
when you put the code on top of a picture of a grade 2 Hilbert curve, it starts
getting easier to understand at least the code flow:

![Example code that prints "A6"](example_small.png)

First `3` and `7` are pushed on the stack, and added, which leaves a `10` on the
stack. Next, a `6` is pushed and multiplied with the `10`, leaving a `60` on the
stack. Then, `5` is added to the number, resulting in `65`.

`c` converts the number to a character (65 is the ASCII code for `A`). `p`
prints the result. Next, we add `2` and `4`, resulting in `6`. The `v` makes the
interpreter move downwards (despite the curve). In this case, not writing the
`v` wouldn't have made a difference, because spaces do nothing. The final `p`
prints the number `6` that is on the stack.

## Installation

    git clone https://github.com/L3viathan/aceto --recursive

## Commands

Unless otherwise specified, commands that perform an action with an element from
the stack end up removing it.

### General
- ` ` (a space): Do nothing. Any undefined character will also nop.
- `s`: Swap the top two elements on the stack.
- `d`: Pop a value and push it twice (duplicate).
- `(`, `)`: Change the active stack to the left or right stack relative to the
  currently active stack.
- `{`, `}`: Pop a value and push it on the stack to the left or right (but don't
  change which stack is active).
- `X`: Exit the interpreter abruptly.
- `x`: Pop a value and ignore it.

### Movement, Conditions, and Catching
- `<`, `>`, `v`, `^`: Special commands that make the interpreter ignore the
  shape of the Hilbert curve for this turn and instead move in the direction
  indicated by the character.
- `W`, `E`, `S`, `N`: Like `<>v^`, but turn clockwise after execution.
- `u`: Reverse the direction the IP is moving.
- `?`: Move in a random direction.
- `|`, `_`: Special commands that make the interpreter ignore the shape of the
  Hilbert curve for this turn and instead move to the point on the grid mirrored
  vertically/horizontally, but only if the popped value is truthy.
- `#`: Like `|`/`_`, but mirrors both vertically and horizontally.
- `@`: Set the current cell to the catch cell. When a (normal) error occurs, jump here.
- `&`: Manually raise an error.
- `$`: Pop a value and assert that it is truthy. Otherwise, raise an error.
- `O`: Jump to the origin (0,0 or the bottom right cell, if the direction is
  reversed)

### Arithmetics and Comparisons
- `+`, `-`, `*`, `%`: Perform that operation (`%` means modulo) with the top two
  elements of the stack. For operations where the order matters, the operation
  will take the top element on the stack as the second argument; i.e. `5`, `3`,
  `-` will leave a 2 on the stack, not a -2.
- `/`, `:`: Perform division. `/` is integer division, `:` float division.
- `=`: Take two elements a and b from the stack and put the result of `a==b` on
  the stack (a boolean value).
- `I`: Pop a value, increment it, and push it.
- `D`: Pop a value, decrement it, and push it.
- `!`: Push the negation of a popped value.
- `~`: Invert the popped element and push it.

### Literals
- `0`, `1`, `2`, ..., `9`: Push that number on the active stack.
- `"`: Starts a string literal. This works pretty much like in other languages.
  String literals are terminated with another `"`, but escaping (with a
  backslash) works too. That means that `"\"Hello\\World\n" will result in
  `"Hello\World\n`, where the `\n` is a newline character (`\t` is also
  supported). The resulting string will be pushed on the active stack.
- `'`: Starts a character literal. The next character will be pushed on the
  stack as a string. Escaping (for `\n`, `\t`, and `\\`) also works, but not for
  `\'`, because `''` will already accomplish the desired effect (push a single
  quote character).

### Casting
- `i`: Pop a value, cast it to an integer (if possible, otherwise to 0), and put
the result on the stack.
- `f`: Like `i`, but with float.
- `c`: Pop a value, convert it to the character of the unicode value and push
  it. If the value doesn't correspond to a unicode codepoint, push `U+FFFD`
  instead.
- `o`: The opposite of `c`; Pop a character and convert it to the number of its
  unicode codepoint and push the result. When anything fails, push a 0 instead.

### I/O
- `p`: Print the element on the stack.
- `r`: Read a string from the user and put it on the stack.
- `n`: Print a newline.
- `,`: Get a single character (without requiring a newline).

### Special
- `\`: Escapes the next character: It will be ignored.
- `P`, `e`, `R`: Push π, 𝑒, or a random float between 0 and 1.
- `.`: Repeat the previous command.
- `T`: Set the global timestamp to now. It is initialized to the time of script
  start.
- `t`: Push the difference between now and the global timestamp.
