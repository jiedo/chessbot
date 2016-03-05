#!/usr/bin/env python
#encoding: utf-8

import sys
import time
import random
import chess


def main():
    # main 默认实现成回调strategy()模式,
    # 但可以实现成更复杂模式, 符合bot通信协议即可
    sleep_time = 1
    show_verbose = False
    chess.g_debug_info = False
    if len(sys.argv) >= 2:
        if "-w" in sys.argv:
            #如果选择白方, 则通知对方START.
            chess.chess_operate("START")

        if "-v" in sys.argv:
            show_verbose = True

        if "-d" in sys.argv:
            chess.g_debug_info = True


    bot = chess.Bot()
    while True:
        # 首先读取对方的落子位置, 并写入棋盘
        while bot.b_next == bot.b_your_side:
            h, w = bot.chess_get()

        # if show_verbose:
        #     time.sleep(sleep_time/10)
        #     bot.show_board()
        #     time.sleep(sleep_time)

        # 检测对方是否获胜
        if bot.is_winner(bot.b_your_side):
            bot.light_on_win_points()
            chess.chess_log("Notes: %d" % (len(bot.notes)))
            time.sleep(0.1)
            bot.show_board()
            break

        # 回调自己的策略
        h, w = strategy(bot)
        # 写入棋盘并通知对方
        bot.chess_put(h, w)
        if show_verbose:
            time.sleep(sleep_time/10)
            bot.show_board()
            time.sleep(sleep_time)

        # 检测自己是否获胜
        if bot.is_winner(bot.b_my_side):
            chess.chess_log("%s Win." % bot.b_my_side)
            break


def strategy(self):
    # 测试AI
    if self.b_my_side == chess.BLACK:
        return strategy3(self)
    else:
        return strategy0(self)


def strategy0(self):
    # 测试AI
    # 同下， 连珠对附近空白有加分
    all_my_blank_points_count_pair = self.get_score_of_blanks_side(self.b_your_side, dup=True)
    if all_my_blank_points_count_pair:
        pt, count = all_my_blank_points_count_pair[0]
        if count >= 3:
            return pt

    all_my_blank_points_count_pair = self.get_score_of_blanks_side(self.b_my_side, dup=True)
    if not all_my_blank_points_count_pair:
        random_point = (random.randint(0, chess.HEIGHT-1), random.randint(0, chess.WIDTH-1))
        chess.chess_log("random_points: %s" % str(random_point), level="DEBUG")
        return random_point
    return all_my_blank_points_count_pair[0][0]

    
def strategy1(self):
    # 测试AI
    # 在对方所有棋子米字形线条交汇计数最多的空白处，计数超过3个时，进行防守放置
    # 否则，在己方所有棋子米字形线条交汇计数最多的空白处放置
    all_my_blank_points_count_pair = self.get_score_of_blanks_side(self.b_your_side)
    if all_my_blank_points_count_pair:
        pt, count = all_my_blank_points_count_pair[0]
        if count >= 3:
            return pt

    all_my_blank_points_count_pair = self.get_score_of_blanks_side(self.b_my_side)
    if not all_my_blank_points_count_pair:
        random_point = (random.randint(0, chess.HEIGHT-1), random.randint(0, chess.WIDTH-1))
        chess.chess_log("random_points: %s" % str(random_point), level="DEBUG")
        return random_point
    return all_my_blank_points_count_pair[0][0]


def strategy2(self):
    # 测试AI
    # 在己方所有棋子米字形线条交汇计数最多的空白处放置
    all_my_blank_points_count_pair = self.get_score_of_blanks_side(self.b_my_side)
    if not all_my_blank_points_count_pair:
        random_point = (random.randint(0, chess.HEIGHT-1), random.randint(0, chess.WIDTH-1))
        chess.chess_log("random_points: %s" % str(random_point), level="DEBUG")
        return random_point
    return all_my_blank_points_count_pair[0][0]


def strategy3(self):
    # 测试AI
    # 在随机一个己方棋子米字形线条内随机放置
    random_point = (random.randint(0, chess.HEIGHT-1), random.randint(0, chess.WIDTH-1))
    all_my_points = [random_point]
    for h in range(chess.HEIGHT):
        for w in range(chess.WIDTH):
            if self.board[h][w] != self.b_my_side:
                continue
            all_my_points += [(h, w)]

    point_h, point_w = random.choice(all_my_points)
    point_h += random.randint(-chess.WIN_NUM, chess.WIN_NUM)
    point_w += random.randint(-chess.WIN_NUM, chess.WIN_NUM)
    return point_h, point_w


def strategy9(self):
    # 测试AI
    # 纯逆序
    for i in range(chess.HEIGHT):
        for j in range(chess.WIDTH):
            if self.board[chess.HEIGHT-i-1][chess.WIDTH-j-1] == chess.BLANK:
                return chess.HEIGHT-i-1, chess.WIDTH-j-1


def strategy10(self):
    # 测试AI
    # 纯随机
    return random.randint(0, chess.HEIGHT-1), random.randint(0, chess.WIDTH-1)



if __name__ == "__main__":
    main()
