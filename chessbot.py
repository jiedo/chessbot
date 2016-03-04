#!/usr/bin/env python
#encoding: utf-8

import sys
import time


BLANK = " "
WHITE = "O"
BLACK = "X"


WIN_NUM = 5
WIDTH = 17
HEIGHT = 17

OP_PUT = "OP_PUT"

g_started = False
g_my_side = WHITE
g_your_side = BLACK

g_next = g_your_side

g_board = [[BLANK] * WIDTH for i in range(HEIGHT)]


def chess_log(msg, op_side=" "):
    print >> sys.stderr, op_side, msg


def chess_operate(op):
    print op


def show_board():
    global g_board
    time.sleep(1)
    print >> sys.stderr, "_" * WIDTH
    for i in range(HEIGHT):
        print >> sys.stderr, "".join(g_board[i])
    print >> sys.stderr, " " * WIDTH


def chess_check(a, b):
    global g_board

    if a < 0 or a >= HEIGHT:
        chess_log("a out of range.")
        return False

    if b < 0 or b >= WIDTH:
        chess_log("b out of range.")
        return False

    if g_board[a][b] != BLANK:
        chess_log("put twice. (%d, %d)" % (a, b))
        return False
    return True


def chess_put(a, b):
    global g_board, g_next, g_your_side, g_started, g_my_side

    if g_next != g_my_side:
        chess_log("not my turn.")
        return False

    if chess_check(a, b):
        g_board[a][b] = g_next
        chess_operate("%s %d %d %s" % (OP_PUT, a, b, g_next))
        show_board()

        g_next = g_your_side
        return True

    return False

def chess_get():
    global g_board, g_next, g_your_side, g_started, g_my_side

    if g_next != g_your_side:
        chess_log("not op's turn.")
        return None, None

    line = raw_input()
    if line == "START":
        if not g_started:
            g_started = True
            g_my_side, g_your_side = g_your_side, g_my_side
            g_next = g_my_side
        return None, None

    if not line.startswith(OP_PUT):
        return None, None

    try:
        op_token, a, b, _ = line.split(" ", 3)
        if op_token == OP_PUT:
            a = int(a)
            b = int(b)
    except Exception, e:
        chess_log("error(%s): %s" % (line, e))
        #sys.exit(1)
        return None, None

    if op_token == OP_PUT and chess_check(a, b):
        g_started = True
        g_board[a][b] = g_next
        g_next = g_my_side

        return a, b

    return None, None


def is_winner(test_side):
    global g_board

    for i in range(HEIGHT):
        for j in range(WIDTH):
            if g_board[i][j] != test_side:
                continue

            # row
            counter = 1
            for k in range(j):
                if g_board[i][j-k-1] != test_side:
                    break
                counter += 1
            for k in range(WIDTH-j-1):
                if g_board[i][j+k+1] != test_side:
                    break
                counter += 1
            if counter >= WIN_NUM:
                return True


            # col
            counter = 1
            for k in range(i):
                if g_board[i-k-1][j] != test_side:
                    break
                counter += 1
            for k in range(WIDTH-i-1):
                if g_board[i+k+1][j] != test_side:
                    break
                counter += 1
            if counter >= WIN_NUM:
                return True


            # up
            counter = 1
            h = min(HEIGHT-i-1, j)
            for k in range(h):
                if g_board[i+k+1][j-k-1] != test_side:
                    break
                counter += 1
            h = min(i, WIDTH-j-1)
            for k in range(h):
                if g_board[i-k-1][j+k+1] != test_side:
                    break
                counter += 1
            if counter >= WIN_NUM:
                return True


            # down
            counter = 1
            h = min(i, j)
            for k in range(h):
                if g_board[i-k-1][j-k-1] != test_side:
                    break
                counter += 1
            h = min(HEIGHT-i-1, WIDTH-j-1)
            for k in range(h):
                if g_board[i+k+1][j+k+1] != test_side:
                    break
                counter += 1
            if counter >= WIN_NUM:
                return True

    return False


def main():
    global g_next, g_your_side, g_started, g_my_side

    if len(sys.argv) == 2:
        if sys.argv[1] == "-w":
            chess_operate("START")

    while True:
        while g_next == g_your_side:
            a, b = chess_get()
            time.sleep(0.1)

        if is_winner(g_your_side):
            break

        a, b = strategy()
        chess_put(a, b)
        time.sleep(0.1)
        if is_winner(g_my_side):
            chess_log("%s Win." % g_my_side)
            break


def strategy():
    if g_my_side == BLACK:
        return strategy2()
    else:
        return strategy9()


def strategy0():
    global g_board, g_next, g_your_side, g_started, g_my_side
    for i in range(HEIGHT):
        for j in range(WIDTH):
            if g_board[i][j] == BLANK:
                return i, j

def strategy1():
    global g_board, g_next, g_your_side, g_started, g_my_side
    for i in range(HEIGHT):
        if g_board[i][0] == BLANK:
                return i, 0

def strategy2():
    global g_board, g_next, g_your_side, g_started, g_my_side
    for i in range(HEIGHT):
        if g_board[i][i] == BLANK:
                return i, i


def strategy9():
    global g_board, g_next, g_your_side, g_started, g_my_side
    for i in range(HEIGHT):
        for j in range(WIDTH):
            if g_board[HEIGHT-i-1][WIDTH-j-1] == BLANK:
                return HEIGHT-i-1, WIDTH-j-1



if __name__ == "__main__":
    main()
