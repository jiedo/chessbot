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

BOARD_MARKS = 'abcdefghijklmnopqrstuvwxyz'
BOARD_MARKS_LENGTH = len(BOARD_MARKS)

assert (BOARD_MARKS_LENGTH > WIDTH)
assert (BOARD_MARKS_LENGTH > HEIGHT)

def idtoa(i):
    if i < 0 or i > BOARD_MARKS_LENGTH:
        return 0
    return BOARD_MARKS[i]

def atoid(a):
    return BOARD_MARKS.find(a)


def chess_log(msg, op_side=" "):
    print >> sys.stderr, op_side, msg


def chess_operate(op):
    print op


class Bot():
    def __init__(self):
        self.b_started = False
        self.b_my_side = WHITE
        self.b_your_side = BLACK

        self.b_next = self.b_your_side

        self.board = [[BLANK] * WIDTH for i in range(HEIGHT)]


    def show_board(self):
        time.sleep(0.3)

        print >> sys.stderr, "   " + " ".join([idtoa(i) for i in range(WIDTH)])
        print >> sys.stderr, "   " + "_ " * WIDTH
        for i in range(HEIGHT):
            print >> sys.stderr, ("%2d|" % i) + " ".join(self.board[i])
        print >> sys.stderr, "   " + "_ " * WIDTH


    def check_point(self, a, b):
        if a < 0 or a >= HEIGHT:
            chess_log("a out of range.")
            return False

        if b < 0 or b >= WIDTH:
            chess_log("b out of range.")
            return False

        if self.board[a][b] != BLANK:
            chess_log("put twice. (%d, %d)" % (a, b))
            return False
        return True


    def chess_put(self, a, b):
        if self.b_next != self.b_my_side:
            chess_log("not my turn.")
            return False

        if self.check_point(a, b):
            self.board[a][b] = self.b_next
            chess_operate("%s %d %s %s" % (OP_PUT, a, idtoa(b), self.b_next))
            self.show_board()

            self.b_next = self.b_your_side
            return True

        return False


    def chess_get(self):
        if self.b_next != self.b_your_side:
            chess_log("not your turn.")
            return None, None

        line = raw_input()
        if line == "START":
            if not self.b_started:
                self.b_started = True
                self.b_my_side, self.b_your_side = self.b_your_side, self.b_my_side
                self.b_next = self.b_my_side
            return None, None

        if not line.startswith(OP_PUT):
            return None, None

        try:
            op_token, a, b, _ = line.split(" ", 3)
            if op_token == OP_PUT:
                a = int(a)
                b = atoid(b)

        except Exception, e:
            chess_log("error(%s): %s" % (line, e))
            #sys.exit(1)
            return None, None

        if op_token == OP_PUT and self.check_point(a, b):
            self.b_started = True
            self.board[a][b] = self.b_next
            self.b_next = self.b_my_side

            return a, b

        return None, None


    def is_winner(self, test_side):
        for i in range(HEIGHT):
            for j in range(WIDTH):
                if self.board[i][j] != test_side:
                    continue

                # row
                counter = 1
                for k in range(j):
                    if self.board[i][j-k-1] != test_side:
                        break
                    counter += 1
                for k in range(WIDTH-j-1):
                    if self.board[i][j+k+1] != test_side:
                        break
                    counter += 1
                if counter >= WIN_NUM:
                    return True


                # col
                counter = 1
                for k in range(i):
                    if self.board[i-k-1][j] != test_side:
                        break
                    counter += 1
                for k in range(WIDTH-i-1):
                    if self.board[i+k+1][j] != test_side:
                        break
                    counter += 1
                if counter >= WIN_NUM:
                    return True


                # up
                counter = 1
                h = min(HEIGHT-i-1, j)
                for k in range(h):
                    if self.board[i+k+1][j-k-1] != test_side:
                        break
                    counter += 1
                h = min(i, WIDTH-j-1)
                for k in range(h):
                    if self.board[i-k-1][j+k+1] != test_side:
                        break
                    counter += 1
                if counter >= WIN_NUM:
                    return True


                # down
                counter = 1
                h = min(i, j)
                for k in range(h):
                    if self.board[i-k-1][j-k-1] != test_side:
                        break
                    counter += 1
                h = min(HEIGHT-i-1, WIDTH-j-1)
                for k in range(h):
                    if self.board[i+k+1][j+k+1] != test_side:
                        break
                    counter += 1
                if counter >= WIN_NUM:
                    return True

        return False
