import socket
import ssl
import time

CANDIDATES = {
    "github.com": ["20.200.245.247", "20.27.177.113", "140.82.113.3", "20.205.243.168"],
    "api.github.com": ["20.200.245.247", "20.27.177.113", "140.82.113.6", "20.205.243.168"],
    "codeload.github.com": ["20.200.245.247", "20.27.177.113", "140.82.113.10"],
    "github.githubassets.com": ["185.199.108.154", "185.199.109.154", "185.199.110.154", "185.199.111.154"],
    "raw.githubusercontent.com": ["185.199.108.133", "185.199.109.133", "185.199.110.133", "185.199.111.133"],
    "objects.githubusercontent.com": ["185.199.108.133", "185.199.109.133", "185.199.110.133", "185.199.111.133"],
    "avatars.githubusercontent.com": ["185.199.108.133", "185.199.109.133", "185.199.110.133", "185.199.111.133"],
}

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def probe(ip, sni, timeout=5):
    try:
        s = socket.create_connection((ip, 443), timeout=timeout)
    except Exception:
        return False, False, timeout
    t0 = time.time()
    tls = False
    try:
        ss = ctx.wrap_socket(s, server_hostname=sni)
        tls = True
        ss.close()
    except Exception:
        pass
    s.close()
    return True, tls, time.time() - t0


print(f"{'域名':<32}{'DNS解析到的IP':<18}{'解析IP':<10}{'可用IP'}")
print("-" * 92)

for host, candidates in CANDIDATES.items():
    try:
        resolved = socket.gethostbyname(host)
    except Exception:
        resolved = "解析失败"

    ok, tls, _ = probe(resolved, host)
    dns_status = "通" if (ok and tls) else "不通"

    good = []
    for ip in candidates:
        ok2, tls2, _ = probe(ip, host)
        if ok2 and tls2:
            good.append(ip)

    print(f"{host:<32}{resolved:<18}{dns_status:<10}{', '.join(good) if good else '无可用的'}")
