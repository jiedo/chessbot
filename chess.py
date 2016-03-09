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
WHITE_WIN = "\033[32mO\033[0m"
BLACK_WIN = "\033[32m*\033[0m"


OP_PUT = "PUT"
BOARD_MARKS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
BOARD_MARKS_LENGTH = len(BOARD_MARKS)
BLANK_ID = 0
WHITE_ID = -1
BLACK_ID = 1
WHITE_WIN_ID = 3
BLACK_WIN_ID = 2

MARK_WIN = {
    WHITE_ID: WHITE_WIN_ID,
    BLACK_ID: BLACK_WIN_ID,
}

NOTE_TO_ID = {
    BLANK: BLANK_ID,
    WHITE: WHITE_ID,
    BLACK: BLACK_ID,
}
ID_TO_NOTE = [BLANK, BLACK, BLACK_WIN, WHITE_WIN, WHITE]

POINT_NEED_UPDATE = 12
DIRECTION_ROW = 0
DIRECTION_WEST = 1
DIRECTION_EAST = 2

DIRECTION_COL = 3
DIRECTION_SOUTH = 4
DIRECTION_NORTH = 5

DIRECTION_DOWN = 6
DIRECTION_NORTHWEST = 7
DIRECTION_SOUTHEAST = 8

DIRECTION_UP = 9
DIRECTION_SOUTHWEST = 10
DIRECTION_NORTHEAST = 11

assert (BOARD_MARKS_LENGTH > WIDTH)
assert (BOARD_MARKS_LENGTH > HEIGHT)

g_debug_info = False

def idtoa(point_w):
    if point_w < 0 or point_w > BOARD_MARKS_LENGTH:
        return BOARD_MARKS[0]
    return BOARD_MARKS[point_w]


def atoid(mark_w):
    return BOARD_MARKS.find(str(mark_w))


