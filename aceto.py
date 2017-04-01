from hilbert_curve import hilbert
from fileinput import input as fileinput
from math import ceil, log2
from toolib.tools import eprint
import json

stack = []
code = []

for line in reversed(list(fileinput())):
    code.append(list(line.rstrip("\n")))

# eprint(code)

p = ceil(log2(max([len(code), max(len(line) for line in code)])))
eprint("Set p to", p)

def next_coord(x, y, p):
    """Return the next coordinate, or None if done"""
    distance = hilbert.distance_from_coordinates([y,x], p, N=2)
    y, x = hilbert.coordinates_from_distance(distance+1, p, N=2)
    return x, y

def execute_command(cmd, x, y):
    eprint("cmd:", cmd)
    if cmd == "<":
        return (x, y-1)
    elif cmd == ">":
        return (x, y+1)
    elif cmd == "v":
        return (x-1, y)
    elif cmd == "^":
        return (x+1, y)
    elif cmd.isnumeric():
        stack.append(int(cmd))
    elif cmd == "+":
        x = stack.pop()
        y = stack.pop()
        stack.append(x+y)
    elif cmd == "-":
        x = stack.pop()
        y = stack.pop()
        stack.append(x-y)
    elif cmd == "*":
        x = stack.pop()
        y = stack.pop()
        stack.append(x*y)
    elif cmd == "%":
        x = stack.pop()
        y = stack.pop()
        stack.append(x%y)
    elif cmd == "=":
        x = stack.pop()
        y = stack.pop()
        stack.append(x==y)
    elif cmd == "p":
        print(stack.pop())
    elif cmd == 'r':
        stack.append(input())
    elif cmd == 'i':
        stack.append(int(stack.pop()))
    elif cmd == 'd':
        x = stack.pop()
        stack.append(x)
        stack.append(x)
    elif cmd == '!':
        stack.append(not stack.pop())
    elif cmd == '|':
        cond = stack.pop()
        if cond:
            newpos = (x, 2**p-(y+1))
            eprint("Mirroring horizontally from", x, y, "to", newpos)
            return newpos
    elif cmd == '_':
        cond = stack.pop()
        if cond:
            newpos = (2**p-(x+1), y)
            eprint("Mirroring vertically from", x, y, "to", newpos)
            return newpos

x, y = 0, 0
while True:
    # eprint(x,y)
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
