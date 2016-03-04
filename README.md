## 简介

A bot can play gobang(五子棋) with another chessbot. You can write strategy for it to make it smarter.

棋盘使用直角坐标系来记录棋子位置. 棋盘范围为: height * width.
原点(0, 0)在左上角, A轴方向向下, B轴方向向右.

棋子坐标(a, b)必须在棋盘范围内. 即:

    0 <= a < height
    0 <= b < width

参与方有黑方和白方, 黑方先下.

## 运行方式

    $ python ./chessbot

chessbot读取stdin, 得到对方落子位置. 然后将自己落子位置输出到stdout.

chessbot支持和另一个chessbot对弈, 绑定双方stdin和stdout即可. 当一方胜利后, chessbot退出.


## 使用文本操作命令

    START

表示开局, 收到开局命令的bot为黑方.


    OP_PUT a b

表示落子到棋盘坐标(a, b), 黑白双方都使用同样的命令落子.


## AI

函数strategy()在己方应该下棋时调用, 可分析棋盘, 并返回落子位置.
请修改如下函数, 实现自己的AI.

    def strategy():
        a, b = 1, 1
        return a, b


##
