#!/usr/bin/env python
#encoding: utf-8

import sys
import time
import chess

from chessbot import *

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
    board_block = """
   - - - - - - - - - - - - - - -
15|. . . . . . . . . . . . . . .|
14|. . . . . . . . . . . . . . .|
13|. . . . . . . * . . . . . . .|
12|. . . . . . O . O . . . . . .|
11|. . * * * * O * . * . . . . .|
10|. . . . * . . . . . . . . . .|
 9|. . . O . O O . . . . . . . .|
 8|. . . . . . . O . . . . . . .|
 7|. . . . . . . . . . . . . . .|
 6|. . . . . . . . . . . . . . .|
 5|. . . . . . . . . . . . . . .|
 4|. . . . . . . . . . . . . . .|
 3|. . . . . . . . . . . . . . .|
 2|. . . . . . . . . . . . . . .|
 1|. . . . . . . . . . . . . . .|
   - - - - - - - - - - - - - - -
   A B C D E F G H I J K L M N O
"""

    board_block = """
   - - - - - - - - - - - - - - -
15|. . . . . . . . . . . . . . .|
14|. . . . . . . . . . . . . . .|
13|. . . . . . . . . . . . . . .|
12|. . . O * * * O . . . . . . .|
11|. . . . . * * . . . . . . . .|
10|. . . . . . O . . . . . . . .|
 9|. . . . . . . . . . . . . . .|
 8|. . . . . . . O . . . . . . .|
 7|. . . . . . . . . . . . . . .|
 6|. . . . . . . . . . . . . . .|
 5|. . . . . . . . . . . . . . .|
 4|. . . . . . . . . . . . . . .|
 3|. . . . . . . . . . . . . . .|
 2|. . . . . . . . . . . . . . .|
 1|. . . . . . . . . . . . . . .|
   - - - - - - - - - - - - - - -
   A B C D E F G H I J K L M N O
"""

    bot.board_loads(board_block)
    bot.board_dumps()
    # h, w = strategy4(bot, 0, True)

    # for pt, count in all_my_blank_points_count_pair:
    #     print chess.get_label_of_point(pt[0], pt[1]), count

    h, w = strategy6(bot, 0, True,
                     max_level_good = 4,
                     max_level_bad = 5)

    bot.put_chessman_at_point(bot.side_this_turn, h, w)
    bot.board_dumps()

if __name__ == '__main__':
    main()
