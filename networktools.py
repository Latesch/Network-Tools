from pythonping import ping
from scapy.all import IP, UDP, DNS, DNSQR, sr1
import subprocess
import sys
import random


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
            cmd = ["tracert", "-h", str(max_hops), "-w",
                    str(int(timeout * 1000)), host]
        else:
            cmd = ["traceroute", "-m", str(max_hops), "-q", str(queries), 
                   "-w", str(int(timeout)), host]

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


def nslookup(host, qtype="A", dns_server="8.8.8.8", timeout=2):
    try:
        dns_req = IP(dst=dns_server)/UDP(sport=random.randint(1024,65535), dport=53)/DNS(rd=1,qd=DNSQR(qname=host, qtype=qtype))
        resp = sr1(dns_req, verbose=0, timeout=timeout)

        if resp is None:
            return (f"*** No response from DNS server {dns_server}", "danger")

        if resp.haslayer(DNS) and resp[DNS].ancount > 0:
            answers = []
            for i in range(resp[DNS].ancount):
                r = resp[DNS].an[i]
                answers.append(r.rdata if hasattr(r, "rdata") else str(r))
            return ("\n".join(map(str, answers)), "ok")

        return (f"*** No {qtype} record found for {host}", "warn")

    except Exception as e:
        return (f"Error: {str(e)}", "danger")
