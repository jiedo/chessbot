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


def point_to_mark(point_h, point_w):
    return "%s%d" % (idtoa(point_w), point_h+1)


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


    def get_board(self, pt):
        h, w = pt
        return self.board[h][w]


    def check_point(self, point_h, point_w):
        if point_h < 0 or point_h >= HEIGHT:
            chess_log("point_h(%d) out of range." % point_h, level="DEBUG")
            return False
        if point_w < 0 or point_w >= WIDTH:
            chess_log("point_w(%d) out of range." % point_w, level="DEBUG")
            return False
        if self.board[point_h][point_w] != BLANK:
            chess_log("put twice. (%s)" % point_to_mark(point_h, point_w), level="DEBUG")
            return False
        return True


    def chess_put(self, point_h, point_w):
        if self.b_next != self.b_my_side:
            chess_log("not my turn.", level="DEBUG")
            return False

        if self.check_point(point_h, point_w):
            self.board[point_h][point_w] = self.b_next
            operate = "%s %s %s" % (OP_PUT, point_to_mark(point_h, point_w), self.b_next)
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


    def test_point_around(self, point_h, point_w):
        h, w = point_h, point_w
        self.center_point = (point_h, point_w)
        self.center_side = self.board[h][w]

        # test row (-)
        self.callback_begin("row")
        for k in range(min(WIN_NUM-1, w)):
            pt = (h, w-k-1)
            if self.callback_count(pt, "row", "west"):
                break
        for k in range(min(WIN_NUM-1, WIDTH-w-1)):
            pt = (h, w+k+1)
            if self.callback_count(pt, "row", "east"):
                break
        if self.callback_end("row"):
            return True

        # test col (|)
        self.callback_begin("col")
        for k in range(min(WIN_NUM-1, h)):
            pt = (h-k-1, w)
            if self.callback_count(pt, "col", "south"):
                break
        for k in range(min(WIN_NUM-1, WIDTH-h-1)):
            pt = (h+k+1, w)
            if self.callback_count(pt, "col", "north"):
                break
        if self.callback_end("col"):
            return True

        # test down (\)
        self.callback_begin("down")
        for k in range(min(WIN_NUM-1, HEIGHT-h-1, w)):
            pt = (h+k+1, w-k-1)
            if self.callback_count(pt, "down", "northwest"):
                break
        for k in range(min(WIN_NUM-1, h, WIDTH-w-1)):
            pt = (h-k-1, w+k+1)
            if self.callback_count(pt, "down", "southeast"):
                break
        if self.callback_end("down"):
            return True

        # test up (/)
        self.callback_begin("up")
        for k in range(min(WIN_NUM-1, h, w)):
            pt = (h-k-1, w-k-1)
            if self.callback_count(pt, "up", "southwest"):
                break
        for k in range(min(WIN_NUM-1, HEIGHT-h-1, WIDTH-w-1)):
            pt = (h+k+1, w+k+1)
            if self.callback_count(pt, "up", "northeast"):
                break
        if self.callback_end("up"):
            return True

        return False


    def light_on_win_points(self):
        for h, w in self.win_points:
            test_side = self.board[h][w]
            test_side_win = MARK_WIN[test_side]
            self.board[h][w] = test_side_win


    def callback_begin_winner(self, where):
        self.win_points = [self.center_point]
    def callback_count_winner(self, pt, where, part):
        if self.get_board(pt) != self.center_side:
            return True
        self.win_points += [pt]
        return False
    def callback_end_winner(self, where):
        if len(self.win_points) >= WIN_NUM:
            return True
        return False
    def is_winner(self, test_side):
        self.callback_count = self.callback_count_winner
        self.callback_end = self.callback_end_winner
        self.callback_begin = self.callback_begin_winner

        for h in range(HEIGHT):
            for w in range(WIDTH):
                if self.board[h][w] != test_side:
                    continue

                if self.test_point_around(h, w):
                    return True
        return False


    def win_test(self, pt, test_side):
        self.callback_count = self.callback_count_winner
        self.callback_end = self.callback_end_winner
        self.callback_begin = self.callback_begin_winner

        backup_side = self.get_board(pt)

        (point_h, point_w) = pt
        self.board[point_h][point_w] = test_side
        if self.test_point_around(point_h, point_w):
            self.board[point_h][point_w] = backup_side
            return True

        self.board[point_h][point_w] = backup_side
        return False


    def callback_begin_chain(self, where):
        self.direction_chain_count[where] = 1
        # 单排连珠计数
        return
    def callback_count_chain(self, pt, where, part):
        if self.get_board(pt) != self.center_side:
            return True
        self.direction_chain_count[where] = self.direction_chain_count.get(where, 0) + 1
        self.direction_chain_count[part] = self.direction_chain_count.get(part, 0) + 1
        return False
    def callback_end_chain(self, where):
        return False


    def callback_begin_space(self, where):
        self.direction_space_count[where] = 1
        # 单排有效空间计数
        return
    def callback_count_space(self, pt, where, part):
        if self.get_board(pt) not in [self.center_side, BLANK]:
            return True
        self.direction_space_count[where] = self.direction_space_count.get(where, 0) + 1
        self.direction_space_count[part] = self.direction_space_count.get(part, 0) + 1
        return False
    def callback_end_space(self, where):
        return False


    def callback_begin_blank_points(self, where):
        # 寻找焦点上的blank
        return
    def callback_count_blank_points(self, pt, where, part):
        if self.direction_space_count[where] < WIN_NUM:
            # 单排空间不足不计数
            return True

        if self.get_board(pt) == self.center_side:
            pass
        elif self.get_board(pt) == BLANK:
            counter = self.direction_chain_count[where]
            is_part_link = self.direction_chain_count.get(part, 0)
            if is_part_link < 0:
                counter = 1
            self.direction_chain_count[part] = -1
            self.blank_points += [(pt, counter)]
        else:
            return True
        return False
    def callback_end_blank_points(self, where):
        return False


    def all_blank_points_around(self, point_h, point_w, test_space=False):
        h, w = point_h, point_w
        center_side = self.board[h][w]
        if center_side == BLANK:
            return []

        self.direction_space_count = {}
        if test_space:
            self.callback_count = self.callback_count_space
            self.callback_end = self.callback_end_space
            self.callback_begin = self.callback_begin_space
            self.test_point_around(point_h, point_w)
        else:
            self.direction_space_count = {
                "row": 5,
                "col": 5,
                "up": 5,
                "down": 5,
            }

        self.direction_chain_count = {}
        self.callback_count = self.callback_count_chain
        self.callback_end = self.callback_end_chain
        self.callback_begin = self.callback_begin_chain
        self.test_point_around(point_h, point_w)

        self.blank_points = []
        self.callback_count = self.callback_count_blank_points
        self.callback_end = self.callback_end_blank_points
        self.callback_begin = self.callback_begin_blank_points
        self.test_point_around(point_h, point_w)
        return self.blank_points


    def get_score_of_blanks_side(self, test_side, test_space=False, dup=False):
        all_my_points = []
        for h in range(HEIGHT):
            for w in range(WIDTH):
                if self.board[h][w] != test_side:
                    continue
                all_my_points += [(h, w)]

        chess_log("%s Points: %s" % (test_side,
                                         ", ".join([point_to_mark(h, w)
                                                    for h, w in all_my_points])), level="DEBUG")
        all_my_blank_points_count = {}
        for point_h, point_w in all_my_points:
            blank_points_around_hw = self.all_blank_points_around(point_h, point_w, test_space)
            for pt, counter in blank_points_around_hw:
                if not dup:
                    counter = 1
                all_my_blank_points_count[pt] = all_my_blank_points_count.get(pt, 0) + counter

        if not all_my_blank_points_count:
            return []

        all_my_blank_points_count_pair = all_my_blank_points_count.items()
        all_my_blank_points_count_pair.sort(key=lambda x:x[1])
        all_my_blank_points_count_pair.reverse()

        chess_log("%s Score: %s" % (
            test_side,
            ", ".join(["%s:%d" % (point_to_mark(h, w), count)
                       for (h, w), count in all_my_blank_points_count_pair if count > 3])), level="DEBUG")
        return all_my_blank_points_count_pair



    def is_a_good_choice(self, choice_pt, my_side, your_side, max_level=-1):
        if max_level == 0:
            return False

        (point_h, point_w) = choice_pt
        self.board[point_h][point_w] = my_side
        chess_log("%s TEST GOOD CHOICE[%d]: %s" % (my_side, max_level,
                                                  point_to_mark(point_h, point_w)), level="DEBUG")

        is_dup_enforce = False
        is_space_enough = True
        all_my_blank_points_count_pair = self.get_score_of_blanks_side(my_side,
                                                                       dup=is_dup_enforce,
                                                                       test_space=is_space_enough)
        tested_not_good_pt = []
        for my_pt, count in all_my_blank_points_count_pair:
            tested_not_good_pt += [my_pt]
            if not self.is_a_bad_choice(my_pt, your_side, my_side, max_level=max_level):
                self.board[point_h][point_w] = BLANK
                return False

        is_dup_enforce = False
        is_space_enough = True
        all_your_blank_points_count_pair = self.get_score_of_blanks_side(your_side,
                                                                         dup=is_dup_enforce,
                                                                         test_space=is_space_enough)
        for your_pt, count in all_your_blank_points_count_pair:
            if your_pt in tested_not_good_pt: continue
            if not self.is_a_bad_choice(your_pt, your_side, my_side, max_level=max_level):
                self.board[point_h][point_w] = BLANK
                return False

        self.board[point_h][point_w] = BLANK
        return True


    def is_a_bad_choice(self, choice_pt, my_side, your_side, max_level=-1):
        if max_level == 0:
            return False

        (point_h, point_w) = choice_pt
        self.board[point_h][point_w] = my_side
        chess_log("%s TEST BAD CHOICE[%d]: %s" % (my_side, max_level,
                                                  point_to_mark(point_h, point_w)), level="DEBUG")

        is_dup_enforce = False
        is_space_enough = True
        all_your_blank_points_count_pair = self.get_score_of_blanks_side(your_side,
                                                                         dup=is_dup_enforce,
                                                                         test_space=is_space_enough)
        for your_pt, count in all_your_blank_points_count_pair:
            if count > 2:
                if self.win_test(your_pt, your_side):
                    self.board[point_h][point_w] = BLANK
                    return True

                if self.is_a_good_choice(your_pt, your_side, my_side, max_level=max_level-1):
                    self.board[point_h][point_w] = BLANK
                    return True
        self.board[point_h][point_w] = BLANK
        return False
