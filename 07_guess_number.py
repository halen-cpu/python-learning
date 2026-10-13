""" 用python设计第一个游戏 """

temp = input("猜一下你翔哥的幸运数字:")
guess = int(temp)

if guess == 7:
     print("哇塞这你都知道吗奖励一颗糖叭嘻嘻")
     print("猜错了,骗你的!")
else:
     print("猜错了我的幸运数字是7")

print("game over")
