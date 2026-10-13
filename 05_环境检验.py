# -*- coding: utf-8 -*-
"""
05 环境检验 —— 数据分析全套库是否真的能跑
------------------------------------------
跑法：  python 05_环境检验.py
输出：  终端结果 + 一张「房价检验图.png」
"""
import sys
import platform

LINE = "=" * 58

print(LINE)
print("  Python 环境检验")
print(LINE)
print("  Python 版本 :", sys.version.split()[0])
print("  系统        :", platform.system(), platform.release())
print("  解释器      :", sys.executable)
print()

# ---------- 1. 逐个导入核心库 ----------
LIBS = [
    ("numpy",      "数值计算（所有库的底座）"),
    ("pandas",     "表格数据处理（最核心）"),
    ("matplotlib", "画图"),
    ("seaborn",    "统计图表（更好看的图）"),
    ("scipy",      "科学计算 / 统计检验"),
    ("openpyxl",   "读写 Excel 文件"),
]

print("【1】核心库导入检验")
ok = 0
for name, desc in LIBS:
    try:
        mod = __import__(name)
        ver = getattr(mod, "__version__", "?")
        print("   [OK] %-11s %-9s  %s" % (name, ver, desc))
        ok += 1
    except Exception as e:
        print("   [!!] %-11s 导入失败 -> %s" % (name, e))
print("   结果: %d / %d" % (ok, len(LIBS)))

# ---------- 2. 用 pandas 真算一遍 ----------
print()
print("【2】实战检验 — 算一遍广州各区的房价")
import numpy as np
import pandas as pd

data = {
    "区域":        ["天河", "越秀", "海珠", "番禺", "黄埔", "白云", "增城", "南沙"],
    "均价(元/㎡)": [52000, 48000, 41000, 27000, 32000, 31500, 14000, 17500],
    "户型(㎡)":    [89, 75, 88, 95, 100, 92, 110, 105],
}
df = pd.DataFrame(data)
df["总价(万)"] = (df["均价(元/㎡)"] * df["户型(㎡)"] / 10000).round(1)

print(df.to_string(index=False))

cheapest = df.sort_values("均价(元/㎡)").iloc[0]
priciest = df.sort_values("均价(元/㎡)", ascending=False).iloc[0]
avg = df["均价(元/㎡)"].mean()
print()
print("   最便宜: %s  %d 元/㎡" % (cheapest["区域"], cheapest["均价(元/㎡)"]))
print("   最贵  : %s  %d 元/㎡" % (priciest["区域"], priciest["均价(元/㎡)"]))
print("   八区平均: %.0f 元/㎡" % avg)

# ---------- 3. 用 numpy 算月供（等额本息） ----------
print()
print("【3】实战检验 — numpy 算房贷月供")
total = 2000000      # 贷款 200 万
rate = 0.031         # 年利率 3.1%
years = 30


def monthly_payment(principal, annual_rate, years):
    r = annual_rate / 12
    n = years * 12
    return principal * r * (1 + r) ** n / ((1 + r) ** n - 1)


m = monthly_payment(total, rate, years)
print("   贷款 200 万 / 年利率 3.1% / 30 年")
print("   月供 = %.2f 元" % m)
print("   总利息 = %.2f 万元" % ((m * years * 12 - total) / 10000))

# ---------- 4. 画图 ----------
print()
print("【4】画图检验 — 生成「房价检验图.png」")
import matplotlib
matplotlib.use("Agg")          # 不开窗口，直接存文件
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

d = df.sort_values("均价(元/㎡)", ascending=False)
fig, ax = plt.subplots(figsize=(10, 5.5))
colors = ["#c0392b" if v >= avg else "#7f8c8d" for v in d["均价(元/㎡)"]]
bars = ax.bar(d["区域"], d["均价(元/㎡)"], color=colors, width=0.62)
for b, v in zip(bars, d["均价(元/㎡)"]):
    ax.text(b.get_x() + b.get_width() / 2, v + 600, "%d" % v,
            ha="center", fontsize=10)
ax.axhline(avg, color="#2980b9", linestyle="--", linewidth=1.2)
ax.text(7.4, avg + 700, "平均 %.0f" % avg, color="#2980b9", fontsize=10, ha="right")
ax.set_title("广州各区二手房均价对比（元/㎡）", fontsize=15, pad=14)
ax.set_ylabel("均价（元/㎡）")
ax.set_ylim(0, d["均价(元/㎡)"].max() * 1.18)
ax.spines[["top", "right"]].set_visible(False)
ax.grid(axis="y", alpha=0.25)
fig.tight_layout()
fig.savefig("房价检验图.png", dpi=130)
print("   已保存: 房价检验图.png")

# ---------- 5. Jupyter ----------
print()
print("【5】Jupyter 检验")
from importlib.metadata import version as _ver
for pkg in ("jupyterlab", "notebook", "ipykernel"):
    try:
        print("   [OK] %-11s %s" % (pkg, _ver(pkg)))
    except Exception as e:
        print("   [!!] %-11s %s" % (pkg, e))

print()
print(LINE)
print("  检验结束" if ok == len(LIBS) else "  有项目未通过，请看上面的 [!!]")
print(LINE)
