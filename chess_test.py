#!/usr/bin/env python
#encoding: utf-8

import sys
import time
import chess

from chessbot import strategy6

def main():
    # 默认实现成回调strategy()模式,
    # 但可以实现成更复杂模式, 符合bot通信协议即可

    show_verbose = False
    chess.g_debug_info = False
    if len(sys.argv) >= 2:
        if "-v" in sys.argv:
            show_verbose = True

        if "-d" in sys.argv:
            chess.g_debug_info = True


    bot = chess.Bot()
    bord_block = """
   - - - - - - - - - - - - - - -
15|                             |
14|                             |
13|        O                    |
12|          *   O   O          |
11|        O   *   *   *        |
10|          *   *   O          |
 9|        *   *   O   O        |
 8|      O   O   *   *          |
 7|                *            |
 6|              O   O          |
 5|                             |
 4|                             |
 3|                             |
 2|                             |
 1|                             |
   - - - - - - - - - - - - - - -
   A B C D E F G H I J K L M N O
    """

    board_block = """
   - - - - - - - - - - - - - - -
15|                             |
14|                             |
13|                             |
12|                             |
11|                             |
10|                  O          |
 9|                *       O    |
 8|              *   *          |
 7|                *            |
 6|                  O          |
 5|                             |
 4|                             |
 3|                             |
 2|                             |
 1|                             |
   - - - - - - - - - - - - - - -
   A B C D E F G H I J K L M N O
"""

    bot.board_loads(board_block)
    bot.board_dumps()
    h, w = strategy6(bot, 0, True,
              max_level_good = 2,
              max_level_bad = 2)

    bot.put_chessman_at_point(bot.side_this_turn, h, w)
    bot.board_dumps()

if __name__ == '__main__':
    main()
