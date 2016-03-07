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
        while bot.side_this_turn == bot.your_side:
            h, w = bot.get_point_of_your_chessman()

        # 检测对方是否获胜
        if bot.is_winner(bot.your_side):
            bot.light_on_win_points()
            chess.chess_log("Notes: %d" % (len(bot.notes)))
            time.sleep(0.1)
            bot.show_board()
            break

        # 回调自己的策略
        h, w = strategy(bot)
        # 写入棋盘并通知对方
        bot.put_my_chessman_at_point(h, w)
        if show_verbose:
            time.sleep(sleep_time/10)
            bot.show_board()
            time.sleep(sleep_time)

        # 检测自己是否获胜
        if bot.is_winner(bot.my_side):
            chess.chess_log("%s Win." % bot.my_side)
            break


def strategy(self):
    # 测试AI
    if self.my_side == chess.BLACK:
        return strategy6(self, 0, True,
                         max_level_good = 1,
                         max_level_bad = 2)
        #return strategy4(self, 0, True)
    else:
        #return strategy4(self, 0, True)
        return strategy6(self, 0, True,
                         max_level_good = 1,
                         max_level_bad = 1)


def strategy6(self, defence_level, is_dup_enforce,
              max_level_good = 1,
              max_level_bad = 2):
    # 测试AI
    # 同4,
    # 搜索max_level_good步必胜, 和避免max_level_bad步必败
    # 搜索更多步比较耗时
    #
    # is_dup_enforce: 连珠对附近空白是否有加分
    # defence_level: 防御权重, 越大越重视防御
    #
    # 统计双方所有棋子米字形线条交汇计数最高的空白
    # max(points_score) = max(max(your's + defence),  max(mine))
    #
    all_my_blank_points_count_pair = self.get_score_of_blanks_for_side(self.my_side,
                                                                   dup=is_dup_enforce)
    for pt, count in all_my_blank_points_count_pair:
        if count > 7:
            if self.win_test(pt, self.my_side):
                return pt

    all_your_blank_points_count_pair = self.get_score_of_blanks_for_side(self.your_side,
                                                                   dup=is_dup_enforce)
    for pt, count in all_your_blank_points_count_pair:
        if count > 7:
            if self.win_test(pt, self.your_side):
                return pt

    tested_not_good_pt = []
    # make a better choice
    for pt, count in all_my_blank_points_count_pair:
        tested_not_good_pt += [pt]
        if self.is_a_good_choice(pt, self.my_side, self.your_side, max_level=max_level_good):
            chess.chess_log("%s GOOD: %s" % (self.my_side,  chess.get_notename_of_point(pt[0], pt[1])),
                            level="DEBUG")
            return pt
    for pt, count in all_your_blank_points_count_pair:
        if pt in tested_not_good_pt: continue
        if self.is_a_good_choice(pt, self.my_side, self.your_side, max_level=max_level_good):
            chess.chess_log("%s GOOD: %s" % (self.my_side,  chess.get_notename_of_point(pt[0], pt[1])),
                            level="DEBUG")
            return pt

    tested_bad_pt = []
    # don't make a bad choice
    for pt, count in all_my_blank_points_count_pair:
        if count > 2:
            if self.is_a_bad_choice(pt, self.my_side, self.your_side, max_level=max_level_bad):
                chess.chess_log("%s BAD : %s" % (self.my_side,  chess.get_notename_of_point(pt[0], pt[1])),
                                level="DEBUG")
                tested_bad_pt += [pt]
    for pt, count in all_your_blank_points_count_pair:
        if count > 2:
            if self.is_a_bad_choice(pt, self.my_side, self.your_side, max_level=max_level_bad):
                chess.chess_log("%s BAD : %s" % (self.my_side,  chess.get_notename_of_point(pt[0], pt[1])),
                                level="DEBUG")
                tested_bad_pt += [pt]

    all_blank_points_count = {}
    for pt, count in all_your_blank_points_count_pair:
        if pt in tested_bad_pt: continue
        all_blank_points_count[pt] = count + defence_level
    for pt, count in all_my_blank_points_count_pair:
        if pt in tested_bad_pt: continue
        all_blank_points_count[pt] = all_blank_points_count.get(pt, 0) + count

    all_blank_points_count_pair = all_blank_points_count.items()
    all_blank_points_count_pair.sort(key=lambda x:x[1])
    all_blank_points_count_pair.reverse()

    if all_blank_points_count_pair:
        _, max_count = all_blank_points_count_pair[0]
        candidates = [pt for pt, count in all_blank_points_count_pair if count == max_count]
        pt = random.choice(candidates)
        chess.chess_log("%s No.6 give: %s" % (self.my_side,  chess.get_notename_of_point(pt[0], pt[1])),
                        level="DEBUG")
        return pt

    # all choices are not good
    if all_your_blank_points_count_pair:
        your_pt, your_max_count = all_your_blank_points_count_pair[0]
        if all_my_blank_points_count_pair:
            my_pt, my_max_count = all_my_blank_points_count_pair[0]
            if defence_level + your_max_count <= my_max_count:
                candidates = [pt for pt, count in all_my_blank_points_count_pair if count == my_max_count]
                return random.choice(candidates)

        candidates = [pt for pt, count in all_your_blank_points_count_pair if count == your_max_count]
        return random.choice(candidates)

    return (chess.HEIGHT/2, chess.WIDTH/2)


