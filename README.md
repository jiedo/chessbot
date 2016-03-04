## 简介

A bot can play gobang(五子棋) with another chessbot. You can write a strategy for it to make it smarter.

棋盘使用直角坐标系来记录棋子位置. 棋盘范围为: height * width.
原点(0, 0)在左上角, A轴方向向下, B轴方向向右.

棋子坐标(a, b)必须在棋盘范围内. 即:

    0 <= a < height
    0 <= b < width

参与方有黑方(X)和白方(O), 黑方先下.

## 运行方式

chessbot读取stdin, 得到对方落子位置. 然后将自己落子位置输出到stdout.

    $ python -u ./chessbot.py

支持参数 -w , 表示选择白方.

    $ python -u ./chessbot.py -w

chessbot支持和另一个chessbot对弈, 绑定双方stdin和stdout即可. 必须有一方选择白方. 当一方胜利后, chessbot退出.

    $ mkfifo fifo
    $ python2.7 -u ./chessbot.py -w < fifo | tee /dev/stderr | python2.7 -u ./chessbot.py | tee /dev/stderr > fifo


## 使用文本操作命令

    START

表示开局, 收到开局命令的bot为黑方.


    OP_PUT a b X/O

表示落子到棋盘坐标(a, b), 黑白双方都使用同样的命令落子. 命令末尾附带X或O表示黑方或白方.


## AI

chessbot.py中的函数strategy()在己方应该下棋时调用, 可分析棋盘, 并返回落子位置.
请修改如下函数, 实现自己的AI.

    def strategy():
        a, b = 1, 1
        return a, b
