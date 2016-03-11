#!/usr/bin/env python
#encoding: utf-8

import sys
import time


WIDTH = 15
HEIGHT = 15
WIN_NUM = 5
BLANK = "."
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

POINT_NOTE = 0

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

OPPOSITE_DIRECTION = {
    DIRECTION_UP: DIRECTION_DOWN,
    DIRECTION_DOWN: DIRECTION_UP,
    DIRECTION_ROW: DIRECTION_COL,
    DIRECTION_COL: DIRECTION_ROW,

    DIRECTION_WEST: DIRECTION_EAST,
    DIRECTION_EAST: DIRECTION_WEST,
    DIRECTION_SOUTH: DIRECTION_NORTH,
    DIRECTION_NORTH: DIRECTION_SOUTH,
    DIRECTION_NORTHWEST: DIRECTION_SOUTHEAST,
    DIRECTION_SOUTHEAST: DIRECTION_NORTHWEST,
    DIRECTION_SOUTHWEST: DIRECTION_NORTHEAST,
    DIRECTION_NORTHEAST: DIRECTION_SOUTHWEST,
}

LEG_INFO_IDX_DUP_SUM_SCORE = 13
LEG_INFO_IDX_SUM_SCORE = 14
LEG_INFO_N = 15

assert (BOARD_MARKS_LENGTH > WIDTH)
assert (BOARD_MARKS_LENGTH > HEIGHT)

g_debug_info = False

def idtoa(point_w):
    if point_w < 0 or point_w > BOARD_MARKS_LENGTH:
        return BOARD_MARKS[0]
    return BOARD_MARKS[point_w]


def atoid(mark_w):
    return BOARD_MARKS.find(str(mark_w))


def get_label_of_point(point_h, point_w):
    return "%s%d" % (idtoa(point_w), point_h+1)


def chess_log(msg, level="INFO"):
    if level == "DEBUG" and not g_debug_info:
        return
    print >> sys.stderr, msg


def chess_operate(op):
    chess_log(op)
    print op


