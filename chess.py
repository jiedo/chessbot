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

OP_PUT = "PUT"

BOARD_MARKS = 'abcdefghijklmnopqrstuvwxyz'
BOARD_MARKS_LENGTH = len(BOARD_MARKS)

assert (BOARD_MARKS_LENGTH > WIDTH)
assert (BOARD_MARKS_LENGTH > HEIGHT)

def idtoa(point_w):
    if point_w < 0 or point_w > BOARD_MARKS_LENGTH:
        return BOARD_MARKS[0]
    return BOARD_MARKS[point_w]

def atoid(mark_w):
    return BOARD_MARKS.find(str(mark_w))


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


    def check_point(self, point_h, point_w):
        if point_h < 0 or point_h >= HEIGHT:
            chess_log("point_h out of range.")
            return False

        if point_w < 0 or point_w >= WIDTH:
            chess_log("point_w out of range.")
            return False

        if self.board[point_h][point_w] != BLANK:
            chess_log("put twice. (%d, %d)" % (point_h, point_w))
            return False
        return True


    def chess_put(self, point_h, point_w):
        if self.b_next != self.b_my_side:
            chess_log("not my turn.")
            return False

        if self.check_point(point_h, point_w):
            self.board[point_h][point_w] = self.b_next
            chess_operate("%s %d %s %s" % (OP_PUT, point_h, idtoa(point_w), self.b_next))
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
            op_token, point_h, point_w, _ = line.split(" ", 3)
            if op_token == OP_PUT:
                point_h = int(point_h)
                x = atoid(point_w)
                if x < 0:
                    point_w = int(point_w)
                else:
                    point_w = x

        except Exception, e:
            chess_log("error(%s): %s" % (line, e))
            #sys.exit(1)
            return None, None

        if op_token == OP_PUT and self.check_point(point_h, point_w):
            self.b_started = True
            self.board[point_h][point_w] = self.b_next
            self.b_next = self.b_my_side

            return point_h, point_w

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
