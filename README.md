# Aceto

Aceto ([aˈtʃeto]) is a simple stack language that is based on a 2D Hilbert curve
grid. The name is a reference to Aceto Balsamico (balsamic vinegar), and to
[OIL](https://github.com/L3viathan/OIL). It was a birthday present for
[@sarnthil](https://github.com/sarnthil).


## Installation

    pip install acetolang

If your `pip` refers to Python 2's pip, instead use `pip3`. The "binary" that
will be installed is called `aceto`.

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

## Commands

The colored marks generally mean that the number of elements in all stacks
together is 🟩
increasing, 🟥
decreasing, or 🟦 staying
the same. In sticky mode, or when stacks aren't sufficiently full, that can
vary (for example, `+` is normally decreasing the total number of elements by
1, but increases them by one if the stack was empty before). There are some
commands where the impact on total number of elements is
🟨 undefined, because
they depends on the previous command.

### General
- 🟦 ` ` (a space): Do
  nothing. Any undefined character will also nop.
- 🟦 `s`: Swap the top two
  elements on the stack.
- 🟩 `d`: Pop a value and
  push it twice (duplicate).
- 🟥 `h`: Remove all
  values from the stack, except for the top (head).
- 🟦 `(`, `)`: Change the
  active stack to the left or right stack relative to the currently active
  stack.
- 🟦 `{`, `}`: Pop a value
  and push it on the stack to the left or right (but don't change which stack is
  active).
- 🟦 `[`, `]`: Pop a
  value, move a stack to the left or right, and push it again.
- 🟦 `k`: Make the current
  stack "sticky", i.e. when popping from it the value is not removed, only
  copied.
- 🟦 `K`: Make the current
  stack unsticky again.
- 🟦 `U`: Reverse the
  current stack.
- 🟦 `q`: Pop an item and
  insert it at the bottom of the stack.
- 🟦 `Q`: Remove an item
  from the bottom of the stack and push it.
- 🟦 `Y`: Shuffle the
  current stack.
- 🟦 `X`: Exit the
  interpreter abruptly.
- 🟥 `x`: Pop a value and
  ignore it.
- 🟥 `ø`: Empty the
  current stack.

### Movement, Conditions, and Catching
- 🟦 `<`, `>`, `v`, `^`:
  Special commands that make the interpreter ignore the shape of the Hilbert
  curve for this turn and instead move in the direction indicated by the
  character. With all of these commands, if the movement would cause the new
  position to be outside of the grid, it wraps around and appears on the other
  side.
- 🟦 `W`, `E`, `S`, `N`:
  Like `<>v^`, but turn clockwise after execution.
- 🟦 `u`: Reverse the
  direction the IP is moving.
- 🟦 `?`: Move in a random
  direction.
- 🟥 `|`, `_`: Special
  commands that make the interpreter ignore the shape of the Hilbert curve for
  this turn and instead move to the point on the grid mirrored
  vertically/horizontally, but only if the popped value is truthy.
- 🟥 `#`: Like `|`/`_`,
  but mirrors both vertically and horizontally.
- 🟦 `@`: Set the current
  cell to the catch cell. When a (normal) error occurs, jump here.
- 🟦 `&`: Manually raise
  an error.
- 🟥 `$`: Pop a value and
  assert that it is truthy. Otherwise, raise an error.
- 🟦 `O`: Jump to the
  origin (0,0 or the bottom right cell, if the direction is reversed)
- 🟦 `;`: Jump to the
  end (the bottom right cell, or 0,0, if the direction is reversed).
- 🟥 `j`: Pop a value and
  jump so many positions ahead. Also works with negative numbers.
- 🟥 `§`: Pop a value and
  jump to the absolute position of that value.
- 🟥 `` ` ``: Pops a
  value: If it's truthy, behaves like a space (nop), if not, like a backslash
  (escape).

### Arithmetics and Comparisons
- 🟥 `+`, `-`, `*`, `%`:
  Perform that operation (`%` means modulo) with the top two elements of the
  stack. For operations where the order matters, the operation will take the top
  element on the stack as the second argument; i.e. `5`, `3`, `-` will leave a 2
  on the stack, not a -2.
- 🟥 `/`, `:`: Perform
  division. `/` is integer division, `:` float division.
- 🟥 `=`: Take two
  elements a and b from the stack and put the result of `a==b` on the stack (a
  boolean value).
- 🟥 `m`: Take two
  elements a and b from the stack and put the result of `a>b` on the stack (a
  boolean value).
- 🟥 `w`: Take two
  elements a and b from the stack and put the result of `a<=b` on the stack (a
  boolean value).
- 🟦 `I`: Pop a value,
  increment it, and push it.
- 🟦 `D`: Pop a value,
  decrement it, and push it.
- 🟦 `!`: Push the
  negation of a popped value.
- 🟦 `~`: Invert the
  popped element and push it. Will also negate booleans and reverse strings.
- 🟦 `y`: Push the sign of
  a popped element (1 for positive numbers, -1 for negative numbers, 0
  otherwise).
- 🟥 `A`: Take two
  elements a and b from the stack and put the result of `a&b` (bitwise AND) on
  the stack.
- 🟥 `V`: Take two
  elements a and b from the stack and put the result of `a|b` (bitwise OR) on
  the stack.
- 🟥 `H`: Take two
  elements a and b from the stack and put the result of `a^b` (bitwise XOR) on
  the stack.
- 🟦 `a`: Push the result
  of bitwise NOT of the popped element on the stack.
- 🟥 `«`, `»`: Pop the top
  element (x) and the next element (y), and push `y<<x` (for `«`) or `y>>x` (for
  `»`).
- 🟥 `F`: Raise the second
  popped number by the power of the first.
- 🟦 `±`: Push the
  absolute value of a popped value.

### Literals
- 🟩 `0`, `1`, `2`, ...,
  `9`: Push that number on the active stack.
- 🟩 `"`: Starts a string
  literal. This works pretty much like in other languages. String literals are
  terminated with another `"`, but escaping (with a backslash) works too. That
  means that `"\"Hello\\World\n"` will result in `"Hello\World\n`, where the `\n`
  is a newline character (`\t` is also supported). The resulting string will be
  pushed on the active stack.
- 🟩 `'`: Starts a
  character literal. The next character will be pushed on the stack as a string.
  Escaping (for `\n`, `\t`, and `\\`) also works, but not for `\'`, because `''`
  will already accomplish the desired effect (push a single quote character).

### String methods
- 🟥 `J`: Join the top two
  elements as a string.
- 🟦 `~`: Reverse a string
  on top of the stack. Will also negate booleans and invert integers.
- 🟥 `F`: Pop an integer,
  then a string. Push `that_string[that_integer]`.
- 🟥 `£`: Implode a
  string: Replace the stack with all of its elements, joined by empty spaces,
  casted to strings, top to bottom.
- 🟩 `€`: Explode a
  string: Pop a string, and push all of its characters in reverse (such that the
  top stack element will be the first character).
- 🟨 `-`: Split a string
  on whitespace.
- 🟨 `:`: Split a string
  on another string (`['foo,bar,bat', ',']` → `['bat', 'bar', 'foo']`).
- 🟥 `/`: Push the number
  of regex matches of the first popped value in the second.
- 🟥 `%`: Push the third
  popped value, but with all instances of the regex in the second popped value
  replaced with the first popped value.
- 🟨 `a`: Push all
  matching strings of the first popped element in the second popped element.

### Casting
- 🟦 `i`: Pop a value,
  cast it to an integer (if possible, otherwise to 0), and put the result on the
  stack.
- 🟦 `f`: Like `i`, but
  with float.
- 🟦 `b`: Like `i`, but
  with bool.
- 🟦 `∑`: Like `i`, but
  with string.
- 🟦 `c`: Pop a value,
  convert it to the character of the unicode value and push it. If the value
  doesn't correspond to a unicode codepoint, push `U+FFFD` instead.
- 🟦 `o`: The opposite of
  `c`; Pop a character and convert it to the number of its unicode codepoint and
  push the result. When anything fails, push a 0 instead.

### I/O
- 🟥 `p`: Print the
  element on the stack.
- 🟥 `B`: Print the
  element in quick storage.
- 🟩 `r`: Read a string
  from the user and put it on the stack.
- 🟦 `n`: Print a newline.
- 🟩 `,`: Get a single
  character (without requiring a newline).

### Special
- 🟦 `\`: Escapes the next
  character: It will be ignored.
- 🟩 `P`, `e`, `R`: Push
  π, 𝑒, or a random float between 0 and 1.
- 🟨 `.`: Repeat the
  previous command.
- 🟦 `T`: Set the global
  timestamp to now. It is initialized to the time of script start.
- 🟩 `t`: Push the
  difference between now and the global timestamp.
- 🟩 `τ`: Push a local,
  datetime on the stack (year, month, day, hour, minute, second).
- 🟦 `C`: Pop a value and
  push a boolean: Whether the value is contained in the current stack.
- 🟩 `l`: Push the length
  of the current stack.
- 🟩 `L`: Load the value
  of the quick memory (initially an empty string) and push it on the stack.
- 🟥 `M`: Pop a value and
  memorize it in the quick memory.
- 🟩 `z`: Pop a value and
  push a decreasing range on the stack: A popped `5` will push `5`, `4`, `3`,
  `2`, `1`. Also works with negative numbers, in which case it will count up to
  `-1`.
- 🟩 `Z`: Pop a value and
  push an increasing range on the stack: A popped `5` will push `1`, `2`, `3`,
  `4`, `5`. Also works with negative numbers, in which case it will count down
  from `-1`.
- 🟦 `g`: Sort the top two
  elements of the stack (ascending)
- 🟦 `G`: Sort the top two
  elements of the stack (descending)
- 🟩 `×`: Multiply the
  stack by the top element (`[1,2,3]` becomes `[1,2,1,2,1,2]`).
