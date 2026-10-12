# -*- coding: utf-8 -*-
# Python 最核心的 5 样东西：变量、运算、判断、循环、函数
# 运行：python 02_basics.py

# ---------- 1. 变量：给数据起个名字 ----------
name = "侯ii"           # 字符串（文字）
age = 18                # 整数
height = 1.75           # 小数
is_student = True       # 布尔值（True / False）

print("姓名：", name)
print("年龄：", age)
print("身高：", height)
print("是学生：", is_student)
print("-" * 40)

# ---------- 2. 运算 ----------
a = 10
b = 3
print("a + b  =", a + b)      # 加
print("a - b  =", a - b)      # 减
print("a * b  =", a * b)      # 乘
print("a / b  =", a / b)      # 除，结果一定是小数
print("a // b =", a // b)     # 整除，砍掉小数部分
print("a % b  =", a % b)      # 取余数
print("a ** b =", a ** b)     # a 的 b 次方
print("-" * 40)

# ---------- 3. 判断 if ----------
score = 85
if score >= 90:
    print("优秀")
elif score >= 60:
    print("及格")
else:
    print("不及格")
print("-" * 40)

# ---------- 4. 循环 for ----------
print("数 1 到 5：")
for i in range(1, 6):
    print(i)

print("列表里的东西：")
fruits = ["苹果", "香蕉", "橙子"]
for f in fruits:
    print("-", f)
print("-" * 40)

# ---------- 5. 函数 def：把一段逻辑打包 ----------
def add(x, y):
    """把两个数加起来并返回结果"""
    return x + y

print("add(3, 5)     =", add(3, 5))
print("add(100, 250) =", add(100, 250))
