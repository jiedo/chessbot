#!/usr/bin/env python
#encoding: utf-8

import sys
import time


WIDTH = 15
HEIGHT = 15
WIN_NUM = 5
BLANK = " "
WHITE = "O"
BLACK = "*"
MARK_WIN = {
    WHITE: "\033[32mO\033[0m",
    BLACK: "\033[32m*\033[0m",
}

OP_PUT = "PUT"
BOARD_MARKS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
BOARD_MARKS_LENGTH = len(BOARD_MARKS)

assert (BOARD_MARKS_LENGTH > WIDTH)
assert (BOARD_MARKS_LENGTH > HEIGHT)

g_debug_info = False
 
def idtoa(point_w):
    if point_w < 0 or point_w > BOARD_MARKS_LENGTH:
        return BOARD_MARKS[0]
    return BOARD_MARKS[point_w]


def atoid(mark_w):
    return BOARD_MARKS.find(str(mark_w))


def chess_log(msg, level="INFO"):
    if level == "DEBUG" and not g_debug_info:
        return 
    print >> sys.stderr, msg


def chess_operate(op):
    chess_log(op)
    print op


class Bot():
    def __init__(self):
        self.b_started = False
        self.b_my_side = WHITE
        self.b_your_side = BLACK
        self.b_next = self.b_your_side
        self.board = [[BLANK] * WIDTH for i in range(HEIGHT)]
        self.notes = []
       

    def show_board(self):
        print >> sys.stderr, "   " + "- " * WIDTH
        for i in range(HEIGHT, 0, -1):
            print >> sys.stderr, ("%2d|" % i) + " ".join(self.board[i-1]) + "|"
        print >> sys.stderr, "   " + "- " * WIDTH
        print >> sys.stderr, "   " + " ".join([idtoa(i) for i in range(WIDTH)])
        time.sleep(0.03)

    def check_point(self, point_h, point_w):
        if point_h < 0 or point_h >= HEIGHT:
            chess_log("point_h(%d) out of range." % point_h, level="DEBUG")
            return False
        if point_w < 0 or point_w >= WIDTH:
            chess_log("point_w(%d) out of range." % point_w, level="DEBUG")
            return False
        if self.board[point_h][point_w] != BLANK:
            chess_log("put twice. (%d, %d)" % (point_h, point_w), level="DEBUG")
            return False
        return True


    def chess_put(self, point_h, point_w):
        if self.b_next != self.b_my_side:
            chess_log("not my turn.", level="DEBUG")
            return False

        if self.check_point(point_h, point_w):
            self.board[point_h][point_w] = self.b_next
            operate = "%s %s%d %s" % (OP_PUT, idtoa(point_w), point_h+1, self.b_next)
            chess_operate(operate)
            self.notes += [operate]                       
            self.b_next = self.b_your_side
            return True

        return False


    def chess_get(self):
        if self.b_next != self.b_your_side:
            chess_log("not your turn.", level="DEBUG")
            return None, None

        line = raw_input()
        line = line.upper()        
        if line == "START":
            if not self.b_started:
                self.b_started = True
                self.b_my_side, self.b_your_side = self.b_your_side, self.b_my_side
                self.b_next = self.b_my_side
            return None, None

        if not line.startswith(OP_PUT):
            return None, None

        try:
            if len(line.split()) == 2:
                op_token, point_token = line.split()                
            else:
                op_token, point_token, _ = line.split(" ", 2)

            point_w, point_h = point_token[0], point_token[1:]
            point_h = int(point_h) - 1
            point_w = atoid(point_w)
        except Exception, e:
            chess_log("error(%s): %s" % (line, e), level="DEBUG")
            return None, None

        if op_token == OP_PUT and self.check_point(point_h, point_w):
            self.b_started = True
            self.board[point_h][point_w] = self.b_next
            self.notes += [line]                                   
            self.b_next = self.b_my_side
            return point_h, point_w

        return None, None


    def light_on_win_points(self):
        for h, w in self.win_points:
            test_side = self.board[h][w]
            test_side_win = MARK_WIN[test_side]
            self.board[h][w] = test_side_win
        

    def is_winner(self, test_side):
        for h in range(HEIGHT):
            for w in range(WIDTH):
                if self.board[h][w] != test_side:
                    continue
                # test row (-)
                self.win_points = [(h, w)]
                for k in range(w):
                    if self.board[h][w-k-1] != test_side:
                        break
                    self.win_points += [(h, w-k-1)]
                for k in range(WIDTH-w-1):
                    if self.board[h][w+k+1] != test_side:
                        break
                    self.win_points += [(h, w+k+1)]
                if len(self.win_points) >= WIN_NUM:
                    return True

                # test col (|)
                self.win_points = [(h, w)]
                for k in range(h):
                    if self.board[h-k-1][w] != test_side:
                        break
                    self.win_points += [(h-k-1, w)]
                for k in range(WIDTH-h-1):
                    if self.board[h+k+1][w] != test_side:
                        break
                    self.win_points += [(h+k+1, w)]
                if len(self.win_points) >= WIN_NUM:
                    return True

                # test down (\)
                self.win_points = [(h, w)]
                min_len = min(HEIGHT-h-1, w)
                for k in range(min_len):
                    if self.board[h+k+1][w-k-1] != test_side:
                        break
                    self.win_points += [(h+k+1, w-k-1)]
                min_len = min(h, WIDTH-w-1)
                for k in range(min_len):
                    if self.board[h-k-1][w+k+1] != test_side:
                        break
                    self.win_points += [(h-k-1, w+k+1)]
                if len(self.win_points) >= WIN_NUM:
                    return True

                # test up (/)
                self.win_points = [(h, w)]
                min_len = min(h, w)
                for k in range(min_len):
                    if self.board[h-k-1][w-k-1] != test_side:
                        break
                    self.win_points += [(h-k-1, w-k-1)]
                min_len = min(HEIGHT-h-1, WIDTH-w-1)
                for k in range(min_len):
                    if self.board[h+k+1][w+k+1] != test_side:
                        break
                    self.win_points += [(h+k+1, w+k+1)]
                if len(self.win_points) >= WIN_NUM:
                    return True

        return False
