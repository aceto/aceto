"""
Aceto - A language based on 2D hilbert curve grids

Usage:
    aceto.py [options] <filename>

Options:
    -v --verbose    Be verbose. Can be specified several times.
    -F --flush      Always flush after printing.
"""
import sys
from math import ceil, log2
from collections import defaultdict
from docopt import docopt
from hilbert_curve import hilbert


class Aceto(object):
    def __init__(self, args):
        self.stacks = defaultdict(list)
        self.sid = 0
        self.dir = 1
        self.mode = 'command'
        self.buf = ''
        self.code = []
        self.x, self.y = 0, 0
        with open(args['<filename>']) as f:
            for line in reversed(f.readlines()):
                self.code.append(list(line.rstrip("\n")))
        self.verbosity = args['--verbose']
        self.flushness = args['--flush']
        self.p = ceil(log2(max([len(self.code), max(len(line) for line in self.code)])))
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

    def run(self):
        while True:
            self.step()

    def push(self, thing):
        self.stacks[self.sid].append(thing)

    def pop(self):
        try:
            return self.stacks[self.sid].pop()
        except IndexError:
            return 0

    def log(self, level, *pargs, **kwargs):
        if level <= self.verbosity:
            print(*pargs, file=sys.stderr, **kwargs)

    def next_coord(self):
        """Return the next coordinate"""
        distance = hilbert.distance_from_coordinates([self.y,self.x], self.p, N=2)
        y, x = hilbert.coordinates_from_distance(distance+self.dir, self.p, N=2)
        return x, y

    def step(self):
        try:
            cmd = self.code[self.x][self.y]
        except IndexError:
            cmd = ' '  # nop
        if self.mode == 'command':
            self.log(1, cmd, end='') if cmd != ' ' else None
            method = self.commands.get(cmd, Aceto._nop)
            method(self, cmd)
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
        elif self.mode == 'escape':
            self.move()

    def move(self, coords=None):
        if coords is not None:
            x, y = coords
        else:
            x, y = self.next_coord()
        if x >= 2**self.p or y>= 2**self.p or x < 0 or y < 0:
            sys.exit()
        self.x, self.y = x, y

    def _nop(self, cmd) -> ' ':
        self.move()

    def _left(self, cmd) -> '<':
        self.move((self.x, self.y-1))

    def _right(self, cmd) -> '>':
        self.move((self.x, self.y+1))

    def _down(self, cmd) -> 'v':
        self.move((self.x-1, self.y))

    def _up(self, cmd) -> '^':
        self.move((self.x+1, self.y))

    def _numeric(self, cmd) -> '1234567890':
        self.push(int(cmd))
        self.move()

    def _plus(self, cmd) -> '+':
        x = self.pop()
        y = self.pop()
        self.push(y+x)
        self.move()

    def _minus(self, cmd) -> '-':
        x = self.pop()
        y = self.pop()
        self.push(y-x)
        self.move()

    def _times(self, cmd) -> '*':
        x = self.pop()
        y = self.pop()
        self.push(y*x)
        self.move()

    def _mod(self, cmd) -> '%':
        x = self.pop()
        y = self.pop()
        self.push(y%x)
        self.move()

    def _div(self, cmd) -> '/':
        x = self.pop()
        y = self.pop()
        self.push(y//x)
        self.move()

    def _floatdiv(self, cmd) -> ':':
        x = self.pop()
        y = self.pop()
        self.push(y/x)
        self.move()

    def _equals(self, cmd) -> '=':
        x = self.pop()
        y = self.pop()
        self.push(y==x)
        self.move()

    def _print(self, cmd) -> 'p':
        print(self.pop(), end='', flush=self.flushness)
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
        except:
            self.push(0)
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

    def _escape(self, cmd) -> '\\':
        self.mode = 'escape'
        self.move()

if __name__ == '__main__':
    args = docopt(__doc__, version="1.0")
    A=Aceto(args)
    A.run()
