#!/usr/bin/env python
#encoding: utf-8

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

g_board = [[BLANK] * WIDTH] * HEIGHT



def check(a, b):
    if a < 0 or a >= HEIGHT:
        print "a out of range."
        return False

    if b < 0 or b >= WIDTH:
        print "b out of range."
        return False

    if g_board[a][b] != BLANK:
        print "put twice."
        return False
    return True


def put(a, b):
    if g_next != g_my_side:
        print "not my turn."
        return

    if check(a, b):
        g_board[a][b] = g_next
    g_next = g_your_side
    print "%s %d %d" % (OP_PUT, a, b)



def get():
    if g_next != g_your_side:
        print "not op's turn."
        return

    line = raw_input()
    if line == "start":
        if not g_started:
            g_started = True
            g_my_side, g_your_side = g_your_side, g_my_side
            g_next = g_my_side
        return None, None

    try:
        op_token, a, b = line.split()
        a = int(a)
        b = int(b)
    except:
        return None, None

    if op_token == OP_PUT and check(a, b):
        g_started = True
        g_board[a][b] = g_next
        g_next = g_my_side

        return a, b

    return None, None


def is_winner(test_side):
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



def strategy():
    a, b = 1, 1


    return a, b


def main():
    while True:
        while g_next == g_your_side:
            a, b = get()

        if is_winner(g_your_side):
            print g_your_side, "Win."
            break

        a, b = strategy()
        put(a, b)

        if is_winner(g_my_side):
            print g_my_side, "Win."
            break


if __name__ == "__main__":
    main()
