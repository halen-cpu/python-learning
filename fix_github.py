# -*- coding: utf-8 -*-
"""
GitHub 访问修复工具
------------------
作用：自动测速挑出当前最稳的 GitHub 节点，写进 hosts，刷新 DNS 缓存。
      每个节点测多轮，按「成功率 + 延迟」综合排序，避免网络抖动误判。
需要管理员权限才能改 hosts。

用法：
    双击桌面「修复github打不开.bat」   （推荐，会自动提权）
    python fix_github.py --check      （只测速，不修改任何文件）
"""
import os
import shutil
import socket
import subprocess
import sys
import time

HOSTS = r"C:\Windows\System32\drivers\etc\hosts"
BACKUP = r"C:\Windows\System32\drivers\etc\hosts.backup"

# GitHub 常见节点 IP，脚本会从中挑当前最快的
CANDIDATES = [
    "20.205.243.168",
    "20.27.177.113",
    "20.26.156.215",
    "140.82.112.3",
    "140.82.114.3",
    "4.237.22.38",
    "20.200.245.247",
    "20.205.243.166",
]

ROUNDS = 3        # 每个节点测几轮
TIMEOUT = 2.5     # 单次连接超时（秒）

CHECK_ONLY = "--check" in sys.argv

LINE = "=" * 52


def measure(ip):
    """多轮测量，返回 (成功次数, 平均耗时秒 | None)。"""
    ok, times = 0, []
    for _ in range(ROUNDS):
        t0 = time.time()
        try:
            s = socket.create_connection((ip, 443), timeout=TIMEOUT)
            s.close()
            times.append(time.time() - t0)
            ok += 1
        except Exception:
            pass
    avg = sum(times) / len(times) if times else None
    return ok, avg


def wait_exit():
    if not CHECK_ONLY:
        input("\n按回车键关闭窗口...")


def main():
    print(LINE)
    print("  GitHub 访问修复工具")
    print(LINE)
    print()
    print("[1/3] 正在测试各个节点（每个 %d 轮）..." % ROUNDS)

    stats = []
    for ip in CANDIDATES:
        cnt, avg = measure(ip)
        stats.append((cnt, avg, ip))
        if cnt == 0:
            print("   %-17s  %d/%d  不通" % (ip, cnt, ROUNDS))
        else:
            print("   %-17s  %d/%d  平均 %.2f 秒" % (ip, cnt, ROUNDS, avg))

    usable = [s for s in stats if s[0] > 0]
    if not usable:
        print()
        print("!! 所有节点都不通。")
        print("!! 你的网络对 GitHub 的限制比较彻底，请开加速器再试。")
        wait_exit()
        return 1

    usable.sort(key=lambda s: (-s[0], s[1]))
    best_cnt, best_avg, best = usable[0]

    if best_cnt < ROUNDS:
        print()
        print("   提示：当前网络访问 GitHub 不稳定"
              "（最优节点也只有 %d/%d 成功）。" % (best_cnt, ROUNDS))
        print("   修复后如果仍然时好时坏，建议开加速器。")

    print()
    print("[2/3] 最优节点: %s  (%d/%d 通, 平均 %.2f 秒)"
          % (best, best_cnt, ROUNDS, best_avg))

    if CHECK_ONLY:
        print()
        print("(仅测速模式，未修改任何文件)")
        return 0

    # 备份原始 hosts（只在第一次备份，保留最原始的版本）
    if not os.path.exists(BACKUP):
        try:
            shutil.copy2(HOSTS, BACKUP)
            print("   已备份原始 hosts -> hosts.backup")
        except Exception as e:
            print("   备份失败: %s" % e)
    else:
        print("   备份已存在，保留不动")

    # 读取现有 hosts
    try:
        with open(HOSTS, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.read().splitlines()
    except Exception as e:
        print("   读取 hosts 失败: %s" % e)
        wait_exit()
        return 1

    # 删掉旧的 github.com 行，其他内容一律保留
    kept = [ln for ln in lines if "github.com" not in ln.lower()]
    kept.append("%s    github.com" % best)

    try:
        with open(HOSTS, "w", encoding="utf-8", newline="\r\n") as f:
            f.write("\n".join(kept) + "\n")
        print("   已写入 hosts:  %s  ->  github.com" % best)
    except PermissionError:
        print()
        print("!! 没有管理员权限，改不了 hosts。")
        print("!! 请右键这个 bat 文件 -> 以管理员身份运行。")
        wait_exit()
        return 1

    print("[3/3] 刷新 DNS 缓存...")
    subprocess.run(["ipconfig", "/flushdns"],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("   完成")

    print()
    print(LINE)
    print("  修复完成！")
    print()
    print("  接下来：")
    print("   1. 彻底关掉浏览器（整个退出，不是按 F5）")
    print("   2. 重新打开，访问 github.com")
    print()
    print("  以后再打不开 -> 重跑一遍本工具")
    print("  想还原     -> 把 hosts.backup 改名成 hosts")
    print(LINE)
    wait_exit()
    return 0


if __name__ == "__main__":
    sys.exit(main())
