# -*- coding: utf-8 -*-
"""
GitHub 访问修复工具
------------------
作用：自动挑出当前「真正能打开网页」的 GitHub 节点，写进 hosts，刷新 DNS 缓存。

为什么要做两步验证：
    你的网络对 GitHub 是间歇性放行 —— 一个 IP 可能「TCP 连得上」但网页打不开，
    也可能几分钟前还通、现在就废。所以本工具先测连通，再发一次真实网页请求确认，
    只把「确实能打开 github.com」的 IP 写进 hosts。

需要管理员权限才能改 hosts。

用法：
    双击桌面「修复github打不开.bat」   （推荐，会自动提权）
    python fix_github.py --check      （只检测，不修改任何文件）
    python fix_github.py --restore    （还原 hosts，删掉 github 那一行）

【2026-10-13 重要更新】
    实测发现：当 GitHub 变成「域名级阻断」（TLS 里的 SNI=github.com 被掐，
    换成 api.github.com 走同一台服务器就通）时，**换 hosts 里的 IP 完全无效**。
    本工具遇到「所有节点都连不上」会直接告诉你 —— 那时候只能开加速器。
"""
import http.client
import os
import shutil
import socket
import ssl
import subprocess
import sys
import time

HOSTS = r"C:\Windows\System32\drivers\etc\hosts"
BACKUP = r"C:\Windows\System32\drivers\etc\hosts.backup"

# GitHub 常见节点 IP 池（会动态变化，所以多备一些）
CANDIDATES = [
    "4.237.22.38",
    "20.200.245.247",
    "20.205.243.166",
    "20.26.156.216",
    "20.26.156.215",
    "20.205.243.165",
    "20.205.243.167",
    "20.205.243.168",
    "140.82.112.3",
    "140.82.113.3",
    "140.82.114.3",
    "20.27.177.113",
    "20.27.177.114",
    "20.201.28.151",
]

TCP_ROUNDS = 2
TCP_TIMEOUT = 2.5
HTTP_TIMEOUT = 10

CHECK_ONLY = "--check" in sys.argv
RESTORE = "--restore" in sys.argv
LINE = "=" * 58


def tcp_test(ip):
    """测 TCP 连通，返回 (成功次数, 最快耗时)。"""
    ok, best = 0, None
    for _ in range(TCP_ROUNDS):
        t0 = time.time()
        try:
            s = socket.create_connection((ip, 443), timeout=TCP_TIMEOUT)
            s.close()
            dt = time.time() - t0
            ok += 1
            if best is None or dt < best:
                best = dt
        except Exception:
            pass
    return ok, best


def http_test(ip):
    """向该 IP 发起真实 HTTPS 请求（SNI=github.com），尽量还原浏览器。

    关键：请求头必须和真实 Chrome 一致。头不全时 GitHub 会回 403，
    会把本来能用的节点误判成「打不开网页」—— 踩过这个坑。

    只有状态码 < 400 才算通过（403 可能是反爬，也可能是被限流）。
    返回 (耗时, 状态码或原因)；不通过时耗时为 None。
    """
    try:
        t0 = time.time()
        raw = socket.create_connection((ip, 443), timeout=HTTP_TIMEOUT)
        ctx = ssl._create_unverified_context()
        s = ctx.wrap_socket(raw, server_hostname="github.com")
        s.send(b"GET / HTTP/1.1\r\n"
               b"Host: github.com\r\n"
               b"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
               b"AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36\r\n"
               b"Accept: text/html,application/xhtml+xml,application/xml;q=0.9,"
               b"image/avif,image/webp,image/apng,*/*;q=0.8\r\n"
               b"Accept-Language: zh-CN,zh;q=0.9,en;q=0.8\r\n"
               b"sec-ch-ua: \"Chromium\";v=\"141\", \"Not?A_Brand\";v=\"24\"\r\n"
               b"sec-ch-ua-mobile: ?0\r\n"
               b"sec-ch-ua-platform: \"Windows\"\r\n"
               b"Sec-Fetch-Dest: document\r\n"
               b"Sec-Fetch-Mode: navigate\r\n"
               b"Sec-Fetch-Site: none\r\n"
               b"Sec-Fetch-User: ?1\r\n"
               b"Upgrade-Insecure-Requests: 1\r\n"
               b"Connection: close\r\n\r\n")
        s.settimeout(HTTP_TIMEOUT)
        data = s.recv(64)
        s.close()
        if not data.startswith(b"HTTP/"):
            return None, "无响应"
        parts = data.split(b"\r\n", 1)[0].split(b" ")
        if len(parts) >= 2 and parts[1].isdigit():
            code = int(parts[1])
            if code < 400:
                return time.time() - t0, code
            return None, code
        return None, "响应异常"
    except Exception as e:
        return None, str(e)[:24]


def http_via_system():
    """走系统解析（即 hosts）请求 github.com，验证 hosts 是否真的生效。"""
    try:
        t0 = time.time()
        ctx = ssl._create_unverified_context()
        conn = http.client.HTTPSConnection("github.com", 443,
                                           timeout=HTTP_TIMEOUT, context=ctx)
        conn.request("GET", "/", headers={"User-Agent": "Mozilla/5.0"})
        r = conn.getresponse()
        r.read(32)
        conn.close()
        return time.time() - t0, r.status
    except Exception as e:
        return None, str(e)


def wait_exit():
    if not CHECK_ONLY:
        input("\n按回车键关闭窗口...")


