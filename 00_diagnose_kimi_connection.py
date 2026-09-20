import json
import os
import socket
import ssl
import urllib.request
import urllib.error

HOSTS = ["api.moonshot.ai", "api.moonshot.cn"]  # .ai = international, .cn = China
TIMEOUT = 5


def check_dns(host):
    try:
        ip = socket.getaddrinfo(host, 443)[0][4][0]
        return f"OK   -> resolves to {ip}"
    except socket.gaierror as e:
        return f"FAIL -> {e}"


def check_tcp(host, port=443):
    try:
        with socket.create_connection((host, port), timeout=TIMEOUT):
            return "OK   -> TCP connection opened"
    except OSError as e:
        return f"FAIL -> {e}"


def check_tls(host):
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, 443), timeout=TIMEOUT) as sock:
            with ctx.wrap_socket(sock, server_hostname=host):
                return "OK   -> TLS handshake completed"
    except ssl.SSLError as e:
        return f"FAIL -> {e}"
    except OSError as e:
        return f"FAIL -> {e}"


def check_https(host):
    """A real HTTP request WITHOUT your app code. Any HTTP status = connection works."""
    key = os.environ.get("MOONSHOT_API_KEY", "")
    req = urllib.request.Request(
        f"https://{host}/v1/models",
        headers={"Authorization": f"Bearer {key}"} if key else {},
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return f"OK   -> HTTP {r.status} (connection fully working!)"
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")[:200]
        return f"OK   -> HTTP {e.code} (connection WORKS; server answered: {body})"
    except urllib.error.URLError as e:
        return f"FAIL -> {e.reason}"


def check_proxy_env():
    return {k: v for k, v in os.environ.items() if "proxy" in k.lower()} or "none set"


if __name__ == "__main__":
    print(f"Proxy env vars: {check_proxy_env()}\n")
    for host in HOSTS:
        print(f"=== {host} ===")
        print(f"  1. DNS : {check_dns(host)}")
        print(f"  2. TCP : {check_tcp(host)}")
        print(f"  3. TLS : {check_tls(host)}")
        print(f"  4. HTTP: {check_https(host)}")
        print()

    print("""HOW TO READ THE RESULTS
  DNS fails  -> your machine cannot resolve the name. Fix DNS (e.g. switch to
                8.8.8.8 / 1.1.1.1, or 223.5.5.5 in China), or check VPN/DNS leak.
  TCP fails  -> connection blocked before reaching the server: firewall, VPN,
                corporate network, or geo-restriction. Try the OTHER host
                (.ai vs .cn). Mainland China -> use api.moonshot.cn; elsewhere -> .ai.
  TLS fails  -> something intercepts the encryption, usually a corporate
                proxy doing MITM. Ask IT for the CA cert and set
                SSL_CERT_FILE=/path/to/corp-ca.pem, or use your VPN.
  HTTP 401   -> network is FINE; the key is wrong/expired (e.g. it belongs to
                the other region's platform). Regenerate it.
  HTTP 200   -> everything works end-to-end; the bug is in your code
                (check base_url for typos, missing /v1, stray whitespace).""")