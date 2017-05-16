#!/usr/bin/env python3
"""
Balsamico — an Aceto editor
"""
from urwid import MainLoop, SolidFill, ExitMainLoop, Edit, Overlay, Columns, Pile, Text, Filler, LineBox, BoxAdapter
from hilbert_curve import hilbert
from math import ceil, log2
from collections import defaultdict
import sys

def str_to_hilbert(string, cursor=None):
    p = ceil(log2(len(string)**.5))
    d = defaultdict(lambda:defaultdict(str))
    for i, c in enumerate(string):
        y, x = hilbert.coordinates_from_distance(i, p, N=2)
        if cursor is not None and i == cursor:
            d[x][y] = "∎"
        else:
            d[x][y] = c
    return "\n".join(
            "".join(d[y][x] for x in range(2**p)) for y in reversed(range(2**p))
            )

def hilbert_to_str(filename):
    code = []
    try:
        with open(filename) as f:
            for line in reversed(f.readlines()):
                code.append(list(line.rstrip("\n")))
        p = ceil(log2(max([len(code), max(len(line) for line in code)])))
        sling = []
        for i in range((2**p)**2):
            y, x = hilbert.coordinates_from_distance(i, p, N=2)
            try:
                sling.append(code[x][y])
            except IndexError:
                sling.append(" ")
        return list("".join(sling).rstrip())
    except FileNotFoundError:
        return ""


def keystroke(key):
    global string, cursor
    if key in ('enter', 'ctrl d'):
        raise ExitMainLoop()
    elif key=='backspace' and string:
        string.pop(cursor-1)
        if cursor > 0:
            cursor -= 1
    elif key=='delete' and string and cursor < len(string):
        string.pop(cursor)
    elif key == 'left' and cursor > 0:
        cursor -= 1
    elif key == 'right' and cursor < len(string):
        cursor += 1
    elif len(key) > 1:
        pass
    else:
        string.insert(cursor, key)
        cursor += 1
    if len(string) > 1:
        text.set_text(str_to_hilbert(string, cursor))
    else:
        text.set_text(''.join(string))

text = Text("""Just start writing...

The text will automatically align correctly. To exit, press Return.""")
string = []
cursor = 0
if len(sys.argv) > 1:
    string = hilbert_to_str(sys.argv[1])
    if len(string) > 1:
        text.set_text(str_to_hilbert(string))
    elif len(string) == 1:
        text.set_text(''.join(string))

filler = SolidFill(" ")
overlay = Overlay(Filler(text), filler, "center", 40, "middle", 40)

main = MainLoop(overlay, unhandled_input=keystroke)
main.run()

print("Do you want to save the file? (Ctrl+C to abort)")
try:
    default = sys.argv[1] if len(sys.argv)>1 else "test.act"
    fn = input("Save as [{}]: ".format(default))
    if not fn:
        fn = default
    with open(fn, "w") as f:
        if len(string) > 1:
            f.write(str_to_hilbert(string))
        else:
            f.write(string)
    print("Saved.")
except KeyboardInterrupt:
    pass
