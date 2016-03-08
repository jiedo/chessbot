#!/usr/bin/env python
#encoding: utf-8

import sys
import time
import chess
import math, pygame
from pygame.locals import *


CHESSMAN_SIZE = 50

BOARD_LEFT = 2 * CHESSMAN_SIZE
BOARD_TOP = 2 * CHESSMAN_SIZE

BOARD_WIDTH = (chess.WIDTH -1)* CHESSMAN_SIZE
BOARD_HEIGHT = (chess.HEIGHT - 1) * CHESSMAN_SIZE

SCREEN_WIDTH = BOARD_WIDTH + 4 * CHESSMAN_SIZE
SCREEN_HEIGHT = BOARD_HEIGHT + 4 * CHESSMAN_SIZE

WINSIZE = [SCREEN_WIDTH, SCREEN_HEIGHT]

g_point_to_put = [0, 0]
g_show_point_to_put = [SCREEN_WIDTH/2, SCREEN_HEIGHT/2]


def get_click_point(pos_click):
    cw, ch = pos_click
    cw, ch = cw + CHESSMAN_SIZE/2, ch + CHESSMAN_SIZE/2

    int_cw = (cw - BOARD_LEFT + CHESSMAN_SIZE) / CHESSMAN_SIZE

    int_cw_out = False
    if int_cw < 0:
        int_cw_out = True
    if cw < BOARD_LEFT + int_cw * CHESSMAN_SIZE + CHESSMAN_SIZE/2:
        int_cw -= 1
    if int_cw < 0 or int_cw >= chess.WIDTH:
        int_cw_out = True

    int_ch_out = False
    int_ch = (ch - BOARD_TOP + CHESSMAN_SIZE) / CHESSMAN_SIZE
    if int_ch < 0:
        int_ch_out = True
    if ch < BOARD_TOP + int_ch * CHESSMAN_SIZE + CHESSMAN_SIZE/2:
        int_ch -= 1
    if int_ch < 0 or int_ch >= chess.HEIGHT:
        int_ch_out = True

    if int_ch_out or int_cw_out:
        return None, None
    return (int_cw, int_ch)


def draw_board(surface, chess_board):
    line_color = 40, 80, 40
    background_color = 100, 100, 100
    black_color = 10, 10, 10
    white_color = 240, 240, 240
    click_color = 40, 80, 40
    font_color = 250, 240, 230
    surface.fill(background_color)

    line_width = 2
    chess_label_font = pygame.font.SysFont("Arial", 12)

    cw, ch = get_click_point(g_show_point_to_put)
    if cw is not None and ch is not None:
        pygame.draw.circle(surface, click_color,
                           (BOARD_LEFT + cw * CHESSMAN_SIZE,
                            BOARD_TOP + ch * CHESSMAN_SIZE),
                           CHESSMAN_SIZE/2, line_width)

    for h in range(chess.HEIGHT):
        start_pos = (BOARD_LEFT,
                     BOARD_TOP + h * CHESSMAN_SIZE,)
        end_pos = (BOARD_LEFT + BOARD_WIDTH,
                     BOARD_TOP + h * CHESSMAN_SIZE,)
        pygame.draw.line(surface, line_color, start_pos, end_pos, line_width)

        vertical_label = str(chess.HEIGHT - h)
        ren = chess_label_font.render(vertical_label, 1, font_color, background_color)
        vertical_label_size = chess_label_font.size(vertical_label)
        surface.blit(ren, (BOARD_LEFT - vertical_label_size[0] - CHESSMAN_SIZE/2,
                           BOARD_TOP + h * CHESSMAN_SIZE - vertical_label_size[1]/2))

    for w in range(chess.WIDTH):
        start_pos = (BOARD_LEFT + w * CHESSMAN_SIZE,
                     BOARD_TOP,)
        end_pos = (BOARD_LEFT + w * CHESSMAN_SIZE,
                     BOARD_TOP + BOARD_HEIGHT,)
        pygame.draw.line(surface, line_color, start_pos, end_pos, line_width)

        horizontal_label = chess.idtoa(w)
        ren = chess_label_font.render(horizontal_label, 1, font_color, background_color)
        horizontal_label_size = chess_label_font.size(horizontal_label)
        surface.blit(ren, (BOARD_LEFT + w * CHESSMAN_SIZE - horizontal_label_size[0]/2,
                           BOARD_TOP + BOARD_HEIGHT + CHESSMAN_SIZE/2))

    for h in range(chess.HEIGHT):
        for w in range(chess.WIDTH):
            test_side = chess_board[chess.HEIGHT-h-1][w]
            if test_side == chess.BLANK_ID:
                continue

            pos = (BOARD_LEFT + w * CHESSMAN_SIZE,
                   BOARD_TOP + h * CHESSMAN_SIZE,)

            if test_side == chess.BLACK_ID:
                color = black_color
            elif test_side == chess.WHITE_ID:
                color = white_color
            else:
                chess.chess_log("note: '%s' is illegal." % (test_side))

            radius = int(CHESSMAN_SIZE * 0.309)
            width = radius
            pygame.draw.circle(surface, color, pos, radius, width)


