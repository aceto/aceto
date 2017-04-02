"""
Aceto - A language based on 2D hilbert curve grids

Usage:
    aceto.py [options] <filename>

Options:
    -v --verbose    Be verbose. Can be specified several times.
"""
import sys
from math import ceil, log2
from collections import defaultdict
from docopt import docopt
from hilbert_curve import hilbert


class Stacks(object):
    def __init__(self):
        self.stacks = defaultdict(list)
        self.sid = 0

    def push(self, thing):
        self.stacks[self.sid].append(thing)

    def pop(self):
        try:
            return self.stacks[self.sid].pop()
        except IndexError:
            return 0

stack = Stacks()
code = []

args = docopt(__doc__)
def eprint(level, *pargs, **kwargs):
    if level <= args['--verbose']:
        print(*pargs, file=sys.stderr, **kwargs)

with open(args['<filename>']) as f:
    for line in reversed(f.readlines()):
        code.append(list(line.rstrip("\n")))

p = ceil(log2(max([len(code), max(len(line) for line in code)])))

def next_coord(x, y, p):
    """Return the next coordinate, or None if done"""
    distance = hilbert.distance_from_coordinates([y,x], p, N=2)
    y, x = hilbert.coordinates_from_distance(distance+1, p, N=2)
    return x, y

def execute_command(cmd, x, y):
    if cmd != " ":
            eprint(1, "cmd:", cmd)
    if cmd == "<":
        return (x, y-1)
    elif cmd == ">":
        return (x, y+1)
    elif cmd == "v":
        return (x-1, y)
    elif cmd == "^":
        return (x+1, y)
    elif cmd.isnumeric():
        stack.push(int(cmd))
    elif cmd == "+":
        x = stack.pop()
        y = stack.pop()
        stack.push(x+y)
    elif cmd == "-":
        x = stack.pop()
        y = stack.pop()
        stack.push(y-x)
    elif cmd == "*":
        x = stack.pop()
        y = stack.pop()
        stack.push(x*y)
    elif cmd == "%":
        x = stack.pop()
        y = stack.pop()
        stack.push(y%x)
    elif cmd == "=":
        x = stack.pop()
        y = stack.pop()
        stack.push(x==y)
    elif cmd == "p":
        print(stack.pop(), end='')
    elif cmd == 'r':
        stack.push(input())
    elif cmd == 's':
        x = stack.pop()
        y = stack.pop()
        stack.push(x)
        stack.push(y)
    elif cmd == 'i':
        x = stack.pop()
        try:
            stack.push(int(x))
        except:
            stack.push(0)
    elif cmd == 'I':
        x = stack.pop()
        try:
            stack.push(int(x)+1)
        except:
            stack.push(0)
    elif cmd == 'D':
        x = stack.pop()
        try:
            stack.push(int(x)-1)
        except:
            stack.push(0)
    elif cmd == 'c':
        x = stack.pop()
        try:
            stack.push(chr(x))
        except:
            stack.push('\ufffd')
    elif cmd == 'o':
        x = stack.pop()
        try:
            stack.push(ord(x))
        except:
            stack.push(0)
    elif cmd == 'f':
        x = stack.pop()
        try:
            stack.push(float(x))
        except:
            stack.push(0)
    elif cmd == 'd':
        x = stack.pop()
        stack.push(x)
        stack.push(x)
    elif cmd == ')':
        stack.sid += 1
    elif cmd == '(':
        stack.sid -= 1
    elif cmd == '{':
        x = stack.pop()
        stack.sid -= 1
        stack.push(x)
        stack.sid += 1
    elif cmd == '}':
        x = stack.pop()
        stack.sid += 1
        stack.push(x)
        stack.sid -= 1
    elif cmd == '!':
        stack.push(not stack.pop())
    elif cmd == 'X':
        sys.exit()
    elif cmd == '|':
        cond = stack.pop()
        if cond:
            newpos = (x, 2**p-(y+1))
            eprint(2, "Mirroring horizontally from", x, y, "to", newpos)
            return newpos
    elif cmd == '_':
        cond = stack.pop()
        if cond:
            newpos = (2**p-(x+1), y)
            eprint(2, "Mirroring vertically from", x, y, "to", newpos)
            return newpos

x, y = 0, 0
while True:
    try:
        cmd = code[x][y]
    except IndexError:
        cmd = ' '  # nop
    rpos = execute_command(cmd, x, y)
    if rpos is None:
        x, y = next_coord(x, y, p)
        if x >= 2**p or y>= 2**p or x < 0 or y < 0:
            break  # done
    else:
        x, y = rpos