def do_restore():
    """把 hosts 还原成修改前的样子（删掉 github 那一行）。"""
    print(LINE)
    print("  hosts 还原工具")
    print(LINE)
    print()
    if not os.path.exists(BACKUP):
        print("!! 没找到备份文件：")
        print("   " + BACKUP)
        print()
        print("无法自动还原。请手动编辑下面这个文件，删掉 github 那一行：")
        print("   " + HOSTS)
        wait_exit()
        return 1
    try:
        shutil.copy2(BACKUP, HOSTS)
    except PermissionError:
        print("!! 没有管理员权限，写不了 hosts。")
        print("!! 请右键本脚本 → 以管理员身份运行。")
        wait_exit()
        return 1
    except Exception as e:
        print("!! 还原失败：%s" % e)
        wait_exit()
        return 1
    try:
        subprocess.run(["ipconfig", "/flushdns"], capture_output=True, timeout=20)
    except Exception:
        pass
    print("   done: hosts 已还原为原始状态（github 那一行已删除）")
    print("   done: DNS 缓存已刷新")
    print()
    print("   现在 hosts 不再干预 github.com —— 可以放心开加速器了。")
    print(LINE)
    wait_exit()
    return 0


def main():
    if RESTORE:
        return do_restore()

    print(LINE)
    print("  GitHub 访问修复工具")
    print(LINE)
    print()
    print("[1/3] 测试节点连通性（每个 %d 轮）..." % TCP_ROUNDS)

    alive = []
    for ip in CANDIDATES:
        ok, dt = tcp_test(ip)
        if ok:
            alive.append((ok, dt, ip))
            print("   %-17s  连得上  %d/%d" % (ip, ok, TCP_ROUNDS))
        else:
            print("   %-17s  连不上" % ip)

    if not alive:
        print()
        print("!! 所有节点都连不上。")
        print("!! 这种情况通常不是 IP 的问题，而是 github.com 这个域名被整段阻断 ——")
        print("!! 换 hosts 里的 IP 没用。")
        print("!! 请开加速器（雷神），然后用 --restore 把 hosts 清干净。")
        wait_exit()
        return 1

    print()
    print("[2/3] 验证哪些节点能真正打开网页...")
    verified = []
    for ok, dt, ip in alive:
        t, info = http_test(ip)
        if t is None:
            print("   %-17s  能连但打不开网页（%s），排除" % (ip, info))
        else:
            verified.append((t, ok, ip))
            print("   %-17s  网页正常 %.2f 秒  <<< 可用" % (ip, t))

    if not verified:
        print()
        print("!! 没有节点能完整打开网页。")
        print("!! 如果所有节点都是「能连但打不开」，说明是域名级阻断 —— 换 IP 无效。")
        print("!! 请开加速器（雷神），然后用 --restore 把 hosts 清干净。")
        wait_exit()
        return 1

    verified.sort()
    best_t, best_ok, best = verified[0]
    print()
    print("    >>> 最优节点: %s   (网页 %.2f 秒)" % (best, best_t))
    if len(verified) > 1:
        others = ", ".join(v[2] for v in verified[1:4])
        print("    >>> 备选节点: %s" % others)

    if CHECK_ONLY:
        print()
        print("(仅检测模式，未修改任何文件)")
        return 0

    # --- 备份 ---
    if not os.path.exists(BACKUP):
        try:
            shutil.copy2(HOSTS, BACKUP)
            print("   已备份原始 hosts -> hosts.backup")
        except Exception as e:
            print("   备份失败: %s" % e)
    else:
        print("   备份已存在，保留不动")

    # --- 读取 hosts ---
    try:
        with open(HOSTS, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.read().splitlines()
    except Exception as e:
        print("   读取 hosts 失败: %s" % e)
        wait_exit()
        return 1

    kept = [ln for ln in lines if "github.com" not in ln.lower()]
    kept.append("%s    github.com" % best)

    # --- 写入 ---
    try:
        with open(HOSTS, "w", encoding="utf-8", newline="\r\n") as f:
            f.write("\n".join(kept) + "\n")
        print("   已写入 hosts:  %s  ->  github.com" % best)
    except PermissionError:
        print()
        print("!! 没有管理员权限，改不了 hosts。")
        print("!! 请右键这个 bat -> 以管理员身份运行。")
        wait_exit()
        return 1

    subprocess.run(["ipconfig", "/flushdns"],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # --- 最终验证：走 hosts 解析再访问一次 ---
    print()
    print("[3/3] 验证修复效果（走 hosts 访问 github.com）...")
    try:
        resolved = socket.gethostbyname("github.com")
        print("   系统解析 github.com -> %s" % resolved)
    except Exception as e:
        resolved = None
        print("   解析失败: %s" % e)

    t, status = http_via_system()
    if t is not None and isinstance(status, int) and status < 400:
        print("   ✅ 修复成功！github.com 可正常访问（%.2f 秒）" % t)
        ok_flag = True
    else:
        print("   ⚠ 网页验证未通过（%s）—— 网络刚换过 IP，可能又抖了" % status)
        print("     请再跑一次本工具，或在浏览器里直接试试。")
        ok_flag = False

    print()
    print(LINE)
    print("  接下来：")
    print("   1. 彻底关掉浏览器（整个退出，不是按 F5）")
    print("   2. 重新打开，访问 github.com")
    print()
    print("  ⚠ 重要：本网络对 github.com 是「域名级」间歇阻断。")
    print("    修好就尽快操作；再打不开、且所有节点都连不上时，")
    print("    别反复修 hosts（没用），直接开加速器。")
    print()
    print("  想还原 hosts -> 双击桌面「还原hosts.bat」")
    print(LINE)
    wait_exit()
    return 0 if ok_flag else 2


if __name__ == "__main__":
    sys.exit(main())
