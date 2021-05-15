# main.py

import curses

BLACK_STONE = "X"
WHITE_STONE = "O"
INTERSECTION = "+"
MIDSECTION = "-"

def draw():
    screen = curses.initscr()
    for i in range(curses.LINES - 1):
        for j in range(curses.COLS - 1):
            if i % 2 == 0 and j % 2 == 0:
                screen.addch(i, j, "|")
            elif i % 2 == 1:
                screen.addch(i, j, INTERSECTION if j % 6 == 0 else BLACK_STONE if j % 6 == 2 else WHITE_STONE if j % 6 == 4 else MIDSECTION)
    curses.curs_set(1)
    screen.refresh()
    curses.napms(3000)

if __name__ == "__main__":
    draw()