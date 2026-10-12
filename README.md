# Python 学习目录 · 侯ii

## 环境信息

| 项目 | 值 |
| --- | --- |
| Python 版本 | 3.13.15 |
| 安装位置 | `C:\Users\13377\AppData\Local\Programs\Python\Python313` |
| 学习目录 | `C:\Users\13377\python-learning` |
| pip 镜像 | 清华 TUNA（已配置，装库飞快） |

---

## 怎么运行代码

### 第 1 步：打开命令行

按 `Win + R`，输入 `cmd`，回车。

### 第 2 步：进到学习目录

```cmd
cd C:\Users\13377\python-learning
```

### 第 3 步：运行

```cmd
python 01_hello.py
```

换文件名就运行别的：

```cmd
python 02_basics.py
python 03_mortgage.py
```

---

## 必须记住的 4 个命令

| 命令 | 作用 |
| --- | --- |
| `python 文件名.py` | 运行一个脚本 |
| `python` | 进入交互模式（敲一行执行一行，`exit()` 退出） |
| `python -m pip install 库名` | 安装第三方库，例如 `python -m pip install requests` |
| `python -m pip list` | 看已经装了哪些库 |

---

## 三个练习文件

1. `01_hello.py` —— 第一个程序，先跑通再说
2. `02_basics.py` —— 变量 / 运算 / 判断 / 循环 / 函数，Python 的 80% 就这些
3. `03_mortgage.py` —— 房贷月供计算器，会问你贷款金额、利率、年限，算出月供和总利息

运行 `03_mortgage.py` 时，程序会停下来等你输入，直接打字然后回车就行。

---

## 下一步建议

1. 把 `02_basics.py` 里的数字、文字全改一遍，看输出怎么变
2. 给 `03_mortgage.py` 加一个「等额本金」的计算方式做对比
3. 用 VS Code 打开这个文件夹（桌面图标已备好），比记事本舒服得多
4. 看 `04_GitHub上手.md`，把代码备份到 GitHub 上

---

_遇到报错，把完整的报错文字发给我，别只发截图的一半。_
