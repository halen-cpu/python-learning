#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Python 学习面板 —— 本地服务

用法：双击“启动学习面板.bat”（或在本目录执行 python app.py）
数据：保存在同目录 study_data.json，纯文本，可以直接用微信/Git 备份。
关闭运行时的黑窗口 = 停止服务。
"""

import json
import os
import socket
import sys
import threading
import urllib.request
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

try:  # 控制台编码不给力时，至少别让 print 把程序搞崩
    sys.stdout.reconfigure(errors="replace")
except Exception:
    pass

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "study_data.json")
PORTS = range(8765, 8786)
EMPTY = {"version": 1, "sessions": {}, "notes": []}


class Handler(SimpleHTTPRequestHandler):
    """静态文件 + 两个接口：GET /api/data 读取，POST /api/data 保存。"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE, **kwargs)

    def log_message(self, fmt, *args):
        pass  # 保持控制台干净

    # ---------------- 工具 ----------------
    def _send_json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _load(self):
        if not os.path.exists(DATA_FILE):
            return dict(EMPTY)
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return dict(EMPTY)
        if not isinstance(data, dict):
            return dict(EMPTY)
        data.setdefault("version", 1)
        data.setdefault("sessions", {})
        data.setdefault("notes", [])
        return data

    # ---------------- 路由 ----------------
    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/api/ping":
            self._send_json({"ok": True, "data_file": DATA_FILE})
            return
        if path == "/api/data":
            self._send_json(self._load())
            return
        super().do_GET()

    def do_POST(self):
        path = self.path.split("?")[0]
        if path != "/api/data":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length)
        try:
            obj = json.loads(raw.decode("utf-8"))
            assert isinstance(obj, dict)
        except Exception:
            self._send_json({"ok": False, "error": "invalid json"}, 400)
            return
        tmp = DATA_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=2)
        os.replace(tmp, DATA_FILE)  # 原子替换，防止写坏
        self._send_json({"ok": True})


def find_port():
    """找一个可用端口；如果发现是本程序已在运行，返回负数。"""
    for port in PORTS:
        s = socket.socket()
        try:
            s.bind(("127.0.0.1", port))
            s.close()
            return port
        except OSError:
            s.close()
            try:
                url = "http://127.0.0.1:%d/api/ping" % port
                with urllib.request.urlopen(url, timeout=0.4) as r:
                    if json.loads(r.read().decode("utf-8")).get("ok"):
                        return -port
            except Exception:
                pass
    return None


def main():
    port = find_port()
    if port is None:
        print("端口 8765-8785 全部被占用，请重启电脑后再试。")
        input("按回车退出...")
        return

    if port < 0:
        # 已经在跑：只开浏览器，并用退出码 3 告诉启动脚本“不用再停留提示”
        webbrowser.open("http://127.0.0.1:%d/" % -port)
        print("Panel already running -> browser opened.")
        sys.exit(3)

    httpd = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    url = "http://127.0.0.1:%d/" % port
    threading.Timer(0.8, lambda: webbrowser.open(url)).start()

    print("=" * 52)
    print("  Python 学习面板 已启动")
    print("  地址：" + url)
    print("  数据：" + DATA_FILE)
    print("  关闭这个窗口 = 停止服务（可以先最小化）")
    print("=" * 52)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