class Bot():

    def init_data(self):
        self.my_side = WHITE_ID
        self.your_side = BLACK_ID
        self.side_this_turn = self.your_side
        self.board = [ [[BLANK_ID, [1] * LEG_INFO_N, [1] * LEG_INFO_N]
                        for w in range(WIDTH)]
                       for h in range(HEIGHT)]

        self.board_blank_count = [ [[BLANK_ID,
                                     [[1, 1, 1, 1] for i in range(LEG_INFO_N)],
                                     [[1, 1, 1, 1] for i in range(LEG_INFO_N)],]
                                    for w in range(WIDTH)]
                                   for h in range(HEIGHT)]
        self.notes = []


    def __init__(self):
        self.started = False
        self.init_data()
        self.board_separate_line = "- " * WIDTH
        chess_log("init blank score.", level="DEBUG")
        self.get_score_of_blanks_for_side(BLACK_ID)
        self.get_score_of_blanks_for_side(WHITE_ID)
        chess_log("init ok.", level="DEBUG")


    def notes_dumps(self):
        chess_log("Notes[%d]: %s" % (len(self.notes), ("".join(self.notes)).lower()))


    def board_dumps(self):
        print >> sys.stderr, "   " + self.board_separate_line

        for i in range(HEIGHT, 0, -1):
            print >> sys.stderr, ("%2d|" % i) + " ".join([ID_TO_NOTE[note_info[POINT_NOTE]]
                                                          for note_info in self.board[i-1]]) + "|"

        print >> sys.stderr, "   " + self.board_separate_line
        print >> sys.stderr, "   " + " ".join([idtoa(i) for i in range(WIDTH)])


    def board_debug_dumps(self):
        for h in range(HEIGHT):
            for w in range(WIDTH):
                if self.get_board_at_point((h, w)) != BLANK_ID:
                    continue
                chess_log("%s: %s, BLACK: %s" % (
                    get_label_of_point(h, w),
                    ID_TO_NOTE[self.board[h][w][POINT_NOTE]],
                    self.board[h][w][BLACK_ID]
                    ), level="DEBUG")
                chess_log("%s: %s, WHITE: %s" % (
                    get_label_of_point(h, w),
                    ID_TO_NOTE[self.board[h][w][POINT_NOTE]],
                    self.board[h][w][WHITE_ID]
                    ), level="DEBUG")


    def board_loads(self, board_block):
        board_block_lines = board_block.split("\n")
        if len(board_block_lines) < HEIGHT + 5:
            chess_log("error in board_loads: not enough lines.")
            return False
        board_block_lines.reverse()

        self.init_data()
        chess_log("load board start.", level="DEBUG")

        count_balance = 0
        for height, line_side_notes in enumerate(board_block_lines[3:-2]):
            height_label, side_notes, _ = line_side_notes.split("|")
            for i in range(WIDTH):
                note = side_notes[i*2]
                if note in [BLACK, WHITE, BLANK]:
                    self.set_board_at_point((height, i), NOTE_TO_ID[note])
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

        self.get_score_of_blanks_for_side(BLACK_ID)
        self.get_score_of_blanks_for_side(WHITE_ID)
        chess_log("load board ok.", level="DEBUG")
        return True


    def light_on_win_points(self):
        for pt in self.win_points:
            test_side = self.get_board_at_point(pt)
            test_side_win = MARK_WIN[test_side]
            self.set_board_at_point(pt, test_side_win)


    def can_put_at_point(self, point_h, point_w):
        if point_h < 0 or point_h >= HEIGHT:
            chess_log("point_h(%d) out of range." % point_h, level="DEBUG")
            return False
        if point_w < 0 or point_w >= WIDTH:
            chess_log("point_w(%d) out of range." % point_w, level="DEBUG")
            return False
        if self.get_board_at_point((point_h, point_w)) != BLANK_ID:
            chess_log("put twice. (%s)" % get_label_of_point(point_h, point_w), level="DEBUG")
            return False
        return True


    def swap_user_side(self):
        self.my_side, self.your_side = self.your_side, self.my_side


    def swap_turn_side(self):
        if self.side_this_turn == self.my_side:
            self.side_this_turn = self.your_side
        else:
            self.side_this_turn = self.my_side


    def get_board_at_point(self, pt):
        return self.board[pt[0]][pt[1]][POINT_NOTE]


    def set_board_at_point(self, pt, side_note):
        self.board[pt[0]][pt[1]][POINT_NOTE] = side_note


    def put_chessman_at_point(self, put_side, point_h, point_w):
        if self.side_this_turn != put_side:
            chess_log("not %s turn." % ID_TO_NOTE[put_side], level="DEBUG")
            return False

        if self.can_put_at_point(point_h, point_w):
            self.set_board_at_point((point_h, point_w), self.side_this_turn)
            self.update_put_around_point(point_h, point_w)
            operate = "%s %s %s" % (OP_PUT, get_label_of_point(point_h, point_w), ID_TO_NOTE[self.side_this_turn])
            chess_operate(operate)
            self.notes += [get_label_of_point(point_h, point_w)]
            self.swap_turn_side()
            return True

        return False


    def get_point_of_chessman(self, get_side):
        if self.side_this_turn != get_side:
            chess_log("not %s turn." % ID_TO_NOTE[get_side], level="DEBUG")
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
            self.set_board_at_point((point_h, point_w), self.side_this_turn)
            self.update_put_around_point(point_h, point_w)
            self.notes += [get_label_of_point(point_h, point_w)]
            self.swap_turn_side()
            return point_h, point_w

        return None, None


    def detect_positions_around_point(self, point_h, point_w, test_side=None):
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
        self.center_side = self.get_board_at_point((h, w))
        if test_side is None:
            self.test_side = self.center_side
        else:
            self.test_side = test_side

        # test row (-)
        self.callback_begin(DIRECTION_ROW)
        for k in range(min(WIN_NUM-1, w)):
            pt = (h, w-k-1)
            if self.callback_count(k, pt, DIRECTION_ROW, DIRECTION_WEST):
                break
        for k in range(min(WIN_NUM-1, WIDTH-w-1)):
            pt = (h, w+k+1)
            if self.callback_count(k, pt, DIRECTION_ROW, DIRECTION_EAST):
                break
        if self.callback_end(DIRECTION_ROW):
            return True

        # test col (|)
        self.callback_begin(DIRECTION_COL)
        for k in range(min(WIN_NUM-1, h)):
            pt = (h-k-1, w)
            if self.callback_count(k, pt, DIRECTION_COL, DIRECTION_SOUTH):
                break
        for k in range(min(WIN_NUM-1, WIDTH-h-1)):
            pt = (h+k+1, w)
            if self.callback_count(k, pt, DIRECTION_COL, DIRECTION_NORTH):
                break
        if self.callback_end(DIRECTION_COL):
            return True

        # test down (\)
        self.callback_begin(DIRECTION_DOWN)
        for k in range(min(WIN_NUM-1, HEIGHT-h-1, w)):
            pt = (h+k+1, w-k-1)
            if self.callback_count(k, pt, DIRECTION_DOWN, DIRECTION_NORTHWEST):
                break
        for k in range(min(WIN_NUM-1, h, WIDTH-w-1)):
            pt = (h-k-1, w+k+1)
            if self.callback_count(k, pt, DIRECTION_DOWN, DIRECTION_SOUTHEAST):
                break
        if self.callback_end(DIRECTION_DOWN):
            return True

        # test up (/)
        self.callback_begin(DIRECTION_UP)
        for k in range(min(WIN_NUM-1, h, w)):
            pt = (h-k-1, w-k-1)
            if self.callback_count(k, pt, DIRECTION_UP, DIRECTION_SOUTHWEST):
                break
        for k in range(min(WIN_NUM-1, HEIGHT-h-1, WIDTH-w-1)):
            pt = (h+k+1, w+k+1)
            if self.callback_count(k, pt, DIRECTION_UP, DIRECTION_NORTHEAST):
                break
        if self.callback_end(DIRECTION_UP):
            return True

        return False


    def callback_begin_winner(self, where):
        self.win_points = [self.center_point]
    def callback_count_winner(self, k, pt, where, part):
        if self.get_board_at_point(pt) != self.test_side:
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
                if self.get_board_at_point((h, w)) != test_side:
                    continue
                if self.detect_positions_around_point(h, w):
                    return True
        return False


    def win_test(self, pt, test_side):
        self.callback_count = self.callback_count_winner
        self.callback_end = self.callback_end_winner
        self.callback_begin = self.callback_begin_winner

        (point_h, point_w) = pt
        self.set_board_at_point((point_h, point_w), test_side)
        if self.detect_positions_around_point(point_h, point_w):
            self.set_board_at_point((point_h, point_w), BLANK_ID)
            return True

        self.set_board_at_point((point_h, point_w), BLANK_ID)
        return False


    def callback_begin_legtype(self, where):
        # 空点汇合计数
        return
    def callback_count_legtype(self, k, pt, where, part):
        k_type = 1<<k
        legtype = self.direction_legtype_count[part]
        legtype += k_type

        h, w = self.center_point
        if self.get_board_at_point(pt) == -self.test_side:
            return True

        if self.get_board_at_point(pt) != BLANK_ID:
            legtype += k_type
        self.direction_legtype_count[part] = legtype
        return False
    def callback_end_legtype(self, where):
        return False


    def callback_begin_update_blank_score_after_put(self, where):
        # 放子更新
        return
    def callback_count_update_blank_score_after_put(self, k, pt, where, part):
        if self.get_board_at_point(pt) != BLANK_ID:
            return False

        h, w = pt
        opposite_part = OPPOSITE_DIRECTION[part]

        self.board_blank_count[h][w][BLACK_ID][opposite_part][k] = self.board[h][w][BLACK_ID][opposite_part]
        self.board_blank_count[h][w][WHITE_ID][opposite_part][k] = self.board[h][w][WHITE_ID][opposite_part]

        k_type = 1<<k
        temp_c = self.board[h][w][self.test_side][opposite_part]
        if temp_c > k_type:
            temp_c += k_type
            self.board[h][w][self.test_side][opposite_part] = temp_c
        temp_c = self.board[h][w][-self.test_side][opposite_part]
        if temp_c > k_type:
            temp_c &= (k_type-1)
            temp_c += k_type
            self.board[h][w][-self.test_side][opposite_part] = temp_c
        self.update_total_score(h, w, BLACK_ID)
        self.update_total_score(h, w, WHITE_ID)
        return False
    def callback_end_update_blank_score_after_put(self, where):
        return False


    def update_total_score(self, h, w, test_side):
        total_score = 0
        total_dup_score = 0
        LEG_TYPE_TO_COUNT = [0, 0, 0, 1,
                             0, 1, 1, 2,
                             0, 1, 1, 2,
                             1, 2, 2, 3,
                             0, 1, 1, 2,
                             1, 2, 2, 3,
                             1, 2, 2, 3,
                             2, 2, 3, 4,]
        LEG_TYPE_TO_SPACE = [0, 0, 1, 1,
                             2, 2, 2, 2,
                             3, 3, 3, 3,
                             3, 3, 3, 3,
                             4, 4, 4, 4,
                             4, 4, 4, 4,
                             4, 4, 4, 4,
                             4, 4, 4, 4,]
        LEG_TYPE_TO_ADDITION_COUNT = [0, 0, 0, 0,
                                      0, 0, 0, 2,
                                      0, 0, 0, 2,
                                      0, 0, 0, 3,
                                      0, 0, 0, 2,
                                      0, 0, 0, 3,
                                      0, 0, 0, 2,
                                      0, 0, 0, 4,]
        LEG_TYPE_TO_DOUBLE_ADDITION_COUNT = [0, 0, 0, 1,
                                          0, 1, 0, 2,
                                          0, 1, 0, 2,
                                          0, 1, 0, 3,
                                          0, 1, 0, 2,
                                          0, 1, 0, 3,
                                          0, 1, 0, 2,
                                          0, 1, 0, 4,]

        dir_types = self.board[h][w][test_side][:-3]
        for direction, t in enumerate(dir_types):
            opposite_dir = OPPOSITE_DIRECTION[direction]
            opposite_t = dir_types[opposite_dir]
            # test space
            t_score = LEG_TYPE_TO_SPACE[t]
            opposite_t_score = LEG_TYPE_TO_SPACE[opposite_t]
            if t_score + opposite_t_score < WIN_NUM-1:
                continue
            # base score
            total_score += LEG_TYPE_TO_COUNT[t]
            total_dup_score += LEG_TYPE_TO_ADDITION_COUNT[t]

            # addition score
            t_score = LEG_TYPE_TO_DOUBLE_ADDITION_COUNT[t]
            opposite_t_score = LEG_TYPE_TO_DOUBLE_ADDITION_COUNT[opposite_t]
            if t_score > 0 and opposite_t_score > 0:
                total_dup_score += t_score

        self.board[h][w][test_side][LEG_INFO_IDX_DUP_SUM_SCORE] = total_score + total_dup_score
        self.board[h][w][test_side][LEG_INFO_IDX_SUM_SCORE] = total_score


    def callback_begin_update_blank_score_after_remove(self, where):
        # 放子更新
        return
    def callback_count_update_blank_score_after_remove(self, k, pt, where, part):
        if self.get_board_at_point(pt) != BLANK_ID:
            return False
        h, w = pt
        opposite_part = OPPOSITE_DIRECTION[part]
        self.board[h][w][BLACK_ID][opposite_part] = self.board_blank_count[h][w][BLACK_ID][opposite_part][k]
        self.board[h][w][WHITE_ID][opposite_part] = self.board_blank_count[h][w][WHITE_ID][opposite_part][k]
        self.update_total_score(h, w, BLACK_ID)
        self.update_total_score(h, w, WHITE_ID)
        return False
    def callback_end_update_blank_score_after_remove(self, where):
        return False


    def update_remove_around_point(self, point_h, point_w):
        self.callback_count = self.callback_count_update_blank_score_after_remove
        self.callback_end = self.callback_end_update_blank_score_after_remove
        self.callback_begin = self.callback_begin_update_blank_score_after_remove
        self.detect_positions_around_point(point_h, point_w)


    def update_put_around_point(self, point_h, point_w):
        self.callback_count = self.callback_count_update_blank_score_after_put
        self.callback_end = self.callback_end_update_blank_score_after_put
        self.callback_begin = self.callback_begin_update_blank_score_after_put
        self.detect_positions_around_point(point_h, point_w)


    def get_score_of_blanks_for_side(self, test_side, is_dup_enforce=False):
        # test_side的每一个棋子, 对它米子型中心WIN_NUM范围的空白的位置贡献记分
        # 返回所有的空白位置坐标和对应的累计记分, pair

        # 获取所有在棋盘中test_side棋子的位置坐标
        all_my_blank_points_count = {}
        for h in range(HEIGHT):
            for w in range(WIDTH):
                if self.get_board_at_point((h, w)) != BLANK_ID:
                    continue

                self.direction_legtype_count = self.board[h][w][test_side]

                chess_log("%s GET SCORE[%s]: %s" % (ID_TO_NOTE[test_side], get_label_of_point(h, w),
                                                    self.direction_legtype_count), level="DEBUG")

                if self.direction_legtype_count[POINT_NEED_UPDATE] == 1:
                    for i in range(LEG_INFO_N):
                        self.direction_legtype_count[i] = 1
                    self.direction_legtype_count[POINT_NEED_UPDATE] = 0

                    self.callback_count = self.callback_count_legtype
                    self.callback_end = self.callback_end_legtype
                    self.callback_begin = self.callback_begin_legtype
                    self.detect_positions_around_point(h, w, test_side)

                    self.update_total_score(h, w, test_side)
                    chess_log("%s UPDATE SCORE[%s]: %s" % (ID_TO_NOTE[test_side], get_label_of_point(h, w),
                                                           self.direction_legtype_count), level="DEBUG")

                if is_dup_enforce:
                    blank_score = self.direction_legtype_count[LEG_INFO_IDX_DUP_SUM_SCORE]
                else:
                    blank_score = self.direction_legtype_count[LEG_INFO_IDX_SUM_SCORE]
                if blank_score:
                    all_my_blank_points_count[(h, w)] = blank_score

        if not all_my_blank_points_count:
            return []

        # 返回所有的空白位置坐标和对应的记分数 pair
        all_my_blank_points_count_pair = all_my_blank_points_count.items()
        all_my_blank_points_count_pair.sort(key=lambda x:x[1])
        all_my_blank_points_count_pair.reverse()

        chess_log("%s Score: %s" % (
            ID_TO_NOTE[test_side],
            ", ".join(["%s:%d" % (get_label_of_point(h, w), count)
                       for (h, w), count in all_my_blank_points_count_pair if count >= 0])), level="DEBUG")
        return all_my_blank_points_count_pair


    def is_a_good_choice(self, choice_pt, my_side, your_side, max_level=-1):
        # todo: 层序遍历, 最高得分先检查
        if max_level == 0:
            return False

        (point_h, point_w) = choice_pt
        self.set_board_at_point((point_h, point_w), my_side)
        self.update_put_around_point(point_h, point_w)
        chess_log("%s TEST GOOD CHOICE[%d]: %s" % (ID_TO_NOTE[my_side], max_level,
                                                  get_label_of_point(point_h, point_w)), level="DEBUG")

        is_dup_enforce = True
        all_my_blank_points_count_pair = self.get_score_of_blanks_for_side(my_side,
                                                                           is_dup_enforce=is_dup_enforce)

        count_win_point = 0
        for my_pt, count in all_my_blank_points_count_pair:
            # 先扫一遍有没有多处直接胜利的, count<4的点不可能胜利
            if count < 4: continue
            if self.win_test(my_pt, my_side):
                count_win_point += 1
                if count_win_point > 1:
                    self.update_remove_around_point(point_h, point_w)
                    self.set_board_at_point((point_h, point_w), BLANK_ID)
                    return True

        tested_not_good_pt = []
        for my_pt, count in all_my_blank_points_count_pair:
            tested_not_good_pt += [my_pt]
            if not self.is_a_bad_choice(my_pt, your_side, my_side, max_level=max_level):
                self.update_remove_around_point(point_h, point_w)
                self.set_board_at_point((point_h, point_w), BLANK_ID)
                return False

        is_dup_enforce = True
        all_your_blank_points_count_pair = self.get_score_of_blanks_for_side(your_side,
                                                                         is_dup_enforce=is_dup_enforce)
        for your_pt, count in all_your_blank_points_count_pair:
            if your_pt in tested_not_good_pt: continue
            if not self.is_a_bad_choice(your_pt, your_side, my_side, max_level=max_level):
                chess_log("%s GET BAD CHOICE[%d]: %s" % (
                    ID_TO_NOTE[your_side], max_level-1,
                    get_label_of_point(your_pt[0], your_pt[1])), level="DEBUG")

                self.update_remove_around_point(point_h, point_w)
                self.set_board_at_point((point_h, point_w), BLANK_ID)
                return False

        self.update_remove_around_point(point_h, point_w)
        self.set_board_at_point((point_h, point_w), BLANK_ID)
        return True


    def is_a_bad_choice(self, choice_pt, my_side, your_side, max_level=-1):
        # todo: 层序遍历, 最高得分先检查
        if max_level == 0:
            return False

        (point_h, point_w) = choice_pt
        self.set_board_at_point((point_h, point_w), my_side)
        self.update_put_around_point(point_h, point_w)
        chess_log("%s TEST BAD CHOICE[%d]: %s" % (ID_TO_NOTE[my_side], max_level,
                                                  get_label_of_point(point_h, point_w)), level="DEBUG")

        is_dup_enforce = True
        all_your_blank_points_count_pair = self.get_score_of_blanks_for_side(your_side,
                                                                             is_dup_enforce=is_dup_enforce)
        for your_pt, count in all_your_blank_points_count_pair:
            # 先扫一遍有没有直接胜利的, count<4的点不可能胜利
            if count >= 4:
                if self.win_test(your_pt, your_side):
                    self.update_remove_around_point(point_h, point_w)
                    self.set_board_at_point((point_h, point_w), BLANK_ID)
                    return True

        for your_pt, count in all_your_blank_points_count_pair:
            if count > 2:
                # tofix: 不应该忽视count==1的点, 但为了减少计算
                if self.is_a_good_choice(your_pt, your_side, my_side, max_level=max_level-1):
                    chess_log("%s GET GOOD CHOICE[%d]: %s" % (
                        ID_TO_NOTE[your_side], max_level-1,
                        get_label_of_point(your_pt[0], your_pt[1])), level="DEBUG")

                    self.update_remove_around_point(point_h, point_w)
                    self.set_board_at_point((point_h, point_w), BLANK_ID)
                    return True

        is_dup_enforce = True
        all_my_blank_points_count_pair = self.get_score_of_blanks_for_side(my_side,
                                                                           is_dup_enforce=is_dup_enforce)
        for my_pt, count in all_my_blank_points_count_pair:
            if count > 2:
                # tofix: 不应该忽视count==1的点, 但为了减少计算
                if self.is_a_good_choice(my_pt, your_side, my_side, max_level=max_level-1):
                    chess_log("%s GET GOOD CHOICE[%d]: %s" % (
                        ID_TO_NOTE[your_side], max_level-1,
                        get_label_of_point(your_pt[0], your_pt[1])), level="DEBUG")

                    self.update_remove_around_point(point_h, point_w)
                    self.set_board_at_point((point_h, point_w), BLANK_ID)
                    return True

        self.update_remove_around_point(point_h, point_w)
        self.set_board_at_point((point_h, point_w), BLANK_ID)
        return False