def main():
    # 默认实现成回调strategy()模式,
    # 但可以实现成更复杂模式, 符合bot通信协议即可
    global g_point_to_put, g_show_point_to_put

    sleep_time = 0.01
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

    ################
    clock = pygame.time.Clock()
    pygame.init()
    screen = pygame.display.set_mode(WINSIZE)
    pygame.display.set_caption('Gobang')
    done = False
    ################

    bot = chess.Bot()


    board_block = """
   - - - - - - - - - - - - - - -
15|O                           *|
14|                             |
13|                             |
12|                             |
11|                             |
10|                             |
 9|            * O *            |
 8|            O O O O         O|
 7|            * * *           *|
 6|                             |
 5|                             |
 4|                             |
 3|                             |
 2|                             |
 1|*                           O|
   - - - - - - - - - - - - - - -
   A B C D E F G H I J K L M N O
    """

    bot.board_loads(board_block)
    bot.board_dumps()
    while True:
        ################
        draw_board(screen, bot.board)
        pygame.display.update()
        for e in pygame.event.get():
            if e.type == QUIT or (e.type == KEYUP and e.key == K_ESCAPE):
                done = True
                break
            elif e.type == MOUSEMOTION:
                g_show_point_to_put = list(e.pos)
            elif e.type == MOUSEBUTTONDOWN and e.button == 1:
                g_point_to_put[:] = list(e.pos)
                g_show_point_to_put = list(e.pos)
        if done: break
        clock.tick(10)
        ################

        # 首先读取对方的落子位置, 并写入棋盘
        if bot.side_this_turn == bot.your_side:
            #h, w = bot.get_point_of_chessman(bot.your_side)
            # 读取ui点击
            cw, ch = get_click_point(g_point_to_put)
            if cw is None or ch is None:
                continue
            g_point_to_put = [0, 0]
            h, w = chess.HEIGHT-ch-1, cw

            bot.put_chessman_at_point(bot.your_side, h, w)

            # 检测对方是否获胜
            if bot.is_winner(bot.your_side):
                bot.light_on_win_points()
                chess.chess_log("Notes: %d" % (len(bot.notes)))
                time.sleep(0.1)
                bot.board_dumps()
                break


        # 读取ui点击
        cw, ch = get_click_point(g_point_to_put)
        if cw is None or ch is None:
            continue
        g_point_to_put = [0, 0]
        h, w = chess.HEIGHT-ch-1, cw

        # 写入棋盘并通知对方
        bot.put_chessman_at_point(bot.my_side, h, w)
        if show_verbose:
            time.sleep(sleep_time/10)
            bot.board_dumps()
            time.sleep(sleep_time)

        # 检测自己是否获胜
        if bot.is_winner(bot.my_side):
            chess.chess_log("%s Win." % bot.my_side)
            break


if __name__ == '__main__':
    main()
