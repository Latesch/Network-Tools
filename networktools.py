from pythonping import ping
import subprocess
import sys


def ping_host(host, count=4, timeout=1):
    try:
        result = ping(host, count=count, timeout=timeout)
        if result.stats_packets_lost >= (count // 2):
            status = "warn"
        else:
            status = "ok"
        return result, status
    except OSError as e:
        return f"Ошибка сети: {e}", "danger"


def traceroute_host(host, max_hops=15, timeout=1, queries=1):
    try:
        is_windows = sys.platform.startswith("win")
        if is_windows:
            cmd = [
                "tracert",
                "-h", str(max_hops),
                "-w", str(int(timeout * 1000)),
                host,
            ]
        else:
            cmd = [
                "traceroute",
                "-m", str(max_hops),
                "-q", str(queries),
                "-w", str(int(timeout)),
                host,
            ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        output = (result.stdout or "") + "\n" + (result.stderr or "")

        if is_windows:
            if "request timed out" in output.lower():
                status = "warn"
            elif host.lower() in output.lower():
                status = "ok"
            else:
                status = "danger"
        else:
            if host.lower() in output.lower():
                status = "warn" if "*" in output else "ok"
            else:
                status = "danger"

        return output.strip(), status

    except Exception as e:
        return f"Ошибка при выполнении traceroute: {e}", "danger"


def nslookup(host, qtype="A", dns_server="8.8.8.8", timeout=2):
    try:
        cmd = ["nslookup", "-type=" + qtype, host, dns_server]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        output = (result.stdout or "") + "\n" + (result.stderr or "")

        if "timed out" in output.lower() or "no response" in output.lower():
            status = "danger"
        elif "non-existent domain" in output.lower() or "can't find" in output.lower():
            status = "danger"
        elif "name:" in output.lower() and "address" in output.lower():
            status = "ok"
        else:
            status = "warn"

        return output.strip(), status

    except subprocess.TimeoutExpired:
        return f"*** Timeout: no response from DNS server {dns_server}", "danger"
    except Exception as e:
        return f"Error while running nslookup: {e}", "danger"
