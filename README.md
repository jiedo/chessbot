## 简介

A bot can play gobang(五子棋) with another chessbot. You can write a strategy for it to make it smarter.

棋盘使用直角坐标系来记录棋子位置. 棋盘范围为: Height * Width.
原点(0, 0)在左上角, H轴方向向下, W轴方向向右.

棋子坐标(h, w)必须在棋盘范围内. 即:

    0 <= h < height
    0 <= w < width

参与方有黑方(X)和白方(O), 黑方先下.

## AI通信协议

    PUT h w X/O

表示落子到棋盘坐标(h, w), 黑白双方都使用同样的命令落子. 命令末尾附带X或O表示黑方或白方.

其中h为数字; w为数字,或者为序数是w的小写英文字母. 序数从0开始.

    START

表示开局, 收到开局命令的bot为黑方. 未收到而直接收到 PUT 的为白方.



## AI实现

chessbot.py中的函数strategy()在己方应该下棋时调用, 可分析棋盘, 并返回落子位置.
请修改如下函数, 实现自己的AI.

    def strategy():
        h, w = 1, 1
        return h, w


## 运行方式

暂时实现为通过stdin/stdout通信. chessbot读取stdin, 得到对方落子位置. 然后将自己落子位置输出到stdout.

    $ python -u ./chessbot.py

支持参数 -w , 表示选择白方, 对方将成为黑方.

    $ python -u ./chessbot.py -w

chessbot支持和另一个chessbot对弈, 绑定双方stdin和stdout即可. 必须有一方选择白方. 当一方胜利后, chessbot退出.

    $ mkfifo fifo
    $ python2.7 -u ./chessbot.py -w < fifo | tee /dev/stderr | python2.7 -u ./chessbot.py | tee /dev/stderr > fifo


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
