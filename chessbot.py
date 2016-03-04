#!/usr/bin/env python
#encoding: utf-8

import sys
import time
import chess


def main():
    # main 默认实现成回调strategy()模式,
    # 但可以实现成更复杂模式, 符合bot通信协议即可

    if len(sys.argv) == 2:
        if sys.argv[1] == "-w":
            #如果选择白方, 则通知对方START.
            chess.chess_operate("START")

    bot = chess.Bot()
    while True:
        # 首先读取对方的落子位置, 并写入棋盘
        while bot.b_next == bot.b_your_side:
            a, b = bot.chess_get()
            time.sleep(0.1)

        # 检测对方是否获胜
        if bot.is_winner(bot.b_your_side):
            break

        # 回调自己的策略
        a, b = strategy(bot)
        # 写入棋盘并通知对方
        bot.chess_put(a, b)

        time.sleep(0.1)
        # 检测自己是否获胜
        if bot.is_winner(bot.b_my_side):
            chess.chess_log("%s Win." % bot.b_my_side)
            break


def strategy(self):
    # 测试AI
    if self.b_my_side == chess.BLACK:
        return strategy2(self)
    else:
        return strategy9(self)


def strategy0(self):
    # 测试AI0
    for i in range(chess.HEIGHT):
        for j in range(chess.WIDTH):
            if self.board[i][j] == chess.BLANK:
                return i, j

def strategy1(self):
    # 测试AI1
    for i in range(chess.HEIGHT):
        if self.board[i][0] == chess.BLANK:
                return i, 0

def strategy2(self):
    # 测试AI2
    for i in range(chess.HEIGHT):
        if self.board[i][i] == chess.BLANK:
                return i, i


def strategy9(self):
    # 测试AI9
    for i in range(chess.HEIGHT):
        for j in range(chess.WIDTH):
            if self.board[chess.HEIGHT-i-1][chess.WIDTH-j-1] == chess.BLANK:
                return chess.HEIGHT-i-1, chess.WIDTH-j-1


if __name__ == "__main__":
    main()