def get_notename_of_point(point_h, point_w):
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
        self.started = False
        self.my_side = WHITE_ID
        self.your_side = BLACK_ID
        self.side_this_turn = self.your_side
        self.board = [[BLANK_ID] * WIDTH for h in range(HEIGHT)]
        self.board_separate_line = "- " * WIDTH
        self.notes = []

        self.direction_space_count_cache_at_point = [ [[1] * 13
                                                       for w in range(WIDTH)]
                                                      for h in range(HEIGHT)]
        self.direction_chain_count_cache_at_point = [ [[1] * 13
                                                       for w in range(WIDTH)]
                                                      for h in range(HEIGHT)]

    def board_dumps(self):
        print >> sys.stderr, "   " + self.board_separate_line

        for i in range(HEIGHT, 0, -1):
            print >> sys.stderr, ("%2d|" % i) + " ".join([ID_TO_NOTE[note_id]
                                                          for note_id in self.board[i-1]]) + "|"

        print >> sys.stderr, "   " + self.board_separate_line
        print >> sys.stderr, "   " + " ".join([idtoa(i) for i in range(WIDTH)])


    def board_loads(self, board_block):
        self.my_side = WHITE_ID
        self.your_side = BLACK_ID
        self.side_this_turn = self.your_side

        board_block_lines = board_block.split("\n")
        if len(board_block_lines) < HEIGHT + 5:
            chess_log("error in board_loads: not enough lines.")
            return False
        board_block_lines.reverse()

        count_balance = 0
        for height, line_side_notes in enumerate(board_block_lines[3:-2]):
            height_label, side_notes, _ = line_side_notes.split("|")
            for i in range(WIDTH):
                note = side_notes[i*2]
                if note in [BLACK, WHITE, BLANK]:
                    self.board[height][i] = NOTE_TO_ID[note]
                else:
                    chess_log("error in board_loads: note '%s' is illegal." % note)
                    return False

                if note == BLACK:
                    count_balance += 1
                    self.swap_turn_side()
                elif note == WHITE:
                    count_balance -= 1
                    self.swap_turn_side()

        if count_balance > 1 or count_balance < 0:
            chess_log("error in board_loads: notes[%d] is not balance." % count_balance)
            return False

        if self.side_this_turn == self.your_side:
            assert(count_balance == 0)
            self.swap_user_side()
        else:
            assert(count_balance == 1)

        return True


    def light_on_win_points(self):
        for h, w in self.win_points:
            test_side = self.board[h][w]
            test_side_win = MARK_WIN[test_side]
            self.board[h][w] = test_side_win


    def can_put_at_point(self, point_h, point_w):
        if point_h < 0 or point_h >= HEIGHT:
            chess_log("point_h(%d) out of range." % point_h, level="DEBUG")
            return False
        if point_w < 0 or point_w >= WIDTH:
            chess_log("point_w(%d) out of range." % point_w, level="DEBUG")
            return False
        if self.board[point_h][point_w] != BLANK_ID:
            chess_log("put twice. (%s)" % get_notename_of_point(point_h, point_w), level="DEBUG")
            return False
        return True


    def swap_user_side(self):
        self.my_side, self.your_side = self.your_side, self.my_side


    def swap_turn_side(self):
        if self.side_this_turn == self.my_side:
            self.side_this_turn = self.your_side
        else:
            self.side_this_turn = self.my_side


    def put_chessman_at_point(self, put_side, point_h, point_w):
        if self.side_this_turn != put_side:
            chess_log("not %s turn." % put_side, level="DEBUG")
            return False

        if self.can_put_at_point(point_h, point_w):
            self.board[point_h][point_w] = self.side_this_turn
            operate = "%s %s %s" % (OP_PUT, get_notename_of_point(point_h, point_w), ID_TO_NOTE[self.side_this_turn])
            chess_operate(operate)
            self.notes += [operate]
            self.swap_turn_side()
            return True

        return False


    def get_point_of_chessman(self, get_side):
        if self.side_this_turn != get_side:
            chess_log("not %s turn." % get_side, level="DEBUG")
            return None, None

        line = raw_input()
        line = line.upper()
        if line == "START":
            if not self.started:
                self.started = True
                self.swap_user_side()
                self.side_this_turn = self.my_side
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

        if op_token == OP_PUT and self.can_put_at_point(point_h, point_w):
            self.started = True
            self.board[point_h][point_w] = self.side_this_turn
            self.notes += [line]
            self.swap_turn_side()
            return point_h, point_w

        return None, None


    def detect_positions_around_point(self, point_h, point_w):
        # 包括回调函数:
        #
        # self.callback_begin
        # self.callback_count
        # self.callback_end
        #
        # 在遍历中心点的4个主要方向时回调.
        # 开始遍历此方向时调用一次: callback_begin,
        # 遍历此方向上每一个位置调用: callback_count
        # 此方向遍历完毕调用: callback_end
        # 如果callback_end返回True, 则函数提前返回True
        #
        # 遍历完8个方向后, 返回False
        #
        h, w = point_h, point_w
        self.center_point = (point_h, point_w)
        self.center_side = self.board[h][w]

        # test row (-)
        self.callback_begin(DIRECTION_ROW)
        for k in range(min(WIN_NUM-1, w)):
            pt = (h, w-k-1)
            if self.callback_count(pt, DIRECTION_ROW, DIRECTION_WEST):
                break
        for k in range(min(WIN_NUM-1, WIDTH-w-1)):
            pt = (h, w+k+1)
            if self.callback_count(pt, DIRECTION_ROW, DIRECTION_EAST):
                break
        if self.callback_end(DIRECTION_ROW):
            return True

        # test col (|)
        self.callback_begin(DIRECTION_COL)
        for k in range(min(WIN_NUM-1, h)):
            pt = (h-k-1, w)
            if self.callback_count(pt, DIRECTION_COL, DIRECTION_SOUTH):
                break
        for k in range(min(WIN_NUM-1, WIDTH-h-1)):
            pt = (h+k+1, w)
            if self.callback_count(pt, DIRECTION_COL, DIRECTION_NORTH):
                break
        if self.callback_end(DIRECTION_COL):
            return True

        # test down (\)
        self.callback_begin(DIRECTION_DOWN)
        for k in range(min(WIN_NUM-1, HEIGHT-h-1, w)):
            pt = (h+k+1, w-k-1)
            if self.callback_count(pt, DIRECTION_DOWN, DIRECTION_NORTHWEST):
                break
        for k in range(min(WIN_NUM-1, h, WIDTH-w-1)):
            pt = (h-k-1, w+k+1)
            if self.callback_count(pt, DIRECTION_DOWN, DIRECTION_SOUTHEAST):
                break
        if self.callback_end(DIRECTION_DOWN):
            return True

        # test up (/)
        self.callback_begin(DIRECTION_UP)
        for k in range(min(WIN_NUM-1, h, w)):
            pt = (h-k-1, w-k-1)
            if self.callback_count(pt, DIRECTION_UP, DIRECTION_SOUTHWEST):
                break
        for k in range(min(WIN_NUM-1, HEIGHT-h-1, WIDTH-w-1)):
            pt = (h+k+1, w+k+1)
            if self.callback_count(pt, DIRECTION_UP, DIRECTION_NORTHEAST):
                break
        if self.callback_end(DIRECTION_UP):
            return True

        return False


    def callback_begin_winner(self, where):
        self.win_points = [self.center_point]
    def callback_count_winner(self, pt, where, part):
        if self.board[pt[0]][pt[1]] != self.center_side:
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
                if self.detect_positions_around_point(h, w):
                    return True
        return False


    def win_test(self, pt, test_side):
        self.callback_count = self.callback_count_winner
        self.callback_end = self.callback_end_winner
        self.callback_begin = self.callback_begin_winner

        (point_h, point_w) = pt
        self.board[point_h][point_w] = test_side
        if self.detect_positions_around_point(point_h, point_w):
            self.board[point_h][point_w] = BLANK_ID
            return True

        self.board[point_h][point_w] = BLANK_ID
        return False


    def callback_begin_chain(self, where):
        self.direction_chain_count[where] = 1
        # 单排连珠计数
        return
    def callback_count_chain(self, pt, where, part):
        if self.board[pt[0]][pt[1]] != self.center_side:
            return True
        self.direction_chain_count[where] += 1
        self.direction_chain_count[part] += 1
        return False
    def callback_end_chain(self, where):
        return False


    def callback_begin_space(self, where):
        self.direction_space_count[where] = 1
        # 单排有效空间计数
        return
    def callback_count_space(self, pt, where, part):
        if self.board[pt[0]][pt[1]] == -self.center_side:
            return True

        self.direction_space_count[where] += 1
        self.direction_space_count[part] += 1
        return False
    def callback_end_space(self, where):
        return False


    def callback_begin_space_cache(self, where):
        # 有效空间缓存purge
        return
    def callback_count_space_cache(self, pt, where, part):
        h, w = pt
        if self.board[h][w] == self.center_side:
            return True
        if self.board[h][w] == -self.center_side:
            self.direction_space_count_cache_at_point[h][w][POINT_NEED_UPDATE] = 1
        return False
    def callback_end_space_cache(self, where):
        return False


    def callback_begin_chain_cache(self, where):
        # 单排连珠计数缓存purge
        return
    def callback_count_chain_cache(self, pt, where, part):
        h, w = pt
        if self.board[h][w] == self.center_side:
            self.direction_chain_count_cache_at_point[h][w][POINT_NEED_UPDATE] = 1
            return False
        return True
    def callback_end_chain_cache(self, where):
        return False


    def callback_begin_blank_points(self, where):
        # 寻找焦点上的blank
        return
    def callback_count_blank_points(self, pt, where, part):
        if self.direction_space_count[where] < WIN_NUM:
            # 单排空间不足不计数
            return True
        if self.board[pt[0]][pt[1]] == -self.center_side:
            return True
        if self.board[pt[0]][pt[1]] == BLANK_ID:
            count = self.direction_chain_count[where]
            is_part_link = self.direction_chain_count[part]
            if is_part_link < 0:
                count = 1
            self.direction_chain_count[part] = -1
            self.blank_points_with_count_pair += [(pt, count)]
        return False
    def callback_end_blank_points(self, where):
        return False


    def do_some_cache_update_around_point(self, point_h, point_w):
        self.direction_space_count_cache_at_point[point_h][point_w][POINT_NEED_UPDATE] = 1
        self.callback_count = self.callback_count_space_cache
        self.callback_end = self.callback_end_space_cache
        self.callback_begin = self.callback_begin_space_cache
        self.detect_positions_around_point(point_h, point_w)

        self.direction_chain_count_cache_at_point[point_h][point_w][POINT_NEED_UPDATE] = 1
        self.callback_count = self.callback_count_chain_cache
        self.callback_end = self.callback_end_chain_cache
        self.callback_begin = self.callback_begin_chain_cache
        self.detect_positions_around_point(point_h, point_w)


    def get_all_blank_points_around_point(self, point_h, point_w):
        # 棋子周围能"有效影响"的空白的位置坐标
        # 其中:
        # 1. 空余连线必须不小于WIN_NUM
        # 2. 紧密相连的多个棋子对同一条线上的范围内的空白加分

        h, w = point_h, point_w
        center_side = self.board[h][w]
        if center_side == BLANK_ID:
            return []

        self.direction_space_count = self.direction_space_count_cache_at_point[h][w]
        if self.direction_space_count[POINT_NEED_UPDATE] == 1:
            self.direction_space_count[POINT_NEED_UPDATE] = 0
            self.callback_count = self.callback_count_space
            self.callback_end = self.callback_end_space
            self.callback_begin = self.callback_begin_space
            self.detect_positions_around_point(point_h, point_w)

        self.direction_chain_count = self.direction_chain_count_cache_at_point[h][w]
        if self.direction_chain_count[POINT_NEED_UPDATE] == 1:
            self.direction_chain_count[POINT_NEED_UPDATE] = 0
            self.callback_count = self.callback_count_chain
            self.callback_end = self.callback_end_chain
            self.callback_begin = self.callback_begin_chain
            self.detect_positions_around_point(point_h, point_w)

        self.blank_points_with_count_pair = []
        self.callback_count = self.callback_count_blank_points
        self.callback_end = self.callback_end_blank_points
        self.callback_begin = self.callback_begin_blank_points
        self.detect_positions_around_point(point_h, point_w)
        return self.blank_points_with_count_pair


    def get_score_of_blanks_for_side(self, test_side, is_dup_enforce=False):
        # 找出所有在棋盘中test_side棋子的位置坐标, 并找出每一个棋子周围能影响到的空白的位置坐标
        # 返回所有的空白位置坐标和对应的重复次数 pair

        # 获取所有在棋盘中test_side棋子的位置坐标
        all_my_points = []
        for h in range(HEIGHT):
            for w in range(WIDTH):
                if self.board[h][w] != test_side:
                    continue
                all_my_points += [(h, w)]

        chess_log("%s Points: %s" % (test_side,
                                     ", ".join([get_notename_of_point(h, w)
                                                for h, w in all_my_points])), level="DEBUG")
        all_my_blank_points_count = {}
        for point_h, point_w in all_my_points:
            # 获取每一个棋子周围能影响到的空白的位置坐标
            blank_points_around_hw = self.get_all_blank_points_around_point(point_h, point_w)
            for pt, count in blank_points_around_hw:
                if not is_dup_enforce:
                    count = 1
                all_my_blank_points_count[pt] = all_my_blank_points_count.get(pt, 0) + count

        if not all_my_blank_points_count:
            return []

        # 返回所有的空白位置坐标和对应的重复次数 pair
        all_my_blank_points_count_pair = all_my_blank_points_count.items()
        all_my_blank_points_count_pair.sort(key=lambda x:x[1])
        all_my_blank_points_count_pair.reverse()

        chess_log("%s Score: %s" % (
            test_side,
            ", ".join(["%s:%d" % (get_notename_of_point(h, w), count)
                       for (h, w), count in all_my_blank_points_count_pair if count > 3])), level="DEBUG")
        return all_my_blank_points_count_pair


    def is_a_good_choice(self, choice_pt, my_side, your_side, max_level=-1):
        # todo: 层序遍历, 最高得分先检查
        if max_level == 0:
            return False

        (point_h, point_w) = choice_pt
        self.board[point_h][point_w] = my_side
        self.do_some_cache_update_around_point(point_h, point_w)
        chess_log("%s TEST GOOD CHOICE[%d]: %s" % (my_side, max_level,
                                                  get_notename_of_point(point_h, point_w)), level="DEBUG")

        is_dup_enforce = False
        all_my_blank_points_count_pair = self.get_score_of_blanks_for_side(my_side,
                                                                           is_dup_enforce=is_dup_enforce)

        count_win_point = 0
        for my_pt, count in all_my_blank_points_count_pair:
            # 先扫一遍有没有多处直接胜利的, count<4的点不可能胜利
            if count < 4: continue
            if self.win_test(my_pt, my_side):
                count_win_point += 1
                if count_win_point > 1:
                    self.do_some_cache_update_around_point(point_h, point_w)
                    self.board[point_h][point_w] = BLANK_ID
                    return True

        tested_not_good_pt = []
        for my_pt, count in all_my_blank_points_count_pair:
            tested_not_good_pt += [my_pt]
            if not self.is_a_bad_choice(my_pt, your_side, my_side, max_level=max_level):
                self.do_some_cache_update_around_point(point_h, point_w)
                self.board[point_h][point_w] = BLANK_ID
                return False

        is_dup_enforce = False
        all_your_blank_points_count_pair = self.get_score_of_blanks_for_side(your_side,
                                                                         is_dup_enforce=is_dup_enforce)
        for your_pt, count in all_your_blank_points_count_pair:
            if your_pt in tested_not_good_pt: continue
            if not self.is_a_bad_choice(your_pt, your_side, my_side, max_level=max_level):
                self.do_some_cache_update_around_point(point_h, point_w)
                self.board[point_h][point_w] = BLANK_ID
                return False

        self.do_some_cache_update_around_point(point_h, point_w)
        self.board[point_h][point_w] = BLANK_ID
        return True


    def is_a_bad_choice(self, choice_pt, my_side, your_side, max_level=-1):
        # todo: 层序遍历, 最高得分先检查
        if max_level == 0:
            return False

        (point_h, point_w) = choice_pt
        self.board[point_h][point_w] = my_side
        self.do_some_cache_update_around_point(point_h, point_w)
        chess_log("%s TEST BAD CHOICE[%d]: %s" % (my_side, max_level,
                                                  get_notename_of_point(point_h, point_w)), level="DEBUG")

        is_dup_enforce = False
        all_your_blank_points_count_pair = self.get_score_of_blanks_for_side(your_side,
                                                                             is_dup_enforce=is_dup_enforce)
        for your_pt, count in all_your_blank_points_count_pair:
            # 先扫一遍有没有直接胜利的, count<4的点不可能胜利
            if count >= 4:
                if self.win_test(your_pt, your_side):
                    self.do_some_cache_update_around_point(point_h, point_w)
                    self.board[point_h][point_w] = BLANK_ID
                    return True
        for your_pt, count in all_your_blank_points_count_pair:
            if count > 1:
                # tofix: 不应该忽视count==1的点, 但为了减少计算
                if self.is_a_good_choice(your_pt, your_side, my_side, max_level=max_level-1):
                    self.do_some_cache_update_around_point(point_h, point_w)
                    self.board[point_h][point_w] = BLANK_ID
                    return True

        self.do_some_cache_update_around_point(point_h, point_w)
        self.board[point_h][point_w] = BLANK_ID
        return False
