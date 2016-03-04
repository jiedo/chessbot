## 简介

A bot can play gobang(五子棋) with another chessbot. You can write a strategy for it to make it smarter.

chessbot作为独立运行的peer启动, 与另一个chessbot互联对弈, 不需要中心服务器.

## 背景

棋盘使用直角坐标系来记录棋子位置. 棋盘范围为: HEIGHT * WIDTH.
原点(0, 0)在左上角, H轴方向向下, W轴方向向右.

棋子坐标(h, w)必须在棋盘范围内. 即:

    0 <= h < HEIGHT
    0 <= w < WIDTH

参与方有黑方(X)和白方(O), 黑方先下.


## AI通信协议

    PUT h w X/O

表示落子到棋盘坐标(h, w), 黑白双方都使用同样的命令落子. 命令末尾附带X或O表示黑方或白方.

其中h为数字; w为数字,或者为序数是w的小写英文字母. 序数从0开始.

    START

表示开局, 收到 START 的bot为黑方. 而直接收到 PUT 的为白方.


## AI实现

chessbot.py中的main函数已实现一个bot框架, 按顺序处理了通信. 留出strategy()在己方应该下棋时调用, strategy只需分析棋盘, 并返回落子位置.

棋盘记录在二维数组中, 每个位置有3种状态: 黑/白/空, 棋盘会在通信时自动更新.

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

## 结果展示

    START
    PUT 0 a X
    PUT 16 q O
    ...
    ...
    PUT 4 e X
       a b c d e f g h i j k l m n o p q
       _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
     0|X
     1|  X
     2|    X
     3|      X
     4|        X
     5|
     6|
     7|
     8|
     9|
    10|
    11|
    12|
    13|
    14|
    15|
    16|                          O O O O
       _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
      X Win.

## TODO

* 很容易实现一个chessbot前端, 实现人机对弈.
* 增加其他棋类规则
