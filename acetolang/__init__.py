#!/usr/bin/env python3
import sys
import os
import signal
import tty
import termios
import time
import click
import shutil
import re
from math import ceil, pi, e as euler
from numbers import Number
from collections import defaultdict
from random import choice, random, shuffle
from enum import Enum
from hilbertcurve.hilbertcurve import HilbertCurve


class Colors(Enum):
    """ Terminal colors """

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class CodeException(Exception):
    """ Generic exception for Aceto errors """

    pass


class Aceto(object):
    """ Interpreter object """

    def __init__(self, verbosity, flushness, allerr, encoding):
        self.stacks = defaultdict(list)
        self.sticky = set()
        self.sid = 0
        self.quick = ""
        self.verbosity = verbosity
        self.flushness = flushness
        self.allerr = allerr
        self.encoding = encoding
        # annotate this!
        self.commands = self.get_annotations()

    def get_annotations(self):
        cmds = {}
        d = type(self).__dict__
        for key in d:
            try:
                chars = d[key].__annotations__["return"]
                for c in chars:
                    cmds[c] = d[key]
            except KeyError:
                pass
            except AttributeError:
                pass
        return cmds

    @staticmethod
    def load_code_linear(fileobj):
        code_helper = defaultdict(lambda: defaultdict(str))
        chars = "".join(char for line in fileobj for char in line.strip())
        p = (ceil(len(chars) ** 0.5) - 1).bit_length()
        hilbert = HilbertCurve(p, 2)
        for step, char in enumerate(chars):
            y, x = hilbert.coordinates_from_distance(step)
            code_helper[x][y] = char
        return code_helper, p

    @staticmethod
    def load_code_hilbert(fileobj):
        code = []
        for line in reversed(fileobj.readlines()):
            code.append(list(line.rstrip("\n")))
        return code, (max(len(code), max(map(len, code))) - 1).bit_length()

    def load_code(self, filename, linear_mode=False):
        with open(filename, encoding=self.encoding) as f:
            if linear_mode:
                self.code, self.p = self.load_code_linear(f)
            else:
                self.code, self.p = self.load_code_hilbert(f)
        self.s = 2 ** self.p
        self.x, self.y = 0, 0
        self.timestamp = time.time()
        self.catch_mark = None
        self.dir = 1
        self.buf = ""
        self.mode = "command"
        self.previous_cmd = " "
        self.hilbert = HilbertCurve(self.p, 2)  # side length p, 2 dimensions

    def run(self):
        while True:
            try:
                self.step()
            except Exception as e:
                if self.catch_mark is not None and not self.allerr:
                    self.log(2, "Caught", e)
                    self.x, self.y = self.catch_mark
                else:
                    raise e

    def push(self, thing):
        self.stacks[self.sid].append(thing)

    def pushiter(self, iterable):
        self.stacks[self.sid].extend(iterable)

    def pop(self):
        try:
            x = self.stacks[self.sid][-1]
            if self.sid not in self.sticky:
                self.stacks[self.sid].pop()
            return x
        except IndexError:
            return 0

    def log(self, level, *pargs, **kwargs):
        if level <= self.verbosity:
            print(Colors.FAIL.value, file=sys.stderr, end="")
            print(*pargs, file=sys.stderr, **kwargs)
            print(Colors.ENDC.value, file=sys.stderr, end="", flush=True)

    def next_coord(self):
        """Return the next coordinate"""
        distance = self.hilbert.distance_from_coordinates([self.y, self.x])
        y, x = self.hilbert.coordinates_from_distance(distance + self.dir)
        return x, y

    def step_command_mode(self, cmd):
        method = self.commands.get(cmd, Aceto._nop)
        method(self, cmd)
        self.previous_cmd = cmd

    def step_string_mode(self, cmd):
        if cmd == '"' and self.mode == "string":
            self.push(self.buf)
            self.buf = ""
            self.mode = "command"
        elif cmd == "\\" and self.mode == "string":
            self.mode = "string-escape"
        elif self.mode == "string-escape" and cmd in "nt":
            self.buf += {"n": "\n", "t": "\t"}[cmd]
            self.mode = "string"
        else:
            self.buf += cmd
            self.mode = "string"
        self.move()

    def step_char_mode(self, cmd):
        if cmd == "\\" and self.mode == "char":
            self.mode = "char-escape"
        elif self.mode == "char-escape" and cmd in "nt":
            self.push({"n": "\n", "t": "\t"}[cmd])
            self.mode = "command"
        else:
            self.push(cmd)
            self.mode = "command"
        self.move()

    def step_escape_mode(self, cmd):
        self.move()
        self.mode = "command"

    def get_command(self):
        try:
            return self.code[self.x][self.y]
        except IndexError:
            return " "  # nop

    def step(self):
        cmd = self.get_command()
        if cmd != " ":
            self.log(1, cmd, end="")
            self.log(2, "\nActive stack:", self.stacks[self.sid])
        if self.mode == "command":
            self.step_command_mode(cmd)
        elif self.mode in ("string", "string-escape"):
            self.step_string_mode(cmd)
        elif self.mode in ("char", "char-escape"):
            self.step_char_mode(cmd)
        elif self.mode == "escape":
            self.step_escape_mode(cmd)
        else:
            raise CodeException("Invalid mode:", self.mode)

    def move(self, coords=None):
        if coords is not None:
            x, y = coords
        else:
            if self.dir == -1 and (0, 0) == (self.x, self.y):
                x, y = -1, -1
            else:
                try:
                    x, y = self.next_coord()
                except ValueError:
                    sys.exit()
        if x >= 2 ** self.p or y >= 2 ** self.p or x < 0 or y < 0:
            sys.exit()
        self.x, self.y = x, y

    def _nop(self, cmd) -> " ":
        self.move()

    def _left(self, cmd) -> "<W":
        if cmd == "W":
            self.code[self.x][self.y] = "N"
        self.move((self.x, (self.y - 1) % self.s))

    def _right(self, cmd) -> ">E":
        if cmd == "E":
            self.code[self.x][self.y] = "S"
        self.move((self.x, ((self.y + 1) % self.s)))

    def _down(self, cmd) -> "vS":
        if cmd == "S":
            self.code[self.x][self.y] = "W"
        self.log(
            2,
            f"{self.s} From {self.x},{self.y} to " f"{(self.x - 1) % self.s}, {self.y}",
        )
        self.move(((self.x - 1) % self.s, self.y))

    def _up(self, cmd) -> "^N":
        if cmd == "N":
            self.code[self.x][self.y] = "E"
        self.move(((self.x + 1) % self.s, self.y))

    def _numeric(self, cmd) -> "1234567890":
        self.push(int(cmd))
        self.move()

    def _plus(self, cmd) -> "+":
        x = self.pop()
        y = self.pop()
        try:
            self.push(y + x)
            self.move()
        except TypeError:
            raise CodeException(f"Can't add {x!r} to {y!r}")

    def _pow__find_char(self, cmd) -> "F":
        x = self.pop()
        y = self.pop()
        if isinstance(y, Number):
            try:
                self.push(y ** x)
            except TypeError:
                raise CodeException(f"Can't raise {y!r} to the power of {x!r}")
        else:
            try:
                self.push(y[x])
            except IndexError:
                raise CodeException("Index out of range")
        self.move()

    def _minus__split1(self, cmd) -> "-":
        x = self.pop()
        if isinstance(x, Number):
            y = self.pop()
            try:
                self.push(y - x)
            except TypeError:
                raise CodeException(f"Can't subtract {x!r} from {y!r}")
        else:
            self.pushiter(reversed(x.split()))
        self.move()

    def _times(self, cmd) -> "*":
        x = self.pop()
        y = self.pop()
        try:
            self.push(y * x)
            self.move()
        except TypeError:
            raise CodeException(f"Can't multiply {x!r} with {y!r}")

    def _mod__re_replace(self, cmd) -> "%":
        x = self.pop()
        y = self.pop()
        if isinstance(x, Number):
            try:
                self.push(y % x)
            except TypeError:
                raise CodeException(f"Can't get modulo of {y!r} and {x!r}")
        else:
            z = self.pop()
            self.push(re.sub(y, z, x))
        self.move()

    def _div__re_matches(self, cmd) -> "/":
        x = self.pop()
        y = self.pop()
        if isinstance(x, Number):
            try:
                self.push(y // x)
            except ZeroDivisionError:
                raise CodeException("Zero division")
            except TypeError:
                raise CodeException(f"Can't idivide {y!r} by {x!r}")
        else:
            self.push(len(re.findall(y, x)))
        self.move()

    def _floatdiv__split2(self, cmd) -> ":":
        x = self.pop()
        if isinstance(x, Number):
            y = self.pop()
            try:
                self.push(y / x)
            except ZeroDivisionError:
                raise CodeException("Zero division")
            except TypeError:
                raise CodeException(f"Can't fdivide {y!r} by {x!r}")
        else:
            y = self.pop()
            self.pushiter(reversed(y.split(x)))
        self.move()

    def _equals(self, cmd) -> "=":
        x = self.pop()
        y = self.pop()
        self.log(2, f"Testing equality of {x!r} and {y!r}")
        self.push(y == x)
        self.move()

    def _print(self, cmd) -> "p":
        print(self.pop(), end="", flush=self.flushness)
        self.move()

    def _print_quick(self, cmd) -> "B":
        print(self.quick, end="", flush=self.flushness)
        self.move()

    def _sticky_mode_on(self, cmd) -> "k":
        self.sticky.add(self.sid)
        self.move()

    def _sticky_mode_off(self, cmd) -> "K":
        self.sticky.remove(self.sid)
        self.move()

    def _newline(self, cmd) -> "n":
        print()
        self.move()

    def _read(self, cmd) -> "r":
        self.push(input().rstrip("\n"))
        self.move()

    def _swap(self, cmd) -> "s":
        x = self.pop()
        y = self.pop()
        self.push(x)
        self.push(y)
        self.move()

    def _cast_int(self, cmd) -> "i":
        x = self.pop()
        try:
            self.push(int(x))
        except ValueError:
            raise CodeException(f"Can't cast {x!r} to int")
        self.move()

    def _cast_bool(self, cmd) -> "b":
        x = self.pop()
        try:
            self.push(bool(x))
        except ValueError:
            raise CodeException(f"Can't cast {x!r} to bool")
        self.move()

    def _cast_string(self, cmd) -> "∑":
        x = self.pop()
        try:
            self.push(str(x))
        except ValueError:
            raise CodeException(f"Can't cast {x!r} to string")
        self.move()

    def _increment(self, cmd) -> "I":
        x = self.pop()
        try:
            self.push(x + 1)
        except Exception:
            self.push(1)
        self.move()

    def _decrement(self, cmd) -> "D":
        x = self.pop()
        try:
            self.push(x - 1)
        except Exception:
            self.push(1)
        self.move()

    def _chr(self, cmd) -> "c":
        x = self.pop()
        try:
            self.push(chr(x))
        except Exception:
            self.push("\ufffd")
        self.move()

    def _ord(self, cmd) -> "o":
        x = self.pop()
        try:
            self.push(ord(x))
        except Exception:
            self.push(0)
        self.move()

    def _cast_float(self, cmd) -> "f":
        x = self.pop()
        try:
            self.push(float(x))
        except Exception:
            self.push(0)
        self.move()

    def _duplicate(self, cmd) -> "d":
        x = self.pop()
        self.push(x)
        self.push(x)
        self.move()

    def _head(self, cmd) -> "h":
        x = self.pop()
        self.stacks[self.sid] = []
        self.push(x)
        self.move()

    def _next_stack(self, cmd) -> ")":
        self.sid += 1
        self.move()

    def _prev_stack(self, cmd) -> "(":
        self.sid -= 1
        self.move()

    def _move_next_stack(self, cmd) -> "}":
        x = self.pop()
        self.sid += 1
        self.push(x)
        self.sid -= 1
        self.move()

    def _move_prev_stack(self, cmd) -> "{":
        x = self.pop()
        self.sid -= 1
        self.push(x)
        self.sid += 1
        self.move()

    def _move_go_next_stack(self, cmd) -> "]":
        x = self.pop()
        self.sid += 1
        self.push(x)
        self.move()

    def _move_go_prev_stack(self, cmd) -> "[":
        x = self.pop()
        self.sid -= 1
        self.push(x)
        self.move()

    def _negation(self, cmd) -> "!":
        self.push(not self.pop())
        self.move()

    def _die(self, cmd) -> "X":
        sys.exit()

    def _mirror_h(self, cmd) -> "|":
        cond = self.pop()
        if cond:
            new_pos = (self.x, 2 ** self.p - (self.y + 1))
            self.log(2, "Mirroring horizontally from", self.x, self.y, "to", new_pos)
            self.move(new_pos)
        else:
            self.move()

    def _mirror_v(self, cmd) -> "_":
        cond = self.pop()
        if cond:
            new_pos = (2 ** self.p - (self.x + 1), self.y)
            self.log(2, "Mirroring vertically from", self.x, self.y, "to", new_pos)
            self.move(new_pos)
        else:
            self.move()

    def _mirror_vh(self, cmd) -> "#":
        cond = self.pop()
        if cond:
            new_pos = (2 ** self.p - (self.x + 1), 2 ** self.p - (self.y + 1))
            self.log(2, "Mirroring (both) from", self.x, self.y, "to", new_pos)
            self.move(new_pos)
        else:
            self.move()

    def _reverse(self, cmd) -> "u":  # reverse direction
        self.dir *= -1
        self.move()

    def _reverse_stack(self, cmd) -> "U":  # reverse stack
        self.stacks[self.sid].reverse()
        self.move()

    def _string_literal(self, cmd) -> '"':
        self.mode = "string"
        self.move()

    def _char_literal(self, cmd) -> "'":
        self.mode = "char"
        self.move()

    def _escape(self, cmd) -> "\\":
        self.mode = "escape"
        self.move()

    def _cond_escape(self, cmd) -> "`":
        if not self.pop():
            self.mode = "escape"
        self.move()

    def _random_direction(self, cmd) -> "?":
        cmd_ = choice("v^<>")
        method = self.commands.get(cmd_, Aceto._nop)
        method(self, cmd)

    def _random_number(self, cmd) -> "R":
        self.push(random())
        self.move()

    def _pi(self, cmd) -> "P":
        self.push(pi)
        self.move()

    def _euler(self, cmd) -> "e":
        self.push(euler)
        self.move()

    def _invert(self, cmd) -> "~":
        x = self.pop()
        if isinstance(x, bool):
            self.push(not x)
        elif isinstance(x, Number):
            self.push(-x)
        elif isinstance(x, str):
            self.push(x[::-1])
        else:
            raise CodeException(f"Don't know how to invert {x!r}")
        self.move()

    def _bitwise_negate(self, cmd) -> "a":
        x = self.pop()
        if isinstance(x, Number):
            try:
                self.push(~x)
            except Exception:
                raise CodeException(f"Don't know how to invert {x!r}")
        else:
            y = self.pop()
            self.pushiter(reversed(re.findall(y, x)))
        self.move()

    def _restart(self, cmd) -> "O":
        if self.dir == 1:
            self.x, self.y = 0, 0
        else:
            length = 2 ** self.p
            self.x, self.y = 0, length - 1

    def _finalize(self, cmd) -> ";":
        if self.dir == -1:
            self.x, self.y = 0, 0
        else:
            length = 2 ** self.p
            self.x, self.y = 0, length - 1

    def _getch(self, cmd) -> ",":
        ch = getch()
        if ch == "\r":
            ch = ""
        self.push(ch)
        self.move()

    def _repeat(self, cmd) -> ".":
        method = self.commands.get(self.previous_cmd, Aceto._nop)
        method(self, self.previous_cmd)

    def _empty_stack(self, cmd) -> "ø":
        self.stacks[self.sid] = []
        self.move()

    def _jump(self, cmd) -> "j":
        steps = self.pop()
        distance = self.hilbert.distance_from_coordinates([self.y, self.x])
        y, x = self.hilbert.coordinates_from_distance(distance + self.dir * steps)
        self.x, self.y = x, y

    def _goto(self, cmd) -> "§":
        distance = self.pop()
        # TODO: should take the direction (self.dir) into account.
        y, x = self.hilbert.coordinates_from_distance(distance)
        self.x, self.y = x, y

    def _join(self, cmd) -> "J":
        x, y = self.pop(), self.pop()
        self.push(str(x) + str(y))
        self.move()

    def _catch_mark(self, cmd) -> "@":
        self.catch_mark = self.x, self.y
        self.move()

    def _raise(self, cmd) -> "&":
        raise CodeException("Raised an &rror.")

    def _assert(self, cmd) -> "$":
        if self.pop():
            raise CodeException("A$$ertion failed")
        else:
            self.move()

    def _get_stopwatch(self, cmd) -> "t":
        self.push(time.time() - self.timestamp)
        self.move()

    def _set_stopwatch(self, cmd) -> "T":
        self.timestamp = time.time()
        self.move()

    def _get_datetime(self, cmd) -> "™τ":
        self.pushiter([*time.localtime()][:6][::-1])
        self.move()

    def _drop(self, cmd) -> "x":
        self.pop()
        self.move()

    def _contains(self, cmd) -> "C":
        x = self.pop()
        self.push(x in self.stacks[self.sid])
        self.move()

    def _length(self, cmd) -> "l":
        self.push(len(self.stacks[self.sid]))
        self.move()

    def _queue(self, cmd) -> "q":
        self.stacks[self.sid].insert(0, self.pop())
        self.move()

    def _unqueue(self, cmd) -> "Q":
        try:
            self.push(self.stacks[self.sid].pop(0))
        except IndexError:
            self.push(0)
        self.move()

    def _memorize_quick(self, cmd) -> "M":
        self.quick = self.pop()
        self.move()

    def _load_quick(self, cmd) -> "L":
        self.push(self.quick)
        self.move()

    def _more(self, cmd) -> "m":
        x = self.pop()
        y = self.pop()
        self.log(2, f"Testing if {y!r} > {x!r}")
        self.push(y > x)
        self.move()

    def _less_or_equal(self, cmd) -> "w":
        x = self.pop()
        y = self.pop()
        self.log(2, f"Testing if {y!r} <= {x!r}")
        self.push(y <= x)
        self.move()

    def _bitwise_and(self, cmd) -> "A":
        x = self.pop()
        y = self.pop()
        self.push(y & x)
        self.move()

    def _bitwise_or(self, cmd) -> "V":
        x = self.pop()
        y = self.pop()
        self.push(y | x)
        self.move()

    def _bitwise_xor(self, cmd) -> "H":
        x = self.pop()
        y = self.pop()
        self.push(y ^ x)
        self.move()

    def _range_down(self, cmd) -> "z":
        val = self.pop()
        if not isinstance(val, int) or val == 0:
            raise CodeException("Can only construct range with non-0 integer")
        step = -1 if val > 0 else 1
        self.pushiter(range(val, 0, step))
        self.move()

    def _range_up(self, cmd) -> "Z":
        val = self.pop()
        if not isinstance(val, int) or val == 0:
            raise CodeException("Can only construct range with non-0 integer")
        step = 1 if val > 0 else -1
        self.pushiter(range(step, val + step, step))
        self.move()

    def _order_up(self, cmd) -> "G":
        x = [self.pop(), self.pop()]
        x.sort()
        self.push(x.pop())
        self.push(x.pop())
        self.move()

    def _order_down(self, cmd) -> "g":
        x = [self.pop(), self.pop()]
        x.sort(reverse=True)
        self.push(x.pop())
        self.push(x.pop())
        self.move()

    def _shuffle(self, cmd) -> "Y":
        shuffle(self.stacks[self.sid])
        self.move()

    def _sign(self, cmd) -> "y":
        x = self.pop()
        self.push(1 if x > 0 else -1 if x < 0 else 0)
        self.move()

    def _bitwise_left(self, cmd) -> "«":
        x = self.pop()
        y = self.pop()
        self.push(y << x)
        self.move()

    def _bitwise_right(self, cmd) -> "»":
        x = self.pop()
        y = self.pop()
        self.push(y >> x)
        self.move()

    def _multiply_stack(self, cmd) -> "×":
        x = self.pop()
        self.stacks[self.sid] *= x
        self.move()

    def _abs(self, cmd) -> "±":
        x = self.pop()
        self.push(abs(x))
        self.move()

    def _explode_string(self, cmd) -> "€":
        x = self.pop()
        self.stacks[self.sid].extend(reversed(x))
        self.move()

    def _implode_string(self, cmd) -> "£¥":
        s = "".join(map(str, reversed(self.stacks[self.sid])))
        self.stacks[self.sid] = [s]
        self.move()


def getch():
    fd = sys.stdin.fileno()
    if not os.isatty(fd):
        return sys.stdin.read(1)
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
        # restore behavior for special things
        if ch == "\x03":  # ^C
            raise KeyboardInterrupt
        elif ch == "\x1a":  # ^Z
            os.kill(os.getpid(), signal.SIGTSTP)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


@click.command()
@click.argument("files", type=click.Path(), nargs=-1)
@click.option("--verbose", "-v", count=True)
@click.option("--flush", "-F", is_flag=True)
@click.option("--err-all", "-e", is_flag=True)
@click.option("--windows-1252", "-w", is_flag=True)
@click.option("--latin-7", "-g", is_flag=True)
@click.option("--linear", "-l", is_flag=True)
def cli(files, verbose, flush, err_all, windows_1252, latin_7, linear):
    A = Aceto(
        verbosity=verbose,
        flushness=flush,
        allerr=err_all,
        encoding=("cp1252" if windows_1252 else "greek" if latin_7 else "utf-8"),
    )
    for filename in files:
        A.load_code(filename, linear)
        A.run()
    if not files:
        cols, _ = shutil.get_terminal_size((80, 20))
        info = [f"{c} {f.__name__[1:]}" for c, f in A.commands.items()]
        info.sort()
        maxlen = max(len(x) for x in info) + 1
        columns = cols // maxlen
        iinfo = iter(info)
        end_character = "" if sys.stdout.isatty() else "\n"
        try:
            while True:
                for _ in range(columns):
                    item = next(iinfo)
                    # skip all numbers except for 0
                    while any(item.startswith(x) for x in "123456789"):
                        item = next(iinfo)
                    print(item.ljust(maxlen), end=end_character)
                if not end_character:
                    print()
        except StopIteration:
            print()
