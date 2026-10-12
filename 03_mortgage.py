# -*- coding: utf-8 -*-
# 实战小项目：房贷月供计算器（等额本息）
#
# 等额本息公式：
#   月供 = 本金 x 月利率 x (1+月利率)^月数 / ((1+月利率)^月数 - 1)
#
# 运行：python 03_mortgage.py

def monthly_payment(loan, annual_rate, years):
    """
    loan        : 贷款总额，单位「元」
    annual_rate : 年利率，0.031 表示 3.1%
    years       : 贷款年限
    """
    months = years * 12                 # 总月数
    monthly_rate = annual_rate / 12     # 月利率
    if monthly_rate == 0:               # 万一利率是 0，避免除以 0
        return loan / months
    factor = (1 + monthly_rate) ** months
    return loan * monthly_rate * factor / (factor - 1)


def main():
    print("=" * 46)
    print("          房贷月供计算器（等额本息）")
    print("=" * 46)

    # input() 拿到的是文字，要用 float() / int() 转成数字
    loan = float(input("贷款总额（万元，例如 200）：")) * 10000
    annual_rate = float(input("年利率（%，例如 3.1）：")) / 100
    years = int(input("贷款年限（年，例如 30）："))

    pay = monthly_payment(loan, annual_rate, years)   # 每月月供
    total = pay * years * 12                          # 还款总额
    interest = total - loan                           # 利息总额

    print("-" * 46)
    print(f"贷款总额： {loan / 10000:>12,.2f} 万元")
    print(f"年　利率： {annual_rate * 100:>12,.2f} %")
    print(f"贷款年限： {years:>12} 年")
    print("-" * 46)
    print(f"每月月供： {pay:>12,.2f} 元")
    print(f"还款总额： {total:>12,.2f} 元")
    print(f"其中利息： {interest:>12,.2f} 元")
    print("=" * 46)


if __name__ == "__main__":
    main()
