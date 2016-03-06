#!/usr/bin/env python
#encoding: utf-8

import sys
import time
import random
import chess


def main():
    # 默认实现成回调strategy()模式,
    # 但可以实现成更复杂模式, 符合bot通信协议即可
    sleep_time = 0.1
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
        return strategy4(self, 0, True, True)
    else:
        return strategy40(self, 0, True, True)



def strategy40(self, defence_level, is_dup_enforce, is_space_enough):
    # 测试AI
    # 同4, 检测一步胜利
    #
    # is_dup_enforce: 连珠对附近空白是否有加分
    # is_space_enough: 是否检查空白处扩展空间足够WIN_NUM
    # defence_level: 防御权重, 越大越重视防御
    #
    # 统计双方所有棋子米字形线条交汇计数最高的空白
    # max(points_score) = max(max(your's + defence),  max(mine))
    #
    all_my_blank_points_count_pair = self.get_score_of_blanks_side(self.b_my_side,
                                                                   dup=is_dup_enforce,
                                                                   test_space=is_space_enough)
    for pt, count in all_my_blank_points_count_pair:
        if count < 8:
            if self.win_test(pt, self.b_my_side):
                return pt

    all_your_blank_points_count_pair = self.get_score_of_blanks_side(self.b_your_side,
                                                                   dup=is_dup_enforce,
                                                                   test_space=is_space_enough)
    for pt, count in all_your_blank_points_count_pair:
        if count < 8:
            if self.win_test(pt, self.b_your_side):
                return pt

    if not all_your_blank_points_count_pair:
        if not all_my_blank_points_count_pair:
            return (chess.HEIGHT/2, chess.WIDTH/2)
    else:
        your_pt, your_max_count = all_your_blank_points_count_pair[0]
        if all_my_blank_points_count_pair:
            my_pt, my_max_count = all_my_blank_points_count_pair[0]
            if defence_level + your_max_count <= my_max_count:
                candidates = [pt for pt, count in all_my_blank_points_count_pair if count == my_max_count]
                return random.choice(candidates)

        candidates = [pt for pt, count in all_your_blank_points_count_pair if count == your_max_count]
        return random.choice(candidates)




def strategy5(self, defence_level, is_dup_enforce, is_space_enough):
    # 测试AI
    # is_dup_enforce: 连珠对附近空白是否有加分
    # is_space_enough: 是否检查空白处扩展空间足够WIN_NUM
    # defence_level: 防御权重, 越大越重视防御
    #
    # 统计双方所有棋子米字形线条交汇计数最高的空白(ME, YOU)
    # max(points_score) = max((your's + defence) JOIN (mine))
    #
    all_my_blank_points_count_pair = self.get_score_of_blanks_side(self.b_my_side,
                                                                   dup=is_dup_enforce,
                                                                   test_space=is_space_enough)
    all_your_blank_points_count_pair = self.get_score_of_blanks_side(self.b_your_side,
                                                                   dup=is_dup_enforce,
                                                                   test_space=is_space_enough)

    all_blank_points_count = {}
    for pt, count in all_your_blank_points_count_pair:
        all_blank_points_count[pt] = count + defence_level

    for pt, count in all_my_blank_points_count_pair:
        all_blank_points_count[pt] = all_blank_points_count.get(pt, 0) + count

    all_blank_points_count_pair = all_blank_points_count.items()
    all_blank_points_count_pair.sort(key=lambda x:x[1])
    all_blank_points_count_pair.reverse()

    if not all_blank_points_count_pair:
        return (chess.HEIGHT/2, chess.WIDTH/2)
    else:
        pt = all_blank_points_count_pair[0][0]
        return pt



def strategy4(self, defence_level, is_dup_enforce, is_space_enough):
    # 测试AI
    # is_dup_enforce: 连珠对附近空白是否有加分
    # is_space_enough: 是否检查空白处扩展空间足够WIN_NUM
    # defence_level: 防御权重, 越大越重视防御
    #
    # 统计双方所有棋子米字形线条交汇计数最高的空白
    # max(points_score) = max(max(your's + defence),  max(mine))
    all_my_blank_points_count_pair = self.get_score_of_blanks_side(self.b_my_side,
                                                                   dup=is_dup_enforce,
                                                                   test_space=is_space_enough)
    all_your_blank_points_count_pair = self.get_score_of_blanks_side(self.b_your_side,
                                                                   dup=is_dup_enforce,
                                                                   test_space=is_space_enough)
    if not all_your_blank_points_count_pair:
        if not all_my_blank_points_count_pair:
            return (chess.HEIGHT/2, chess.WIDTH/2)
    else:
        your_pt, your_max_count = all_your_blank_points_count_pair[0]
        if all_my_blank_points_count_pair:
            my_pt, my_max_count = all_my_blank_points_count_pair[0]
            if defence_level + your_max_count <= my_max_count:
                candidates = [pt for pt, count in all_my_blank_points_count_pair if count == my_max_count]
                return random.choice(candidates)

        candidates = [pt for pt, count in all_your_blank_points_count_pair if count == your_max_count]
        return random.choice(candidates)



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
    point_h += random.randint(-chess.WIN_NUM+1, chess.WIN_NUM-1)
    point_w += random.randint(-chess.WIN_NUM+1, chess.WIN_NUM-1)
    return point_h, point_w


def strategy2(self):
    # 测试AI
    # 纯逆序
    for h in range(chess.HEIGHT):
        for w in range(chess.WIDTH):
            if self.board[chess.HEIGHT-h-1][chess.WIDTH-w-1] == chess.BLANK:
                return chess.HEIGHT-h-1, chess.WIDTH-w-1


def strategy1(self):
    # 测试AI
    # 纯顺序
    for h in range(chess.HEIGHT):
        for w in range(chess.WIDTH):
            if self.board[h][w] == chess.BLANK:
                return h, w


def strategy0(self):
    # 测试AI
    # 纯随机
    return random.randint(0, chess.HEIGHT-1), random.randint(0, chess.WIDTH-1)



if __name__ == "__main__":
    main()
