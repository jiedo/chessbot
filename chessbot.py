#!/usr/bin/env python
#encoding: utf-8

import sys
import time
import random
import chess


def main():
    # main 默认实现成回调strategy()模式,
    # 但可以实现成更复杂模式, 符合bot通信协议即可

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

        if show_verbose:            
            bot.show_board()
            
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
            bot.show_board()
            
        # 检测自己是否获胜
        if bot.is_winner(bot.b_my_side):
            chess.chess_log("%s Win." % bot.b_my_side)
            break


def strategy(self):
    # 测试AI
    if self.b_my_side == chess.BLACK:
        return strategy2(self)
    else:
        return strategy2(self)


def strategy0(self):
    # 测试AI0
    return random.randint(0, chess.HEIGHT-1), random.randint(0, chess.WIDTH-1)


def strategy1(self):
    # 测试AI1
    for i in range(chess.HEIGHT):
        if self.board[i][0] == chess.BLANK:
                return i, 0

            
def strategy2(self):
    # 测试AI2
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
    # 测试AI9
    for i in range(chess.HEIGHT):
        for j in range(chess.WIDTH):
            if self.board[chess.HEIGHT-i-1][chess.WIDTH-j-1] == chess.BLANK:
                return chess.HEIGHT-i-1, chess.WIDTH-j-1


if __name__ == "__main__":
    main()
