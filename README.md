# Aceto

Aceto ([aˈtʃeto]) is a simple stack language that is based on a 2D Hilbert curve
grid. The name is a reference to Aceto Balsamico (balsamic vinegar), and to
[OIL](https://github.com/L3viathan/OIL). It was a birthday present for
[@sarnthil](https://github.com/sarnthil).

## Concept

A program written in Aceto consists of a square grid of characters.
The side length of that square can be any power of two, although source files
that aren't square will also work, as they will be transformed to one before
execution.

For a grid of side length 2^n, during execution the interpreter will go in the
path of a 2D Hilbert curve of grade n. The starting point is the bottom left
corner.

Every character corresponds to a command. There are many commands, most of them
are concerned with the manipulation of a stack. Aceto comes with an unlimited
amount of stacks, one of which is the active stack (by default 0). There is also
a quick storage, which is persistent and can only hold one thing at a time.

## Example

As an example, let's look at the following code:

    5+24
    *cp+
    6+ v
    37 p

Without knowing the corresponding Hilbert curve, this can be hard to read. But
when you put the code on top of a picture of a grade 2 Hilbert curve, it starts
getting easier to understand at least the code flow:

![Example code that prints "A6"](code_sample.png)

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

The colored marks generally mean that the number of elements in all stacks
together is ![#c5f015](https://placehold.it/15/c5f015/000000?text=+) increasing,
![#f03c15](https://placehold.it/15/f03c15/000000?text=+) decreasing, or
![#1589F0](https://placehold.it/15/1589F0/000000?text=+) staying the same. In
sticky mode, or when stacks aren't sufficiently full, that can vary (for
example, `+` is normally decreasing the total number of elements by 1, but
increases them by one if the stack was empty before). There is currently one
command where the impact on total number of elements is
![#f0e788](https://placehold.it/15/f0e788/000000?text=+) undefined, because it
depends on the previous command.

### General
- ![#1589F0](https://placehold.it/15/1589F0/000000?text=+) ` ` (a space): Do
  nothing. Any undefined character will also nop.
- ![#1589F0](https://placehold.it/15/1589F0/000000?text=+) `s`: Swap the top two
  elements on the stack.
- ![#c5f015](https://placehold.it/15/c5f015/000000?text=+) `d`: Pop a value and
  push it twice (duplicate).
- ![#f03c15](https://placehold.it/15/f03c15/000000?text=+) `h`: Remove all
  values from the stack, except for the top (head).
- ![#1589F0](https://placehold.it/15/1589F0/000000?text=+) `(`, `)`: Change the
  active stack to the left or right stack relative to the currently active
  stack.
- ![#1589F0](https://placehold.it/15/1589F0/000000?text=+) `{`, `}`: Pop a value
  and push it on the stack to the left or right (but don't change which stack is
  active).
- ![#1589F0](https://placehold.it/15/1589F0/000000?text=+) `[`, `]`: Pop a
  value, move a stack to the left or right, and push it again.
- ![#1589F0](https://placehold.it/15/1589F0/000000?text=+) `k`: Make the current
  stack "sticky", i.e. when popping from it the value is not removed, only
  copied.
- ![#1589F0](https://placehold.it/15/1589F0/000000?text=+) `K`: Make the current
  stack unsticky again.
- ![#1589F0](https://placehold.it/15/1589F0/000000?text=+) `U`: Reverse the
  current stack.
- ![#1589F0](https://placehold.it/15/1589F0/000000?text=+) `q`: Pop an item and
  insert it at the bottom of the stack.
- ![#1589F0](https://placehold.it/15/1589F0/000000?text=+) `Q`: Remove an item
  from the bottom of the stack and push it.
- ![#1589F0](https://placehold.it/15/1589F0/000000?text=+) `Y`: Shuffle the
  current stack.
- ![#1589F0](https://placehold.it/15/1589F0/000000?text=+) `X`: Exit the
  interpreter abruptly.
- ![#f03c15](https://placehold.it/15/f03c15/000000?text=+) `x`: Pop a value and
  ignore it.
- ![#f03c15](https://placehold.it/15/f03c15/000000?text=+) `ø`: Empty the
  current stack.

### Movement, Conditions, and Catching
- ![#1589F0](https://placehold.it/15/1589F0/000000?text=+) `<`, `>`, `v`, `^`:
  Special commands that make the interpreter ignore the shape of the Hilbert
  curve for this turn and instead move in the direction indicated by the
  character. With all of these commands, if the movement would cause the new
  position to be outside of the grid, it wraps around and appears on the other
  side.
- ![#1589F0](https://placehold.it/15/1589F0/000000?text=+) `W`, `E`, `S`, `N`:
  Like `<>v^`, but turn clockwise after execution.
- ![#1589F0](https://placehold.it/15/1589F0/000000?text=+) `u`: Reverse the
  direction the IP is moving.
- ![#1589F0](https://placehold.it/15/1589F0/000000?text=+) `?`: Move in a random
  direction.
- ![#f03c15](https://placehold.it/15/f03c15/000000?text=+) `|`, `_`: Special
  commands that make the interpreter ignore the shape of the Hilbert curve for
  this turn and instead move to the point on the grid mirrored
  vertically/horizontally, but only if the popped value is truthy.
- ![#f03c15](https://placehold.it/15/f03c15/000000?text=+) `#`: Like `|`/`_`,
  but mirrors both vertically and horizontally.
- ![#1589F0](https://placehold.it/15/1589F0/000000?text=+) `@`: Set the current
  cell to the catch cell. When a (normal) error occurs, jump here.
- ![#1589F0](https://placehold.it/15/1589F0/000000?text=+) `&`: Manually raise
  an error.
- ![#f03c15](https://placehold.it/15/f03c15/000000?text=+) `$`: Pop a value and
  assert that it is truthy. Otherwise, raise an error.
- ![#1589F0](https://placehold.it/15/1589F0/000000?text=+) `O`: Jump to the
  origin (0,0 or the bottom right cell, if the direction is reversed)
- ![#1589F0](https://placehold.it/15/1589F0/000000?text=+) `;`: Jump to the
  end (the bottom right cell, or 0,0, if the direction is reversed).
- ![#f03c15](https://placehold.it/15/f03c15/000000?text=+) `j`: Pop a value and
  jump so many positions ahead. Also works with negative numbers.
- ![#f03c15](https://placehold.it/15/f03c15/000000?text=+) `§`: Pop a value and
  jump to the absolute position of that value.
- ![#f03c15](https://placehold.it/15/f03c15/000000?text=+) `` ` ``: Pops a
  value: If it's truthy, behaves like a space (nop), if not, like a backslash
  (escape).

### Arithmetics and Comparisons
- ![#f03c15](https://placehold.it/15/f03c15/000000?text=+) `+`, `-`, `*`, `%`:
  Perform that operation (`%` means modulo) with the top two elements of the
  stack. For operations where the order matters, the operation will take the top
  element on the stack as the second argument; i.e. `5`, `3`, `-` will leave a 2
  on the stack, not a -2.
- ![#f03c15](https://placehold.it/15/f03c15/000000?text=+) `/`, `:`: Perform
  division. `/` is integer division, `:` float division.
- ![#f03c15](https://placehold.it/15/f03c15/000000?text=+) `=`: Take two
  elements a and b from the stack and put the result of `a==b` on the stack (a
  boolean value).
- ![#f03c15](https://placehold.it/15/f03c15/000000?text=+) `m`: Take two
  elements a and b from the stack and put the result of `a>b` on the stack (a
  boolean value).
- ![#f03c15](https://placehold.it/15/f03c15/000000?text=+) `w`: Take two
  elements a and b from the stack and put the result of `a<=b` on the stack (a
  boolean value).
- ![#1589F0](https://placehold.it/15/1589F0/000000?text=+) `I`: Pop a value,
  increment it, and push it.
- ![#1589F0](https://placehold.it/15/1589F0/000000?text=+) `D`: Pop a value,
  decrement it, and push it.
- ![#1589F0](https://placehold.it/15/1589F0/000000?text=+) `!`: Push the
  negation of a popped value.
- ![#1589F0](https://placehold.it/15/1589F0/000000?text=+) `~`: Invert the
  popped element and push it. Will also negate booleans and reverse strings.
- ![#1589F0](https://placehold.it/15/1589F0/000000?text=+) `y`: Push the sign of
  a popped element (1 for positive numbers, -1 for negative numbers, 0
  otherwise).
- ![#f03c15](https://placehold.it/15/f03c15/000000?text=+) `A`: Take two
  elements a and b from the stack and put the result of `a&b` (bitwise AND) on
  the stack.
- ![#f03c15](https://placehold.it/15/f03c15/000000?text=+) `V`: Take two
  elements a and b from the stack and put the result of `a|b` (bitwise OR) on
  the stack.
- ![#f03c15](https://placehold.it/15/f03c15/000000?text=+) `H`: Take two
  elements a and b from the stack and put the result of `a^b` (bitwise XOR) on
  the stack.
- ![#1589F0](https://placehold.it/15/1589F0/000000?text=+) `a`: Push the result
  of bitwise NOT of the popped element on the stack.
- ![#f03c15](https://placehold.it/15/f03c15/000000?text=+) `«`, `»`: Pop the top
  element (x) and the next element (y), and push `y<<x` (for `«`) or `y>>x` (for
  `»`).
- ![#f03c15](https://placehold.it/15/f03c15/000000?text=+) `F`: Raise the second
  popped number by the power of the first.
- ![#1589F0](https://placehold.it/15/1589F0/000000?text=+) `±`: Push the
  absolute value of a popped value.

### Literals
- ![#c5f015](https://placehold.it/15/c5f015/000000?text=+) `0`, `1`, `2`, ...,
  `9`: Push that number on the active stack.
- ![#c5f015](https://placehold.it/15/c5f015/000000?text=+) `"`: Starts a string
  literal. This works pretty much like in other languages. String literals are
  terminated with another `"`, but escaping (with a backslash) works too. That
  means that `"\"Hello\\World\n" will result in `"Hello\World\n`, where the `\n`
  is a newline character (`\t` is also supported). The resulting string will be
  pushed on the active stack.
- ![#c5f015](https://placehold.it/15/c5f015/000000?text=+) `'`: Starts a
  character literal. The next character will be pushed on the stack as a string.
  Escaping (for `\n`, `\t`, and `\\`) also works, but not for `\'`, because `''`
  will already accomplish the desired effect (push a single quote character).

### String methods
- ![#f03c15](https://placehold.it/15/f03c15/000000?text=+) `J`: Join the top two
  elements as a string.
- ![#1589F0](https://placehold.it/15/1589F0/000000?text=+) `~`: Reverse a string
  on top of the stack. Will also negate booleans and invert integers.
- ![#f03c15](https://placehold.it/15/f03c15/000000?text=+) `F`: Pop an integer,
  then a string. Push `that_string[that_integer]`.
- ![#f03c15](https://placehold.it/15/f03c15/000000?text=+) `¥`: Implode a
  string: Replace the stack with all of its elements, joined by empty spaces,
  casted to strings, top to bottom.
- ![#c5f015](https://placehold.it/15/c5f015/000000?text=+) `€`: Explode a
  string: Pop a string, and push all of its characters in reverse (such that the
  top stack element will be the first character).
- ![#f0e788](https://placehold.it/15/f0e788/000000?text=+) `-`: Split a string
  on whitespace.
- ![#f0e788](https://placehold.it/15/f0e788/000000?text=+) `:`: Split a string
  on another string (`['foo,bar,bat', ',']` → `['bat', 'bar', 'foo']`).
- ![#f03c15](https://placehold.it/15/f03c15/000000?text=+) `/`: Push the number
  of regex matches of the first popped value in the second.
- ![#f03c15](https://placehold.it/15/f03c15/000000?text=+) `%`: Push the third
  popped value, but with all instances of the regex in the second popped value
  replaced with the first popped value.
- ![#f0e788](https://placehold.it/15/f0e788/000000?text=+) `a`: Push all
  matching strings of the first popped element in the second popped element.

### Casting
- ![#1589F0](https://placehold.it/15/1589F0/000000?text=+) `i`: Pop a value,
  cast it to an integer (if possible, otherwise to 0), and put the result on the
  stack.
- ![#1589F0](https://placehold.it/15/1589F0/000000?text=+) `f`: Like `i`, but
  with float.
- ![#1589F0](https://placehold.it/15/1589F0/000000?text=+) `b`: Like `i`, but
  with bool.
- ![#1589F0](https://placehold.it/15/1589F0/000000?text=+) `∑`: Like `i`, but
  with string.
- ![#1589F0](https://placehold.it/15/1589F0/000000?text=+) `c`: Pop a value,
  convert it to the character of the unicode value and push it. If the value
  doesn't correspond to a unicode codepoint, push `U+FFFD` instead.
- ![#1589F0](https://placehold.it/15/1589F0/000000?text=+) `o`: The opposite of
  `c`; Pop a character and convert it to the number of its unicode codepoint and
  push the result. When anything fails, push a 0 instead.

### I/O
- ![#f03c15](https://placehold.it/15/f03c15/000000?text=+) `p`: Print the
  element on the stack.
- ![#f03c15](https://placehold.it/15/f03c15/000000?text=+) `B`: Print the
  element in quick storage.
- ![#c5f015](https://placehold.it/15/c5f015/000000?text=+) `r`: Read a string
  from the user and put it on the stack.
- ![#1589F0](https://placehold.it/15/1589F0/000000?text=+) `n`: Print a newline.
- ![#c5f015](https://placehold.it/15/c5f015/000000?text=+) `,`: Get a single
  character (without requiring a newline).

### Special
- ![#1589F0](https://placehold.it/15/1589F0/000000?text=+) `\`: Escapes the next
  character: It will be ignored.
- ![#c5f015](https://placehold.it/15/c5f015/000000?text=+) `P`, `e`, `R`: Push
  π, 𝑒, or a random float between 0 and 1.
- ![#f0e788](https://placehold.it/15/f0e788/000000?text=+) `.`: Repeat the
  previous command.
- ![#1589F0](https://placehold.it/15/1589F0/000000?text=+) `T`: Set the global
  timestamp to now. It is initialized to the time of script start.
- ![#c5f015](https://placehold.it/15/c5f015/000000?text=+) `t`: Push the
  difference between now and the global timestamp.
- ![#c5f015](https://placehold.it/15/c5f015/000000?text=+) `™`: Push a local,
  datetime on the stack (year, month, day, hour, minute, second).
- ![#1589F0](https://placehold.it/15/1589F0/000000?text=+) `C`: Pop a value and
  push a boolean: Whether the value is contained in the current stack.
- ![#c5f015](https://placehold.it/15/c5f015/000000?text=+) `l`: Push the length
  of the current stack.
- ![#c5f015](https://placehold.it/15/c5f015/000000?text=+) `L`: Load the value
  of the quick memory (initially an empty string) and push it on the stack.
- ![#f03c15](https://placehold.it/15/f03c15/000000?text=+) `M`: Pop a value and
  memorize it in the quick memory.
- ![#c5f015](https://placehold.it/15/c5f015/000000?text=+) `z`: Pop a value and
  push a decreasing range on the stack: A popped `5` will push `5`, `4`, `3`,
  `2`, `1`. Also works with negative numbers, in which case it will count up to
  `-1`.
- ![#c5f015](https://placehold.it/15/c5f015/000000?text=+) `Z`: Pop a value and
  push an increasing range on the stack: A popped `5` will push `1`, `2`, `3`,
  `4`, `5`. Also works with negative numbers, in which case it will count down
  from `-1`.
- ![#1589F0](https://placehold.it/15/1589F0/000000?text=+) `g`: Sort the top two
  elements of the stack (ascending)
- ![#1589F0](https://placehold.it/15/1589F0/000000?text=+) `G`: Sort the top two
  elements of the stack (descending)
- ![#c5f015](https://placehold.it/15/c5f015/000000?text=+) `×`: Multiply the
  stack by the top element (`[1,2,3]` becomes `[1,2,1,2,1,2]`).
