"""
Aceto - A language based on 2D hilbert curve grids

Usage:
    aceto.py [-v ...] [options] [<filename> ...]

Options:
    -v --verbose    Be verbose. Can be specified several times.
    -F --flush      Always flush after printing.
    -e --err-all    Ignore catch marks (@) and always error out
"""
import sys
import os
import signal
import tty
import termios
import time
import shutil
from math import ceil, log2
from collections import defaultdict
from random import choice, random
from math import e, pi
from docopt import docopt
from hilbert_curve import hilbert


class colors(object):
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class CodeException(Exception):
    pass


class Aceto(object):
    def __init__(self, args):
        self.stacks = defaultdict(list)
        self.sticky = set()
        self.sid = 0
        self.buf = ''
        self.x, self.y = 0, 0
        self.verbosity = args['--verbose']
        self.flushness = args['--flush']
        self.allerr = args['--err-all']
        # annotate this!
        self.commands = {}
        d = type(self).__dict__
        for key in d:
            try:
                chars = d[key].__annotations__['return']
                for c in chars:
                    self.commands[c] = d[key]
            except KeyError:
                pass
            except AttributeError:
                pass

    def load_code(self, filename):
        self.code = []
        with open(filename) as f:
            for line in reversed(f.readlines()):
                self.code.append(list(line.rstrip("\n")))
        self.p = ceil(log2(max([len(self.code), max(len(line) for line in self.code)])))
        self.x, self.y = 0, 0
        self.timestamp = time.time()
        self.catch_mark = None
        self.dir = 1
        self.buf = ''
        self.mode = 'command'
        self.previous_cmd = ' '

    def run(self):
        while True:
            try:
                self.step()
            except Exception as e:
                if self.catch_mark is not None and not self.allerr:
                    self.log(1, "Caught", e)
                    self.x, self.y = self.catch_mark
                else:
                    raise e

    def push(self, thing):
        self.stacks[self.sid].append(thing)

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
            print(colors.FAIL, file=sys.stderr, end='')
            print(*pargs, file=sys.stderr, **kwargs)
            print(colors.ENDC, file=sys.stderr, end='', flush=True)

    def next_coord(self):
        """Return the next coordinate"""
        distance = hilbert.distance_from_coordinates([self.y,self.x], self.p, N=2)
        y, x = hilbert.coordinates_from_distance(distance+self.dir, self.p, N=2)
        return x, y

    def step(self):
        # self.log(3, self.x, self.y)
        try:
            cmd = self.code[self.x][self.y]
        except IndexError:
            cmd = ' '  # nop
        self.log(1, cmd, end='') if cmd != ' ' else None
        if self.mode == 'command':
            method = self.commands.get(cmd, Aceto._nop)
            method(self, cmd)
            self.previous_cmd = cmd
        elif self.mode in ('string', 'string-escape'):
            if cmd == '"' and self.mode == 'string':
                self.push(self.buf)
                self.buf = ''
                self.mode = 'command'
            elif cmd == '\\' and self.mode == 'string':
                self.mode = 'string-escape'
            elif self.mode == 'string-escape' and cmd in "nt":
                self.buf += {'n': '\n', 't': '\t'}[cmd]
                self.mode = 'string'
            else:
                self.buf += cmd
                self.mode = 'string'
            self.move()
        elif self.mode in ('char', 'char-escape'):
            if cmd == '\\' and self.mode == 'char':
                self.mode = 'char-escape'
            elif self.mode == 'char-escape' and cmd in 'nt':
                self.push({'n': '\n', 't': '\t'}[cmd])
                self.mode = 'command'
            else:
                self.push(cmd)
                self.mode = 'command'
            self.move()
        elif self.mode == 'escape':
            self.move()

    def move(self, coords=None):
        if coords is not None:
            x, y = coords
        else:
            if self.dir == -1 and (0,0) == (self.x, self.y):
                x, y = -1, -1
            else:
                x, y = self.next_coord()
        if x >= 2**self.p or y>= 2**self.p or x < 0 or y < 0:
            sys.exit()
        self.x, self.y = x, y

    def _nop(self, cmd) -> ' ':
        self.move()

    def _left(self, cmd) -> '<W':
        if cmd.isalpha():
            self.code[self.x][self.y] = 'N'
        self.move((self.x, self.y-1))

    def _right(self, cmd) -> '>E':
        if cmd.isalpha():
            self.code[self.x][self.y] = 'S'
        self.move((self.x, self.y+1))

    def _down(self, cmd) -> 'vS':
        if cmd.isalpha():
            self.code[self.x][self.y] = 'W'
        self.move((self.x-1, self.y))

    def _up(self, cmd) -> '^N':
        if cmd.isalpha():
            self.code[self.x][self.y] = 'E'
        self.move((self.x+1, self.y))

    def _numeric(self, cmd) -> '1234567890':
        self.push(int(cmd))
        self.move()

    def _plus(self, cmd) -> '+':
        x = self.pop()
        y = self.pop()
        try:
            self.push(y+x)
            self.move()
        except TypeError:
            raise CodeException(f"Can't add {x!r} to {y!r}")

    def _pow(self, cmd) -> 'F':
        x = self.pop()
        y = self.pop()
        try:
            self.push(y**x)
            self.move()
        except TypeError:
            raise CodeException(f"Can't raise {x!r} to the power of {y!r}")

    def _minus(self, cmd) -> '-':
        x = self.pop()
        y = self.pop()
        try:
            self.push(y-x)
            self.move()
        except TypeError:
            raise CodeException(f"Can't subtract {y!r} from {x!r}")

    def _times(self, cmd) -> '*':
        x = self.pop()
        y = self.pop()
        try:
            self.push(y*x)
            self.move()
        except TypeError:
            raise CodeException(f"Can't multiply {x!r} with {y!r}")

    def _mod(self, cmd) -> '%':
        x = self.pop()
        y = self.pop()
        try:
            self.push(y%x)
            self.move()
        except TypeError:
            raise CodeException(f"Can't get modulo of {x!r} and {y!r}")

    def _div(self, cmd) -> '/':
        x = self.pop()
        y = self.pop()
        try:
            self.push(y//x)
        except ZeroDivisionError:
            raise CodeException("Zero division")
        except TypeError:
            raise CodeException(f"Can't idivide {x!r} by {y!r}")
        self.move()

    def _floatdiv(self, cmd) -> ':':
        x = self.pop()
        y = self.pop()
        try:
            self.push(y/x)
        except ZeroDivisionError:
            raise CodeException("Zero division")
        except TypeError:
            raise CodeException(f"Can't fdivide {x!r} by {y!r}")
        self.move()

    def _equals(self, cmd) -> '=':
        x = self.pop()
        y = self.pop()
        self.log(3, f"Testing equality of {x!r} and {y!r}")
        self.push(y==x)
        self.move()

    def _print(self, cmd) -> 'p':
        print(self.pop(), end='', flush=self.flushness)
        self.move()

    def _sticky_mode_on(self, cmd) -> 'k':
        self.sticky.add(self.sid)
        self.move()

    def _sticky_mode_off(self, cmd) -> 'K':
        self.sticky.remove(self.sid)
        self.move()

    def _newline(self, cmd) -> 'n':
        print()
        self.move()

    def _read(self, cmd) -> 'r':
        self.push(input().rstrip('\n'))
        self.move()

    def _swap(self, cmd) -> 's':
        x = self.pop()
        y = self.pop()
        self.push(x)
        self.push(y)
        self.move()

    def _int(self, cmd) -> 'i':
        x = self.pop()
        try:
            self.push(int(x))
        except ValueError:
            raise CodeException(f"Can't cast {x!r} to int")
        self.move()

    def _increment(self, cmd) -> 'I':
        x = self.pop()
        try:
            self.push(x+1)
        except:
            self.push(1)
        self.move()

    def _decrement(self, cmd) -> 'D':
        x = self.pop()
        try:
            self.push(x-1)
        except:
            self.push(1)
        self.move()

    def _chr(self, cmd) -> 'c':
        x = self.pop()
        try:
            self.push(chr(x))
        except:
            self.push('\ufffd')
        self.move()

    def _ord(self, cmd) -> 'o':
        x = self.pop()
        try:
            self.push(ord(x))
        except:
            self.push(0)
        self.move()

    def _float(self, cmd) -> 'f':
        x = self.pop()
        try:
            self.push(float(x))
        except:
            self.push(0)
        self.move()

    def _duplicate(self, cmd) -> 'd':
        x = self.pop()
        self.push(x)
        self.push(x)
        self.move()

    def _next_stack(self, cmd) -> ')':
        self.sid += 1
        self.move()

    def _prev_stack(self, cmd) -> '(':
        self.sid -= 1
        self.move()

    def _move_next_stack(self, cmd) -> '}':
        x = self.pop()
        self.sid += 1
        self.push(x)
        self.sid -= 1
        self.move()

    def _move_prev_stack(self, cmd) -> '{':
        x = self.pop()
        self.sid -= 1
        self.push(x)
        self.sid += 1
        self.move()

    def _negation(self, cmd) -> '!':
        self.push(not self.pop())
        self.move()

    def _die(self, cmd) -> 'X':
        sys.exit()

    def _mirror_h(self, cmd) -> '|':
        cond = self.pop()
        if cond:
            new_pos = (self.x, 2**self.p-(self.y+1))
            self.log(2, "Mirroring horizontally from", self.x, self.y, "to", new_pos)
            self.move(new_pos)
        else:
            self.move()

    def _mirror_v(self, cmd) -> '_':
        cond = self.pop()
        if cond:
            new_pos = (2**self.p-(self.x+1), self.y)
            self.log(2, "Mirroring vertically from", self.x, self.y, "to", new_pos)
            self.move(new_pos)
        else:
            self.move()

    def _mirror_vh(self, cmd) -> '#':
        cond = self.pop()
        if cond:
            new_pos = (2**self.p-(self.x+1), 2**self.p-(self.y+1))
            self.log(2, "Mirroring (both) from", self.x, self.y, "to", new_pos)
            self.move(new_pos)
        else:
            self.move()

    def _reverse(self, cmd) -> 'u': #reverse direction
        self.dir *= -1
        self.move()

    def _string_literal(self, cmd) -> '"':
        self.mode = 'string'
        self.move()

    def _char_literal(self, cmd) -> '\'':
        self.mode = 'char'
        self.move()

    def _escape(self, cmd) -> '\\':
        self.mode = 'escape'
        self.move()

    def _random_direction(self, cmd) -> '?':
        cmd_ = random.choice("v^<>")
        method = self.commands.get(cmd_, Aceto._nop)
        method(self, cmd)

    def _random_number(self, cmd) -> 'R':
        self.push(random())
        self.move()

    def _pi(self, cmd) -> 'P':
        self.push(pi)
        self.move()

    def _euler(self, cmd) -> 'e':
        self.push(pi)
        self.move()

    def _invert(self, cmd) -> '~':
        self.push(-self.pop())
        self.move()

    def _restart(self, cmd) -> 'O':
        if self.dir==1:
            self.x, self.y = 0, 0
        else:
            length = 2**self.p
            self.x, self.y = length-1, length-1

    def _getch(self, cmd) -> ',':
        ch = getch()
        if ch == '\r':
            ch = ''
        self.push(ch)
        self.move()

    def _repeat(self, cmd) -> '.':
        method = self.commands.get(self.previous_cmd, Aceto._nop)
        method(self, self.previous_cmd)

    def _catch_mark(self, cmd) -> '@':
        self.catch_mark = self.x, self.y
        self.move()

    def _raise(self, cmd) -> '&':
        raise CodeException("Raised an &rror.")

    def _assert(self, cmd) -> '$':
        if self.pop():
            raise CodeException("A$$ertion failed")
        else:
            self.move()

    def _get_time(self, cmd) -> 't':
        self.push(time.time()-self.timestamp)
        self.move()

    def _set_time(self, cmd) -> 'T':
        self.timestamp = time.time()
        self.move()

    def _drop(self, cmd) -> 'x':
        self.pop()
        self.move()



def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
        # restore behavior for special things
        if ch == '\x03':  # ^C
            raise KeyboardInterrupt
        elif ch == '\x1a':  # ^Z
            os.kill(os.getpid(), signal.SIGTSTP)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

if __name__ == '__main__':
    args = docopt(__doc__, version="1.0")
    A=Aceto(args)
    for filename in args['<filename>']:
        A.load_code(filename)
        A.run()
    if not args['<filename>']:
        cols, _ = shutil.get_terminal_size((80, 20))
        info = [f'{c} {f.__name__[1:]}' for c, f in A.commands.items()]
        maxlen = max(len(x) for x in info) + 1
        columns = cols // maxlen
        iinfo = iter(info)
        try:
            while True:
                for _ in range(columns):
                    print(next(iinfo).ljust(maxlen), end='')
                print()
        except StopIteration:
            print()
