"""
猜幸运数字 · 第 2 版
=====================
原版：07_guess_number.py（2026-10-13 23:30，侯ii 的第一个程序，一字未动保留）

这一版改了 4 个地方：
  1. 加了 while 循环 —— 猜不对可以一直猜
  2. 输入非数字不再崩溃（try / except 兜底）
  3. 会提示「大了 / 小了」，猜起来有方向
  4. 统计一共猜了几次
"""

LUCKY = 7            # 幸运数字（想玩随机的：import random 后改成 random.randint(1, 100)）

count = 0            # 已经猜了几次

print("猜一下你翔哥的幸运数字：")

while True:
    temp = input("请输入你猜的数字：")

    # ① 容错：input() 拿到的永远是字符串，直接 int() 遇到字母会崩
    try:
        guess = int(temp)
    except ValueError:
        print("喂，要输入整数啊，重新来～")
        continue

    count = count + 1

    # ② 判断
    if guess == LUCKY:
        print("哇塞这你都知道吗，奖励一颗糖叭嘻嘻")
        print("猜错了，骗你的！")
        print("你一共猜了", count, "次")
        break
    elif guess > LUCKY:
        print("大了大了，往小了猜")
    else:
        print("小了小了，往大了猜")

print("game over")