def strategy40(self, defence_level, is_dup_enforce):
    # 测试AI
    # 同4, 检测一步胜利
    #
    # is_dup_enforce: 连珠对附近空白是否有加分
    # defence_level: 防御权重, 越大越重视防御
    #
    # 统计双方所有棋子米字形线条交汇计数最高的空白
    # max(points_score) = max(max(your's + defence),  max(mine))
    #
    all_my_blank_points_count_pair = self.get_score_of_blanks_for_side(self.my_side,
                                                                   dup=is_dup_enforce)
    for pt, count in all_my_blank_points_count_pair:
        if count > 7:
            if self.win_test(pt, self.my_side):
                return pt

    all_your_blank_points_count_pair = self.get_score_of_blanks_for_side(self.your_side,
                                                                   dup=is_dup_enforce)
    for pt, count in all_your_blank_points_count_pair:
        if count > 7:
            if self.win_test(pt, self.your_side):
                return pt

    if all_your_blank_points_count_pair:
        your_pt, your_max_count = all_your_blank_points_count_pair[0]
        if all_my_blank_points_count_pair:
            my_pt, my_max_count = all_my_blank_points_count_pair[0]
            if defence_level + your_max_count <= my_max_count:
                candidates = [pt for pt, count in all_my_blank_points_count_pair if count == my_max_count]
                return random.choice(candidates)

        candidates = [pt for pt, count in all_your_blank_points_count_pair if count == your_max_count]
        return random.choice(candidates)

    return (chess.HEIGHT/2, chess.WIDTH/2)


def strategy5(self, defence_level, is_dup_enforce):
    # 测试AI
    # is_dup_enforce: 连珠对附近空白是否有加分
    # defence_level: 防御权重, 越大越重视防御
    #
    # 统计双方所有棋子米字形线条交汇计数最高的空白(ME, YOU)
    # max(points_score) = max((your's + defence) JOIN (mine))
    #
    all_my_blank_points_count_pair = self.get_score_of_blanks_for_side(self.my_side,
                                                                   dup=is_dup_enforce)
    all_your_blank_points_count_pair = self.get_score_of_blanks_for_side(self.your_side,
                                                                   dup=is_dup_enforce)

    all_blank_points_count = {}
    for pt, count in all_your_blank_points_count_pair:
        all_blank_points_count[pt] = count + defence_level

    for pt, count in all_my_blank_points_count_pair:
        all_blank_points_count[pt] = all_blank_points_count.get(pt, 0) + count

    all_blank_points_count_pair = all_blank_points_count.items()
    all_blank_points_count_pair.sort(key=lambda x:x[1])
    all_blank_points_count_pair.reverse()

    if all_blank_points_count_pair:
        return all_blank_points_count_pair[0][0]
    return (chess.HEIGHT/2, chess.WIDTH/2)


def strategy4(self, defence_level, is_dup_enforce):
    # 测试AI
    # is_dup_enforce: 连珠对附近空白是否有加分
    # defence_level: 防御权重, 越大越重视防御
    #
    # 统计双方所有棋子米字形线条交汇计数最高的空白
    # max(points_score) = max(max(your's + defence),  max(mine))
    all_my_blank_points_count_pair = self.get_score_of_blanks_for_side(self.my_side,
                                                                   dup=is_dup_enforce)
    all_your_blank_points_count_pair = self.get_score_of_blanks_for_side(self.your_side,
                                                                   dup=is_dup_enforce)
    if all_your_blank_points_count_pair:
        your_pt, your_max_count = all_your_blank_points_count_pair[0]
        if all_my_blank_points_count_pair:
            my_pt, my_max_count = all_my_blank_points_count_pair[0]
            if defence_level + your_max_count <= my_max_count:
                candidates = [pt for pt, count in all_my_blank_points_count_pair if count == my_max_count]
                return random.choice(candidates)

        candidates = [pt for pt, count in all_your_blank_points_count_pair if count == your_max_count]
        return random.choice(candidates)

    return (chess.HEIGHT/2, chess.WIDTH/2)


def strategy3(self):
    # 测试AI
    # 在随机一个己方棋子米字形线条内随机放置
    random_point = (random.randint(0, chess.HEIGHT-1), random.randint(0, chess.WIDTH-1))
    all_my_points = [random_point]
    for h in range(chess.HEIGHT):
        for w in range(chess.WIDTH):
            if self.board[h][w] != self.my_side:
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
