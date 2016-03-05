## 简介

A bot can play gobang(五子棋) with another chessbot. You can write a strategy for it to make it smarter.

chessbot作为独立运行的peer启动, 与另一个chessbot互联对弈, 不需要中心服务器.

## 背景

棋盘使用去掉0点的直角坐标系来记录棋子位置. 原点(1, 1)在左下角, W轴方向向右, H轴方向向上.

棋盘范围为: WIDTH * HEIGHT. 棋子坐标(w, h)必须在棋盘范围内. 即:

    1 <= w <= WIDTH
    1 <= h <= HEIGHT

传统上将W轴表示为序数是w的英文字母. 序数从1开始. 如将棋子坐标(3, 6)写成C6.

参与方有黑方(*)和白方(O), 黑方先下.


## AI通信协议

通信命令不区分大小写。

    PUT Wh

表示落子到棋盘坐标(w, h)。黑白双方都使用同样的命令落子. 命令末尾可选附带*或O表示黑方或白方.

    START

表示开局, 收到 START 的bot为黑方. 而直接收到 PUT 的为白方.


## AI实现

chessbot.py中的main函数已实现一个bot框架, 按顺序处理了通信. 留出strategy()在己方应该下棋时调用, strategy只需分析棋盘, 并返回落子位置.

棋盘记录在二维数组中, 每个位置有3种状态: 黑/白/空, 棋盘会在通信时自动更新. 注意二维数组下标从0开始，高维是H轴。

可修改如下strategy函数, 实现自己的AI.

    def strategy(self):
        # 棋盘:
        # self.board[h][w]
        # 此demo逻辑为顺序落子
        #
        for h in range(chess.HEIGHT):
            for w in range(chess.WIDTH):
                if self.board[h][w] == chess.BLANK:
                    return h, w

或者重写main函数, 仅仅使用chess.Bot代码来构建非简单回调strategy的AI, 只要依据回合制顺序通信即可.


## 运行方式

chessbot.py暂时实现为通过stdin/stdout通信. chessbot.py读取stdin, 得到对方落子位置. 然后将自己落子位置输出到stdout.

    $ python -u ./chessbot.py
    
支持参数 -w , 表示选择白方, 对方将成为黑方.

    $ python -u ./chessbot.py -w

对弈时, 绑定双方stdin和stdout即可. 注意必须有一方选择白方. 当一方胜利后, chessbot.py自动退出.

    $ mkfifo fifo
    $ python2.7 -u ./chessbot.py -w < fifo | python2.7 -u ./chessbot.py > fifo

用nc可实现远程对弈.

    # hostA, 选择白方, 先建立监听:
    $ mkfifo fifo
    $ python2.7 -u ./chessbot.py -w < fifo | nc -l -p 8002 > fifo

    # hostB 为黑方:
    $ mkfifo fifo
    $ python2.7 -u ./chessbot.py < fifo | nc hostA 8002 > fifo
    
支持参数 -v , 输出每一步棋盘.

    $ python -u ./chessbot.py -v

支持参数 -d , 输出调试错误.

    $ python -u ./chessbot.py -d


## 结果展示

    START
    PUT A1 *
    PUT Q17 O
    ...
    ...
    PUT E5 *
    * Win.    
    Notes: 9    
       ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
    17|                          O O O O|
    16|                                 |
    15|                                 |
    14|                                 |
    13|                                 |
    12|                                 |
    11|                                 |
    10|                                 |
     9|                                 |
     8|                                 |
     7|                                 |
     6|                                 |
     5|        *                        |
     4|      *                          |
     3|    *                            |
     2|  *                              |
     1|*                                |
       ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
       A B C D E F G H I J K L M N O P Q

## TODO

* 记录双方计算过程时间
* 实现对弈策略
* 很容易实现一个chessbot前端, 实现人机对弈.
* 增加其他棋类规则
