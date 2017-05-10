from urwid import MainLoop, SolidFill, ExitMainLoop, Edit, Overlay, Columns, Pile, Text, Filler, LineBox, BoxAdapter
from hilbert_curve import hilbert
from math import ceil, log2
from collections import defaultdict

def str_to_hilbert(string):
    p = ceil(log2(len(string)**.5))
    d = defaultdict(lambda:defaultdict(str))
    for i, c in enumerate(string):
        y, x = hilbert.coordinates_from_distance(i, p, N=2)
        d[x][y] = c
    return "\n".join(
            "".join(d[y][x] for x in range(2**p)) for y in reversed(range(2**p))
            )

string = ""

def quitter(key):
    global string
    if key == 'enter':
        raise ExitMainLoop()
    elif key=='backspace':
        string = string[:-1]
    else:
        string += key
    if len(string) > 1:
        text.set_text(str_to_hilbert(string))
    else:
        text.set_text(string)

text = Text("""Just start writing...

The text will automatically align correctly. To exit, press Return.""")
filler = SolidFill(" ")
overlay = Overlay(Filler(text), filler, "center", 40, "middle", 40)

main = MainLoop(overlay, unhandled_input=quitter, palette=[
    ('headings', 'white,underline', 'black', 'bold,underline'), # bold text in monochrome mode
    ('body_text', 'dark cyan', 'light gray'),
    ('buttons', 'yellow', 'dark green', 'standout'),
    ('section_text', 'body_text'), # alias to body_text
    ])
main.run()
