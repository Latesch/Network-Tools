import subprocess
import sys
from pythonping import ping


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
        if sys.platform.startswith("win"):
            cmd = ["tracert", "-h", str(max_hops), "-w", str(int(timeout * 1000)), host]
        else:
            cmd = ["traceroute", "-m", str(max_hops), "-q", str(queries), "-w", str(int(timeout)), host]

        result = subprocess.run(cmd, capture_output=True, text=True)
        output = (result.stdout or "") + "\n" + (result.stderr or "")

        if sys.platform.startswith("win"):
            if "request timed out" in output.lower():
                status = "warn"
            elif host.lower() in output.lower():
                status = "ok"
            else:
                status = "danger"
        else:
            if host.lower() in output.lower():
                if "*" in output:
                    status = "warn"
                else:
                    status = "ok"
            else:
                status = "danger"
        return output.strip(), status

    except Exception as e:
        return f"Ошибка при выполнении traceroute: {e}", "danger"
